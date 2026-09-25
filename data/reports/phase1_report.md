# Baseline Data Pipeline & RAG Evaluation Report (Phase 1)

- **Date Run:** 2026-09-25T09:43:48.539890+00:00
- **Model:** `gemini-3.8-flash` (mock)
- **Embedding:** `sentence-transformers/all-MiniLM-L6-v2`

## 1. Data Ingestion & Quality Summary
- **Source API:** Crossref REST API
- **Raw Records Fetched:** 24
- **Clean Records Processed:** 24
- **Great Expectations Quality Gate:** PASSED
- **Freshness SLA Status:** FRESH (Stale records: 1 / 24)

## 2. Baseline Benchmark Metrics
| Metric | Baseline Score | Target Threshold | Status |
| :--- | :---: | :---: | :---: |
| **Retrieval Hit Rate** | 100.00% | >= 80.0% | PASS |
| **Mean Token F1** | 0.7852 | >= 0.60 | PASS |
| **LLM Judge Accuracy** | 80.00% | >= 70.0% | PASS |
| **Mean Judge Score (1-5)** | 4.00 / 5.0 | >= 3.5 | PASS |

## 3. Conclusion
Baseline pipeline executed successfully. Corpus indexed and grounded evaluation complete.
