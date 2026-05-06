import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CẤU HÌNH TRANG
st.set_page_config(page_title="🌸 Hoa của Chinsu yêu dấu 🌸", page_icon="🌸", layout="centered")

# 2. HÀM ÁNH XẠ MÀU SẮC
def get_color_by_type(flower_type):
    t = str(flower_type).strip().lower()
    colors = {
        "đỏ": "#ef4444", "cam": "#f97316", 
        "tím": "#a855f7", "lam": "#3b82f6", "lục": "#22c55e"
    }
    return colors.get(t, "#475569")

# 3. CSS CUSTOM
st.markdown("""
    <style>
    h1 {
        font-size: 1.8rem !important;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        text-align: center;
    }
    .flower-card {
        background: white;
        padding: 1.2rem;
        border-radius: 1rem;
        border: 1px solid #e2e8f0;
        margin-bottom: 0.8rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .flower-name { font-size: 1.15rem; font-weight: 700; }
    .type-tag { font-size: 0.75rem; color: #64748b; background: #f1f5f9; padding: 2px 8px; border-radius: 4px; font-weight: 600; }
    .owner-tag {
        display: inline-block;
        background: #ecfdf5;
        color: #059669;
        padding: 2px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        margin: 4px 4px 0 0;
        border: 1px solid #d1fae5;
    }
    /* Style mới cho danh sách hoa trong View theo Người */
    .flower-inline-tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 4px;
        color: white;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    .person-header {
        margin: 1.5rem 0 0.8rem 0;
        padding-left: 0.5rem;
        border-left: 4px solid #f472b6;
        font-size: 1.3rem;
        font-weight: 700;
        color: #1e293b;
    }
    .person-container {
        background: #f8fafc;
        padding: 10px;
        border-radius: 12px;
        margin-bottom: 1rem;
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

# 5. XỬ LÝ DANH SÁCH THÀNH VIÊN
exclude_cols = ['Type', 'Flower', 'Total']
all_owners = [col for col in df.columns if col not in exclude_cols]

def get_owners(row):
    return [owner for owner in all_owners if str(row[owner]).strip().upper() == 'X']

df['owners_list'] = df.apply(get_owners, axis=1)
df['has_owner'] = df['owners_list'].apply(lambda x: len(x) > 0)

# --- GIAO DIỆN CHÍNH ---
st.title("🌸 Hoa của Chinsu yêu dấu 🌸")

# NÚT CẬP NHẬT DỮ LIỆU (Popover)
with st.popover("⚙️ Cập nhật dữ liệu", use_container_width=True):
    pwd = st.text_input("Xác thực", type="password", placeholder="Nhập mật khẩu...")
    if pwd == "Chinsu":
        tab1, tab2, tab3 = st.tabs(["+ Thành viên", "+ Loài hoa", "Sở hữu"])
        
        with tab1:
            new_owner_name = st.text_input("Tên thành viên mới")
            if st.button("Xác nhận thêm người", use_container_width=True):
                if new_owner_name.strip() and new_owner_name not in all_owners:
                    df_to_add = df.copy().drop(columns=['owners_list', 'has_owner'])
                    df_to_add[new_owner_name] = ""
                    df_to_add[new_owner_name] = df_to_add[new_owner_name].astype(object)
                    conn.update(data=df_to_add)
                    st.cache_data.clear()
                    st.rerun()
                else: st.error("Tên trống hoặc đã tồn tại!")
            
        with tab2:
            n_f_name = st.text_input("Tên hoa mới")
            n_f_type = st.selectbox("Màu sắc", ["Đỏ", "Cam", "Tím", "Lam", "Lục"])
            if st.button("Xác nhận thêm hoa", use_container_width=True):
                if n_f_name.strip() and n_f_name not in df['Flower'].values:
                    df_to_add = df.copy().drop(columns=['owners_list', 'has_owner']).astype(object)
                    new_row = {**{'Type': n_f_type, 'Flower': n_f_name, 'Total': '0'}, **{o: '' for o in all_owners}}
                    df_to_add = pd.concat([df_to_add, pd.DataFrame([new_row])], ignore_index=True)
                    conn.update(data=df_to_add)
                    st.cache_data.clear()
                    st.rerun()
                else: st.error("Tên trống hoặc đã tồn tại!")

        with tab3:
            s_tab_f, s_tab_o = st.tabs(["Theo Hoa", "Theo Người"])
            with s_tab_f:
                f_edit = st.selectbox("Chọn hoa", df['Flower'].tolist(), key="sb_f")
                idx = df[df['Flower'] == f_edit].index[0]
                cur_o = df.at[idx, 'owners_list']
                new_sel = [o for o in all_owners if st.checkbox(o, value=(o in cur_o), key=f"f_{f_edit}_{o}")]
                if st.button("Lưu theo Hoa", use_container_width=True):
                    df_up = df.copy()
                    for c in all_owners:
                        df_up[c] = df_up[c].astype(object)
                        df_up.at[idx, c] = 'X' if c in new_sel else ''
                    if 'Total' in df_up.columns: df_up.at[idx, 'Total'] = str(len(new_sel))
                    conn.update(data=df_up.drop(columns=['owners_list', 'has_owner']))
                    st.cache_data.clear()
                    st.rerun()
            with s_tab_o:
                o_edit = st.selectbox("Chọn người", all_owners, key="sb_o")
                cur_f = df[df[o_edit].astype(str).str.upper() == 'X']['Flower'].tolist()
                new_f_sel = [f for f in df['Flower'].tolist() if st.checkbox(f, value=(f in cur_f), key=f"o_{o_edit}_{f}")]
                if st.button("Lưu theo Người", use_container_width=True):
                    df_up = df.copy()
                    df_up[o_edit] = df_up[o_edit].astype(object)
                    for i, row in df_up.iterrows():
                        df_up.at[i, o_edit] = 'X' if row['Flower'] in new_f_sel else ''
                        row_o = [o for o in all_owners if str(df_up.at[i, o]).strip().upper() == 'X']
                        if 'Total' in df_up.columns: df_up.at[i, 'Total'] = str(len(row_o))
                    conn.update(data=df_up.drop(columns=['owners_list', 'has_owner']))
                    st.cache_data.clear()
                    st.rerun()
    elif pwd != "": st.error("Sai mật khẩu!")

st.divider()

# 6. CHẾ ĐỘ HIỂN THỊ VÀ BỘ LỌC
view_mode = st.radio("Chế độ xem:", ["Xem theo Hoa", "Xem theo Người"], horizontal=True)

c1, c2 = st.columns([2, 1])
with c1: search = st.text_input("🔍 Tìm kiếm", placeholder="Tên hoa...")
with c2: s_o_filter = st.selectbox("👤 Chủ sở hữu", ["Tất cả"] + all_owners)
o_empty = st.checkbox("Chỉ hiện hoa chưa có chủ")

# LOGIC LỌC
f_df = df.copy()
if search: f_df = f_df[f_df['Flower'].str.contains(search, case=False, na=False)]
if s_o_filter != "Tất cả": f_df = f_df[f_df[s_o_filter].astype(str).str.upper() == 'X']
if o_empty: f_df = f_df[~f_df['has_owner']]

# 7. HIỂN THỊ KẾT QUẢ
if view_mode == "Xem theo Hoa":
    st.write(f"Kết quả: **{len(f_df)}** loài hoa")
    for _, row in f_df.iterrows():
        t_color = get_color_by_type(row['Type'])
        o_html = "".join([f"<span class='owner-tag'>{o}</span>" for o in row['owners_list']])
        st.markdown(f"""
            <div class="flower-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="flower-name" style="color: {t_color};">{row['Flower']}</span>
                    <span class="type-tag">{row['Type']}</span>
                </div>
                <div style="margin-top: 8px;">
                    {o_html if o_html else '<span style="color:#94a3b8; font-style:italic; font-size:0.9rem;">Trống</span>'}
                </div>
            </div>
        """, unsafe_allow_html=True)

else:  # Xem theo Người
    display_people = all_owners if s_o_filter == "Tất cả" else [s_o_filter]
    
    found_any = False
    for person in display_people:
        person_flowers = f_df[f_df[person].astype(str).str.upper() == 'X']
        
        if not person_flowers.empty:
            found_any = True
            st.markdown(f'<div class="person-header">👤 {person} ({len(person_flowers)})</div>', unsafe_allow_html=True)
            
            # Tạo danh sách các hoa dưới dạng tags màu
            flowers_html = ""
            for _, row in person_flowers.iterrows():
                bg_color = get_color_by_type(row['Type'])
                flowers_html += f"<span class='flower-inline-tag' style='background-color: {bg_color};'>{row['Flower']}</span>"
            
            st.markdown(f"""
                <div class="person-container">
                    {flowers_html}
                </div>
            """, unsafe_allow_html=True)
    
    if not found_any:
        st.info("Không tìm thấy dữ liệu phù hợp.")
