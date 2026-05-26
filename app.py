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
# 1. 讀取 Excel 資料
# ==========================================
@st.cache_data
def load_data(path):
    excel_data = pd.read_excel(path, sheet_name=None)
    sheet_names = list(excel_data.keys())
    house_sheet = [s for s in sheet_names if '屋' in s or '房' in s] if sheet_names else None
    parking_sheet = [s for s in sheet_names if '車' in s] if sheet_names else None
    
    house_df = excel_data[house_sheet] if house_sheet else excel_data[sheet_names]
    parking_df = excel_data[parking_sheet] if parking_sheet else excel_data[sheet_names]
    
    # 建立 Python 字典
    h_dict = {}
    for _, row in house_df.iterrows():
        f, u, p = str(row['樓層']), str(row['戶型']), int(row['總價(元)'])
        if f not in h_dict: h_dict[f] = {}
        h_dict[f][u] = p
        
    p_dict = {}
    for _, row in parking_df.iterrows():
        l, pid, p = str(row['地下樓層']), str(row['車位號碼']), int(row['總價(元)'])
        if l not in p_dict: p_dict[l] = {}
        p_dict[l][pid] = p
        
    return h_dict, p_dict

try:
    house_dict, parking_dict = load_data(excel_path)
except Exception as e:
    st.error("資料讀取失敗，請確認 data/價格表.xlsx 是否正確。")
    house_dict, parking_dict = {}, {}

# 常數設定
PERSONAL_VALUE = 29393269
RATIO = 0.95

# ==========================================
# 2. 定義左右雙欄排版 (Streamlit 原生完美連動)
# ==========================================
col1, col2 = st.columns([1, 1.2])

# --- 左側：全原生美化計算機 ---
with col1:
    st.subheader("🏡 選屋找補計算機")
    
    # 房屋選擇區
    floors = sorted(list(house_dict.keys()))
    sel_floor = st.selectbox("1. 選擇房屋樓層：", floors if floors else ["無資料"])
    
    units = sorted(list(house_dict[sel_floor].keys())) if sel_floor in house_dict else []
    sel_unit = st.selectbox("2. 選擇房屋戶型：", units if units else ["無資料"])
    
    h_price = house_dict[sel_floor][sel_unit] if sel_floor in house_dict and sel_unit in house_dict[sel_floor] else 0
    st.markdown(f"<p style='text-align:right;color:#666;'>房屋單價：<span style='color:#d9534f;font-weight:bold;'>{h_price:,}</span> 元</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 車位選擇區
    p_floors = sorted(list(parking_dict.keys()))
    sel_p_floor = st.selectbox("3. 選擇車位樓層：", p_floors if p_floors else ["無資料"])
    
    p_ids = sorted(list(parking_dict[sel_p_floor].keys()), key=lambda x: int(x) if x.isdigit() else x) if sel_p_floor in parking_dict else []
    sel_p_id = st.selectbox("4. 選擇車位號碼：", p_ids if p_ids else ["無資料"])
    
    p_price = parking_dict[sel_p_floor][sel_p_id] if sel_p_floor in parking_dict and sel_p_id in parking_dict[sel_p_floor] else 0
    st.markdown(f"<p style='text-align:right;color:#666;'>車位單價：<span style='color:#d9534f;font-weight:bold;'>{p_price:,}</span> 元</p>", unsafe_allow_html=True)
    
    # 計算總價與找補
    total_price = h_price + p_price
    diff_price = round((total_price - PERSONAL_VALUE) * RATIO)
    
    # 漂亮高質感結果面板
    st.markdown(f"""
    <div style='background: #eef7ff; padding: 12px; border-radius: 4px; text-align: center; font-size: 1.2em; font-weight: bold; color: #0056b3; border: 1px solid #bce8f1; margin-bottom: 8px;'>
        總計金額：{total_price:,} 元
    </div>
    <div style='background: #fdfdfd; padding: 12px; border-radius: 4px; text-align: center; font-size: 1.1em; font-weight: bold; color: #333; border: 1px solid #ddd; margin-bottom: 8px; line-height: 1.5;'>
        個人權值金額：29,393,269 元<br>找補比率：95%
    </div>
    <div style='background: #fff4e5; padding: 12px; border-radius: 4px; text-align: center; font-size: 1.2em; font-weight: bold; color: #e67e22; border: 1px solid #ffe5b4;'>
        找補金額：{diff_price:,} 元
    </div>
    """, unsafe_allow_html=True)

# --- 右側：自動圖面對照欄 ---
with col2:
    st.subheader("🗺️ 樓層與車位圖面參考")
    
    # 1. 房屋圖面自動判定
    st.markdown(f"#### 🏠 房屋：{sel_floor} 平面圖")
    try:
        f_num = int(sel_floor.replace('F',''))
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
            st.caption("💡 暫無此樓層圖檔")
    except:
        st.caption("無法解析樓層。")

    st.write("---")

    # 2. 車位圖面自動判定
    st.markdown(f"#### 🚗 車位：{sel_p_floor} 平面圖")
    p_img_file = os.path.join('maps', f"parking_{sel_p_floor}.png")
    
    if os.path.exists(p_img_file):
        st.image(p_img_file, use_column_width=True)
    else:
        st.caption("💡 暫無此車位圖檔")
