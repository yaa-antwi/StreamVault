
import json
import pandas as pd

from pipeline.config import (
    CANDIDATE_LIST,
    MOVIES_CACHE,
    CREDITS_CACHE,
    PROCESSED_DIR
)


SUCCESS = ["downloaded", "cached"]


def validate():

    failures = []

    # 1. Read and classify the original candidates.
    candidates = pd.read_csv(
        CANDIDATE_LIST,
        dtype=str,
        keep_default_na=False,
        skip_blank_lines=False
    )

    candidates["original_row"] = range(1, len(candidates) + 1)
    candidates["original_tmdb_id"] = candidates["tmdb_id"]
    candidates["tmdb_id"] = candidates["tmdb_id"].str.strip()

    ids = candidates["tmdb_id"]
    numeric = ids.str.fullmatch(r"\d+")

    candidates["candidate_status"] = "invalid_non_numeric"
    candidates.loc[numeric, "candidate_status"] = "numeric_unique"
    candidates.loc[
        numeric & ids.duplicated(), "candidate_status"
    ] = "duplicate_numeric"

    candidates.loc[ids == "", "candidate_status"] = "blank"
    candidates.loc[ids == "N/A", "candidate_status"] = "missing_value_marker"
    candidates.loc[ids == "-1", "candidate_status"] = "invalid_looking_id"
    candidates.loc[
        ids.str.lower().str.startswith("tt"), "candidate_status"
    ] = "IMDb_id"

    # 2. Read the extraction log.
    log_path = PROCESSED_DIR / "extraction_log.csv"

    if not log_path.exists():
        raise FileNotFoundError("Run extraction before validation.")

    log = pd.read_csv(log_path, dtype=str, keep_default_na=False)

    required_columns = ["tmdb_id", "movie_status", "credits_status"]

    if not all(column in log.columns for column in required_columns):
        raise ValueError("Extraction log is missing required columns.")

    log["tmdb_id"] = log["tmdb_id"].str.strip()

    # 3. Check IDs.
    numeric_ids = set(ids[numeric])
    log_ids = set(log["tmdb_id"])

    if log["tmdb_id"].duplicated().any():
        failures.append("Duplicate IDs found in extraction log.")

    if numeric_ids != log_ids:
        failures.append(
            f"ID mismatch. Missing: {numeric_ids - log_ids}. "
            f"Unexpected: {log_ids - numeric_ids}"
        )

    # 4. Check extraction statuses.
    for column in ["movie_status", "credits_status"]:
        invalid = ~log[column].isin(SUCCESS + ["not_found"])

        if invalid.any():
            failures.append(f"Invalid or failed statuses in {column}.")

    # 5. Match results to every original candidate.
    candidates = candidates.merge(
        log,
        on="tmdb_id",
        how="left",
        validate="many_to_one"
    )

    candidates.loc[
        ~numeric, ["movie_status", "credits_status"]
    ] = "not_requested"

    # 6. Check downloaded movie and credits files.
    missing_financial_values = []

    for row in log.itertuples(index=False):

        movie_id = row.tmdb_id

        if row.movie_status not in SUCCESS:
            continue

        movie_file = MOVIES_CACHE / f"{movie_id}.json"
        credits_file = CREDITS_CACHE / f"{movie_id}.json"

        if not movie_file.exists():
            failures.append(f"Missing movie file: {movie_id}")
            continue

        if row.credits_status not in SUCCESS:
            failures.append(f"Missing credits response: {movie_id}")
            continue

        if not credits_file.exists():
            failures.append(f"Missing credits file: {movie_id}")
            continue

        try:
            with open(movie_file, encoding="utf-8") as file:
                movie = json.load(file)

            with open(credits_file, encoding="utf-8") as file:
                credits = json.load(file)

        except (OSError, json.JSONDecodeError):
            failures.append(f"Unreadable JSON file: {movie_id}")
            continue

        if not isinstance(movie, dict) or not isinstance(credits, dict):
            failures.append(f"Invalid JSON structure: {movie_id}")
            continue

        if str(movie.get("id")) != movie_id:
            failures.append(f"Movie ID mismatch: {movie_id}")

        if str(credits.get("id")) != movie_id:
            failures.append(f"Credits ID mismatch: {movie_id}")

        required_fields = [
            "title", "release_date", "budget",
            "revenue", "genres", "production_companies"
        ]

        for field in required_fields:
            if field not in movie:
                failures.append(f"Missing {field} for movie {movie_id}")

        if not isinstance(movie.get("title"), str) or not movie.get("title", "").strip():
            failures.append(f"Invalid title: {movie_id}")

        if not isinstance(movie.get("genres"), list):
            failures.append(f"Invalid genres: {movie_id}")

        if not isinstance(movie.get("production_companies"), list):
            failures.append(f"Invalid production companies: {movie_id}")

        for field in ["budget", "revenue"]:
            value = movie.get(field)

            if value is None:
                missing_financial_values.append((movie_id, field))
            elif not isinstance(value, (int, float)) or isinstance(value, bool):
                failures.append(f"Invalid {field}: {movie_id}")

        if not isinstance(credits.get("cast"), list):
            failures.append(f"Invalid cast: {movie_id}")

        if not isinstance(credits.get("crew"), list):
            failures.append(f"Invalid crew: {movie_id}")

    # 7. Display results.
    print("\nVALIDATION RESULTS")
    print("Original candidates:", len(candidates))

    print("\nCandidate classifications:")
    print(candidates["candidate_status"].value_counts())

    print("\nExtraction outcomes:")
    print(candidates["movie_status"].value_counts())

    print("\nMissing financial values:", len(missing_financial_values))

    if missing_financial_values:
        print(missing_financial_values)

    if failures:
        print("\nVALIDATION FAILURES")

        for failure in failures:
            print("-", failure)

        raise RuntimeError("Validation failed.")

    print("\nValidation completed successfully.")

    return candidates


if __name__ == "__main__":
    validate()
