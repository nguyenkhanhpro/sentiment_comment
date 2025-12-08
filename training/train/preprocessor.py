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
        'j': 'gì',
        'a': 'anh',
        'e': 'em',
        'hj': 'hihi',
        'c': 'chị',
        'z': 'vậy',
    }
    
    for old, new in teen_code.items():
        text = re.sub(r'\b' + old + r'\b', new, text)
    
    # Xóa URL và email
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\S+@\S+', '', text)
    
    # Xóa emoticon tim <3 và các biến thể
    text = re.sub(r'<3+', '', text)
    
    # Xóa emoticon cười lớn :D và các biến thể
    text = re.sub(r':-?d+', '', text, flags=re.IGNORECASE)
    
    # Xóa emoticon cười :) và các biến thể
    text = re.sub(r':-?\)+', '', text)
    
    # Xóa emoticon buồn :( và các biến thể
    text = re.sub(r':-?\(+', '', text)
    
    # Xóa dấu chấm than lặp (giữ lại 1)
    text = re.sub(r'!+', '!', text)
    
    # Xóa dấu hỏi lặp (giữ lại 1)
    text = re.sub(r'\?+', '?', text)
    
    # Chuẩn hóa từ lặp
    text = re.sub(r'(.)\1{3,}', r'\1\1\1', text)
    

    # Xóa ký tự đặc biệt nhưng giữ emoji
    # Dùng cách tiếp cận: giữ mọi thứ trừ các ký tự đặc biệt cụ thể
    import unicodedata
    
    # Tạo list ký tự hợp lệ
    cleaned_chars = []
    for char in text:
        # Giữ: chữ, số, khoảng trắng
        if char.isalnum() or char.isspace():
            cleaned_chars.append(char)
        # Giữ: dấu câu cơ bản
        elif char in '.,!?':
            cleaned_chars.append(char)
        # Giữ: emoji (các ký tự có tên chứa "EMOJI" hoặc thuộc phạm vi emoji)
        elif unicodedata.category(char) in ['So']:  # Symbol, Other (bao gồm emoji)
            cleaned_chars.append(char)
        # Giữ: ký tự có mã Unicode cao (thường là emoji)
        elif ord(char) > 0x1000:  # Giữ các ký tự Unicode mở rộng
            cleaned_chars.append(char)
        # Các ký tự khác: thay bằng khoảng trắng
        else:
            cleaned_chars.append(' ')
    
    text = ''.join(cleaned_chars)
    
    # Xóa khoảng trắng thừa
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def debug_emoticon_processing():
    print("DEBUG EMOTICON PROCESSING (DA XOA EMOTICON, GIU EMOJI)")
    
    test_cases = [
        ("Tốt :)", "tốt"),
        ("Tốt :))", "tốt"),
        ("Tệ :(", "tệ"),
        ("Yêu <3", "yêu"),
        ("Vui :D", "vui"),
        ("Sản phẩm tốt!!!", "sản phẩm tốt"),
        ("Rất tệ???", "rất tệ"),
        ("Tốt 😊", "tốt 😊"),
        ("Tuyệt vời 👍", "tuyệt vời 👍"),
        ("Thất vọng 😔", "thất vọng 😔"),
    ]
    
    for original, expected in test_cases:
        cleaned = clean_text_with_intensity(original, None, 'balanced')
        cleaned_simple = re.sub(r'\s+', ' ', cleaned).strip()
        
        if cleaned_simple == expected:
            status = "YES"
        else:
            status = "NO"
        
        print(f"{status} '{original}' -> '{cleaned_simple}' (expected: '{expected}')")

def balance_dataset(df, method='undersample'):
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

def add_features(df, emoji_processor):
    print("Them features...")
    
    df['comment_length'] = df['cleaned_comments'].str.len()
    df['word_count'] = df['cleaned_comments'].apply(lambda x: len(str(x).split()))
    
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
    
    print(f"Da them {len(df.columns) - 2} features")
    
    return df

