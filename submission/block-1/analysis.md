# Phân tích Block 1

## Phạm vi đã làm

Làm trên bản sao stage 00/01/02 trong thư mục này; giữ nguyên các stage mẫu ở
root. Không sao chép `.env`, API key hoặc trace cũ vào bài nộp.

Theo yêu cầu bổ sung, cấu hình OpenRouter dùng một `.env` chung ở thư mục này;
`ENV_PATH` của cả ba stage bản sao trỏ đến file chung. Chỉ thay đường dẫn cấu hình,
không thay prompt hoặc logic agent. File thật bị `.gitignore` loại khỏi version
control và không được đưa vào bài nộp. Người dùng đã điền key, model và endpoint;
kiểm tra chỉ ghi trạng thái có/không, không hiển thị các giá trị bí mật.

- Stage 01/02: thêm `_list` và tool `list_files` trong `tools/files.py`;
  export ở `tools/__init__.py`, đăng ký vào `agent.TOOLS`.
- Hai tài liệu chính sách nằm ở `workspace/data/policies/` của cả hai stage.
- Stage 02: thêm `workspace/skills/refund-policy/SKILL.md` và
  `references/answer-template.md`. Catalog hiện có tự phát hiện skill.
- Giữ nguyên system prompt. Tool không chứa tên tài liệu chính sách, điều khoản,
  cách tính hoàn tiền hoặc đáp án. Các câu hỏi trong `run_cases.py` chỉ là đầu vào
  kiểm thử; script này ở ngoài stage và không đăng ký làm tool cho agent.

## Tool và kiểm thử cục bộ

`list_files(path: str)` trả JSON `ok`, `path`, `entries`. Mỗi entry gồm `name`,
`path` tương đối workspace, `type` là `file` hoặc `directory`; sắp xếp theo tên,
không liệt kê đệ quy. `.` dùng để liệt kê gốc workspace.

Tool tái sử dụng `_resolve` và `_error`; resolve đường dẫn rồi kiểm tra giới hạn
workspace trước khi truy cập. Các mục con cũng được resolve trước khi kiểm tra
loại, vì một symlink trong thư mục hợp lệ có thể dẫn ra ngoài. Khi gặp mục như
vậy, toàn bộ lần liệt kê trả lỗi, không trả kết quả một phần như danh sách hợp lệ.

| Kiểm tra | Kết quả đã quan sát |
|---|---|
| Thư mục có file và thư mục con | Có tên/đường dẫn/loại; sắp xếp; không trả file cháu |
| Thư mục rỗng | `ok: true`, `entries: []` |
| Đường dẫn là file | `NOT_A_DIRECTORY` |
| Đường dẫn không tồn tại | `DIRECTORY_NOT_FOUND` |
| `../outside` và `data/../../outside` | `PATH_OUTSIDE_WORKSPACE` |
| Đường dẫn tuyệt đối | `PATH_OUTSIDE_WORKSPACE` |
| Đường dẫn rỗng | `INVALID_PATH` |
| Tool `.invoke` và argument schema | JSON hợp lệ; tham số `path` bắt buộc, kiểu string |
| Symlink thư mục và symlink mục con vượt workspace | Đạt trên Ubuntu WSL: trả PATH_OUTSIDE_WORKSPACE |
| Read/write qua symlink vượt phạm vi | Đạt trên Ubuntu WSL: từ chối truy cập, không đọc/ghi dữ liệu ngoài phạm vi |
| Đổi tên hai tài liệu rồi list/read trong workspace mới | Tìm được tên mới; nội dung bằng nội dung trước đổi tên |
| Catalog và reference của refund-policy | Metadata hợp lệ, đọc được skill/reference bằng tool |

Bằng chứng: `local-verification.txt`, `stage-01-files/tests/test_list_files.py`,
`stage-02-skills/tests/test_list_files.py` và `tests/test_refund_resources.py`.

Lần kiểm tra trước trên Windows, chạy `python -X utf8 submission/block-1/verify_local.py` từ root lab:

