import re

html_file = r'C:\defly\png\综合数据展示.htm'

with open(html_file, 'rb') as f:
    raw = f.read()
content = raw.decode('gbk', errors='ignore')

# 搜索所有厚度值
pattern = r'(\d+\.\d+)'
matches = re.findall(pattern, content)
unique_hd = sorted(set(float(m) for m in matches if 1 <= float(m) <= 50))
print(f'厚度值 (1-50): {unique_hd}')

# 搜索岩石名称
print(f'\n白云石英片岩: {len(re.findall(r白云石英片岩, content))}次')
print(f'煌斑岩: {len(re.findall(r煌斑岩, content))}次')

# 搜索所有包含"岩"的名称
patterns = [
    r'([一-龥]{2,4}片岩)',
    r'([一-龥]{2,4}岩)',
]

for p in patterns:
    matches = re.findall(p, content)
    uniq = sorted(set(matches))
    if uniq:
        print(f'\n{p}: {uniq}')