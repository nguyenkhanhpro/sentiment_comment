import os
from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret")

# Đường dẫn file CSV có đúng 2 cột: comments,sentiment
CSV_PATH = os.getenv("COMMENTS_CSV", "comments_ipad_labeled.csv")
PER_PAGE = int(os.getenv("PER_PAGE", "50"))

def ensure_csv_exists():
    if not os.path.exists(CSV_PATH):
        # Tạo file rỗng với header đúng yêu cầu: comments,sentiment
        pd.DataFrame(columns=["comments", "sentiment"]).to_csv(
            CSV_PATH, index=False, encoding="utf-8"
        )

def load_df() -> pd.DataFrame:
    ensure_csv_exists()
    df = pd.read_csv(CSV_PATH, encoding="utf-8")

    changed = False

    # Tương thích nếu từng dùng schema cũ text/status
    if "comments" not in df.columns and "text" in df.columns:
        df["comments"] = df["text"]
        changed = True
    if "sentiment" not in df.columns and "status" in df.columns:
        df["sentiment"] = df["status"]
        changed = True

    # Đảm bảo 2 cột: comments, sentiment
    if "comments" not in df.columns:
        df["comments"] = ""
        changed = True
    if "sentiment" not in df.columns:
        df["sentiment"] = 0
        changed = True

    # Chuẩn hóa kiểu sentiment về int và fill NaN
    try:
        df["sentiment"] = pd.to_numeric(df["sentiment"], errors="coerce").fillna(0).astype(int)
    except Exception:
        df["sentiment"] = 0
        changed = True

    # Chỉ giữ đúng 2 cột theo yêu cầu
    df = df[["comments", "sentiment"]]

    if changed:
        df.to_csv(CSV_PATH, index=False, encoding="utf-8")

    return df

def save_df(df: pd.DataFrame):
    # Chỉ lưu đúng 2 cột: comments,sentiment
    out = df[["comments", "sentiment"]].copy()
    out.to_csv(CSV_PATH, index=False, encoding="utf-8")

@app.route("/")
def index():
    page = request.args.get("page", default=1, type=int)
    df = load_df()

    total = len(df)
    total_pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)
    page = max(1, min(page, total_pages))

    start = (page - 1) * PER_PAGE
    end = min(start + PER_PAGE, total)

    page_df = df.iloc[start:end].copy()

    # Dùng chỉ số hàng (row index) để cập nhật chính xác khi lưu
    records = []
    for idx, row in page_df.iterrows():
        records.append({
            "row": int(idx),  # chỉ số tuyệt đối trong file
            "comments": row.get("comments", ""),
            "sentiment": int(row.get("sentiment", 0)),
        })

    return render_template(
        "index.html",
        records=records,
        page=page,
        total_pages=total_pages,
        total_rows=total,
        per_page=PER_PAGE,
    )

@app.post("/save")
def save():
    page = request.args.get("page", default=1, type=int)
    df = load_df()

    updated = 0
    for key, val in request.form.items():
        # name dạng: sentiment_<row_index>
        if not key.startswith("sentiment_"):
            continue
        try:
            row_index = int(key.split("_", 1)[1])
        except ValueError:
            continue
        if val not in {"0", "1", "2"}:
            continue

        if 0 <= row_index < len(df):
            df.at[row_index, "sentiment"] = int(val)
            updated += 1

    save_df(df)
    flash(f"Đã lưu {updated} dòng.")
    return redirect(url_for("index", page=page))

if __name__ == "__main__":
    ensure_csv_exists()
    app.run(debug=True)