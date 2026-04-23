import re
import csv

html_file = r'C:\defly\png\综合数据展示.htm'

with open(html_file, 'rb') as f:
    raw = f.read()
content = raw.decode('gbk', errors='ignore')

# 搜索地质分层数据 - 查找带数值的span
# FCH 分层号
fch_pattern = r'<span[^>]*>(\d+)</span>'
fch_matches = re.findall(fch_pattern, content)
print(f'FCH (分层号): {fch_matches}')

# 查找厚度 - 搜索TD
hd_pattern = r'<span[^>]*>(\d+\.\d+)</span>'
all_spans = re.findall(hd_pattern, content)
# 过滤合理的厚度值 (1-50之间)
hd_values = []
for s in all_spans:
    try:
        v = float(s)
        if 1 <= v <= 50:
            hd_values.append(v)
    except:
        pass

# 去重排序
unique_hd = sorted(set(hd_values))
print(f'厚度值 (1-50): {unique_hd}')

# 搜索白云石英片岩
yqspy = re.findall(r'白云石英片岩', content)
print(f'白云石英片岩: {len(yqspy)}次')

# 搜索所有岩石名称
ysmc_pattern = r'field="YSMC"[^>]*>.*?<span[^>]*>([^<]+)</span>'
ysmc = re.findall(ysmc_pattern, content, re.DOTALL)
print(f'YSMC: {ysmc}')

# 直接搜索HTML中的数字分层号
fch = re.findall(r'>(\d+)<', content)
fch_nums = [int(x) for x in fch if x.isdigit() and 1 <= int(x) <= 100]
print(f'分层号 (1-100): {sorted(set(fch_nums))}')