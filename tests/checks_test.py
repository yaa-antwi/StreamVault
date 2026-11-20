
import pandas as pd

from pipeline.checks import check_tables


def create_sample_tables():
    movies = pd.DataFrame({
        "tmdb_id": [str(i) for i in range(1, 11)],
        "revenue": ["0", ""] + ["1000000"] * 8,
        "release_year": ["2000"] * 10
    })

    genres = pd.DataFrame({
        "tmdb_id": ["1", "2"],
        "genre_name": ["Action", "Drama"]
    })

    companies = pd.DataFrame({
        "tmdb_id": ["1"],
        "company_name": ["Example Company"]
    })

    cast = pd.DataFrame({
        "tmdb_id": ["1"],
        "person_name": ["Actor One"]
    })

    crew = pd.DataFrame({
        "tmdb_id": ["2"],
        "person_name": ["Crew One"]
    })

    movie_cast = movies.merge(
        cast,
        on="tmdb_id",
        how="left",
        validate="one_to_many",
        indicator=True
    )

    movie_crew = movies.merge(
        crew,
        on="tmdb_id",
        how="left",
        validate="one_to_many",
        indicator=True
    )

    spot_check = movies.copy()

    return {
        "movies": movies,
        "genres": genres,
        "companies": companies,
        "cast": cast,
        "crew": crew,
        "movie_cast": movie_cast,
        "movie_crew": movie_crew,
        "spot_check": spot_check
    }


def test_valid_tables_pass_quality_checks():
    tables = create_sample_tables()

    report = check_tables(tables)

    assert not (report["status"] == "FAIL").any()


def test_duplicate_movie_ids_fail():
    tables = create_sample_tables()

    tables["movies"].loc[1, "tmdb_id"] = "1"

    report = check_tables(tables)

    result = report[
        report["check"] == "Unique movie records"
    ]

    assert result.iloc[0]["status"] == "FAIL"


def test_related_table_unknown_movie_id_fails():
    tables = create_sample_tables()

    tables["genres"].loc[0, "tmdb_id"] = "999"

    report = check_tables(tables)

    result = report[
        report["check"] == "genres movie references"
    ]

    assert result.iloc[0]["status"] == "FAIL"


def test_non_numeric_revenue_fails():
    tables = create_sample_tables()

    tables["movies"].loc[0, "revenue"] = "unknown"

    report = check_tables(tables)

    result = report[
        report["check"] == "Revenue values"
    ]

    assert result.iloc[0]["status"] == "FAIL"


def test_zero_and_blank_revenue_are_distinguished():
    tables = create_sample_tables()

    report = check_tables(tables)

    result = report[
        report["check"] == "Zero and blank revenue"
    ]

    details = result.iloc[0]["details"]

    assert "Zero revenue: 1" in details
    assert "Blank revenue: 1" in details


def test_join_that_loses_a_movie_fails():
    tables = create_sample_tables()

    tables["movie_cast"] = tables["movie_cast"].iloc[1:].copy()

    report = check_tables(tables)

    result = report[
        report["check"] == "movie_cast join"
    ]

    assert result.iloc[0]["status"] == "FAIL"
