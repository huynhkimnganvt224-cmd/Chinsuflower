import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CẤU HÌNH TRANG
st.set_page_config(page_title="🌸 Hoa của Chinsu yêu dấu 🌸", page_icon="🌸", layout="wide")

# 2. HÀM HỖ TRỢ
def get_color_by_type(flower_type):
    t = str(flower_type).strip().lower()
    colors = {"đỏ": "#ef4444", "cam": "#f97316", "tím": "#a855f7", "lam": "#3b82f6", "lục": "#22c55e"}
    return colors.get(t, "#475569")

# 3. CSS CUSTOM
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 5rem; padding-left: 2rem; padding-right: 2rem; }
    h1 { text-align: center; margin-top: -1.2rem; margin-bottom: 1rem; color: #D81B60; font-weight: bold; }
    .stRadio > div { justify-content: center; gap: 20px; }
    .flower-card { background: white; padding: 1.2rem; border-radius: 1rem; border: 1px solid #e2e8f0; margin-bottom: 0.8rem; position: relative; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
    .flower-name { font-size: 1.15rem; font-weight: 700; }
    .owner-tag { display: inline-block; background: #ecfdf5; color: #059669; padding: 2px 10px; border-radius: 6px; font-size: 0.85rem; margin: 4px 4px 0 0; border: 1px solid #d1fae5; }
    .flower-inline-tag { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.9rem; font-weight: 600; margin: 4px; color: white; }
    .person-header { margin: 1.5rem 0 0.8rem 0; padding-left: 0.5rem; border-left: 4px solid #f472b6; font-size: 1.3rem; font-weight: 700; display: flex; align-items: center; justify-content: space-between; }
    .person-container { background: #f8fafc; padding: 10px; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# 4. KẾT NỐI DỮ LIỆU
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=0)
def load_data():
    try:
        data = conn.read()
        return data.astype(str).replace(['None', 'nan', '0.0', '0', 'NoneType'], '')
    except:
        return pd.DataFrame()

df = load_data()
if df.empty:
    st.error("Không thể tải dữ liệu.")
    st.stop()

exclude_cols = ['Type', 'Flower', 'Total']
all_owners = [col for col in df.columns if col not in exclude_cols]
df['owners_list'] = df.apply(lambda r: [o for o in all_owners if str(r[o]).strip().upper() == 'X'], axis=1)

if 'admin_mode' not in st.session_state:
    st.session_state.admin_mode = False

# --- PHẦN ĐẦU TRANG ---
st.title("🌸 Hoa của Chinsu yêu dấu 🌸")

with st.popover("⚙️ Cập nhật dữ liệu", use_container_width=True):
    pwd = st.text_input("Mật khẩu", type="password")
    if pwd == "Chinsu":
        tabs = st.tabs(["+ Thành viên", "+ Loài hoa", "Sở hữu", "✏️ Đổi tên"])
        
        with tabs[2]: # SỞ HỮU CHI TIẾT
            type_edit = st.radio("Chọn kiểu cập nhật:", ["Cập nhật theo HOA", "Cập nhật theo NGƯỜI"], horizontal=True)
            st.divider()

            if type_edit == "Cập nhật theo HOA":
                f_target = st.selectbox("Chọn loài hoa:", df['Flower'].tolist())
                idx = df[df['Flower'] == f_target].index[0]
                cur_owners = df.at[idx, 'owners_list']
                new_sel = []
                cols = st.columns(4)
                for i, owner in enumerate(all_owners):
                    with cols[i % 4]:
                        if st.checkbox(owner, value=(owner in cur_owners), key=f"f_up_{owner}"):
                            new_sel.append(owner)
                if st.button("Xác nhận Lưu (Theo Hoa)"):
                    df_up = df.drop(columns=['owners_list']).copy()
                    for o in all_owners: df_up.at[idx, o] = 'X' if o in new_sel else ''
                    conn.update(data=df_up); st.cache_data.clear(); st.rerun()

            else: # Cập nhật theo NGƯỜI
                o_target = st.selectbox("Chọn người:", all_owners)
                
                # --- THÊM RADIO BUTTON LỌC PHẨM TRONG QUẢN LÝ ---
                filter_type_admin = st.radio("Phẩm hoa:", ["Tất cả", "Đỏ", "Cam", "Tím", "Lam", "Lục"], horizontal=True, key="admin_filter_type")
                
                # Lọc danh sách hoa hiển thị dựa trên radio button
                if filter_type_admin == "Tất cả":
                    flowers_to_show = df
                else:
                    flowers_to_show = df[df['Type'] == filter_type_admin]

                cur_flowers = df[df[o_target].astype(str).str.upper() == 'X']['Flower'].tolist()
                
                st.write(f"Đang hiển thị: {len(flowers_to_show)} hoa")
                new_f_sel = list(set(cur_flowers)) # Giữ lại các hoa cũ không nằm trong danh sách đang hiển thị

                cols = st.columns(4)
                for i, (f_idx, f_row) in enumerate(flowers_to_show.iterrows()):
                    f_name = f_row['Flower']
                    with cols[i % 4]:
                        # Nếu hoa đang được chọn, checkbox sẽ tích
                        is_checked = st.checkbox(f_name, value=(f_name in cur_flowers), key=f"o_up_{f_name}")
                        
                        # Cập nhật danh sách mới dựa trên thay đổi của checkbox
                        if is_checked:
                            if f_name not in new_f_sel: new_f_sel.append(f_name)
                        else:
                            if f_name in new_f_sel: new_f_sel.remove(f_name)
                
                if st.button("Xác nhận Lưu (Theo Người)"):
                    df_up = df.drop(columns=['owners_list']).copy()
                    for i, row in df_up.iterrows():
                        df_up.at[i, o_target] = 'X' if row['Flower'] in new_f_sel else ''
                    conn.update(data=df_up); st.cache_data.clear(); st.rerun()
        
        # (Các tab khác giữ nguyên như cũ...)
        with tabs[0]:
             new_o = st.text_input("Tên thành viên mới")
             if st.button("Thêm người"):
                 if new_o.strip():
                     df_up = df.drop(columns=['owners_list'])[all_owners + exclude_cols]
                     df_up[new_o] = ""; conn.update(data=df_up); st.cache_data.clear(); st.rerun()
        with tabs[1]:
             n_f_n = st.text_input("Tên hoa mới")
             n_f_p = st.selectbox("Phẩm", ["Đỏ", "Cam", "Tím", "Lam", "Lục"])
             if st.button("Thêm hoa"):
                 if n_f_n.strip():
                     new_row = {**{'Type': n_f_p, 'Flower': n_f_n, 'Total': '0'}, **{o: '' for o in all_owners}}
                     df_up = pd.concat([df.drop(columns=['owners_list']), pd.DataFrame([new_row])], ignore_index=True)
                     conn.update(data=df_up); st.cache_data.clear(); st.rerun()
        with tabs[3]:
             old_n = st.selectbox("Tên cũ", all_owners)
             new_n = st.text_input("Tên mới")
             if st.button("Đổi tên"):
                 if new_n.strip():
                     df_up = df.drop(columns=['owners_list']).rename(columns={old_n: new_n})
                     conn.update(data=df_up); st.cache_data.clear(); st.rerun()

st.divider()

# --- GIAO DIỆN TÌM KIẾM & LỌC TRANG CHỦ ---
view_mode = st.radio("Chế độ xem", ["Xem theo Hoa", "Xem theo Người"], horizontal=True, label_visibility="collapsed")

# --- THÊM RADIO BUTTON LỌC PHẨM Ở TRANG CHỦ ---
filter_type_main = st.radio("Chọn phẩm:", ["Tất cả", "Đỏ", "Cam", "Tím", "Lam", "Lục"], horizontal=True, key="main_filter_type")

c1, c2, c3 = st.columns([2, 1, 1])
with c1: search = st.text_input("Tìm kiếm tên hoa...", label_visibility="collapsed")
with c2: s_o_filter = st.selectbox("Lọc theo người", ["Tất cả"] + all_owners, label_visibility="collapsed")
with c3: no_owner_only = st.checkbox("🔍 Chưa có chủ")

# LOGIC LỌC TỔNG HỢP
f_df = df.copy()
if filter_type_main != "Tất cả": f_df = f_df[f_df['Type'] == filter_type_main]
if search: f_df = f_df[f_df['Flower'].str.contains(search, case=False, na=False)]
if s_o_filter != "Tất cả": f_df = f_df[f_df[s_o_filter].astype(str).str.upper() == 'X']
if no_owner_only: f_df = f_df[f_df['owners_list'].map(len) == 0]

# --- HIỂN THỊ KẾT QUẢ ---
if view_mode == "Xem theo Hoa":
    st.write(f"Kết quả: **{len(f_df)}** loài hoa {' (Admin Mode)' if st.session_state.admin_mode else ''}")
    for _, row in f_df.iterrows():
        t_color = get_color_by_type(row['Type'])
        o_html = "".join([f"<span class='owner-tag'>{o}</span>" for o in row['owners_list']])
        col_info, col_del = st.columns([9, 1])
        with col_info:
            st.markdown(f'<div class="flower-card"><span class="flower-name" style="color:{t_color}">{row["Flower"]}</span><br><div style="margin-top:8px;">{o_html if o_html else "<i>Trống</i>"}</div></div>', unsafe_allow_html=True)
        with col_del:
            if st.session_state.admin_mode:
                if st.button("🗑️", key=f"del_f_{row['Flower']}"):
                    df_up = df[df['Flower'] != row['Flower']].drop(columns=['owners_list'])
                    conn.update(data=df_up); st.cache_data.clear(); st.rerun()
else:
    display_people = all_owners if s_o_filter == "Tất cả" else [s_o_filter]
    for p in display_people:
        p_f = f_df[f_df[p].astype(str).str.upper() == 'X']
        if not p_f.empty:
            col_p_h, col_p_d = st.columns([9, 1])
            with col_p_h: st.markdown(f'<div class="person-header">👤 {p} ({len(p_f)})</div>', unsafe_allow_html=True)
            with col_p_d:
                if st.session_state.admin_mode:
                    if st.button("🗑️", key=f"del_p_{p}"):
                        df_up = df.drop(columns=[p, 'owners_list']); conn.update(data=df_up); st.cache_data.clear(); st.rerun()
            tags = "".join([f"<span class='flower-inline-tag' style='background:{get_color_by_type(r['Type'])}'>{r['Flower']}</span>" for _, r in p_f.iterrows()])
            st.markdown(f'<div class="person-container">{tags}</div>', unsafe_allow_html=True)

# --- ADMIN LOGIN Ở CUỐI TRANG ---
st.write("<br><br>", unsafe_allow_html=True)
st.divider()
c_a1, c_a2, c_a3 = st.columns([2, 1, 2])
with c_a2:
    if not st.session_state.admin_mode:
        with st.popover("🔑 Admin Login", use_container_width=True):
            a_pwd = st.text_input("Mật khẩu Admin", type="password")
            if a_pwd == "administrator":
                st.session_state.admin_mode = True; st.rerun()
    else:
        if st.button("🔓 Thoát Admin", use_container_width=True):
            st.session_state.admin_mode = False; st.rerun()