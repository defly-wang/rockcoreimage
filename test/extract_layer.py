import re

html_file = r'C:\defly\png\综合数据展示.htm'

with open(html_file, 'rb') as f:
    raw = f.read()
content = raw.decode('gbk', errors='ignore')

patterns = [
    ('FCH', r'<td[^>]*field="FCH"[^>]*>.*?<span[^>]*>([^<]+)</span>'),
    ('HD', r'<td[^>]*field="HD"[^>]*>.*?<span[^>]*>([^<]+)</span>'),
    ('YSMC', r'<td[^>]*field="YSMC"[^>]*>.*?<span[^>]*>([^<]+)</span>'),
    ('DZMS', r'<td[^>]*field="DZMS"[^>]*>.*?<span[^>]*>([^<]+)</span>'),
]

for field, pattern in patterns:
    matches = re.findall(pattern, content, re.DOTALL)
    print(f'{field}: {len(matches)} matches')
    for i, m in enumerate(matches[:5]):
        print(f'  {i+1}. {m.strip()[:80]}')