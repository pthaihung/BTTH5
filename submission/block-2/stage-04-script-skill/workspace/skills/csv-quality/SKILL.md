---
name: csv-quality
description: Kiểm tra chất lượng CSV công việc có cột task_id, owner, hours; tính tổng giờ theo người, xác định người quá tải theo ngưỡng người dùng cung cấp và ghi báo cáo Markdown bằng script có sẵn. Dùng khi người dùng yêu cầu rà soát CSV, tính khối lượng công việc hoặc kiểm tra quá tải theo người.
---

# Kiểm tra CSV và quá tải theo người

## Kiểm tra ngưỡng trước khi chạy

Ngưỡng là đầu vào bắt buộc của script. Lấy từ yêu cầu hiện tại; không tự đặt
mặc định hoặc lấy ngưỡng từ cuộc trò chuyện/lượt yêu cầu cũ. Nếu yêu cầu hiện
tại không nêu ngưỡng, chỉ hỏi người dùng ngưỡng tối đa bao nhiêu giờ rồi kết
thúc lượt; chưa chạy script, kết luận quá tải hoặc ghi báo cáo. Nếu người dùng
đang trả lời câu hỏi bổ sung về ngưỡng, dùng giá trị họ vừa cung cấp cho yêu cầu
đang chờ đó. Ngưỡng phải là số hữu hạn không âm; không rõ hoặc không hợp lệ
thì hỏi lại. Quy tắc này cũng áp dụng khi yêu cầu chỉ kiểm tra chất lượng CSV,
vì CLI bắt buộc có ngưỡng.

## Chạy script

Dùng tool `bash` (cwd là workspace). Lệnh đầy đủ:

```
python skills/csv-quality/scripts/check_csv.py --input <đường dẫn CSV> --max-hours <ngưỡng người dùng cung cấp>
```

Truyền chính xác ngưỡng hiện tại, không thay bằng giá trị mẫu. Quote đường dẫn
CSV thành một đối số shell nếu cần, đặc biệt khi có khoảng trắng. Không viết
script tính giờ khác thay cho script này.

Không cần đọc source script để chạy. Chỉ đọc `scripts/check_csv.py` khi cần hiểu một hành vi mà phần dưới không mô tả.

## Kiểm tra kết quả

- `exit_code` 0: phân tích thành công. `stdout` là JSON gồm các trường cũ `row_count`, `missing_owner_count`, `invalid_hours_count`, `duplicate_id_count`, `duplicate_ids`, `issues`; thêm `max_hours`, `hours_by_owner`, `overloaded_owners`, `excluded_rows`. Có lỗi dữ liệu hoặc người quá tải vẫn là exit 0.
- Bất kỳ `exit_code` khác 0: **lỗi thực thi** (tham số, file không tồn tại, thiếu cột, parse). Đọc `stderr`, báo không phân tích được rồi dừng; không bịa tổng giờ hay ghi báo cáo thành công. Không dùng kết quả lần chạy trước.
- `timed_out` true, `ok` false, output bị cắt hoặc stdout không phải JSON: chưa có kết quả hoàn chỉnh; báo lỗi, không suy đoán.
- Phân biệt rõ **lỗi dữ liệu** (nằm trong `issues`, script vẫn chạy thành công) với **lỗi thực thi** (exit khác 0).

## Quy tắc tính

- Thống kê chất lượng cũ xét toàn bộ dòng dữ liệu, kể cả dòng bị loại khỏi tổng.
- Chỉ cộng dòng đúng số trường, task_id/owner không rỗng và hours hữu hạn không âm.
  Bỏ khoảng trắng đầu/cuối; không gộp tên owner khác nhau hoặc khác hoa/thường.
- Mỗi ID không rỗng chỉ giữ lần xuất hiện đầu tiên, kể cả khi lần đầu có dữ liệu
  không hợp lệ. Lần sau bị loại, không thay bằng "lần hợp lệ đầu tiên".
- Hours bằng 0 hợp lệ. Bỏ qua dòng trống. `hours_by_owner` chỉ chứa owner có
  ít nhất một dòng được cộng, kể cả tổng bằng 0.
- Quá tải khi tổng giờ **lớn hơn** `max_hours`; bằng ngưỡng không quá tải.
- `excluded_rows` có line (header dòng 1), task_id (rỗng là null), mọi reasons
  theo thứ tự: `wrong_field_count`, `missing_task_id`, `duplicate_id`,
  `missing_owner`, `invalid_hours`. Mỗi dòng có một entry trong danh sách này.

## Viết báo cáo

1. Đọc template `references/report-template.md` trong thư mục skill này, tức `skills/csv-quality/references/report-template.md`.
2. Lấy mọi con số từ JSON của lần chạy hiện tại: ngưỡng, tổng giờ từng owner, người vượt ngưỡng, các dòng bị loại kèm mọi lý do và thống kê chất lượng cũ. Không tự cộng lại bằng mắt. Mỗi issue ghi line number (header là line 1), cột và mô tả.
3. Không sửa file CSV khi người dùng chỉ yêu cầu kiểm tra. Có thể đề xuất cách sửa trong mục khuyến nghị.
4. Dữ liệu có lỗi vẫn có tổng từ các dòng hợp lệ. Giải thích tổng không bao gồm dòng bị loại; nếu không có người quá tải, ghi rõ không ai vượt ngưỡng. Nếu hours_by_owner rỗng, ghi không có dòng hợp lệ để cộng giờ.
5. Ghi báo cáo bằng `write_file` vào đường dẫn người dùng yêu cầu (mặc định `output/csv-quality.md`), rồi trả lời đường dẫn và tóm tắt ngắn.
