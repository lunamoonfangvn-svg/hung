import sqlite3
import os
import glob
import re

# 1. KHỞI TẠO CẤU TRÚC DATABASE CHUẨN
def setup_database():
    """Tạo file database và các bảng nếu chưa tồn tại"""
    conn = sqlite3.connect('nha_xuat_ban_online.db')
    cursor = conn.cursor()
    
    # Bảng chứa thông tin truyện
    cursor.execute('''CREATE TABLE IF NOT EXISTS Stories (
        story_id INTEGER PRIMARY KEY, 
        title TEXT, 
        author TEXT, 
        origin TEXT, 
        description TEXT)''')
    
    # Bảng chứa nội dung chương
    cursor.execute('''CREATE TABLE IF NOT EXISTS Chapters (
        chapter_id INTEGER PRIMARY KEY AUTOINCREMENT, 
        story_id INTEGER, 
        chapter_number REAL, 
        title TEXT, 
        content TEXT,
        UNIQUE(story_id, chapter_number))''')
        
    conn.commit()
    return conn

# 2. HÀM XỬ LÝ NỘI DUNG VĂN BẢN (KHỬ LỖI HIỂN THỊ CODE)
def clean_content(text):
    """Làm sạch văn bản để tránh lỗi hiển thị code thừa trên app.py"""
    # Loại bỏ các ký tự đặc biệt có thể khiến Streamlit hiểu lầm là Markdown code block
    cleaned = text.replace('\r', '')
    # Đảm bảo không có các thẻ HTML lạ lọt vào
    cleaned = re.sub(r'<[^>]*>', '', cleaned) 
    return cleaned.strip()

# 3. QUY TRÌNH NẠP TRUYỆN TỰ ĐỘNG [cite: 2026-01-10]
def run_import():
    setup_database()
    conn = sqlite3.connect('nha_xuat_ban_online.db')
    cursor = conn.cursor()
    
    input_dir = "input_novels"
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
        print(f"📂 Đã tạo thư mục {input_dir}. Hãy bỏ các thư mục truyện vào đây.")
        return

    # Quét các thư mục ID (1, 2, 3...)
    subdirs = [d for d in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, d))]
    
    if not subdirs:
        print("⚠️ Không tìm thấy thư mục truyện nào trong 'input_novels/'.")
        return

    for folder_id in subdirs:
        if not folder_id.isdigit():
            continue
            
        story_id = int(folder_id)
        
        # Tự động khởi tạo truyện nếu chưa có trong DB
        cursor.execute("INSERT OR IGNORE INTO Stories (story_id, title, author) VALUES (?,?,?)", 
                       (story_id, f"Truyện ID {story_id}", "Ẩn danh"))
        
        path = os.path.join(input_dir, folder_id)
        # Tìm tất cả file .txt trong thư mục ID [cite: 2026-01-10]
        for f_path in glob.glob(os.path.join(path, "*.txt")):
            try:
                with open(f_path, 'r', encoding='utf-8', errors='ignore') as f:
                    full_text = f.read()
                
                # Tách chương theo định dạng === CHƯƠNG X === [cite: 2026-01-10]
                parts = re.split(r'(=== CHƯƠNG \d+ ===)', full_text)
                
                for i in range(1, len(parts), 2):
                    raw_title = parts[i].replace("===", "").strip()
                    raw_content = clean_content(parts[i+1])
                    
                    # Lấy số chương để sắp xếp [cite: 2026-01-10]
                    try:
                        ch_num = float(re.findall(r'\d+', raw_title)[0])
                    except:
                        ch_num = 0.0
                        
                    # Nạp vào Database
                    cursor.execute('''INSERT OR REPLACE INTO Chapters 
                                    (story_id, chapter_number, title, content) 
                                    VALUES (?,?,?,?)''', 
                                    (story_id, ch_num, raw_title, raw_content))
                
                print(f"✅ Đã nạp thành công: {os.path.basename(f_path)} (ID: {story_id})")
            except Exception as e:
                print(f"❌ Lỗi khi xử lý file {f_path}: {e}")

    conn.commit()
    conn.close()
    print("\n✨ TẤT CẢ DỮ LIỆU ĐÃ ĐƯỢC ĐỒNG BỘ!")

if __name__ == "__main__":
    run_import()