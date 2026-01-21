import streamlit as st
import sqlite3
import streamlit.components.v1 as components

st.set_page_config(page_title="Reader Pro Mobile", layout="wide")

# CSS khóa khung hình và định dạng nội dung
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { overflow-x: hidden !important; }
    .main { overflow-x: hidden !important; }
    .reader-box {
        padding: 20px 10px;
        text-align: justify;
        word-wrap: break-word;
        overflow-x: hidden;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

def get_db_connection():
    # Sử dụng check_same_thread=False để hỗ trợ đa luồng trên Cloud
    conn = sqlite3.connect('nha_xuat_ban_online.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

if 'page' not in st.session_state: st.session_state.page = "home"
if 'ch_idx' not in st.session_state: st.session_state.ch_idx = 0

# --- CHIẾN THUẬT AUTO-SCROLL MỚI ---
def nav_to(page, idx=0):
    st.session_state.page = page
    st.session_state.ch_idx = idx
    # JavaScript ép trình duyệt cuộn về đầu trang
    components.html(
        f"""
        <script>
            window.parent.document.querySelector('.main').scrollTo(0,0);
        </script>
        """,
        height=0
    )
    st.rerun()

# --- TRANG CHỦ ---
def home_page():
    st.markdown("<h3 style='text-align: center;'>📚 THƯ VIỆN</h3>", unsafe_allow_html=True)
    conn = get_db_connection()
    stories = conn.execute('SELECT * FROM Stories').fetchall()
    conn.close()
    
    if stories:
        for s in stories:
            with st.container(border=True):
                st.subheader(s['title'])
                if st.button("Đọc ngay", key=f"r_{s['story_id']}", use_container_width=True):
                    st.session_state.current_id = s['story_id']
                    nav_to("reading", 0)

# --- TRANG ĐỌC (TỐI ƯU CUỘN) ---
def reading_page():
    conn = get_db_connection()
    chapters = conn.execute('SELECT * FROM Chapters WHERE story_id = ? ORDER BY chapter_number ASC', 
                            (st.session_state.current_id,)).fetchall()
    
    if chapters:
        titles = [c['title'] for c in chapters]
        
        # Thanh cài đặt
        with st.popover("⚙️ Cài đặt"):
            f_size = st.slider("Cỡ chữ", 16, 45, 22)
            theme = st.radio("Nền", ["Sáng", "Sepia", "Tối"], horizontal=True)

        # Chọn chương
        cur = st.selectbox("Chọn chương:", range(len(titles)), index=st.session_state.ch_idx, format_func=lambda x: titles[x])
        if cur != st.session_state.ch_idx: nav_to("reading", cur)
        
        ch = chapters[st.session_state.ch_idx]
        bg = {"Sáng": "#FFFFFF", "Sepia": "#F4ECD8", "Tối": "#1A1A1A"}[theme]
        tx = {"Sáng": "#111111", "Sepia": "#5B4636", "Tối": "#D1D1D1"}[theme]

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

        # NỘI DUNG
        content_html = ch['content'].replace('\n', '<br>')
        st.html(f"""
        <div class="reader-box" style="background-color: {bg}; color: {tx}; font-size: {f_size}px; font-family: serif;">
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

if st.session_state.page == "home": home_page()
else: reading_page()
