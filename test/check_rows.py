from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
import time

edge_options = Options()
edge_options.add_argument('--headless')

driver = webdriver.Edge(options=edge_options)

try:
    html_file = r'C:\defly\png\综合数据展示.htm'
    driver.get(f'file://{html_file}')
    time.sleep(5)
    
    # 直接获取datagrid-body中的数据
    grid_body = driver.find_elements(By.CSS_SELECTOR, '.datagrid-body')
    print(f'Datagrid body: {len(grid_body)}')
    
    # 获取所有tr
    all_trs = driver.find_elements(By.TAG_NAME, 'tr')
    print(f'All TRs: {len(all_trs)}')
    
    # 找到包含数据的行
    data_rows = []
    for tr in all_trs:
        cls = tr.get_attribute('class') or ''
        if 'datagrid-row' in cls:
            data_rows.append(tr)
    
    print(f'Data rows: {len(data_rows)}')
    
    # 打印第一个数据行的内容
    if data_rows:
        first_row = data_rows[0]
        tds = first_row.find_elements(By.TAG_NAME, 'td')
        print(f'TDs in first row: {len(tds)}')
        
        for td in tds[:15]:
            field = td.get_attribute('field')
            text = td.text[:50]
            print(f'  field={field}, text={text}')
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
finally:
    driver.quit()