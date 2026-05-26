import streamlit as st
import pandas as pd
import os

# 設定網頁為寬螢幕模式與漂亮的主題圖示
st.set_page_config(page_title="選屋找補對照系統", page_icon="🏡", layout="wide")

# ==========================================
# 🔒 安全隱私設定區：鎖定 data 資料夾與新檔名
# ==========================================
DATA_FOLDER = 'data'
EXCEL_FILENAME = '價格表.xlsx'
excel_path = os.path.join(DATA_FOLDER, EXCEL_FILENAME)

# ==========================================
# 1. 智慧排序讀取：自動處理樓層與車位順序
# ==========================================
@st.cache_data
def load_data(path):
    excel_file = pd.ExcelFile(path)
    sheet_names = excel_file.sheet_names
    
    house_df = pd.read_excel(path, sheet_name=sheet_names[0])
    parking_df = pd.read_excel(path, sheet_name=sheet_names[1]) if len(sheet_names) > 1 else house_df
    
    # 建立房屋 Python 字典
    h_dict = {}
    for _, row in house_df.iterrows():
        f, u, p = str(row['樓層']).strip(), str(row['戶型']).strip(), int(row['總價(元)'])
        if f not in h_dict: h_dict[f] = {}
        h_dict[f][u] = p
        
    # 建立車位 Python 字典
    p_dict = {}
    for _, row in parking_df.iterrows():
        l, pid, p = str(row['地下樓層']).strip(), str(row['車位號碼']).strip(), int(row['總價(元)'])
        if l not in p_dict: p_dict[l] = {}
        p_dict[l][pid] = p
        
    return h_dict, p_dict

try:
    house_dict, parking_dict = load_data(excel_path)
    has_data = True
except Exception as e:
    st.error(f"資料解讀失敗！請確保 data 資料夾內有放「價格表.xlsx」")
    house_dict, parking_dict = {}, {}
    has_data = False

# 找補固定常數
PERSONAL_VALUE = 29393269
RATIO = 0.95

# ==========================================
# 2. 定義自訂美化 CSS 樣式
# ==========================================
st.markdown("""
    <style>
        /* 徹底移除 Streamlit 頂部的空白與不必要的文字殘留 */
        .block-container { padding-top: 1.5rem !important; }
        [data-testid="stMarkdownContainer"] h3 { margin-bottom: 0px !important; }
        
        /* 卡片精美外框樣式 */
        .custom-card {
            font-family: "Microsoft JhengHei", sans-serif;
            padding: 24px;
            border: 1px solid #e1e4e8;
            border-radius: 12px;
            background: #ffffff;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }
        .sub-price { font-size: 0.92em; color: #666; text-align: right; margin-top: 5px; margin-bottom: 15px; }
        .price-val { color: #d9534f; font-weight: bold; font-size: 1.05em; }
    </style>
""", unsafe_allow_html=True)

# 樓層與車位智慧排序函式
def sort_floors(floor_list):
    # 拔掉 F 轉成數字排序，例如 "13F" -> 13
    return sorted(floor_list, key=lambda x: int(x.upper().replace('F','')) if x.upper().replace('F','').isdigit() else 99)

def sort_parking_levels(level_list):
    # 拔掉 B 轉成數字排序，例如 "B2" -> 2
    return sorted(level_list, key=lambda x: int(x.upper().replace('B','')) if x.upper().replace('B','').isdigit() else 99)

col1, col2 = st.columns([1, 1.2])

