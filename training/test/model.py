import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from underthesea import word_tokenize

if __name__ == "__main__":
    # Đọc dữ liệu
    data = pd.read_csv(r"E:\university\Data mining\project A\training\train\preprocessed_data_model.csv", encoding="utf-8")

    # Chia train/test
    x_train, x_test, y_train, y_test = train_test_split(
        data["tokenized"], data["sentiment"], test_size=0.2, random_state=42, stratify=data["sentiment"]
    )


    # Tokenize + nối tokens thành chuỗi (phù hợp TF-IDF)
    x_train = x_train.apply(lambda text: ' '.join(word_tokenize(text)))
    x_test  = x_test.apply(lambda text: ' '.join(word_tokenize(text)))

    print("train sample:", x_train.head())
    print("test sample:", x_test.head())

    # TF-IDF
    vectorizer = TfidfVectorizer(
        max_features=10000,
        ngram_range=(1, 2),
        encoding="utf-8",
        token_pattern=r"(?u)\b\w+\b",
    )
    X_train_tfidf = vectorizer.fit_transform(x_train)
    X_test_tfidf = vectorizer.transform(x_test)


    # Logistic Regression (đa lớp, lbfgs, dùng tất cả lõi nếu nhiều lớp)
    clf = LogisticRegression(
        C=1,
        max_iter=2000,
        multi_class="multinomial",
        n_jobs=-1,
        # class_weight="balanced"
    )
    clf.fit(X_train_tfidf, y_train)

    # Dự đoán và báo cáo
    y_pred = clf.predict(X_test_tfidf)
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, digits=4))