import requests
import csv
from bs4 import BeautifulSoup

URL = "http://kt.ijs.si/data/Emoji_sentiment_ranking/"

def fetch_emoji_sentiment(url=URL):
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    table = soup.find("table")
    rows = table.find_all("tr")

    header = [th.get_text().strip() for th in rows[0].find_all("th")]

    # Cột mới theo đúng header bạn nhận được
    try:
        col_emoji = header.index("Char")
        col_S = header.index("Sentiment score[-1...+1]")
    except ValueError:
        raise RuntimeError("Không tìm thấy cột Char hoặc Sentiment score — header: " + str(header))

    data = []
    for row in rows[1:]:
        cols = row.find_all("td")
        if len(cols) <= max(col_emoji, col_S):
            continue

        emoji_char = cols[col_emoji].get_text().strip()
        score = cols[col_S].get_text().strip()

        try:
            score = float(score)
        except:
            continue

        # mapping sentiment
        if score > 0:
            label = 2  # positive
        elif score < 0:
            label = 0  # negative
        else:
            label = 1  # neutral

        data.append((emoji_char, score, label))

    return data


def save_to_csv(data, filepath="emoji_sentiment_labeled.csv"):
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["emoji", "sentiment_score", "label"])
        for emoji_char, score, label in data:
            writer.writerow([emoji_char, score, label])


if __name__ == "__main__":
    data = fetch_emoji_sentiment()
    print(f"Fetched {len(data)} emoji rows")
    save_to_csv(data)
    print("Saved to emoji_sentiment_labeled.csv")
