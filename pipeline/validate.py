
import json
import pandas as pd

from pipeline.config import (
    CANDIDATE_LIST,
    MOVIES_CACHE,
    CREDITS_CACHE,
    PROCESSED_DIR
)


SUCCESS_STATUSES = {"downloaded", "cached"}

REQUIRED_MOVIE_FIELDS = [
    "id",
    "title",
    "release_date",
    "budget",
    "revenue",
    "genres",
    "production_companies"
]


def validate(raise_on_failure=True):

    failures = []

    # 1. Read the original candidate list.
    candidates = pd.read_csv(
        CANDIDATE_LIST,
        dtype=str,
        keep_default_na=False,
        skip_blank_lines=False
    )

    if "tmdb_id" not in candidates.columns:
        raise ValueError("The candidate list must contain a tmdb_id column.")

    candidates["original_row"] = range(1, len(candidates) + 1)

    # Keep the original identifier value for traceability.
    candidates["original_tmdb_id"] = candidates["tmdb_id"]

    # Remove surrounding spaces for classification and matching.
    candidates["tmdb_id"] = candidates["tmdb_id"].str.strip()

    # 2. Classify every original candidate.
    is_blank = candidates["tmdb_id"].eq("")
    is_numeric = candidates["tmdb_id"].str.fullmatch(r"\d+")

    is_duplicate = (
        is_numeric
        & candidates["tmdb_id"].duplicated(keep="first")
    )

    candidates["candidate_status"] = "invalid_non_numeric"

    candidates.loc[is_blank, "candidate_status"] = "blank"

    candidates.loc[
        is_numeric & ~is_duplicate,
        "candidate_status"
    ] = "numeric_unique"

    candidates.loc[
        is_duplicate,
        "candidate_status"
    ] = "duplicate_numeric"

    # 3. Read the extraction log.
    extraction_log_path = PROCESSED_DIR / "extraction_log.csv"

    if not extraction_log_path.exists():
        raise FileNotFoundError(
            "extraction_log.csv was not found. Run extraction first."
        )

    extraction_results = pd.read_csv(
        extraction_log_path,
        dtype=str,
        keep_default_na=False
    )

    required_log_columns = [
        "tmdb_id",
        "movie_status",
        "credits_status"
    ]

    for column in required_log_columns:
        if column not in extraction_results.columns:
            raise ValueError(
                f"Extraction log is missing the {column} column."
            )

    extraction_results["tmdb_id"] = (
        extraction_results["tmdb_id"].str.strip()
    )

    # 4. Check that the extraction log has one row per requested ID.
    duplicate_log_ids = extraction_results[
        extraction_results["tmdb_id"].duplicated(keep=False)
    ]["tmdb_id"].unique().tolist()

    if duplicate_log_ids:
        failures.append(
            f"Duplicate IDs in extraction log: {duplicate_log_ids}"
        )
        raise RuntimeError("\n".join(failures))

    # 5. Reconcile original numeric IDs against the extraction log.
    unique_numeric_ids = set(
        candidates.loc[is_numeric, "tmdb_id"]
    )

    extraction_ids = set(extraction_results["tmdb_id"])

    missing_ids = unique_numeric_ids - extraction_ids
    unexpected_ids = extraction_ids - unique_numeric_ids

    if missing_ids:
        failures.append(
            f"IDs missing from extraction log: {sorted(missing_ids)}"
        )

    if unexpected_ids:
        failures.append(
            f"Unexpected IDs in extraction log: {sorted(unexpected_ids)}"
        )

    # 6. Match extraction results back to every original candidate row.
    candidates = candidates.merge(
        extraction_results,
        on="tmdb_id",
        how="left",
        validate="many_to_one"
    )

    # Identify candidates that were not sent to TMDb.
    not_attempted = candidates["candidate_status"].isin(
        ["blank", "invalid_non_numeric"]
    )

    candidates.loc[
        not_attempted, "movie_status"
    ] = "not_attempted_invalid_input"

    candidates.loc[
        not_attempted, "credits_status"
    ] = "not_attempted_invalid_input"

    # Identify numeric candidates without an extraction result.
    missing_from_log = (
        candidates["candidate_status"].isin(
            ["numeric_unique", "duplicate_numeric"]
        )
        & candidates["movie_status"].isna()
    )

    candidates.loc[
        missing_from_log, "movie_status"
    ] = "missing_from_extraction_log"

    candidates.loc[
        missing_from_log, "credits_status"
    ] = "missing_from_extraction_log"

    # 7. Check successful extraction responses and their cached files.
    successful_movies = extraction_results[
        extraction_results["movie_status"].isin(SUCCESS_STATUSES)
    ]

    movie_id_mismatches = []
    credits_id_mismatches = []
    missing_movie_fields = []
    missing_movie_files = []
    missing_credits_files = []

    for row in extraction_results.itertuples(index=False):

        movie_id = row.tmdb_id
        movie_status = row.movie_status
        credits_status = row.credits_status

        # A recorded request error means the candidate is unresolved.
        if movie_status.startswith("request_error"):
            failures.append(
                f"Movie request failed for {movie_id}: {movie_status}"
            )

        if credits_status.startswith("request_error"):
            failures.append(
                f"Credits request failed for {movie_id}: {credits_status}"
            )

        # Only downloaded or cached movie responses should have movie files.
        if movie_status not in SUCCESS_STATUSES:
            continue

        movie_file = MOVIES_CACHE / f"{movie_id}.json"

        if not movie_file.exists():
            missing_movie_files.append(movie_id)
            continue

        try:
            with open(movie_file, "r", encoding="utf-8") as file:
                movie = json.load(file)
        except (OSError, json.JSONDecodeError) as error:
            failures.append(
                f"Could not read movie file for {movie_id}: {error}"
            )
            continue

        # Check that the returned movie ID matches the requested ID.
        if str(movie.get("id")) != movie_id:
            movie_id_mismatches.append(movie_id)

        # Check that the required fields are present in the response.
        # A field being present does not mean its value must be non-blank.
        missing_fields = [
            field for field in REQUIRED_MOVIE_FIELDS
            if field not in movie
        ]

        if missing_fields:
            missing_movie_fields.append({
                "tmdb_id": movie_id,
                "missing_fields": missing_fields
            })

        # A successfully retrieved movie must have successful credits.
        if credits_status not in SUCCESS_STATUSES:
            failures.append(
                f"Credits were not successfully retrieved for {movie_id}: "
                f"{credits_status}"
            )
            continue

        credits_file = CREDITS_CACHE / f"{movie_id}.json"

        if not credits_file.exists():
            missing_credits_files.append(movie_id)
            continue

        try:
            with open(credits_file, "r", encoding="utf-8") as file:
                credits = json.load(file)
        except (OSError, json.JSONDecodeError) as error:
            failures.append(
                f"Could not read credits file for {movie_id}: {error}"
            )
            continue

        if str(credits.get("id")) != movie_id:
            credits_id_mismatches.append(movie_id)

    if missing_movie_files:
        failures.append(
            f"Missing movie files: {missing_movie_files}"
        )

    if missing_credits_files:
        failures.append(
            f"Missing credits files: {missing_credits_files}"
        )

    if movie_id_mismatches:
        failures.append(
            f"Movie ID mismatches: {movie_id_mismatches}"
        )

    if credits_id_mismatches:
        failures.append(
            f"Credits ID mismatches: {credits_id_mismatches}"
        )

    if missing_movie_fields:
        failures.append(
            f"Missing required movie fields: {missing_movie_fields}"
        )

    # 8. Display the validation results.
    print("\nCANDIDATE VALIDATION")
    print("Original candidate entries:", len(candidates))

    print("\nCandidate classifications:")
    print(candidates["candidate_status"].value_counts().to_string())

    print("\nExtraction results against original candidates:")
    print(candidates["movie_status"].value_counts().to_string())

    print("\nID reconciliation:")
    print("Unique numeric IDs in original list:", len(unique_numeric_ids))
    print("Unique IDs in extraction log:", len(extraction_ids))
    print("IDs missing from extraction log:", missing_ids)
    print("Unexpected IDs in extraction log:", unexpected_ids)

    print("\nResponse validation:")
    print("Movie ID mismatches:", movie_id_mismatches)
    print("Credits ID mismatches:", credits_id_mismatches)
    print("Missing movie fields:", missing_movie_fields)
    print("Missing movie files:", missing_movie_files)
    print("Missing credits files:", missing_credits_files)

    # 9. Stop the next stage if required validation has failed.
    if failures:
        print("\nVALIDATION FAILURES")
        for failure in failures:
            print("-", failure)

        if raise_on_failure:
            raise RuntimeError(
                "Validation failed. Review the results before transforming."
            )

    else:
        print("\nValidation completed successfully.")

    return candidates


if __name__ == "__main__":
    validate()
