import pandas as pd
import re
from underthesea import word_tokenize
from emoji_processor import EmojiSentimentProcessor
from collections import Counter
import warnings
import os
warnings.filterwarnings('ignore')

def clean_text_with_intensity(text, emoji_processor=None, mode='balanced'):
    if pd.isna(text) or not isinstance(text, str):
        return ""
    
    text = str(text).lower()
    
    # Xử lý teen code
    teen_code = {
        'mik': 'mình', 'mk': 'mình',
        'bn': 'bạn',
        'đc': 'được', 'dc': 'được',
        'k': 'không', 'ko': 'không', 'kh': 'không',
        'vs': 'với',
        'cx': 'cũng',
        'sp': 'sản phẩm',
        'ok': 'ok',
        'oki': 'ok',
    }
    
    for old, new in teen_code.items():
        text = re.sub(r'\b' + old + r'\b', new, text)
    
    # Xóa URL và email
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\S+@\S+', '', text)
    
    # ========== XỬ LÝ EMOTICON CÓ CƯỜNG ĐỘ ==========
    
    # 1. Xử lý EMOJI trước (nếu có processor)
    if emoji_processor and mode == 'balanced':
        text = emoji_processor.process_text(text, mode='balanced')
    
    # 2. Emoticon tim <3 (xử lý từ dài đến ngắn)
    # <333 hoặc nhiều hơn → [tim mạnh]   (DẤU CÁCH)
    text = re.sub(r'<3{3,}', ' [tim mạnh] ', text)
    # <33 → [tim vừa]   (DẤU CÁCH)
    text = re.sub(r'<3{2}(?!3)', ' [tim vừa] ', text)
    # <3 → [tim nhẹ]   (DẤU CÁCH)
    text = re.sub(r'<3(?!3)', ' [tim nhẹ] ', text)
    
    # 3. Emoticon cười lớn :D (xử lý từ dài đến ngắn)
    # :DDD hoặc nhiều hơn → [cười to mạnh]   (DẤU CÁCH)
    text = re.sub(r':-?d{3,}', ' [cười to mạnh] ', text, flags=re.IGNORECASE)
    # :DD → [cười to vừa]   (DẤU CÁCH)
    text = re.sub(r':-?d{2}(?!d)', ' [cười to vừa] ', text, flags=re.IGNORECASE)
    # :D → [cười to nhẹ]   (DẤU CÁCH)
    text = re.sub(r':-?d(?!d)', ' [cười to nhẹ] ', text, flags=re.IGNORECASE)
    
    # 4. Emoticon cười :) (FIXED - QUAN TRỌNG)
    # Xử lý từ DÀI nhất đến NGẮN nhất
    # :)))) hoặc nhiều hơn → [rất cười]   (DẤU CÁCH)
    text = re.sub(r':-?\){4,}', ' [rất cười] ', text)
    # :))) → [cười mạnh]   (DẤU CÁCH)
    text = re.sub(r':-?\){3}(?!\))', ' [cười mạnh] ', text)
    # :)) → [cười vừa]   (DẤU CÁCH)
    text = re.sub(r':-?\){2}(?!\))', ' [cười vừa] ', text)
    # :) → [cười nhẹ]   (DẤU CÁCH)
    text = re.sub(r':-?\)(?!\))', ' [cười nhẹ] ', text)
    
    # 5. Emoticon buồn :( 
    # Xử lý từ DÀI nhất đến NGẮN nhất
    # :(((( hoặc nhiều hơn → [rất buồn]   (DẤU CÁCH)
    text = re.sub(r':-?\({4,}', ' [rất buồn] ', text)
    # :((( → [buồn mạnh]   (DẤU CÁCH)
    text = re.sub(r':-?\({3}(?!\()', ' [buồn mạnh] ', text)
    # :(( → [buồn vừa]   (DẤU CÁCH)
    text = re.sub(r':-?\({2}(?!\()', ' [buồn vừa] ', text)
    # :( → [buồn nhẹ]   (DẤU CÁCH)
    text = re.sub(r':-?\((?!\()', ' [buồn nhẹ] ', text)
    
    # ========== XỬ LÝ DẤU CÂU CÓ CƯỜNG ĐỘ ==========
    # Xử lý từ mạnh đến nhẹ
    
    # !!!! trở lên → [nhấn mạnh mạnh]   (DẤU CÁCH)
    text = re.sub(r'!{4,}', ' [nhấn mạnh mạnh] ', text)
    # !!! → [nhấn mạnh vừa]   (DẤU CÁCH)
    text = re.sub(r'!{3}(?!!)', ' [nhấn mạnh vừa] ', text)
    # !! → [nhấn mạnh nhẹ]   (DẤU CÁCH)
    text = re.sub(r'!{2}(?!!)', ' [nhấn mạnh nhẹ] ', text)
    # ! → (xóa)
    text = re.sub(r'!(?!!)', '', text)
    
    # ??? tương tự
    text = re.sub(r'\?{3,}', ' [nhiều chấm hỏi mạnh] ', text)
    text = re.sub(r'\?{2}(?!\?)', ' [nhiều chấm hỏi nhẹ] ', text)
    text = re.sub(r'\?(?!\?)', ' ', text)
    
    # ========== CHUẨN HÓA CUỐI CÙNG ==========
    # Chuẩn hóa từ lặp
    text = re.sub(r'(.)\1{3,}', r'\1\1\1', text)
    
    # Loại bỏ ký tự đặc biệt, giữ chữ, số, khoảng trắng, và dấu []
    text = re.sub(r'[^a-zA-ZÀ-ỹ0-9\s\[\]]', ' ', text)
    
    # Xóa khoảng trắng thừa
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

