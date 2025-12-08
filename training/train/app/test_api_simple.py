import requests
import json
import time

# Cấu hình
BASE_URL = "http://localhost:5000"
TEST_TEXTS = [
    "Sản phẩm tuyệt vời",
    "Sản phẩm tuyệt vời 😂",
    "Sản phẩm tuyệt vời 😂😂😂",
    "Sản phẩm tệ",
    "Sản phẩm tệ 😭",
    "Sản phẩm tệ 😭😭😭",
    "Sản phẩm bình thường",
    "Sản phẩm bình thường 😐",
    "Tuyệt vời quá! ❤️❤️❤️",
    "Tệ quá đi! 😡😡😡",
    "Ok, được 😊",
    "Không biết nói gì hơn... 🤔",
    "Chán quá 😒",
    "Quá hay! 👏👏👏",
    "Quá tốt luôn! 👍👍👍",
    "Tệ hại thật sự! 👎👎👎",
    "Đẹp quá 😍😍😍",
    "Buồn quá 😢😢😢",
    "Vui quá 🥳🥳🥳",
    "Sợ quá 😨😨😨",
    "Giận quá! 😠😠😠",
    "Ngạc nhiên quá! 😲😲😲",
    "Mệt quá 😫😫😫",
    "Yêu thích quá! 🥰🥰🥰",
]

