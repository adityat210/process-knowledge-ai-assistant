from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List, Union

from src.ingest import read_jsonl, write_csv, write_jsonl


def find_material_batch(text: str) -> str:
    match = re.search(r"MB-\d{4}-\d{4}", text)
    return match.group(0) if match else "unknown"


def find_equipment_id(text: str) -> str:
    match = re.search(r"EQ-\d{3}", text)
    return match.group(0) if match else "unknown"


def risk_level(severity: str, validation_status: str) -> str:
    if severity == "high" and validation_status == "failed":
        return "high"
    if severity == "medium" or validation_status == "warning":
        return "medium"
    if severity == "low" and validation_status == "passed":
        return "low"
    return "medium"


def root_cause_hint(text: str, failure_mode: str = "") -> str:
    lowered = text.lower()
    failure = failure_mode.lower()
    material_terms = ["contamination", "batch variance", "material inconsistency", "composition", "batch"]
    equipment_terms = ["calibration", "drift", "sensor", "equipment", "maintenance"]
    process_terms = ["temperature", "pressure", "coating speed", "drying time", "parameter change"]
    if any(term in failure for term in equipment_terms):
        return "equipment/process issue"
    if any(term in failure for term in material_terms):
        return "materials issue"
    if any(term in failure for term in process_terms):
        return "process parameter issue"
    if any(term in lowered for term in material_terms):
        return "materials issue"
    if any(term in lowered for term in equipment_terms):
        return "equipment/process issue"
    if any(term in lowered for term in process_terms):
        return "process parameter issue"
    return "requires investigation"


def extract_metadata(record: dict) -> dict:
    parameters = record.get("parameters", {})
    if isinstance(parameters, str):
        parameters = json.loads(parameters)
    text = " ".join(
        [
            record.get("title", ""),
            record.get("experiment_notes", ""),
            record.get("failure_mode", ""),
            json.dumps(parameters),
            record.get("validation_outcome", ""),
        ]
    )
    metadata = {
        "category": record["process_category"],
        "failure_mode": record["failure_mode"],
        "severity": record["severity"],
        "parameters": parameters,
        "validation_status": record["validation_outcome"],
        "material_batch": find_material_batch(text),
        "equipment_id": find_equipment_id(text),
        "risk_level": risk_level(record["severity"], record["validation_outcome"]),
        "root_cause_hint": root_cause_hint(text, record["failure_mode"]),
    }
    enriched = record.copy()
    enriched["metadata"] = metadata
    return enriched


def enrich_records(
    input_path: Union[str, Path] = "data/processed/ingested_records.jsonl",
    csv_path: Union[str, Path] = "data/processed/metadata_enriched_records.csv",
    jsonl_path: Union[str, Path] = "data/processed/metadata_enriched_records.jsonl",
) -> List[dict]:
    records = read_jsonl(input_path)
    enriched = [extract_metadata(record) for record in records]
    write_csv(enriched, csv_path)
    write_jsonl(enriched, jsonl_path)
    return enriched


if __name__ == "__main__":
    records = enrich_records()
    print(f"Metadata enriched records: {len(records)}")
