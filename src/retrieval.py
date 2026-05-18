from __future__ import annotations

from pathlib import Path
from typing import List, Union

from src.embeddings import INDEX_DIR, load_scores


def make_snippet(record: dict, length: int = 260) -> str:
    text = f"{record.get('experiment_notes', '')} Validation: {record.get('validation_outcome', '')}."
    if len(text) <= length:
        return text
    return text[: length - 3].rstrip() + "..."


def retrieve(query: str, top_k: int = 5, index_dir: Union[str, Path] = INDEX_DIR) -> List[dict]:
    records, scores = load_scores(query, index_dir)
    ranked_indexes = scores.argsort()[::-1][:top_k]
    results = []
    for index in ranked_indexes:
        record = records[int(index)]
        results.append(
            {
                "record_id": record["record_id"],
                "title": record["title"],
                "process_category": record["process_category"],
                "similarity_score": round(float(scores[int(index)]), 4),
                "source_file": record["source_file"],
                "snippet": make_snippet(record),
                "metadata": record.get("metadata", {}),
            }
        )
    return results


if __name__ == "__main__":
    queries = [
        "coating defect rate increased after parameter change",
        "equipment calibration drift causing failed validation",
        "material batch inconsistency during thermal cycling",
    ]
    for sample_query in queries:
        print(f"\nQuery: {sample_query}")
        for item in retrieve(sample_query, top_k=3):
            print(item["record_id"], item["similarity_score"], item["title"])
