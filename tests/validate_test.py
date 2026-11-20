
import json
import pandas as pd

import pipeline.validate as validation
from pipeline.config import (
    CANDIDATE_LIST,
    PROCESSED_DIR
)


def test_all_candidates_are_accounted_for():
    candidates = validation.validate()

    assert len(candidates) == 127
    assert candidates["candidate_status"].notna().all()


def test_candidate_merge_preserves_original_rows():
    candidates = validation.validate()

    assert sorted(candidates["original_row"]) == list(range(1, 128))


def test_numeric_ids_match_extraction_log():
    candidates = pd.read_csv(
        CANDIDATE_LIST,
        dtype=str,
        keep_default_na=False
    )

    numeric_ids = set(
        candidates.loc[
            candidates["tmdb_id"].str.strip().str.isdigit(),
            "tmdb_id"
        ].str.strip()
    )

    log = pd.read_csv(PROCESSED_DIR / "extraction_log.csv", dtype=str)

    assert numeric_ids == set(log["tmdb_id"])


def test_missing_financial_values_are_allowed(tmp_path, monkeypatch):

    processed = tmp_path / "processed"
    movies = tmp_path / "movies"
    credits = tmp_path / "credits"

    processed.mkdir()
    movies.mkdir()
    credits.mkdir()

    candidate_file = tmp_path / "candidates.csv"

    pd.DataFrame({"tmdb_id": ["155"]}).to_csv(
        candidate_file, index=False
    )

    pd.DataFrame({
        "tmdb_id": ["155"],
        "movie_status": ["cached"],
        "credits_status": ["cached"]
    }).to_csv(processed / "extraction_log.csv", index=False)

    movie = {
        "id": 155,
        "title": "The Dark Knight",
        "release_date": "2008-07-18",
        "budget": None,
        "revenue": 1000000000,
        "genres": [],
        "production_companies": []
    }

    with open(movies / "155.json", "w") as file:
        json.dump(movie, file)

    with open(credits / "155.json", "w") as file:
        json.dump({"id": 155, "cast": [], "crew": []}, file)

    monkeypatch.setattr(validation, "CANDIDATE_LIST", candidate_file)
    monkeypatch.setattr(validation, "PROCESSED_DIR", processed)
    monkeypatch.setattr(validation, "MOVIES_CACHE", movies)
    monkeypatch.setattr(validation, "CREDITS_CACHE", credits)

    candidates = validation.validate()

    assert len(candidates) == 1
