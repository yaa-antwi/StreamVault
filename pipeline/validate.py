import pandas as pd
import json

from pipeline.config import (
    CANDIDATE_LIST,
    MOVIES_CACHE,
    CREDITS_CACHE,
    PROCESSED_DIR
)

# Load the original candidate list.
candidates = pd.read_csv(
    CANDIDATE_LIST,
    dtype=str,
    keep_default_na=False,
    skip_blank_lines=False
)

# Give every original row a reference number.
candidates["original_row"] = range(1, len(candidates) + 1)

# Identify numeric and blank IDs.
is_numeric = candidates["tmdb_id"].str.isdigit()
is_blank = candidates["tmdb_id"].eq("")

# Identify repeated numeric IDs.
is_duplicate = is_numeric & candidates["tmdb_id"].duplicated()

# Classify every original entry.
candidates["candidate_status"] = "invalid_non_numeric"
candidates.loc[is_blank, "candidate_status"] = "blank"
candidates.loc[is_numeric, "candidate_status"] = "numeric_unique"
candidates.loc[is_duplicate, "candidate_status"] = "duplicate_numeric"

print("Original candidate entries:", len(candidates))

print("\nCandidate classifications:")
print(candidates["candidate_status"].value_counts())

print("\nNon-numeric entries:")
print(
    candidates.loc[
        candidates["candidate_status"].isin(
            ["blank", "invalid_non_numeric"]
        ),
        ["original_row", "tmdb_id", "candidate_status"]
    ]
)

# Load the extraction results.
extraction_results = pd.read_csv(
    PROCESSED_DIR / "extraction_log.csv",
    dtype={"tmdb_id": str}
)

# Match the original candidate IDs to extraction results.
candidates = candidates.merge(
    extraction_results,
    on="tmdb_id",
    how="left"
)

print("\nExtraction results against original candidates:")
print(candidates["movie_status"].value_counts(dropna=False))

# Check whether the extraction log contains every unique numeric ID.
original_ids = set(
    candidates.loc[
        candidates["candidate_status"].isin(
            ["numeric_unique", "duplicate_numeric"]
        ),
        "tmdb_id"
    ]
)

extracted_ids = set(extraction_results["tmdb_id"])

print("\nID reconciliation:")
print("Unique numeric IDs in original list:", len(original_ids))
print("Unique IDs in extraction log:", len(extracted_ids))
print("IDs missing from extraction log:", original_ids - extracted_ids)
print("Unexpected IDs in extraction log:", extracted_ids - original_ids)

# Check that each saved response contains the requested movie ID.
movie_id_mismatches = []
credits_id_mismatches = []

for movie_id in extraction_results["tmdb_id"]:
    movie_file = MOVIES_CACHE / f"{movie_id}.json"
    credits_file = CREDITS_CACHE / f"{movie_id}.json"

    if movie_file.exists():
        with open(movie_file, "r", encoding="utf-8") as file:
            movie = json.load(file)

        if str(movie.get("id")) != movie_id:
            movie_id_mismatches.append(movie_id)

    if credits_file.exists():
        with open(credits_file, "r", encoding="utf-8") as file:
            credits = json.load(file)

        if str(credits.get("id")) != movie_id:
            credits_id_mismatches.append(movie_id)

print("\nResponse ID checks:")
print("Movie ID mismatches:", movie_id_mismatches)
print("Credits ID mismatches:", credits_id_mismatches)

# Check that each saved response contains the requested movie ID.
movie_id_mismatches = []
credits_id_mismatches = []

for movie_id in extraction_results["tmdb_id"]:
    movie_file = MOVIES_CACHE / f"{movie_id}.json"
    credits_file = CREDITS_CACHE / f"{movie_id}.json"

    if movie_file.exists():
        with open(movie_file, "r", encoding="utf-8") as file:
            movie = json.load(file)

        if str(movie.get("id")) != movie_id:
            movie_id_mismatches.append(movie_id)

    if credits_file.exists():
        with open(credits_file, "r", encoding="utf-8") as file:
            credits = json.load(file)

        if str(credits.get("id")) != movie_id:
            credits_id_mismatches.append(movie_id)

print("\nResponse ID checks:")
print("Movie ID mismatches:", movie_id_mismatches)
print("Credits ID mismatches:", credits_id_mismatches)