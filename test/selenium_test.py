from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv

print("Setting up Chrome...")

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

try:
    # 打开保存的HTML文件
    html_file = r'C:\defly\png\综合数据展示.htm'
    print(f'Opening: {html_file}')
    driver.get(f'file://{html_file}')
    
    time.sleep(3)
    
    # 等待页面加载
    print('Page title:', driver.title)
    
    # 查找表格
    tables = driver.find_elements(By.CLASS_NAME, 'datagrid-btable')
    print(f'Tables found: {len(tables)}')
    
    # 查找行
    rows = driver.find_elements(By.CSS_SELECTOR, 'tr.datagrid-row')
    print(f'Data rows: {len(rows)}')
    
    if rows:
        print('\nFirst 5 rows:')
        for i, row in enumerate(rows[:5]):
            cells = row.find_elements(By.TAG_NAME, 'td')
            row_data = []
            for cell in cells[:8]:
                row_data.append(cell.text[:20])
            print(f'{i+1}. {row_data}')
    
except Exception as e:
    print(f'Error: {e}')
finally:
    driver.quit()
    print('Done')