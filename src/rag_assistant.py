from __future__ import annotations

from typing import Dict, List

from src.retrieval import retrieve


def grouped_evidence(results: List[dict]) -> Dict[str, List[dict]]:
    grouped = {}
    for result in results:
        grouped.setdefault(result["process_category"], []).append(result)
    return grouped


def answer_query(query: str, top_k: int = 5) -> str:
    results = retrieve(query, top_k=top_k)
    grouped = grouped_evidence(results)
    source_ids = [result["record_id"] for result in results]

    answer_lines = [
        "# Answer",
        f"I found {len(results)} relevant process records for: `{query}`.",
        "The strongest evidence points to the categories and failure modes shown below. I am only using the retrieved records, so this answer stays grounded in the local dataset.",
        "",
        "## Relevant Evidence",
    ]

    for category, category_results in grouped.items():
        answer_lines.append(f"- {category}")
        for result in category_results[:3]:
            metadata = result.get("metadata", {})
            answer_lines.append(
                f"  - {result['record_id']} ({result['similarity_score']}): "
                f"{metadata.get('failure_mode', 'unknown failure mode')} | "
                f"risk={metadata.get('risk_level', 'unknown')} | "
                f"root cause={metadata.get('root_cause_hint', 'unknown')}"
            )

    high_risk = [item for item in results if item.get("metadata", {}).get("risk_level") == "high"]
    next_steps = [
        "Review the cited source records before changing process settings.",
        "Compare validation outcomes against the current threshold and rerun the failing check.",
        "Check whether the likely root cause is equipment, materials, or process-parameter related.",
    ]
    if high_risk:
        next_steps.insert(0, "Prioritize the high-risk records because they combine high severity with failed validation.")

    answer_lines.extend(["", "## Recommended Next Steps"])
    answer_lines.extend([f"- {step}" for step in next_steps])

    answer_lines.extend(["", "## Source Records"])
    for result in results:
        answer_lines.append(f"- {result['record_id']} - {result['title']} - {result['source_file']}")
    return "\n".join(answer_lines)


if __name__ == "__main__":
    print(answer_query("equipment calibration drift causing failed validation", top_k=5))
