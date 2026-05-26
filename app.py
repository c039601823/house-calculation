import streamlit as st
import os
import base64

# 設定網頁為寬螢幕模式
st.set_page_config(page_title="選屋找補對照系統", page_icon="🏡", layout="wide")

# 引入相關模組
if os.path.exists('app_data.py') and os.path.exists('app_viewer.py'):
    import app_data
    import app_viewer
else:
    st.error("系統元件缺失，請確保 app_data.py 與 app_viewer.py 皆已執行上傳。")

# 安全讀取價格表
excel_path = os.path.join('data', '價格表.xlsx')
try:
    house_dict, parking_dict = app_data.load_house_and_parking(excel_path)
    has_data = True
except:
    house_dict, parking_dict = {}, {}
    has_data = False

# 常數設定
PERSONAL_VALUE = 29393269
RATIO = 0.95

# 頁面極簡美化排版
st.markdown("""
    <style>
        [data-testid="stHeader"] { display: none !important; }
        .block-container { padding-top: 1.5rem !important; padding-bottom: 1.5rem !important; }
        .title-left, .title-right {
            font-family: "Microsoft JhengHei", sans-serif;
            font-size: 24px; font-weight: bold; color: #1a1a1a;
            padding-bottom: 12px !important; border-bottom: 2px solid #eaeaea;
            margin-bottom: 20px !important;
        }
        .custom-card {
            font-family: "Microsoft JhengHei", sans-serif;
            padding: 24px; border: 1px solid #e1e4e8; border-radius: 12px;
            background: #ffffff; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-top: 5px;
        }
        .sub-price { font-size: 0.92em; color: #666; text-align: right; margin-top: -8px; margin-bottom: 18px; }
        .price-val { color: #d9534f; font-weight: bold; font-size: 1.05em; }
    </style>
""", unsafe_allow_html=True)

def sort_floors(f_list): return sorted(f_list, key=lambda x: int(x.upper().replace('F','')) if x.upper().replace('F','').isdigit() else 99)
def sort_parking(l_list): return sorted(l_list, key=lambda x: int(x.upper().replace('B','')) if x.upper().replace('B','').isdigit() else 99)
def get_b64(path):
    if os.path.exists(path):
        with open(path, "rb") as f: return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
    return ""

col1, col2 = st.columns([1, 1.2])

# --- 左側：計算機 ---
with col1:
    st.markdown('<div class="title-left">🏡 選屋找補計算機</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        
        st.markdown("<span style='color:#444; font-weight:bold; font-size:15px;'>選擇樓層：</span>", unsafe_allow_html=True)
        floors = sort_floors(list(house_dict.keys())) if has_data else []
        sel_floor = st.selectbox("f_h", floors if floors else ["無資料"], label_visibility="collapsed", key="f_select")
        
        st.markdown("<span style='color:#444; font-weight:bold; font-size:15px;'>選擇戶型：</span>", unsafe_allow_html=True)
        units = sorted(list(house_dict[sel_floor].keys())) if sel_floor in house_dict else []
        sel_unit = st.selectbox("u_h", units if units else ["無資料"], label_visibility="collapsed", key="u_select")
        
        h_price = house_dict[sel_floor][sel_unit] if sel_floor in house_dict and sel_unit in house_dict[sel_floor] else 0
        st.markdown(f'<div class="sub-price">房屋單價：<span class="price-val">{h_price:,}</span> 元</div>', unsafe_allow_html=True)
        
        st.markdown("<span style='color:#444; font-weight:bold; font-size:15px;'>選擇車位樓層：</span>", unsafe_allow_html=True)
        p_floors = sort_parking(list(parking_dict.keys())) if has_data else []
        sel_p_floor = st.selectbox("p_h", p_floors if p_floors else ["無資料"], label_visibility="collapsed", key="p_f_select")
        
        st.markdown("<span style='color:#444; font-weight:bold; font-size:15px;'>選擇車位號碼：</span>", unsafe_allow_html=True)
        p_ids = sorted(list(parking_dict[sel_p_floor].keys()), key=lambda x: int(x) if x.isdigit() else x) if sel_p_floor in parking_dict else []
        sel_p_id = st.selectbox("pid_h", p_ids if p_ids else ["無資料"], label_visibility="collapsed", key="p_i_select")
        
        p_price = parking_dict[sel_p_floor][sel_p_id] if sel_p_floor in parking_dict and sel_p_id in parking_dict[sel_p_floor] else 0
        st.markdown(f'<div class="sub-price">車位單價：<span class="price-val">{p_price:,}</span> 元</div>', unsafe_allow_html=True)
        
        total_price = h_price + p_price
        diff_price = round((total_price - PERSONAL_VALUE) * RATIO)
        
        st.markdown(f"""
            <div style='background: #eef7ff; padding: 14px; border-radius: 6px; text-align: center; font-size: 1.25em; font-weight: bold; color: #0056b3; border: 1px solid #bce8f1; margin-bottom: 12px;'>總計金額：{total_price:,} 元</div>
            <div style='background: #fafafa; padding: 14px; border-radius: 6px; text-align: center; font-size: 1.1em; font-weight: bold; color: #444; border: 1px solid #e1e4e8; margin-bottom: 12px; line-height: 1.6;'>個人權值金額：29,393,269 元<br>找補比率：95%</div>
            <div style='background: #fff4e5; padding: 14px; border-radius: 6px; text-align: center; font-size: 1.25em; font-weight: bold; color: #e67e22; border: 1px solid #ffe5b4;'>找補金額：{diff_price:,} 元</div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- 右側：地圖化自動圖面對照欄 ---
with col2:
    st.markdown('<div class="title-right">🗺️ 樓層與車位圖面參考</div>', unsafe_allow_html=True)
    try:
        f_num = int(sel_floor.upper().replace('F',''))
        h_path = os.path.join('maps', 'floor_3.png' if f_num == 3 else 'floor_4_14.png' if 4 <= f_num <= 14 else 'floor_15_24.png' if 15 <= f_num <= 24 else '')
    except:
        h_path = ""
    p_path = os.path.join('maps', f"parking_{sel_p_floor}.png")
    
    # 調用外部地圖模組渲染
    viewer_html = app_viewer.get_map_html(sel_floor, sel_p_floor, get_b64(h_path), get_b64(p_path))
    st.components.v1.html(viewer_html, height=830, scrolling=False)
