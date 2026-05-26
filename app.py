import streamlit as st
import pandas as pd  # 假設您原本有用到 pandas

# 1. 這裡放您原本的 Python 核心邏輯/運算功能
def my_original_function(name):
    return f"處理後的資料：{name}"

# 2. 這裡放 Streamlit 的網頁介面程式碼
st.title("🚀 我的獨立網頁")
user_input = st.text_input("請輸入資料：")

if st.button("開始執行"):
    # 呼叫您原本的功能
    result = my_original_function(user_input)
    st.success(result)
