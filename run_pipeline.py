
from pipeline.extract import extract_all_movies
from pipeline.validate import validate
from pipeline.transform import transform
from pipeline.checks import run_checks
from pipeline.load import load


def run_pipeline():

    print("STREAMVAULT DATA PIPELINE")

    # Stage 1: Extract
    print("\n[STAGE 1/5] EXTRACTING DATA")
    extract_all_movies()

    # Stage 2: Validate
    print("\n[STAGE 2/5] VALIDATING EXTRACTED DATA")
    validate()

    # Stage 3: Transform
    print("\n[STAGE 3/5] TRANSFORMING DATA")
    transform()

    # Stage 4: Quality checks
    print("\n[STAGE 4/5] RUNNING QUALITY CHECKS")
    run_checks()

    # Stage 5: Load
    print("\n[STAGE 5/5] LOADING FINAL DATA")
    load()

    print("\nSTREAMVAULT PIPELINE COMPLETED")


if __name__ == "__main__":
    run_pipeline()
