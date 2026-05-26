import streamlit as st
import os

# 設定網頁為寬螢幕模式
st.set_page_config(page_title="選屋找補對照系統", page_icon="🏡", layout="wide")

# 引入資料讀取器
if os.path.exists('app_data.py'):
    import app_data
else:
    with open('app_data.py', 'w') as f: f.write("")
    import app_data

# 安全讀取價格表
excel_path = os.path.join('data', '價格表.xlsx')
try:
    house_dict, parking_dict = app_data.load_house_and_parking(excel_path)
    has_data = True
except Exception as e:
    st.error(f"資料讀取失敗！請確保 data 資料夾內有放「價格表.xlsx」檔案。")
    house_dict, parking_dict = {}, {}
    has_data = False

# 常數設定
PERSONAL_VALUE = 29393269
RATIO = 0.95

# 強力清洗頂部多餘間距與客製化美化外框
st.markdown("""
    <style>
        .block-container { padding-top: 1.5rem !important; padding-bottom: 1.5rem !important; }
        [data-testid="stHeader"] { display: none !important; }
        
        /* 客製化精美卡片外框 */
        .custom-card {
            font-family: "Microsoft JhengHei", sans-serif;
            padding: 24px;
            border: 1px solid #e1e4e8;
            border-radius: 12px;
            background: #ffffff;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }
        .sub-price { font-size: 0.92em; color: #666; text-align: right; margin-top: -8px; margin-bottom: 18px; }
        .price-val { color: #d9534f; font-weight: bold; font-size: 1.05em; }
    </style>
""", unsafe_allow_html=True)

# 智慧排序函式：確保下拉選單按照 3F, 4F... 順序排列
def sort_floors(floor_list):
    return sorted(floor_list, key=lambda x: int(x.upper().replace('F','')) if x.upper().replace('F','').isdigit() else 99)

def sort_parking_levels(level_list):
    return sorted(level_list, key=lambda x: int(x.upper().replace('B','')) if x.upper().replace('B','').isdigit() else 99)

# 進行左右雙欄配置
col1, col2 = st.columns([1, 1.2])

# --- 左側：高質感原生看屋計算機 ---
with col1:
    st.markdown("### 📊 數據試算欄")
    
    with st.container():
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center; color:#222; margin-top:0; font-size:22px; font-weight:bold;'>選屋找補計算機</h2>", unsafe_allow_html=True)
        
        # --- 房屋下拉選單 ---
        st.markdown("<span style='color:#444; font-weight:bold; font-size:15px;'>選擇樓層：</span>", unsafe_allow_html=True)
        floors = sort_floors(list(house_dict.keys())) if has_data else []
        sel_floor = st.selectbox("floor_hidden", floors if floors else ["無資料"], label_visibility="collapsed", key="f_select")
        
        st.markdown("<span style='color:#444; font-weight:bold; font-size:15px;'>選擇戶型：</span>", unsafe_allow_html=True)
        units = sorted(list(house_dict[sel_floor].keys())) if sel_floor in house_dict else []
        sel_unit = st.selectbox("unit_hidden", units if units else ["無資料"], label_visibility="collapsed", key="u_select")
        
        h_price = house_dict[sel_floor][sel_unit] if sel_floor in house_dict and sel_unit in house_dict[sel_floor] else 0
        st.markdown(f'<div class="sub-price">房屋單價：<span class="price-val">{h_price:,}</span> 元</div>', unsafe_allow_html=True)
        
        # --- 車位下拉選單 ---
        st.markdown("<span style='color:#444; font-weight:bold; font-size:15px;'>選擇車位樓層：</span>", unsafe_allow_html=True)
        p_floors = sort_parking_levels(list(parking_dict.keys())) if has_data else []
        sel_p_floor = st.selectbox("p_floor_hidden", p_floors if p_floors else ["無資料"], label_visibility="collapsed", key="p_f_select")
        
        st.markdown("<span style='color:#444; font-weight:bold; font-size:15px;'>選擇車位號碼：</span>", unsafe_allow_html=True)
        p_ids = sorted(list(parking_dict[sel_p_floor].keys()), key=lambda x: int(x) if x.isdigit() else x) if sel_p_floor in parking_dict else []
        sel_p_id = st.selectbox("pid_hidden", p_ids if p_ids else ["無資料"], label_visibility="collapsed", key="p_i_select")
        
        p_price = parking_dict[sel_p_floor][sel_p_id] if sel_p_floor in parking_dict and sel_p_id in parking_dict[sel_p_floor] else 0
        st.markdown(f'<div class="sub-price">車位單價：<span class="price-val">{p_price:,}</span> 元</div>', unsafe_allow_html=True)
        
        # 計算試算總金額
        total_price = h_price + p_price
        diff_price = round((total_price - PERSONAL_VALUE) * RATIO)
        
        # 三色看板高質感重現
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

# --- 右側：自動圖面對照欄（100% 保證同步連動） ---
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
            st.caption(f"💡 暫無此樓層圖檔（預期路徑：{img_file}）")
    except:
        st.caption("暫時無法解析樓層。")

    st.markdown("<br><hr>", unsafe_allow_html=True)

    # 2. 車位圖面自動檢索
    st.markdown(f"#### 🚗 車位：{sel_p_floor} 平面圖")
    p_img_file = os.path.join('maps', f"parking_{sel_p_floor}.png")
    
    if os.path.exists(p_img_file):
        st.image(p_img_file, use_column_width=True)
    else:
        st.caption(f"💡 暫無此車位圖檔（預期路徑：{p_img_file}）")
