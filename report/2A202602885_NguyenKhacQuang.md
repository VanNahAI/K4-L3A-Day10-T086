# Member Role Report — Day 10: Data Pipeline & Data Observability
## BÁO CÁO CÁ NHÂN — THÀNH VIÊN 2

---

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| :--- | :--- |
| **Họ và tên** | **Nguyễn Khắc Quang** |
| **MSSV** | **2A202602885** |
| **Email** | `quang180204@gmail.com` |
| **Khóa/Lớp** | K4-L3A-Day10 |
| **Tên nhóm** | K4-L3A-Day10-T086 |
| **Vai trò chính** | **RAG Specialist & Observability & Evaluation Lead** |
| **Nhánh Git phụ trách** | `Quang` (hoặc `feature/rag-observability`) |
| **Repository** | `https://github.com/VanNahAI/K4-L3A-Day10-T086` |
| **Ngày hoàn thành** | 2026-09-25 |

---

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu trực tiếp (Ownership)

| Module / Deliverable | File / Hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| :--- | :--- | :--- | :--- | :---: |
| **Data Quality Gate (GX 1.x)** | `src/observability/quality.py` (`run_data_quality_checks`) | `pd.DataFrame` dữ liệu (Clean / Corrupted / Repaired) | `data/quality/*_quality_report.json` | ✅ Hoàn thành 100% |
| **Freshness SLA Monitoring** | `src/observability/quality.py` (`build_freshness_report`) | `pd.DataFrame` kèm cột `age_days`, `published` | `data/quality/*_freshness_report.json` | ✅ Hoàn thành 100% |
| **Benchmark Test Set Generator** | `src/evaluation/testset.py` (`build_test_set`) | `pd.DataFrame` 24 bản ghi sạch | `data/eval/test_set.json` (10 câu hỏi qua 4 nhóm) | ✅ Hoàn thành 100% |
| **Vector Store & Indexing** | `src/retrieval/index.py` & `embeddings.py` | Clean/Corrupted/Repaired DataFrame, MiniLM model | 3 Chroma Collections (`papers-baseline`, `papers-corrupted`, `papers-repaired`) | ✅ Hoàn thành 100% |
| **Baseline Phase 1 Report** | `src/observability/reporting.py` (`generate_phase1_report`) | Ingestion summary, Baseline metrics, GX status, Freshness | `data/reports/phase1_report.md` | ✅ Hoàn thành 100% |
| **Comparative 3-State Report** | `src/observability/reporting.py` (`generate_corruption_report`) | Metrics 3 pha (Baseline, Corrupted, Repaired), GX, Freshness | `data/reports/corruption_report.md` | ✅ Hoàn thành 100% |

### Việc hỗ trợ ngoài phạm vi chính
1. **Xử lý lỗi mã hóa console Windows (`UnicodeEncodeError`):**
   - Bổ sung cấu hình `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` trong `src/pipelines/corruption_flow.py` giúp script in bảng ma trận tiếng Việt mượt mà trên console Windows PowerShell mà không bị crash khi chấm bài.
2. **Loại bỏ đường dẫn tuyệt đối (Zero Absolute Path):**
   - Rà soát toàn bộ repo và chuẩn hóa tất cả các link tài liệu sang dạng Markdown relative links, tránh nguy cơ bị trừ 5 điểm theo quy định của Rubric.
3. **Quản lý môi trường & Package Linking:**
   - Cấu hình môi trường ảo chuẩn Python 3.12, cài đặt thư viện lõi (`chromadb`, `great-expectations`, `sentence-transformers`, `torch`) qua `uv`, thiết lập chế độ editable package `src/`.

---

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File / Hàm / Artifact liên quan | Kết quả bàn giao | Cách xác minh thực tế |
| :--- | :--- | :--- | :--- |
| **Trạm kiểm dịch GX 1.x** | `src/observability/quality.py` | File JSON báo cáo 4 rules: row count, not null, unique paper_id, summary min length | `python script/run_phase1.py` in ra `Quality Gate: PASSED` |
| **Giám sát Freshness SLA** | `src/observability/quality.py` | Phát hiện chính xác tỷ lệ bài báo quá hạn 180 ngày | `corrupted_freshness_report.json` báo động `is_fresh: False` |
| **Bộ đề thi 10 câu hỏi** | `src/evaluation/testset.py` | `data/eval/test_set.json` phủ 4 taxonomy: summary (3), authors (3), date (2), categories (2) | File JSON sinh đúng 10 câu hỏi có ground truth và doc IDs |
| **Đo lường RAG 3 trạng thái** | `src/evaluation/metrics.py` | `baseline_metrics.json`, `corrupted_metrics.json`, `repaired_metrics.json` | Hit Rate: 100% -> 60% -> 100%<br>Token F1: 0.95 -> 0.85 -> 0.95<br>Judge Score: 4.60 -> 4.20 -> 4.60 |
| **Báo cáo đối chiếu 3 cột** | `src/observability/reporting.py` | `data/reports/corruption_report.md` | Bảng ma trận 3 trạng thái và bài phân tích Silent Failure |

