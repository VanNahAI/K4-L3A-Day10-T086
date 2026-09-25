# 📊 Báo Cáo Chất Lượng Dữ Liệu & RAG Baseline (Phase 1 Report)

> **Thời gian tạo báo cáo:** `2026-09-25 09:57:44 UTC`  
> **Trạng thái:** Baseline Pipeline hoàn thành thành công  

---

## 1. Tổng Quan Thu Thập & Chất Lượng Dữ Liệu (Ingestion & Quality Gate)

| Chỉ số kiểm định | Giá trị ghi nhận | Tiêu chuẩn chất lượng (SLA) | Trạng thái |
| :--- | :---: | :---: | :---: |
| **Số lượng bản ghi sạch** | `24` | $\ge 5$ bản ghi | ✅ Đạt yêu cầu |
| **Great Expectations 1.x Gate** | `PASSED (True)` | `success = True` (4 rules) | ✅ PASSED |
| **Tổng số Expectations đã chạy** | `6` | Đủ 4-6 rules thiết yếu | ✅ Đầy đủ |
| **Độ tươi mới dữ liệu (Freshness SLA)** | `Tươi mới (True)` | Tỷ lệ quá hạn $\le 25\%$ | ✅ Tươi mới |
| **Tỷ lệ bài báo quá hạn 180 ngày** | `4.2%` | Ngưỡng cảnh báo: $25\%$ | ✅ Nằm trong ngưỡng |
| **Bản ghi mới nhất (`latest_published`)** | `2026-07-22` | — | — |
| **Bản ghi cũ nhất (`oldest_published`)** | `2026-03-28` | — | — |

---

## 2. Kết Quả Đo Lường Hiệu Năng RAG (Baseline Benchmark Metrics)

Bộ đề thi chuẩn hóa gồm **10 câu hỏi** bao phủ 4 nhóm nghiệp vụ (`summary`, `authors`, `date`, `categories`) được dùng để đo lường:

| Chỉ số đánh giá | Điểm số Baseline | Mục tiêu tối thiểu | Đánh giá kỹ thuật |
| :--- | :---: | :---: | :--- |
| **Retrieval Hit Rate** | **`100.0%`** | $\ge 90\%$ | Khả năng truy xuất chính xác tài liệu nguồn vào Top-K context |
| **Mean Token F1** | **`0.9526`** | $\ge 0.60$ | Độ trùng khớp câu từ chi tiết giữa câu trả lời và Ground Truth |
| **LLM Judge Accuracy** | **`100.0%`** | $\ge 80\%$ | Tỷ lệ câu trả lời được LLM Judge công nhận đúng về bản chất |
| **LLM Judge Score** | **`4.60 / 5.0`** | $\ge 4.0 / 5.0$ | Đánh giá toàn diện về tính chính xác và không Hallucination |

---

## 3. Kết Luận & Đánh Giá Sẵn Sàng (Readiness)
- Luồng Ingestion và Cleaning đảm bảo tính nhất quán (Consistency) và toàn vẹn dữ liệu (Data Integrity).
- Quality Gate (Great Expectations 1.x) đã xác thực thành công cấu trúc schema, khóa chính `paper_id`, và độ dài tối thiểu của tóm tắt khoa học.
- Môi trường Vector Store ChromaDB collection `papers-baseline` hoạt động ổn định và sẵn sàng phục vụ các truy vấn nghiệp vụ.
