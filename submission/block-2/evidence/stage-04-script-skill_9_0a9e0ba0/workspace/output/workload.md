# Báo cáo chất lượng dữ liệu và quá tải: `data/workload.csv`

Công cụ: `skills/csv-quality/scripts/check_csv.py` | exit code: 0

Ngưỡng: **9.0 giờ**. Chỉ tổng lớn hơn ngưỡng là quá tải; bằng ngưỡng không quá tải.

## Tổng quan
| Chỉ số | Giá trị |
|---|---|
| Số dòng dữ liệu (không tính header) | 6 |
| Dòng thiếu owner | 1 |
| Dòng hours không hợp lệ | 1 |
| Số task_id bị lặp (distinct) | 1 (T02) |

Các thống kê chất lượng xét toàn bộ dữ liệu, bao gồm cả dòng không được cộng giờ.

## Tổng giờ theo người

| Owner | Tổng giờ |
|---|---|
| Lan | 9.0 |
| Minh | 3.0 |

## Người vượt ngưỡng

**Không ai vượt ngưỡng.** Không có owner nào có tổng giờ lớn hơn 9 giờ.

## Dòng bị loại khỏi tổng giờ

| Dòng | task_id | Tất cả lý do |
|---|---|---|
| 5 | T04 | invalid_hours |
| 6 | T02 | duplicate_id |
| 7 | T05 | missing_owner |

## Chi tiết lỗi
| Line | Cột | Loại | task_id | Mô tả |
|---|---|---|---|---|
| 5 | hours | invalid_hours | T04 | hours 'abc' không phải số hữu hạn không âm. |
| 6 | task_id | duplicate_id | T02 | task_id T02 đã xuất hiện ở line 3. |
| 7 | owner | missing_owner | T05 | owner trống. |

## Đánh giá
- Tổng chỉ dùng dòng hợp lệ và lần đầu mỗi ID; lần đầu có lỗi vẫn giữ chỗ ID, không dùng lần hợp lệ sau. Bỏ khoảng trắng; phân biệt tên owner và hoa/thường.
- Dữ liệu có lỗi vẫn được phân tích; tổng không gồm dòng bị loại. Lan có đúng 9 giờ (bằng ngưỡng, không quá tải).

## Khuyến nghị
- Sửa giá trị hours cho dòng T04 (line 5) từ "abc" thành một số hữu hạn không hợp lệ hợp lệ.
- Kiểm tra lại việc trùng task_id T02 ở dòng 6 và điều chỉnh để tránh lặp.
- Điền thông tin owner cho dòng T05 (line 7) để đảm bảo dữ liệu hoàn chỉnh.
