# Member Role Report — Day 10: Data Pipeline & Data Observability
## BÁO CÁO CÁ NHÂN — THÀNH VIÊN 2

---

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| :--- | :--- |
| **Họ và tên** | Quang (Điền đầy đủ: `[Họ và Tên]`) |
| **MSSV** | `[Điền MSSV]` |
| **Email** | `[Điền Email]` |
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

1. **Data Lineage & Raw Preservation:**
   - File snapshot gốc `data/raw/crossref_records.json` là "nguồn chân lý" duy nhất. Toàn bộ các bước biến đổi dữ liệu phía sau đều bắt nguồn từ đây.
2. **Silent Failure trong AI:**
   - Lỗi dữ liệu không làm sập code mà làm sai lệch ngữ nghĩa vector embedding. Khi cosine similarity chọn nhầm passage, LLM bắt buộc phải bịa đặt câu trả lời.
3. **Idempotence trong Data Engineering:**
   - Luồng phục hồi (Repair) có tính lũy thừa: chạy lại bao nhiêu lần vẫn cho ra cùng một kết quả chuẩn sạch duy nhất, xóa sạch vector rác (Ghost Vectors) trong ChromaDB.
