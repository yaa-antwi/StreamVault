import pandas as pd

from pipeline.checks import check_tables


def create_sample_tables():
    ids = [str(i) for i in range(1, 11)]

    movies = pd.DataFrame({
        "tmdb_id": ids,
        "budget": ["100"] * 10,
        "revenue": ["0", ""] + ["500"] * 8,
        "release_year": ["2000"] * 10
    })

    related = pd.DataFrame({"tmdb_id": ids})

    return {
        "movies": movies,
        "genres": related.copy(),
        "companies": related.copy(),
        "cast": related.copy(),
        "crew": related.copy(),
        "movie_cast": related.copy(),
        "movie_crew": related.copy(),
        "spot_check": related.copy()
    }


def test_valid_tables_pass():
    report = check_tables(create_sample_tables())
    assert (report["status"] == "PASS").all()


def test_duplicate_movie_ids_fail():
    tables = create_sample_tables()
    tables["movies"].loc[1, "tmdb_id"] = "1"

    report = check_tables(tables)
    status = report.loc[
        report["check"] == "Movie IDs", "status"
    ].iloc[0]

    assert status == "FAIL"


def test_unknown_related_movie_id_fails():
    tables = create_sample_tables()
    tables["genres"].loc[0, "tmdb_id"] = "99"

    report = check_tables(tables)
    status = report.loc[
        report["check"] == "genres references", "status"
    ].iloc[0]

    assert status == "FAIL"


def test_nonnumeric_revenue_fails():
    tables = create_sample_tables()
    tables["movies"].loc[0, "revenue"] = "unknown"

    report = check_tables(tables)
    status = report.loc[
        report["check"] == "revenue", "status"
    ].iloc[0]

    assert status == "FAIL"


def test_zero_and_missing_revenue_are_distinguished():
    tables = create_sample_tables()
    report = check_tables(tables)

    details = report.loc[
        report["check"] == "Zero and missing revenue", "details"
    ].iloc[0]

    assert "Zero: 1" in details
    assert "missing: 1" in details


def test_zero_revenue_is_preserved():
    tables = create_sample_tables()
    report = check_tables(tables)

    status = report.loc[
        report["check"] == "Zero and missing revenue", "status"
    ].iloc[0]

    assert status == "PASS"


def test_invalid_revenue_fails_zero_and_missing_check():
    tables = create_sample_tables()
    tables["movies"].loc[0, "revenue"] = "unknown"

    report = check_tables(tables)

    status = report.loc[
        report["check"] == "Zero and missing revenue", "status"
    ].iloc[0]

    assert status == "FAIL"


def test_missing_movie_in_join_fails():
    tables = create_sample_tables()
    tables["movie_cast"] = tables["movie_cast"].iloc[:9]

    report = check_tables(tables)
    status = report.loc[
        report["check"] == "movie_cast join", "status"
    ].iloc[0]

    assert status == "FAIL"