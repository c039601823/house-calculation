import streamlit as st
import pandas as pd
import json
import os
from streamlit_components_auth import html # 引入自訂組件，若無則使用內建，這裡用內建改良

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
    house_data_dict = {}
    for _, row in house_df.iterrows():
        floor = str(row['樓層'])
        unit = str(row['戶型'])
        price = int(row['總價(元)'])
        if floor not in house_data_dict:
            house_data_dict[floor] = {}
        house_data_dict[floor][unit] = price

    parking_df = excel_data[parking_sheet] if parking_sheet else excel_data[sheet_names]
    parking_data_dict = {}
    for _, row in parking_df.iterrows():
        level = str(row['地下樓層'])
        p_id = str(row['車位號碼'])
        price = int(row['總價(元)'])
        if level not in parking_data_dict:
            parking_data_dict[level] = {}
        parking_data_dict[level][p_id] = price
        
    return house_data_dict, parking_data_dict, json.dumps(house_data_dict, ensure_ascii=False), json.dumps(parking_data_dict, ensure_ascii=False)

try:
    house_dict, parking_dict, house_json, parking_json = load_data(excel_path)
except Exception as e:
    st.error(f"安全性讀取失敗！請確保已在 data 資料夾中放入正確的 Excel 檔案。")
    house_dict, parking_dict, house_json, parking_json = {}, {}, "{}", "{}"

# ==========================================
# 2. 初始化 Streamlit 狀態暫存（用來記住當前看哪張圖）
# ==========================================
# 利用網址參數 (Query Params) 來當作 HTML 與 Python 之間的橋樑，免安裝外掛
query_params = st.query_params
current_floor = query_params.get("f", sorted(list(house_dict.keys()))[0] if house_dict else "3F")
current_p_floor = query_params.get("p", sorted(list(parking_dict.keys()))[0] if parking_dict else "B1")

# ==========================================
# 3. 定義左右雙欄排版
# ==========================================
col1, col2 = st.columns([1, 1.2]) # 左邊放計算機，右邊放平面圖

