import re
import csv

html_file = r'C:\defly\png\综合数据展示.htm'

with open(html_file, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# 方法1: 从表2获取YSMC和对应的QKS/ZKS
# 找到table2的所有数据行
table2_pattern = r'<table[^>]*class="datagrid-btable"[^>]*>(.*?)</table>'
table2_match = re.search(table2_pattern, content, re.DOTALL)

if table2_match:
    table2_html = table2_match.group(1)
    
    # 获取每行的YSMC和QKS/ZKS
    row_pattern = r'<tr[^>]*datagrid-row-index="(\d+)"[^>]*>(.*?)</tr>'
    
    rows_data = []
    for row_match in re.finditer(row_pattern, table2_html, re.DOTALL):
        row_idx = row_match.group(1)
        row_html = row_match.group(2)
        
        # 提取YSMC
        ysmc_match = re.search(r'<td[^>]*field="YSMC"[^>]*>.*?<span[^>]*>([^<]+)</span>', row_html, re.DOTALL)
        ysmc = ysmc_match.group(1) if ysmc_match else ''
        
        # 提取QKS和ZKS
        qks_match = re.search(r'<td[^>]*field="QKS"[^>]*>.*?<span[^>]*>([^<]+)</span>', row_html, re.DOTALL)
        zks_match = re.search(r'<td[^>]*field="ZKS"[^>]*>.*?<span[^>]*>([^<]+)</span>', row_html, re.DOTALL)
        
        qks = qks_match.group(1) if qks_match else ''
        zks = zks_match.group(1) if zks_match else ''
        
        if ysmc:
            rows_data.append((row_idx, ysmc, qks, zks))
    
    print('Table2 rows:', len(rows_data))
    for idx, ysmc, qks, zks in rows_data[:10]:
        print(f'  Row {idx}: YSMC={ysmc[:20]}, QKS={qks}, ZKS={zks}')

# 方法2: 从表1获取FCH和HD
table1_pattern = r'<table[^>]*class="datagrid-btable"[^>]*>(.*?)</table>'
table1_matches = list(re.finditer(table1_pattern, content, re.DOTALL))

if table1_matches:
    table1_html = table1_matches[0].group(1) if table1_matches else ''
    
    hd_data = []
    for row_match in re.finditer(row_pattern, table1_html, re.DOTALL):
        row_html = row_match.group(2)
        
        hd_match = re.search(r'<td[^>]*field="HD"[^>]*>.*?<span[^>]*>([^<]+)</span>', row_html, re.DOTALL)
        fch_match = re.search(r'<td[^>]*field="FCH"[^>]*>.*?<span[^>]*>([^<]+)</span>', row_html, re.DOTALL)
        
        hd = hd_match.group(1) if hd_match else ''
        fch = fch_match.group(1) if fch_match else ''
        
        if hd:
            hd_data.append((fch, hd))
    
    print('\nTable1 HD:', hd_data[:10])