- Stage 01: **25 passed, 2 skipped, 2 deselected**.
- Stage 02: **27 passed, 2 skipped, 2 deselected**.
- Hai ca skipped mỗi stage là tests mới cần symlink. Hai ca deselected là tests
  mẫu cũng cần quyền tạo symlink. Kết quả Windows này được giữ làm lịch sử;
  kiểm chứng đầy đủ trên Ubuntu WSL bên dưới đã khắc phục phần còn thiếu.
- `quick_validate.py` trả **Skill is valid!**.

Đã bổ sung chế độ `verify_local.py --require-symlinks` cho Ubuntu/WSL. Khi dùng
Python Linux, runner không loại tests symlink, tạo fixture ở thư mục tạm Linux
và thất bại nếu bất kỳ test nào bị skip. Có 4 tests symlink mỗi stage: symlink
thư mục vượt workspace, symlink mục con khi list, read qua symlink vượt workspace,
write qua symlink vượt output. Runner lưu log POSIX và JUnit XML riêng, giữ lại
log Windows để đối chiếu. Người dùng đã chạy lệnh sau trong Ubuntu:

```bash
.venv-wsl/bin/python -X utf8 submission/block-1/verify_local.py --require-symlinks
```

Đã đọc log và XML thực tế, xác nhận:

- Stage 01: **29 passed**, 0 failures, 0 errors, 0 skipped.
- Stage 02: **31 passed**, 0 failures, 0 errors, 0 skipped.
- Cả 4 tests symlink ở mỗi stage có mặt trong XML và thực sự được thực thi:
  `test_symlink_directory_escape_is_rejected`,
  `test_listing_rejects_child_symlink_outside_workspace`,
  `test_read_symlink_escape_blocked`,
  `test_write_absolute_and_symlink_escape_rejected`.
- Bằng chứng: `posix-verification.txt`, `posix-tests-stage-01-files.xml`,
  `posix-tests-stage-02-skills.xml`. Không còn ca symlink chờ kiểm chứng.

Windows Python 3.13 tạo ACL không đọc được trong sandbox khi pytest gọi
`mkdir(mode=0o700)`. Đã tái hiện bằng cách tạo hai thư mục: mặc định đọc được,
mode 0o700 báo `PermissionError`. `verify_local.py` thay riêng fixture `tmp_path`
bằng thư mục test có quyền kế thừa bình thường; không thay `_resolve`, tool hoặc
cơ chế symlink. Dữ liệu tạm đều là dữ liệu giả dưới `.verification-temp/` ở root.

## Kết quả từ trace model thật

Người dùng đã chạy runner trong terminal máy ngày 07/10/2026 và tạo 10 trace
thành công, rồi chạy lại ca thiếu thông tin với skill đã điều chỉnh và tạo thêm
một trace đạt yêu cầu. Đã đọc toàn bộ câu trả lời và sự kiện tìm/đọc tài liệu, không suy ra
đáp án đúng chỉ từ exit code. `trace-index.json` lưu đường dẫn trace, sequence
sự kiện và schema. Các conversation có ID khác nhau, chat_turn 1; snapshot đầu
chỉ có câu hỏi người dùng, không có tool result hoặc tài liệu từ lịch sử cũ.
Schema stage 01/02 chứa `read_file`, `write_file`, `list_files`; stage 00 không có tool.

