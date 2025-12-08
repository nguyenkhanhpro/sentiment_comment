from flask import Flask, render_template, request, jsonify
import joblib
import re
from underthesea import word_tokenize
import os
import time
import emoji
import numpy as np

# Import class EmojiSentimentProcessor
try:
    from emoji_processor import EmojiSentimentProcessor
    print("Đã import EmojiSentimentProcessor thành công")
except ImportError as e:
    print(f"Lỗi import EmojiSentimentProcessor: {e}")
    # Tạo class dummy nếu không import được
    class EmojiSentimentProcessor:
        def __init__(self, csv_path=None, emoji_weight=0.3):
            print(f"Sử dụng EmojiSentimentProcessor dummy")
            self.emoji_to_score = {}
            self.emoji_weight = emoji_weight
        
        def analyze_text_emojis(self, text):
            return {'has_emoji': False, 'emoji_count': 0, 'weighted_score': 0.0}
        
        def combine_text_and_emoji_sentiment(self, text, text_score):
            return {
                'final_label': 1 if text_score > 0.2 else 0 if text_score < -0.2 else 1,
                'final_score': text_score,
                'confidence': min(abs(text_score) * 2, 1.0),
                'emoji_score': 0.0,
                'emoji_count': 0
            }

app = Flask(__name__)

# Đường dẫn đến các file trong folder app
current_dir = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(current_dir, 'sentiment_model.pkl')
VECTORIZER_PATH = os.path.join(current_dir, 'tfidf_vectorizer.pkl')
CONFIG_PATH = os.path.join(current_dir, 'model_config.txt')
EMOJI_CSV_PATH = os.path.join(current_dir, 'emoji_sentiment_labeled.csv')

print("=" * 70)
print("KHỞI ĐỘNG SENTIMENT ANALYZER WITH EMOJI AI")
print("=" * 70)

# Biến toàn cục
model = None
vectorizer = None
emoji_processor = None
model_info = {
    'accuracy': 'N/A',
    'test_accuracy': 'N/A',
    'training_samples': 'N/A',
    'test_samples': 'N/A',
    'features': 'N/A',
    'date': 'N/A',
    'model_type': 'Logistic Regression với Emoji AI Fusion'
}

# DEBUG: Kiểm tra file
print(f"Checking files in {current_dir}:")
print(f"  Model: {os.path.exists(MODEL_PATH)} - {MODEL_PATH}")
print(f"  Vectorizer: {os.path.exists(VECTORIZER_PATH)} - {VECTORIZER_PATH}")
print(f"  Config: {os.path.exists(CONFIG_PATH)} - {CONFIG_PATH}")
print(f"  Emoji CSV: {os.path.exists(EMOJI_CSV_PATH)} - {EMOJI_CSV_PATH}")

# 1. Khởi tạo EmojiSentimentProcessor với cùng trọng số như training (0.3)
try:
    if os.path.exists(EMOJI_CSV_PATH):
        print("\nKhởi tạo EmojiSentimentProcessor...")
        # SỬA: Sử dụng cùng emoji_weight=0.3 như trong training
        emoji_processor = EmojiSentimentProcessor(EMOJI_CSV_PATH, emoji_weight=0.3)
        print(f"Loaded {len(emoji_processor.emoji_to_score)} emojis")
        
        # Test một vài emoji để debug
        print("\nTest emoji scores:")
        test_emojis = ['😂', '❤️', '😍', '😭', '😊', '😡', '👎', '👍', '😘', '😔']
        for emoji_char in test_emojis:
            try:
                score = emoji_processor.get_sentiment_score(emoji_char)
                label = emoji_processor.get_sentiment_label(emoji_char)
                category, description, weight = emoji_processor.get_intensity_category(emoji_char)
                print(f"  {emoji_char}: score={score:.3f}, label={label}, category={category}")
            except Exception as e:
                print(f"  {emoji_char}: Error - {e}")
    else:
        print(f"Không tìm thấy file emoji CSV: {EMOJI_CSV_PATH}")
        emoji_processor = None
