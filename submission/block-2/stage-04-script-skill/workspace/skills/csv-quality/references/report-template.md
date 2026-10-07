# Báo cáo chất lượng dữ liệu và quá tải: `{input}`

Công cụ: `skills/csv-quality/scripts/check_csv.py` | exit code: {exit_code}

Ngưỡng: **{max_hours} giờ**. Chỉ tổng lớn hơn ngưỡng là quá tải; bằng ngưỡng không quá tải.

## Tổng quan
| Chỉ số | Giá trị |
|---|---|
| Số dòng dữ liệu (không tính header) | {row_count} |
| Dòng thiếu owner | {missing_owner_count} |
| Dòng hours không hợp lệ | {invalid_hours_count} |
| Số task_id bị lặp (distinct) | {duplicate_id_count} ({duplicate_ids}) |

Các thống kê chất lượng xét toàn bộ dữ liệu, bao gồm cả dòng không được cộng giờ.

## Tổng giờ theo người

| Owner | Tổng giờ |
|---|---|
| {Mỗi owner trong hours_by_owner} | {total} |

Nếu object rỗng, ghi không có dòng hợp lệ để cộng giờ.

## Người vượt ngưỡng

Liệt kê mọi `overloaded_owners`, gồm owner và total_hours. Nếu danh sách rỗng,
ghi rõ **không ai vượt ngưỡng**. Không coi người bằng ngưỡng là quá tải.

## Dòng bị loại khỏi tổng giờ

| Dòng | task_id | Tất cả lý do |
|---|---|---|
| {line} | {task_id hoặc null} | {reasons} |

Lấy từ `excluded_rows`, mỗi dòng một lần, giữ mọi mã lý do. Các mã là:
`wrong_field_count` sai số trường; `missing_task_id` thiếu ID; `duplicate_id`
ID xuất hiện sau lần đầu; `missing_owner` thiếu người; `invalid_hours` giờ không hợp lệ.

## Chi tiết lỗi
| Line | Cột | Loại | task_id | Mô tả |
|---|---|---|---|---|
| {line} | {column} | {type} | {task_id} | {message} |

## Đánh giá
- Tổng chỉ dùng dòng hợp lệ và lần đầu mỗi ID; lần đầu có lỗi vẫn giữ chỗ ID,
  không dùng lần hợp lệ sau. Bỏ khoảng trắng; phân biệt tên owner và hoa/thường.
- Dữ liệu có lỗi vẫn được phân tích; tổng không gồm dòng bị loại. Không sửa CSV.

## Khuyến nghị
- {Cách sửa đề xuất cho từng nhóm lỗi; không tự sửa file nguồn}

Mọi số liệu lấy từ JSON hiện tại. Khi lệnh lỗi, chỉ báo lỗi thực thi; không dùng
mẫu này để viết báo cáo như thể phân tích đã thành công.
