
import pandas as pd
import requests
import json

from datetime import datetime, timezone
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from pipeline.config import (
    TMDB_API_KEY,
    CANDIDATE_LIST,
    MOVIES_CACHE,
    CREDITS_CACHE,
    PROCESSED_DIR
)


def load_candidate_list():
    return pd.read_csv(
        CANDIDATE_LIST,
        dtype=str,
        keep_default_na=False,
        skip_blank_lines=False
    )


def create_session():
    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        respect_retry_after_header=True
    )

    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.headers.update({"User-Agent": "StreamVault-Data-Pipeline"})

    return session


def fetch_data(movie_id, data_type, session):
    if data_type == "movie":
        folder = MOVIES_CACHE
        url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    else:
        folder = CREDITS_CACHE
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits"

    cache_file = folder / f"{movie_id}.json"
    metadata_file = folder / f"{movie_id}_metadata.json"

    if cache_file.exists():
        with open(cache_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        status = "cached"

    else:
        try:
            response = session.get(
                url,
                params={"api_key": TMDB_API_KEY},
                timeout=(3.05, 10)
            )

            if response.status_code == 404:
                return None, "not_found"

            response.raise_for_status()
            data = response.json()

            folder.mkdir(parents=True, exist_ok=True)

            with open(cache_file, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)

            status = "downloaded"

        except (requests.RequestException, ValueError) as error:
            return None, f"request_error: {error}"

    metadata = {
        "tmdb_id": movie_id,
        "data_type": data_type,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "status": status
    }

    with open(metadata_file, "w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=4)

    return data, status


def fetch_movie(movie_id, session):
    return fetch_data(movie_id, "movie", session)


def fetch_credits(movie_id, session):
    return fetch_data(movie_id, "credits", session)


def reconcile_candidates(candidates, results_df):
    reconciliation = candidates.copy()

    reconciliation.insert(
        0, "candidate_entry", range(1, len(candidates) + 1)
    )

    ids = reconciliation["tmdb_id"].str.strip()
    numeric = ids.str.isdigit()

    reconciliation["candidate_type"] = "unrecognized_non_numeric"
    reconciliation.loc[numeric, "candidate_type"] = "numeric_id"

    reconciliation.loc[
        numeric & ids.duplicated(), "candidate_type"
    ] = "duplicate_numeric_id"

    reconciliation.loc[ids == "", "candidate_type"] = "blank_id"
    reconciliation.loc[ids == "N/A", "candidate_type"] = "missing_value_marker"
    reconciliation.loc[ids == "-1", "candidate_type"] = "invalid_looking_id"

    reconciliation.loc[
        ids.str.lower().str.startswith("tt"), "candidate_type"
    ] = "IMDb_id"

    status = results_df.set_index("tmdb_id")

    reconciliation["movie_status"] = ids.map(
        status["movie_status"]
    ).fillna("not_requested")

    reconciliation["credits_status"] = ids.map(
        status["credits_status"]
    ).fillna("not_requested")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    reconciliation.to_csv(
        PROCESSED_DIR / "candidate_reconciliation.csv",
        index=False
    )

    assert len(reconciliation) == len(candidates)

    return reconciliation



def extract_all_movies():
    candidates = load_candidate_list()

    if "tmdb_id" not in candidates.columns:
        raise ValueError("Candidate list must contain tmdb_id.")

    ids = candidates["tmdb_id"].str.strip()
    unique_ids = ids[ids.str.isdigit()].drop_duplicates()

    session = create_session()
    results = []

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    log_file = PROCESSED_DIR / "extraction_log.csv"

    print(f"Original entries: {len(candidates)}")
    print(f"Unique numeric IDs: {len(unique_ids)}")

    for movie_id in unique_ids:
        movie, movie_status = fetch_movie(movie_id, session)
        credits, credits_status = fetch_credits(movie_id, session)

        results.append({
            "tmdb_id": movie_id,
            "movie_status": movie_status,
            "credits_status": credits_status
        })

        # Save progress after each movie.
        pd.DataFrame(results).to_csv(log_file, index=False)

        print(movie_id, movie_status, credits_status)

    results_df = pd.DataFrame(results)

    reconciliation = reconcile_candidates(candidates, results_df)

    print("\nCandidate classifications:")
    print(reconciliation["candidate_type"].value_counts())

    print("\nMovie retrieval outcomes:")
    print(reconciliation["movie_status"].value_counts())

    print("\nExtraction completed.")
    print(f"Original entries accounted for: {len(reconciliation)}")

    return results_df



if __name__ == "__main__":
    extract_all_movies()
