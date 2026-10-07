# Phân tích Block 2

## Thay đổi đã làm

Tạo bản sao stage 03 và stage 04 trong `submission/block-2/`. Đã đối chiếu bytes:
`agent.py`, tools, prompts, config và paths của cả hai bản sao giữ nguyên so với
mẫu. Không thêm tool. Chỉ sửa skill csv-quality, reference, script trong stage 04;
thêm dữ liệu, cập nhật tests CLI và tạo runner kiểm chứng ngoài stage.

`workspace/skills/csv-quality/` và `fixtures/skills/csv-quality/` đồng bộ cả ba
file `SKILL.md`, `scripts/check_csv.py`, `references/report-template.md`. CSV đề
bài nằm ở workspace và fixtures của cả hai stage; edge CSV ở stage 04. Reset
bản sao stage 04 sẽ giữ skill và dữ liệu bài tập. Stage mẫu không bị sửa.

## Thuật toán

Script tái sử dụng CSV reader UTF-8/BOM, `parse_hours`, `first_seen`, các kiểm tra
chất lượng và `InputError` hiện có. Thêm CLI `--max-hours` bắt buộc, dùng cùng
quy tắc số hữu hạn không âm. Không có ngưỡng mặc định hoặc kết quả cố định trong
script/skill. Ngưỡng trong test/harness là dữ liệu kiểm tra theo đề.

Mỗi dòng vẫn được kiểm tra đầy đủ, kể cả trùng ID hoặc sai số trường. Ghi nhận
ID không rỗng vào `first_seen` ngay lần xuất hiện đầu tiên, trước khi quyết định
có cộng giờ. Do vậy lần đầu có hours lỗi, owner thiếu hoặc số trường sai vẫn
chiếm ID; các lần sau bị loại. Không đổi thành "lần hợp lệ đầu tiên".

Lưu vị trí đầu của `issues` trước khi kiểm tra một dòng; sau kiểm tra, lấy mã lỗi
của riêng dòng đó làm `reasons`. Các kiểm tra vốn chạy theo đúng thứ tự mã lý do
trong đề. Nếu có lý do, thêm một entry `excluded_rows` với mọi lý do. Nếu không,
cộng parsed_hours vào owner đã strip. Các thống kê chất lượng cũ tiếp tục xét
toàn bộ dòng dữ liệu. Dòng trống vẫn được bỏ qua như script mẫu.

Owner khác tên hoặc khác hoa/thường được giữ riêng. Hours 0 được cộng và owner
có dòng hợp lệ 0 vẫn xuất hiện trong tổng. Overloaded dùng so sánh `total > max_hours`,
không dùng `>=`. Danh sách người quá tải theo tên; dòng bị loại theo line.

## Kiểm thử và JSON trực tiếp

Đã viết tests mới trước khi sửa script. Lần đầu: **7 failed, 6 passed**; các ca
thành công thất bại vì CLI chưa nhận `--max-hours`, ca thiếu ngưỡng thất bại vì
CLI cũ vẫn cho chạy. Bằng chứng: `tests-red.xml`.

Sau sửa và đồng bộ fixtures: **25 passed**, gồm các tests chất lượng cũ và tests
mới. Bằng chứng: `tests-green.xml`; chạy lại từ root lab bằng:

```powershell
.\.venv\Scripts\python.exe -X utf8 submission/block-2/verify_local.py
```

Harness chỉ thay fixture đường dẫn tạm để tránh ACL mode 0o700 của Python 3.13
trong sandbox Windows; không thay thuật toán hoặc hàm đọc CSV. Tên thư mục tạm
có UUID để tránh va chạm giữa tham số `NaN` và `nan` trên Windows.

| Ca trực tiếp | Kết quả đã quan sát | Bằng chứng |
|---|---|---|
| Workload, ngưỡng 8 | Lan 9, Minh 3; chỉ Lan quá tải; loại dòng 5 invalid_hours, 6 duplicate_id, 7 missing_owner | `script-results/threshold-8.json` |
| Workload, ngưỡng 9 | Tổng và dòng bị loại giữ nguyên; không ai quá tải | `script-results/threshold-9.json` |
| Edge, ngưỡng 0 | Chỉ Minh có tổng 0; không ai quá tải; loại dòng 2 invalid_hours và dòng 3 duplicate_id; không cộng giờ cho Lan | `script-results/edge-0.json` |
| File không tồn tại | exit 1, stdout rỗng, stderr báo không đọc được file | `script-results/not-found.stderr.txt` |
| Thiếu --max-hours | exit 2, stdout rỗng, stderr báo thiếu tham số | `script-results/missing-threshold.stderr.txt` |
| Ngưỡng NaN | exit 2, stdout rỗng, stderr báo ngưỡng không hợp lệ | `script-results/invalid-threshold.stderr.txt` |

