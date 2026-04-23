from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
import time
import csv
import re

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
    
    # 先获取所有TD元素
    all_cells = driver.find_elements(By.TAG_NAME, 'td')
    print(f'Total TD cells: {len(all_cells)}')
    
    # 收集各字段数据
    fch_list = []
    hd_list = []
    ysmc_list = []
    dzms_list = []
    
    for cell in all_cells:
        field = cell.get_attribute('field')
        if not field:
            continue
        
        # 获取纯文本内容
        text = cell.text.strip()
        if not text:
            continue
        
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        if field == 'FCH':
            fch_list.extend(lines)
        elif field == 'HD':
            hd_list.extend(lines)
        elif field == 'YSMC':
            ysmc_list.extend(lines)
        elif field == 'DZMS':
            dzms_list.extend(lines)
    
    # 清理数据 - 过滤掉表头
    def clean_list(items, is_hd=False):
        result = []
        for item in items:
            # 跳过表头文字
            if '分层' in item or '厚度' in item or '岩石' in item or '地质' in item or '描述' in item:
                continue
            if is_hd:
                try:
                    result.append(float(item))
                except:
                    continue
            else:
                result.append(item)
        return result
    
    hd_clean = clean_list(hd_list, is_hd=True)
    ysmc_clean = [y for y in ysmc_list if y]
    dzms_clean = [d for d in dzms_list if d and len(d) > 20]
    
    print(f'\n清理后的数据:')
    print(f'HD: {len(hd_clean)} - {hd_clean}')
    print(f'YSMC: {len(ysmc_clean)} - {ysmc_clean}')
    print(f'DZMS: {len(dzms_clean)} - {[d[:50] for d in dzms_clean]}')
    
    # 生成CSV
    layers = []
    start_depth = 0.0
    for i, ysmc in enumerate(ysmc_clean):
        if i >= len(hd_clean):
            break
        hd = hd_clean[i] if i < len(hd_clean) else 0
        
        layer = {
            '分层号': i + 1,
            '起始孔深(m)': start_depth,
            '终止孔深(m)': round(start_depth + hd, 2),
            '厚度(m)': hd,
            '岩石名称': ysmc,
            '地质描述': dzms_clean[i] if i < len(dzms_clean) else ''
        }
        layers.append(layer)
        start_depth += hd
        
        print(f'{layer["分层号"]}. {layer["起始孔深(m)"]}-{layer["终止孔深(m)"]}m ({layer["厚度(m)"]}m): {ysmc[:20]}')
    
    # 保存CSV
    csv_file = r'C:\defly\png\lithology_layers.csv'
    with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['分层号', '起始孔深(m)', '终止孔深(m)', '厚度(m)', '岩石名称', '地质描述'])
        writer.writeheader()
        writer.writerows(layers)
    
    print(f'\n已保存到: {csv_file}')
    print(f'共 {len(layers)} 层')
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
finally:
    driver.quit()
    print('Done')