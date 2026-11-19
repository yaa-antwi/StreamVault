import pandas as pd
import requests
import json

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from pipeline.config import (
    TMDB_API_KEY,
    CANDIDATE_LIST,
    MOVIES_CACHE,
    CREDITS_CACHE,
    PROCESSED_DIR
)

movie_ids = pd.read_csv(
    CANDIDATE_LIST,
    dtype=str,
    keep_default_na=False, # Preserves the literal N/A
    skip_blank_lines=False
)

def create_session():
    retry_strategy = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods={"GET"},
        respect_retry_after_header=True
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)

    session = requests.Session()
    session.mount("https://", adapter)

    session.headers.update({
        "User-Agent": "StreamVault-Licensing-Analysis/1.0"
    })

    return session

def get_cached_movie(movie_id):
    cache_file = MOVIES_CACHE / f"{movie_id}.json"
    MOVIES_CACHE.mkdir(parents=True, exist_ok=True)

    if cache_file.exists():
        with open(cache_file, "r", encoding="utf-8") as file:
            return json.load(file)

    return None


def fetch_movie(movie_id, session):
    # First, check whether the movie is already saved.
    cached_movie = get_cached_movie(movie_id)

    if cached_movie is not None:
        return cached_movie, "cached"

    # If it is not saved, request it from TMDb.
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"

    try:
        response = session.get(
            url,
            params={"api_key": TMDB_API_KEY},
            timeout=(3.05, 10)
        )

        # A 404 means TMDb could not find this movie ID.
        if response.status_code == 404:
            return None, "not_found"

        # Raise an error for other unsuccessful HTTP responses.
        response.raise_for_status()

        movie = response.json()

        # Save the successful response locally.
        cache_file = MOVIES_CACHE / f"{movie_id}.json"

        with open(cache_file, "w", encoding="utf-8") as file:
            json.dump(movie, file, indent=2)

        return movie, "downloaded"

    except requests.RequestException as error:
        return None, f"request_error: {error}"

def get_cached_credits(movie_id):
    cache_file = CREDITS_CACHE / f"{movie_id}.json"

    if cache_file.exists():
        with open(cache_file, "r", encoding="utf-8") as file:
            return json.load(file)

    return None


def fetch_credits(movie_id, session):
    cached_credits = get_cached_credits(movie_id)

    if cached_credits is not None:
        return cached_credits, "cached"

    url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits"

    try:
        response = session.get(
            url,
            params={"api_key": TMDB_API_KEY},
            timeout=(3.05, 10)
        )

        if response.status_code == 404:
            return None, "not_found"

        response.raise_for_status()

        credits = response.json()

        CREDITS_CACHE.mkdir(parents=True, exist_ok=True)

        cache_file = CREDITS_CACHE / f"{movie_id}.json"

        with open(cache_file, "w", encoding="utf-8") as file:
            json.dump(credits, file, indent=2)

        return credits, "downloaded"

    except requests.RequestException as error:
        return None, f"request_error: {error}"

def extract_all_movies():
    # Keep only numeric IDs and remove repeated IDs.
    valid_ids = movie_ids.loc[
        movie_ids["tmdb_id"].str.isdigit(),
        "tmdb_id"
    ].drop_duplicates().tolist()

    session = create_session()
    results = []

    for movie_id in valid_ids:
        movie, movie_status = fetch_movie(movie_id, session)

        if movie is not None:
            credits, credits_status = fetch_credits(movie_id, session)
        else:
            credits_status = "not_attempted"

        results.append({
            "tmdb_id": movie_id,
            "movie_status": movie_status,
            "credits_status": credits_status
        })

    results_df = pd.DataFrame(results)

    # Save the outcome of every extraction attempt.
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    results_df.to_csv(
        PROCESSED_DIR / "extraction_log.csv",
        index=False
    )

    print("Unique numeric IDs:", len(valid_ids))
    print("Extraction results:")
    print(results_df["movie_status"].value_counts())

    print("\nCredits results:")
    print(results_df["credits_status"].value_counts())

    return results_df


if __name__ == "__main__":
    extract_all_movies()