def preprocess_and_save_data():
    print("TIEN XU LY DU LIEU VA LUU RA FILE")
    
    debug_emoticon_processing()
    
    print("\n1. Khoi tao EmojiSentimentProcessor...")
    try:
        emoji_processor = EmojiSentimentProcessor('emoji_sentiment_labeled.csv', emoji_weight=0.25)
        print(f" Loaded {len(emoji_processor.emoji_to_score)} emojis")
        print(f" Emoji weight: {emoji_processor.emoji_weight}")
    except Exception as e:
        print(f" Loi khi khoi tao emoji processor: {e}")
        emoji_processor = None
    
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
                print(f" Doc tu: {path}")
                break
        
        if df is None:
            print("  Khong tim thay file comments.")
            print("  Tao du lieu mau de test...")
            
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
    
    print("\n3. Tien xu ly du lieu (giu emoji)...")
    df['cleaned_comments'] = df['comments'].apply(
        lambda x: clean_text_with_intensity(x, emoji_processor, mode='balanced')
    )
    
    before_len = len(df)
    df = df[df['cleaned_comments'].str.strip() != '']
    removed = before_len - len(df)
    print(f"   Loai bo {removed} comments rong")
    print(f"   Con lai: {len(df)} comments")
    
    df = add_features(df, emoji_processor)
    
    print("\n4. Tach tu tieng Viet...")
    df['tokenized'] = df['cleaned_comments'].apply(
        lambda x: ' '.join(word_tokenize(x)) if x else ''
    )
    
    print("\n5. Can bang du lieu...")
    df_balanced = balance_dataset(df, method='undersample')
    print(f"   Phan bo sau can bang:")
    balanced_counts = df_balanced['sentiment'].value_counts().sort_index()
    for label, count in balanced_counts.items():
        label_name = ['Tieu cuc', 'Trung tinh', 'Tich cuc'][label]
        print(f"     {label_name}: {count}")
    
    print("\n6. Luu du lieu da tien xu ly...")
    
    model_columns = ['sentiment', 'cleaned_comments']
    df_for_model = df_balanced[model_columns].copy()
    
    df_for_model = df_for_model.rename(columns={'cleaned_comments': 'comments'})
    
    preprocessed_file = 'preprocessed_data_model.csv'
    df_for_model.to_csv(preprocessed_file, index=False, encoding='utf-8')
    
    mapping_file = 'comments_mapping.csv'
    df_mapping = df_balanced[['comments', 'cleaned_comments', 'sentiment']].copy()
    df_mapping.to_csv(mapping_file, index=False, encoding='utf-8')
    
    file_size = os.path.getsize(preprocessed_file) / (1024*1024) 
    
    print(f"\n7. Kiem tra mau du lieu da luu:")
    print(f" File: {preprocessed_file}")
    print(f" So dong: {len(df_for_model)}, So cot: {len(df_for_model.columns)}")
    print(f" Kich thuoc: {file_size:.2f} MB")
    
    print(f"\n Mau 5 dong dau:")
    for i, row in df_for_model.head(5).iterrows():
        sentiment_label = ['Tieu cuc', 'Trung tinh', 'Tich cuc'][row['sentiment']]
        comment_preview = row['comments'][:50] + "..." if len(row['comments']) > 50 else row['comments']
        print(f" [{i}] Sentiment: {row['sentiment']} ({sentiment_label})")
        print(f" Comment: '{comment_preview}'")
    
    print(f"\n   So sanh voi du lieu goc (mau 3 dong):")
    for i in range(min(3, len(df_balanced))):
        original = df_balanced.iloc[i]['comments']
        cleaned = df_balanced.iloc[i]['cleaned_comments']
        sentiment = df_balanced.iloc[i]['sentiment']
        
        print(f"     [{i}] Sentiment: {sentiment}")
        print(f"         Goc: '{original[:50]}...'")
        print(f"         Clean: '{cleaned[:50]}...'")
    
    print(f"\nDa luu cac file:")
    print(f" - {preprocessed_file}: {len(df_for_model)} mau, {len(df_for_model.columns)} cot")
    print(f" - {mapping_file}: Mapping comments goc da clean")
    print(f"\n  QUAN TRONG: File {preprocessed_file} chua COMMENTS DA DUOC CLEAN (GIU EMOJI)")
    
    return df_balanced, emoji_processor

if __name__ == "__main__":
    preprocess_and_save_data()