import pandas as pd
import os

def load_house_and_parking(path):
    # 讀取 Excel 內所有分頁名稱
    excel_file = pd.ExcelFile(path)
    sheets = excel_file.sheet_names
    
    # 防呆：強制指定第一張工作表為房屋，第二張為車位
    house_df = pd.read_excel(path, sheet_name=sheets[0])
    parking_df = pd.read_excel(path, sheet_name=sheets[1]) if len(sheets) > 1 else house_df
    
    # 欄位名稱去空格、統一化
    house_df.columns = [str(c).strip() for c in house_df.columns]
    parking_df.columns = [str(c).strip() for c in parking_df.columns]
    
    # 建立房屋 Python 字典
    h_dict = {}
    for _, row in house_df.iterrows():
        f = str(row['樓層']).strip()
        u = str(row['戶型']).strip()
        p = int(row['總價(元)'])
        if f not in h_dict: h_dict[f] = {}
        h_dict[f][u] = p
        
    # 建立車位 Python 字典
    p_dict = {}
    for _, row in parking_df.iterrows():
        l = str(row['地下樓層']).strip()
        pid = str(row['車位號碼']).strip()
        p = int(row['總價(元)'])
        if l not in p_dict: p_dict[l] = {}
        p_dict[l][pid] = p
        
    return h_dict, p_dict
