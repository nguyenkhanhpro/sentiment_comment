# Sentiment Comment Analysis Project

## Mô tả dự án

Dự án phân tích cảm xúc từ bình luận sử dụng machine learning và emoji sentiment analysis. Hệ thống có khả năng huấn luyện mô del, tiền xử lý dữ liệu và triển khai ứng dụng web để phân tích cảm xúc real-time.

## Cấu trúc thư mục
``` bash
PROJECT A/
├── data/                          # Thư mục chứa dữ liệu
├── env/                           # Môi trường ảo Python
├── takeData/                      # Lấy dữ liệu
├── training/                      # Thư mục chính cho training và deployment
│   ├── test/                      # Dữ liệu và code test
│   ├── train/                     # Thư mục training chính
│   │   ├── app/                   # Ứng dụng web Flask
│   │   │   ├── static/            # Files tĩnh (CSS, JS)
│   │   │   │   ├── css/
│   │   │   │   │   └── style.css
│   │   │   │   └── js/
│   │   │   │       └── app.js
│   │   │   ├── templates/         # HTML templates
│   │   │   │   └── index.html
│   │   │   └── app.py             # Flask application
│   │   ├── emoji_processor.py     # Xử lý emoji
│   │   ├── model_config.txt       # Cấu hình model
│   │   ├── sentiment_model.pkl    # Model đã train
│   │   ├── tfidf_vectorizer.pkl   # TF-IDF vectorizer
│   ├── __init__.py
│   ├── comments_mapping.csv       # Data Mapping dữ liệu
│   ├── comments_text_labeled.csv  # Data Dữ liệu có nhãn
│   ├── comments.csv               # Data Dữ liệu bình luận
│   ├── emoji_processor.py         # Module xử lý emoji
│   ├── emoji_sentiment_labeled.csv # Data emoji có nhãn
│   ├── features_info.txt          # Thông tin features
│   ├── get_emoji_sentiment.py     # Lấy sentiment từ emoji
│   ├──main.py                        # File chạy chính
│   ├──model_test.py                  # Đánh nhãn comment
│   ├──model_trainer.py               # Huấn luyện model
│   ├──preprocessed_data_model.csv    # Data đã tiền xử lý
│   ├──preprocessor.py                # Module tiền xử lý dữ liệu
│   └──requirements.txt               # Dependencies
├── .gitignore                     # Git ignore file
├── a.py                           # Script phụ trợ
└── Project A.docx                 # Tài liệu dự án
```
## Các thành phần chính

### 1. Tiền xử lý dữ liệu

- `preprocessor.py`: Xử lý và làm sạch dữ liệu văn bản
- `emoji_processor.py`: Xử lý và phân tích emoji trong bình luận
- `get_emoji_sentiment.py`: Trích xuất sentiment từ emoji

### 2. Huấn luyện Model

- `model_trainer.py`: Script huấn luyện model machine learning
- `model_test.py`: Đánh nhãn comment
- `sentiment_model.pkl`: Model đã được huấn luyện
- `tfidf_vectorizer.pkl`: Vectorizer cho text features

### 3. Web Application

- `app.py`: Flask web server
- `index.html`: Giao diện người dùng
- `style.css`: Styling cho ứng dụng
- `app.js`: Logic frontend

### 4. Dữ liệu

- `comments.csv`: Dữ liệu bình luận
- `comments_text_labeled.csv`: Dữ liệu đã được gán nhãn
- `emoji_sentiment_labeled.csv`: Dữ liệu emoji và sentiment
- `preprocessed_data_model.csv`: Dữ liệu sau tiền xử lý

## Cài đặt

### Yêu cầu hệ thống

- Python 3.8+
- pip

### Các bước cài đặt

**1. Clone repository:**

```bash
git clone https://github.com/nguyenkhanhpro/sentiment_comment.git
cd "PROJECT A"
```

**2. Tạo môi trường ảo:**

```bash
python -m venv env
source env/bin/activate  # Linux/Mac
env\Scripts\activate     # Windows
```

**3. Cài đặt dependencies:**

```bash
pip install -r requirements.txt
```

## Sử dụng
### 1. Chạy Lấy dữ liệu với TakeData
- Đọc file README trong thư mục TakeData để lấy dữ liệu bình luận từ YouTube
### 2. Đánh nhãn dữ liệu đã lấy được từ TakeData
- Sử dụng file `model_test.py` để đánh nhãn dữ liệu bình luận đã lấy được
```bash
cd training/train/
python model_test.py
```
### 3. Lấy emoji sentiment và xử lí dữ liệu
- Dùng file `get_emoji_sentiment.py` để lấy sentiment từ emoji trên trang web và lưu vào file `emoji_sentiment_labeled.csv`
```bash
cd training/train/
python get_emoji_sentiment.py
```
- Sau đó dùng file emoji_processor.py để xử lí emoji trong bình luận
```bash
cd training/train/
python emoji_processor.py
```
### 4. Tiền xử lý dữ liệu và huấn luyện Model

```bash
cd training/train/
python main.py
```
- File main chạy chương trình bao gồm :
    - 1 là chạy tiền xử lí dữ liệu với file `preprocessor.py`
    - 2 là chạy models với file `model_trainer.py`
    - 3 là chạy đồng thời cả 2 bước trên
    - 4 là thoát chương trình
### 5. Chạy Web Application

```bash
cd training/train/app
python app.py
```

Truy cập: `http://localhost:5000`


## Features chính

- Phân tích sentiment từ văn bản tiếng Việt
- Xử lý và phân tích emoji
- Giao diện web thân thiện
- Model machine learning tùy chỉnh
- Tiền xử lý dữ liệu tự động
- Hỗ trợ phân loại nhiều mức độ sentiment

## Requirements

Các thư viện chính:

- Flask: Web framework
- scikit-learn: Machine learning
- pandas: Xử lý dữ liệu
- numpy: Tính toán số học
- pickle: Lưu trữ model

Xem đầy đủ trong `requirements.txt`

## Cấu hình

Cấu hình model được lưu trong `model_config.txt`. Có thể điều chỉnh:

- Hyperparameters
- Feature extraction settings
- Model selection

## Đóng góp

1. Fork project
2. Tạo branch mới (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## Tác giả

Nguyễn Khánh

## Ghi chú

- Đảm bảo có đủ dữ liệu training trước khi huấn luyện model
- Backup model và dữ liệu thường xuyên
- Kiểm tra version compatibility của các thư viện
- Sử dụng môi trường ảo để tránh conflict dependencies