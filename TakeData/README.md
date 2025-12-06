# Trình thu thập bình luận YouTube (OAuth) và web dán nhãn

Dự án cung cấp:

- Script Python để lấy bình luận YouTube (bao gồm cả trả lời) cho nhiều video liệt kê trong `videos_id.txt`, và lưu ra CSV với hai cột: `comments` và `sentiment` (mặc định sentiment = 0 cho mọi bình luận).
- Web Flask đơn giản để đọc CSV và gán nhãn 0/1/2 (tùy chọn, nếu bạn dùng workflow qua web).

Lưu ý: Ngôn ngữ chính của repo là Python.

## 1) Tính năng

- Đọc nhiều video ID trên YouTube từ `videos_id.txt` (mỗi dòng tương ứng với 1 video ).
- Xác thực OAuth 2.0 cho YouTube Data API v3, video hướng dẫn cách cấu hình nếu ai cần có thể liên hệ tinhvu2k4.edu@gmail.com
- chương trình này được xây dựng để phục vụ việc lấy dữ liệu comment để xây dựng mô hình phân loại cảm xúc của các bình luận nên sẽ lấy ra tất cả bình luận bao gồm các bình luận và các replies của bình luận đó

## 2) Chuẩn bị môi trường

- Python 3.8+ (khuyến nghị 3.12)
- Tạo môi trường ảo (khuyến nghị):

Windows (PowerShell):

```
py -3.12 -m venv .venv
.\.venv\Scripts\Activate
python -m pip install --upgrade pip
```

macOS/Linux:

```
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
```

- Cài thư viện cần thiết (`pip install -r requirements.txt`):

```

## 3) Cấu hình OAuth trên Google Cloud

1. Vào [Google Cloud Console](https://console.cloud.google.com/) (chọn hoặc tạo Project).
2. Bật API:
   - APIs & Services → Library → tìm “YouTube Data API v3” → Enable.
3. Cấu hình OAuth consent screen:
   - User type: External
   - Điền App name, User support email, Developer contact info
   - Add scopes:
     - `https://www.googleapis.com/auth/youtube.readonly`
     - `https://www.googleapis.com/auth/youtube.force-ssl`
   - Test users: thêm email bạn sẽ dùng để đăng nhập (ví dụ: `youremail@gmail.com`)
   - Save (không cần Publish).
4. Tạo OAuth Client ID:
   - APIs & Services → Credentials → Create Credentials → OAuth Client ID
   - Application type: Desktop app
   - Tải file JSON (ví dụ: `client_secret.json`) và đặt cạnh script

Lưu ý:

- Nếu thay đổi scopes, hãy xóa `token.json` rồi cấp quyền lại.
- Email đăng nhập phải nằm trong danh sách Test users khi app đang ở trạng thái Testing.

```

## 4) Chuẩn bị dữ liệu đầu vào

Tạo file `videos_id.txt` trong thư mục dự án. Mỗi dòng là một video ID hoặc URL YouTube hợp lệ. Ví dụ:

```

một link youtube có dạng: https://www.youtube.com/watch?v=nOj0ptinh (link này không tồn tại thật mà chỉ đang ví dụ)

sẽ có video id là nOj0ptinh

```

Dòng rỗng sẽ bị bỏ qua. Dòng không hợp lệ sẽ được thông báo và bỏ qua.

## 5) Chạy script thu thập bình luận

Ví dụ lệnh:

```

python fetch_youtube_texts_oauth.py --secrets client_secret.json --output_csv comments_text.csv --max_pages 30

```

Tham số:

- `--secrets`: đường dẫn tới file OAuth client (JSON).
- `--output_csv`: đường dẫn file CSV đầu ra, mặc định `comments_text.csv`.
- `--max_pages`: số trang tối đa mỗi video (mỗi trang tối đa 100 bình luận gốc).
- `--order`: `time` (mặc định) hoặc `relevance`.
- `--html`: nếu thêm cờ này, nội dung bình luận sẽ là HTML (`textDisplay` với HTML) thay vì plain text.

Lần đầu chạy:

- Trình duyệt sẽ mở trang cấp quyền OAuth → đăng nhập bằng email đã ở Test users → chấp nhận scopes.
- Token sẽ được lưu tại `token.json` để dùng lại.

Kết quả CSV:

```

comments,sentiment
Bình luận 1,0
Bình luận 2,0
...

```

Mỗi bình luận và trả lời là một dòng riêng biệt, `sentiment` luôn là `0` mặc định.

Ghi chú:

- Script ghi nối tiếp (append) vào CSV; nếu chạy lại cùng video, có thể sinh trùng lặp.

## 6) Tránh trùng lặp (tuỳ chọn)

Có thể loại trùng lặp sau khi crawl bằng pandas:

```

import pandas as pd
df = pd.read_csv("comments_text.csv")
df = df.drop_duplicates(subset=["comments"])
df.to_csv("comments_text_dedup.csv", index=False)

```

Nếu cần, có thể tích hợp loại trùng lặp vào script theo yêu cầu.

## 7) Web dán nhãn (tuỳ chọn)

Dự án có kèm web Flask đơn giản (`app.py`) để:

- Đọc `comments_text.csv`
- Hiển thị bình luận theo trang
- Chọn trạng thái 0/1/2 tương ứng với 3 sắc thái cảm xúc (tiêu cực, trung lập, tích cực) cho từng dòng và lưu lại

Chạy web:

```

python app.py

```

Mở trình duyệt:

```

http://127.0.0.1:5000

```

Yêu cầu:

- File CSV có tồn tại (web sẽ tạo nếu chưa có, và chuẩn hoá cột).

## 8) Các lỗi thường gặp và cách khắc phục

- 403 `access_denied`: Email chưa nằm trong Test users hoặc dùng sai Project. Thêm email vào Test users, kiểm tra lại Project/Client ID.
- 403 `insufficientPermissions`: Chưa thêm scope `youtube.force-ssl` hoặc chưa xóa `token.json` sau khi thay đổi scopes. Thêm scope → xóa `token.json` → chạy lại.
- `videos_id.txt not found`: File chưa tạo hoặc sai tên. Đảm bảo đúng `videos_id.txt`.
- Trùng lặp bình luận: Script append dữ liệu; hãy xử lý trùng lặp hậu kỳ như mục 6.

## 9) Quota và giới hạn

- Mặc định quota YouTube Data API v3: khoảng 10,000 đơn vị/ngày (có thể khác tùy Project).
- `commentThreads.list`: ~1 đơn vị mỗi lần gọi, tối đa 100 bình luận gốc/trang. Phân trang bằng `nextPageToken`.
- Nếu gọi quá nhanh, có thể gặp giới hạn tốc độ; thêm `sleep` nhỏ giữa các lần gọi nếu cần.

## 10) Cập nhật/tuỳ biến

Bạn có thể yêu cầu:

- Thêm cột `video_id` vào CSV để biết bình luận thuộc video nào.
- Lấy đầy đủ replies bằng `comments.list` với `parentId` (để vượt hạn chế của `replies` trong `commentThreads`).
- Tự động loại trùng lặp trước khi ghi.
- Bộ lọc theo từ khóa hoặc độ dài bình luận.