def test_health():
    """Test endpoint health"""
    print("=" * 70)
    print("TEST HEALTH CHECK")
    print("=" * 70)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Health check passed")
            print(f"  Model loaded: {data.get('model_loaded', False)}")
            print(f"  Vectorizer loaded: {data.get('vectorizer_loaded', False)}")
            print(f"  Emoji processor loaded: {data.get('emoji_processor_loaded', False)}")
            print(f"  Status: {data.get('status', 'unknown')}")
            
            # Print model info
            if 'model_info' in data:
                print("\nModel Info:")
                for key, value in data['model_info'].items():
                    print(f"  {key}: {value}")
            return True
        else:
            print(f"✗ Health check failed with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to server. Make sure server is running!")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_predict_single(text, expected_sentiment=None):
    """Test predict với một text"""
    print(f"\n{'='*60}")
    print(f"TEST PREDICT: '{text[:50]}{'...' if len(text) > 50 else ''}'")
    print(f"{'='*60}")
    
    try:
        payload = {"text": text}
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/predict", 
                                json=payload, 
                                headers={"Content-Type": "application/json"},
                                timeout=10)
        elapsed_time = (time.time() - start_time) * 1000
        
        print(f"Response Time: {elapsed_time:.1f}ms")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                print(f"✓ Success: {data.get('success')}")
                print(f"  Sentiment: {data.get('sentiment')} ({data.get('label')})")
                print(f"  Confidence: {data.get('confidence')}%")
                print(f"  Processing Time: {data.get('processing_time_ms')}ms")
                
                # Emoji info
                emoji_count = data.get('emoji_count', 0)
                if emoji_count > 0:
                    print(f"  Emoji Count: {emoji_count}")
                    print(f"  Emoji Score: {data.get('emoji_score', 0):.3f}")
                    print(f"  Emoji Intensity: {data.get('emoji_intensity', 0):.3f}")
                    print(f"  Has Emoji Effect: {data.get('has_emoji_effect', False)}")
                
                # Probabilities
                if 'probabilities_formatted' in data:
                    print(f"\n  Probabilities (adjusted with emoji):")
                    for label, prob in data['probabilities_formatted'].items():
                        print(f"    {label}: {prob}")
                
                if 'original_probabilities' in data:
                    print(f"\n  Original Probabilities (text only):")
                    orig = data['original_probabilities']
                    print(f"    Tiêu cực: {orig.get('negative', 0):.1f}%")
                    print(f"    Trung tính: {orig.get('neutral', 0):.1f}%")
                    print(f"    Tích cực: {orig.get('positive', 0):.1f}%")
                
                # Text vs Combined score
                print(f"\n  Scores:")
                print(f"    Text Score: {data.get('text_sentiment_score', 0):.3f}")
                print(f"    Combined Score: {data.get('combined_score', 0):.3f}")
                print(f"    Text Prediction: {data.get('text_prediction')} ({data.get('text_label')})")
                print(f"    Final Prediction: {data.get('sentiment')} ({data.get('label')})")
                
                # Emoji details
                if 'emoji_details' in data and data['emoji_details']:
                    print(f"\n  Emoji Details:")
                    for i, emoji_detail in enumerate(data['emoji_details'][:3]):  # Hiển thị 3 emoji đầu
                        print(f"    {i+1}. {emoji_detail.get('emoji')} - "
                              f"Score: {emoji_detail.get('score', 0):.3f}, "
                              f"Label: {emoji_detail.get('label_name', 'Unknown')}")
                    if len(data['emoji_details']) > 3:
                        print(f"    ... and {len(data['emoji_details']) - 3} more")
                
                # Check if emoji changed the result
                if data.get('has_emoji_effect'):
                    print(f"\n  ⚠️  EMOJI CHANGED THE RESULT!")
                    print(f"     Text-only would be: {data.get('text_prediction')} ({data.get('text_label')})")
                    print(f"     With emoji it is: {data.get('sentiment')} ({data.get('label')})")
                
                # Check with expected
                if expected_sentiment is not None:
                    if data.get('sentiment') == expected_sentiment:
                        print(f"\n  ✅ PREDICTION MATCHES EXPECTED!")
                    else:
                        print(f"\n  ❌ PREDICTION DOES NOT MATCH EXPECTED!")
                        print(f"     Expected: {expected_sentiment}")
                        print(f"     Got: {data.get('sentiment')}")
                
                return data
            else:
                print(f"✗ Failed: {data.get('error', 'Unknown error')}")
                return None
        else:
            print(f"✗ Request failed with status: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_batch():
    """Test hàng loạt các văn bản"""
    print("\n" + "=" * 70)
    print("BATCH TEST - MULTIPLE TEXTS")
    print("=" * 70)
    
    results = []
    for i, text in enumerate(TEST_TEXTS, 1):
        print(f"\n[{i}/{len(TEST_TEXTS)}] Testing: '{text}'")
        
        result = test_predict_single(text)
        if result:
            results.append({
                'text': text,
                'sentiment': result.get('sentiment'),
                'label': result.get('label'),
                'confidence': result.get('confidence'),
                'emoji_count': result.get('emoji_count', 0),
                'emoji_effect': result.get('has_emoji_effect', False)
            })
        
        # Pause a bit between requests
        time.sleep(0.5)
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    positive_count = sum(1 for r in results if r.get('sentiment') == 2)
    neutral_count = sum(1 for r in results if r.get('sentiment') == 1)
    negative_count = sum(1 for r in results if r.get('sentiment') == 0)
    
    print(f"Total tests: {len(results)}")
    print(f"Positive: {positive_count} ({positive_count/len(results)*100:.1f}%)")
    print(f"Neutral: {neutral_count} ({neutral_count/len(results)*100:.1f}%)")
    print(f"Negative: {negative_count} ({negative_count/len(results)*100:.1f}%)")
    
    # Texts with emoji effect
    emoji_effect_texts = [r for r in results if r.get('emoji_effect')]
    print(f"\nTexts where emoji changed result: {len(emoji_effect_texts)}")
    for r in emoji_effect_texts[:5]:  # Show first 5
        print(f"  - '{r['text'][:30]}...' -> {r['label']}")
    
    return results

def test_edge_cases():
    """Test các trường hợp đặc biệt"""
    print("\n" + "=" * 70)
    print("EDGE CASE TESTS")
    print("=" * 70)
    
    edge_cases = [
        ("", False),  # Empty text
        ("   ", False),  # Whitespace only
        ("a" * 1000, True),  # Very long text
        ("1234567890", True),  # Numbers only
        ("!@#$%^&*()", True),  # Special characters only
        ("😂😂😂😂😂", True),  # Emoji only
        ("😊😡😢😂", True),  # Mixed emoji only
        ("Hello " * 50, True),  # Repetitive text
    ]
    
    for text, expect_success in edge_cases:
        print(f"\nTesting edge case: '{text[:30]}{'...' if len(text) > 30 else ''}'")
        result = test_predict_single(text)
        
        if expect_success:
            if result and result.get('success'):
                print(" Passed as expected")
            else:
                print(" Failed but should have succeeded")
        else:
            if not result or not result.get('success'):
                print(" Failed as expected")
            else:
                print(" Succeeded but should have failed")

def test_specific_scenarios():
    """Test các kịch bản cụ thể để debug probabilities"""
    print("\n" + "=" * 70)
    print("SPECIFIC SCENARIO TESTS - DEBUG PROBABILITIES")
    print("=" * 70)
    
    scenarios = [
        ("Sản phẩm tốt nhưng không tuyệt vời", "Mixed"),
        ("Sản phẩm tốt nhưng không tuyệt vời 😊", "Mixed with positive emoji"),
        ("Sản phẩm tốt nhưng không tuyệt vời 😡", "Mixed with negative emoji"),
        ("Sản phẩm ok", "Neutral"),
        ("Sản phẩm ok 👍", "Neutral with positive emoji"),
        ("Sản phẩm ok 👎", "Neutral with negative emoji"),
        ("Tệ", "Negative"),
        ("Tệ 😊", "Negative with positive emoji (conflict)"),
        ("Tốt 😡", "Positive with negative emoji (conflict)"),
    ]
    
    for text, description in scenarios:
        print(f"\nScenario: {description}")
        print(f"Text: '{text}'")
        test_predict_single(text)
        time.sleep(0.3)

def interactive_test():
    """Chế độ test tương tác"""
    print("\n" + "=" * 70)
    print("INTERACTIVE TEST MODE")
    print("=" * 70)
    print("Nhập 'quit' để thoát, 'stats' để xem thống kê")
    print("-" * 70)
    
    stats = {'total': 0, 'positive': 0, 'neutral': 0, 'negative': 0}
    
    while True:
        text = input("\nNhập văn bản để phân tích: ").strip()
        
        if text.lower() == 'quit':
            break
        elif text.lower() == 'stats':
            print(f"\nThống kê phiên làm việc:")
            print(f"  Total: {stats['total']}")
            print(f"  Positive: {stats['positive']} ({stats['positive']/stats['total']*100 if stats['total'] > 0 else 0:.1f}%)")
            print(f"  Neutral: {stats['neutral']} ({stats['neutral']/stats['total']*100 if stats['total'] > 0 else 0:.1f}%)")
            print(f"  Negative: {stats['negative']} ({stats['negative']/stats['total']*100 if stats['total'] > 0 else 0:.1f}%)")
            continue
        elif not text:
            print("Vui lòng nhập văn bản!")
            continue
        
        result = test_predict_single(text)
        if result and result.get('success'):
            stats['total'] += 1
            sentiment = result.get('sentiment')
            if sentiment == 2:
                stats['positive'] += 1
            elif sentiment == 1:
                stats['neutral'] += 1
            elif sentiment == 0:
                stats['negative'] += 1
    
    print("\nKết thúc phiên test tương tác!")

def main():
    """Hàm chính chạy tất cả các test"""
    print("SENTIMENT ANALYSIS BACKEND TEST SUITE")
    print("=" * 70)
    
    # 1. Kiểm tra server
    if not test_health():
        print("\n Không thể kết nối đến server!")
        print("Vui lòng chạy server trước với: python app.py")
        return
    
    # 2. Chọn chế độ test
    print("\nChọn chế độ test:")
    print("1. Test đơn lẻ")
    print("2. Test hàng loạt")
    print("3. Test trường hợp đặc biệt")
    print("4. Test kịch bản cụ thể (debug probabilities)")
    print("5. Test tương tác")
    print("6. Tất cả các test")
    
    choice = input("\nNhập lựa chọn (1-6): ").strip()
    
    if choice == '1':
        text = input("Nhập văn bản để test: ")
        test_predict_single(text)
    elif choice == '2':
        test_batch()
    elif choice == '3':
        test_edge_cases()
    elif choice == '4':
        test_specific_scenarios()
    elif choice == '5':
        interactive_test()
    elif choice == '6':
        # Run all tests
        test_batch()
        test_edge_cases()
        test_specific_scenarios()
        interactive_test()
    else:
        print("Lựa chọn không hợp lệ!")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETED!")
    print("=" * 70)

if __name__ == "__main__":
    main()