`script-results/runs.json` ghi lệnh CLI, exit code và SHA-256 đầu vào. Đã xác nhận
CSV không bị sửa. Script trả 0 khi phân tích được, kể cả có lỗi dữ liệu/quá tải.
Tests còn bao phủ trim, tên owner khác hoa/thường, dòng trống, tổng bằng ngưỡng,
nhiều lý do trên cùng dòng, missing ID, sai số trường, ID đầu tiên sai số trường,
hours không hữu hạn/âm/rỗng, ngưỡng không hợp lệ, thiếu cột và lỗi parse.

`quick_validate.py` xác nhận skill hợp lệ. Skill lấy ngưỡng từ yêu cầu hiện tại;
thiếu ngưỡng thì chỉ hỏi bổ sung và dừng. Không tái sử dụng ngưỡng cũ. Reference
ghi đủ ngưỡng, tổng từng người, người quá tải, dòng bị loại và thống kê chất lượng.

## Trace và báo cáo agent: đã đối chiếu

Người dùng đã cài môi trường Linux riêng `.venv-wsl` và chạy runner trong Ubuntu
WSL ngày 07/10/2026. Có đủ 5 trace thật và hai báo cáo do agent tạo. Phiên agent
vẫn không được truy cập WSL, nhưng có thể đọc các artifact chung trên ổ D để
đối chiếu. Không sửa tool Bash hoặc giả lập trace. Runner dùng `.env` chung của
Block 1, không sao chép credential vào evidence.

`trace-index.json` ghi đường dẫn, sequence, schema và báo cáo. Đã xác nhận 5
conversation ID khác nhau; snapshot đầu chỉ có câu hỏi mới. Schema vẫn gồm
read_file, write_file, bash, không thêm tool. Mọi `input-integrity.json` có
`unchanged: true`, fingerprint trước/sau bằng nhau. CSV không bị sửa.

| Ca | Kết quả thực tế | Đánh giá |
|---|---|---|
| Stage 03 baseline | Python qua Bash tính Lan 9, Minh 3; bỏ T04 hours lỗi, T02 lặp và T05 owner trống | Đúng CSV đã cho; thuật toán tự viết còn hạn chế được phân tích dưới đây |
| Stage 04 ngưỡng 8 | Nạp skill/reference, truyền --max-hours 8; Lan 9, Minh 3, chỉ Lan quá tải; ghi báo cáo đủ dòng bị loại | Đạt |
| Stage 04 ngưỡng 9 | Truyền --max-hours 9; tổng/dòng bị loại giữ nguyên; không ai quá tải; ghi rõ Lan bằng ngưỡng | Đạt |
| Stage 04 thiếu ngưỡng | Chỉ đọc skill rồi hỏi ngưỡng; không Bash, không write_file, không kết luận quá tải | Đạt |
| Stage 04 file thiếu | Bash exit 1, stdout rỗng, stderr báo không đọc được file; agent hỏi xác nhận đường dẫn, không đưa tổng/ghi báo cáo | Đạt |

JSON stdout trong hai ca 8/9 bằng toàn bộ JSON chạy trực tiếp, trừ trường `input`
khác tiền tố đường dẫn do cwd. Báo cáo có ngưỡng, tổng từng người, danh sách quá
tải, các dòng 5/6/7 cùng lý do và thống kê chất lượng 6 dòng, 1 thiếu owner,
1 hours lỗi, 1 ID trùng. Đã đọc báo cáo thực tế, không chỉ xem exit code 0.

Báo cáo ngưỡng 9 có một lỗi diễn đạt nhỏ trong khuyến nghị sửa hours (cụm
"không hợp lệ hợp lệ"); số liệu, điều kiện quá tải và lý do loại đúng. Giữ nguyên
artifact agent tạo để trung thực với trace, không sửa báo cáo bằng tay.

### Vị trí bằng chứng

Đường dẫn dưới đây tương đối `submission/block-2/`. Mỗi trace một sự kiện mỗi
dòng; `seq` là sequence và cũng là số dòng.

