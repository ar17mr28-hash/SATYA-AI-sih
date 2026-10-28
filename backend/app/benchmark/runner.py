"""
Benchmark Runner and Evaluation Suite for VerifyAI.
Executes reproducible benchmarks against version-controlled datasets,
evaluates precision, recall, F1, accuracy, confusion matrices, latency,
and compares against a naive baseline.
Exports results to JSON and CSV.
"""
import os
import json
import csv
import time
from typing import Dict, Any, List
from app.verification.pipeline import VerificationPipeline

class BaselineVerifier:
    """
    Naive baseline verifier (simple substring match without numerical, date, or negation logic).
    Used to establish fair comparative benchmark.
    """
    @staticmethod
    def verify(text: str, evidence_sources: List[Dict[str, Any]]) -> str:
        if not text.strip():
            return "UNVERIFIABLE"
        combined_evidence = " ".join([s.get("text", "") for s in evidence_sources]).lower()
        # Naive substring check
        words = [w.lower() for w in text.split() if len(w) > 3]
        if not words:
            return "UNVERIFIABLE"
        matches = sum(1 for w in words if w in combined_evidence)
        ratio = matches / len(words)
        if ratio > 0.5:
            return "SUPPORTED"
        return "UNVERIFIABLE"

class BenchmarkRunner:
    """
    Orchestrates the evaluation benchmark.
    """

    def __init__(self, dataset_path: str = None):
        if not dataset_path:
            base_dir = os.path.dirname(__file__)
            dataset_path = os.path.join(base_dir, "dataset.json")
        self.dataset_path = dataset_path
        self.pipeline = VerificationPipeline()

    def load_dataset(self) -> List[Dict[str, Any]]:
        with open(self.dataset_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def run(self) -> Dict[str, Any]:
        """
        Executes full benchmark suite and computes metrics.
        """
        cases = self.load_dataset()
        results: List[Dict[str, Any]] = []
        latencies_ms: List[float] = []

        tp = 0  # Expected SUPPORTED, predicted SUPPORTED
        fp = 0  # Expected non-SUPPORTED, predicted SUPPORTED
        tn = 0  # Expected non-SUPPORTED, predicted non-SUPPORTED
        fn = 0  # Expected SUPPORTED, predicted non-SUPPORTED

        baseline_correct = 0

        for case in cases:
            case_id = case["id"]
            expected_verdict = case["expected_verdict"]
            expected_security = case["expected_security_safe"]

            t0 = time.perf_counter()
            out = self.pipeline.verify(
                response_text=case["response_text"],
                evidence_sources=case["evidence_sources"],
                query=case.get("description"),
                scan_security=True
            )
            elapsed = (time.perf_counter() - t0) * 1000.0
            latencies_ms.append(elapsed)

            # Determine actual verdict
            if not out["security"]["is_safe"]:
                actual_verdict = "BLOCKED"
            elif not out["claims"]:
                actual_verdict = "UNVERIFIABLE"
            else:
                # Top primary verdict
                primary_verdict = out["claims"][0]["verdict"]
                actual_verdict = primary_verdict

            # Check correctness
            passed = (actual_verdict == expected_verdict)

            # Binary classification stats (Positive = SUPPORTED, Negative = Not SUPPORTED)
            is_expected_pos = (expected_verdict == "SUPPORTED")
            is_actual_pos = (actual_verdict == "SUPPORTED")

            if is_expected_pos and is_actual_pos:
                tp += 1
            elif not is_expected_pos and is_actual_pos:
                fp += 1
            elif not is_expected_pos and not is_actual_pos:
                tn += 1
            elif is_expected_pos and not is_actual_pos:
                fn += 1

            # Run baseline comparison
            base_pred = BaselineVerifier.verify(case["response_text"], case["evidence_sources"])
            if (base_pred == "SUPPORTED" and is_expected_pos) or (base_pred != "SUPPORTED" and not is_expected_pos):
                baseline_correct += 1

            results.append({
                "case_id": case_id,
                "category": case["category"],
                "expected": expected_verdict,
                "actual": actual_verdict,
                "passed": passed,
                "latency_ms": round(elapsed, 2),
                "claims_count": len(out["claims"]),
                "trust_score": out["scorecard"]["overall_trust_score"],
            })

        total = len(cases)
        passed_count = sum(1 for r in results if r["passed"])
        accuracy = (passed_count / total) * 100.0 if total > 0 else 0.0

        precision = (tp / (tp + fp)) * 100.0 if (tp + fp) > 0 else 100.0
        recall = (tp / (tp + fn)) * 100.0 if (tp + fn) > 0 else 100.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        baseline_accuracy = (baseline_correct / total) * 100.0 if total > 0 else 0.0

        latencies_ms.sort()
        avg_latency = sum(latencies_ms) / len(latencies_ms) if latencies_ms else 0.0
        p95_idx = int(len(latencies_ms) * 0.95)
        p95_latency = latencies_ms[p95_idx] if latencies_ms else 0.0

        metrics = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total_cases": total,
            "passed_cases": passed_count,
            "failed_cases": total - passed_count,
            "accuracy": round(accuracy, 2),
            "precision": round(precision, 2),
            "recall": round(recall, 2),
            "f1_score": round(f1, 2),
            "confusion_matrix": {
                "true_positives": tp,
                "false_positives": fp,
                "true_negatives": tn,
                "false_negatives": fn,
            },
            "latency": {
                "avg_ms": round(avg_latency, 2),
                "min_ms": round(latencies_ms[0], 2) if latencies_ms else 0.0,
                "max_ms": round(latencies_ms[-1], 2) if latencies_ms else 0.0,
                "p95_ms": round(p95_latency, 2),
            },
            "baseline_comparison": {
                "verifyai_accuracy": round(accuracy, 2),
                "naive_baseline_accuracy": round(baseline_accuracy, 2),
                "accuracy_delta": round(accuracy - baseline_accuracy, 2),
            },
            "cases": results,
        }

        # Save machine-readable outputs
        self._export_results(metrics)

        return metrics

    def _export_results(self, metrics: Dict[str, Any]):
        base_dir = os.path.dirname(__file__)
        json_path = os.path.join(base_dir, "benchmark_results.json")
        csv_path = os.path.join(base_dir, "benchmark_results.csv")

        # Save JSON
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)

        # Save CSV
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["case_id", "category", "expected", "actual", "passed", "latency_ms", "trust_score"])
            for c in metrics["cases"]:
                writer.writerow([
                    c["case_id"],
                    c["category"],
                    c["expected"],
                    c["actual"],
                    c["passed"],
                    c["latency_ms"],
                    c["trust_score"],
                ])

if __name__ == "__main__":
    runner = BenchmarkRunner()
    res = runner.run()
    print("=" * 60)
    print(f"VERIFYAI BENCHMARK RUN COMPLETE")
    print(f"Total Cases:     {res['total_cases']}")
    print(f"Passed Cases:    {res['passed_cases']} / {res['total_cases']}")
    print(f"Accuracy:        {res['accuracy']}%")
    print(f"Precision:       {res['precision']}%")
    print(f"Recall:          {res['recall']}%")
    print(f"F1 Score:        {res['f1_score']}%")
    print(f"Naive Baseline:  {res['baseline_comparison']['naive_baseline_accuracy']}%")
    print(f"Accuracy Delta:  +{res['baseline_comparison']['accuracy_delta']}%")
    print(f"Avg Latency:     {res['latency']['avg_ms']} ms (P95: {res['latency']['p95_ms']} ms)")
    print("=" * 60)
