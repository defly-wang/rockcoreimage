import re

html_file = r'C:\defly\png\综合数据展示.htm'

with open(html_file, 'rb') as f:
    raw = f.read()
content = raw.decode('gbk', errors='ignore')

# 查找JSON格式的数据
patterns = [
    r'datagrid[^>]*data-options[^>]*data:',
    r'\{"D',
    r'rows',
]

for p in patterns:
    matches = re.findall(p, content)
    print(f'{p}: {len(matches)} matches')

# 查看包含QSKS/ZKS/YSMC的JSON结构
qsks_pattern = r'QSKS["\']?\s*:'
qsks = re.findall(qsks_pattern, content)
print(f'QSKS: {len(qsks)} matches')

# 尝试从图片数据中提取深度并计算分层
img_depths = []
pattern = re.compile(r'qssd:([0-9.]+),zzsd:([0-9.]+)')
for m in pattern.finditer(content):
    qssd = float(m.group(1))
    zzsd = float(m.group(2))
    img_depths.append((qssd, zzsd))

print(f'图片深度: {len(img_depths)} ranges')
if img_depths:
    print(f'前5: {img_depths[:5]}')
    print(f'最后: {img_depths[-5:]}')