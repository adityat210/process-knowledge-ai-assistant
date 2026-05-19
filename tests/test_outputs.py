from pathlib import Path


def test_workflow_outputs_exist():
    expected_outputs = [
        "data/outputs/summary_report.md",
        "data/outputs/source_map.csv",
        "data/outputs/source_map.md",
        "data/outputs/troubleshooting_guide.md",
    ]
    for output in expected_outputs:
        assert Path(output).exists()

