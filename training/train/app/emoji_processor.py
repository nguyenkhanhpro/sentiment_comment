import emoji
import re
import pandas as pd
import numpy as np
from collections import Counter

class EmojiSentimentProcessor:
    def __init__(self, csv_path='emoji_sentiment_labeled.csv', emoji_weight=0.3):
        """
        Xử lý sentiment emoji dựa trên data crawl từ kt.ijs.si
        
        Parameters:
        - csv_path: file CSV với cột [emoji, sentiment_score, label]
        - emoji_weight: trọng số emoji trong phân tích tổng thể (0.0-1.0)
        """
        self.emoji_to_score = {}
        self.emoji_to_label = {}
        self.emoji_weight = emoji_weight
        self._load_data(csv_path)
    
    def _load_data(self, csv_path):
        """Tải dữ liệu emoji từ file CSV"""
        try:
            df = pd.read_csv(csv_path)
            print(f"✅ Đã tải {len(df)} emoji từ: {csv_path}")
            
            for _, row in df.iterrows():
                emoji_char = str(row['emoji']).strip()
                score = float(row['sentiment_score'])
                label = int(row['label'])
                
                # Lưu vào dict
                self.emoji_to_score[emoji_char] = score
                self.emoji_to_label[emoji_char] = label
                
                # Thêm variant selector nếu cần
                if len(emoji_char) == 1:
                    variant = emoji_char + '\ufe0f'
                    self.emoji_to_score[variant] = score
                    self.emoji_to_label[variant] = label
            
            print(f"📊 Tổng số emoji trong bộ nhớ: {len(self.emoji_to_score)}")
            
            # Thống kê
            label_counts = Counter(self.emoji_to_label.values())
            print("📈 Phân bố sentiment:")
            for label, count in label_counts.items():
                label_name = {0: 'Tiêu cực', 1: 'Trung tính', 2: 'Tích cực'}[label]
                print(f"  {label_name}: {count} emoji")
            
            # Tính điểm trung bình
            scores = list(self.emoji_to_score.values())
            print(f"  Điểm trung bình: {np.mean(scores):.3f} (min: {min(scores):.3f}, max: {max(scores):.3f})")
            print(f"  Trọng số emoji trong model: {self.emoji_weight}")
            
        except Exception as e:
            print(f"❌ Lỗi khi tải CSV: {e}")
            self.emoji_to_score = {}
            self.emoji_to_label = {}
    
    def get_emoji_info(self, emoji_char):
        """Lấy thông tin đầy đủ của emoji"""
        if emoji_char in self.emoji_to_score:
            score = self.emoji_to_score[emoji_char]
            label = self.emoji_to_label[emoji_char]
            return {
                'emoji': emoji_char,
                'score': score,
                'label': label,
                'label_name': {0: 'negative', 1: 'neutral', 2: 'positive'}[label]
            }
        
        # Thử tìm variant
        if len(emoji_char) > 1 and emoji_char[-1] == '\ufe0f':
            base_char = emoji_char[0]
            if base_char in self.emoji_to_score:
                score = self.emoji_to_score[base_char]
                label = self.emoji_to_label[base_char]
                return {
                    'emoji': base_char,
                    'score': score,
                    'label': label,
                    'label_name': {0: 'negative', 1: 'neutral', 2: 'positive'}[label]
                }
        
        return None
    
    def get_sentiment_score(self, emoji_char):
        """Lấy sentiment score (-1 đến +1)"""
        info = self.get_emoji_info(emoji_char)
        return info['score'] if info else 0.0
    
    def get_sentiment_label(self, emoji_char):
        """Lấy sentiment label (0, 1, 2)"""
        info = self.get_emoji_info(emoji_char)
        return info['label'] if info else 1  # Mặc định trung tính
    
    def get_intensity_category(self, emoji_char):
        """
        Phân loại cường độ cảm xúc dựa trên sentiment score
        Trả về: (category, description, weight)
        """
        score = self.get_sentiment_score(emoji_char)
        
        # Phân loại theo ngưỡng từ research paper
        if score > 0.6:
            return ('very_positive', 'rất_tích_cực', 0.9)
        elif score > 0.3:
            return ('positive', 'tích_cực', 0.7)
        elif score > 0.1:
            return ('slightly_positive', 'hơi_tích_cực', 0.4)
        elif score < -0.6:
            return ('very_negative', 'rất_tiêu_cực', 0.9)
        elif score < -0.3:
            return ('negative', 'tiêu_cực', 0.7)
        elif score < -0.1:
            return ('slightly_negative', 'hơi_tiêu_cực', 0.4)
        else:
            return ('neutral', 'trung_tính', 0.1)
    
    def analyze_text_emojis(self, text):
        """
        Phân tích tất cả emoji trong text
        Trả về kết quả tổng hợp với trọng số
        """
        if not isinstance(text, str):
            return {
                'has_emoji': False,
                'emoji_count': 0,
                'weighted_score': 0.0,
                'dominant_label': 1,
                'dominant_label_name': 'neutral',
                'intensity': 'neutral',
                'emoji_details': []
            }
        
        emoji_details = []
        total_weight = 0.0
        weighted_score_sum = 0.0
        label_votes = []
        
        # Tìm và phân tích từng emoji
        for char in text:
            if emoji.is_emoji(char):
                info = self.get_emoji_info(char)
                if info:
                    category, description, weight = self.get_intensity_category(char)
                    
                    emoji_details.append({
                        'emoji': char,
                        'score': info['score'],
                        'label': info['label'],
                        'category': category,
                        'description': description,
                        'weight': weight
                    })
                    
                    # Tính điểm có trọng số
                    weighted_score_sum += info['score'] * weight
                    total_weight += weight
                    label_votes.append(info['label'])
        
        if not emoji_details:
            return {
                'has_emoji': False,
                'emoji_count': 0,
                'weighted_score': 0.0,
                'dominant_label': 1,
                'dominant_label_name': 'neutral',
                'intensity': 'neutral',
                'emoji_details': []
            }
        
        # Tính điểm trung bình có trọng số
        weighted_score = weighted_score_sum / total_weight if total_weight > 0 else 0.0
        
        # Xác định label phổ biến nhất
        if label_votes:
            label_counter = Counter(label_votes)
            dominant_label = label_counter.most_common(1)[0][0]
        else:
            dominant_label = 1  # neutral
        
        # Xác định cường độ tổng
        if weighted_score > 0.5:
            intensity = 'very_positive'
        elif weighted_score > 0.2:
            intensity = 'positive'
        elif weighted_score < -0.5:
            intensity = 'very_negative'
        elif weighted_score < -0.2:
            intensity = 'negative'
        else:
            intensity = 'neutral'
        
        label_names = {0: 'negative', 1: 'neutral', 2: 'positive'}
        
        return {
            'has_emoji': True,
            'emoji_count': len(emoji_details),
            'weighted_score': weighted_score,
            'dominant_label': dominant_label,
            'dominant_label_name': label_names[dominant_label],
            'intensity': intensity,
            'emoji_details': emoji_details,
            'total_weight': total_weight
        }
    
    def process_text(self, text, mode='balanced'):
        """
        Xử lý text với emoji sentiment
        
        mode:
        - 'balanced': Giữ emoji + thêm tag nhẹ (recommended)
        - 'tag_only': Thay emoji bằng tag
        - 'keep_emoji': Chỉ giữ emoji
        - 'remove': Xóa emoji
        """
        if not isinstance(text, str):
            return ""
        
        if mode == 'remove':
            return ''.join(char for char in text if not emoji.is_emoji(char))
        
        if mode == 'keep_emoji':
            return text
        
        processed_chars = []
        emoji_count = 0
        emoji_scores = []
        
        for char in text:
            if emoji.is_emoji(char):
                emoji_count += 1
                score = self.get_sentiment_score(char)
                emoji_scores.append(score)
                
                if mode == 'tag_only':
                    # Thay thế emoji bằng tag
                    category, description, _ = self.get_intensity_category(char)
                    if category in ['very_positive', 'positive']:
                        processed_chars.append(' [pos_emoji] ')
                    elif category in ['very_negative', 'negative']:
                        processed_chars.append(' [neg_emoji] ')
                    elif category == 'slightly_positive':
                        processed_chars.append(' [weak_pos_emoji] ')
                    elif category == 'slightly_negative':
                        processed_chars.append(' [weak_neg_emoji] ')
                    else:
                        processed_chars.append(' [neu_emoji] ')
                
                elif mode == 'balanced':
                    # GIỮ NGUYÊN EMOJI, thêm tag nếu cần
                    processed_chars.append(char)
                    category, description, weight = self.get_intensity_category(char)
                    
                    # Chỉ thêm tag cho emoji có cường độ trung bình trở lên
                    if weight >= 0.7:  # positive/negative mạnh
                        processed_chars.append(f' [{description}] ')
                    elif weight >= 0.4 and emoji_count <= 3:  # Giới hạn số tag
                        processed_chars.append(f' [{description}] ')
            
            else:
                processed_chars.append(char)
        
        # Thêm tag tổng hợp nếu có nhiều emoji
        if emoji_count >= 2 and mode == 'balanced':
            if emoji_scores:
                avg_score = sum(emoji_scores) / len(emoji_scores)
                if avg_score > 0.3:
                    processed_chars.append(' [nhiều_emoji_tích_cực] ')
                elif avg_score < -0.2:
                    processed_chars.append(' [nhiều_emoji_tiêu_cực] ')
        
        # Ghép lại và làm sạch
        result = ''.join(processed_chars)
        result = re.sub(r'\s+', ' ', result).strip()
        
        return result
    
    def combine_text_and_emoji_sentiment(self, text, text_sentiment_score=0.0):
        """
        Kết hợp sentiment từ text và emoji với trọng số
        
        Parameters:
        - text: văn bản cần phân tích
        - text_sentiment_score: điểm sentiment từ text (-1 đến +1)
        
        Returns:
        - final_score: điểm tổng hợp (-1 đến +1)
        - final_label: nhãn tổng hợp (0, 1, 2)
        - confidence: độ tin cậy
        """
        # Phân tích emoji trong text
        emoji_analysis = self.analyze_text_emojis(text)
        
        if not emoji_analysis['has_emoji']:
            # Không có emoji, dùng sentiment từ text
            final_score = text_sentiment_score
        else:
            # Kết hợp với trọng số
            emoji_score = emoji_analysis['weighted_score']
            final_score = (text_sentiment_score * (1 - self.emoji_weight) + 
                         emoji_score * self.emoji_weight)
        
        # Chuyển score thành label
        if final_score > 0.2:
            final_label = 2  # positive
        elif final_score < -0.2:
            final_label = 0  # negative
        else:
            final_label = 1  # neutral
        
        # Tính confidence
        confidence = min(abs(final_score) * 2, 1.0)
        
        return {
            'final_score': final_score,
            'final_label': final_label,
            'final_label_name': {0: 'negative', 1: 'neutral', 2: 'positive'}[final_label],
            'confidence': confidence,
            'text_score': text_sentiment_score,
            'emoji_score': emoji_analysis['weighted_score'] if emoji_analysis['has_emoji'] else 0.0,
            'emoji_count': emoji_analysis['emoji_count'],
            'emoji_weight': self.emoji_weight
        }