# ========== DEBUG FUNCTION ==========
def debug_emoticon_processing():
    """Debug quá trình xử lý emoticon"""
    print("\n" + "="*70)
    print("DEBUG EMOTICON PROCESSING (DUNG DAU CACH)")
    print("="*70)
    
    test_cases = [
        ("Tốt :)", "[cười nhẹ]"),
        ("Tốt :))", "[cười vừa]"),
        ("Tốt :)))", "[cười mạnh]"),
        ("Tốt :))))", "[rất cười]"),
        ("Tệ :(", "[buồn nhẹ]"),
        ("Tệ :((", "[buồn vừa]"),
        ("Tệ :(((", "[buồn mạnh]"),
        ("Tệ :((((", "[rất buồn]"),
        ("Yêu <3", "[tim nhẹ]"),
        ("Yêu <33", "[tim vừa]"),
        ("Yêu <333", "[tim mạnh]"),
        ("Vui :D", "[cười to nhẹ]"),
        ("Vui :DD", "[cười to vừa]"),
        ("Vui :DDD", "[cười to mạnh]"),
    ]
    
    for original, expected_tag in test_cases:
        cleaned = clean_text_with_intensity(original, None, 'balanced')
        
        if expected_tag in cleaned:
            status = "YES"
        else:
            status = "NO"
            tags = re.findall(r'\[(.*?)\]', cleaned)
            if tags:
                expected_tag = f" (found: {tags})"
            else:
                expected_tag = " (no tags found)"
        
        print(f"{status} '{original}' -> '{cleaned}'")

# ========== BALANCE DATASET FUNCTION ==========
def balance_dataset(df, method='undersample'):
    """Cân bằng dữ liệu"""
    if method == 'undersample':
        min_count = df['sentiment'].value_counts().min()
        balanced_dfs = []
        
        for sentiment in [0, 1, 2]:
            sentiment_df = df[df['sentiment'] == sentiment]
            sampled_df = sentiment_df.sample(n=min_count, random_state=42)
            balanced_dfs.append(sampled_df)
        
        result = pd.concat(balanced_dfs).sample(frac=1, random_state=42).reset_index(drop=True)
        print(f"Undersampled: {len(result)} samples")
        
    elif method == 'oversample':
        max_count = df['sentiment'].value_counts().max()
        balanced_dfs = []
        
        for sentiment in [0, 1, 2]:
            sentiment_df = df[df['sentiment'] == sentiment]
            sampled_df = sentiment_df.sample(n=max_count, replace=True, random_state=42)
            balanced_dfs.append(sampled_df)
        
        result = pd.concat(balanced_dfs).sample(frac=1, random_state=42).reset_index(drop=True)
        print(f"Oversampled: {len(result)} samples")
        
    else:
        result = df
        print(f"No balancing: {len(result)} samples")
    
    return result

