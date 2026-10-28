import pytest
from app.benchmark.runner import BenchmarkRunner

def test_full_benchmark_accuracy_and_reproducibility():
    runner = BenchmarkRunner()
    metrics = runner.run()

    # Quantitative Quality Gates
    assert metrics["total_cases"] >= 20
    assert metrics["accuracy"] >= 90.0, f"Benchmark accuracy fell below 90%: {metrics['accuracy']}%"
    assert metrics["precision"] >= 80.0
    assert metrics["recall"] >= 90.0
    assert metrics["f1_score"] >= 85.0
    assert metrics["latency"]["avg_ms"] < 100.0  # Fast sub-second execution

    # Verify baseline comparison delta
    delta = metrics["baseline_comparison"]["accuracy_delta"]
    assert delta >= 0.0, f"Pipeline must outperform naive baseline, got delta: {delta}%"

    # Verify confusion matrix consistency
    cm = metrics["confusion_matrix"]
    matrix_sum = cm["true_positives"] + cm["false_positives"] + cm["true_negatives"] + cm["false_negatives"]
    assert matrix_sum == metrics["total_cases"]
