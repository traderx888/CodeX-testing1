import requests
from bs4 import BeautifulSoup
import gspread
from google.oauth2.service_account import Credentials
import time

def setup_google_sheets():
    # 设置 Google Sheets API 的权限范围
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    # 加载服务账号凭证
    # 注意：您需要先创建服务账号并下载 JSON 凭证文件
    credentials = Credentials.from_service_account_file(
        'your-credentials.json',  # 替换为您的凭证文件路径
        scopes=scopes
    )
    
    # 创建 gspread 客户端
    client = gspread.authorize(credentials)
    
    # 打开或创建电子表格
    try:
        spreadsheet = client.open('Web Scraping Results')  # 如果已存在则打开
    except:
        spreadsheet = client.create('Web Scraping Results')  # 如果不存在则创建
    
    return spreadsheet

def scrape_webpage(url):
    try:
        # 发送 HTTP 请求
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
        
        # 打印网页源码（用于调试）
        print("网页源码：")
        print(response.text[:1000])  # 只打印前1000个字符
        
        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找所有表格
        tables = soup.find_all('table')
        
        if not tables:
            print("未找到表格！")
            return None
            
        # 获取第一个表格的数据
        table = tables[0]
        rows = table.find_all('tr')
        
        # 提取数据
        data = []
        for row in rows:
            cols = row.find_all(['td', 'th'])
            row_data = [col.text.strip() for col in cols]
            if row_data:  # 只添加非空行
                data.append(row_data)
        
        return data
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return None

def update_spreadsheet(spreadsheet, data):
    if not data:
        print("没有数据要写入！")
        return
    
    # 选择第一个工作表
    worksheet = spreadsheet.sheet1
    
    # 清除现有内容
    worksheet.clear()
    
    # 写入新数据
    worksheet.update('A1', data)
    
    print("数据已成功写入 Google Spreadsheets！")

def main():
    # 示例网页 URL（请替换为您要爬取的实际网页 URL）
    url = "https://example.com/table"  # 替换为实际的网页 URL
    
    print("开始爬取网页...")
    data = scrape_webpage(url)
    
    if data:
        print("\n提取的数据：")
        for row in data:
            print(row)
        
        print("\n正在连接到 Google Spreadsheets...")
        spreadsheet = setup_google_sheets()
        
        print("正在更新电子表格...")
        update_spreadsheet(spreadsheet, data)
    else:
        print("未能获取数据！")

if __name__ == "__main__":
    main() 