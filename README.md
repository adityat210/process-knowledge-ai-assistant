# Process Knowledge AI Assistant

I built this project as a local, runnable resume artifact for a process knowledge assistant. It ingests synthetic process records, extracts metadata, builds a local search index, retrieves relevant records, and generates source-grounded workflow outputs without requiring paid API keys.

## Why I Built It

I wanted the project to back up the resume bullets with real files, tests, and generated evidence instead of only describing the work. The dataset is synthetic, but the workflow mirrors the kind of process engineering knowledge system I would build around experiment notes, QA records, maintenance logs, failure reports, validation summaries, and parameter changes.

## Resume Bullet Alignment

- Built AI assistant over 300 process notes and records by combining Python ingestion, metadata extraction, embeddings, and RAG retrieval.
- Improved knowledge lookup across 6 process categories by structuring experiment notes, failure modes, parameters, and validation outcomes.
- Supported demo-ready analysis across 3 workflow outputs by using NotebookLM-style reports and a Jupyter notebook.

## Architecture

```text
synthetic process records
        |
        v
python ingestion + pydantic validation
        |
        v
rule-based metadata extraction
        |
        v
local embeddings / tf-idf vector index
        |
        v
retrieval + template-based rag assistant
        |
        v
summary report + source map + troubleshooting guide + jupyter demo
```

## Tech Stack

- Python
- Pydantic
- scikit-learn TF-IDF fallback
- Optional sentence-transformers support
- Local RAG answer templates
- Pytest
- Jupyter notebook format

## Setup

```bash
pip install -r requirements.txt
python run_pipeline.py
pytest
```

## Example Queries

- coating defect rate increased after parameter change
- equipment calibration drift causing failed validation
- material batch inconsistency during thermal cycling

## Example RAG Output

The assistant retrieves the closest source records, summarizes the evidence, recommends next steps, and cites record IDs such as `PKAI-0004` or `PKAI-0012`. It avoids unsupported claims by only using the retrieved local context.

## Generated Workflow Outputs

- `data/outputs/summary_report.md`
- `data/outputs/source_map.csv`
- `data/outputs/source_map.md`
- `data/outputs/troubleshooting_guide.md`
- `data/outputs/project_metrics.json`

## Resume Metric Evidence

| Resume Claim | Project Evidence |
|---|---|
| 250+ process notes and records | Synthetic dataset generated with at least 300 records |
| 6 process categories | Category taxonomy enforced during ingestion |
| 3 workflow outputs | Summary report, source map, troubleshooting guide |
| Python ingestion | ingest.py and run_pipeline.py |
| Metadata extraction | metadata_extraction.py |
| Embeddings | embeddings.py with local embedding/TF-IDF fallback |
| RAG retrieval | retrieval.py and rag_assistant.py |
| NotebookLM and Jupyter analysis | NotebookLM-style markdown outputs and demo_analysis.ipynb |

## Metrics Table

The pipeline writes final metrics to `data/outputs/project_metrics.json`.

| Metric | Target |
|---|---:|
| total_processed_records | >= 250 |
| process_categories | 6 |
| workflow_outputs | >= 3 |
| metadata_coverage | >= 0.95 |
| retrievable_records | >= 250 |

## Limitations

- The records are synthetic, so this is a resume project and not a live manufacturing system.
- The local answer generator is template-based, so it is useful for demos but not the same as a production LLM workflow.
- The TF-IDF fallback is simple and reliable, but a production system would likely use a stronger embedding model and more evaluation data.

## Future Improvements

- Add a small Streamlit or FastAPI demo UI.
- Add human-labeled retrieval evaluation examples.
- Add role-based filtering by owner, category, and validation status.
- Store the index in a dedicated vector database when the dataset grows.
