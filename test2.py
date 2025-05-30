import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import brotli

def get_btc_data():
    print("开始获取数据...")
    
    try:
        # 创建一个cloudscraper实例，使用更详细的配置
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True,
                'mobile': False
            },
            delay=10  # 添加延迟
        )
        
        url = "https://farside.co.uk/btc/"
        print(f"正在访问网址: {url}")
        
        # 添加更多的请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'br, gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        
        print("发送请求...")
        # 使用cloudscraper获取页面
        response = scraper.get(url, headers=headers)
        
        # 打印响应信息
        print(f"HTTP状态码: {response.status_code}")
        print("响应头信息:")
        for key, value in response.headers.items():
            print(f"{key}: {value}")
        
        # 检查响应内容
        print("\n响应内容预览:")
        
        # 处理可能的压缩内容
        content_encoding = response.headers.get('Content-Encoding', '').lower()
        if 'br' in content_encoding:
            content = brotli.decompress(response.content).decode('utf-8')
        elif 'gzip' in content_encoding:
            import gzip
            content = gzip.decompress(response.content).decode('utf-8')
        else:
            content = response.content.decode('utf-8')
            
        print(content[:500])  # 只打印前500个字符
        
        response.raise_for_status()
        
        # 使用BeautifulSoup解析HTML
        print("\n开始解析HTML...")
        soup = BeautifulSoup(content, 'html.parser')
        
        # 查找表格
        print("查找数据表格...")
        table = soup.find('table', class_='etf')
        if not table:
            print("未找到数据表格！")
            print("页面内容:")
            print(soup.prettify()[:1000])  # 打印格式化的HTML前1000个字符
            return
            
        print("找到表格，开始提取数据...")
        
        # 获取表头
        headers = ['Date', 'IBIT', 'FBTC', 'BITB', 'ARKB', 'BTCO', 'EZBC', 'BRRR', 'HODL', 'BTCW', 'GBTC', 'BTC', 'Total']
        
        # 获取数据行
        rows = []
        data_rows = table.find_all('tr')[4:]  # 跳过表头行和费用行
        
        print(f"找到 {len(data_rows)} 行数据")
        
        for row in data_rows:
            cols = row.find_all(['td'])
            if len(cols) == 13:  # 确保行有正确的列数
                row_data = []
                for i, col in enumerate(cols):
                    value = col.get_text(strip=True)
                    if i == 0:  # 日期列
                        row_data.append(value)
                    else:  # 数值列
                        try:
                            # 处理带括号的负数
                            if value.startswith('(') and value.endswith(')'):
                                value = '-' + value[1:-1]
                            # 移除逗号并转换为浮点数
                            value = float(value.replace(',', '')) if value != '-' else 0.0
                        except ValueError:
                            value = 0.0
                        row_data.append(value)
                if any(row_data[1:]):  # 如果除了日期外还有其他非零数据
                    rows.append(row_data)
        
        if rows:
            # 创建DataFrame
            df = pd.DataFrame(rows, columns=headers)
            
            # 保存到CSV文件
            output_file = 'btc_etf_data.csv'
            df.to_csv(output_file, index=False, encoding='utf-8')
            print(f"\n数据已成功保存到 {output_file}")
            print("\n数据预览：")
            print(df.head())
            
            # 打印一些统计信息
            print("\n数据统计：")
            print(f"总行数：{len(df)}")
            print(f"总列数：{len(df.columns)}")
        else:
            print("未找到有效的数据行！")
            
    except Exception as e:
        print(f"发生错误：{str(e)}")
        import traceback
        print("\n详细错误信息：")
        print(traceback.format_exc())

if __name__ == "__main__":
    get_btc_data()