---

## 4. Giải thích phần kỹ thuật đã thực hiện

### 4.1. Vấn đề cần giải quyết
Trong hệ thống RAG thực tế, **60% - 80% thời gian là làm sạch và kiểm soát chất lượng dữ liệu**. Khi dữ liệu đầu vào bị lỗi (thiếu trường, tóm tắt bị rỗng hoặc nhiễu, dữ liệu bị trùng lặp, bài báo quá hạn), **AI Agent không hề ném lỗi runtime** mà vẫn tự tin sinh câu trả lời sai lệch sự thật (**Hallucination**). Đây chính là hiện tượng **Silent Failure** nguy hiểm nhất trong Production. Nhiệm vụ của mình là thiết lập trạm kiểm soát chất lượng tự động ngăn chặn dữ liệu xấu lọt vào Vector Store.

### 4.2. Cách triển khai
1. **Great Expectations 1.x Ephemeral Mode:**
   - Sử dụng chuẩn `gx.get_context(mode="ephemeral")` với `data_sources.add_pandas()`, `add_dataframe_asset()`, và `add_batch_definition_whole_dataframe()`.
   - Cài đặt 4 Expectations bắt buộc:
     - `ExpectTableRowCountToBeBetween(min_value=5, max_value=5000)`
     - `ExpectColumnValuesToNotBeNull` cho `paper_id`, `title`, `text_for_embedding`.
     - `ExpectColumnValuesToBeUnique(column="paper_id")`
     - `ExpectColumnValueLengthsToBeBetween(column="summary", min_value=30)`
2. **Freshness SLA Monitoring:**
   - Tính toán `stale_rows` dựa trên `age_days > 180`.
   - Tính `stale_ratio = stale_rows / total_rows`.
   - Kích hoạt báo động `is_fresh = False` khi tỷ lệ quá hạn vượt quá $25\%$.
3. **Benchmark Test Set:**
   - Thiết kế thuật toán lấy mẫu có cấu trúc, sinh đúng 10 câu hỏi đa dạng qua 4 dạng bài toán: `summary` (câu tóm tắt đầu tiên), `authors` (tác giả bài báo), `date` (ngày xuất bản), `categories` (chuyên ngành).
4. **Báo Cáo Đối Chiếu 3 Trạng Thái:**
   - Tự động định dạng bảng Markdown so sánh định lượng: **Dữ liệu Sạch (Baseline) vs Bị Tiêm Lỗi (Corrupted) vs Sau Phục Hồi (Repaired)**.

### 4.3. Input, Output và Contract

| Thành phần | Mô tả |
| :--- | :--- |
| **Input** | `pd.DataFrame` tuân thủ Schema chuẩn hóa (16 cột: `paper_id`, `title`, `summary`, `authors_joined`, `categories_joined`, `age_days`, `text_for_embedding`, ...) |
| **Output** | `data/eval/test_set.json`, `data/quality/*.json`, `data/reports/phase1_report.md`, `data/reports/corruption_report.md` |
| **Module phụ thuộc** | `src/core/config.py`, `src/core/utils.py`, `src/retrieval/index.py` |
| **Module sử dụng output** | `src/pipelines/phase1.py`, `src/pipelines/corruption_flow.py`, Ban giám khảo / Giảng viên |

---

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Great Expectations phiên bản 1.x đã tái cấu trúc toàn diện API. Cú pháp cũ từ bản 0.18 (`context.sources.pandas_default` hoặc `context.add_or_update_expectation_suite`) bị cấm vì gây lỗi crash trong runtime.
- **Các phương án đã cân nhắc:**
  1. *Phương án A:* Dùng Great Expectations với file cấu hình lưu trên ổ đĩa (`gx/great_expectations.yml`).
  2. *Phương án B:* Dùng Great Expectations 1.x với chế độ **Ephemeral Context (In-Memory)**.
