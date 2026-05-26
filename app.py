import streamlit as st
import os

# 設定網頁為寬螢幕模式
st.set_page_config(page_title="選屋找補對照系統", page_icon="🏡", layout="wide")

# 引入區塊一的資料讀取模組
if os.path.exists('app_data.py'):
    import app_data
else:
    with open('app_data.py', 'w') as f: f.write("")
    import app_data

# 安全讀取
excel_path = os.path.join('data', '價格表.xlsx')
try:
    house_json, parking_json = app_data.get_clean_json(excel_path)
except:
    house_json, parking_json = "{}", "{}"

# 強力清除 Streamlit 頂部殘留白條與框架
st.markdown("""
    <style>
        .block-container { padding-top: 0.5rem !important; padding-bottom: 0.5rem !important; }
        [data-testid="stHeader"] { display: none !important; }
        div[data-testid="stVerticalBlock"] > div { padding: 0px !important; margin: 0px !important; }
        .right-title {
            font-family: "Microsoft JhengHei", sans-serif;
            font-size: 24px; font-weight: bold; color: #1a1a1a;
            padding-top: 15px !important; padding-bottom: 12px !important;
            line-height: 1.6 !important; border-bottom: 2px solid #eaeaea;
            margin-bottom: 20px !important;
        }
    </style>
""", unsafe_allow_html=True)

# 動態解析當前網址參數，用來更新右側圖面
query_params = st.query_params
current_floor = query_params.get("f", "15F")
current_p_floor = query_params.get("p", "B2")

col1, col2 = st.columns([1, 1.2])

