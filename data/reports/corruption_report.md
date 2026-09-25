# Báo Cáo Đối Chiếu 3 Trạng Thái: Baseline vs Corrupted vs Repaired

- **Thời điểm chạy:** 2026-09-25T09:18:21.827559+00:00
- **Model:** `gemini-2.5-flash` (gemini)
- **Embedding:** `sentence-transformers/all-MiniLM-L6-v2`

## 1. Bảng Ma Trận So Sánh Định Lượng 3 Trạng Thái

| Tiêu chí đánh giá / Metric | 1. Dữ liệu Sạch (Baseline) | 2. Dữ liệu Lỗi (Corrupted) | 3. Sau Phục Hồi (Repaired) | Đánh giá xu hướng & Tác động |
| :--- | :---: | :---: | :---: | :--- |
| **Data Quality Gate (GX 1.x)** | PASSED (True) | FAILED (False) | PASSED (True) | Chốt kiểm dịch chặn đứng bản ghi rác & trùng lặp |
| **Freshness SLA (>180d)** | Tươi mới (True) | Cũ / Quá hạn (False) | Tươi mới (True) | Bắt được 35% bản ghi bị lùi ngày |
| **Retrieval Hit Rate** | **100.00%** | **60.00%** | **100.00%** | Hit rate sụt giảm mạnh khi tài liệu mới bị drop |
| **Mean Token F1** | **1.0000** | **0.6741** | **1.0000** | Câu trả lời mất độ khớp từ vựng khi summary rỗng/nhiễu |
| **Mean Judge Score (1-5)** | **5.00 / 5.0** | **3.60 / 5.0** | **5.00 / 5.0** | Phục hồi hoàn toàn độ chính xác ngữ nghĩa của AI |

## 2. Phân Tích Hiện Tượng Silent Failure
Khi dữ liệu bị tiêm lỗi:
- Các trường `summary` bị xóa rỗng hoặc chèn chuỗi ký tự rác không hề gây ra exception runtime.
- Agent vẫn tự tin trả lời nhưng chất lượng thông tin bị suy thoái nghiêm trọng (Token F1 rớt từ 1.00 xuống 0.67).
- Great Expectations 1.x đóng vai trò then chốt: Chặn đứng dữ liệu hỏng ngay từ trạm trung chuyển, ngăn ngừa độc tố dữ liệu xâm nhập vào Vector Database serving layer.

## 3. Cơ Chế Phục Hồi An Toàn (Idempotent Repair)
- Hệ thống khôi phục dữ liệu sạch hoàn toàn tự động bằng cách đọc lại từ snapshot nguyên cội `data/raw/crossref_records.json`.
- Áp dụng các quy tắc làm sạch chuẩn hóa và tái lập các index ChromaDB.
- Tính chất **Idempotent**: Chạy lại tiến trình bao nhiêu lần vẫn cho ra đúng một kết quả chuẩn sạch nhất quán, đưa các chỉ số RAG trở lại mức tối ưu ban đầu.
