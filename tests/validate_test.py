
import json
import pandas as pd

from pipeline.validate import validate
from pipeline.config import (
    CANDIDATE_LIST,
    PROCESSED_DIR,
    MOVIES_CACHE,
    CREDITS_CACHE
)


def test_all_candidates_are_accounted_for():

    candidates = validate()

    assert len(candidates) == 127

    assert candidates["candidate_status"].notna().all()

    assert candidates["candidate_status"].value_counts().to_dict() == {
        "numeric_unique": 117,
        "duplicate_numeric": 6,
        "invalid_non_numeric": 3,
        "blank": 1
    }


def test_candidate_merge_preserves_all_original_rows():

    candidates = validate()

    original_rows = sorted(candidates["original_row"].tolist())

    assert original_rows == list(range(1, 128))


def test_unique_numeric_ids_reconcile_with_extraction_log():

    candidates = pd.read_csv(
        CANDIDATE_LIST,
        dtype=str,
        keep_default_na=False,
        skip_blank_lines=False
    )

    extraction_results = pd.read_csv(
        PROCESSED_DIR / "extraction_log.csv",
        dtype=str,
        keep_default_na=False
    )

    numeric_ids = set(
        candidates.loc[
            candidates["tmdb_id"].str.fullmatch(r"\d+"),
            "tmdb_id"
        ]
    )

    extracted_ids = set(extraction_results["tmdb_id"])

    assert numeric_ids == extracted_ids


def test_successful_extractions_have_matching_movie_and_credits_files():

    extraction_results = pd.read_csv(
        PROCESSED_DIR / "extraction_log.csv",
        dtype=str,
        keep_default_na=False
    )

    successful_movies = extraction_results[
        extraction_results["movie_status"].isin(
            ["downloaded", "cached"]
        )
    ]

    for row in successful_movies.itertuples(index=False):

        movie_id = row.tmdb_id

        movie_file = MOVIES_CACHE / f"{movie_id}.json"
        credits_file = CREDITS_CACHE / f"{movie_id}.json"

        assert movie_file.exists()
        assert credits_file.exists()

        with open(movie_file, "r", encoding="utf-8") as file:
            movie = json.load(file)

        with open(credits_file, "r", encoding="utf-8") as file:
            credits = json.load(file)

        assert str(movie.get("id")) == movie_id
        assert str(credits.get("id")) == movie_id
