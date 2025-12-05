from flask import Flask, render_template, request, jsonify
import joblib
import re
from underthesea import word_tokenize
import os

app = Flask(__name__)

# Đường dẫn đến các file trong folder app
current_dir = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(current_dir, 'sentiment_model.pkl')
VECTORIZER_PATH = os.path.join(current_dir, 'tfidf_vectorizer.pkl')
CONFIG_PATH = os.path.join(current_dir, 'model_config.txt')

print("Dang tai model...")

# Biến toàn cục
model = None
vectorizer = None
model_info = {
    'accuracy': 'N/A',
    'test_accuracy': 'N/A',
    'training_samples': 'N/A',
    'test_samples': 'N/A',
    'features': 'N/A',
    'date': 'N/A',
    'model_type': 'Logistic Regression voi Emoticon Cuong Do'
}

# 1. Đọc file config đầu tiên
try:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
            # Parse thông tin từ config
            lines = content.split('\n')
            for line in lines:
                if 'Test set accuracy:' in line:
                    model_info['accuracy'] = line.split(': ')[1] if ': ' in line else 'N/A'
                elif 'Test cases accuracy:' in line:
                    model_info['test_accuracy'] = line.split(': ')[1] if ': ' in line else 'N/A'
                elif 'Training samples:' in line:
                    model_info['training_samples'] = line.split(': ')[1] if ': ' in line else 'N/A'
                elif 'Test samples:' in line:
                    model_info['test_samples'] = line.split(': ')[1] if ': ' in line else 'N/A'
                elif 'Features:' in line:
                    model_info['features'] = line.split(': ')[1] if ': ' in line else 'N/A'
                elif 'Date:' in line:
                    model_info['date'] = line.split(': ')[1] if ': ' in line else 'N/A'
        print("YES Da doc file config")
    else:
        print(f"NO Khong tim thay file: {CONFIG_PATH}")
except Exception as e:
    print(f"NO Loi doc file config: {e}")

# 2. Load model
try:
    model = joblib.load(MODEL_PATH)
    print(f"YES Da load model tu: {MODEL_PATH}")
except Exception as e:
    print(f"NO Loi load model: {e}")
    model = None

# 3. Load vectorizer
try:
    vectorizer = joblib.load(VECTORIZER_PATH)
    print(f"YES Da load vectorizer tu: {VECTORIZER_PATH}")
except Exception as e:
    print(f"NO Loi load vectorizer: {e}")
    vectorizer = None

print("Hoan tat tai model")

