
import pandas as pd
import pytest

import pipeline.load as load_module


def create_source_files(tmp_path, monkeypatch):
    processed_dir = tmp_path / "processed"
    final_dir = tmp_path / "final"
    candidate_list = tmp_path / "id_list.csv"

    processed_dir.mkdir()

    # Create the original candidate list.
    candidate_list.write_text(
        "tmdb_id\n550\n680\n",
        encoding="utf-8"
    )

    # Create the extraction log.
    (processed_dir / "extraction_log.csv").write_text(
        "tmdb_id,movie_status\n550,downloaded\n",
        encoding="utf-8"
    )

    # Create a passing quality report.
    pd.DataFrame({
        "check": ["Required tables", "Unique movie records"],
        "status": ["PASS", "PASS"],
        "details": ["Available", "All IDs are unique"]
    }).to_csv(
        processed_dir / "checks_report.csv",
        index=False
    )

    # Create the eight transformed files.
    for filename in load_module.TRANSFORMED_FILES:
        (processed_dir / filename).write_text(
            "tmdb_id\n550\n",
            encoding="utf-8"
        )

    monkeypatch.setattr(
        load_module,
        "PROCESSED_DIR",
        processed_dir
    )

    monkeypatch.setattr(
        load_module,
        "FINAL_DIR",
        final_dir
    )

    monkeypatch.setattr(
        load_module,
        "CANDIDATE_LIST",
        candidate_list
    )

    return processed_dir, final_dir, candidate_list


def test_load_copies_all_required_files(tmp_path, monkeypatch):
    processed_dir, final_dir, candidate_list = create_source_files(
        tmp_path,
        monkeypatch
    )

    load_module.load()

    expected_files = [
        candidate_list,
        processed_dir / "extraction_log.csv",
        processed_dir / "checks_report.csv"
    ]

    expected_files.extend(
        processed_dir / filename
        for filename in load_module.TRANSFORMED_FILES
    )

    assert final_dir.exists()
    assert len(list(final_dir.iterdir())) == 11

    for source_file in expected_files:
        destination = final_dir / source_file.name

        assert destination.exists()
        assert destination.read_bytes() == source_file.read_bytes()


def test_loading_stops_when_quality_check_fails(
    tmp_path,
    monkeypatch
):
    processed_dir, final_dir, candidate_list = create_source_files(
        tmp_path,
        monkeypatch
    )

    pd.DataFrame({
        "check": ["Unique movie records"],
        "status": ["FAIL"],
        "details": ["Duplicate IDs found"]
    }).to_csv(
        processed_dir / "checks_report.csv",
        index=False
    )

    with pytest.raises(RuntimeError):
        load_module.load()

    assert not final_dir.exists()


def test_loading_stops_when_required_file_is_missing(
    tmp_path,
    monkeypatch
):
    processed_dir, final_dir, candidate_list = create_source_files(
        tmp_path,
        monkeypatch
    )

    missing_file = processed_dir / "movies.csv"
    missing_file.unlink()

    with pytest.raises(FileNotFoundError):
        load_module.load()

    assert not final_dir.exists()


def test_loading_does_not_change_source_files(
    tmp_path,
    monkeypatch
):
    processed_dir, final_dir, candidate_list = create_source_files(
        tmp_path,
        monkeypatch
    )

    source_files = [
        candidate_list,
        *processed_dir.iterdir()
    ]

    original_contents = {
        file.name: file.read_bytes()
        for file in source_files
    }

    load_module.load()

    for source_file in source_files:
        assert source_file.read_bytes() == original_contents[
            source_file.name
        ]
