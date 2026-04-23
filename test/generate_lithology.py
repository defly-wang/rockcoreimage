import re
import json
import csv

html_file = r'C:\defly\png\综合数据展示.htm'

with open(html_file, 'rb') as f:
    raw = f.read()
content = raw.decode('gbk', errors='ignore')

# 提取图片深度范围
pattern = re.compile(r'class="yanxinImage ([^"]+)"[^>]*data-options="qssd:([0-9.]+),zzsd:([0-9.]+)')
images = []
for m in pattern.finditer(content):
    img_name = m.group(1).strip()
    qssd = float(m.group(2))
    zzsd = float(m.group(3))
    images.append({
        'imgName': img_name,
        'start_depth': qssd,
        'end_depth': zzsd,
        'thickness': round(zzsd - qssd, 2)
    })

# 去重并按深度排序
seen = set()
unique_images = []
for img in images:
    key = (img['start_depth'], img['end_depth'])
    if key not in seen:
        seen.add(key)
        unique_images.append(img)

unique_images.sort(key=lambda x: x['start_depth'])

print(f'图片深度范围: {len(unique_images)} 个')

# 生成岩性数据
layers = []
for i, img in enumerate(unique_images):
    layers.append({
        '分层号': i + 1,
        '厚度(m)': img['thickness'],
        '起始孔深(m)': img['start_depth'],
        '终止孔深(m)': img['end_depth'],
        '岩石名称': '',
        '地质描述': ''
    })

# 保存CSV
csv_file = r'C:\defly\png\lithology_data.csv'
with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['分层号', '厚度(m)', '起始孔深(m)', '终止孔深(m)', '岩石名称', '地质描述'])
    writer.writeheader()
    writer.writerows(layers)

print(f'已保存到: {csv_file}')
print(f'共 {len(layers)} 层')

# 显示前10行
print('\n前10行:')
for row in layers[:10]:
    print(f'{row["分层号"]}. {row["起始孔深(m)"]}-{row["终止孔深(m)"]}m, 厚度:{row["厚度(m)"]}m')

# 统计
total_thickness = sum(l['厚度(m)'] for l in layers)
print(f'\n总厚度: {total_thickness:.2f}m')