# --- 左側：網頁找補計算機 ---
with col1:
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .container {{ font-family: "Microsoft JhengHei", sans-serif; max-width: 100%; padding: 20px; border: 1px solid #e1e4e8; border-radius: 12px; background: #fff; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-top: 15px; }}
            .section {{ margin-bottom: 18px; padding: 14px; border: 1px solid #eee; border-radius: 6px; }}
            h2 {{ color: #222; text-align: center; margin-top: 0; font-size: 22px; font-weight: bold; }}
            label {{ display: block; margin: 10px 0 5px; font-weight: bold; color: #444; font-size: 15px; }}
            select {{ width: 100%; padding: 10px; margin-bottom: 10px; border-radius: 6px; border: 1px solid #ccc; background-color: #f9f9f9; font-size: 15px; }}
            .sub-price {{ font-size: 0.92em; color: #666; margin-bottom: 8px; text-align: right; }}
            .price-val {{ color: #d9534f; font-weight: bold; font-size: 1.05em; }}
            .result-box {{ background: #eef7ff; padding: 14px; border-radius: 6px; text-align: center; font-size: 1.25em; font-weight: bold; color: #0056b3; border: 1px solid #bce8f1; margin-bottom: 12px; }}
            .info-box {{ background: #fafafa; padding: 14px; border-radius: 6px; text-align: center; font-size: 1.1em; font-weight: bold; color: #444; border: 1px solid #e1e4e8; margin-bottom: 12px; line-height: 1.6; }}
            .diff-box {{ background: #fff4e5; padding: 14px; border-radius: 6px; text-align: center; font-size: 1.25em; font-weight: bold; color: #e67e22; border: 1px solid #ffe5b4; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>選屋找補計算機</h2>
            <div class="section">
                <label>選擇樓層：</label>
                <select id="floorSelect" onchange="sync()"></select>
                <label>選擇戶型：</label>
                <select id="unitSelect" onchange="calculate()"></select>
                <div class="sub-price">房屋單價：<span id="housePriceVal" class="price-val">0</span> 元</div>
            </div>
            <div class="section">
                <label>選擇車位樓層：</label>
                <select id="pFloorSelect" onchange="sync()"></select>
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
                const fs = document.getElementById('floorSelect');
                const pfs = document.getElementById('pFloorSelect');
                
                Object.keys(houseData).sort((a,b)=>parseInt(a)-parseInt(b)).forEach(f => fs.add(new Option(f, f)));
                Object.keys(parkingData).sort((a,b)=>parseInt(a)-parseInt(b)).forEach(pf => pfs.add(new Option(pf, pf)));
                
                if(houseData["{current_floor}"]) fs.value = "{current_floor}";
                if(parkingData["{current_p_floor}"]) pfs.value = "{current_p_floor}";
                
                updateUnits(false);
                updateParkingIds(false);
                calculate();
            }}

            function sync() {{
                const f = document.getElementById('floorSelect').value;
                const p = document.getElementById('pFloorSelect').value;
                const url = window.parent.location.protocol + "//" + window.parent.location.host + window.parent.location.pathname + "?f=" + f + "&p=" + p;
                window.parent.history.replaceState({{path:url}}, '', url);
                window.parent.postMessage({{type: 'streamlit:set_page_config'}}, '*');
                updateUnits(true);
                updateParkingIds(true);
            }}

            function updateUnits(c) {{
                const f = document.getElementById('floorSelect').value;
                const us = document.getElementById('unitSelect');
                if(!f) return; const v = us.value; us.innerHTML = '';
                Object.keys(houseData[f]).sort().forEach(u => us.add(new Option(u, u)));
                if(v && houseData[f][v]) us.value = v;
                if(c) calculate();
            }}

            function updateParkingIds(c) {{
                const pf = document.getElementById('pFloorSelect').value;
                const pids = document.getElementById('pIdSelect');
                if(!pf) return; const v = pids.value; pids.innerHTML = '';
                Object.keys(parkingData[pf]).sort((a,b)=>a-b).forEach(p => pids.add(new Option(p, p)));
                if(v && parkingData[pf][v]) pids.value = v;
                if(c) calculate();
            }}

            function calculate() {{
                const f = document.getElementById('floorSelect').value;
                const u = document.getElementById('unitSelect').value;
                const pf = document.getElementById('pFloorSelect').value;
                const p = document.getElementById('pIdSelect').value;
                if(!f || !u || !pf || !p) return;
                const hp = houseData[f][u] || 0;
                const pp = parkingData[pf][p] || 0;
                const total = hp + pp;
                const diff = (total - personalValue) * ratio;
                document.getElementById('housePriceVal').innerText = hp.toLocaleString();
                document.getElementById('parkingPriceVal').innerText = pp.toLocaleString();
                document.getElementById('totalPrice').innerText = total.toLocaleString();
                document.getElementById('reimbursementPrice').innerText = Math.round(diff).toLocaleString();
            }}
            init();
        </script>
    </body>
    </html>
    '''
    st.components.v1.html(html_content, height=680, scrolling=False)

# --- 右側：自動圖面對照欄（防裁切優化版） ---
with col2:
    st.markdown('<div class="right-title">📖 樓層與車位圖面參考</div>', unsafe_allow_html=True)
    
    st.markdown(f"#### 🏠 房屋：{current_floor} 平面圖")
    try:
        f_num = int(current_floor.upper().replace('F',''))
        img_file = os.path.join('maps', 'floor_3.png' if f_num == 3 else 'floor_4_14.png' if 4 <= f_num <= 14 else 'floor_15_24.png' if 15 <= f_num <= 24 else '')
        if img_file and os.path.exists(img_file):
            st.image(img_file, use_column_width=True)
        else:
            st.caption("💡 暫無此樓層對應圖檔")
    except:
        st.caption("無法解析樓層圖面。")

    st.markdown("<br><hr>", unsafe_allow_html=True)

    st.markdown(f"#### 🚗 車位：{current_p_floor} 平面圖")
    p_img_file = os.path.join('maps', f"parking_{current_p_floor}.png")
    if os.path.exists(p_img_file):
        st.image(p_img_file, use_column_width=True)
    else:
        st.caption("💡 暫無此車位對應圖檔")
