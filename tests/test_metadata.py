from src.ingest import read_jsonl
from src.metrics import metadata_coverage


def test_metadata_coverage_is_high_enough():
    records = read_jsonl("data/processed/metadata_enriched_records.jsonl")
    assert metadata_coverage(records) >= 0.95


def test_metadata_has_risk_and_root_cause_fields():
    record = read_jsonl("data/processed/metadata_enriched_records.jsonl")[0]
    metadata = record["metadata"]
    assert metadata["risk_level"] in {"low", "medium", "high"}
    assert metadata["root_cause_hint"] in {
        "equipment/process issue",
        "materials issue",
        "process parameter issue",
        "requires investigation",
    }

