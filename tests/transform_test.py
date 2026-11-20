
import pandas as pd
from pipeline.transform import transform


def test_transformation_creates_all_tables():
    data = transform()

    expected_tables = [
        "movies",
        "genres",
        "companies",
        "cast",
        "crew",
        "movie_cast",
        "movie_crew",
        "spot_check"
    ]

    for table in expected_tables:
        assert table in data


def test_movie_table_has_one_row_per_movie():
    data = transform()

    assert data["movies"]["tmdb_id"].is_unique
    assert len(data["movies"]) == 112


def test_nested_records_are_kept_separate():
    data = transform()

    assert "genre_name" in data["genres"].columns
    assert "company_name" in data["companies"].columns
    assert "person_name" in data["cast"].columns
    assert "person_name" in data["crew"].columns


def test_franchise_and_standalone_are_identified():
    data = transform()

    movies = data["movies"]

    assert set(movies["licensing_type"].dropna()).issubset(
        {"franchise", "standalone"}
    )


def test_zero_and_missing_revenue_remain_distinct():
    data = transform()

    movies = data["movies"]

    zero_revenue = movies["revenue"].eq(0)
    missing_revenue = movies["revenue"].isna()

    assert not (zero_revenue & missing_revenue).any()


def test_joins_preserve_all_movie_ids():
    data = transform()

    movie_ids = set(data["movies"]["tmdb_id"])

    assert set(data["movie_cast"]["tmdb_id"]) == movie_ids
    assert set(data["movie_crew"]["tmdb_id"]) == movie_ids


def test_spot_check_is_reproducible():
    first = transform()["spot_check"]
    second = transform()["spot_check"]

    assert first["tmdb_id"].is_unique
    assert 10 <= len(first) <= 15

    pd.testing.assert_frame_equal(first, second)


def test_transformed_files_are_created():
    transform()

    from pipeline.config import PROCESSED_DIR

    expected_files = [
        "movies.csv",
        "movie_genres.csv",
        "movie_companies.csv",
        "movie_cast.csv",
        "movie_crew.csv",
        "movie_cast_joined.csv",
        "movie_crew_joined.csv",
        "spot_check_sample.csv"
    ]

    for filename in expected_files:
        assert (PROCESSED_DIR / filename).exists()
