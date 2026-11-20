
import json
import pandas as pd

from pipeline.config import (
    MOVIES_CACHE,
    CREDITS_CACHE,
    PROCESSED_DIR
)


SUCCESS_STATUSES = {"downloaded", "cached"}
SPOT_CHECK_SEED = 42


def create_spot_check_sample(
    movies,
    genres,
    companies,
    cast,
    crew
):
    selected = {}

    def add_record(movie_id, reason):
        if movie_id not in selected:
            selected[movie_id] = []

        if reason not in selected[movie_id]:
            selected[movie_id].append(reason)

    # 1. Select eight records using a fixed random seed.
    random_count = min(8, len(movies))

    random_ids = movies["tmdb_id"].sample(
        n=random_count,
        random_state=SPOT_CHECK_SEED
    ).tolist()

    for movie_id in random_ids:
        add_record(movie_id, "Fixed-seed random sample")

    # 2. Select the lowest and highest recorded revenue values.
    numeric_revenue = pd.to_numeric(
        movies["revenue"],
        errors="coerce"
    )

    available_revenue = numeric_revenue.dropna()

    if not available_revenue.empty:
        lowest_id = movies.loc[
            available_revenue.idxmin(), "tmdb_id"
        ]

        highest_id = movies.loc[
            available_revenue.idxmax(), "tmdb_id"
        ]

        add_record(lowest_id, "Lowest recorded revenue")
        add_record(highest_id, "Highest recorded revenue")

    # 3. Select the movie with the most related records.
    related_counts = pd.Series(
        0,
        index=movies["tmdb_id"],
        dtype="int64"
    )

    for table in [genres, companies, cast, crew]:
        counts = table.groupby("tmdb_id").size()
        related_counts = related_counts.add(
            counts,
            fill_value=0
        )

    most_transformed_id = related_counts.idxmax()

    add_record(
        most_transformed_id,
        "Most related genre, company, cast and crew records"
    )

    # 4. Select the earliest and latest release-year boundaries.
    numeric_years = pd.to_numeric(
        movies["release_year"],
        errors="coerce"
    )

    available_years = numeric_years.dropna()

    if not available_years.empty:
        earliest_id = movies.loc[
            available_years.idxmin(), "tmdb_id"
        ]

        latest_id = movies.loc[
            available_years.idxmax(), "tmdb_id"
        ]

        add_record(earliest_id, "Earliest release-year boundary")
        add_record(latest_id, "Latest release-year boundary")

    # 5. Ensure that at least ten records are selected when available.
    minimum_sample = min(10, len(movies))

    if len(selected) < minimum_sample:
        remaining = movies[
            ~movies["tmdb_id"].isin(selected)
        ]

        additional_count = minimum_sample - len(selected)

        additional_ids = remaining["tmdb_id"].sample(
            n=additional_count,
            random_state=SPOT_CHECK_SEED
        ).tolist()

        for movie_id in additional_ids:
            add_record(movie_id, "Additional fixed-seed sample")

    # 6. Create the spot-check table.
    title_lookup = movies.set_index("tmdb_id")["title"].to_dict()

    spot_check_records = []

    for movie_id, reasons in selected.items():
        spot_check_records.append({
            "tmdb_id": movie_id,
            "title": title_lookup.get(movie_id),
            "sample_reason": "; ".join(reasons),
            "discrepancy_class": "",
            "notes": ""
        })

    return pd.DataFrame(spot_check_records)


