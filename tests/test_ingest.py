from src.generate_synthetic_records import CATEGORIES
from src.ingest import read_jsonl


def test_dataset_has_resume_scale_records():
    records = read_jsonl("data/processed/ingested_records.jsonl")
    assert len(records) >= 250


def test_dataset_has_exactly_six_categories():
    records = read_jsonl("data/processed/ingested_records.jsonl")
    categories = {record["process_category"] for record in records}
    assert categories == set(CATEGORIES)

