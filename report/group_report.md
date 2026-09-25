# Group Report — Day 10: Data Pipeline & Data Observability
## BÁO CÁO TỔNG KẾT NHÓM

---

## 1. Thông tin bài nộp

| Thông tin | Nội dung |
| :--- | :--- |
| **Khóa / Lớp** | K4-L3A-Day10 |
| **Tên nhóm** | K4-L3A-Day10-T086 |
| **Repository** | `https://github.com/VanNahAI/K4-L3A-Day10-T086` |
| **Ngày hoàn thành** | 2026-09-25 |

### Thành viên và phân công (Cơ cấu nhóm 2 người)

| STT | Họ và tên | MSSV | Vai trò chính | Module / Deliverable sở hữu |
| --: | :--- | :--- | :--- | :--- |
| 1 | [Điền Họ Tên 1] | [Điền MSSV 1] | **Pipeline Lead & Data Foundation Owner** | Ingestion (`crossref.py`), Cleaning (`cleaning.py`), Corruption (`corruption.py`), Pipeline Orchestration (`phase1.py`, `corruption_flow.py`) |
| 2 | Quang | [Điền MSSV 2] | **RAG Specialist & Observability & Evaluation Lead** | Data Quality Gate GX 1.x & Freshness SLA (`quality.py`), Benchmark Test Set (`testset.py`), Vector Store (`index.py`), Reporting (`reporting.py`) |

---

## 2. Tóm tắt kết quả

Nhóm đã hoàn thành trọn vẹn 100% các yêu cầu từ Checkpoint 0 đến Checkpoint 6 của bài thực hành:
1. **Baseline Data Pipeline:** Xây dựng luồng xử lý dữ liệu học thuật tự động từ Crossref API (kèm cơ chế cứu hộ offline snapshot), chuẩn hóa 24 bài báo khoa học, tính tuổi dữ liệu `age_days`, tạo ngữ cảnh `text_for_embedding` và nạp vào ChromaDB collection `papers-baseline` với mô hình nhúng `all-MiniLM-L6-v2`.
2. **Data Observability (GX 1.x & Freshness):** Thiết lập trạm kiểm soát tự động theo chuẩn Great Expectations 1.x Ephemeral context với 4 Expectations cốt lõi (row count, not null, unique `paper_id`, summary min length) và giám sát Freshness SLA 180 ngày.
3. **Thử thách tiêm lỗi (Controlled Corruption):** Triển khai Synthetic Corruption Suite với 6 kịch bản lỗi thực tế (drop latest records, blank summary, inject noise, truncate title, stale date, duplicate rows).
4. **Phát hiện Silent Failure & Tự phục hồi (Idempotent Repair):** Chứng minh Quality Gate lập tức gióng chuông cảnh báo (`success = False`, `is_fresh = False`). Khi dữ liệu bị lỗi, Retrieval Hit Rate sụt giảm nghiêm trọng từ $100\%$ xuống $60\%$. Cơ chế phục hồi an toàn từ Raw Snapshot đã tái tạo hoàn toàn hệ thống về trạng thái sạch, khôi phục Hit Rate và Token F1 về $100\%$ phong độ ban đầu.

---

## 3. Kiến trúc và luồng dữ liệu

### Luồng End-to-End

```text
Nguồn Crossref API / Snapshot Local
    │
    ├── 1. Raw Ingestion & Preservation ──> data/raw/crossref_records.json
    ├── 2. Transformation & Cleaning    ──> data/clean/papers_clean.csv (16 cột chuẩn hóa)
    ├── 3. Data Observability Gate      ──> Great Expectations 1.x (4 rules) + Freshness SLA
    ├── 4. Vector Store Indexing        ──> sentence-transformers/all-MiniLM-L6-v2 + ChromaDB
    ├── 5. Benchmark Evaluation         ──> 10 câu hỏi testset (Hit Rate, Token F1, LLM Judge)
    ├── 6. Synthetic Data Corruption    ──> Giả lập 6 lỗi dữ liệu thực tế (Silent Failure)
    └── 7. Idempotent Repair & Compare  ──> Tái tạo từ Raw & Báo cáo đối chiếu 3 trạng thái
```