- **Phương án đã chọn:** **Phương án B (Ephemeral Context)**.
- **Lý do:** Chế độ Ephemeral không phụ thuộc vào trạng thái file tĩnh trên ổ cứng, khởi tạo nhẹ nhàng, tương thích 100% với CI/CD, không gây xung đột Git giữa các thành viên, và tuân thủ đúng yêu cầu của giảng viên trong tài liệu hướng dẫn.

---

## 6. Lỗi / Blocker đã xử lý

1. **Lỗi phiên bản Python không tương thích:**
   - *Triệu chứng:* `ERROR: Package 'day10-data-observability-lab-student' requires a different Python: 3.14.4 not in '<3.14,>=3.11'`.
   - *Nguyên nhân:* Môi trường ban đầu dùng Python 3.14.4 (bản thử nghiệm), trong khi `pyproject.toml` và các gói AI/ML như `chromadb`, `torch` yêu cầu Python 3.11 - 3.13.
   - *Cách xử lý:* Tạo lại môi trường ảo với **Python 3.12.10** (`py -3.12 -m venv .venv`), sau đó cài đặt bằng `uv pip install -e .`.
2. **Lỗi console encoding trên Windows PowerShell:**
   - *Triệu chứng:* `UnicodeEncodeError: 'charmap' codec can't encode character '\u1ea2' in position 12`.
   - *Nguyên nhân:* Mặc định Windows PowerShell sử dụng codepage `cp1252` không hỗ trợ ký tự tiếng Việt có dấu khi lệnh `print()` xuất chuỗi ra stdout.
   - *Cách xử lý:* Cấu hình `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` ngay đầu script thực thi, đảm bảo toàn bộ bảng Live Demo in ra sắc nét và exit code 0.

---

## 7. Hiểu biết về luồng End-to-End

1. **Dữ liệu đi từ Crossref đến Vector Index như thế nào?**
   - API Crossref trả về JSON thô $\rightarrow$ lưu snapshot bất biến `crossref_records.json` $\rightarrow$ làm sạch HTML/LaTeX tags, trích xuất năm/ngày, tính `age_days`, ghép `text_for_embedding` $\rightarrow$ kiểm định chất lượng qua trạm Great Expectations $\rightarrow$ nhúng vector bằng mô hình `all-MiniLM-L6-v2` $\rightarrow$ lưu trữ vĩnh viễn vào ChromaDB collection.
2. **Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality ra sao?**
   - Bộ đề thi cố định 10 câu hỏi kèm `ground_truth` và `expected_doc_ids`. Khi câu hỏi đi qua RAG:
     - `retrieval_hit_rate` kiểm tra xem tài liệu kỳ vọng có nằm trong top-K tài liệu được tìm kiếm hay không.
     - `mean_token_f1` đo độ trùng khớp từ vựng giữa câu trả lời của AI và đáp án mẫu.
     - `judge_score` (LLM-as-a-judge) chấm điểm độ chính xác ngữ nghĩa và độ bám sát tài liệu (groundedness).
3. **Quality checks khác freshness monitoring ở điểm nào trong bài lab?**
   - *Quality checks (Great Expectations):* Kiểm tra tính toàn vẹn cấu trúc và logic dữ liệu tại một thời điểm (schema, not null, unique, độ dài chuỗi).
   - *Freshness monitoring (SLA):* Đo lường tính thời sự và độ trễ theo thời gian (`age_days > 180`). Dữ liệu có thể hoàn hảo về cấu trúc nhưng vẫn bị đánh giá là lỗi thời (Stale Data).
4. **Vì sao phải dùng cùng test set cho baseline, corrupted và repaired?**
   - Để đảm bảo tính khách quan và khoa học của phép đo (Controlled Experiment). Chỉ khi cùng một bộ câu hỏi kiểm tra trên cùng các tiêu chí, ta mới thấy rõ sự sụt giảm hiệu năng do dữ liệu bẩn và sự phục hồi tuyệt đối sau quá trình Repair.
5. **Repair được xem là thành công dựa trên artifact và metric nào?**
   - Dựa trên việc Great Expectations chuyển từ `FAILED` về `PASSED`, Freshness chuyển từ `STALE` về `FRESH`, chỉ số RAG phục hồi trọn vẹn (Hit Rate từ 60% lên lại 100%, Token F1 từ 0.85 lên 0.95), và ChromaDB loại bỏ triệt để các vector rác (Ghost Vectors).

---

## 8. Phân tích kết quả thực nghiệm

### 8.1. Bảng Metrics đối chiếu 3 trạng thái

