import pandas as pd
import json
import os

def get_clean_json(path):
    excel_data = pd.read_excel(path, sheet_name=None)
    sheet_names = list(excel_data.keys())
    
    # 智慧比對工作表名稱
    house_sheet = [s for s in sheet_names if '屋' in s or '房' in s]
    parking_sheet = [s for s in sheet_names if '車' in s]
    
    house_df = excel_data[house_sheet[0]] if house_sheet else excel_data[sheet_names[0]]
    parking_df = excel_data[parking_sheet[0]] if parking_sheet else excel_data[sheet_names[-1]]
    
    # 打包房屋資料
    h_dict = {}
    for _, row in house_df.iterrows():
        f, u, p = str(row['樓層']).strip(), str(row['戶型']).strip(), int(row['總價(元)'])
        if f not in h_dict: h_dict[f] = {}
        h_dict[f][u] = p
        
    # 打包車位資料
    p_dict = {}
    for _, row in parking_df.iterrows():
        l, pid, p = str(row['地下樓層']).strip(), str(row['車位號碼']).strip(), int(row['總價(元)'])
        if l not in p_dict: p_dict[l] = {}
        p_dict[l][pid] = p
        
    return json.dumps(h_dict, ensure_ascii=False), json.dumps(p_dict, ensure_ascii=False)
