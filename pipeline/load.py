
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


def check_quality_report(processed_dir):
    report_file = processed_dir / "checks_report.csv"

    if not report_file.exists():
        raise FileNotFoundError("Quality report not found.")

    report = pd.read_csv(report_file, keep_default_na=False)

    if report.empty or "status" not in report.columns:
        raise ValueError("Quality report is invalid.")

    if (report["status"].str.upper() == "FAIL").any():
        raise RuntimeError("Quality checks failed.")


def load(
    processed_dir=PROCESSED_DIR,
    final_dir=FINAL_DIR,
    candidate_list=CANDIDATE_LIST
):
    check_quality_report(processed_dir)

    files = [
        candidate_list,
        processed_dir / "extraction_log.csv",
        processed_dir / "checks_report.csv"
    ]

    files.extend(
        processed_dir / name for name in TRANSFORMED_FILES
    )

    missing = [file.name for file in files if not file.exists()]

    if missing:
        raise FileNotFoundError(f"Missing files: {missing}")

    final_dir.mkdir(parents=True, exist_ok=True)

    for file in files:
        shutil.copy2(file, final_dir / file.name)

    print("Loading completed.")
    print("Files published:", len(files))
    print("Final location:", final_dir)


if __name__ == "__main__":
    load()
