import joblib

try:
    model = joblib.load('sentiment_model.pkl')
    print(" Model loaded:", type(model))
    
    vectorizer = joblib.load('tfidf_vectorizer.pkl')
    print(" Vectorizer loaded:", type(vectorizer))
    
    print("\nCẢ HAI FILE ĐỀU LOAD ĐƯỢC!")
    
except Exception as e:
    print(f"LỖI: {e}")
    import traceback
    traceback.print_exc()


