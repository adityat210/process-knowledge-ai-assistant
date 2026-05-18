from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import List, Tuple, Union

from src.ingest import read_jsonl


OUTPUT_DIR = Path("data/outputs")


def count_values(records: List[dict], key: str) -> Counter:
    return Counter(record[key] for record in records)


def top_failure_modes(records: List[dict], limit: int = 8) -> List[Tuple[str, int]]:
    return Counter(record["failure_mode"] for record in records).most_common(limit)


def write_summary_report(records: List[dict], output_path: Path = OUTPUT_DIR / "summary_report.md") -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    category_counts = count_values(records, "process_category")
    type_counts = count_values(records, "record_type")
    validation_counts = count_values(records, "validation_outcome")
    risks = Counter(record["metadata"]["risk_level"] for record in records)
    example_records = records[:6]

    lines = [
        "# Summary Report",
        "",
        "I built this report from the processed process records so the analysis is tied back to source IDs.",
        "",
        f"- Total records: {len(records)}",
        "",
        "## Category Counts",
    ]
    lines.extend([f"- {category}: {count}" for category, count in category_counts.items()])
    lines.extend(["", "## Record Type Counts"])
    lines.extend([f"- {record_type}: {count}" for record_type, count in type_counts.items()])
    lines.extend(["", "## Top Failure Modes"])
    lines.extend([f"- {mode}: {count}" for mode, count in top_failure_modes(records)])
    lines.extend(["", "## Validation Pass/Fail Distribution"])
    lines.extend([f"- {status}: {count}" for status, count in validation_counts.items()])
    lines.extend(["", "## Recurring Risks"])
    lines.extend([f"- {risk}: {count}" for risk, count in risks.items()])
    lines.extend(
        [
            "",
            "## Operational Insights",
            "- Calibration drift, sensor anomalies, and equipment checks show up often enough that I would review maintenance cadence before changing process limits.",
            "- Batch consistency and thermal cycling records give useful evidence for separating materials issues from process parameter issues.",
            "- Failed validation records are most useful when paired with severity and root-cause hints because they show where to investigate first.",
            "",
            "## Example Cited Records",
        ]
    )
    lines.extend([f"- {record['record_id']}: {record['title']} ({record['source_file']})" for record in example_records])
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_source_map(records: List[dict], csv_path: Path = OUTPUT_DIR / "source_map.csv", md_path: Path = OUTPUT_DIR / "source_map.md") -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    columns = [
        "process_category",
        "record_id",
        "record_type",
        "failure_mode",
        "parameters",
        "validation_outcome",
        "source_file",
        "tags",
        "risk_level",
        "root_cause_hint",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        for record in records:
            metadata = record["metadata"]
            writer.writerow(
                {
                    "process_category": record["process_category"],
                    "record_id": record["record_id"],
                    "record_type": record["record_type"],
                    "failure_mode": record["failure_mode"],
                    "parameters": json.dumps(record["parameters"]),
                    "validation_outcome": record["validation_outcome"],
                    "source_file": record["source_file"],
                    "tags": ", ".join(record["tags"]),
                    "risk_level": metadata["risk_level"],
                    "root_cause_hint": metadata["root_cause_hint"],
                }
            )

    lines = [
        "# Source Map",
        "",
        "I use this source map to show how each generated record connects to process category, risk, and root-cause evidence.",
        "",
        "| Category | Record ID | Type | Failure Mode | Risk | Root Cause |",
        "|---|---|---|---|---|---|",
    ]
    for record in records[:40]:
        metadata = record["metadata"]
        lines.append(
            f"| {record['process_category']} | {record['record_id']} | {record['record_type']} | "
            f"{record['failure_mode']} | {metadata['risk_level']} | {metadata['root_cause_hint']} |"
        )
    lines.append("\nFull source map is saved in `data/outputs/source_map.csv`.")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_troubleshooting_guide(records: List[dict], output_path: Path = OUTPUT_DIR / "troubleshooting_guide.md") -> None:
    grouped = defaultdict(list)
    for record in records:
        grouped[record["process_category"]].append(record)

    lines = [
        "# Troubleshooting Guide",
        "",
        "I organized this guide by process category so it can be used as a demo-ready lookup artifact.",
    ]
    for category, category_records in grouped.items():
        failure_modes = Counter(record["failure_mode"] for record in category_records).most_common(4)
        root_causes = Counter(record["metadata"]["root_cause_hint"] for record in category_records).most_common(3)
        examples = category_records[:3]
        lines.extend(
            [
                "",
                f"## {category}",
                "",
                "### Common Failure Modes",
            ]
        )
        lines.extend([f"- {mode}: {count} records" for mode, count in failure_modes])
        lines.extend(["", "### Likely Root Causes"])
        lines.extend([f"- {cause}: {count} records" for cause, count in root_causes])
        lines.extend(["", "### Example Source Records"])
        lines.extend([f"- {record['record_id']}: {record['title']}" for record in examples])
        lines.extend(
            [
                "",
                "### Recommended Next Steps",
                "- Re-check the parameters attached to the cited records.",
                "- Compare validation outcomes before and after the suspected process change.",
                "- Review maintenance, batch, and sensor evidence before deciding on corrective action.",
                "",
                "### Validation Checks",
                "- Confirm pass/fail status against the validation threshold.",
                "- Check whether severity and risk level agree with the source notes.",
                "- Rerun the category-specific validation check after corrective action.",
            ]
        )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate_workflow_outputs(input_path: Union[str, Path] = "data/processed/metadata_enriched_records.jsonl") -> List[str]:
    records = read_jsonl(input_path)
    write_summary_report(records)
    write_source_map(records)
    write_troubleshooting_guide(records)
    return [
        "data/outputs/summary_report.md",
        "data/outputs/source_map.csv",
        "data/outputs/source_map.md",
        "data/outputs/troubleshooting_guide.md",
    ]


if __name__ == "__main__":
    for output in generate_workflow_outputs():
        print(output)
