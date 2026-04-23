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
    
    tables = driver.find_elements(By.CSS_SELECTOR, 'table.datagrid-btable')
    
    table1 = tables[0]
    tbody1 = table1.find_element(By.TAG_NAME, 'tbody')
    rows1 = tbody1.find_elements(By.TAG_NAME, 'tr')
    
    fch_data = {}
    hd_data = {}
    
    for ri, row in enumerate(rows1):
        tds = row.find_elements(By.TAG_NAME, 'td')
        for td in tds:
            field = td.get_attribute('field')
            if not field:
                continue
            text = td.text.strip()
            if not text:
                continue
            
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            
            if field == 'FCH':
                for l in lines:
                    if l.isdigit():
                        fch_data[ri] = l
                        break
            elif field == 'HD':
                for l in lines:
                    try:
                        v = float(l)
                        if 0.1 <= v <= 50:
                            hd_data[ri] = v
                            break
                    except:
                        pass
    
    table2 = tables[1]
    tbody2 = table2.find_element(By.TAG_NAME, 'tbody')
    rows2 = tbody2.find_elements(By.TAG_NAME, 'tr')
    
    ysmc_data = {}
    dzms_data = {}
    
    for ri, row in enumerate(rows2):
        tds = row.find_elements(By.TAG_NAME, 'td')
        for td in tds:
            field = td.get_attribute('field')
            if not field:
                continue
            text = td.text.strip()
            if not text:
                continue
            
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            
            if field == 'YSMC':
                for l in lines:
                    if l:
                        ysmc_data[ri] = l
                        break
            elif field == 'DZMS':
                for l in lines:
                    if len(l) > 20:
                        dzms_data[ri] = l
                        break
    
    print('Table1 FCH:', fch_data)
    print('Table1 HD:', hd_data)
    print('Table2 YSMC:', ysmc_data)
    
    all_row_indices = sorted(set(list(fch_data.keys()) + list(ysmc_data.keys())))
    print('Row indices:', all_row_indices)
    
    layers = []
    start = 0.0
    
    for ri in all_row_indices:
        fch = fch_data.get(ri, '')
        hd = hd_data.get(ri, 0)
        ysmc = ysmc_data.get(ri, '')
        dzms = dzms_data.get(ri, '')
        
        if hd > 0:
            end = start + hd
            layers.append({
                '分层号': fch if fch else str(ri + 1),
                '起始孔深(m)': round(start, 2),
                '终止孔深(m)': round(end, 2),
                '厚度(m)': hd,
                '岩石名称': ysmc,
                '地质描述': dzms
            })
            start = end
    
    if layers:
        csv_file = r'C:\defly\png\lithology_from_table.csv'
        with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['分层号', '起始孔深(m)', '终止孔深(m)', '厚度(m)', '岩石名称', '地质描述'])
            writer.writeheader()
            writer.writerows(layers)
        
        print('Saved:', csv_file)
        print('Layers:', len(layers))
    
except Exception as e:
    print('Error:', e)
    import traceback
    traceback.print_exc()
finally:
    driver.quit()