# --- 左側：高質感對照計算機 ---
with col1:
    with st.container():
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center; color:#222; margin-top:0; font-size:22px; font-weight:bold;'>選屋找補計算機</h2>", unsafe_allow_html=True)
        
        # --- 房屋下拉選單（套用智慧數字排序） ---
        st.markdown("<span style='color:#444; font-weight:bold; font-size:15px;'>選擇樓層：</span>", unsafe_allow_html=True)
        floors = sort_floors(list(house_dict.keys())) if has_data else []
        sel_floor = st.selectbox("floor_sel", floors if floors else ["無資料"], label_visibility="collapsed", key="f_sel")
        
        st.markdown("<span style='color:#444; font-weight:bold; font-size:15px;'>選擇戶型：</span>", unsafe_allow_html=True)
        units = sorted(list(house_dict[sel_floor].keys())) if sel_floor in house_dict else []
        sel_unit = st.selectbox("unit_sel", units if units else ["無資料"], label_visibility="collapsed", key="u_sel")
        
        h_price = house_dict[sel_floor][sel_unit] if sel_floor in house_dict and sel_unit in house_dict[sel_floor] else 0
        st.markdown(f'<div class="sub-price">房屋單價：<span class="price-val">{h_price:,}</span> 元</div>', unsafe_allow_html=True)
        
        # --- 車位下拉選單（套用智慧數字排序） ---
        st.markdown("<span style='color:#444; font-weight:bold; font-size:15px;'>選擇車位樓層：</span>", unsafe_allow_html=True)
        p_floors = sort_parking_levels(list(parking_dict.keys())) if has_data else []
        sel_p_floor = st.selectbox("p_floor_sel", p_floors if p_floors else ["無資料"], label_visibility="collapsed", key="p_f_sel")
        
        st.markdown("<span style='color:#444; font-weight:bold; font-size:15px;'>選擇車位號碼：</span>", unsafe_allow_html=True)
        p_ids = sorted(list(parking_dict[sel_p_floor].keys()), key=lambda x: int(x) if x.isdigit() else x) if sel_p_floor in parking_dict else []
        sel_p_id = st.selectbox("pid_sel", p_ids if p_ids else ["無資料"], label_visibility="collapsed", key="p_i_sel")
        
        p_price = parking_dict[sel_p_floor][sel_p_id] if sel_p_floor in parking_dict and sel_p_id in parking_dict[sel_p_floor] else 0
        st.markdown(f'<div class="sub-price">車位單價：<span class="price-val">{p_price:,}</span> 元</div>', unsafe_allow_html=True)
        
        # 計算總價與找補金額
        total_price = h_price + p_price
        diff_price = round((total_price - PERSONAL_VALUE) * RATIO)
        
        # 經典三色結果面板
        st.markdown(f"""
            <div style='background: #eef7ff; padding: 14px; border-radius: 6px; text-align: center; font-size: 1.25em; font-weight: bold; color: #0056b3; border: 1px solid #bce8f1; margin-bottom: 12px;'>
                總計金額：{total_price:,} 元
            </div>
            <div style='background: #fafafa; padding: 14px; border-radius: 6px; text-align: center; font-size: 1.1em; font-weight: bold; color: #444; border: 1px solid #e1e4e8; margin-bottom: 12px; line-height: 1.6;'>
                個人權值金額：29,393,269 元<br>找補比率：95%
            </div>
            <div style='background: #fff4e5; padding: 14px; border-radius: 6px; text-align: center; font-size: 1.25em; font-weight: bold; color: #e67e22; border: 1px solid #ffe5b4;'>
                找補金額：{diff_price:,} 元
            </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- 右側：自動圖面對照欄 ---
with col2:
    st.markdown("### 🗺️ 樓層與車位圖面參考")
    
    # 1. 房屋圖面自動檢索
    st.markdown(f"#### 🏠 房屋：{sel_floor} 平面圖")
    try:
        f_num = int(sel_floor.upper().replace('F',''))
        if f_num == 3:
            img_file = os.path.join('maps', 'floor_3.png')
        elif 4 <= f_num <= 14:
            img_file = os.path.join('maps', 'floor_4_14.png')
        elif 15 <= f_num <= 24:
            img_file = os.path.join('maps', 'floor_15_24.png')
        else:
            img_file = None
            
        if img_file and os.path.exists(img_file):
            st.image(img_file, use_column_width=True)
        else:
            st.caption("💡 暫無此樓層對應圖檔")
    except:
        st.caption("暫時無法解析樓層圖面。")

    st.markdown("<br><hr>", unsafe_allow_html=True)

    # 2. 車位圖面自動檢索
    st.markdown(f"#### 🚗 車位：{sel_p_floor} 平面圖")
    p_img_file = os.path.join('maps', f"parking_{sel_p_floor}.png")
    
    if os.path.exists(p_img_file):
        st.image(p_img_file, use_column_width=True)
    else:
        st.caption("💡 暫無此車位對應圖檔")
