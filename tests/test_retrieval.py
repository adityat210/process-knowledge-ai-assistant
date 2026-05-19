from src.retrieval import retrieve


def test_retrieval_returns_top_k_with_required_fields():
    results = retrieve("equipment calibration drift causing failed validation", top_k=5)
    assert len(results) == 5
    for result in results:
        assert result["record_id"]
        assert result["source_file"]
        assert isinstance(result["similarity_score"], float)
        assert result["snippet"]
        assert isinstance(result["metadata"], dict)

