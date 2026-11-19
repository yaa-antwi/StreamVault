from pathlib import Path
import os
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT/"data"
CANDIDATE_LIST = DATA_DIR/ "id_list.csv"

load_dotenv(PROJECT_ROOT / ".env")

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
if not TMDB_API_KEY:
    raise ValueError("TMDB API key not found. Check your .env file.")

## print("API key loaded:", bool(TMDB_API_KEY))