def clean_text_for_prediction(text):
    """Tiền xử lý văn bản - GIỐNG HỆT training"""
    if not text:
        return ""
    
    text = str(text).lower()
    
    # Teen code (giống training)
    teen_code = {
        'k': 'không', 'ko': 'không', 'kh': 'không',
        'đc': 'được', 'dc': 'được',
        'mik': 'mình', 'mk': 'mình',
        'bn': 'bạn',
        'vs': 'với',
        'cx': 'cũng',
    }
    
    for old, new in teen_code.items():
        text = re.sub(r'\b' + old + r'\b', new, text)
    
    # Xóa URL và email
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\S+@\S+', '', text)
    
    # Xử lý emoticon cường độ (GIỐNG training)
    # :) → [cười nhẹ]
    text = re.sub(r':-?\)(?!\))', ' [cười nhẹ] ', text)
    # :)) → [cười vừa]
    text = re.sub(r':-?\){2}(?!\))', ' [cười vừa] ', text)
    # :))) → [cười mạnh]
    text = re.sub(r':-?\){3}(?!\))', ' [cười mạnh] ', text)
    # :))))+ → [rất cười]
    text = re.sub(r':-?\){4,}', ' [rất cười] ', text)
    
    # :( → [buồn nhẹ]
    text = re.sub(r':-?\((?!\()', ' [buồn nhẹ] ', text)
    # :(( → [buồn vừa]
    text = re.sub(r':-?\({2}(?!\()', ' [buồn vừa] ', text)
    # :((( → [buồn mạnh]
    text = re.sub(r':-?\({3}(?!\()', ' [buồn mạnh] ', text)
    # :((((+ → [rất buồn]
    text = re.sub(r':-?\({4,}', ' [rất buồn] ', text)
    
    # <3 → [tim nhẹ]
    text = re.sub(r'<3(?!3)', ' [tim nhẹ] ', text)
    # <33 → [tim vừa]
    text = re.sub(r'<3{2}(?!3)', ' [tim vừa] ', text)
    # <333+ → [tim mạnh]
    text = re.sub(r'<3{3,}', ' [tim mạnh] ', text)
    
    # Xóa ký tự đặc biệt, giữ chữ, số, khoảng trắng, và dấu []
    text = re.sub(r'[^a-zA-ZÀ-ỹ0-9\s\[\]]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

@app.route('/')
def index():
    """Trang chủ"""
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health():
    """Kiểm tra server và model"""
    return jsonify({
        'status': 'healthy' if model and vectorizer else 'error',
        'model_loaded': model is not None,
        'vectorizer_loaded': vectorizer is not None,
        'config_loaded': os.path.exists(CONFIG_PATH),
        'model_info': model_info
    })

@app.route('/predict', methods=['POST'])
def predict():
    """API dự đoán cảm xúc"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({
                'success': False,
                'error': 'Vui long nhap binh luan!'
            }), 400
        
        if model is None or vectorizer is None:
            return jsonify({
                'success': False,
                'error': 'Model chua duoc tai!'
            }), 500
        
        # Tiền xử lý (PHẢI GIỐNG training)
        cleaned = clean_text_for_prediction(text)
        if not cleaned:
            return jsonify({
                'success': False,
                'error': 'Van ban rong sau khi xu ly'
            }), 400
        
        # Tách từ
        tokenized = ' '.join(word_tokenize(cleaned))
        
        # Vector hóa
        vector = vectorizer.transform([tokenized])
        
        # Dự đoán
        prediction = model.predict(vector)[0]
        
        # Lấy xác suất
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(vector)[0]
            probabilities = {
                'negative': float(proba[0]) * 100,
                'neutral': float(proba[1]) * 100,
                'positive': float(proba[2]) * 100
            }
            confidence = float(max(proba)) * 100
        else:
            probabilities = {'negative': 0.0, 'neutral': 0.0, 'positive': 0.0}
            probabilities[['negative', 'neutral', 'positive'][prediction]] = 100.0
            confidence = 100.0
        
        # Làm tròn
        probabilities = {k: round(v, 2) for k, v in probabilities.items()}
        confidence = round(confidence, 2)
        
        # Tạo kết quả
        sentiment_map = {
            0: {'label': 'Tiêu cực'},
            1: {'label': 'Trung tính'},
            2: {'label': 'Tích cực'}
        }
        
        result = sentiment_map[prediction]
        result['success'] = True
        result['sentiment'] = int(prediction)
        result['confidence'] = confidence
        result['probabilities'] = probabilities
        result['probabilities_formatted'] = {
            'Tiêu cực': f"{probabilities['negative']:.1f}%",
            'Trung tính': f"{probabilities['neutral']:.1f}%",
            'Tích cực': f"{probabilities['positive']:.1f}%"
        }
        result['cleaned_text'] = cleaned
        
        # Thêm thông tin model
        result['model_info'] = model_info
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Loi server: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("Khoi dong server...")
    print("Thong tin model:")
    print(f"  Accuracy: {model_info['accuracy']}")
    print(f"  Test accuracy: {model_info['test_accuracy']}")
    print(f"  Date: {model_info['date']}")
    print(f"  Features: {model_info['features']}")
    app.run(debug=True, host='0.0.0.0', port=5000)