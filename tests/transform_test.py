
import json
import pandas as pd
import pytest

import pipeline.transform as transform_module


@pytest.fixture
def sample_project(tmp_path, monkeypatch):

    movies_dir = tmp_path / "movies"
    credits_dir = tmp_path / "credits"
    processed_dir = tmp_path / "processed"

    movies_dir.mkdir()
    credits_dir.mkdir()
    processed_dir.mkdir()

    extraction_records = []

    # Create twelve sample movies and their credits.
    for number in range(101, 113):

        if number == 101:
            movie = {
                "id": number,
                "title": "Film A",
                "release_date": "1999-01-01",
                "budget": 100,
                "revenue": 0,
                "belongs_to_collection": {
                    "id": 900,
                    "name": "Franchise A"
                },
                "genres": [
                    {"id": 1, "name": "Action"},
                    {"id": 2, "name": "Drama"}
                ],
                "production_companies": [
                    {
                        "id": 11,
                        "name": "Company A",
                        "origin_country": "US"
                    },
                    {
                        "id": 12,
                        "name": "Company B",
                        "origin_country": "GB"
                    }
                ]
            }

            credits = {
                "id": number,
                "cast": [
                    {
                        "id": 201,
                        "name": "Actor A",
                        "character": "Hero",
                        "order": 0
                    },
                    {
                        "id": 202,
                        "name": "Actor B",
                        "character": "Friend",
                        "order": 1
                    }
                ],
                "crew": [
                    {
                        "id": 301,
                        "name": "Director A",
                        "department": "Directing",
                        "job": "Director"
                    }
                ]
            }

        elif number == 102:
            movie = {
                "id": number,
                "title": "Film B",
                "release_date": "2005-01-01",
                "budget": 50,
                "revenue": None,
                "belongs_to_collection": None,
                "genres": [
                    {"id": 3, "name": "Comedy"}
                ],
                "production_companies": []
            }

            credits = {
                "id": number,
                "cast": [],
                "crew": [
                    {
                        "id": 302,
                        "name": "Director B",
                        "department": "Directing",
                        "job": "Director"
                    }
                ]
            }

        else:
            movie = {
                "id": number,
                "title": f"Film {number}",
                "release_date": f"{2000 + number - 103}-01-01",
                "budget": 100,
                "revenue": number * 100,
                "belongs_to_collection": None,
                "genres": [
                    {"id": 4, "name": "Action"}
                ],
                "production_companies": []
            }

            credits = {
                "id": number,
                "cast": [
                    {
                        "id": number + 100,
                        "name": f"Actor {number}",
                        "character": "Character",
                        "order": 0
                    }
                ],
                "crew": [
                    {
                        "id": number + 200,
                        "name": f"Director {number}",
                        "department": "Directing",
                        "job": "Director"
                    }
                ]
            }

        with open(
            movies_dir / f"{number}.json",
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(movie, file)

        with open(
            credits_dir / f"{number}.json",
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(credits, file)

        extraction_records.append({
            "tmdb_id": str(number),
            "movie_status": "downloaded",
            "credits_status": "downloaded"
        })

    pd.DataFrame(extraction_records).to_csv(
        processed_dir / "extraction_log.csv",
        index=False
    )

    monkeypatch.setattr(
        transform_module,
        "MOVIES_CACHE",
        movies_dir
    )

    monkeypatch.setattr(
        transform_module,
        "CREDITS_CACHE",
        credits_dir
    )

    monkeypatch.setattr(
        transform_module,
        "PROCESSED_DIR",
        processed_dir
    )

    return processed_dir


def test_transformation_creates_all_tables(sample_project):

    data = transform_module.transform()

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

    assert len(data["movies"]) == 12


def test_movie_table_has_one_row_per_movie(sample_project):

    data = transform_module.transform()

    assert data["movies"]["tmdb_id"].is_unique
    assert len(data["movies"]) == 12


def test_nested_records_are_kept_in_separate_tables(sample_project):

    data = transform_module.transform()

    assert len(data["genres"]) == 13
    assert len(data["companies"]) == 2

    assert len(data["cast"]) == 12
    assert len(data["crew"]) == 12


def test_collection_data_identifies_franchise_and_standalone(sample_project):

    data = transform_module.transform()

    movies = data["movies"].set_index("tmdb_id")

    assert movies.loc["101", "licensing_type"] == "franchise"
    assert movies.loc["101", "collection_name"] == "Franchise A"

    assert movies.loc["102", "licensing_type"] == "standalone"
    assert pd.isna(movies.loc["102", "collection_id"])


def test_zero_and_unavailable_revenue_remain_distinct(sample_project):

    data = transform_module.transform()

    movies = data["movies"].set_index("tmdb_id")

    assert movies.loc["101", "revenue"] == 0
    assert pd.isna(movies.loc["102", "revenue"])


def test_movie_cast_and_crew_joins_preserve_movie_records(sample_project):

    data = transform_module.transform()

    movie_ids = set(data["movies"]["tmdb_id"])

    cast_movie_ids = set(data["movie_cast"]["tmdb_id"])
    crew_movie_ids = set(data["movie_crew"]["tmdb_id"])

    assert cast_movie_ids == movie_ids
    assert crew_movie_ids == movie_ids

    # Film 102 has no cast, so the left join retains it.
    film_b_cast = data["movie_cast"][
        data["movie_cast"]["tmdb_id"] == "102"
    ]

    assert len(film_b_cast) == 1
    assert film_b_cast.iloc[0]["_merge"] == "left_only"


def test_joined_row_counts_reflect_one_to_many_relationships(sample_project):

    data = transform_module.transform()

    # Film 101 has two cast members.
    # Film 102 has none, so it contributes one left-only row.
    # The other ten films each have one cast member.
    assert len(data["movie_cast"]) == 13

    # Each of the twelve films has one crew record.
    assert len(data["movie_crew"]) == 12


def test_spot_check_sample_is_reproducible_and_has_10_to_15_records(
    sample_project
):

    first_run = transform_module.transform()
    second_run = transform_module.transform()

    first_sample = first_run["spot_check"]
    second_sample = second_run["spot_check"]

    assert 10 <= len(first_sample) <= 15

    assert first_sample["tmdb_id"].is_unique

    assert first_sample["sample_reason"].ne("").all()

    pd.testing.assert_frame_equal(
        first_sample,
        second_sample
    )


def test_transformed_files_are_created(sample_project):

    transform_module.transform()

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
        assert (sample_project / filename).exists()