# ========== ADD FEATURES FUNCTION ==========
def add_features(df, emoji_processor):
    """Thêm features với xử lý emoji và emoticon cường độ"""
    print("Them features...")
    
    # 1. Features cơ bản
    df['comment_length'] = df['cleaned_comments'].str.len()
    df['word_count'] = df['cleaned_comments'].apply(lambda x: len(str(x).split()))
    
    # 2. Features từ khóa TEXT
    positive_words = [
        'tốt', 'đẹp', 'tuyệt', 'hài lòng', 'thích', 'yêu', 
        'tuyệt vời', 'hoàn hảo', 'xuất sắc', 'chất lượng',
        'ưng', 'thú vị', 'ấn tượng', 'đáng giá', 'nên mua',
        'recommend', 'ủng hộ', 'mua lại', 'hài', 'vui'
    ]
    
    negative_words = [
        'tệ', 'kém', 'thất vọng', 'không nên', 'đừng', 'cẩn thận',
        'hỏng', 'lừa', 'không tốt', 'kém chất lượng', 'rẻ tiền',
        'dở', 'chán', 'tốn tiền', 'không hợp', 'khó chịu'
    ]
    
    neutral_words = [
        'bình thường', 'tàm tạm', 'trung bình', 'không có gì',
        'cũng được', 'cũng tạm', 'không sao', 'ổn', 'được',
        'chấp nhận', 'tạm', 'vừa', 'không đặc biệt'
    ]
    
    df['positive_word_count'] = df['cleaned_comments'].apply(
        lambda x: sum(1 for word in positive_words if word in str(x))
    )
    df['negative_word_count'] = df['cleaned_comments'].apply(
        lambda x: sum(1 for word in negative_words if word in str(x))
    )
    df['neutral_word_count'] = df['cleaned_comments'].apply(
        lambda x: sum(1 for word in neutral_words if word in str(x))
    )
    
    # 3. Features EMOTICON CƯỜNG ĐỘ
    df['smile_light'] = df['cleaned_comments'].apply(
        lambda x: str(x).count('[cười nhẹ]')
    )
    df['smile_medium'] = df['cleaned_comments'].apply(
        lambda x: str(x).count('[cười vừa]')
    )
    df['smile_strong'] = df['cleaned_comments'].apply(
        lambda x: str(x).count('[cười mạnh]') + str(x).count('[rất cười]')
    )
    
    df['sad_light'] = df['cleaned_comments'].apply(
        lambda x: str(x).count('[buồn nhẹ]')
    )
    df['sad_medium'] = df['cleaned_comments'].apply(
        lambda x: str(x).count('[buồn vừa]')
    )
    df['sad_strong'] = df['cleaned_comments'].apply(
        lambda x: str(x).count('[buồn mạnh]') + str(x).count('[rất buồn]')
    )
    
    df['heart_light'] = df['cleaned_comments'].apply(
        lambda x: str(x).count('[tim nhẹ]')
    )
    df['heart_medium'] = df['cleaned_comments'].apply(
        lambda x: str(x).count('[tim vừa]')
    )
    df['heart_strong'] = df['cleaned_comments'].apply(
        lambda x: str(x).count('[tim mạnh]')
    )
    
    df['emphasis_light'] = df['cleaned_comments'].apply(
        lambda x: str(x).count('[nhấn mạnh nhẹ]')
    )
    df['emphasis_medium'] = df['cleaned_comments'].apply(
        lambda x: str(x).count('[nhấn mạnh vừa]')
    )
    df['emphasis_strong'] = df['cleaned_comments'].apply(
        lambda x: str(x).count('[nhấn mạnh mạnh]')
    )
    
    # 4. Features EMOJI
    if emoji_processor:
        print("  Them features tu emoji analysis...")
        
        emoji_positive_counts = []
        emoji_negative_counts = []
        emoji_neutral_counts = []
        has_emoji_list = []
        emoji_sentiment_scores = []
        
        for comment in df['comments']:
            analysis = emoji_processor.analyze_text_emojis(str(comment))
            
            if analysis['has_emoji']:
                emoji_labels = [detail['label'] for detail in analysis['emoji_details']]
                label_counter = Counter(emoji_labels)
                
                emoji_positive_counts.append(label_counter.get(2, 0))
                emoji_negative_counts.append(label_counter.get(0, 0))
                emoji_neutral_counts.append(label_counter.get(1, 0))
                has_emoji_list.append(1)
                emoji_sentiment_scores.append(analysis['weighted_score'])
            else:
                emoji_positive_counts.append(0)
                emoji_negative_counts.append(0)
                emoji_neutral_counts.append(0)
                has_emoji_list.append(0)
                emoji_sentiment_scores.append(0.0)
        
        df['emoji_positive_count'] = emoji_positive_counts
        df['emoji_negative_count'] = emoji_negative_counts
        df['emoji_neutral_count'] = emoji_neutral_counts
        df['has_emoji'] = has_emoji_list
        df['emoji_sentiment_score'] = emoji_sentiment_scores
        
        print(f"  - Comments co emoji: {sum(has_emoji_list)}/{len(df)}")
    
    # 5. Features tổng hợp TEXT
    df['text_sentiment_score'] = df.apply(
        lambda row: (row['positive_word_count'] - row['negative_word_count']) / 
                   max(row['word_count'], 1),
        axis=1
    )
    
    # 6. Features tổng hợp EMOTICON CƯỜNG ĐỘ
    df['total_smile_intensity'] = (
        df['smile_light'] * 1 + 
        df['smile_medium'] * 2 + 
        df['smile_strong'] * 3 +
        df['heart_light'] * 1 +
        df['heart_medium'] * 2 +
        df['heart_strong'] * 3
    )
    
    df['total_sad_intensity'] = (
        df['sad_light'] * 1 + 
        df['sad_medium'] * 2 + 
        df['sad_strong'] * 3
    )
    
    df['emoticon_balance'] = df['total_smile_intensity'] - df['total_sad_intensity']
    
    # 7. Features mâu thuẫn cảm xúc
    df['has_mixed_sentiment'] = df.apply(
        lambda row: 1 if (row['positive_word_count'] > 0 and row['negative_word_count'] > 0) else 0,
        axis=1
    )
    
    df['has_mixed_emoticon'] = df.apply(
        lambda row: 1 if (row['total_smile_intensity'] > 0 and row['total_sad_intensity'] > 0) else 0,
        axis=1
    )
    
    print(f"YES Da them {len(df.columns) - 2} features")
    
    print(f"  - Comments co emoticon: {(df['total_smile_intensity'] + df['total_sad_intensity'] > 0).sum()}")
    print(f"  - Comments co emoticon manh: {(df['smile_strong'] + df['sad_strong'] + df['heart_strong'] > 0).sum()}")
    print(f"  - Comments co cam xuc hon hop: {df['has_mixed_sentiment'].sum()}")
    
    return df

