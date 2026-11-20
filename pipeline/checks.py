
import pandas as pd
from pipeline.config import PROCESSED_DIR


def check_tables(tables):
    results = []

    required = [
        "movies", "genres", "companies", "cast",
        "crew", "movie_cast", "movie_crew", "spot_check"
    ]

    for name in required:
        if name not in tables:
            results.append(["Required tables", "FAIL", f"{name} missing"])
            return pd.DataFrame(results, columns=["check", "status", "details"])

    movies = tables["movies"]
    movie_ids = movies["tmdb_id"].astype("string")
    valid_ids = set(movie_ids.dropna())

    def add(name, passed, details):
        results.append([
            name, "PASS" if passed else "FAIL", details
        ])

    # Movie IDs must be present and unique.
    add(
        "Movie IDs",
        movie_ids.notna().all()
        and movie_ids.str.strip().ne("").all()
        and movie_ids.is_unique,
        "Check for blank and duplicate movie IDs."
    )

    # Related records must refer to existing movies.
    for name in ["genres", "companies", "cast", "crew"]:
        ids = tables[name]["tmdb_id"].astype("string")
        valid = (
            ids.notna().all()
            and ids.str.strip().ne("").all()
            and set(ids).issubset(valid_ids)
        )
        add(name + " references", valid, "Check movie IDs.")

    # Financial values must be numeric when present.
    for column in ["budget", "revenue"]:
        values = movies[column].replace("", pd.NA)
        numeric = pd.to_numeric(values, errors="coerce")
        valid = (values.isna() | numeric.notna()).all()

        add(column, valid, "Non-blank values must be numeric.")

        if column == "revenue":
            add(
                "Zero and missing revenue",
                True,
                f"Zero: {numeric.eq(0).sum()}; "
                f"missing: {numeric.isna().sum()}."
            )

    # Release years must be numeric when present.
    years = movies["release_year"].replace("", pd.NA)
    numeric_years = pd.to_numeric(years, errors="coerce")

    add(
        "Release years",
        (years.isna() | numeric_years.notna()).all(),
        f"Missing: {years.isna().sum()}."
    )

    # Joined tables must retain every movie.
    for name in ["movie_cast", "movie_crew"]:
        joined_ids = set(tables[name]["tmdb_id"].dropna())
        add(
            name + " join",
            valid_ids.issubset(joined_ids),
            "Every movie must remain in the joined table."
        )

    # Spot-check sample must contain 10–15 unique movie IDs.
    sample = tables["spot_check"]
    add(
        "Spot-check sample",
        10 <= len(sample) <= 15
        and sample["tmdb_id"].is_unique,
        f"Sample contains {len(sample)} records."
    )

    return pd.DataFrame(
        results, columns=["check", "status", "details"]
    )


def run_checks():
    files = {
        "movies": "movies.csv",
        "genres": "movie_genres.csv",
        "companies": "movie_companies.csv",
        "cast": "movie_cast.csv",
        "crew": "movie_crew.csv",
        "movie_cast": "movie_cast_joined.csv",
        "movie_crew": "movie_crew_joined.csv",
        "spot_check": "spot_check_sample.csv"
    }

    tables = {
        name: pd.read_csv(
            PROCESSED_DIR / filename,
            dtype={"tmdb_id": "string"},
            keep_default_na=False
        )
        for name, filename in files.items()
    }

    report = check_tables(tables)
    report.to_csv(PROCESSED_DIR / "checks_report.csv", index=False)

    print(report.to_string(index=False))

    if (report["status"] == "FAIL").any():
        raise RuntimeError("Quality checks failed.")

    print("Quality checks completed.")


if __name__ == "__main__":
    run_checks()
