import os

INPUT_FILE = "videos_id.txt"

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"File không tồn tại: {INPUT_FILE}")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        ids = [line.strip() for line in f if line.strip()]

    unique_ids = set(ids)  # không giữ thứ tự

    with open(INPUT_FILE, "w", encoding="utf-8", newline="") as f:
        for vid in unique_ids:
            f.write(vid + "\n")

    print(f"Đã loại bỏ trùng lặp: {len(ids)} dòng -> {len(unique_ids)} video ID duy nhất.")

if __name__ == "__main__":
    main()