### Trách nhiệm của từng khối

| Khối | Input | Xử lý chính | Output / Artifact | Owner |
| :--- | :--- | :--- | :--- | :---: |
| **Ingestion** | Crossref REST API / Snapshot | Fetch, fallback offline, bóc tách `PaperRecord` | `data/raw/crossref_records.json` | Thành viên 1 |
| **Cleaning** | `list[PaperRecord]` | Khử HTML tag, tính `age_days`, tạo `text_for_embedding` | `data/clean/papers_clean.csv` | Thành viên 1 |
| **Observability** | Clean/Corrupted/Repaired DF | GX 1.x Ephemeral validation (4 rules), Freshness SLA | `data/quality/*.json` | Thành viên 2 |
| **Evaluation** | Clean DataFrame | Sinh 10 câu hỏi bao phủ 4 nhóm (`summary`, `authors`, `date`, `categories`) | `data/eval/test_set.json` | Thành viên 2 |
| **Embedding / Index**| Clean/Corrupted/Repaired DF | MiniLM vector embedding, Cosine similarity | 3 Collections ChromaDB (`baseline`, `corrupted`, `repaired`) | Thành viên 2 |
| **Corruption** | Clean DataFrame | Tiêm 6 dạng độc tố dữ liệu, ghi nhật ký lỗi | `data/clean/*_corrupted.csv`, `corruption_log.json` | Thành viên 1 |
| **Repair & Orchestration** | Raw snapshot | Khôi phục Idempotent từ gốc, chạy chu trình 3 pha | `data/reports/corruption_report.md` | Thành viên 1 & 2 |

---

## 4. Cách tái hiện kết quả

### Cấu hình môi trường

| Biến / Cấu hình | Giá trị sử dụng |
| :--- | :--- |
| `LLM_PROVIDER` | `gemini` (hoặc `mock` khi không có API key) |
| `LLM_MODEL` | `gemini-2.5-flash` |
| Embedding model | `sentence-transformers/all-MiniLM-L6-v2` |
| Số lượng records | 24 bài báo học thuật |
| Retrieval `top_k` | 4 |
| Freshness threshold | 180 ngày |

### Lệnh cài đặt và chạy thực thi

```powershell
# Kích hoạt môi trường ảo
.\.venv\Scripts\Activate.ps1

# Chạy Baseline Pipeline (Checkpoint 3)
python script/run_phase1.py

# Chạy Corruption Flow & Idempotent Repair (Checkpoint 4 & 5)
python script/run_corruption_flow.py
```

### Kết quả tái hiện thực tế

| Lệnh | Trạng thái | Thời điểm chạy | Bằng chứng nghiệm thu |
| :--- | :---: | :---: | :--- |
| `run_phase1.py` | ✅ Thành công (Exit code 0) | 2026-09-25 | `data/reports/phase1_report.md`, `baseline_metrics.json` |
| `run_corruption_flow.py` | ✅ Thành công (Exit code 0) | 2026-09-25 | `data/reports/corruption_report.md`, in bảng Live Demo ra console |

---

## 5. Ingestion, Cleaning và Data Contract

### Schema DataFrame chuẩn hóa (`papers_clean.csv`)
Gồm 16 trường thông tin nghiêm ngặt:
- `paper_id` (str): Mã định danh DOI độc nhất, khóa chính (Not Null, Unique).
- `title` (str): Tiêu đề bài báo ($\ge 8$ ký tự).
- `summary` (str): Tóm tắt đã loại bỏ thẻ XML/JATS ($\ge 30$ ký tự).
- `authors` (list[str]) & `authors_joined` (str): Tác giả nối bằng dấu phẩy.
- `categories` (list[str]) & `categories_joined` (str): Chuyên ngành nối bằng dấu phẩy.
- `published` & `updated` (str): Chuỗi ngày ISO `YYYY-MM-DD`.
- `age_days` (int): Số ngày tính từ ngày xuất bản đến ngày chạy pipeline.
- `text_for_embedding` (str): Chuỗi ngữ cảnh đầy đủ 5 phần phục vụ sinh vector.

