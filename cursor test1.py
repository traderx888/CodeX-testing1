import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import html5lib
import time
import random
import os

def calculate_sma(data, window):
    """
    計算簡單移動平均線 (Simple Moving Average, SMA)
    
    參數:
    data (list, numpy array, or pandas Series): 輸入的價格數據
    window (int): 移動平均的期間長度
    
    回傳:
    numpy array: SMA 數值陣列
    """
    # 確保輸入數據是 numpy array
    data = np.array(data)
    # 使用 numpy 的 convolve 函數計算移動平均
    sma = np.convolve(data, np.ones(window)/window, mode='valid')
    return sma

def calculate_sma_pandas(data, window):
    """
    使用 pandas 計算簡單移動平均線 (SMA)
    
    參數:
    data (pandas Series): 輸入的價格數據
    window (int): 移動平均的期間長度
    
    回傳:
    pandas Series: SMA 數值序列
    """
    return data.rolling(window=window).mean()

def scrape_btc_data():
    """
    爬取 BTC 網頁數據並保存為 CSV
    """
    # 設定網址
    url = 'https://farside.co.uk/btc/'
    
    # 設定請求頭，模擬瀏覽器訪問
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    try:
        # 發送請求獲取網頁內容
        print("正在獲取網頁內容...")
        response = requests.get(url, headers=headers)
        response.encoding = response.apparent_encoding
        
        # 檢查請求是否成功
        print(f"網頁狀態碼: {response.status_code}")
        if response.status_code != 200:
            print("獲取網頁失敗！")
            return
        
        # 保存網頁源碼以供檢查
        print("保存網頁源碼...")
        with open('webpage.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("網頁源碼已保存到 webpage.html")
        
        # 解析網頁內容
        print("正在解析網頁內容...")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找所有表格
        tables = soup.find_all('table')
        print(f"找到 {len(tables)} 個表格")
        
        # 如果沒有找到表格，嘗試其他方法
        if not tables:
            print("使用 find_all 未找到表格，嘗試其他方法...")
            tables = soup.select('table')
            print(f"使用 select 找到 {len(tables)} 個表格")
        
        # 處理找到的表格
        for i, table in enumerate(tables):
            try:
                # 將表格轉換為 DataFrame
                df = pd.read_html(str(table))[0]
                
                # 保存為 CSV 文件
                filename = f'btc_table_{i+1}.csv'
                df.to_csv(filename, index=False, encoding='utf-8-sig')
                print(f"表格 {i+1} 已保存到 {filename}")
                
                # 顯示表格的前幾行
                print(f"\n表格 {i+1} 的前5行數據：")
                print(df.head())
                print("\n" + "="*50 + "\n")
                
            except Exception as e:
                print(f"處理表格 {i+1} 時發生錯誤: {str(e)}")
        
        print("\n所有表格處理完成！")
        
    except Exception as e:
        print(f"發生錯誤: {str(e)}")

# 下載蘋果公司股票數據
if __name__ == "__main__":
    print("開始爬取 BTC 數據...")
    scrape_btc_data()
    print("\n程式執行完成！")
