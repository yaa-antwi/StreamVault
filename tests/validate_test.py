
from pipeline.validate import validate

def test_all_candidates_are_accounted_for():
    candidates = validate()

    assert len(candidates) == 127

    assert candidates["candidate_status"].notna().all()

    assert candidates["candidate_status"].value_counts().to_dict() == {
        "numeric_unique": 117,
        "duplicate_numeric": 6,
        "invalid_non_numeric": 3,
        "blank": 1
    }


def test_candidate_merge_preserves_all_rows():
    candidates = validate()

    assert len(candidates) == 127