| Tình huống | Kết quả thực tế | Đánh giá |
|---|---|---|
| Stage 00 — A | Nêu không có công cụ/cơ sở dữ liệu, tính 8 ngày; không đọc tài liệu. Có thêm nhận định chung về chính sách phổ biến, chưa được tài liệu chứng minh | Xác định được giới hạn và rủi ro đoán từ kiến thức sẵn có |
| Stage 01 — A gốc | Chọn cũ, quá hạn 1 ngày, từ chối | Đúng kết luận; chưa nêu trực tiếp 8 ngày và thiếu đường dẫn căn cứ |
| Stage 01 — B gốc | Chọn mới, 10 ngày, đủ điều kiện | Đúng kết luận; thiếu phí và đường dẫn căn cứ |
| Stage 01 — A đổi tên | Đọc file mới, chọn cũ, từ chối và dẫn đúng đường dẫn | Đổi tên không đổi kết luận; chưa nêu trực tiếp 8 ngày |
| Stage 01 — B đổi tên | Đọc file mới, chọn mới, đủ điều kiện, không phí | Đổi tên không đổi kết luận; thiếu số ngày đã qua và đường dẫn căn cứ trong câu trả lời |
| Stage 02 — A gốc/đổi tên | Chọn cũ, 8 ngày, không đủ điều kiện, dẫn đúng file đã đọc | Đạt; skill và reference đã vào context |
| Stage 02 — B gốc/đổi tên | Chọn mới, 10 ngày, đủ điều kiện, không phí, dẫn đúng file đã đọc | Đạt; skill và reference đã vào context |
| Stage 02 — thiếu kích hoạt, lần đầu | Hỏi trạng thái kích hoạt, không tự giả định. Tuy nhiên tiếp tục phân tích sơ bộ, đưa nhánh điều kiện và phí | Đã phát hiện và chỉnh skill |
| Stage 02 — thiếu kích hoạt, chạy lại | Chỉ hỏi trạng thái kích hoạt; chưa kết luận, chưa nêu phí, chưa tra cứu chính sách | Đạt |

Stage 01 chứng minh tool giúp khám phá tài liệu nhưng chưa bảo đảm định dạng và
độ đầy đủ của câu trả lời. Stage 02 với skill cho câu trả lời A/B đầy đủ hơn.
Các file chính sách đổi tên có nội dung giữ nguyên trong workspace bằng chứng.

## Vị trí bằng chứng trong trace

Các đường dẫn bên dưới tương đối thư mục `submission/block-1/`. `seq` là
`sequence` của sự kiện; mỗi trace này ghi một sự kiện mỗi dòng nên cũng là số dòng.

| Ca | Trace | Bằng chứng |
|---|---|---|
| 00 A | `evidence/stage-00-chat_A_original_35bd1917/20261007-123455_85e80244_turn01_35bd1917.jsonl` | seq 2 schema không có tools; seq 4 câu trả lời nêu giới hạn |
| 01 A gốc | `evidence/stage-01-files_A_original_ab3101bf/20261007-123514_dba7db2d_turn01_ab3101bf.jsonl` | seq 13 list policies; seq 19 đọc cũ; seq 22 trả lời |
| 01 B gốc | `evidence/stage-01-files_B_original_8870dba2/20261007-123541_d724f920_turn01_8870dba2.jsonl` | seq 13 list policies; seq 17 đọc mới; seq 20 trả lời |
| 01 A đổi tên | `evidence/stage-01-files_A_renamed_a2d301d4/20261007-123604_babb0338_turn01_a2d301d4.jsonl` | seq 14 tìm tên mới; seq 21 đọc document-1; seq 24 trả lời |
| 01 B đổi tên | `evidence/stage-01-files_B_renamed_9bf6a11f/20261007-123637_1a3ef021_turn01_9bf6a11f.jsonl` | seq 15 tìm tên mới; seq 21 đọc document-2; seq 24 trả lời |
| 02 A gốc | `evidence/stage-02-skills_A_original_743b85b1/20261007-123701_fa99ae28_turn01_743b85b1.jsonl` | seq 5 skill; 9 list; 15 đọc cũ; 19 reference; 20 context có skill/reference; 22 đáp án |
| 02 B gốc | `evidence/stage-02-skills_B_original_8fee5294/20261007-123728_fc8c65e8_turn01_8fee5294.jsonl` | seq 5 skill; 10 list; 11 reference; 17 đọc mới; 18 context; 20 đáp án |
| 02 A đổi tên | `evidence/stage-02-skills_A_renamed_c5a5a4e6/20261007-123748_2e2e4807_turn01_c5a5a4e6.jsonl` | seq 5 skill; 10 list tên mới; 11 reference; 16 đọc document-1; 18 context; 20 đáp án |
| 02 B đổi tên | `evidence/stage-02-skills_B_renamed_8219b2f1/20261007-123812_fcaeadba_turn01_8219b2f1.jsonl` | seq 5 skill; 9 list tên mới; 14 đọc document-2; 19 reference; 20 context; 22 đáp án |
| 02 thiếu kích hoạt | `evidence/stage-02-skills_missing_original_e98ce63e/20261007-123826_22ab5f1a_turn01_e98ce63e.jsonl` | seq 5 skill; 19 reference; 22 hỏi lại nhưng thêm phân tích có điều kiện |
| 02 thiếu kích hoạt sau chỉnh skill | `evidence/stage-02-skills_missing_original_63957595/20261007-124728_62e7052f_turn01_63957595.jsonl` | seq 2 context mới chỉ có user; 5 đọc skill; 6 context chứa skill mới; 8 chỉ hỏi trạng thái kích hoạt |

