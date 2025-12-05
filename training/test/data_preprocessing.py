import re
import pandas as pd
from datasets import Dataset
def clean_text(text):
    # Xóa URL
    text = re.sub(r'http\S+|www\.\S+', ' ', text)

    # Xóa ký tự không cần thiết nhưng giữ emoji
    text = re.sub(r'[\x00-\x1F\x7F]', ' ', text)

    # Chuẩn hóa khoảng trắng
    text = re.sub(r'\s+', ' ', text).strip()

    return text
def dataset_preprocessing():
    df = pd.read_csv("comments_text_labeled.csv")
    df["comments"] = df["comments"].astype(str).apply(clean_text)

    dataset = Dataset.from_pandas(df)
    print(dataset)

    return dataset