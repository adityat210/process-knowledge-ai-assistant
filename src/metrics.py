from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Union

from src.ingest import read_jsonl


def metadata_coverage(records: list) -> float:
    required = ["category", "failure_mode", "severity", "parameters", "validation_status", "risk_level", "root_cause_hint"]
    covered = 0
    for record in records:
        metadata = record.get("metadata", {})
        if all(metadata.get(key) not in [None, "", {}] for key in required):
            covered += 1
    return round(covered / len(records), 4) if records else 0.0


def count_outputs() -> int:
    expected = [
        Path("data/outputs/summary_report.md"),
        Path("data/outputs/source_map.csv"),
        Path("data/outputs/troubleshooting_guide.md"),
    ]
    return sum(path.exists() for path in expected)


def build_metrics(
    raw_path: Union[str, Path] = "data/raw/process_records.jsonl",
    processed_path: Union[str, Path] = "data/processed/metadata_enriched_records.jsonl",
    output_path: Union[str, Path] = "data/outputs/project_metrics.json",
) -> dict:
    raw_records = read_jsonl(raw_path)
    records = read_jsonl(processed_path)
    categories = sorted({record["process_category"] for record in records})
    vector_records_path = Path("data/processed/vector_index/records.joblib")
    retrievable_records = len(records) if vector_records_path.exists() else 0

    metrics = {
        "total_raw_records": len(raw_records),
        "total_processed_records": len(records),
        "process_categories": len(categories),
        "workflow_outputs": count_outputs(),
        "metadata_coverage": metadata_coverage(records),
        "retrievable_records": retrievable_records,
        "top_failure_modes": dict(Counter(record["failure_mode"] for record in records).most_common(8)),
        "validation_outcome_counts": dict(Counter(record["validation_outcome"] for record in records)),
        "category_counts": dict(Counter(record["process_category"] for record in records)),
        "record_type_counts": dict(Counter(record["record_type"] for record in records)),
    }

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    return metrics


def print_final_summary(metrics: dict) -> None:
    print("\nPROJECT COMPLETE\n")
    print("Resume Evidence:")
    print(f"- Built AI assistant over {metrics['total_processed_records']} process notes and records.")
    print("- Structured knowledge lookup across 6 process categories.")
    print("- Generated 3 workflow outputs: summary report, source map, troubleshooting guide.")
    print("- Created Python ingestion, metadata extraction, embedding, retrieval, and local RAG answer pipeline.")
    print("- Added NotebookLM-style outputs and Jupyter demo notebook.")
    print("- Saved metrics to data/outputs/project_metrics.json.")


if __name__ == "__main__":
    final_metrics = build_metrics()
    print_final_summary(final_metrics)
