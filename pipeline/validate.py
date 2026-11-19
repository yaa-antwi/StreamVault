
import pandas as pd
import json

from pipeline.config import (
    CANDIDATE_LIST,
    MOVIES_CACHE,
    CREDITS_CACHE,
    PROCESSED_DIR
)


def validate():
    # 1. Load and classify the original candidate list.
    candidates = pd.read_csv(
        CANDIDATE_LIST,
        dtype=str,
        keep_default_na=False,
        skip_blank_lines=False
    )

    candidates["original_row"] = range(1, len(candidates) + 1)

    is_numeric = candidates["tmdb_id"].str.isdigit()
    is_blank = candidates["tmdb_id"].eq("")
    is_duplicate = is_numeric & candidates["tmdb_id"].duplicated()

    candidates["candidate_status"] = "invalid_non_numeric"
    candidates.loc[is_blank, "candidate_status"] = "blank"
    candidates.loc[is_numeric, "candidate_status"] = "numeric_unique"
    candidates.loc[is_duplicate, "candidate_status"] = "duplicate_numeric"

    # 2. Load the extraction log.
    extraction_results = pd.read_csv(
        PROCESSED_DIR / "extraction_log.csv",
        dtype=str,
        keep_default_na=False
    )

    # Identify numeric IDs that TMDb could not find.
    not_found_ids = extraction_results.loc[
        extraction_results["movie_status"] == "not_found",
        "tmdb_id"
    ]

    print("\nNumeric IDs not found by TMDb:")
    print(not_found_ids.to_list())

    # 3. Match original candidates to extraction results.
    candidates = candidates.merge(
        extraction_results,
        on="tmdb_id",
        how="left",
        validate="many_to_one"
    )

    # 4. Check that every unique numeric candidate ID was attempted.
    original_ids = set(
        candidates.loc[
            candidates["candidate_status"].isin(
                ["numeric_unique", "duplicate_numeric"]
            ),
            "tmdb_id"
        ]
    )

    extracted_ids = set(extraction_results["tmdb_id"])

    missing_ids = original_ids - extracted_ids
    unexpected_ids = extracted_ids - original_ids

    # 5. Validate the saved movie and credits responses.
    movie_id_mismatches = []
    credits_id_mismatches = []
    missing_movie_fields = []

    required_movie_fields = [
        "id",
        "title",
        "release_date",
        "budget",
        "revenue",
        "genres",
        "production_companies"
    ]

    for movie_id in extraction_results["tmdb_id"]:
        movie_file = MOVIES_CACHE / f"{movie_id}.json"
        credits_file = CREDITS_CACHE / f"{movie_id}.json"

        if movie_file.exists():
            with open(movie_file, "r", encoding="utf-8") as file:
                movie = json.load(file)

            if str(movie.get("id")) != movie_id:
                movie_id_mismatches.append(movie_id)

            missing = [
                field for field in required_movie_fields
                if field not in movie
            ]

            if missing:
                missing_movie_fields.append({
                    "tmdb_id": movie_id,
                    "missing_fields": missing
                })

        if credits_file.exists():
            with open(credits_file, "r", encoding="utf-8") as file:
                credits = json.load(file)

            if str(credits.get("id")) != movie_id:
                credits_id_mismatches.append(movie_id)

    # 6. Check that retrieved movies have credits files.
    missing_credits = []

    for movie_id in extraction_results.loc[
        extraction_results["movie_status"].isin(["downloaded", "cached"]),
        "tmdb_id"
    ]:
        credits_file = CREDITS_CACHE / f"{movie_id}.json"

        if not credits_file.exists():
            missing_credits.append(movie_id)

    # 7. Print the validation results.
    print("\nOriginal candidate entries:", len(candidates))

    print("\nCandidate classifications:")
    print(candidates["candidate_status"].value_counts())

    print("\nExtraction results against original candidates:")
    print(
        candidates["movie_status"]
        .replace("", pd.NA)
        .value_counts(dropna=False)
    )

    print("\nID reconciliation:")
    print("Unique numeric IDs in original list:", len(original_ids))
    print("Unique IDs in extraction log:", len(extracted_ids))
    print("IDs missing from extraction log:", missing_ids)
    print("Unexpected IDs in extraction log:", unexpected_ids)

    print("\nResponse validation:")
    print("Movie ID mismatches:", movie_id_mismatches)
    print("Credits ID mismatches:", credits_id_mismatches)
    print("Missing movie fields:", missing_movie_fields)

    print("\nCredits files missing:", missing_credits)
    print("Number of missing credits files:", len(missing_credits))

    return candidates


if __name__ == "__main__":
    validate()
