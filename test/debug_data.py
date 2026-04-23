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
    
    # 找所有TD
    tds = driver.find_elements(By.TAG_NAME, 'td')
    
    data = {'FCH': [], 'HD': [], 'YSMC': [], 'DZMS': [], 'QKS': [], 'ZKS': []}
    
    for td in tds:
        field = td.get_attribute('field')
        if field not in data:
            continue
        
        text = td.text.strip()
        if not text:
            continue
        
        # 分割并过滤
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        if field == 'FCH':
            for l in lines:
                if l.isdigit():
                    data[field].append(l)
        elif field == 'HD':
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
    
    # 打印结果
    for k, v in data.items():
        print(f'{k}: {len(v)} - {v}')
    
except Exception as e:
    print(f'Error: {e}')
finally:
    driver.quit()