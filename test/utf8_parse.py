import re

html_file = r'C:\defly\png\综合数据展示.htm'

with open(html_file, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# 搜索岩石名称
ysmc = re.findall(r'([一-龥]{2,6}片岩)', content)
print('YSMC:', sorted(set(ysmc)))

# 搜索厚度
hd_pattern = r'<td[^>]*field="HD"[^>]*>.*?<span[^>]*>(\d+\.\d+)</span>'
hd = re.findall(hd_pattern, content, re.DOTALL)
print('HD:', sorted(set(float(h) for h in hd if 1 <= float(h) <= 50)))