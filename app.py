import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CẤU HÌNH TRANG
st.set_page_config(page_title="🌸 Hoa của Chinsu", page_icon="🌸", layout="centered")

# 2. HÀM ÁNH XẠ MÀU SẮC
def get_color_by_type(flower_type):
    t = str(flower_type).strip().lower()
    colors = {
        "đỏ": "#ef4444", "cam": "#f97316", 
        "tím": "#a855f7", "lam": "#3b82f6", "lục": "#22c55e"
    }
    return colors.get(t, "#475569")

# 3. CSS CUSTOM TỐI ƯU CHO MOBILE
st.markdown("""
    <style>
    /* Tổng thể */
    .main { padding-top: 1rem; }
    h1 {
        font-size: 1.5rem !important;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    /* Thẻ hoa (View theo Hoa) */
    .flower-card {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 0.6rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .flower-name { font-size: 1.1rem; font-weight: 800; }
    
    /* Tag chủ sở hữu */
    .owner-tag {
        display: inline-block;
        background: #f0fdf4;
        color: #166534;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.8rem;
        margin: 2px;
        border: 1px solid #dcfce7;
    }
    
    /* Tag hoa (View theo Người) */
    .flower-inline-tag {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 3px;
        color: white;
    }
    
    /* Container cho từng người */
    .person-container {
        background: #ffffff;
        padding: 12px;
        border-radius: 12px;
        border: 1px solid #f1f5f9;
        margin-bottom: 1.5rem;
    }
    .person-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
    }
    
    /* Tối ưu thanh lọc cho mobile */
    div[data-testid="stHorizontalBlock"] {
        gap: 0.5rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. KẾT NỐI VÀ TẢI DỮ LIỆU
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=0)
def load_data():
    data = conn.read()
    data = data.astype(str)
    return data.replace(['None', 'nan', 'False', '0.0', '0', 'NoneType'], '')

df = load_data()

# 5. XỬ LÝ DỮ LIỆU
exclude_cols = ['Type', 'Flower', 'Total']
all_owners = [col for col in df.columns if col not in exclude_cols]

def get_owners(row):
    return [owner for owner in all_owners if str(row[owner]).strip().upper() == 'X']

df['owners_list'] = df.apply(get_owners, axis=1)
df['has_owner'] = df['owners_list'].apply(lambda x: len(x) > 0)

# --- GIAO DIỆN CHÍNH ---
st.title("🌸 Hoa của Chinsu yêu dấu")

# Khu vực quản lý gọn gàng
with st.expander("⚙️ Quản lý dữ liệu"):
    pwd = st.text_input("Mật khẩu", type="password")
    if pwd == "Chinsu":
        # Gom các chức năng cập nhật vào đây để tiết kiệm chỗ màn hình chính
        mode = st.selectbox("Chọn thao tác", ["Thêm thành viên", "Thêm hoa", "Cập nhật sở hữu"])
        st.divider()
        if mode == "Thêm thành viên":
            new_name = st.text_input("Tên mới")
            if st.button("Lưu người"):
                # ... logic giữ nguyên ...
                pass
        # (Các logic Tab1, Tab2, Tab3 cũ có thể tích hợp vào Selectbox này để UI Mobile mượt hơn)
    elif pwd != "": st.error("Sai mật khẩu")

st.divider()

# 6. BỘ LỌC THÔNG MINH (Responsive)
view_mode = st.segmented_control("Chế độ:", ["Xem theo Hoa", "Xem theo Người"], default="Xem theo Hoa")

c1, c2 = st.columns(2)
with c1: search = st.text_input("🔍 Tên hoa", placeholder="Tìm...")
with c2: s_o_filter = st.selectbox("👤 Chủ sở hữu", ["Tất cả"] + all_owners)

o_empty = st.toggle("Chỉ hiện hoa chưa có chủ")

# LOGIC LỌC
f_df = df.copy()
if search: f_df = f_df[f_df['Flower'].str.contains(search, case=False, na=False)]
if s_o_filter != "Tất cả": f_df = f_df[f_df[s_o_filter].astype(str).str.upper() == 'X']
if o_empty: f_df = f_df[~f_df['has_owner']]

# 7. HIỂN THỊ
if view_mode == "Xem theo Hoa":
    st.caption(f"Đang hiển thị {len(f_df)} kết quả")
    for _, row in f_df.iterrows():
        t_color = get_color_by_type(row['Type'])
        o_html = "".join([f"<span class='owner-tag'>{o}</span>" for o in row['owners_list']])
        st.markdown(f"""
            <div class="flower-card" style="border-left: 5px solid {t_color};">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <span class="flower-name" style="color: {t_color};">{row['Flower']}</span>
                    <span class="type-tag" style="background:#f1f5f9; padding:2px 6px; border-radius:4px; font-size:0.7rem;">{row['Type']}</span>
                </div>
                <div style="margin-top: 6px;">{o_html if o_html else '<span style="color:#cbd5e1; font-size:0.8rem;">Chưa có chủ</span>'}</div>
            </div>
        """, unsafe_allow_html=True)

else:
    display_people = all_owners if s_o_filter == "Tất cả" else [s_o_filter]
    for person in display_people:
        person_flowers = f_df[f_df[person].astype(str).str.upper() == 'X']
        if not person_flowers.empty:
            flowers_html = "".join([
                f"<span class='flower-inline-tag' style='background: {get_color_by_type(r['Type'])};'>{r['Flower']}</span>" 
                for _, r in person_flowers.iterrows()
            ])
            st.markdown(f"""
                <div class="person-header">👤 {person} <span style="margin-left:8px; font-size:0.8rem; color:#64748b; font-weight:400;">({len(person_flowers)} hoa)</span></div>
                <div class="person-container">{flowers_html}</div>
            """, unsafe_allow_html=True)