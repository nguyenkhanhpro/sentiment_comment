import pandas as pd
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from underthesea import word_tokenize
from sklearn.pipeline import Pipeline
import numpy as np

data = pd.read_csv("preprocessed_data_model.csv")
data
x_clean = data['tokenized'].apply(lambda x: word_tokenize(x))
y = data['sentiment']

X_train, X_test, y_train, y_test = train_test_split(
    x_clean, y, test_size=0.2, random_state=42
)
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(
        tokenizer=lambda x: x,
        preprocessor=lambda x: x,
        token_pattern=None
    )),
    ('svc', LinearSVC(max_iter=5000))
])

param_dist = {
    'tfidf__ngram_range': [(1,2)],  # unigram, bigram, trigram
    'tfidf__max_df': [1.0],        # loại bỏ từ quá phổ biến
    'tfidf__min_df': [1],                   # loại bỏ từ quá hiếm
    'svc__class_weight': ['balanced']      # cân bằng lớp
}
# Randomized Search
random_search = RandomizedSearchCV(
    pipeline, param_distributions=param_dist,
    n_iter=120,               # số thử nghiệm ngẫu nhiên
    scoring='accuracy',
    cv=5,                    # 5-fold cross-validation
    verbose=2,
    random_state=42,
    n_jobs=-1
)
random_search.fit(X_train, y_train)

print("Best Score:", random_search.best_score_)
print("Best Params:", random_search.best_params_)

best_model = random_search.best_estimator_
y_pred = best_model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print("Test Accuracy:", acc)
report = classification_report(y_test, y_pred, digits=4)
print("Classification Report:\n", report)