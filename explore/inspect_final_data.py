
import pandas as pd

from pipeline.config import FINAL_DIR


expected_files = [
    "id_list.csv",
    "extraction_log.csv",
    "checks_report.csv",
    "movies.csv",
    "movie_genres.csv",
    "movie_companies.csv",
    "movie_cast.csv",
    "movie_crew.csv",
    "movie_cast_joined.csv",
    "movie_crew_joined.csv",
    "spot_check_sample.csv"
]


print("\nFINAL OUTPUT INSPECTION")

if not FINAL_DIR.exists():
    raise FileNotFoundError("The final folder does not exist.")

actual_files = {
    file.name
    for file in FINAL_DIR.glob("*.csv")
}

missing_files = set(expected_files) - actual_files
unexpected_files = actual_files - set(expected_files)

print("\nFiles found:", len(actual_files))
print("Files expected:", len(expected_files))

if missing_files:
    print("\nMissing files:", sorted(missing_files))

if unexpected_files:
    print("\nUnexpected files:", sorted(unexpected_files))

print("\nFILE DETAILS")

for filename in expected_files:
    file_path = FINAL_DIR / filename

    if not file_path.exists():
        continue

    df = pd.read_csv(file_path, keep_default_na=False)

    print(f"\n{filename}")
    print("Rows:", len(df))
    print("Columns:", list(df.columns))

print("\nINSPECTION COMPLETED")
