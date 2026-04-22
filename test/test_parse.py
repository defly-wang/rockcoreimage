import os
import sys
sys.path.insert(0, r'C:\Users\Lenovo\git\rockcoreimage')

from parse_images import RockImageParser

html_file = r'C:\defly\png\综合数据展示.htm'

if not os.path.exists(html_file):
    print(f'文件不存在: {html_file}')
    sys.exit(1)

with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

parser = RockImageParser()
parser.feed(content)

print(f'找到 {len(parser.images)} 张岩心图片')
print()

# 显示前10张
print('前10张图片:')
for i, img in enumerate(parser.images[:10]):
    print(f'{i+1}. {img.get("yxtpbh")} 深度:{img.get("qssd")}-{img.get("zzsd")}m')

# 保存列表
import json
output_file = r'C:\defly\png\image_list.json'
download_list = []
for img in parser.images:
    download_list.append({
        'filename': img.get('yxtpbh', ''),
        'qssd': img.get('qssd', 0),
        'zzsd': img.get('zzsd', 0),
        'src': img.get('src', ''),
    })

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(download_list, f, ensure_ascii=False, indent=2)

print(f'\n图片列表已保存到: {output_file}')
