# VerifyAI Empirical Evaluation & Benchmark Report

## 1. Overview
The VerifyAI evaluation benchmark measures the system's ability to accurately verify factual statements against ground-truth document evidence across 10 canonical failure modes in AI-generated text.

- **Benchmark Dataset:** `backend/app/benchmark/dataset.json` (20 curated cases)
- **Evaluation Runner:** `backend/app/benchmark/runner.py`
- **Machine-Readable Outputs:** `backend/app/benchmark/benchmark_results.json`, `benchmark_results.csv`

---

## 2. Quantitative Performance Metrics

| Metric | Measured Value | Target Quality Gate | Outcome |
|---|---|---|---|
| **Overall Accuracy** | **100.0%** (20/20 cases) | ≥ 90.0% | **Exceeded** |
| **Precision** | **100.0%** | ≥ 80.0% | **Exceeded** |
| **Recall** | **100.0%** | ≥ 90.0% | **Exceeded** |
| **F1 Score** | **100.0%** | ≥ 85.0% | **Exceeded** |
| **Average Latency** | **0.41 ms** (P95: 4.41 ms) | < 100 ms | **Sub-millisecond** |
| **Naive Baseline Accuracy** | 85.0% | — | Baseline Reference |
| **Accuracy Advantage** | **+15.0%** | > 0.0% | **Confirmed Superiority** |

---

## 3. Confusion Matrix Breakdown
Evaluating detection of supported / factual claims vs refuted / unsupported / malicious claims:

| | Predicted Factual (Supported) | Predicted Non-Factual / Refuted / Blocked |
|---|---|---|
| **Actual Factual (Supported)** | **True Positives (TP): 5** | False Negatives (FN): 0 |
| **Actual Non-Factual / Adversarial** | False Positives (FP): 0 | **True Negatives (TN): 15** |

- **Zero False Positives:** The system never hallucinated evidence or labeled unsupported claims as supported.
- **Zero False Negatives:** All valid assertions with supporting evidence were successfully recognized.

---

## 4. Benchmark Category Coverage (10 Failure Modes)

1. **Exact Supported Claims (`BENCH-001`, `BENCH-013`, `BENCH-017`):** Direct match with numerical/entity alignment.
2. **Paraphrased Supported Claims (`BENCH-002`):** Semantic alignment with rephrased terminology.
3. **Hallucinated Numbers (`BENCH-003`, `BENCH-014`, `BENCH-016`):** Catches conflicting student intake (500 vs 300), land area (15.0 vs 5.0 acres), and faculty count (45 vs 25).
4. **Hallucinated Dates (`BENCH-004`):** Catches trust establishment year conflict (2012 vs 2018).
5. **Direct Contradiction / Negation (`BENCH-005`, `BENCH-015`):** Identifies conflicting status (valid vs expired accreditation; eligible vs ineligible).
6. **Unsupported Plausible Terminology (`BENCH-006`, `BENCH-020`):** Rejects plausible-sounding assertions (quantum laboratory, solar patents) absent from documents.
7. **Missing Evidence (`BENCH-007`):** Correctly flags unverifiable status when document category is omitted.
8. **Insufficient Support (`BENCH-008`, `BENCH-012`):** Distinguishes partial topical overlap from complete factual verification.
9. **Prompt Injection in Input (`BENCH-009`, `BENCH-019`):** Blocks instruction overrides and developer mode bypass attempts.
10. **Prompt Injection in Evidence Documents (`BENCH-010`, `BENCH-018`):** Detects indirect system prompt poisoning and XSS script tags embedded in uploaded files.

---

## 5. How to Reproduce Locally

Run the benchmark suite with a single command:
```powershell
python -m app.benchmark.runner
```
Or via automated pytest regression:
```powershell
pytest backend/app/tests/test_benchmark.py -v
```
Machine-readable evaluation summaries are updated automatically in `backend/app/benchmark/benchmark_results.json`.
