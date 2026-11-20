
import pandas as pd
import pytest

from pipeline.transform import transform
from pipeline.config import PROCESSED_DIR


@pytest.fixture(scope="module")
def data():
    return transform()


def test_transformation_creates_all_tables(data):
    expected_tables = [
        "movies", "genres", "companies", "cast",
        "crew", "movie_cast", "movie_crew", "spot_check"
    ]

    for table in expected_tables:
        assert table in data


def test_movie_table_has_one_row_per_movie(data):
    movies = data["movies"]

    assert not movies.empty
    assert movies["tmdb_id"].notna().all()
    assert movies["tmdb_id"].is_unique


def test_nested_records_are_kept_separate(data):
    assert "genre_name" in data["genres"].columns
    assert "company_name" in data["companies"].columns
    assert "person_name" in data["cast"].columns
    assert "person_name" in data["crew"].columns


def test_franchise_and_standalone_are_identified(data):
    assert set(data["movies"]["licensing_type"].dropna()).issubset(
        {"franchise", "standalone"}
    )


def test_zero_and_missing_revenue_remain_distinct(data):
    movies = data["movies"]

    assert not (
        movies["revenue"].eq(0) & movies["revenue"].isna()
    ).any()


def test_joins_preserve_all_movie_ids(data):
    movie_ids = set(data["movies"]["tmdb_id"])

    assert set(data["movie_cast"]["tmdb_id"]) == movie_ids
    assert set(data["movie_crew"]["tmdb_id"]) == movie_ids


def test_spot_check_is_reproducible(data):
    second = transform()["spot_check"]

    assert data["spot_check"]["tmdb_id"].is_unique
    assert 10 <= len(data["spot_check"]) <= 15

    pd.testing.assert_frame_equal(data["spot_check"], second)


def test_transformed_files_are_created(data):
    expected_files = [
        "movies.csv", "movie_genres.csv", "movie_companies.csv",
        "movie_cast.csv", "movie_crew.csv",
        "movie_cast_joined.csv", "movie_crew_joined.csv",
        "spot_check_sample.csv"
    ]

    for filename in expected_files:
        assert (PROCESSED_DIR / filename).exists()
