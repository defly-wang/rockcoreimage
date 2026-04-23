from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
import time
import csv

edge_options = Options()
edge_options.add_argument('--headless')
edge_options.add_argument('--no-sandbox')

driver = webdriver.Edge(options=edge_options)

try:
    html_file = r'C:\defly\png\综合数据展示.htm'
    driver.get(f'file://{html_file}')
    time.sleep(5)
    
    # 获取表头
    headers = driver.find_elements(By.CSS_SELECTOR, '.datagrid-header-row td')
    header_fields = []
    for h in headers:
        field = h.get_attribute('field')
        if field:
            header_fields.append(field)
    
    print(f'表头字段: {header_fields}')
    
    # 获取数据行的FCH, HD, YSMC, DZMS
    rows = driver.find_elements(By.CSS_SELECTOR, 'tr.datagrid-row')
    
    layers = []
    current_depth = 0.0
    
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, 'td')
        
        fch = hd = ysmc = dzms = ''
        
        for cell in cells:
            field = cell.get_attribute('field')
            if not field:
                continue
            
            text = cell.text.strip()
            if not text:
                continue
            
            # 分割多行文本
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            
            if field == 'FCH':
                # 取数字
                for l in lines:
                    if l.isdigit():
                        fch = l
                        break
            elif field == 'HD':
                for l in lines:
                    try:
                        hd = float(l)
                        break
                    except:
                        continue
            elif field == 'YSMC':
                for l in lines:
                    if l and len(l) > 1:
                        ysmc = l
                        break
            elif field == 'DZMS':
                for l in lines:
                    if l and len(l) > 10:
                        dzms = l
                        break
        
        if fch and hd and ysmc:
            end_depth = current_depth + hd
            layers.append({
                '分层号': fch,
                '起始孔深(m)': current_depth,
                '终止孔深(m)': end_depth,
                '厚度(m)': hd,
                '岩石名称': ysmc,
                '地质描述': dzms
            })
            print(f'{fch}. {current_depth}-{end_depth}m ({hd}m): {ysmc}')
            current_depth = end_depth
    
    # 保存
    if layers:
        csv_file = r'C:\defly\png\lithology_layers.csv'
        with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['分层号', '起始孔深(m)', '终止孔深(m)', '厚度(m)', '岩石名称', '地质描述'])
            writer.writeheader()
            writer.writerows(layers)
        print(f'\n已保存: {csv_file}')
        print(f'共 {len(layers)} 层')
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
finally:
    driver.quit()