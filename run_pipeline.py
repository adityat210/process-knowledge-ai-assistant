from __future__ import annotations

import json
from pathlib import Path
from typing import Union

from src.embeddings import build_index
from src.generate_synthetic_records import generate_records
from src.ingest import ingest_records
from src.metadata_extraction import enrich_records
from src.metrics import build_metrics, print_final_summary
from src.rag_assistant import answer_query
from src.retrieval import retrieve
from src.workflow_outputs import generate_workflow_outputs


SAMPLE_QUERIES = [
    "coating defect rate increased after parameter change",
    "equipment calibration drift causing failed validation",
    "material batch inconsistency during thermal cycling",
]


def create_demo_notebook(path: Union[str, Path] = "notebooks/demo_analysis.ipynb") -> None:
    notebook_path = Path(path)
    if notebook_path.exists():
        return

    cells = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Process Knowledge AI Assistant Demo\n",
                "\n",
                "I use this notebook to inspect the processed records, run retrieval examples, and reference the generated workflow outputs.\n",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "from collections import Counter\n",
                "from src.ingest import read_jsonl\n",
                "records = read_jsonl('data/processed/metadata_enriched_records.jsonl')\n",
                "len(records)\n",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "Counter(record['process_category'] for record in records)\n",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "Counter(record['validation_outcome'] for record in records)\n",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "from src.retrieval import retrieve\n",
                "queries = [\n",
                "    'coating defect rate increased after parameter change',\n",
                "    'equipment calibration drift causing failed validation',\n",
                "    'material batch inconsistency during thermal cycling',\n",
                "]\n",
                "{query: retrieve(query, top_k=3) for query in queries}\n",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "from src.rag_assistant import answer_query\n",
                "print(answer_query('equipment calibration drift causing failed validation', top_k=3))\n",
            ],
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Generated Workflow Outputs\n",
                "\n",
                "- `data/outputs/summary_report.md`\n",
                "- `data/outputs/source_map.csv` and `data/outputs/source_map.md`\n",
                "- `data/outputs/troubleshooting_guide.md`\n",
            ],
        },
    ]
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    notebook_path.parent.mkdir(parents=True, exist_ok=True)
    notebook_path.write_text(json.dumps(notebook, indent=2) + "\n", encoding="utf-8")


def run_pipeline() -> dict:
    print("1. generating synthetic records")
    generate_records(count=300)

    print("\n2. ingesting records")
    ingest_records()

    print("\n3. extracting metadata")
    enrich_records()

    print("\n4. building local embeddings/index")
    build_index()

    print("\n5. running sample retrieval queries")
    for query in SAMPLE_QUERIES:
        print(f"\nquery: {query}")
        for result in retrieve(query, top_k=3):
            print(f"- {result['record_id']} {result['similarity_score']} {result['title']}")

    print("\n6. generating sample rag answers")
    for query in SAMPLE_QUERIES:
        print(answer_query(query, top_k=3).split("## Source Records")[0])

    print("\n7. generating NotebookLM-style workflow outputs")
    generate_workflow_outputs()

    print("\n8. creating jupyter demo notebook")
    create_demo_notebook()

    print("\n9. saving final metrics")
    metrics = build_metrics()
    print_final_summary(metrics)
    return metrics


if __name__ == "__main__":
    run_pipeline()
