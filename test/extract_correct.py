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
    
    # 获取所有TD元素
    tds = driver.find_elements(By.TAG_NAME, 'td')
    
    ysmc_list = []
    hd_list = []
    dzms_list = []
    
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
                    ysmc_list.append(l)
        elif field == 'HD':
            for l in lines:
                try:
                    v = float(l)
                    if 0.1 <= v <= 50:
                        hd_list.append(v)
                except:
                    pass
        elif field == 'DZMS':
            for l in lines:
                if len(l) > 20:
                    dzms_list.append(l)
    
    # 去重
    ysmc_list = list(dict.fromkeys(ysmc_list))
    hd_list = list(dict.fromkeys(hd_list))
    dzms_list = list(dict.fromkeys(dzms_list))
    
    print(f'岩石名称: {len(ysmc_list)}')
    for i, r in enumerate(ysmc_list):
        print(f'  {i+1}. {r}')
    
    print(f'\n厚度: {len(hd_list)}')
    for i, h in enumerate(hd_list[:20]):
        print(f'  {i+1}. {h}')
    
    # 生成CSV
    if len(ysmc_list) > 0:
        layers = []
        start_depth = 0.0
        
        for i, ysmc in enumerate(ysmc_list):
            hd = hd_list[i] if i < len(hd_list) else 0
            end_depth = start_depth + hd
            
            layer = {
                '分层号': i + 1,
                '起始孔深(m)': start_depth,
                '终止孔深(m)': end_depth,
                '厚度(m)': hd,
                '岩石名称': ysmc,
                '地质描述': dzms_list[i] if i < len(dzms_list) else ''
            }
            layers.append(layer)
            start_depth = end_depth
        
        # 保存
        csv_file = r'C:\defly\png\lithology_data_new.csv'
        with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['分层号', '起始孔深(m)', '终止孔深(m)', '厚度(m)', '岩石名称', '地质描述'])
            writer.writeheader()
            writer.writerows(layers)
        
        print(f'\n已保存: {csv_file}')
        
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
finally:
    driver.quit()