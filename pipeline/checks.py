
import pandas as pd

from pipeline.config import PROCESSED_DIR


def add_check(results, check_name, status, details):
    results.append({
        "check": check_name,
        "status": status,
        "details": details
    })


def check_tables(tables):
    results = []

    required_tables = [
        "movies",
        "genres",
        "companies",
        "cast",
        "crew",
        "movie_cast",
        "movie_crew",
        "spot_check"
    ]

    required_columns = {
        "movies": ["tmdb_id", "revenue", "release_year"],
        "genres": ["tmdb_id"],
        "companies": ["tmdb_id"],
        "cast": ["tmdb_id"],
        "crew": ["tmdb_id"],
        "movie_cast": ["tmdb_id"],
        "movie_crew": ["tmdb_id"],
        "spot_check": ["tmdb_id"]
    }

    # 1. Confirm that all expected tables exist.
    missing_tables = [
        name for name in required_tables
        if name not in tables
    ]

    if missing_tables:
        add_check(
            results,
            "Required tables",
            "FAIL",
            f"Missing tables: {missing_tables}"
        )
        return pd.DataFrame(results)

    add_check(
        results,
        "Required tables",
        "PASS",
        "All eight transformed tables are available."
    )

    # 2. Confirm that all required columns exist.
    missing_columns = []

    for table_name, columns in required_columns.items():
        for column in columns:
            if column not in tables[table_name].columns:
                missing_columns.append(
                    f"{table_name}.{column}"
                )

    if missing_columns:
        add_check(
            results,
            "Required columns",
            "FAIL",
            f"Missing columns: {missing_columns}"
        )
        return pd.DataFrame(results)

    add_check(
        results,
        "Required columns",
        "PASS",
        "All required columns are available."
    )

    movies = tables["movies"]

    movie_ids = movies["tmdb_id"].astype("string")
    valid_movie_ids = set(movie_ids.dropna())

    # 3. Check that each movie appears only once.
    duplicate_count = movie_ids.duplicated().sum()
    blank_ids = movie_ids.isna() | movie_ids.str.strip().eq("")

    if duplicate_count > 0 or blank_ids.any():
        add_check(
            results,
            "Unique movie records",
            "FAIL",
            f"Duplicates: {duplicate_count}. Blank IDs: {blank_ids.sum()}."
        )
    else:
        add_check(
            results,
            "Unique movie records",
            "PASS",
            f"{len(movies)} movies have unique, non-blank IDs."
        )

    # 4. Check that related records refer to existing movies.
    related_tables = [
        "genres",
        "companies",
        "cast",
        "crew"
    ]

    for table_name in related_tables:
        related_ids = set(
            tables[table_name]["tmdb_id"].astype("string").dropna()
        )

        unknown_ids = related_ids - valid_movie_ids

        if unknown_ids:
            add_check(
                results,
                f"{table_name} movie references",
                "FAIL",
                f"Unknown movie IDs: {sorted(unknown_ids)}"
            )
        else:
            add_check(
                results,
                f"{table_name} movie references",
                "PASS",
                "All records refer to movies in the movie table."
            )

    # 5. Check revenue values without treating blanks as zero.
    revenue = movies["revenue"].astype("string")

    blank_revenue = (
        revenue.isna() |
        revenue.str.strip().eq("")
    )

    numeric_revenue = pd.to_numeric(
        revenue.mask(blank_revenue),
        errors="coerce"
    )

    invalid_revenue = (
        ~blank_revenue &
        numeric_revenue.isna()
    )

    zero_revenue = numeric_revenue.eq(0)
    negative_revenue = numeric_revenue.lt(0)

    if invalid_revenue.any():
        add_check(
            results,
            "Revenue values",
            "FAIL",
            f"{invalid_revenue.sum()} non-blank revenue values are not numeric."
        )
    else:
        add_check(
            results,
            "Revenue values",
            "PASS",
            "All non-blank revenue values are numeric."
        )

    add_check(
        results,
        "Zero and blank revenue",
        "PASS",
        f"Zero revenue: {zero_revenue.sum()}. "
        f"Blank revenue: {blank_revenue.sum()}."
    )

    if negative_revenue.any():
        add_check(
            results,
            "Negative revenue",
            "WARN",
            f"{negative_revenue.sum()} negative revenue values need investigation."
        )
    else:
        add_check(
            results,
            "Negative revenue",
            "PASS",
            "No negative revenue values found."
        )

    # 6. Check release-year values.
    years = movies["release_year"].astype("string")

    blank_years = (
        years.isna() |
        years.str.strip().eq("")
    )

    numeric_years = pd.to_numeric(
        years.mask(blank_years),
        errors="coerce"
    )

    invalid_years = (
        ~blank_years &
        numeric_years.isna()
    )

    if invalid_years.any():
        add_check(
            results,
            "Release-year values",
            "FAIL",
            f"{invalid_years.sum()} non-blank release years are not numeric."
        )
    else:
        add_check(
            results,
            "Release-year values",
            "PASS",
            f"All non-blank release years are numeric. "
            f"Blank years: {blank_years.sum()}."
        )

    # 7. Check that joins preserve all movie records
    # and have the expected number of rows.
    for joined_name, related_name in [
        ("movie_cast", "cast"),
        ("movie_crew", "crew")
    ]:
        joined = tables[joined_name]
        related = tables[related_name]

        joined_ids = set(
            joined["tmdb_id"].astype("string").dropna()
        )

        missing_movie_ids = valid_movie_ids - joined_ids

        related_counts = related.groupby("tmdb_id").size()

        expected_rows = sum(
            max(related_counts.get(movie_id, 0), 1)
            for movie_id in valid_movie_ids
        )

        if missing_movie_ids or len(joined) != expected_rows:
            add_check(
                results,
                f"{joined_name} join",
                "FAIL",
                f"Missing movie IDs: {len(missing_movie_ids)}. "
                f"Expected rows: {expected_rows}. "
                f"Actual rows: {len(joined)}."
            )
        else:
            add_check(
                results,
                f"{joined_name} join",
                "PASS",
                f"All movies preserved. Expected and actual rows: {expected_rows}."
            )

    # 8. Check the spot-check sample.
    spot_check = tables["spot_check"]

    sample_ids = set(
        spot_check["tmdb_id"].astype("string").dropna()
    )

    unknown_sample_ids = sample_ids - valid_movie_ids

    if 10 <= len(spot_check) <= 15 and not unknown_sample_ids:
        add_check(
            results,
            "Spot-check sample",
            "PASS",
            f"{len(spot_check)} records selected from the movie table."
        )
    else:
        add_check(
            results,
            "Spot-check sample",
            "FAIL",
            f"Sample size: {len(spot_check)}. "
            f"Unknown movie IDs: {len(unknown_sample_ids)}."
        )

    return pd.DataFrame(results)


