import streamlit as st
import sqlite3
import os

# 1. CẤU HÌNH MOBILE FIRST
st.set_page_config(page_title="Reader Mobile Pro", layout="wide")

# 2. HÀM KHỞI TẠO VÀ KẾT NỐI DB (Sửa lỗi image_f6d7e4.png)
def get_db_connection():
    db_path = 'nha_xuat_ban_online.db'
    db_exists = os.path.exists(db_path)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    
    # Nếu file DB mới tinh, tự tạo cấu trúc bảng để không bị lỗi "no such table"
    if not db_exists:
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS Stories (story_id INTEGER PRIMARY KEY, title TEXT, author TEXT, description TEXT)')
        cursor.execute('CREATE TABLE IF NOT EXISTS Chapters (chapter_id INTEGER PRIMARY KEY AUTOINCREMENT, story_id INTEGER, chapter_number REAL, title TEXT, content TEXT)')
        conn.commit()
    return conn

# Quản lý trạng thái
if 'page' not in st.session_state: st.session_state.page = "home"
if 'ch_idx' not in st.session_state: st.session_state.ch_idx = 0

def nav_to(page, idx=0):
    st.session_state.page = page
    st.session_state.ch_idx = idx
    st.rerun()

# --- TRANG CHỦ ---
def home_page():
    st.markdown("<h3 style='text-align: center;'>📚 THƯ VIỆN</h3>", unsafe_allow_html=True)
    conn = get_db_connection()
    stories = conn.execute('SELECT * FROM Stories').fetchall()
    conn.close()
    
    if not stories:
        st.warning("⚠️ Kệ sách trống! Hãy chạy main.py để nạp truyện vào Database.")
    else:
        for s in stories:
            with st.container(border=True):
                st.subheader(s['title'])
                st.write(f"✍️ {s['author']}")
                if st.button("📖 Đọc truyện", key=f"r_{s['story_id']}", use_container_width=True):
                    st.session_state.current_id = s['story_id']
                    nav_to("reading", 0)

# --- TRANG ĐỌC (Sửa lỗi hiển thị code & giãn dòng) ---
def reading_page():
    st.markdown("<div id='top'></div>", unsafe_allow_html=True)
    conn = get_db_connection()
    chapters = conn.execute('SELECT * FROM Chapters WHERE story_id = ? ORDER BY chapter_number ASC', (st.session_state.current_id,)).fetchall()
    
    with st.popover("⚙️ Cài đặt"):
        f_size = st.slider("Cỡ chữ", 16, 45, 22)
        # Fix lỗi giãn dòng quá mức (Hình image_f5e4a3.png)
        l_height = st.slider("Giãn dòng", 1.0, 2.5, 1.5, step=0.1)
        theme = st.radio("Nền", ["Sáng", "Sepia", "Tối"], horizontal=True)

    if chapters:
        titles = [c['title'] for c in chapters]
        cur = st.selectbox("Chọn chương:", range(len(titles)), index=st.session_state.ch_idx, format_func=lambda x: titles[x])
        if cur != st.session_state.ch_idx: nav_to("reading", cur)
        
        ch = chapters[st.session_state.ch_idx]
        bg = {"Sáng": "#FFF", "Sepia": "#F4ECD8", "Tối": "#1A1A1A"}[theme]
        tx = {"Sáng": "#111", "Sepia": "#5B4636", "Tối": "#D1D1D1"}[theme]

        # ĐIỀU HƯỚNG ĐẦU
        c1, c2, c3 = st.columns(3)
        with c1: 
            if st.session_state.ch_idx > 0:
                if st.button("⏮️", key="t1", use_container_width=True): nav_to("reading", st.session_state.ch_idx-1)
        with c2: 
            if st.button("🏠", key="t2", use_container_width=True): nav_to("home")
        with c3: 
            if st.session_state.ch_idx < len(titles)-1:
                if st.button("⏭️", key="t3", use_container_width=True): nav_to("reading", st.session_state.ch_idx+1)

        # HIỂN THỊ SẠCH (Sửa lỗi image_f65480.png bằng st.html)
        content_safe = ch['content'].replace('\n', '<br>')
        html_layout = f"""
        <div style="background-color:{bg}; color:{tx}; padding:20px 5%; border-radius:10px; 
                    font-family:serif; font-size:{f_size}px; line-height:{l_height}; text-align:justify;">
            <h2 style="text-align:center;">{ch['title']}</h2>
            <hr style="opacity:0.2">
            <div style="white-space: normal;">{content_safe}</div>
        </div>
        """
        # Sử dụng st.html thay cho st.markdown để không bị hiện code thừa
        st.html(html_layout)

        # ĐIỀU HƯỚNG CUỐI
        st.divider()
        b1, b2, b3 = st.columns(3)
        with b1: 
            if st.session_state.ch_idx > 0:
                if st.button("⏮️ Trước", key="b1", use_container_width=True): nav_to("reading", st.session_state.ch_idx-1)
        with b2: 
            if st.button("🏠 Thư viện", key="b2", use_container_width=True): nav_to("home")
        with b3: 
            if st.session_state.ch_idx < len(titles)-1:
                if st.button("Sau ⏭️", key="b3", use_container_width=True): nav_to("reading", st.session_state.ch_idx+1)
    conn.close()

if st.session_state.page == "home": home_page()
else: reading_page()