Mỗi lần chạy thành công còn có `answer.md`, `context.json` và workspace chứa
tài liệu/skill đúng phiên bản đã dùng trong lần đó. Các user message chỉ chứa
câu hỏi trong đề, không nhắc tên file, tên skill hay thứ tự tool.

## Điều chỉnh sau kiểm tra và xác nhận lại

Đã sửa riêng skill stage 02: khi thiếu bất kỳ thông tin bắt buộc nào, chỉ hỏi
bổ sung rồi kết thúc lượt; chưa tìm/đọc chính sách, chưa phân tích sơ bộ, chưa
đưa nhánh điều kiện hoặc phí. Không sửa prompt hay tool để nhúng đáp án.
Trace A/B ở trên lưu workspace của skill trước điều chỉnh; chúng vẫn chứng minh
các ca A/B đó đạt. Ca thiếu thông tin của skill mới đã được chạy lại độc lập.

Đã thử chạy lại ca thiếu trong phiên agent. Dependency `.venv` hiện đã đủ để
khởi tạo agent nhưng kết nối vẫn lỗi `OpenAIConnectionError`; trace thất bại:
`evidence/stage-02-skills_missing_original_0d04b0fd/20261007-124353_1fdc72ad_turn01_0d04b0fd.jsonl`.
Đây không phải bằng chứng skill mới đã đạt. Không có câu trả lời model trong lần này.

Người dùng đã chạy lại thành công trong terminal máy. Trace mới
`evidence/stage-02-skills_missing_original_63957595/20261007-124728_62e7052f_turn01_63957595.jsonl`
chỉ có một tool call đọc `skills/refund-policy/SKILL.md` (seq 5), sau đó hỏi
trạng thái kích hoạt (seq 8). Không gọi `list_files`, không đọc chính sách,
không đưa kết luận có điều kiện hoặc mức phí. Nội dung `answer.md` khớp đáp án
trong trace. Snapshot seq 6 đã chứa nội dung skill mới. **Ca này đạt yêu cầu.**

Các ca chính của stage 02 đã có bằng chứng đạt: A/B trước và sau đổi tên, và
thiếu thông tin sau điều chỉnh. Stage 01 có tool hoạt động đúng và kết luận đúng,
nhưng hạn chế định dạng câu trả lời đã ghi trong bảng. Tests symlink đã đạt
trên Ubuntu WSL, không còn bị bỏ qua. Cấu hình `.env` không được đưa vào bài nộp.
`environment-check.json` phân biệt việc chạy thành công ở terminal người dùng
và việc kết nối bị chặn trong phiên agent.

## Trả lời câu hỏi cuối bài

Tool cung cấp khả năng thao tác dữ liệu: `list_files` khám phá tài liệu đang tồn
tại, rồi `read_file` lấy nội dung làm căn cứ. Skill cung cấp quy trình chuyên
biệt: kiểm tra thông tin còn thiếu, chọn hiệu lực theo ngày mua, tính chênh lệch
ngày lịch, áp dụng điều kiện kích hoạt và trả lời có căn cứ.

Nếu chưa có tool tìm file, sửa prompt không tạo ra khả năng liệt kê thư mục.
Agent có thể thử đoán tên để gọi `read_file`, nhưng không bảo đảm tìm được khi
tên thay đổi. Viết cố định tên file hoặc chính sách vào prompt vừa vi phạm đề,
vừa không giải quyết việc phát hiện tài liệu hiện tại. Tool và skill bổ sung
hai phần cần thiết: khả năng truy cập và hướng dẫn sử dụng khả năng đó.
