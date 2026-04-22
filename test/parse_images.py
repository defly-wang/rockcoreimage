"""
从保存的网页HTML提取岩心图片列表
使用方法：
1. 在浏览器中打开岩心平台钻孔页面
2. 滚动到页面底部确保加载所有图片
3. 右键 → 另存为 → 保存完整HTML
4. 运行此脚本解析图片列表
"""

import os
import re
import json
from html.parser import HTMLParser


class RockImageParser(HTMLParser):
    """解析岩心图片HTML"""
    
    def __init__(self):
        super().__init__()
        self.images = []
    
    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            attrs_dict = dict(attrs)
            cls = attrs_dict.get('class', '')
            
            if 'yanxinImage' in cls:
                data_options = attrs_dict.get('data-options', '')
                src = attrs_dict.get('src', '')
                
                # 解析 data-options
                info = self.parse_data_options(data_options)
                info['src'] = src
                info['class'] = cls
                info['imgName'] = cls.replace('yanxinImage ', '').strip()
                
                if info.get('yxtpbh'):
                    self.images.append(info)
    
    @staticmethod
    def parse_data_options(data_str):
        """解析 qssd:9.58,zzsd:10.12,yxtpbh:xxx 格式"""
        info = {}
        if not data_str:
            return info
        
        for pair in data_str.split(','):
            if ':' in pair:
                key, value = pair.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # 转换数字
                try:
                    value = float(value)
                except ValueError:
                    pass
                
                info[key] = value
        
        return info


def parse_html_file(html_file):
    """解析HTML文件"""
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    parser = RockImageParser()
    parser.feed(html_content)
    
    return parser.images


def generate_download_list(images, output_file='download_list.json'):
    """生成下载列表"""
    # 按深度排序
    images.sort(key=lambda x: x.get('qssd', 0))
    
    download_list = []
    for img in images:
        download_list.append({
            'filename': img.get('yxtpbh', ''),
            'qssd': img.get('qssd', 0),
            'zzsd': img.get('zzsd', 0),
            'height': img.get('height', 0),
            'src': img.get('src', ''),
            'imgName': img.get('imgName', ''),
        })
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(download_list, f, ensure_ascii=False, indent=2)
    
    return download_list


def create_download_script(images, script_file='download_images.py'):
    """生成下载脚本"""
    ZZJGDM = '12100000400014276N'
    DH = '000010'
    ZKBH = 'ZK13-4-2'
    BASE_URL = f'https://ndcp.cgsi.cn/SWZXFILE/file/yanxinImages/{ZZJGDM}/{DH}_{ZKBH}/'
    
    script = f'''"""
岩心图像批量下载脚本
ZK13-4-2 钻孔
共 {len(images)} 张图片
自动生成
"""

import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

ZZJGDM = "{ZZJGDM}"
DH = "{DH}"
ZKBH = "{ZKBH}"
BASE_URL = "{BASE_URL}"
OUTPUT_DIR = f"images/{{DH}}_{{ZKBH}}"


def get_url(filename):
    """生成图片URL"""
    if filename.startswith('T'):
        return BASE_URL + "ST_IMG/ST" + filename
    return BASE_URL + "ST_IMG/" + filename


def download(filename, output_dir=OUTPUT_DIR):
    """下载单张图片"""
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    
    if os.path.exists(output_path):
        return True
    
    url = get_url(filename)
    try:
        r = requests.get(url, timeout=30)
        if r.status_code == 200 and len(r.content) > 1000:
            with open(output_path, 'wb') as f:
                f.write(r.content)
            return True
    except:
        return False
    return False


def main():
    filenames = [
'''
    
    for img in images[:200]:  # 限制200个
        fname = img.get('yxtpbh', '')
        qssd = img.get('qssd', 0)
        script += f'        "{fname}",  # {qssd}m\\n'
    
    script += '''    ]
    
    print(f"开始下载 {{len(filenames)}} 张图片...")
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(download, fn) for fn in filenames]
        success = sum(1 for f in as_completed(futures) if f.result())
    
    print(f"完成: {{success}}/{{len(filenames)}}")


if __name__ == "__main__":
    main()
'''
    
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(script)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python parse_images.py <html_file>")
        print("  1. 在浏览器中打开岩心平台钻孔页面")
        print("  2. 滚动加载所有图片")
        print("  3. 另存为完整HTML")
        print("  4. 运行: python parse_images.py saved_page.html")
        sys.exit(1)
    
    html_file = sys.argv[1]
    
    if not os.path.exists(html_file):
        print(f"文件不存在: {html_file}")
        sys.exit(1)
    
    print(f"解析HTML: {html_file}")
    
    images = parse_html_file(html_file)
    
    print(f"找到 {len(images)} 张岩心图片")
    
    if images:
        # 生成下载列表
        download_list = generate_download_list(images)
        print(f"下载列表已保存: download_list.json")
        
        # 生成下载脚本
        create_download_script(images)
        print(f"下载脚本已生成: download_images.py")
        
        # 显示前5张
        print("\n前5张图片:")
        for img in images[:5]:
            print(f"  {img.get('yxtpbh')} [{img.get('qssd')}-{img.get('zzsd')}m]")