with col1:
    # 渲染純粹的計算機網頁（內嵌網址同步 JavaScript）
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .container {{ font-family: "Microsoft JhengHei", sans-serif; max-width: 100%; padding: 15px; border: 1px solid #ddd; border-radius: 8px; background: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .section {{ margin-bottom: 15px; padding: 12px; border: 1px solid #eee; border-radius: 4px; }}
            h2 {{ color: #333; text-align: center; margin-top: 0; font-size: 20px; }}
            label {{ display: block; margin: 8px 0 3px; font-weight: bold; color: #555; }}
            select {{ width: 100%; padding: 8px; margin-bottom: 8px; border-radius: 4px; border: 1px solid #ccc; background-color: #f9f9f9; font-size: 15px; }}
            .sub-price {{ font-size: 0.9em; color: #666; margin-bottom: 8px; text-align: right; }}
            .price-val {{ color: #d9534f; font-weight: bold; }}
            .result-box {{ background: #eef7ff; padding: 12px; border-radius: 4px; text-align: center; font-size: 1.2em; font-weight: bold; color: #0056b3; border: 1px solid #bce8f1; margin-bottom: 8px; }}
            .info-box {{ background: #fdfdfd; padding: 12px; border-radius: 4px; text-align: center; font-size: 1.2em; font-weight: bold; color: #000; border: 1px solid #ddd; margin-bottom: 8px; line-height: 1.5; }}
            .diff-box {{ background: #fff4e5; padding: 12px; border-radius: 4px; text-align: center; font-size: 1.2em; font-weight: bold; color: #e67e22; border: 1px solid #ffe5b4; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🏡 選屋找補計算機</h2>
            <div class="section">
                <label>選擇樓層：</label>
                <select id="floorSelect" onchange="syncToStreamlit()"></select>
                <label>選擇戶型：</label>
                <select id="unitSelect" onchange="calculate()"></select>
                <div class="sub-price">房屋單價：<span id="housePriceVal" class="price-val">0</span> 元</div>
            </div>
            <div class="section">
                <label>選擇車位樓層：</label>
                <select id="pFloorSelect" onchange="syncToStreamlit()"></select>
                <label>選擇車位號碼：</label>
                <select id="pIdSelect" onchange="calculate()"></select>
                <div class="sub-price">車位單價：<span id="parkingPriceVal" class="price-val">0</span> 元</div>
            </div>
            <div class="result-box">總計金額：<span id="totalPrice">0</span> 元</div>
            <div class="info-box">個人權值金額：29,393,269元<br>找補比率：95%</div>
            <div class="diff-box">找補金額：<span id="reimbursementPrice">0</span> 元</div>
        </div>
        <script>
            const houseData = {house_json};
            const parkingData = {parking_json};
            const personalValue = 29393269;
            const ratio = 0.95;

            function init() {{
                const floorSelect = document.getElementById('floorSelect');
                const pFloorSelect = document.getElementById('pFloorSelect');
                Object.keys(houseData).sort().forEach(f => {{ floorSelect.add(new Option(f, f)); }});
                Object.keys(parkingData).sort().forEach(pf => {{ pFloorSelect.add(new Option(pf, pf)); }});
                
                // 記住前一次選取的數值
                floorSelect.value = "{current_floor}";
                pFloorSelect.value = "{current_p_floor}";
                
                updateUnits(false);
                updateParkingIds(false);
                calculate();
            }}

            // 當切換樓層時，通知外層 Streamlit 刷新圖片
            function syncToStreamlit() {{
                const floor = document.getElementById('floorSelect').value;
                const pFloor = document.getElementById('pFloorSelect').value;
                
                // 透過修改 parent 網址參數即時連動 Streamlit
                const newUrl = window.parent.location.protocol + "//" + window.parent.location.host + window.parent.location.pathname + "?f=" + floor + "&p=" + pFloor;
                window.parent.history.replaceState({{path:newUrl}}, '', newUrl);
                
                // 強制觸發 Streamlit 的重新渲染機制
                window.parent.postMessage({{type: 'streamlit:set_page_config'}}, '*');
                
                updateUnits(true);
                updateParkingIds(true);
            }}

            function updateUnits(shouldCalc) {{
                const floor = document.getElementById('floorSelect').value;
                const unitSelect = document.getElementById('unitSelect');
                if(!floor) return;
                const prevVal = unitSelect.value;
                unitSelect.innerHTML = '';
                Object.keys(houseData[floor]).sort().forEach(u => {{ unitSelect.add(new Option(u, u)); }});
                if(prevVal && houseData[floor][prevVal]) unitSelect.value = prevVal;
                if(shouldCalc) calculate();
            }}

            function updateParkingIds(shouldCalc) {{
                const pFloor = document.getElementById('pFloorSelect').value;
                const pIdSelect = document.getElementById('pIdSelect');
                if(!pFloor) return;
                const prevVal = pIdSelect.value;
                pIdSelect.innerHTML = '';
                Object.keys(parkingData[pFloor]).sort((a,b)=>a-b).forEach(p => {{ pIdSelect.add(new Option(p, p)); }});
                if(prevVal && parkingData[pFloor][prevVal]) pIdSelect.value = prevVal;
                if(shouldCalc) calculate();
            }}

            function calculate() {{
                const floor = document.getElementById('floorSelect').value;
                const unit = document.getElementById('unitSelect').value;
                const pFloor = document.getElementById('pFloorSelect').value;
                const pId = document.getElementById('pIdSelect').value;
                if(!floor || !unit || !pFloor || !pId) return;
                const hPrice = houseData[floor][unit] || 0;
                const pPrice = parkingData[pFloor][pId] || 0;
                const total = hPrice + pPrice;
                const diffPrice = (total - personalValue) * ratio;
                document.getElementById('housePriceVal').innerText = hPrice.toLocaleString();
                document.getElementById('parkingPriceVal').innerText = pPrice.toLocaleString();
                document.getElementById('totalPrice').innerText = total.toLocaleString();
                document.getElementById('reimbursementPrice').innerText = Math.round(diffPrice).toLocaleString();
            }}
            init();
        </script>
    </body>
    </html>
    '''
    # 完美高度
    st.components.v1.html(html_content, height=710, scrolling=False)

# ==========================================
# 4. 右側智慧圖面檢索區（完美去重複、全自動同步連動）
# ==========================================
with col2:
    st.markdown("### 🗺️ 樓層與車位圖面參考")
    
    # 房屋圖面
    st.subheader(f"🏠 房屋：{current_floor} 平面圖")
    try:
        f_num = int(current_floor.replace('F',''))
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
            st.info(f"💡 暫無此樓層圖檔或正在載入中（路徑：{img_file}）")
    except:
        st.info("無法解析樓層圖片。")

    st.write("---")

    # 車位圖面邏輯
    st.subheader(f"🚗 車位：{selected_p_floor} 平面圖")
    p_img_file = os.path.join('maps', f"parking_{selected_p_floor}.png")
    
    if os.path.exists(p_img_file):
        st.image(p_img_file, use_column_width=True)
    else:
        st.info(f"💡 暫無此車位圖檔或正在載入中（路徑：{p_img_file}）")