def transform():

    movie_records = []
    genre_records = []
    company_records = []
    cast_records = []
    crew_records = []

    # 1. Read the extraction log.
    extraction_log = pd.read_csv(
        PROCESSED_DIR / "extraction_log.csv",
        dtype=str,
        keep_default_na=False
    )

    # 2. Use only successfully retrieved movie records.
    successful_movies = extraction_log[
        extraction_log["movie_status"].isin(SUCCESS_STATUSES)
    ]

    movie_ids = successful_movies["tmdb_id"].tolist()

    if not movie_ids:
        raise RuntimeError(
            "There are no successfully extracted movies to transform."
        )

    # 3. Read each movie and its matching credits response.
    for movie_id in movie_ids:

        movie_file = MOVIES_CACHE / f"{movie_id}.json"
        credits_file = CREDITS_CACHE / f"{movie_id}.json"

        if not movie_file.exists():
            raise FileNotFoundError(
                f"Movie file not found for ID {movie_id}"
            )

        if not credits_file.exists():
            raise FileNotFoundError(
                f"Credits file not found for ID {movie_id}"
            )

        with open(movie_file, "r", encoding="utf-8") as file:
            movie = json.load(file)

        with open(credits_file, "r", encoding="utf-8") as file:
            credits = json.load(file)

        # Confirm that the responses belong to the requested movie.
        if str(movie.get("id")) != movie_id:
            raise ValueError(
                f"Movie ID mismatch for {movie_id}"
            )

        if str(credits.get("id")) != movie_id:
            raise ValueError(
                f"Credits ID mismatch for {movie_id}"
            )

        # 4. Extract collection information.
        collection = movie.get("belongs_to_collection")

        if isinstance(collection, dict):
            collection_id = collection.get("id")
            collection_name = collection.get("name")
        else:
            collection_id = None
            collection_name = None

        # A blank or null collection means standalone.
        if collection_id in (None, ""):
            licensing_type = "standalone"
        else:
            licensing_type = "franchise"

        # 5. Extract movie-level information.
        release_date = movie.get("release_date")

        if isinstance(release_date, str) and release_date:
            release_year = release_date[:4]
        else:
            release_year = None

        movie_records.append({
            "tmdb_id": movie_id,
            "title": movie.get("title"),
            "release_date": release_date,
            "release_year": release_year,
            "budget": movie.get("budget"),
            "revenue": movie.get("revenue"),
            "collection_id": collection_id,
            "collection_name": collection_name,
            "licensing_type": licensing_type
        })

        # 6. Extract genres into a separate table.
        for genre in movie.get("genres") or []:
            genre_records.append({
                "tmdb_id": movie_id,
                "genre_id": genre.get("id"),
                "genre_name": genre.get("name")
            })

        # 7. Extract production companies into a separate table.
        for company in movie.get("production_companies") or []:
            company_records.append({
                "tmdb_id": movie_id,
                "company_id": company.get("id"),
                "company_name": company.get("name"),
                "origin_country": company.get("origin_country")
            })

        # 8. Extract cast into a separate table.
        for person in credits.get("cast") or []:
            cast_records.append({
                "tmdb_id": movie_id,
                "person_id": person.get("id"),
                "person_name": person.get("name"),
                "character": person.get("character"),
                "cast_order": person.get("order")
            })

        # 9. Extract crew into a separate table.
        for person in credits.get("crew") or []:
            crew_records.append({
                "tmdb_id": movie_id,
                "person_id": person.get("id"),
                "person_name": person.get("name"),
                "department": person.get("department"),
                "job": person.get("job")
            })

    # 10. Create the separate DataFrames.
    movies_df = pd.DataFrame(
        movie_records,
        columns=[
            "tmdb_id",
            "title",
            "release_date",
            "release_year",
            "budget",
            "revenue",
            "collection_id",
            "collection_name",
            "licensing_type"
        ]
    )

    genres_df = pd.DataFrame(
        genre_records,
        columns=[
            "tmdb_id",
            "genre_id",
            "genre_name"
        ]
    )

    companies_df = pd.DataFrame(
        company_records,
        columns=[
            "tmdb_id",
            "company_id",
            "company_name",
            "origin_country"
        ]
    )

    cast_df = pd.DataFrame(
        cast_records,
        columns=[
            "tmdb_id",
            "person_id",
            "person_name",
            "character",
            "cast_order"
        ]
    )

    crew_df = pd.DataFrame(
        crew_records,
        columns=[
            "tmdb_id",
            "person_id",
            "person_name",
            "department",
            "job"
        ]
    )

    # 11. Keep movie IDs consistent across all tables.
    tables = [
        movies_df,
        genres_df,
        companies_df,
        cast_df,
        crew_df
    ]

    for table in tables:
        table["tmdb_id"] = table["tmdb_id"].astype("string")

    # Keep numeric values and unavailable values distinct.
    # Zero remains zero. None remains unavailable.
    movies_df["budget"] = pd.array(
        [record["budget"] for record in movie_records],
        dtype="Int64"
    )

    movies_df["revenue"] = pd.array(
        [record["revenue"] for record in movie_records],
        dtype="Int64"
    )

    movies_df["release_year"] = pd.array(
        [
            int(record["release_year"])
            if record["release_year"] else None
            for record in movie_records
        ],
        dtype="Int64"
    )

    movies_df["collection_id"] = pd.array(
        [record["collection_id"] for record in movie_records],
        dtype="Int64"
    )

    # 12. Prove the movie-to-cast and movie-to-crew joins.
    # Keep genres and companies separate to avoid multiplying rows
    # across several one-to-many relationships.
    movie_cast_df = movies_df.merge(
        cast_df,
        on="tmdb_id",
        how="left",
        validate="one_to_many",
        indicator=True
    )

    movie_crew_df = movies_df.merge(
        crew_df,
        on="tmdb_id",
        how="left",
        validate="one_to_many",
        indicator=True
    )

    # 13. Create the reproducible spot-check sample.
    spot_check_df = create_spot_check_sample(
        movies_df,
        genres_df,
        companies_df,
        cast_df,
        crew_df
    )

    # 14. Save the transformed tables.
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    movies_df.to_csv(
        PROCESSED_DIR / "movies.csv",
        index=False
    )

    genres_df.to_csv(
        PROCESSED_DIR / "movie_genres.csv",
        index=False
    )

    companies_df.to_csv(
        PROCESSED_DIR / "movie_companies.csv",
        index=False
    )

    cast_df.to_csv(
        PROCESSED_DIR / "movie_cast.csv",
        index=False
    )

    crew_df.to_csv(
        PROCESSED_DIR / "movie_crew.csv",
        index=False
    )

    movie_cast_df.to_csv(
        PROCESSED_DIR / "movie_cast_joined.csv",
        index=False
    )

    movie_crew_df.to_csv(
        PROCESSED_DIR / "movie_crew_joined.csv",
        index=False
    )

    spot_check_df.to_csv(
        PROCESSED_DIR / "spot_check_sample.csv",
        index=False
    )

    # 15. Display transformation results.
    print("\nTRANSFORMATION COMPLETED")

    print("Movies:", len(movies_df))
    print("Genres:", len(genres_df))
    print("Production companies:", len(companies_df))
    print("Cast records:", len(cast_df))
    print("Crew records:", len(crew_df))

    print("Movie and cast joined rows:", len(movie_cast_df))
    print("Movie and crew joined rows:", len(movie_crew_df))

    print("Spot-check records:", len(spot_check_df))

    return {
        "movies": movies_df,
        "genres": genres_df,
        "companies": companies_df,
        "cast": cast_df,
        "crew": crew_df,
        "movie_cast": movie_cast_df,
        "movie_crew": movie_crew_df,
        "spot_check": spot_check_df
    }


if __name__ == "__main__":
    transform()
