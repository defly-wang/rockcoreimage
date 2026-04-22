"""
岩心图像批量下载脚本
支持按深度范围下载
"""

import os
import re
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser

# 配置参数
ZZJGDM = "12100000400014276N"
ZKBBH = "ZK13-4-2"
DH = "000010"
XMM = "四川省第四届岩石矿物学会成都理工大学地球科学学院附属实验室岩心馆"

BASE_URL = f"https://ndcp.cgsi.cn/SWZXFILE/file/yanxinImages/{ZZJGDM}/{DH}_{ZKBBH}/"

OUTPUT_DIR = f"images/{DH}_{ZKBBH}"


class ImageParser(HTMLParser):
    """解析HTML中的岩心图片信息"""
    
    def __init__(self):
        super().__init__()
        self.images = []
    
    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            attrs_dict = dict(attrs)
            if 'class' in attrs_dict and 'yanxinImage' in attrs_dict['class']:
                data_options = attrs_dict.get('data-options', '')
                
                # 解析 data-options
                info = self.parse_data_options(data_options)
                info['src'] = attrs_dict.get('src', '')
                info['class'] = attrs_dict.get('class', '')
                
                if info.get('yxtpbh'):
                    self.images.append(info)
    
    @staticmethod
    def parse_data_options(data_options_str):
        """解析 data-options 字符串"""
        info = {}
        if not data_options_str:
            return info
        
        pairs = data_options_str.split(',')
        for pair in pairs:
            if ':' in pair:
                key, value = pair.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # 尝试转换为数字
                try:
                    value = float(value)
                except ValueError:
                    pass
                
                info[key] = value
        
        return info


def download_image(filename, output_dir=OUTPUT_DIR, subfolder=''):
    """下载单张图片"""
    full_output_dir = output_dir
    if subfolder:
        full_output_dir = os.path.join(output_dir, subfolder)
    
    os.makedirs(full_output_dir, exist_ok=True)
    
    # 尝试原始图URL
    url = BASE_URL + "YT_IMG/" + filename
    output_path = os.path.join(full_output_dir, filename)
    
    # 如果原始图不存在，尝试缩略图
    if not os.path.exists(output_path):
        url = BASE_URL + "ST_IMG/" + filename
        if not os.path.exists(output_path):
            url = BASE_URL + "ST_IMG/ST" + filename
    
    if os.path.exists(output_path):
        print(f"已存在: {filename}")
        return True
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200 and len(response.content) > 1000:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"下载成功: {filename}")
            return True
        else:
            print(f"下载失败 [{response.status_code}]: {filename}")
            return False
    except Exception as e:
        print(f"错误: {filename} - {str(e)}")
        return False


def download_images_by_depth(filenames, start_depth=None, end_depth=None, max_workers=5):
    """按深度范围下载图片"""
    
    # 从文件名解析深度（示例）
    # 文件名格式: T00000022710005000100.jpg
    # 解析规则: T + 起始深度(7位) + 终止深度(7位) + .jpg
    
    def parse_depth_from_filename(filename):
        """从文件名解析深度"""
        try:
            name = os.path.splitext(filename)[0]
            # 格式: T + 起始深度(7位) + 终止深度(7位)
            if name.startswith('T') or name.startswith('HC'):
                if name.startswith('T'):
                    depth_str = name[1:15]
                else:
                    depth_str = name[2:16]
                
                start = float(depth_str[:7]) / 1000
                end = float(depth_str[7:14]) / 1000
                return start, end
        except:
            pass
        return None, None
    
    # 筛选符合条件的图片
    selected_images = []
    for filename in filenames:
        s, e = parse_depth_from_filename(filename)
        if s is not None and e is not None:
            if start_depth and e < start_depth:
                continue
            if end_depth and s > end_depth:
                continue
            selected_images.append((filename, s, e))
    
    print(f"筛选出 {len(selected_images)} 张图片 (深度范围: {start_depth}-{end_depth}米)")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(download_image, fn): (fn, s, e) for fn, s, e in selected_images}
        
        success = 0
        failed = 0
        for future in as_completed(futures):
            fn, s, e = futures[future]
            if future.result():
                success += 1
            else:
                failed += 1
    
    print(f"下载完成: 成功 {success}, 失败 {failed}")


def generate_download_script_from_html(html_content, output_file="download_script.py"):
    """从HTML内容生成下载脚本"""
    
    parser = ImageParser()
    parser.feed(html_content)
    
    print(f"解析到 {len(parser.images)} 张岩心图片")
    
    # 生成图片列表
    images_list = []
    for img in parser.images:
        images_list.append({
            'filename': img.get('yxtpbh', ''),
            'qssd': img.get('qssd', 0),
            'zzsd': img.get('zzsd', 0),
            'width': img.get('width', 0),
            'height': img.get('height', 0),
            'src': img.get('src', ''),
            'url': BASE_URL + "ST_IMG/" + img.get('yxtpbh', '')
        })
    
    # 保存图片信息到JSON
    import json
    json_file = os.path.join(OUTPUT_DIR, 'image_list.json')
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(images_list, f, ensure_ascii=False, indent=2)
    
    print(f"图片列表已保存到: {json_file}")
    
    # 生成下载脚本
    script_content = f'''"""
岩心图像下载脚本 - 自动生成
钻孔: {ZKBBH}
档号: {DH}
共 {len(images_list)} 张图片
"""

import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

OUTPUT_DIR = r"{OUTPUT_DIR}"
BASE_URL = r"{BASE_URL}"

def download_image(filename, output_dir=OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    
    if os.path.exists(output_path):
        print(f"已存在: {{filename}}")
        return True
    
    url = BASE_URL + "ST_IMG/" + filename
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"下载成功: {{filename}}")
            return True
    except Exception as e:
        print(f"错误: {{filename}} - {{e}}")
        return False
    return False

def main():
    filenames = [
'''
    
    for img in images_list[:100]:  # 限制前100个
        script_content += f'        "{img["filename"]}",\\n'
    
    script_content += '''    ]
    
    print(f"开始下载 {len(filenames)} 张图片...")
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(download_image, fn) for fn in filenames]
        
        success = sum(1 for f in as_completed(futures) if f.result())
        print(f"下载完成: 成功 {success}, 失败 {len(filenames) - success}")

if __name__ == "__main__":
    main()
'''
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"下载脚本已生成: {output_file}")


if __name__ == "__main__":
    print("岩心图像下载工具")
    print(f"钻孔: {ZKBBH}")
    print(f"档号: {DH}")
    print(f"图片URL基础路径: {BASE_URL}")
    print("""
使用方法：
1. 保存网页HTML内容到文件
2. 运行脚本解析HTML获取图片列表
3. 按深度范围下载指定图片

示例：
python download_images.py --html page.html --start-depth 0 --end-depth 100
""")