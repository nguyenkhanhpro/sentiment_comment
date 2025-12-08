import sys
import os

# Thêm thư mục hiện tại vào path để import các module trong cùng folder
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

def show_menu():
    """Hiển thị menu"""
    print("\n" + "=" * 70)
    print("PHAN TICH CAM XUC")
    print("=" * 70)
    
    print("\nChon chuc nang:")
    print("1. Tien xu ly du lieu")
    print("2. Huan luyen model tu du lieu da tien xu ly")
    print("3. Chay toan bo (tien xu ly + huan luyen)")
    print("4. Thoat")

def run_preprocessing():
    """Chạy tiền xử lý dữ liệu"""
    try:
        from preprocessor import preprocess_and_save_data
        print("\n" + "=" * 70)
        print("BAT DAU TIEN XU LY DU LIEU")
        print("=" * 70)
        preprocess_and_save_data()
    except Exception as e:
        print(f"Loi khi chay tien xu ly: {e}")

def run_training():
    """Chạy huấn luyện model"""
    try:
        from model_trainer import train_model_from_preprocessed_data
        print("\n" + "=" * 70)
        print("BAT DAU HUAN LUYEN MODEL")
        print("=" * 70)
        train_model_from_preprocessed_data()
    except Exception as e:
        print(f"Loi khi chay huan luyen: {e}")

def run_full_pipeline():
    """Chạy toàn bộ pipeline"""
    try:
        from preprocessor import preprocess_and_save_data
        from model_trainer import train_model_from_preprocessed_data
        
        # Tiền xử lý
        print("\n" + "=" * 70)
        print("BAT DAU TIEN XU LY DU LIEU")
        print("=" * 70)
        df_balanced, emoji_processor = preprocess_and_save_data()
        
        if df_balanced is not None:
            print("\n" + "=" * 70)
            print("BAT DAU HUAN LUYEN MODEL")
            print("=" * 70)
            train_model_from_preprocessed_data()
        else:
            print("Khong the tiep tuc vi khong co du lieu da tien xu ly")
    except Exception as e:
        print(f"Loi khi chay pipeline: {e}")

def main():
    while True:
        show_menu()
        
        choice = input("\nNhap lua chon (1-4): ").strip()
        
        if choice == '1':
            run_preprocessing()
            
        elif choice == '2':
            run_training()
            
        elif choice == '3':
            run_full_pipeline()
            
        elif choice == '4':
            print("\nCam on ban da su dung chuong trinh!")
            print("Thoat chuong trinh...")
            break 
            
        else:
            print("Lua chon khong hop le. Vui long nhap 1, 2, 3 hoac 4.")
        
        if choice in ['1', '2', '3']:
            continue_choice = input("\nBan co muon tiep tuc khong? (y/n): ").strip().lower()
            if continue_choice != 'y':
                print("\nThoat chuong trinh...")
                break

if __name__ == "__main__":
    main()