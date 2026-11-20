import shutil
import pandas as pd

from pipeline.config import (
    CANDIDATE_LIST,
    PROCESSED_DIR,
    FINAL_DIR
)


TRANSFORMED_FILES = [
    "movies.csv",
    "movie_genres.csv",
    "movie_companies.csv",
    "movie_cast.csv",
    "movie_crew.csv",
    "movie_cast_joined.csv",
    "movie_crew_joined.csv",
    "spot_check_sample.csv"
]


def check_quality_report():
    report_file = PROCESSED_DIR / "checks_report.csv"

    if not report_file.exists():
        raise FileNotFoundError(
            "Quality report not found. Run the quality checks first."
        )

    report = pd.read_csv(
        report_file,
        keep_default_na=False
    )

    if report.empty or "status" not in report.columns:
        raise ValueError(
            "Quality report is empty or has no status column."
        )

    failed_checks = report[
        report["status"].str.strip().str.upper() == "FAIL"
    ]

    if not failed_checks.empty:
        raise RuntimeError(
            "Loading stopped because quality checks contain failures."
        )


def load():
    # 1. Confirm that the quality checks passed.
    check_quality_report()

    # 2. Identify all files to publish.
    files_to_copy = [
        CANDIDATE_LIST,
        PROCESSED_DIR / "extraction_log.csv",
        PROCESSED_DIR / "checks_report.csv"
    ]

    files_to_copy.extend(
        PROCESSED_DIR / filename
        for filename in TRANSFORMED_FILES
    )

    # 3. Confirm that every required file exists.
    missing_files = [
        file for file in files_to_copy
        if not file.exists()
    ]

    if missing_files:
        missing_names = [
            file.name for file in missing_files
        ]

        raise FileNotFoundError(
            f"Cannot load. Missing files: {missing_names}"
        )

    # 4. Create the final folder.
    FINAL_DIR.mkdir(parents=True, exist_ok=True)

    # 5. Copy the approved files.
    for source_file in files_to_copy:
        destination = FINAL_DIR / source_file.name

        shutil.copy2(
            source_file,
            destination
        )

    print("\n LOADING COMPLETED")
    print("Files published:", len(files_to_copy))
    print("Final location:", FINAL_DIR)


if __name__ == "__main__":
    load()