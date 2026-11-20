from pathlib import Path
import os
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Project directories
DATA_DIR = PROJECT_ROOT / "data"
CANDIDATE_LIST = DATA_DIR / "id_list.csv"
RAW_DIR = DATA_DIR / "raw"
MOVIES_CACHE = RAW_DIR / "movies"
CREDITS_CACHE = RAW_DIR / "credits"
PROCESSED_DIR = DATA_DIR / "processed"
FINAL_DIR = DATA_DIR / "final"

# Environment configuration
load_dotenv(PROJECT_ROOT / ".env")

TMDB_API_KEY = os.getenv("TMDB_API_KEY")


def get_api_key():
    """Return the TMDB API key or raise a clear error."""
    if not TMDB_API_KEY:
        raise ValueError(
            "TMDB API key not found. Check that TMDB_API_KEY "
            "is set in your .env file."
        )

    return TMDB_API_KEY