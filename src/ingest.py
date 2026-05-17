from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Union

from pydantic import BaseModel, Field, ValidationError, field_validator

from src.generate_synthetic_records import CATEGORIES, RECORD_TYPES


class ProcessRecord(BaseModel):
    record_id: str
    title: str
    process_category: str
    record_type: str
    date: str
    owner: str = "unknown"
    experiment_notes: str = ""
    failure_mode: str = "requires investigation"
    parameters: Dict[str, Any] = Field(default_factory=dict)
    validation_outcome: str = "warning"
    severity: str = "medium"
    tags: List[str] = Field(default_factory=list)
    source_file: str = ""

    @field_validator("process_category")
    @classmethod
    def normalize_category(cls, value: str) -> str:
        cleaned = " ".join(value.strip().split())
        category_lookup = {category.lower(): category for category in CATEGORIES}
        if cleaned.lower() not in category_lookup:
            raise ValueError(f"unknown process category: {value}")
        return category_lookup[cleaned.lower()]

    @field_validator("record_type")
    @classmethod
    def normalize_record_type(cls, value: str) -> str:
        cleaned = value.strip().lower().replace(" ", "_")
        if cleaned not in RECORD_TYPES:
            raise ValueError(f"unknown record type: {value}")
        return cleaned

    @field_validator("date")
    @classmethod
    def normalize_date(cls, value: str) -> str:
        return date.fromisoformat(value[:10]).isoformat()

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, value: List[str]) -> List[str]:
        return sorted({tag.strip().lower().replace(" ", "-") for tag in value if tag})

    @field_validator("validation_outcome")
    @classmethod
    def normalize_validation(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if cleaned not in {"passed", "warning", "failed"}:
            return "warning"
        return cleaned

    @field_validator("severity")
    @classmethod
    def normalize_severity(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if cleaned not in {"low", "medium", "high"}:
            return "medium"
        return cleaned


def read_jsonl(path: Union[str, Path]) -> List[dict]:
    records = []
    with Path(path).open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                records.append(json.loads(line))
    return records


def write_jsonl(records: List[dict], path: Union[str, Path]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record) + "\n")


def write_csv(records: List[dict], path: Union[str, Path]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(records[0].keys()) if records else []
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            row = record.copy()
            row["parameters"] = json.dumps(row["parameters"])
            row["tags"] = json.dumps(row["tags"])
            writer.writerow(row)


def ingest_records(
    input_path: Union[str, Path] = "data/raw/process_records.jsonl",
    csv_path: Union[str, Path] = "data/processed/ingested_records.csv",
    jsonl_path: Union[str, Path] = "data/processed/ingested_records.jsonl",
) -> List[dict]:
    raw_records = read_jsonl(input_path)
    valid_records = []
    for raw in raw_records:
        try:
            valid_records.append(ProcessRecord(**raw).model_dump())
        except ValidationError as error:
            print(f"Skipped invalid record: {error}")

    write_csv(valid_records, csv_path)
    write_jsonl(valid_records, jsonl_path)

    categories = {record["process_category"] for record in valid_records}
    record_types = {record["record_type"] for record in valid_records}
    print(f"Loaded records: {len(raw_records)}")
    print(f"Valid records: {len(valid_records)}")
    print(f"Process categories: {len(categories)}")
    print(f"Record types: {len(record_types)}")
    return valid_records


if __name__ == "__main__":
    ingest_records()
