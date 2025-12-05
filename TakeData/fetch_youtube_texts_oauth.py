import argparse
import csv
import os
import sys
from datetime import datetime
from typing import List, Optional
from urllib.parse import urlparse, parse_qs

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Scopes: cần cả youtube.force-ssl để tránh lỗi insufficient scopes với commentThreads.list
SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]


def get_oauth_client(secrets_path: str, token_path: str = "token.json"):
    """
    Khởi tạo client YouTube Data API v3 với OAuth 2.0.
    """
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(secrets_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def extract_video_id(s: str) -> Optional[str]:
    """
    Nhận vào một video_id hoặc URL YouTube và trích ra video id.
    Hỗ trợ:
      - https://www.youtube.com/watch?v=VIDEO_ID
      - https://youtu.be/VIDEO_ID
      - https://www.youtube.com/embed/VIDEO_ID
      - https://www.youtube.com/shorts/VIDEO_ID
      - nếu chỉ là VIDEO_ID (không có URL), trả lại trực tiếp
    """
    s = s.strip()
    if not s:
        return None
    # ID thuần
    if "://" not in s and "/" not in s and "?" not in s and "&" not in s:
        return s

    try:
        u = urlparse(s)
        # youtu.be/<id>
        if u.netloc in {"youtu.be"} and u.path:
            return u.path.lstrip("/")

        # youtube.com dạng khác
        if u.netloc in {"www.youtube.com", "youtube.com", "m.youtube.com"}:
            if u.path == "/watch":
                qs = parse_qs(u.query)
                vid = qs.get("v", [None])[0]
                if vid:
                    return vid
            if u.path.startswith("/embed/"):
                parts = u.path.split("/")
                return parts[2] if len(parts) >= 3 else None
            if u.path.startswith("/shorts/"):
                parts = u.path.split("/")
                return parts[2] if len(parts) >= 3 else None
    except Exception:
        pass
    return None


def read_video_ids_from_file(path: str = "videos_id.txt") -> List[str]:
    """
    Đọc file videos_id.txt (mỗi dòng là URL YouTube hoặc video_id) và trả về danh sách video_id hợp lệ.
    """
    ids: List[str] = []
    if not os.path.exists(path):
        print(f"videos_id.txt not found at: {os.path.abspath(path)}", file=sys.stderr)
        return ids
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            vid = extract_video_id(line)
            if vid:
                ids.append(vid)
            else:
                bad = line.strip()
                if bad:
                    print(f"Skip invalid line: {bad}", file=sys.stderr)
    return ids


def fetch_all_texts(
    youtube,
    video_id: str,
    max_pages: int = 50,
    order: str = "time",
    text_format: str = "plainText",
) -> List[str]:
    """
    Lấy toàn bộ nội dung text của bình luận GỐC (top-level) cho một video.
    KHÔNG lấy replies.
    Trả về List[str] chỉ gồm text.
    """
    texts: List[str] = []
    pages = 0
    page_token: Optional[str] = None

    while True:
        try:
            request = youtube.commentThreads().list(
                part="snippet",            # chỉ lấy snippet, không kèm replies
                videoId=video_id,
                maxResults=100,
                order=order,
                textFormat=text_format,
                pageToken=page_token,
            )
            response = request.execute()
        except HttpError as e:
            print(f"HttpError when fetching commentThreads for video_id={video_id}: {e}", file=sys.stderr)
            break

        for item in response.get("items", []):
            # Top-level comment only
            top_snippet = item["snippet"]["topLevelComment"]["snippet"]
            top_text = top_snippet.get("textDisplay")
            if top_text:
                texts.append(top_text)

        pages += 1
        if pages >= max_pages:
            break

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    return texts


def save_comments_csv(texts: List[str], output_path: str, append: bool = True):
    """
    Ghi ra CSV 2 cột: comments, sentiment.
    - sentiment mặc định = 0 cho mọi dòng.
    - append=True: ghi nối tiếp, không xóa dữ liệu cũ. Tự thêm header nếu file chưa tồn tại.
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    file_exists = os.path.exists(output_path)
    mode = "a" if append else "w"
    with open(output_path, mode, encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if not file_exists or not append:
            writer.writerow(["comments", "sentiment"])
        for t in texts:
            writer.writerow([t, 0])
    print(f"{'Appended' if append else 'Saved'} {len(texts)} rows to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Fetch top-level YouTube comments via OAuth from videos_id.txt and save to CSV (comments,sentiment=0)."
    )
    parser.add_argument("--secrets", required=True, help="Path to OAuth client_secret.json")
    parser.add_argument("--max_pages", type=int, default=50, help="Max pages per video (100 top-level comments per page)")
    parser.add_argument("--order", choices=["time", "relevance"], default="time", help="Order of comments")
    parser.add_argument("--output_csv", default="comments_text.csv", help="Output CSV path (columns: comments,sentiment)")
    parser.add_argument("--html", action="store_true", help="Use HTML textDisplay instead of plain text")
    args = parser.parse_args()

    # Đọc danh sách video ids từ videos_id.txt
    video_ids = read_video_ids_from_file("videos_id.txt")
    if not video_ids:
        print("videos_id.txt trống hoặc không tồn tại. Hãy tạo file và thêm mỗi dòng là URL hoặc video_id.", file=sys.stderr)
        sys.exit(1)

    youtube = get_oauth_client(args.secrets)
    text_format = "html" if args.html else "plainText"

    print(f"[{datetime.now().isoformat()}] Fetching TOP-LEVEL comments for {len(video_ids)} video(s) from videos_id.txt.")
    total_rows = 0

    for vid in video_ids:
        print(f"Processing video_id={vid} ...")
        texts = fetch_all_texts(
            youtube=youtube,
            video_id=vid,
            max_pages=args.max_pages,
            order=args.order,
            text_format=text_format,
        )
        save_comments_csv(texts, args.output_csv, append=True)
        total_rows += len(texts)

    print(f"Done. Total appended rows: {total_rows}")


if __name__ == "__main__":
    main()