# ========== MAIN PREPROCESSING FUNCTION ==========
def preprocess_and_save_data():
    """Hàm tiền xử lý dữ liệu và lưu ra file - TỐI ƯU"""
    print("=" * 70)
    print("TIEN XU LY DU LIEU VA LUU RA FILE - TOI UU")
    print("=" * 70)
    
    # Debug emoticon processing first
    debug_emoticon_processing()
    
    # 1. Khởi tạo emoji processor
    print("\n1. Khoi tao EmojiSentimentProcessor...")
    try:
        emoji_processor = EmojiSentimentProcessor('emoji_sentiment_labeled.csv', emoji_weight=0.25)
        print(f"   Loaded {len(emoji_processor.emoji_to_score)} emojis")
        print(f"   Emoji weight: {emoji_processor.emoji_weight}")
    except Exception as e:
        print(f"   Loi khi khoi tao emoji processor: {e}")
        emoji_processor = None
    
    # 2. Đọc dữ liệu comments
    print("\n2. Doc du lieu comments...")
    try:
        possible_paths = [
            'comments_text_labeled.csv',
            '../comments_text_labeled.csv',
            'data/comments_text_labeled.csv',
            'labeled_comments.csv'
        ]
        
        df = None
        for path in possible_paths:
            if os.path.exists(path):
                df = pd.read_csv(path)
                print(f"   YES Doc tu: {path}")
                break
        
        if df is None:
            print("   Khong tim thay file comments.")
            print("   Tao du lieu mau de test...")
            
            sample_data = {
                'comments': [
                    'Sản phẩm tốt :)',
                    'Rất tệ :(',
                    'Bình thường',
                    'Xuất sắc :)))',
                    'Thất vọng :(((',
                    'Ổn áp',
                    'Tuyệt vời <3',
                    'Không ổn :((((',
                    'Tạm được',
                    'Rất hài lòng :D'
                ],
                'sentiment': [2, 0, 1, 2, 0, 1, 2, 0, 1, 2]
            }
            
            df = pd.DataFrame(sample_data)
            print(f"   YES Tao du lieu mau: {len(df)} comments")
        
        print(f"   Tong so comments: {len(df)}")
        print(f"   Phan bo nhan:")
        sentiment_counts = df['sentiment'].value_counts().sort_index()
        for label, count in sentiment_counts.items():
            label_name = ['Tieu cuc', 'Trung tinh', 'Tich cuc'][label]
            percentage = count/len(df)*100
            print(f"     {label_name}: {count} ({percentage:.1f}%)")
        
    except Exception as e:
        print(f"   NO Loi doc file comments: {e}")
        return None, None
    
    # 3. Tiền xử lý với EMOTICON CƯỜNG ĐỘ
    print("\n3. Tien xu ly du lieu (voi emoticon cuong do - DAU CACH)...")
    df['cleaned_comments'] = df['comments'].apply(
        lambda x: clean_text_with_intensity(x, emoji_processor, mode='balanced')
    )
    
    # Loại bỏ comments rỗng
    before_len = len(df)
    df = df[df['cleaned_comments'].str.strip() != '']
    removed = before_len - len(df)
    print(f"   Loai bo {removed} comments rong")
    print(f"   Con lai: {len(df)} comments")
    
    # 4. Thêm features
    df = add_features(df, emoji_processor)
    
    # 5. Tách từ tiếng Việt
    print("\n4. Tach tu tieng Viet...")
    df['tokenized'] = df['cleaned_comments'].apply(
        lambda x: ' '.join(word_tokenize(x)) if x else ''
    )
    
    # 6. Cân bằng dữ liệu
    print("\n5. Can bang du lieu...")
    df_balanced = balance_dataset(df, method='undersample')
    print(f"   Phan bo sau can bang:")
    balanced_counts = df_balanced['sentiment'].value_counts().sort_index()
    for label, count in balanced_counts.items():
        label_name = ['Tieu cuc', 'Trung tinh', 'Tich cuc'][label]
        print(f"     {label_name}: {count}")
    
    # 7. Lưu dữ liệu đã tiền xử lý - CHỈ LƯU CỘT CẦN THIẾT
    print("\n6. Luu du lieu da tien xu ly...")
    
    # File 1: Dữ liệu tối giản cho training (chỉ 2 cột)
    model_columns = ['sentiment', 'tokenized']
    df_for_model = df_balanced[model_columns].copy()
    
    preprocessed_file = 'preprocessed_data_model.csv'
    df_for_model.to_csv(preprocessed_file, index=False, encoding='utf-8')
    
    # File 2: Mapping để tra cứu (tuỳ chọn)
    mapping_file = 'comments_mapping.csv'
    df_mapping = df_balanced[['comments', 'cleaned_comments', 'sentiment']].copy()
    df_mapping.to_csv(mapping_file, index=False, encoding='utf-8')
    
    # File 3: Thông tin features (tuỳ chọn)
    metadata_file = 'features_info.txt'
    with open(metadata_file, 'w', encoding='utf-8') as f:
        f.write("THONG TIN FEATURES DA XU LY\n")
        f.write("="*50 + "\n")
        f.write(f"Tong so mau: {len(df_balanced)}\n")
        f.write(f"Tong so features: {len(df_balanced.columns)}\n")
        f.write(f"Features quan trong:\n")
        
        emoticon_cols = [col for col in df_balanced.columns if any(x in col for x in ['smile', 'sad', 'heart', 'emphasis'])]
        for col in emoticon_cols[:10]:  # Chỉ lấy 10 cột đầu
            if col in df_balanced.columns:
                f.write(f"  - {col}: {df_balanced[col].sum()} instances\n")
    
    # Tính kích thước file
    file_size = os.path.getsize(preprocessed_file) / (1024*1024)  # MB
    
    print(f"   YES Da luu cac file:")
    print(f"   - {preprocessed_file}: {len(df_for_model)} mau, {len(df_for_model.columns)} cot ({file_size:.2f} MB)")
    print(f"   - {mapping_file}: Mapping comments goc -> da clean")
    print(f"   - {metadata_file}: Thong tin ve features")
    print(f"\n   CHI CAN SU DUNG FILE: {preprocessed_file} (2 cot: 'sentiment', 'tokenized')")
    
    return df_balanced, emoji_processor

# ========== RUN PREPROCESSING ==========
if __name__ == "__main__":
    preprocess_and_save_data()