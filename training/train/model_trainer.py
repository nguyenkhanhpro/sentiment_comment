import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
import os
from preprocessor import clean_text_with_intensity
from underthesea import word_tokenize

def train_model_from_preprocessed_data():
    print("=" * 70)
    print("HUAN LUYEN MODEL TU DU LIEU DA TIEN XU LY")
    print("=" * 70)
    
    # 1. Đọc dữ liệu đã tiền xử lý
    print("\n1. Doc du lieu da tien xu ly...")
    
    possible_files = ['preprocessed_data_model.csv'] 

    
    data_file = None
    for file in possible_files:
        if os.path.exists(file):
            data_file = file
            print(f"  Doc tu: {file}")
            break
    
    if data_file is None:
        print("   Khong tim thay file du lieu da tien xu ly")
        print("   Vui long chay preprocessor.py truoc")
        return None, None
    
    df = pd.read_csv(data_file)
    
    # Kiểm tra các cột cần thiết
    required_columns = ['tokenized', 'sentiment']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"   Thieu cot: {missing_columns}")
        print(f"   Cac cot co san: {list(df.columns)}")
        return None, None
    
    print(f"   Doc du lieu: {len(df)} mau")
    print(f"   Cac cot: {list(df.columns)}")
    
    # 2. Chia train/test
    print("\n2. Chia du lieu train/test...")
    X = df['tokenized'].values
    y = df['sentiment'].values
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"  Train: {len(X_train)} samples")
    print(f"  Test: {len(X_test)} samples")
    
    # 3. TF-IDF Vectorization
    print("\n3. TF-IDF Vectorization...")
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.8,
        sublinear_tf=True
    )
    
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    print(f"   Train shape: {X_train_tfidf.shape}")
    print(f"   Vocabulary size: {len(vectorizer.vocabulary_)}")
    
    # 4. Train Logistic Regression Model
    print("\n4. Training Logistic Regression...")
    lr_model = LogisticRegression(
        C=0.7,
        max_iter=1000,
        class_weight='balanced',
        random_state=42,
        multi_class='multinomial',
        solver='lbfgs'
    )
    
    lr_model.fit(X_train_tfidf, y_train)
    print(f"  Training hoan tat sau {lr_model.n_iter_[0]} iterations")
    
    # 5. Đánh giá model
    print("\n5. Danh gia model...")
    
    # Dự đoán
    y_pred = lr_model.predict(X_test_tfidf)
    y_pred_proba = lr_model.predict_proba(X_test_tfidf)
    
    # Tính accuracy
    acc = accuracy_score(y_test, y_pred)
    print(f"   Accuracy = {acc:.4f}")
    
    # Classification report
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, 
                               target_names=['Tieu cuc', 'Trung tinh', 'Tich cuc']))
    
    # 6. Lưu model vào folder training/app/
    print("\n6. Luu model vao folder training/app/...")
    
    # Xác định đường dẫn tuyệt đối đến folder training/app/
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_folder_path = os.path.join(script_dir, 'app')
    
    print(f"   Script directory: {script_dir}")
    print(f"   App folder path: {app_folder_path}")
    
    # Tạo folder app nếu chưa tồn tại
    if not os.path.exists(app_folder_path):
        os.makedirs(app_folder_path)
        print(f" Tao folder: {app_folder_path}")
    else:
        print(f" Folder da ton tai: {app_folder_path}")
    
    # Lưu các file vào folder app
    model_path = os.path.join(app_folder_path, 'sentiment_model.pkl')
    vectorizer_path = os.path.join(app_folder_path, 'tfidf_vectorizer.pkl')
    
    joblib.dump(lr_model, model_path)
    joblib.dump(vectorizer, vectorizer_path)
    
    print(f" Luu sentiment_model: {model_path}")
    print(f" Luu tfidf_vectorizer: {vectorizer_path}")
    
    # Lưu config
    config_path = os.path.join(app_folder_path, 'model_config.txt')
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(f"Model trained with emoticon intensity processing (DAU CACH)\n")
        f.write(f"Date: {pd.Timestamp.now()}\n")
        f.write(f"Test set accuracy: {acc:.4f}\n")
        f.write(f"Training samples: {len(X_train)}\n")
        f.write(f"Test samples: {len(X_test)}\n")
        f.write(f"Features: {X_train_tfidf.shape[1]}\n")
        f.write(f"Model saved in: {app_folder_path}\n")
        f.write(f"\nEMOTICON INTENSITY TAGS:\n")
        f.write(f"  :) -> [cười nhẹ] (weight=1)\n")
        f.write(f"  :)) -> [cười vừa] (weight=2)\n")
        f.write(f"  :))) -> [cười mạnh] (weight=3)\n")
        f.write(f"  :))))+ -> [rất cười] (weight=3)\n")
        f.write(f"  :( -> [buồn nhẹ] (weight=1)\n")
        f.write(f"  :(( -> [buồn vừa] (weight=2)\n")
        f.write(f"  :((( -> [buồn mạnh] (weight=3)\n")
        f.write(f"  :((((+ -> [rất buồn] (weight=3)\n")
        f.write(f"  <3 -> [tim nhẹ] (weight=1)\n")
        f.write(f"  <33 -> [tim vừa] (weight=2)\n")
        f.write(f"  <333+ -> [tim mạnh] (weight=3)\n")
        f.write(f"  :D -> [cười to nhẹ] (weight=1)\n")
        f.write(f"  :DD -> [cười to vừa] (weight=2)\n")
        f.write(f"  :DDD+ -> [cười to mạnh] (weight=3)\n")
    
    print(f" Luu config: {config_path}")
    
    # 7. Test model với các trường hợp đặc biệt
    print("\n7. Test model voi cac truong hop dac biet...")
    
    test_cases = [
        ("Tốt :)", 2),
        ("Rất tốt :))", 2),
        ("Xuất sắc :)))", 2),
        ("Tuyệt vời :))))", 2),
        ("Tệ :(", 0),
        ("Rất tệ :((", 0),
        ("Khủng khiếp :(((", 0),
        ("Thảm họa :((((", 0),
        ("Yêu <3", 2),
        ("Rất yêu <33", 2),
        ("Yêu cực <333", 2),
        ("Tốt :D", 2),
        ("Rất tốt :DD", 2),
        ("Xuất sắc :DDD", 2),
        ("Sản phẩm tốt", 2),
        ("Sản phẩm tệ", 0),
        ("Sản phẩm bình thường", 1),
    ]
    
    label_names = ['Tieu cuc', 'Trung tinh', 'Tich cuc']
    
    print("\n" + "=" * 70)
    print("KET QUA TEST EMOTICON CUONG DO (DAU CACH)")
    print("=" * 70)
    
    correct = 0
    total = len(test_cases)
    
    for i, (text, expected) in enumerate(test_cases, 1):
        # Clean và tokenize
        cleaned = clean_text_with_intensity(text, None, 'balanced')
        tokenized = ' '.join(word_tokenize(cleaned))
        
        # Vectorize và predict
        vectorized = vectorizer.transform([tokenized])
        pred = lr_model.predict(vectorized)[0]
        proba = lr_model.predict_proba(vectorized)[0]
        
        # Kết quả
        is_correct = pred == expected
        if is_correct:
            correct += 1
        
        result_symbol = "YES" if is_correct else "NO"
        print(f"\n{i:2d}. {result_symbol} '{text}'")
        print(f"   -> Du doan: {label_names[pred]} (xac suat: {max(proba):.2%})")
        print(f"   -> Ky vong: {label_names[expected]}")
    
    accuracy_rate = correct/total*100
    print(f"\nKet qua: {correct}/{total} ({accuracy_rate:.1f}%)")
    
    # 8. Summary
    print("\n" + "=" * 70)
    print("TONG KET")
    print("=" * 70)
    print(f"Model: Logistic Regression voi Emoticon Cuong Do")
    print(f"Accuracy tren test set: {acc:.4f}")
    print(f"Accuracy tren vi du test: {correct}/{total} ({accuracy_rate:.1f}%)")
    print(f"Models da duoc luu vao: {app_folder_path}/")
    print(f"\nDe chay web app:")
    print(f"   cd {app_folder_path}")
    print(f"   python app.py")
    print(f"Truy cap: http://localhost:5000")
    print("=" * 70)
    
    return lr_model, vectorizer

if __name__ == "__main__":
    train_model_from_preprocessed_data()