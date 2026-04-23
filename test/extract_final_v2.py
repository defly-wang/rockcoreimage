import re
import csv

with open(r'C:\defly\png\综合数据展示.htm', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# 搜索 class="field-fch move-field0" title="..."
fch_pattern = r'class="field-fch move-field(\d+)" title="([^"]+)"'
fch_matches = re.findall(fch_pattern, content)
print('FCH (分层号):', fch_matches)

# 搜索 class="field-hd move-field0" title="..."
hd_pattern = r'class="field-hd move-field(\d+)" title="([^"]+)"'
hd_matches = re.findall(hd_pattern, content)
print('HD (厚度):', hd_matches)

# 搜索 class="field-ysmc move-field0" title="..."
ysmc_pattern = r'class="field-ysmc move-field(\d+)" title="([^"]+)"'
ysmc_matches = re.findall(ysmc_pattern, content)
print('YSMC (岩石名称):', ysmc_matches[:15])

# 搜索 class="field-dzms move-field0" title="..."
dzms_pattern = r'class="field-dzms move-field(\d+)" title="([^"]+)"'
dzms_matches = re.findall(dzms_pattern, content)
print('DZMS (地质描述):', [d[1][:50] for d in dzms_matches[:5]])

# 生成CSV
if ysmc_matches:
    layers = []
    start = 0.0
    
    for i, (idx, ysmc) in enumerate(ysmc_matches):
        hd = 0.0
        if i < len(hd_matches):
            try:
                hd = float(hd_matches[i][1])
            except:
                pass
        
        if hd > 0:
            end = start + hd
            dzms = dzms_matches[i][1] if i < len(dzms_matches) else ''
            
            layers.append({
                '分层号': i + 1,
                '起始孔深(m)': round(start, 2),
                '终止孔深(m)': round(end, 2),
                '厚度(m)': hd,
                '岩石名称': ysmc,
                '地质描述': dzms
            })
            start = end
    
    # 保存CSV
    csv_file = r'C:\defly\png\lithology_from_table.csv'
    with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['分层号', '起始孔深(m)', '终止孔深(m)', '厚度(m)', '岩石名称', '地质描述'])
        writer.writeheader()
        writer.writerows(layers)
    
    print(f'\n已保存: {csv_file}')
    print(f'共 {len(layers)} 层')
    
    for layer in layers:
        print(f'{layer["分层号"]}. {layer["起始孔深(m)"]}-{layer["终止孔深(m)"]}m ({layer["厚度(m)"]}m): {layer["岩石名称"]}')