from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import time
import csv

print('Setting up Edge...')

edge_options = Options()
edge_options.add_argument('--headless')
edge_options.add_argument('--no-sandbox')
edge_options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Edge(options=edge_options)

try:
    html_file = r'C:\defly\png\综合数据展示.htm'
    print(f'Opening: {html_file}')
    driver.get(f'file://{html_file}')
    
    time.sleep(5)
    
    print('Page title:', driver.title)
    
    # 查找datagrid
    rows = driver.find_elements(By.CSS_SELECTOR, 'tr.datagrid-row')
    print(f'Data rows: {len(rows)}')
    
    if rows:
        print('\nFirst 10 rows:')
        for i, row in enumerate(rows[:10]):
            cells = row.find_elements(By.TAG_NAME, 'td')
            texts = []
            for cell in cells[:10]:
                texts.append(cell.text[:30])
            print(f'{i+1}. {texts}')
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
finally:
    driver.quit()
    print('Done')