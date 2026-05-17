from __future__ import annotations

import json
import random
from datetime import date, timedelta
from pathlib import Path
from typing import List, Union


CATEGORIES = [
    "Battery Process Optimization",
    "Materials Characterization",
    "Manufacturing QA",
    "Equipment Maintenance",
    "Failure Analysis",
    "Validation Testing",
]

RECORD_TYPES = [
    "experiment_note",
    "qa_record",
    "maintenance_log",
    "failure_report",
    "validation_summary",
    "parameter_change",
]

FAILURE_MODES = [
    "coating uniformity drift",
    "thermal cycling impedance drift",
    "increased defect rate",
    "calibration offset",
    "material batch inconsistency",
    "sensor anomaly",
    "yield loss",
    "validation threshold miss",
]

PARAMETER_LIBRARY = [
    {"coating_speed_mpm": 1.8, "drying_time_min": 22, "oven_temp_c": 82},
    {"coating_speed_mpm": 2.1, "drying_time_min": 18, "oven_temp_c": 88},
    {"thermal_cycles": 80, "hold_temp_c": 55, "impedance_limit_pct": 8},
    {"calibration_interval_days": 14, "sensor_offset_mv": 3.2, "line_pressure_kpa": 210},
    {"batch_solids_pct": 48.5, "mix_time_min": 35, "viscosity_cp": 920},
    {"inspection_sample_size": 120, "defect_limit_pct": 2.0, "validation_threshold": 0.95},
]


def build_record(index: int) -> dict:
    category = CATEGORIES[index % len(CATEGORIES)]
    record_type = RECORD_TYPES[index % len(RECORD_TYPES)]
    failure_mode = FAILURE_MODES[index % len(FAILURE_MODES)]
    params = PARAMETER_LIBRARY[index % len(PARAMETER_LIBRARY)].copy()
    severity = random.choices(["low", "medium", "high"], weights=[35, 45, 20])[0]
    validation_status = random.choices(["passed", "warning", "failed"], weights=[50, 28, 22])[0]

    if severity == "high" and index % 3 == 0:
        validation_status = "failed"
    if "calibration" in failure_mode and index % 2 == 0:
        validation_status = "failed"

    material_batch = f"MB-{2024 + (index % 2)}-{1000 + index % 75}"
    equipment_id = f"EQ-{(index % 18) + 1:03d}"
    start_date = date(2024, 1, 8)
    record_date = start_date + timedelta(days=index % 420)

    note_templates = [
        f"Observed {failure_mode} during run review. Equipment {equipment_id} and material batch {material_batch} were checked against the current validation threshold.",
        f"Team adjusted parameter change settings after coating uniformity and defect rate moved outside the expected window for {material_batch}.",
        f"Thermal cycling showed impedance drift trend. Calibration records, sensor readings, and maintenance notes were compared for {equipment_id}.",
        f"Manufacturing QA flagged yield loss and sensor anomalies. Batch variance and material consistency were reviewed before validation signoff.",
    ]
    notes = note_templates[index % len(note_templates)]

    return {
        "record_id": f"PKAI-{index + 1:04d}",
        "title": f"{category} {record_type.replace('_', ' ')} {index + 1}",
        "process_category": category,
        "record_type": record_type,
        "date": record_date.isoformat(),
        "owner": random.choice(["A. Patel", "M. Chen", "R. Singh", "J. Rivera", "N. Brooks"]),
        "experiment_notes": notes,
        "failure_mode": failure_mode,
        "parameters": params,
        "validation_outcome": validation_status,
        "severity": severity,
        "tags": sorted({category.lower().replace(" ", "-"), failure_mode.replace(" ", "-"), record_type}),
        "source_file": f"process_notes/{category.lower().replace(' ', '_')}/{record_type}_{index + 1:04d}.md",
    }


def generate_records(output_path: Union[str, Path] = "data/raw/process_records.jsonl", count: int = 300) -> List[dict]:
    random.seed(17)
    records = [build_record(index) for index in range(count)]
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record) + "\n")
    return records


if __name__ == "__main__":
    generated = generate_records()
    print(f"Generated records: {len(generated)}")
