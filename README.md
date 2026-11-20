# StreamVault

## Project overview

This project analyses StreamVault's film licensing candidates using movie data retrieved from TMdb.

The work includes extracting, validating, transforming, checking and loading the data, then analysing franchise and standalone film performance.

The original list contained 127 entries. After accounting for duplicates and invalid IDs, 117 unique valid IDs remained. Of these, 112 titles were retrieved and 5 could not be found.

## Project structure

```text
StreamVault/
├── analysis/
├── data/
├── docs/
├── explore/
├── pipeline/
├── tests/
├── .env
├── .gitignore
├── requirements.txt
└── run_pipeline.py
```

## How to run the project

Run these commands from the main `StreamVault` folder.

**1. Create a virtual environment**

```bash
python -m venv venv
```

**2. Activate it (Windows)**

```bash
venv\Scripts\activate
```

**3. Install the required packages**

```bash
pip install -r requirements.txt
```

**4. Set up your TMdb API key**

Create a `.env` file in the project folder and add:

```text
TMdb_API_KEY=your_api_key
```

**5. Run the data pipeline**

```bash
python run_pipeline.py
```

This runs the five stages in order: extraction, validation, transformation, quality checks and loading.

**6. Run the licensing analysis**

After the pipeline completes, run:

```bash
python analysis/licensing_analysis.py
```

**7. Run the tests**

```bash
pytest
```

## Main outputs

- `data/raw/` – retrieved movie and credits data.
- `data/processed/` – extraction log and candidate reconciliation.
- `data/final/` – prepared data used for analysis.
- `docs/` – findings, client memo, questions, improvement and decision records.

The analysis compares franchise and standalone films across all years and from 2000 onward. It provides historical evidence for licensing discussions, not a final decision on the proposed $14 million spend.