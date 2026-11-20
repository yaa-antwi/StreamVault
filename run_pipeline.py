from pipeline.extract import extract_all_movies
from pipeline.validate import validate
from pipeline.transform import transform
from pipeline.checks import run_checks
from pipeline.load import load


def run_pipeline():

    print("STREAMVAULT DATA PIPELINE")

    stages = [
        ("EXTRACTING DATA", extract_all_movies),
        ("VALIDATING EXTRACTED DATA", validate),
        ("TRANSFORMING DATA", transform),
        ("RUNNING QUALITY CHECKS", run_checks),
        ("LOADING FINAL DATA", load),
    ]

    for number, (stage_name, stage_function) in enumerate(stages, start=1):
        print(f"\n[STAGE {number}/5] {stage_name}")

        try:
            stage_function()
            print(f"[SUCCESS] {stage_name} completed.")

        except Exception as error:
            print(f"[FAILED] {stage_name}: {error}")
            raise

    print("\nSTREAMVAULT PIPELINE COMPLETED")


if __name__ == "__main__":
    run_pipeline()