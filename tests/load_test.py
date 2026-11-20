
import pandas as pd
import pytest

from pipeline.load import load, TRANSFORMED_FILES


def create_source_files(tmp_path):
    processed = tmp_path / "processed"
    final = tmp_path / "final"
    candidate = tmp_path / "id_list.csv"

    processed.mkdir()

    candidate.write_text("tmdb_id\n550\n680\n", encoding="utf-8")

    (processed / "extraction_log.csv").write_text(
        "tmdb_id,movie_status\n550,downloaded\n",
        encoding="utf-8"
    )

    pd.DataFrame({
        "check": ["Movie IDs"],
        "status": ["PASS"],
        "details": ["Unique IDs"]
    }).to_csv(processed / "checks_report.csv", index=False)

    for name in TRANSFORMED_FILES:
        (processed / name).write_text("tmdb_id\n550\n")

    return processed, final, candidate


def test_load_copies_all_files(tmp_path):
    processed, final, candidate = create_source_files(tmp_path)

    load(processed, final, candidate)

    assert len(list(final.iterdir())) == 11

    for file in [candidate, *processed.iterdir()]:
        assert (final / file.name).read_bytes() == file.read_bytes()


def test_loading_stops_when_quality_check_fails(tmp_path):
    processed, final, candidate = create_source_files(tmp_path)

    pd.DataFrame({
        "check": ["Movie IDs"],
        "status": ["FAIL"],
        "details": ["Duplicate IDs"]
    }).to_csv(processed / "checks_report.csv", index=False)

    with pytest.raises(RuntimeError):
        load(processed, final, candidate)

    assert not final.exists()


def test_loading_stops_when_file_is_missing(tmp_path):
    processed, final, candidate = create_source_files(tmp_path)

    (processed / "movies.csv").unlink()

    with pytest.raises(FileNotFoundError):
        load(processed, final, candidate)

    assert not final.exists()


def test_loading_stops_when_quality_report_is_missing(tmp_path):
    processed, final, candidate = create_source_files(tmp_path)

    (processed / "checks_report.csv").unlink()

    with pytest.raises(FileNotFoundError):
        load(processed, final, candidate)

    assert not final.exists()


def test_loading_does_not_change_source_files(tmp_path):
    processed, final, candidate = create_source_files(tmp_path)

    original = {
        file.name: file.read_bytes()
        for file in [candidate, *processed.iterdir()]
    }

    load(processed, final, candidate)

    for file in [candidate, *processed.iterdir()]:
        assert file.read_bytes() == original[file.name]