except Exception as e:
    print(f"Lỗi khởi tạo EmojiSentimentProcessor: {e}")
    import traceback
    traceback.print_exc()
    emoji_processor = None

# 2. Load model
try:
    print("\nLoading sentiment model...")
    model = joblib.load(MODEL_PATH)
    print(f"Model loaded từ: {MODEL_PATH}")
    print(f"   Model class: {model.__class__.__name__}")
    
    if hasattr(model, 'classes_'):
        print(f"   Model classes: {model.classes_}")
        
    if hasattr(model, 'predict_proba'):
        print(f"   Has predict_proba: YES")
    else:
        print(f"   Has predict_proba: NO")
        
except Exception as e:
    print(f"Lỗi load model: {e}")
    import traceback
    traceback.print_exc()
    model = None

# 3. Load vectorizer
try:
    print("\nLoading TF-IDF vectorizer...")
    vectorizer = joblib.load(VECTORIZER_PATH)
    print(f"Vectorizer loaded từ: {VECTORIZER_PATH}")
    print(f"   Vocabulary size: {len(vectorizer.vocabulary_)}")
except Exception as e:
    print(f"Lỗi load vectorizer: {e}")
    vectorizer = None

# 4. Đọc file config
try:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            for line in lines:
                if 'Test set accuracy:' in line:
                    model_info['accuracy'] = line.split(': ')[1] if ': ' in line else 'N/A'
                elif 'Training samples:' in line:
                    model_info['training_samples'] = line.split(': ')[1] if ': ' in line else 'N/A'
                elif 'Test samples:' in line:
                    model_info['test_samples'] = line.split(': ')[1] if ': ' in line else 'N/A'
                elif 'Features:' in line:
                    model_info['features'] = line.split(': ')[1] if ': ' in line else 'N/A'
                elif 'Date:' in line:
                    model_info['date'] = line.split(': ')[1] if ': ' in line else 'N/A'
        print("Đã đọc file config")
    else:
        print(f"Không tìm thấy file: {CONFIG_PATH}")
except Exception as e:
    print(f"Lỗi đọc file config: {e}")

print("\n" + "=" * 70)
print("TRẠNG THÁI HỆ THỐNG:")
print(f"  Model: {'ĐÃ TẢI' if model else 'CHƯA TẢI'}")
print(f"  Vectorizer: {'ĐÃ TẢI' if vectorizer else 'CHƯA TẢI'}")
print(f"  Emoji Processor: {'ĐÃ TẢI' if emoji_processor else 'CHƯA TẢI'}")
print(f"  Emoji weight: {emoji_processor.emoji_weight if emoji_processor else 'N/A'}")
print("=" * 70)

def clean_text_for_prediction(text):
    """
    Tiền xử lý văn bản - GIỮ EMOJI, XÓA EMOTICON TEXT
    GIỐNG VỚI TIỀN XỬ LÝ TRONG TRAINING
    """
    if not text or not isinstance(text, str):
        return ""
    
    text = str(text)
    
    # Teen code - GIỮ NGUYÊN NHƯ TRONG TRAINING
    teen_code = {
        'k': 'không', 'ko': 'không', 'kh': 'không',
        'đc': 'được', 'dc': 'được',
        'mik': 'mình', 'mk': 'mình',
        'bn': 'bạn',
        'vs': 'với',
        'cx': 'cũng',
        'sp': 'sản phẩm',
        'ok': 'ok',
        'oki': 'ok',
        'j': 'gì',
        'a': 'anh',
        'e': 'em',
        'hj': 'hihi',
        'c': 'chị',
        'z': 'vậy',
    }
    
    for old, new in teen_code.items():
        text = re.sub(r'\b' + old + r'\b', new, text, flags=re.IGNORECASE)
    
    # Xóa URL và email
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\S+@\S+', '', text)
    
    # XÓA EMOTICON TEXT, GIỮ EMOJI - GIỮ NGUYÊN NHƯ TRAINING
    text = re.sub(r'<3+', '', text)
    text = re.sub(r':-?d+', '', text, flags=re.IGNORECASE)
    text = re.sub(r':-?\)+', '', text)
    text = re.sub(r':-?\(+', '', text)
    
    # Xóa dấu câu lặp
    text = re.sub(r'!+', ' ', text)
    text = re.sub(r'\?+', ' ', text)
    
    # Chuẩn hóa từ lặp - GIỮ NGUYÊN NHƯ TRAINING
    text = re.sub(r'([a-zA-ZÀ-ỹ])\1{3,}', r'\1\1', text)
    
    # KHÔNG XÓA EMOJI - Giữ nguyên tất cả emoji
    cleaned_chars = []
    for char in text:
        # Giữ emoji
        if emoji.is_emoji(char):
            cleaned_chars.append(char)
        # Giữ chữ cái, số, khoảng trắng
        elif char.isalnum() or char.isspace():
            cleaned_chars.append(char)
        # Giữ ký tự tiếng Việt có dấu
        elif '\u00c0' <= char <= '\u1ef9':
            cleaned_chars.append(char)
        else:
            # Thay thế ký tự đặc biệt khác bằng khoảng trắng
            cleaned_chars.append(' ')
    
    text = ''.join(cleaned_chars)
    
    # Xóa khoảng trắng thừa và chuyển về lowercase
    text = re.sub(r'\s+', ' ', text).strip().lower()
    
    return text