| Metric / Tín hiệu giám sát | Baseline (Sạch) | Corrupted (Nhiễm độc) | Repaired (Sau phục hồi) | Nhận xét của cá nhân |
| :--- | :---: | :---: | :---: | :--- |
| **Số lượng bản ghi** | 24 | 22 | 24 | Khôi phục đầy đủ 100% số bản ghi gốc |
| **Data Quality Gate (GX 1.x)** | **PASSED** (100%) | **FAILED** (4/4 lỗi) | **PASSED** (100%) | Chặn đứng hoàn toàn dữ liệu bẩn |
| **Freshness SLA (180 ngày)** | **FRESH** (4.17%) | **STALE** (36.36% > 25%) | **FRESH** (4.17%) | Báo động chính xác khi có tài liệu quá hạn |
| **Retrieval Hit Rate** | **100.0%** (1.0) | **60.0%** (0.6) | **100.0%** (1.0) | Sụt giảm 40% khi data bẩn, phục hồi 100% |
| **Mean Token F1** | **0.9526** | **0.8506** | **0.9526** | Mức độ trùng khớp đáp án khôi phục nguyên vẹn |
| **Judge Accuracy** | **1.0** | **1.0** | **1.0** | Đánh giá chấp nhận được theo chuẩn Judge |
| **Mean Judge Score (Thang 5.0)**| **4.60 / 5.0** | **4.20 / 5.0** | **4.60 / 5.0** | Điểm số chất lượng câu trả lời phục hồi tối đa |

### 8.2. Kết luận chuỗi nguyên nhân — bằng chứng
1. **Chuỗi sự cố:** Bỏ rơi bản ghi mới + cắt cụt text tóm tắt $\rightarrow$ GX phát hiện 4 failed expectations & Freshness cảnh báo `STALE` $\rightarrow$ Vector Store thiếu hụt context khiến Retrieval Hit Rate sụt giảm từ 100% xuống còn 60%.
2. **Chuỗi phục hồi:** Xóa bỏ toàn bộ collection ChromaDB lỗi + chạy lại cleaning pipeline từ nguồn `crossref_records.json` $\rightarrow$ GX và Freshness phục hồi về trạng thái `PASSED` và `FRESH` $\rightarrow$ Hit Rate lấy lại mốc 100%, Mean Token F1 đạt lại 0.9526.

---

## 9. Điều học được và hướng cải thiện

### Ba bài học quan trọng nhất:
1. **Garbage In $\rightarrow$ Garbage Out:** Chất lượng của AI Agent hoàn toàn phụ thuộc vào chất lượng của dữ liệu đầu vào. Tinh chỉnh prompt hay model không thể cứu vãn một vector store chứa dữ liệu rác.
2. **Silent Failure là rủi ro lớn nhất:** Khi dữ liệu bị lỗi, hệ thống không báo crash mà âm thầm hallucinate. Cần phải có các chốt kiểm dịch tự động (Data Quality Gate) và giám sát liên tục (Observability).
3. **Idempotence & Raw Preservation:** Giữ nguyên dữ liệu thô (Raw Preservation) và thiết kế pipeline lũy thừa (Idempotent) là chìa khóa duy nhất giúp hệ thống có khả năng tự phục hồi mà không cần can thiệp thủ công.

### Hướng cải thiện nếu có thêm thời gian:
- Tích hợp thêm OpenTelemetry / Arize Phoenix / LangSmith để theo dõi độ trễ từng bước truy vấn vector (Retrieval Latency) và chi phí token theo thời gian thực.
- Mở rộng tập dữ liệu lên hàng nghìn bài báo với hybrid search (kết hợp BM25 và Dense Vector Retrieval).

---

## 10. Cam kết của thành viên

Đánh dấu xác nhận:
- [x] Nội dung báo cáo phản ánh đúng 100% phần việc và mức hiểu thực tế của tôi.
- [x] Tôi có thể giải thích trôi chảy toàn bộ luồng end-to-end từ Ingestion, Cleaning, Quality Gate, ChromaDB đến Evaluation.
- [x] Mọi kết luận và số liệu trong báo cáo đều có artifact JSON/Markdown thực tế đối chiếu trong repository.
- [x] Tôi không ghi nhận hoàn thành cho các phần chưa được kiểm chứng qua code chạy thực tế.
- [x] Báo cáo tuyệt đối không chứa `.env`, API key, token hoặc secret.

**Người báo cáo:** **Nguyễn Khắc Quang**  
**MSSV:** **2A202602885**  
**Ngày xác nhận:** 2026-09-25
