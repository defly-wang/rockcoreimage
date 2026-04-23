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
    
    # 表2 - 获取QKS(起始孔深)和ZKS(终止孔深)
    table2 = tables[1]
    tbody2 = table2.find_element(By.TAG_NAME, 'tbody')
    rows2 = tbody2.find_elements(By.TAG_NAME, 'tr')
    
    qks_list = []
    zks_list = []
    ysmc_list = []
    dzms_list = []
    
    for row in rows2:
        tds = row.find_elements(By.TAG_NAME, 'td')
        for td in tds:
            field = td.get_attribute('field')
            if not field:
                continue
            text = td.text.strip()
            if not text:
                continue
            
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            
            if field == 'QKS':
                for l in lines:
                    try:
                        v = float(l)
                        if v >= 0:
                            qks_list.append(v)
                    except:
                        pass
            elif field == 'ZKS':
                for l in lines:
                    try:
                        v = float(l)
                        if v >= 0:
                            zks_list.append(v)
                    except:
                        pass
            elif field == 'YSMC':
                for l in lines:
                    if l:
                        ysmc_list.append(l)
                        break
            elif field == 'DZMS':
                for l in lines:
                    if len(l) > 20:
                        dzms_list.append(l)
                        break
    
    # 去重
    qks_list = list(dict.fromkeys(qks_list))
    zks_list = list(dict.fromkeys(zks_list))
    ysmc_list = list(dict.fromkeys(ysmc_list))
    dzms_list = list(dict.fromkeys(dzms_list))
    
    print('QKS:', len(qks_list), '-', qks_list[:10])
    print('ZKS:', len(zks_list), '-', zks_list[:10])
    print('YSMC:', len(ysmc_list), '-', ysmc_list)
    print('DZMS:', len(dzms_list))
    
    # 使用QKS/ZKS计算厚度并生成CSV
    n = min(len(ysmc_list), len(zks_list))
    if n > 0 and len(qks_list) > 0:
        layers = []
        
        for i in range(n):
            start = qks_list[i] if i < len(qks_list) else 0
            end = zks_list[i] if i < len(zks_list) else 0
            hd = end - start
            
            layers.append({
                '分层号': i + 1,
                '起始孔深(m)': start,
                '终止孔深(m)': end,
                '厚度(m)': round(hd, 2),
                '岩石名称': ysmc_list[i] if i < len(ysmc_list) else '',
                '地质描述': dzms_list[i] if i < len(dzms_list) else ''
            })
        
        csv_file = r'C:\defly\png\lithology_from_table.csv'
        with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['分层号', '起始孔深(m)', '终止孔深(m)', '厚度(m)', '岩石名称', '地质描述'])
            writer.writeheader()
            writer.writerows(layers)
        
        print('Saved:', csv_file)
        print('Layers:', len(layers))
        
        for layer in layers:
            print(f'{layer["分层号"]}. {layer["起始孔深(m)"]}-{layer["终止孔深(m)"]}m ({layer["厚度(m)"]}m): {layer["岩石名称"][:20] if layer["岩石名称"] else "?"}')
    
except Exception as e:
    print('Error:', e)
    import traceback
    traceback.print_exc()
finally:
    driver.quit()