| Ca | Trace | Sequence cần xem |
|---|---|---|
| Baseline | `evidence/stage-03-bash_baseline_a2df02fc/20261007-130705_4480c27c_turn01_a2df02fc.jsonl` | 8 lệnh Python; 9 stdout tổng và lý do loại; 12 đáp án |
| Ngưỡng 8 | `evidence/stage-04-script-skill_8_cfc8fe7d/20261007-130751_c44d6c1f_turn01_cfc8fe7d.jsonl` | 5 đọc skill; 11 reference; 12 context chứa cả hai; 14 lệnh đúng ngưỡng; 15 JSON; 18 nội dung báo cáo; 19 ghi thành công; 22 đáp án |
| Ngưỡng 9 | `evidence/stage-04-script-skill_9_0a9e0ba0/20261007-130827_8f2a85e6_turn01_0a9e0ba0.jsonl` | 5 skill; 9 reference; 10 context; 12 lệnh; 13 JSON; 16 báo cáo; 17 ghi thành công; 20 đáp án |
| Thiếu ngưỡng | `evidence/stage-04-script-skill_missing_ff91b8a7/20261007-130859_e2339429_turn01_ff91b8a7.jsonl` | 5 đọc skill; 6 context; 8 chỉ hỏi ngưỡng |
| File thiếu | `evidence/stage-04-script-skill_not-found_31fc48a9/20261007-130919_4b48274b_turn01_31fc48a9.jsonl` | 5 skill; 8 lệnh script; 9 exit 1/stderr; 12 báo không có file |

Hai báo cáo agent tạo:

- `evidence/stage-04-script-skill_8_cfc8fe7d/workspace/output/workload.md`
- `evidence/stage-04-script-skill_9_0a9e0ba0/workspace/output/workload.md`

Ca thiếu ngưỡng/file thiếu không có báo cáo thành công. Mỗi ca giữ workspace,
answer.md và context.json để đối chiếu.

### Phân tích lệnh tự viết ở Stage 03

Dòng 2 (T01, Lan, 4), dòng 3 (T02, Lan, 5) và dòng 4 (T03, Minh, 3) được cộng.
Dòng 5 T04 bị loại vì hours abc; dòng 6 T02 bị loại vì ID đã gặp; dòng 7 T05 bị
loại vì owner rỗng. Đoạn chống cộng trùng nằm trong command tại seq 8:

```python
if tid in seen_ids:
    duplicates_found.append(tid)
    continue
seen_ids.add(tid)
```

Tuy nhiên lệnh này parse `int(h_raw)` trước khi ghi nhận ID; nếu hours lỗi thì
`continue` ngay, chưa giữ chỗ ID. Với edge CSV, E01 lần đầu abc sẽ không được
ghi nhận, lần sau 5 có thể bị cộng. Lệnh còn không nhận hours thập phân và chưa
kiểm tra đầy đủ số hữu hạn, âm, missing ID hoặc số trường. Đáp án baseline nói
"chỉ giữ bản ghi đầu tiên" rộng hơn điều mà code thực sự bảo đảm.

Đây là giới hạn của Python do model tự viết trong lần baseline, không phải lỗi
script csv-quality đã sửa. Script stage 04 giữ chỗ ID trước khi quyết định cộng
và đã qua test edge: chỉ Minh 0, Lan không được cộng 5 giờ. JSON trực tiếp và
tests tự động cung cấp bằng chứng cho quy tắc đó.

## Trả lời câu hỏi cuối bài

Script chịu trách nhiệm đọc/kiểm tra CSV, chuẩn hóa giá trị, ghi nhận lần đầu của
ID, chọn dòng được cộng, tính tổng giờ, so ngưỡng, sắp xếp và xuất JSON/lỗi CLI.
Model chọn skill theo yêu cầu, hỏi ngưỡng còn thiếu, gọi Bash đúng tham số, diễn
giải JSON và dùng write_file tạo báo cáo. Model không thay thuật toán bằng việc
tự cộng hoặc tự chọn lại dòng.

Nếu chỉ sửa script, skill cũ có thể gọi thiếu `--max-hours`, tự dùng ngưỡng sai
hoặc vẫn từ chối tính tổng khi CSV có lỗi. Reference cũ không yêu cầu tổng theo
người, ngưỡng thực tế, người quá tải và dòng bị loại; báo cáo dễ thiếu các trường
này hoặc nhầm thống kê chất lượng với tập dòng được cộng. Cần đồng bộ cả script,
skill và reference để quyết định, lệnh gọi và báo cáo thống nhất.