def safe_float_conversion(value):
    """Chuyển đổi an toàn sang float"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def normalize_emoji_label(label):
    """Chuẩn hóa nhãn emoji từ text sang số (0, 1, 2)"""
    if isinstance(label, (int, float, np.integer, np.floating)):
        # Đã là số
        return int(label)
    elif isinstance(label, str):
        # Là string, cần convert
        label_lower = label.lower()
        if 'neg' in label_lower or 'tiêu cực' in label_lower or 'very_negative' in label_lower:
            return 0
        elif 'neu' in label_lower or 'trung tính' in label_lower or 'neutral' in label_lower:
            return 1
        elif 'pos' in label_lower or 'tích cực' in label_lower or 'very_positive' in label_lower or 'positive' in label_lower:
            return 2
        else:
            # Mặc định trung tính
            return 1
    else:
        # Mặc định trung tính
        return 1

def adjust_probabilities_with_emoji(text_proba, emoji_score, emoji_intensity, emoji_weight=0.3):
    """
    Điều chỉnh probabilities dựa trên emoji sentiment
    Sử dụng cùng logic với combine_text_and_emoji_sentiment từ emoji_processor
    """
    if emoji_score == 0 or emoji_intensity == 0:
        return text_proba
    
    print(f"   Adjusting probabilities with emoji: score={emoji_score:.3f}, intensity={emoji_intensity:.3f}, weight={emoji_weight}")
    
    # Đảm bảo text_proba là list của float
    try:
        processed_probs = [safe_float_conversion(p) for p in text_proba]
        text_proba = processed_probs
        print(f"   Input probabilities: {[f'{p:.3f}' for p in text_proba]}")
    except Exception as e:
        print(f"   Error in probability conversion: {e}")
        return text_proba
    
    # Tính adjustment dựa trên emoji score và intensity
    # Emoji càng mạnh (|score| lớn) thì điều chỉnh càng nhiều
    base_adjustment = abs(emoji_score) * emoji_weight * 0.8  # 0-24% adjustment
    
    # Nhân thêm với intensity factor (0-1)
    adjustment = base_adjustment * emoji_intensity
    
    # Giới hạn adjustment tối đa 30%
    adjustment = min(adjustment, 0.3)
    
    print(f"   Adjustment amount: {adjustment:.3f}")
    
    adjusted = list(text_proba)
    
    if emoji_score > 0:
        # EMOJI TÍCH CỰC: Tăng positive, giảm negative
        # Tăng positive (index 2)
        adjusted[2] = min(1.0, text_proba[2] + adjustment)
        # Giảm negative (index 0)
        adjusted[0] = max(0.0, text_proba[0] - adjustment * 0.7)
        # Neutral (index 1) giảm nhẹ
        adjusted[1] = max(0.0, text_proba[1] - adjustment * 0.3)
        
        print(f"   Positive adjustment: +{adjustment:.3f} to positive")
    else:
        # EMOJI TIÊU CỰC: Tăng negative, giảm positive
        # Tăng negative (index 0)
        adjusted[0] = min(1.0, text_proba[0] + adjustment)
        # Giảm positive (index 2)
        adjusted[2] = max(0.0, text_proba[2] - adjustment * 0.7)
        # Neutral (index 1) giảm nhẹ
        adjusted[1] = max(0.0, text_proba[1] - adjustment * 0.3)
        
        print(f"   Negative adjustment: +{adjustment:.3f} to negative")
    
    # Đảm bảo không âm và normalize
    adjusted = [max(0.0, p) for p in adjusted]
    total = sum(adjusted)
    if total > 0:
        adjusted = [p/total for p in adjusted]
    
    # Format để debug
    try:
        before_str = ', '.join([f'{p:.3f}' for p in text_proba])
        after_str = ', '.join([f'{p:.3f}' for p in adjusted])
        print(f"   Before adjustment: [{before_str}]")
        print(f"   After adjustment:  [{after_str}]")
        
        # Tính sự thay đổi
        changes = [after - before for before, after in zip(text_proba, adjusted)]
        print(f"   Changes: {[f'{c:+.3f}' for c in changes]}")
    except Exception as e:
        print(f"   Error formatting probabilities: {e}")
    
    return adjusted

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
        'emoji_processor_loaded': emoji_processor is not None,
        'emoji_weight': emoji_processor.emoji_weight if emoji_processor else 'N/A',
        'config_loaded': os.path.exists(CONFIG_PATH),
        'model_info': model_info
    })

@app.route('/predict', methods=['POST'])
def predict():
    """API dự đoán cảm xúc - KẾT HỢP TEXT VÀ EMOJI"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        print(f"\n{'='*50}")
        print(f"Nhận request predict: '{text}'")
        print(f"{'='*50}")
        
        if not text:
            return jsonify({
                'success': False,
                'error': 'Vui lòng nhập bình luận!'
            }), 400
        
        if model is None or vectorizer is None:
            return jsonify({
                'success': False,
                'error': 'Model chưa được tải!'
            }), 500
        
        start_time = time.time()
        
        # 1. Tiền xử lý text (GIỮ EMOJI) - GIỐNG TRAINING
        cleaned = clean_text_for_prediction(text)
        print(f"1. Cleaned text: '{cleaned}'")
        
        if not cleaned:
            return jsonify({
                'success': False,
                'error': 'Văn bản rỗng sau khi xử lý'
            }), 400
        
        # 2. Tách từ - GIỐNG TRAINING
        try:
            tokenized = ' '.join(word_tokenize(cleaned))
            print(f"2. Tokenized: '{tokenized}'")
        except:
            tokenized = cleaned
        
        # 3. Vector hóa và dự đoán TEXT sentiment - GIỐNG TRAINING
        vector = vectorizer.transform([tokenized])
        
        # Lấy text prediction và probabilities
        text_proba = None
        text_prediction = None
        text_sentiment_score = 0.0
        text_confidence = 0.0
        
        try:
            # Sử dụng predict_proba nếu có
            if hasattr(model, 'predict_proba'):
                text_proba_raw = model.predict_proba(vector)[0]
                text_prediction_raw = model.predict(vector)[0]
                
                print(f"3. Raw text prediction: {text_prediction_raw}")
                print(f"   Raw text probabilities: {text_proba_raw}")
                
                # Convert sang kiểu chuẩn
                text_prediction = int(text_prediction_raw)
                text_proba = [safe_float_conversion(x) for x in text_proba_raw]
                
                # Đảm bảo có đúng 3 probabilities (negative, neutral, positive)
                if len(text_proba) != 3:
                    # Tạo probabilities mặc định dựa vào prediction
                    if text_prediction == 0:  # negative
                        text_proba = [0.8, 0.1, 0.1]
                    elif text_prediction == 1:  # neutral
                        text_proba = [0.1, 0.8, 0.1]
                    else:  # positive
                        text_proba = [0.1, 0.1, 0.8]
                
                print(f"   Processed text prediction: {text_prediction}")
                print(f"   Processed text probabilities: {[f'{p:.3f}' for p in text_proba]}")
            else:
                # Fallback nếu không có predict_proba
                text_prediction_raw = model.predict(vector)[0]
                text_prediction = int(text_prediction_raw)
                if text_prediction == 0:
                    text_proba = [0.8, 0.1, 0.1]
                elif text_prediction == 1:
                    text_proba = [0.1, 0.8, 0.1]
                else:
                    text_proba = [0.1, 0.1, 0.8]
                
                print(f"3. Text prediction (no predict_proba): {text_prediction}")
                print(f"   Text probabilities (estimated): {[f'{p:.3f}' for p in text_proba]}")
        except Exception as e:
            print(f"   Error in prediction: {e}")
            import traceback
            traceback.print_exc()
            # Fallback mặc định
            text_prediction = 1  # neutral
            text_proba = [0.1, 0.8, 0.1]
        
        # Tính text sentiment score từ probabilities
        try:
            text_sentiment_score = (
                text_proba[2] * 1.0 +    # positive
                text_proba[1] * 0.0 +    # neutral
                text_proba[0] * -1.0     # negative
            )
        except Exception as e:
            print(f"   Error calculating sentiment score: {e}")
            text_sentiment_score = 1.0 if text_prediction == 2 else (
                0.0 if text_prediction == 1 else -1.0
            )
        
        # Text confidence (lấy max probability)
        try:
            text_confidence = float(max(text_proba))
        except:
            text_confidence = 1.0
        
        print(f"   Text sentiment score: {text_sentiment_score:.3f}")
        print(f"   Text confidence: {text_confidence:.3f}")
        
        # 4. PHÂN TÍCH EMOJI VÀ KẾT HỢP
        final_sentiment = text_prediction
        final_confidence = text_confidence
        final_proba = text_proba  # Mặc định dùng text probabilities
        emoji_details_list = []
        emoji_count = 0
        emoji_score = 0.0
        emoji_intensity = 0.0
        has_emoji_effect = False
        combined_score = text_sentiment_score
        emoji_effect_description = "Không có emoji hoặc emoji không đủ mạnh"
        
        if emoji_processor:
            try:
                # Phân tích emoji trong text GỐC
                emoji_analysis = emoji_processor.analyze_text_emojis(text)
                
                if emoji_analysis['has_emoji']:
                    emoji_count = emoji_analysis.get('emoji_count', 0)
                    emoji_score = emoji_analysis.get('weighted_score', 0.0)
                    emoji_intensity = emoji_analysis.get('intensity', 'neutral')
                    emoji_dominant = emoji_analysis.get('dominant_label', 1)
                    
                    print(f"4. Emoji analysis:")
                    print(f"   Count: {emoji_count}")
                    print(f"   Weighted score: {emoji_score:.3f}")
                    print(f"   Intensity: {emoji_intensity}")
                    print(f"   Dominant label: {emoji_dominant}")
                    
                    # Sử dụng hàm combine từ emoji_processor
                    combined = emoji_processor.combine_text_and_emoji_sentiment(
                        text, 
                        text_sentiment_score
                    )
                    
                    # Lấy kết quả từ combined
                    combined_score_raw = combined.get('final_score', text_sentiment_score)
                    combined_label_raw = combined.get('final_label', text_prediction)
                    combined_confidence = combined.get('confidence', text_confidence)
                    
                    # Normalize
                    combined_score = safe_float_conversion(combined_score_raw)
                    combined_label = normalize_emoji_label(combined_label_raw)
                    
                    print(f"5. Combined result:")
                    print(f"   Score: {combined_score:.3f}")
                    print(f"   Label: {combined_label}")
                    print(f"   Confidence: {combined_confidence:.3f}")
                    
                    # KIỂM TRA EMOJI ẢNH HƯỞNG - NGƯỠNG DỄ HƠN
                    has_emoji_effect = False
                    
                    # Kiểm tra 1: Label thay đổi
                    if combined_label != text_prediction:
                        has_emoji_effect = True
                        emoji_effect_description = f"Emoji đã thay đổi kết quả từ {text_prediction} sang {combined_label}"
                        print(f" EMOJI ĐÃ THAY ĐỔI KẾT QUẢ!")
                        print(f" Text-only: {text_prediction}")
                        print(f" With emoji: {combined_label}")
                    
                    # Kiểm tra 2: Score thay đổi đáng kể (> 0.1)
                    elif abs(combined_score - text_sentiment_score) > 0.05:  # Giảm ngưỡng
                        has_emoji_effect = True
                        score_diff = combined_score - text_sentiment_score
                        direction = "tăng" if score_diff > 0 else "giảm"
                        emoji_effect_description = f"Emoji {direction} cường độ cảm xúc ({abs(score_diff):.2f})"
                        print(f" EMOJI đã thay đổi intensity: {score_diff:.3f}")
                    
                    # Kiểm tra 3: Có emoji mạnh (very_positive/very_negative)
                    elif emoji_intensity in ['very_positive', 'very_negative']:
                        has_emoji_effect = True
                        emoji_effect_description = f"Emoji có cường độ mạnh ({emoji_intensity})"
                        print(f" EMOJI có cường độ mạnh: {emoji_intensity}")
                    
                    # Kiểm tra 4: Nhiều emoji
                    elif emoji_count >= 2:
                        has_emoji_effect = True
                        emoji_effect_description = f"Có {emoji_count} emoji cùng lúc"
                        print(f" Có nhiều emoji: {emoji_count}")
                    
                    # Sử dụng kết quả kết hợp
                    if has_emoji_effect:
                        final_sentiment = int(combined_label)
                        final_confidence = safe_float_conversion(combined_confidence)
                        
                        # ĐIỀU CHỈNH PROBABILITIES VỚI EMOJI
                        if text_proba is not None:
                            # Tính intensity factor từ emoji score
                            intensity_factor = min(abs(emoji_score) * 0.5, 0.3)
                            final_proba = adjust_probabilities_with_emoji(
                                text_proba, 
                                emoji_score, 
                                intensity_factor,
                                emoji_processor.emoji_weight
                            )
                            print(f"6. Final adjusted probabilities: {[f'{p:.3f}' for p in final_proba]}")
                        else:
                            final_proba = text_proba
                    else:
                        print(f"6. Emoji không đủ mạnh để thay đổi kết quả")
                        final_proba = text_proba
                        emoji_effect_description = "Emoji không đủ mạnh để thay đổi kết quả"
                    
                    # Thu thập chi tiết emoji
                    emoji_details = emoji_analysis.get('emoji_details', [])
                    for detail in emoji_details:
                        try:
                            emoji_char = detail.get('emoji', '❓')
                            score_raw = detail.get('score', 0)
                            label_raw = detail.get('label', 1)
                            category = detail.get('category', 'neutral')
                            description = detail.get('description', emoji_char)
                            weight = detail.get('weight', 1.0)
                            
                            # Xử lý an toàn
                            score = safe_float_conversion(score_raw)
                            label = normalize_emoji_label(label_raw)
                            weight = safe_float_conversion(weight)
                            
                            emoji_details_list.append({
                                'emoji': emoji_char,
                                'score': score,
                                'label': label,
                                'label_name': {0: 'Tiêu cực', 1: 'Trung tính', 2: 'Tích cực'}.get(label, 'Không xác định'),
                                'category': category,
                                'description': description,
                                'weight': weight,
                                'category_vn': {
                                    'very_positive': 'Rất tích cực',
                                    'positive': 'Tích cực',
                                    'slightly_positive': 'Hơi tích cực',
                                    'neutral': 'Trung tính',
                                    'slightly_negative': 'Hơi tiêu cực',
                                    'negative': 'Tiêu cực',
                                    'very_negative': 'Rất tiêu cực'
                                }.get(category, category)
                            })
                        except Exception as e:
                            print(f"   Error processing emoji detail: {e}")
                            continue
                    
                    print(f"   Emoji details: {len(emoji_details_list)} items")
                else:
                    print(f"4. Không có emoji trong text")
                    final_proba = text_proba
                    emoji_effect_description = "Không có emoji trong văn bản"
            except Exception as e:
                print(f"   Error analyzing emoji: {e}")
                import traceback
                traceback.print_exc()
                final_proba = text_proba
                emoji_effect_description = f"Lỗi phân tích emoji: {str(e)}"
        else:
            print(f"4. Emoji processor không khả dụng")
            final_proba = text_proba
            emoji_effect_description = "Emoji processor chưa được tải"
        
        # 5. Tính processing time
        processing_time = round((time.time() - start_time) * 1000, 1)
        
        print(f"7. Processing time: {processing_time}ms")
        print(f"   Final sentiment: {final_sentiment}")
        print(f"   Emoji effect: {has_emoji_effect} - {emoji_effect_description}")
        print(f"{'='*50}")
        
        # 6. Tạo kết quả chi tiết
        label_names = {0: 'Tiêu cực', 1: 'Trung tính', 2: 'Tích cực'}
        intensity_vn = {
            'very_positive': 'Rất tích cực',
            'positive': 'Tích cực',
            'slightly_positive': 'Hơi tích cực',
            'neutral': 'Trung tính',
            'slightly_negative': 'Hơi tiêu cực',
            'negative': 'Tiêu cực',
            'very_negative': 'Rất tiêu cực'
        }
        
        result = {
            'success': True,
            'text': text,
            'cleaned_text': cleaned,
            'sentiment': int(final_sentiment),
            'label': label_names.get(final_sentiment, 'Không xác định'),
            'confidence': round(float(final_confidence) * 100, 2),
            'processing_time_ms': processing_time,
            'has_emoji_effect': has_emoji_effect,
            'emoji_effect_description': emoji_effect_description,
            'emoji_count': emoji_count,
            'emoji_score': round(float(emoji_score), 3),
            'emoji_intensity': intensity_vn.get(emoji_intensity, emoji_intensity),
            'text_sentiment_score': round(float(text_sentiment_score), 3),
            'combined_score': round(float(combined_score), 3),
            'text_prediction': int(text_prediction),
            'text_label': label_names.get(text_prediction, 'Không xác định'),
            'emoji_weight': emoji_processor.emoji_weight if emoji_processor else 0.0
        }
        
        # 7. Thêm PROBABILITIES
        if final_proba is not None:
            try:
                # Đảm bảo có đủ 3 probabilities
                prob_values = []
                if len(final_proba) >= 3:
                    prob_values = [safe_float_conversion(p) for p in final_proba[:3]]
                else:
                    # Tạo mặc định nếu không đủ
                    if final_sentiment == 0:
                        prob_values = [0.8, 0.1, 0.1]
                    elif final_sentiment == 1:
                        prob_values = [0.1, 0.8, 0.1]
                    else:
                        prob_values = [0.1, 0.1, 0.8]
                
                # Tính phần trăm
                prob_neg = prob_values[0] * 100
                prob_neu = prob_values[1] * 100
                prob_pos = prob_values[2] * 100
                
                probabilities = {
                    'negative': round(prob_neg, 2),
                    'neutral': round(prob_neu, 2),
                    'positive': round(prob_pos, 2)
                }
                
                result['probabilities'] = probabilities
                result['probabilities_formatted'] = {
                    'Tiêu cực': f"{prob_neg:.1f}%",
                    'Trung tính': f"{prob_neu:.1f}%",
                    'Tích cực': f"{prob_pos:.1f}%"
                }
                
                # Thêm probabilities gốc để so sánh
                if text_proba is not None and len(text_proba) >= 3:
                    orig_probs = [safe_float_conversion(p) for p in text_proba[:3]]
                    result['original_probabilities'] = {
                        'negative': round(orig_probs[0] * 100, 2),
                        'neutral': round(orig_probs[1] * 100, 2),
                        'positive': round(orig_probs[2] * 100, 2)
                    }
                    
                    # Tính sự thay đổi
                    if has_emoji_effect:
                        change_neg = probabilities['negative'] - result['original_probabilities']['negative']
                        change_neu = probabilities['neutral'] - result['original_probabilities']['neutral']
                        change_pos = probabilities['positive'] - result['original_probabilities']['positive']
                        
                        result['probability_changes'] = {
                            'negative': f"{'+' if change_neg > 0 else ''}{change_neg:.1f}%",
                            'neutral': f"{'+' if change_neu > 0 else ''}{change_neu:.1f}%",
                            'positive': f"{'+' if change_pos > 0 else ''}{change_pos:.1f}%"
                        }
            except Exception as e:
                print(f"Error creating probabilities: {e}")
                # Tạo probabilities mặc định
                result['probabilities'] = {
                    'negative': 33.3,
                    'neutral': 33.3,
                    'positive': 33.3
                }
        
        # 8. Thêm chi tiết emoji nếu có
        if emoji_details_list:
            result['emoji_details'] = emoji_details_list
        
        # 9. Thêm thông tin model
        result['model_info'] = model_info
        
        # 10. Thêm flag để frontend biết đã điều chỉnh probabilities
        result['probabilities_adjusted'] = has_emoji_effect
        
        print(f"Response ready - Emoji effect: {has_emoji_effect}")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in predict: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': f'Lỗi server: {str(e)}'
        }), 500

