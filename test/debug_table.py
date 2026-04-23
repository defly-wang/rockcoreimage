from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
import time
import csv

print('Setting up Edge...')

edge_options = Options()
edge_options.add_argument('--headless')
edge_options.add_argument('--no-sandbox')

driver = webdriver.Edge(options=edge_options)

try:
    html_file = r'C:\defly\png\综合数据展示.htm'
    print(f'Opening: {html_file}')
    driver.get(f'file://{html_file}')
    time.sleep(5)
    
    # 获取所有TD元素
    all_cells = driver.find_elements(By.TAG_NAME, 'td')
    print(f'Total TD cells: {len(all_cells)}')
    
    # 按field分组
    field_data = {}
    for cell in all_cells:
        field = cell.get_attribute('field')
        if field and field in ['FCH', 'HD', 'QKS', 'ZKS', 'YSMC', 'DZMS']:
            text = cell.text.strip()
            if text:
                if field not in field_data:
                    field_data[field] = []
                field_data[field].append(text)
    
    for field, values in field_data.items():
        print(f'{field}: {len(values)} values')
        if values:
            print(f'  {values[:10]}')
    
    # 尝试获取datagrid数据
    print('\nTrying datagrid...')
    datagrid = driver.find_elements(By.CLASS_NAME, 'datagrid-btable')
    print(f'Datagrid tables: {len(datagrid)}')
    
    # 尝试获取innerHTML
    trs = driver.find_elements(By.CSS_SELECTOR, '.datagrid-btable tr')
    print(f'TR elements: {len(trs)}')
    
    # 打印第一行TR的内容
    if trs:
        first_tr = trs[0]
        print(f'First TR HTML length: {len(first_tr.get_attribute("outerHTML"))}')
        tds = first_tr.find_elements(By.TAG_NAME, 'td')
        print(f'TDs in first TR: {len(tds)}')
        for td in tds[:10]:
            field = td.get_attribute('field')
            text = td.text[:30]
            print(f'  field={field}, text={text}')
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
finally:
    driver.quit()
    print('Done')