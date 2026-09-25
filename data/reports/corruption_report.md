# 🔬 Báo Cáo Đối Chiếu Độc Tính Dữ Liệu & Phục Hồi An Toàn (Corruption & Repair Report)

> **Thời gian tạo:** `2026-09-25 10:01:27 UTC`  
> **Mục tiêu:** Chứng minh hiện tượng **Silent Failure** khi dữ liệu bị lỗi và năng lực **Idempotent Repair** khôi phục hệ thống về trạng thái chuẩn sạch.

---

## 1. Bảng Ma Trận So Sánh 3 Trạng Thái (Comparative 3-State Matrix)

| Tiêu chí đánh giá / Metric | 1. Dữ liệu Sạch (Baseline) | 2. Dữ liệu Bị Tiêm Lỗi (Corrupted) | 3. Sau Khi Phục Hồi (Repaired) | Đánh giá xu hướng biến động |
| :--- | :---: | :---: | :---: | :--- |
| **GX 1.x Quality Gate** | **PASSED (True)** | **FAILED (False)** | **PASSED (True)** | ✅ Quality Gate chặn đứng dữ liệu bẩn thành công |
| **Freshness SLA (>180 ngày)** | **Tươi mới (True)** | **Quá hạn (False)** | **Tươi mới (True)** | ✅ Hệ thống cảnh báo chính xác khi dữ liệu bị làm cũ |
| **Retrieval Hit Rate** | **100.0%** | **60.0%** | **100.0%** | 📉 Sụt giảm mạnh khi mất dữ liệu $\rightarrow$ 📈 Phục hồi 100% |
| **Mean Token F1** | **0.9526** | **0.8506** | **0.9526** | 📉 Rớt sâu do thiếu context $\rightarrow$ 📈 Khôi phục hoàn toàn |
| **LLM Judge Score (1-5)** | **4.60 / 5.0** | **4.20 / 5.0** | **4.60 / 5.0** | 📉 Tăng nguy cơ ảo giác $\rightarrow$ 📈 Trả lời chuẩn xác |

---

## 2. Phân Tích Hiện Tượng Silent Failure & Ảo Giác AI

Khi hệ thống bị tiêm 6 kịch bản lỗi thực tế (xóa tóm tắt, cắt ngắn tiêu đề, bỏ rơi bản ghi mới, chèn ký tự nhiễu, nhân bản dòng, làm cũ ngày tháng):
1. **AI Agent không hề ném lỗi runtime (`throw Exception`):**
   - Chương trình vẫn tiếp tục chạy, HTTP 200, Agent vẫn sinh câu trả lời hết sức trôi chảy và tự tin.
2. **Nhưng kết quả nghiệp vụ hoàn toàn sai lệch:**
   - Do Vector Database lưu trữ vector nhúng từ văn bản lỗi (`blank summary` hoặc `corrupted text`), độ tương đồng Cosine Similarity bị biến dạng nghiêm trọng.
   - Khi người dùng hỏi thông tin, bộ tìm kiếm không lấy được tài liệu liên quan hoặc lấy nhầm tài liệu rác. LLM buộc phải bịa câu trả lời (**Hallucination**), khiến `Mean Token F1` và `LLM Judge Score` lao dốc không phanh.
3. **Ý nghĩa của Data Quality Gate (GX 1.x & Freshness SLA):**
   - Nếu không có trạm kiểm dịch Great Expectations chặn từ đầu nguồn, dữ liệu bẩn sẽ âm thầm lọt vào Vector Store và đầu độc AI trên môi trường Production suốt nhiều tuần mà không ai hay biết.

---

## 3. Cơ Chế Phục Hồi An Toàn (Idempotent Repair)

1. **Bảo tồn bản gốc (Raw Preservation):**
   - File thô gốc `data/raw/crossref_records.json` luôn được giữ nguyên vẹn như một nguồn chân lý (Single Source of Truth), không bao giờ bị ghi đè hay sửa đổi trực tiếp.
2. **Tính lũy thừa (Idempotence):**
   - Hàm `repair_pipeline` có thể chạy lại bất kỳ lúc nào, bao nhiêu lần tùy ý, trên bất kỳ trạng thái dữ liệu hỏng nào mà vẫn luôn cho ra cùng một kết quả sạch duy nhất.
   - Collection `papers-repaired` trên ChromaDB được tái tạo hoàn toàn, xóa sạch mọi dấu vết của vector rác (Ghost Vectors).
3. **Kết luận:** Hệ thống đã vượt qua bài kiểm tra toàn diện về khả năng tự phục hồi và đảm bảo độ tin cậy cấp doanh nghiệp cho RAG Pipeline.
