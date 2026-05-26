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
# 1. 超級防呆：自動按順序讀取 Excel 資料
# ==========================================
@st.cache_data
def load_data(path):
    # 讀取整本 Excel
    excel_file = pd.ExcelFile(path)
    sheet_names = excel_file.sheet_names
    
    # 防呆：直接依順序抓取第一張與第二張工作表（不管它叫什麼名字）
    house_df = pd.read_excel(path, sheet_name=sheet_names[0])
    parking_df = pd.read_excel(path, sheet_name=sheet_names[1]) if len(sheet_names) > 1 else house_df
    
    # 建立房屋 Python 字典
    h_dict = {}
    for _, row in house_df.iterrows():
        f, u, p = str(row['樓層']), str(row['戶型']), int(row['總價(元)'])
        if f not in h_dict: h_dict[f] = {}
        h_dict[f][u] = p
        
    # 建立車位 Python 字典
    p_dict = {}
    for _, row in parking_df.iterrows():
        l, pid, p = str(row['地下樓層']), str(row['車位號碼']), int(row['總價(元)'])
        if l not in p_dict: p_dict[l] = {}
        p_dict[l][pid] = p
        
    return h_dict, p_dict

try:
    house_dict, parking_dict = load_data(excel_path)
    has_data = True
except Exception as e:
    st.error(f"資料解讀失敗！請確認 data 資料夾內有放「價格表.xlsx」，且欄位名稱包含：樓層、戶型、總價(元)、地下樓層、車位號碼。")
    house_dict, parking_dict = {}, {}
    has_data = False

# 常數設定
PERSONAL_VALUE = 29393269
RATIO = 0.95

# ==========================================
# 2. 定義左右雙欄排版 (高質感網頁風格)
# ==========================================
# 注入自訂 CSS，讓 Streamlit 預設選單和排版變得跟原本的網頁一樣精美有質感
st.markdown("""
    <style>
        .custom-card {
            font-family: "Microsoft JhengHei", sans-serif;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background: #fff;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            margin-bottom: 15px;
        }
        .sub-price { font-size: 0.9em; color: #666; text-align: right; margin-top: -10px; margin-bottom: 15px; }
        .price-val { color: #d9534f; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1.2])

# --- 左側：高質感對照計算機 ---
with col1:
    st.markdown("### 📊 數據試算欄")
    
    # 使用容器包起來，做出漂亮的陰影外框卡片
    with st.container():
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center; color:#333; margin-top:0; font-size:22px;'>選屋找補計算機</h2>", unsafe_allow_html=True)
        
        # --- 房屋區 ---
        st.markdown("<b style='color:#555;'>選擇樓層：</b>", unsafe_allow_html=True)
        floors = sorted(list(house_dict.keys())) if has_data else []
        sel_floor = st.selectbox("floor_hidden", floors if floors else ["無資料"], label_visibility="collapsed")
        
        st.markdown("<b style='color:#555;'>選擇戶型：</b>", unsafe_allow_html=True)
        units = sorted(list(house_dict[sel_floor].keys())) if sel_floor in house_dict else []
        sel_unit = st.selectbox("unit_hidden", units if units else ["無資料"], label_visibility="collapsed")
        
        h_price = house_dict[sel_floor][sel_unit] if sel_floor in house_dict and sel_unit in house_dict[sel_floor] else 0
        st.markdown(f'<div class="sub-price">房屋單價：<span class="price-val">{h_price:,}</span> 元</div>', unsafe_allow_html=True)
        
        # --- 車位區 ---
        st.markdown("<b style='color:#555;'>選擇車位樓層：</b>", unsafe_allow_html=True)
        p_floors = sorted(list(parking_dict.keys())) if has_data else []
        sel_p_floor = st.selectbox("p_floor_hidden", p_floors if p_floors else ["無資料"], label_visibility="collapsed")
        
        st.markdown("<b style='color:#555;'>選擇車位號碼：</b>", unsafe_allow_html=True)
        p_ids = sorted(list(parking_dict[sel_p_floor].keys()), key=lambda x: int(x) if x.isdigit() else x) if sel_p_floor in parking_dict else []
        sel_p_id = st.selectbox("pid_hidden", p_ids if p_ids else ["無資料"], label_visibility="collapsed")
        
        p_price = parking_dict[sel_p_floor][sel_p_id] if sel_p_floor in parking_dict and sel_p_id in parking_dict[sel_p_floor] else 0
        st.markdown(f'<div class="sub-price">車位單價：<span class="price-val">{p_price:,}</span> 元</div>', unsafe_allow_html=True)
        
        # 計算數值
        total_price = h_price + p_price
        diff_price = round((total_price - PERSONAL_VALUE) * RATIO)
        
        # 三色面板區
        st.markdown(f"""
            <div style='background: #eef7ff; padding: 12px; border-radius: 4px; text-align: center; font-size: 1.2em; font-weight: bold; color: #0056b3; border: 1px solid #bce8f1; margin-bottom: 10px;'>
                總計金額：{total_price:,} 元
            </div>
            <div style='background: #fdfdfd; padding: 12px; border-radius: 4px; text-align: center; font-size: 1.1em; font-weight: bold; color: #333; border: 1px solid #ddd; margin-bottom: 10px; line-height: 1.6;'>
                個人權值金額：29,393,269元<br>找補比率：95%
            </div>
            <div style='background: #fff4e5; padding: 12px; border-radius: 4px; text-align: center; font-size: 1.2em; font-weight: bold; color: #e67e22; border: 1px solid #ffe5b4;'>
                找補金額：{diff_price:,} 元
            </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- 右側：自動圖面對照欄 ---
with col2:
    st.markdown("### 🗺️ 樓層與車位圖面參考")
    
    # 1. 房屋圖面
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
        st.caption("無法解析樓層圖面。")

    st.markdown("<br><hr>", unsafe_allow_html=True)

    # 2. 車位圖面
    st.markdown(f"#### 🚗 車位：{sel_p_floor} 平面圖")
    p_img_file = os.path.join('maps', f"parking_{sel_p_floor}.png")
    
    if os.path.exists(p_img_file):
        st.image(p_img_file, use_column_width=True)
    else:
        st.caption("💡 暫無此車位圖檔")
