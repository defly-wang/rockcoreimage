import re

html_file = r'C:\defly\png\综合数据展示.htm'

with open(html_file, 'rb') as f:
    raw = f.read()
content = raw.decode('gbk', errors='ignore')

# 从JS中获取参数
p1 = re.search(r"dh\s*=\s*['\"]([^'\"]+)", content)
p2 = re.search(r"xmmc\s*=\s*['\"]([^'\"]+)", content)
p3 = re.search(r"zkbh\s*=\s*['\"]([^'\"]+)", content)

if p1:
    print('dh:', p1.group(1))
if p2:
    print('xmmc:', p2.group(1)[:50])
if p3:
    print('zkbh:', p3.group(1))