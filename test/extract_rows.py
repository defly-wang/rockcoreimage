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
    
    data_rows = driver.find_elements(By.CSS_SELECTOR, 'tr.datagrid-row')
    print(f'Data rows: {len(data_rows)}')
    
    layers = []
    start_depth = 0.0
    
    for row in data_rows:
        tds = row.find_elements(By.TAG_NAME, 'td')
        
        fch = ''
        hd = 0.0
        ysmc = ''
        dzms = ''
        
        for td in tds:
            field = td.get_attribute('field')
            if not field:
                continue
            
            text = td.text.strip()
            if not text:
                continue
            
            if field == 'FCH' and not fch:
                for l in text.split('\n'):
                    if l.strip().isdigit():
                        fch = l.strip()
                        break
            elif field == 'HD' and hd == 0:
                for l in text.split('\n'):
                    try:
                        v = float(l)
                        if 0.1 <= v <= 50:
                            hd = v
                            break
                    except:
                        pass
            elif field == 'YSMC' and not ysmc:
                lines = [l for l in text.split('\n') if l.strip()]
                if lines:
                    ysmc = lines[0]
            elif field == 'DZMS' and not dzms:
                lines = [l for l in text.split('\n') if len(l.strip()) > 20]
                if lines:
                    dzms = lines[0]
        
        if fch and hd > 0:
            end_depth = start_depth + hd
            layers.append({
                '分层号': fch,
                '起始孔深(m)': round(start_depth, 2),
                '终止孔深(m)': round(end_depth, 2),
                '厚度(m)': hd,
                '岩石名称': ysmc,
                '地质描述': dzms
            })
            ysmc_short = ysmc[:30] if ysmc else '?'
            print(f'{fch}. {start_depth}-{end_depth}m ({hd}m): {ysmc_short}')
            start_depth = end_depth
    
    if layers:
        csv_file = r'C:\defly\png\lithology_data_new.csv'
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