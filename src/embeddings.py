from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Tuple, Union

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.ingest import read_jsonl


INDEX_DIR = Path("data/processed/vector_index")


def searchable_text(record: dict) -> str:
    metadata = record.get("metadata", {})
    parts = [
        record.get("title", ""),
        record.get("experiment_notes", ""),
        record.get("failure_mode", ""),
        json.dumps(record.get("parameters", {})),
        record.get("validation_outcome", ""),
        " ".join(record.get("tags", [])),
        json.dumps(metadata),
    ]
    return " ".join(parts)


def build_tfidf_index(records: List[dict], index_dir: Path) -> None:
    texts = [searchable_text(record) for record in records]
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=6000)
    matrix = vectorizer.fit_transform(texts)
    joblib.dump(vectorizer, index_dir / "tfidf_vectorizer.joblib")
    joblib.dump(matrix, index_dir / "tfidf_matrix.joblib")
    (index_dir / "index_type.txt").write_text("tfidf", encoding="utf-8")


def build_sentence_transformer_index(records: List[dict], index_dir: Path) -> bool:
    if os.environ.get("PKAI_USE_SENTENCE_TRANSFORMERS") != "1":
        return False
    try:
        from sentence_transformers import SentenceTransformer
    except Exception:
        return False

    texts = [searchable_text(record) for record in records]
    model_name = "all-MiniLM-L6-v2"
    model = SentenceTransformer(model_name)
    matrix = model.encode(texts, normalize_embeddings=True)
    np.save(index_dir / "sentence_embeddings.npy", matrix)
    (index_dir / "sentence_model_name.txt").write_text(model_name, encoding="utf-8")
    (index_dir / "index_type.txt").write_text("sentence-transformers", encoding="utf-8")
    return True


def build_index(
    input_path: Union[str, Path] = "data/processed/metadata_enriched_records.jsonl",
    index_dir: Union[str, Path] = INDEX_DIR,
) -> List[dict]:
    records = read_jsonl(input_path)
    output_dir = Path(index_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(records, output_dir / "records.joblib")

    used_sentence_transformers = build_sentence_transformer_index(records, output_dir)
    if not used_sentence_transformers:
        build_tfidf_index(records, output_dir)

    print(f"Indexed records: {len(records)}")
    print(f"Embedding backend: {(output_dir / 'index_type.txt').read_text(encoding='utf-8')}")
    return records


def score_with_tfidf(query: str, index_dir: Path) -> np.ndarray:
    vectorizer = joblib.load(index_dir / "tfidf_vectorizer.joblib")
    matrix = joblib.load(index_dir / "tfidf_matrix.joblib")
    query_vector = vectorizer.transform([query])
    return cosine_similarity(query_vector, matrix)[0]


def score_with_sentence_transformers(query: str, index_dir: Path) -> np.ndarray:
    from sentence_transformers import SentenceTransformer

    model_name = (index_dir / "sentence_model_name.txt").read_text(encoding="utf-8")
    model = SentenceTransformer(model_name)
    matrix = np.load(index_dir / "sentence_embeddings.npy")
    query_vector = model.encode([query], normalize_embeddings=True)
    return cosine_similarity(query_vector, matrix)[0]


def load_scores(query: str, index_dir: Union[str, Path] = INDEX_DIR) -> Tuple[List[dict], np.ndarray]:
    output_dir = Path(index_dir)
    records = joblib.load(output_dir / "records.joblib")
    index_type = (output_dir / "index_type.txt").read_text(encoding="utf-8").strip()
    if index_type == "sentence-transformers":
        scores = score_with_sentence_transformers(query, output_dir)
    else:
        scores = score_with_tfidf(query, output_dir)
    return records, scores


if __name__ == "__main__":
    build_index()
