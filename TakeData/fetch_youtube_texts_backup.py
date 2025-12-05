import argparse
import csv
import os
import sys
from datetime import datetime
from typing import List, Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Scopes: youtube.readonly đủ cho đọc công khai; nếu gặp lỗi, dùng youtube.force-ssl.
SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl",  # bật nếu readonly vẫn bị chặn
]


def get_oauth_client(secrets_path: str, token_path: str = "token.json"):
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())  # type: ignore[name-defined]
            except Exception:
                creds = None
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(secrets_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def fetch_all_texts(
    youtube,
    video_id: str,
    max_pages: int = 50,
    order: str = "time",
    text_format: str = "plainText",
    include_replies: bool = True,
) -> List[str]:
    texts: List[str] = []
    pages = 0
    page_token: Optional[str] = None

    while True:
        try:
            request = youtube.commentThreads().list(
                part="snippet,replies" if include_replies else "snippet",
                videoId=video_id,
                maxResults=100,
                order=order,
                textFormat=text_format,
                pageToken=page_token,
            )
            response = request.execute()
        except HttpError as e:
            print(f"HttpError when fetching commentThreads: {e}", file=sys.stderr)
            break

        for item in response.get("items", []):
            # Top-level comment
            top_snippet = item["snippet"]["topLevelComment"]["snippet"]
            top_text = top_snippet.get("textDisplay")
            if top_text:
                texts.append(top_text)

            # Replies
            if include_replies:
                replies_block = item.get("replies", {})
                for reply in replies_block.get("comments", []) or []:
                    r = reply.get("snippet", {})
                    r_text = r.get("textDisplay")
                    if r_text:
                        texts.append(r_text)

        pages += 1
        if pages >= max_pages:
            break

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    return texts


def save_texts_csv(texts: List[str], output_path: str):
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["text"])
        for t in texts:
            writer.writerow([t])
    print(f"Saved {len(texts)} rows to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Fetch YouTube video comments text (with replies) via OAuth and save to CSV.")
    parser.add_argument("--secrets", required=True, help="Path to OAuth client_secret.json")
    parser.add_argument("--video_id", required=True, help="YouTube video ID")
    parser.add_argument("--max_pages", type=int, default=50, help="Max pages (100 top-level comments per page)")
    parser.add_argument("--order", choices=["time", "relevance"], default="time", help="Order of comments")
    parser.add_argument("--output", default="comments_text.csv", help="Output CSV path")
    parser.add_argument("--html", action="store_true", help="Return HTML instead of plain text")
    args = parser.parse_args()

    youtube = get_oauth_client(args.secrets)
    print(f"[{datetime.now().isoformat()}] Fetching text comments for video_id={args.video_id}")

    texts = fetch_all_texts(
        youtube=youtube,
        video_id=args.video_id,
        max_pages=args.max_pages,
        order=args.order,
        text_format="html" if args.html else "plainText",
        include_replies=True,
    )

    save_texts_csv(texts, args.output)


if __name__ == "__main__":
    main()