def run_checks():
    file_names = {
        "movies": "movies.csv",
        "genres": "movie_genres.csv",
        "companies": "movie_companies.csv",
        "cast": "movie_cast.csv",
        "crew": "movie_crew.csv",
        "movie_cast": "movie_cast_joined.csv",
        "movie_crew": "movie_crew_joined.csv",
        "spot_check": "spot_check_sample.csv"
    }

    tables = {}

    # Read the transformed CSV files.
    # keep_default_na=False preserves blank values as blanks.
    for table_name, file_name in file_names.items():
        file_path = PROCESSED_DIR / file_name

        if not file_path.exists():
            raise FileNotFoundError(
                f"Transformed file not found: {file_path}"
            )

        tables[table_name] = pd.read_csv(
            file_path,
            dtype={"tmdb_id": "string"},
            keep_default_na=False
        )

    report = check_tables(tables)

    # Save the quality-check report.
    report.to_csv(
        PROCESSED_DIR / "checks_report.csv",
        index=False
    )

    print("\nQUALITY CHECK RESULTS")
    print(report.to_string(index=False))

    failures = report[report["status"] == "FAIL"]

    if not failures.empty:
        raise RuntimeError(
            f"Quality checks failed: {len(failures)} failure(s)."
        )

    print("\nQuality checks completed successfully.")

    return report


if __name__ == "__main__":
    run_checks()
