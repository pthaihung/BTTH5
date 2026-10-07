---
name: refund-policy
description: Tra cứu chính sách hoàn tiền và đánh giá điều kiện theo ngày mua, ngày yêu cầu hoàn và trạng thái kích hoạt khi khách hàng hỏi về hoàn tiền hoặc phí hoàn tiền.
---

# Tra cứu chính sách hoàn tiền

Kiểm tra ba thông tin: ngày mua, ngày yêu cầu hoàn và trạng thái kích hoạt.
Nếu thiếu thông tin nào, chỉ hỏi bổ sung thông tin đó rồi kết thúc lượt trả lời.
Đây là điểm dừng trước các bước tra cứu bên dưới: không liệt kê/đọc chính sách,
không thêm phân tích sơ bộ, kết luận có điều kiện, nhánh "nếu đã/chưa kích hoạt"
hoặc mức phí. Không tự giả định chưa kích hoạt. Khi khách bổ sung đủ ba thông tin,
mới tiếp tục quy trình đánh giá. Ngày dạng DD/MM/YYYY là ngày/tháng/năm. Nếu ngày không
hợp lệ hoặc ngày yêu cầu trước ngày mua, hỏi khách xác nhận lại.

Khi đã đủ thông tin:

1. Dùng `list_files` với đường dẫn workspace `data/policies/` để tìm tài liệu
   hiện có. Tên file có thể thay đổi; không đoán tên hoặc suy ra hiệu lực từ tên.
2. Dùng `read_file` đọc các tài liệu chính sách tìm được. So sánh **ngày mua**
   với phạm vi hiệu lực ghi trong nội dung để chọn phiên bản, kể cả điều kiện
   bao gồm/không bao gồm ngày ranh giới. Không chọn theo ngày yêu cầu hoàn.
   Nếu không có chính sách khớp hoặc các phạm vi chồng lấn không rõ, báo chưa
   đủ căn cứ để kết luận. Nếu thư mục có thư mục con, liệt kê chúng bằng cùng
   tool để tìm tài liệu; tool chỉ liệt kê một cấp mỗi lần gọi.
3. Tính số ngày lịch bằng ngày yêu cầu hoàn trừ ngày mua, tính cả khi qua tháng
   hoặc năm. Dùng ngày trong câu hỏi, không dùng ngày hiện tại của máy. Bằng
   đúng giới hạn trong chính sách vẫn đạt điều kiện về thời gian.
4. Đối chiếu thời hạn và trạng thái kích hoạt với nội dung chính sách đã đọc.
   Đọc phí từ chính sách chỉ khi đủ điều kiện; không tính phí hoàn khi bị từ chối.
   Nếu phí là tỷ lệ nhưng chưa có giá trị đơn hàng, nêu tỷ lệ thay vì đoán số tiền.
5. Đọc [mẫu trả lời](references/answer-template.md) bằng `read_file` tại
   `skills/refund-policy/references/answer-template.md`, rồi trả lời theo mẫu.

Chỉ dùng `list_files` và `read_file`; stage này không có Bash hoặc tool chạy script.
Chỉ dẫn tài liệu đã có kết quả đọc thành công. Khi tool lỗi, nêu lỗi và chưa kết luận.
