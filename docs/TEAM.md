# Danh Sách Thành Viên & Báo Cáo Phân Công Nhóm

- **Tên Nhóm:** `[Điền tên nhóm]`
- **Mã Nhóm / Lớp:** `K4-L3-DAY10`
- **Tên Repository Nộp Bài:** `K4-L3-DAY10-TenNhom-DataPipeline`

---

## # Thành viên (Cơ cấu Nhóm 2 người)

| STT | Họ và tên | MSSV | Email | Vai trò & Phân công công việc | Báo cáo cá nhân |
|---:|---|---|---|---|---|
| 1 | [Điền Họ Tên 1] | [Điền MSSV 1] | [Điền Email 1] | **Pipeline Lead & Data Foundation Owner** (`crossref.py`, `cleaning.py`, `corruption.py`, `phase1.py`, `corruption_flow.py`, `script/`) | `report/<MSSV1>_<HoTen1>.md` |
| 2 | Nguyễn Khắc Quang | 2A202602885 | quang180204@gmail.com | **RAG Specialist & Observability & Evaluation Lead** (`quality.py` GX 1.x, `testset.py`, `index.py`, `reporting.py`, `metrics.py`) | [`report/2A202602885_NguyenKhacQuang.md`](../report/2A202602885_NguyenKhacQuang.md) |

*(Chi tiết phân công, đặc tả kỹ thuật và cách chạy song song được quy định tại [TASK_MEMBER_1_PIPELINE_DATA_FOUNDATION.md](../TASK_MEMBER_1_PIPELINE_DATA_FOUNDATION.md), [TASK_MEMBER_2_RAG_OBSERVABILITY_EVAL.md](../TASK_MEMBER_2_RAG_OBSERVABILITY_EVAL.md) và [TASK_INTEGRATION_AND_MERGE_GUIDE.md](../TASK_INTEGRATION_AND_MERGE_GUIDE.md))*

---

## # Cá nhân

### ## [HoVaTen1-MSSV1]
- **Vai trò:** Pipeline Lead & Data Foundation Owner.
- **Công việc chi tiết đã hoàn thành:**
  - Thiết lập module thu thập Crossref REST API kèm fallback nạp snapshot offline (`src/ingestion/crossref.py`).
  - Tiền xử lý, tính toán `age_days`, làm sạch và chuẩn hóa `text_for_embedding` (`src/ingestion/cleaning.py`).
  - Xây dựng bộ giả lập Synthetic Data Corruption Suite với 6 dạng lỗi thực tế (`src/ingestion/corruption.py`).
  - Điều phối Baseline Pipeline (`src/pipelines/phase1.py`) và luồng Phục hồi Idempotent Repair (`src/pipelines/corruption_flow.py`).
- **Điều học được / Đóng góp chính:**
  - Hiểu sâu sắc về thiết kế Idempotent Pipeline, Data Lineage và bảo toàn bản gốc (Raw Preservation).

### ## NguyenKhacQuang-2A202602885
- **Họ và tên:** Nguyễn Khắc Quang
- **MSSV:** 2A202602885
- **Vai trò:** RAG Specialist & Observability & Evaluation Lead.
- **Báo cáo chi tiết:** [`report/2A202602885_NguyenKhacQuang.md`](../report/2A202602885_NguyenKhacQuang.md)
- **Công việc chi tiết đã hoàn thành:**
  - Thiết lập trạm kiểm soát chất lượng tự động theo chuẩn **Great Expectations 1.x** (Ephemeral context, 4 rules bắt buộc) và Freshness SLA 180 ngày (`src/observability/quality.py`).
  - Xây dựng bộ câu hỏi Benchmark Test Set 10 câu qua 4 nhóm nghiệp vụ (`src/evaluation/testset.py`) sinh ra `data/eval/test_set.json`.
  - Quản lý 3 collection ChromaDB (`papers-baseline`, `papers-corrupted`, `papers-repaired`) và mô hình embedding MiniLM (`src/retrieval/`).
  - Thiết kế generator xuất báo cáo Phase 1 (`phase1_report.md`) và Bảng ma trận đối chiếu 3 trạng thái (`corruption_report.md`) trong `src/observability/reporting.py`.
  - Sửa lỗi encoding console Windows (`cp1252`) trong pipeline và loại bỏ 100% đường dẫn tuyệt đối local trong tài liệu.
- **Điều học được / Đóng góp chính:**
  - Hiểu sâu sắc về cơ chế kiểm soát chất lượng dữ liệu để chặn đứng hiện tượng Silent Failure & Hallucination trong các hệ thống RAG Production.

