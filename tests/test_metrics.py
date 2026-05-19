import json
from pathlib import Path


def test_project_metrics_exists_and_has_required_keys():
    path = Path("data/outputs/project_metrics.json")
    assert path.exists()
    metrics = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "total_raw_records",
        "total_processed_records",
        "process_categories",
        "workflow_outputs",
        "metadata_coverage",
        "retrievable_records",
        "top_failure_modes",
        "validation_outcome_counts",
        "category_counts",
        "record_type_counts",
    }
    assert required.issubset(metrics)


def test_project_metrics_meet_resume_thresholds():
    metrics = json.loads(Path("data/outputs/project_metrics.json").read_text(encoding="utf-8"))
    assert metrics["total_processed_records"] >= 250
    assert metrics["process_categories"] == 6
    assert metrics["workflow_outputs"] >= 3
    assert metrics["metadata_coverage"] >= 0.95
    assert metrics["retrievable_records"] >= 250

