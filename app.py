import streamlit as st
import sqlite3

# Tối ưu cấu hình hiển thị cho Mobile
st.set_page_config(page_title="Reader Pro Mobile", layout="wide")

def get_db_connection():
    # check_same_thread=False giúp chạy ổn định trên môi trường Internet
    conn = sqlite3.connect('nha_xuat_ban_online.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# Quản lý trạng thái trang và vị trí chương
if 'page' not in st.session_state: st.session_state.page = "home"
if 'ch_idx' not in st.session_state: st.session_state.ch_idx = 0

def nav_to(page, idx=0):
    st.session_state.page = page
    st.session_state.ch_idx = idx
    # Lệnh rerun giúp trình duyệt quay về đầu trang tự nhiên khi đổi nội dung
    st.rerun()

# --- TRANG CHỦ ---
def home_page():
    st.markdown("<h3 style='text-align: center;'>📚 THƯ VIỆN</h3>", unsafe_allow_html=True)
    conn = get_db_connection()
    stories = conn.execute('SELECT * FROM Stories').fetchall()
    conn.close()
    
    if not stories:
        st.info("Kệ sách trống. Hãy nạp truyện bằng main.py trên máy tính rồi upload file .db lên!")
    else:
        for s in stories:
            with st.container(border=True):
                st.subheader(s['title'])
                st.write(f"✍️ Tác giả: {s['author']}")
                c1, c2 = st.columns(2)
                if c1.button("📖 Đọc truyện", key=f"r_{s['story_id']}", use_container_width=True):
                    st.session_state.current_id = s['story_id']
                    nav_to("reading", 0)
                if c2.button("🛠️ Sửa", key=f"e_{s['story_id']}", use_container_width=True):
                    st.session_state.current_id = s['story_id']
                    nav_to("edit")

# --- TRANG ĐỌC (FIX CUỘN & KHÓA NGANG) ---
def reading_page():
    # Tạo mỏ neo tàng hình ở dòng đầu tiên để ép trình duyệt nhận diện vị trí 0
    st.markdown("<div id='top'></div>", unsafe_allow_html=True)
    
    conn = get_db_connection()
    chapters = conn.execute('SELECT * FROM Chapters WHERE story_id = ? ORDER BY chapter_number ASC', 
                            (st.session_state.current_id,)).fetchall()
    
    with st.popover("⚙️ Cài đặt"):
        f_size = st.slider("Cỡ chữ", 16, 45, 22)
        l_height = st.slider("Giãn dòng", 1.0, 2.5, 1.5, step=0.1)
        theme = st.radio("Nền", ["Sáng", "Sepia", "Tối"], horizontal=True)

    if chapters:
        titles = [c['title'] for c in chapters]
        cur = st.selectbox("Chọn chương:", range(len(titles)), index=st.session_state.ch_idx, format_func=lambda x: titles[x])
        if cur != st.session_state.ch_idx: nav_to("reading", cur)
        
        ch = chapters[st.session_state.ch_idx]
        bg = {"Sáng": "#FFFFFF", "Sepia": "#F4ECD8", "Tối": "#1A1A1A"}[theme]
        tx = {"Sáng": "#111111", "Sepia": "#5B4636", "Tối": "#D1D1D1"}[theme]

        # CSS ÉP KHUNG: KHÓA NGANG VÀ TỐI ƯU MOBILE
        st.markdown(f"""
            <style>
            /* Khóa toàn bộ app không cho trượt ngang */
            [data-testid="stAppViewContainer"] {{ overflow-x: hidden !important; }}
            .main {{ overflow-x: hidden !important; }}
            
            .reader-box {{
                background-color: {bg}; color: {tx};
                padding: 20px 10px; border-radius: 8px;
                font-family: 'Source Serif 4', serif;
                font-size: {f_size}px; line-height: {l_height};
                text-align: justify; word-wrap: break-word;
                overflow-x: hidden; width: 100%; box-sizing: border-box;
            }}
            </style>
        """, unsafe_allow_html=True)

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

        # HIỂN THỊ NỘI DUNG SẠCH (ÉP HTML THUẦN)
        content_html = ch['content'].replace('\n', '<br>')
        st.html(f"""
        <div class="reader-box">
            <h3 style="text-align:center;">{ch['title']}</h3>
            <hr style="opacity:0.2">
            <div>{content_html}</div>
        </div>
        """)

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

# --- TRANG SỬA ---
def edit_page():
    st.title("🛠️ Sửa thông tin")
    conn = get_db_connection()
    story = conn.execute('SELECT * FROM Stories WHERE story_id = ?', (st.session_state.current_id,)).fetchone()
    if st.button("⬅️ Hủy"): nav_to("home")
    if story:
        with st.form("edit_form"):
            t = st.text_input("Tiêu đề", story['title'])
            a = st.text_input("Tác giả", story['author'])
            d = st.text_area("Mô tả", story['description'])
            if st.form_submit_button("Lưu"):
                conn.execute('UPDATE Stories SET title=?, author=?, description=? WHERE story_id=?', (t,a,d,story['story_id']))
                conn.commit()
                st.success("Đã cập nhật!"); nav_to("home")
    conn.close()

if st.session_state.page == "home": home_page()
elif st.session_state.page == "edit": edit_page()
else: reading_page()
