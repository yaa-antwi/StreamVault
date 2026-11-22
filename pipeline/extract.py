import json
from datetime import datetime, timezone

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from pipeline.config import (
    TMDB_API_KEY,
    CANDIDATE_LIST,
    MOVIES_CACHE,
    CREDITS_CACHE,
    PROCESSED_DIR,
)


def load_candidate_list():
    """Load the original candidate list without changing its identifiers."""
    return pd.read_csv(
        CANDIDATE_LIST,
        dtype=str,
        keep_default_na=False,
        skip_blank_lines=False,
    )


def normalize_tmdb_id(movie_id):
    """Return a canonical string form of a numeric TMDb ID.

    The original candidate-list value is not changed. This normalized value is
    used for API requests, cache filenames, duplicate detection and matching
    extraction results back to the original candidate entries.
    """
    normalized_value = str(movie_id).strip()

    if not normalized_value.isdigit():
        raise ValueError(f"Invalid numeric TMDb ID: {normalized_value}")

    return str(int(normalized_value))


def create_session():
    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        respect_retry_after_header=True,
    )

    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.headers.update({"User-Agent": "StreamVault-Data-Pipeline"})

    return session


def fetch_data(movie_id, data_type, session):
    if data_type == "movie":
        folder = MOVIES_CACHE
        url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    else:
        folder = CREDITS_CACHE
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits"

    cache_file = folder / f"{movie_id}.json"
    metadata_file = folder / f"{movie_id}_metadata.json"

    if cache_file.exists():
        with open(cache_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        status = "cached"

    else:
        try:
            response = session.get(
                url,
                params={"api_key": TMDB_API_KEY},
                timeout=(3.05, 10),
            )

            if response.status_code == 404:
                return None, "not_found"

            response.raise_for_status()
            data = response.json()

            folder.mkdir(parents=True, exist_ok=True)

            with open(cache_file, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)

            status = "downloaded"
