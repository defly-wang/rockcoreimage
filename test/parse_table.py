"""
从综合数据展示.htm提取表格数据
解析深度、岩性（岩石名称）、描述（地质描述）
"""

import os
import re
import json


def read_html_file(html_file):
    """读取HTML文件，处理编码问题"""
    with open(html_file, 'rb') as f:
        raw = f.read()
    return raw.decode('gbk', errors='ignore')


def extract_depth_ranges(html_file):
    """提取图片深度范围"""
    content = read_html_file(html_file)
    
    images = []
    pattern = re.compile(
        r'class="yanxinImage ([^"]+)"[^>]*data-options="qssd:([0-9.]+),zzsd:([0-9.]+)',
        re.DOTALL
    )
    
    for m in pattern.finditer(content):
        img_name = m.group(1).strip()
        qssd = float(m.group(2))
        zzsd = float(m.group(3))
        images.append({
            'imgName': img_name,
            'qssd': qssd,
            'zzsd': zzsd
        })
    
    return images


def extract_long_chinese_texts(html_file):
    """提取HTML中所有50字以上的连续中文文本"""
    content = read_html_file(html_file)
    
    texts = []
    pattern = re.compile(r'[\u4e00-\u9fa5]+')
    
    seen = set()
    for m in pattern.finditer(content):
        text = m.group(0).strip()
        if len(text) >= 50 and text not in seen:
            seen.add(text)
            texts.append(text)
    
    return texts


def extract_geological_fields(html_file):
    """提取地质字段"""
    content = read_html_file(html_file)
    
    results = {'YSMC': [], 'DZMS': [], 'FCH': [], 'HD': []}
    
    for field in results.keys():
        pattern = re.compile(
            rf'<td[^>]*field="{field}"[^>]*>.*?<span[^>]*>([^<]+)</span>',
            re.DOTALL
        )
        for m in pattern.finditer(content):
            text = m.group(1).strip()
            if text:
                results[field].append(text)
    
    return results


def main():
    html_file = r'C:\defly\png\综合数据展示.htm'
    
    if not os.path.exists(html_file):
        print(f'文件不存在: {html_file}')
        return
    
    print('提取图片深度...')
    images = extract_depth_ranges(html_file)
    print(f'找到 {len(images)} 个深度范围')
    
    print('\n前10个深度:')
    for i, img in enumerate(images[:10]):
        print(f'{i+1}. {img["qssd"]}-{img["zzsd"]}m')
    
    print('\n提取长文本...')
    texts = extract_long_chinese_texts(html_file)
    print(f'找到 {len(texts)} 个长文本')
    
    if texts:
        print('\n前20个文本:')
        for i, text in enumerate(texts[:20]):
            print(f'{i+1}. {text[:100]}...')
    
    print('\n提取地质字段...')
    fields = extract_geological_fields(html_file)
    for field, values in fields.items():
        print(f'{field}: {len(values)} 个值')
        if values:
            for i, v in enumerate(values[:3]):
                print(f'  {i+1}. {v}')
    
    data = {
        'images': images,
        'long_texts': texts,
        'fields': fields
    }
    
    output_file = r'C:\defly\png\table_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f'\n数据已保存到: {output_file}')


if __name__ == '__main__':
    main()