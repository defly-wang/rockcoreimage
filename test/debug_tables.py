from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
import csv

edge_options = Options()
edge_options.add_argument('--headless')

driver = webdriver.Edge(options=edge_options)

try:
    html_file = r'C:\defly\png\综合数据展示.htm'
    driver.get(f'file://{html_file}')
    import time
    time.sleep(5)
    
    # 找到所有table标签
    tables = driver.find_elements(By.TAG_NAME, 'table')
    print(f'All tables: {len(tables)}')
    
    # 分别处理每个table
    for i, table in enumerate(tables):
        cls = table.get_attribute('class') or ''
        if 'datagrid-btable' in cls:
            rows = table.find_elements(By.TAG_NAME, 'tr')
            print(f'\nTable {i} (class={cls}): {len(rows)} rows')
            
            # 获取该表的所有field
            fields = set()
            sample_row = rows[0] if rows else None
            if sample_row:
                tds = sample_row.find_elements(By.TAG_NAME, 'td')
                for td in tds:
                    f = td.get_attribute('field')
                    if f:
                        fields.add(f)
            print(f'Fields: {sorted(fields)}')
    
    # 直接打印第一个datagrid-btable的子表
    all_tables = driver.find_elements(By.CSS_SELECTOR, 'table.datagrid-btable')
    
    for idx, tbl in enumerate(all_tables):
        tbody = tbl.find_element(By.TAG_NAME, 'tbody')
        if tbody:
            trs = tbody.find_elements(By.TAG_NAME, 'tr')
            print(f'\nTable {idx} tbody trs: {len(trs)}')
            
            for ri, tr in enumerate(trs[:3]):
                tds = tr.find_elements(By.TAG_NAME, 'td')
                row_data = {}
                for td in tds:
                    f = td.get_attribute('field')
                    if f:
                        txt = td.text[:30]
                        row_data[f] = txt
                if row_data:
                    print(f'  Row {ri}: {row_data}')
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
finally:
    driver.quit()