# Test với dữ liệu thực
if __name__ == "__main__":
    print("=" * 70)
    print("EMOJI SENTIMENT PROCESSOR - KT.IJS.SI VERSION")
    print("=" * 70)
    
    # Khởi tạo processor
    processor = EmojiSentimentProcessor('emoji_sentiment_labeled.csv', emoji_weight=0.3)
    
    # Test với các emoji cụ thể từ data của bạn
    print("\n📊 Test các emoji từ file:")
    test_emojis = [
        ('😂', 0.221, 2),   # positive
        ('❤', 0.746, 2),    # very positive
        ('😍', 0.678, 2),   # very positive
        ('😭', -0.093, 0),  # slightly negative
        ('😊', 0.644, 2),   # very positive
        ('👌', 0.563, 2),   # positive
        ('😩', -0.368, 0),  # negative
        ('😘', 0.701, 2),   # very positive
    ]
    
    for emoji_char, expected_score, expected_label in test_emojis:
        score = processor.get_sentiment_score(emoji_char)
        label = processor.get_sentiment_label(emoji_char)
        category, description, weight = processor.get_intensity_category(emoji_char)
        
        print(f"{emoji_char}: score={score:.3f} (expected {expected_score:.3f}), "
              f"label={label} (expected {expected_label}), "
              f"category={category} ({description}), weight={weight}")
    
    # Test với comments thực tế
    print("\n🧪 Test với comments:")
    test_comments = [
        ("Sản phẩm tốt lắm! 😍❤️", 0.8),  # positive text + very positive emoji
        ("Rất thất vọng 😭", -0.6),       # negative text + slightly negative emoji
        ("Bình thường 😐", 0.0),          # neutral text + ? emoji
        ("Chất lượng ok, giao hàng chậm 😊😔", 0.1),  # mixed
        ("Tuyệt vời!!! 👏👍🎉", 0.9),      # very positive text + positive emoji
        ("Tệ 😡", -0.7),                  # very negative text + negative emoji
    ]
    
    for comment, text_score in test_comments:
        print(f"\n{'='*50}")
        print(f"Comment: {comment}")
        print(f"Text sentiment score: {text_score:.2f}")
        
        # Phân tích emoji
        emoji_analysis = processor.analyze_text_emojis(comment)
        if emoji_analysis['has_emoji']:
            print(f"Emoji analysis: {emoji_analysis['emoji_count']} emoji, "
                  f"weighted score: {emoji_analysis['weighted_score']:.3f}, "
                  f"dominant: {emoji_analysis['dominant_label_name']}")
        
        # Kết hợp text và emoji
        combined = processor.combine_text_and_emoji_sentiment(comment, text_score)
        print(f"Combined result: score={combined['final_score']:.3f}, "
              f"label={combined['final_label_name']}, confidence={combined['confidence']:.2f}")
        
        # Xử lý text
        print(f"Processed (balanced): {processor.process_text(comment, 'balanced')}")