@app.route('/test', methods=['GET'])
def test_route():
    """Test route để kiểm tra hệ thống"""
    test_texts = [
        "Sản phẩm tuyệt vời",
        "Sản phẩm tuyệt vời 😂",
        "Sản phẩm tuyệt vời 😂😂😂",
        "Sản phẩm tệ",
        "Sản phẩm tệ 😭",
        "Sản phẩm tệ 😭😭😭",
        "Sản phẩm bình thường",
        "Sản phẩm bình thường 😐",
    ]
    
    results = []
    for text in test_texts:
        try:
            cleaned = clean_text_for_prediction(text)
            
            result = {
                'text': text,
                'cleaned': cleaned,
                'emoji_count': sum(1 for char in text if emoji.is_emoji(char))
            }
            
            if emoji_processor:
                analysis = emoji_processor.analyze_text_emojis(text)
                result['emoji_analysis'] = {
                    'has_emoji': analysis['has_emoji'],
                    'count': analysis['emoji_count'],
                    'score': analysis['weighted_score'],
                    'intensity': analysis['intensity']
                }
            
            results.append(result)
        except Exception as e:
            results.append({'text': text, 'error': str(e)})
    
    return jsonify({'test_results': results})

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("KHỞI ĐỘNG WEB SERVER...")
    print("=" * 70)
    
    print("\nThông tin hệ thống:")
    print(f"  Model: {'ĐÃ TẢI' if model else 'CHƯA TẢI'}")
    print(f"  Vectorizer: {'ĐÃ TẢI' if vectorizer else 'CHƯA TẢI'}")
    print(f"  Emoji Processor: {'ĐÃ TẢI' if emoji_processor else 'CHƯA TẢI'}")
    print(f"  Emoji weight: {emoji_processor.emoji_weight if emoji_processor else 'N/A'}")
    print(f"  Accuracy: {model_info['accuracy']}")
    print(f"  Training samples: {model_info['training_samples']}")
    
    print("\nTính năng mới:")
    print("  ✓ Probabilities điều chỉnh với emoji")
    print("  ✓ Hiển thị probabilities gốc và đã điều chỉnh")
    print("  ✓ Cường độ ảnh hưởng emoji")
    print("  ✓ Sử dụng cùng emoji_weight với training (0.3)")
    
    print("\nServer đang chạy tại: http://localhost:5000")
    print("Test API tại: http://localhost:5000/test")
    print("Health check: http://localhost:5000/health")
    print("\nĐang khởi động server...")
    
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)