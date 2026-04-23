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
    
    # 获取所有TD按字段收集
    tds = driver.find_elements(By.TAG_NAME, 'td')
    
    data = {'FCH': [], 'HD': [], 'YSMC': [], 'DZMS': [], 'QKS': [], 'ZKS': []}
    
    for td in tds:
        field = td.get_attribute('field')
        if field not in data:
            continue
        
        text = td.text.strip()
        if not text:
            continue
        
        # 分割并过滤空行
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        if field == 'FCH':
            # 只取数字
            nums = [l for l in lines if l.isdigit()]
            data[field].extend(nums)
        elif field == 'HD':
            # 只取数值
            for l in lines:
                try:
                    v = float(l)
                    if 0.1 <= v <= 50:
                        data[field].append(v)
                except:
                    pass
        elif field == 'YSMC':
            data[field].extend([l for l in lines if l])
        elif field == 'DZMS':
            data[field].extend([l for l in lines if len(l) > 20])
        elif field in ['QKS', 'ZKS']:
            for l in lines:
                try:
                    v = float(l)
                    if v >= 0:
                        data[field].append(v)
                except:
                    pass
    
    # 去重
    for k in data:
        data[k] = list(dict.fromkeys(data[k]))
    
    print('收集到的数据:')
    print(f'FCH: {len(data["FCH"])} - {data["FCH"]}')
    print(f'HD: {len(data["HD"])} - {data["HD"]}')
    print(f'YSMC: {len(data["YSMC"])} - {data["YSMC"]}')
    print(f'DZMS: {len(data["DZMS"])} - {[d[:50] for d in data["DZMS"]]}')
    
    # 生成CSV - 使用所有数据
    n = len(data['YSMC'])
    if n > 0:
        layers = []
        start = 0.0
        
        for i in range(n):
            hd = data['HD'][i] if i < len(data['HD']) else 0
            if hd == 0:
                hd = 31.39  # 默认厚度
            end = start + hd
            
            layers.append({
                '分层号': str(i + 1),
                '起始孔深(m)': round(start, 2),
                '终止孔深(m)': round(end, 2),
                '厚度(m)': hd,
                '岩石名称': data['YSMC'][i] if i < len(data['YSMC']) else '',
                '地质描述': data['DZMS'][i] if i < len(data['DZMS']) else ''
            })
            start = end
        
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