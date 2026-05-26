import streamlit as st
import pandas as pd
import json

# 設定網頁標題與圖示（讓瀏覽器分頁更好看）
st.set_page_config(page_title="選屋找補計算機", page_icon="🏡", layout="centered")

# ==========================================
# 1. 讀取 Excel 資料
# ==========================================
# 這裡將路徑改為當前目錄，請記得將 Excel 檔上傳到 GitHub
excel_path = '價格表.xlsx'

@st.cache_data  # 加上快取，避免每次操作網頁都重複讀取 Excel，速度會變極快
def load_data(path):
    excel_data = pd.read_excel(path, sheet_name=None)
    
    # 處理房屋資料
    house_df = excel_data['房屋底價資料庫']
    house_data_dict = {}
    for _, row in house_df.iterrows():
        floor = str(row['樓層'])
        unit = str(row['戶型'])
        price = int(row['總價(元)'])
        if floor not in house_data_dict:
            house_data_dict[floor] = {}
        house_data_dict[floor][unit] = price

    # 處理車位資料
    parking_df = excel_data['車位底價資料庫']
    parking_data_dict = {}
    for _, row in parking_df.iterrows():
        level = str(row['地下樓層'])
        p_id = str(row['車位號碼'])
        price = int(row['總價(元)'])
        if level not in parking_data_dict:
            parking_data_dict[level] = {}
        parking_data_dict[level][p_id] = price
        
    return json.dumps(house_data_dict, ensure_ascii=False), json.dumps(parking_data_dict, ensure_ascii=False)

# 執行讀取
try:
    house_json, parking_json = load_data(excel_path)
except Exception as e:
    st.error(f"找不到 Excel 檔案！請確保「宸熙全安_底價表_結構化資料.xlsx」已上傳至 GitHub。")
    house_json, parking_json = "{}", "{}"

# ==========================================
# 2. 將您原本完美的 HTML/CSS/JS 渲染至網頁
# ==========================================
html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <style>
        .container {{ font-family: "Microsoft JhengHei", sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; background: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .section {{ margin-bottom: 20px; padding: 15px; border: 1px solid #eee; border-radius: 4px; }}
        h2 {{ color: #333; text-align: center; margin-top: 0; }}
        label {{ display: block; margin: 10px 0 5px; font-weight: bold; color: #555; }}
        select {{ width: 100%; padding: 8px; margin-bottom: 10px; border-radius: 4px; border: 1px solid #ccc; background-color: #f9f9f9; font-size: 14px; }}
        .sub-price {{ font-size: 0.9em; color: #666; margin-bottom: 10px; text-align: right; }}
        .price-val {{ color: #d9534f; font-weight: bold; }}
        .result-box {{ background: #eef7ff; padding: 15px; border-radius: 4px; text-align: center; font-size: 1.3em; font-weight: bold; color: #0056b3; border: 1px solid #bce8f1; margin-bottom: 10px; }}
        .info-box {{ background: #fdfdfd; padding: 15px; border-radius: 4px; text-align: center; font-size: 1.3em; font-weight: bold; color: #000; border: 1px solid #ddd; margin-bottom: 10px; line-height: 1.6; }}
        .diff-box {{ background: #fff4e5; padding: 15px; border-radius: 4px; text-align: center; font-size: 1.3em; font-weight: bold; color: #e67e22; border: 1px solid #ffe5b4; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>選屋找補計算機</h2>

        <div class="section">
            <label>選擇樓層：</label>
            <select id="floorSelect" onchange="updateUnits()"></select>
            <label>選擇戶型：</label>
            <select id="unitSelect" onchange="calculate()"></select>
            <div class="sub-price">房屋單價：<span id="housePriceVal" class="price-val">0</span> 元</div>
        </div>

        <div class="section">
            <label>選擇車位樓層：</label>
            <select id="pFloorSelect" onchange="updateParkingIds()"></select>
            <label>選擇車位號碼：</label>
            <select id="pIdSelect" onchange="calculate()"></select>
            <div class="sub-price">車位單價：<span id="parkingPriceVal" class="price-val">0</span> 元</div>
        </div>

        <div class="result-box">
            總計金額：<span id="totalPrice">0</span> 元
        </div>

        <div class="info-box">
            個人權值金額：29,393,269元<br>
            找補比率：95%
        </div>

        <div class="diff-box">
            找補金額：<span id="reimbursementPrice">0</span> 元
        </div>
    </div>

    <script>
        const houseData = {house_json};
        const parkingData = {parking_json};
        const personalValue = 29393269;
        const ratio = 0.95;

        function init() {{
            const floorSelect = document.getElementById('floorSelect');
            const pFloorSelect = document.getElementById('pFloorSelect');

            Object.keys(houseData).sort().forEach(f => {{
                let opt = new Option(f, f);
                floorSelect.add(opt);
            }});

            Object.keys(parkingData).sort().forEach(pf => {{
                let opt = new Option(pf, pf);
                pFloorSelect.add(opt);
            }});

            updateUnits();
            updateParkingIds();
        }}

        function updateUnits() {{
            const floor = document.getElementById('floorSelect').value;
            const unitSelect = document.getElementById('unitSelect');
            if(!floor) return;
            unitSelect.innerHTML = '';
            Object.keys(houseData[floor]).sort().forEach(u => {{
                unitSelect.add(new Option(u, u));
            }});
            calculate();
        }}

        function updateParkingIds() {{
            const pFloor = document.getElementById('pFloorSelect').value;
            const pIdSelect = document.getElementById('pIdSelect');
            if(!pFloor) return;
            pIdSelect.innerHTML = '';
            Object.keys(parkingData[pFloor]).sort((a,b)=>a-b).forEach(p => {{
                pIdSelect.add(new Option(p, p));
            }});
            calculate();
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

# 使用 Streamlit components 直接渲染原生 HTML/JS，並放大高度避免捲軸出現
st.components.v1.html(html_content, height=850, scrolling=False)