---

## 6. Kết quả Baseline vs Corrupted vs Repaired

### Bảng Ma Trận So Sánh Định Lượng 3 Trạng Thái

| Tiêu chí đánh giá / Metric | 1. Dữ liệu Sạch (Baseline) | 2. Dữ liệu Lỗi (Corrupted) | 3. Sau Phục Hồi (Repaired) | Đánh giá xu hướng & Tác động |
| :--- | :---: | :---: | :---: | :--- |
| **Số lượng bản ghi** | 24 | 22 (mất 20% bản ghi mới) | 24 | Phục hồi toàn vẹn số lượng |
| **Quality Gate (GX 1.x)** | **PASSED (True)** | **FAILED (False)** | **PASSED (True)** | Chặn đứng dữ liệu bẩn và trùng lặp |
| **Freshness SLA (>180d)** | **FRESH (True)** | **STALE (False)** | **FRESH (True)** | Phát hiện chính xác bài báo bị lùi ngày |
| **Retrieval Hit Rate** | **100.00%** | **60.00%** | **100.00%** | Sụt giảm mạnh $\rightarrow$ Phục hồi 100% |
| **Mean Token F1** | **0.9526** | **0.8506** | **0.9526** | Mất từ vựng khi rỗng context $\rightarrow$ Khôi phục hoàn toàn |
| **Mean Judge Score (1-5)** | **4.60 / 5.0** | **4.20 / 5.0** | **4.60 / 5.0** | Loại bỏ nguy cơ Hallucination |

### Kết luận nhân quả quan trọng
1. **Tiêm lỗi dữ liệu $\rightarrow$ Quality Gate báo động $\rightarrow$ Hiệu năng RAG sụp đổ:**
   - Khi xóa rỗng trường `summary` hoặc drop bản ghi mới, mã nguồn ứng dụng không hề gặp lỗi runtime (`HTTP 200`). Nhưng bộ tìm kiếm vector bị mù ngữ cảnh, Hit Rate rớt từ $100\%$ xuống $60\%$, minh chứng rõ nét cho hiện tượng **Silent Failure**.
2. **Khôi phục an toàn (Idempotent Repair) $\rightarrow$ Khôi phục trọn vẹn chất lượng:**
   - Hệ thống tái tạo lại từ bản thô ban đầu `data/raw/crossref_records.json` (Single Source of Truth), thiết lập lại Chroma collection `papers-repaired`, đưa toàn bộ chỉ số Hit Rate ($100\%$) và Token F1 ($0.9526$) trở về mức tối ưu ban đầu.

---

## 7. Checklist nghiệm thu trước khi nộp bài

- [x] Cấu trúc thư mục module hóa sạch sẽ, môi trường Python 3.12 sẵn sàng.
- [x] Lệnh `python script/run_phase1.py` chạy exit code 0.
- [x] Lệnh `python script/run_corruption_flow.py` chạy exit code 0.
- [x] Đầy đủ các artifact trong `data/raw/`, `data/clean/`, `data/eval/`, `data/quality/`, `data/results/`, `data/reports/`.
- [x] Data Quality Gate tuân thủ 100% chuẩn **Great Expectations 1.x Ephemeral context**.
- [x] Không hardcode đường dẫn tuyệt đối local (`C:\...` hay `f:\...`).
- [x] Không commit API Key hay file `.env` lên GitHub.
- [x] Cả 2 thành viên đều có commit trên nhánh `main`.
