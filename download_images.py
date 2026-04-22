"""
岩心图像批量下载脚本
URL: https://ndcp.cgsi.cn/SWZXFILE/file/yanxinImages/{ZZJGDM}/{dh}_{zkbh}/YT_IMG/{filename}
"""

import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# 配置参数
ZZJGDM = "12100000400014276N"
ZKBBH = "ZK13-4-2"
DH = "000010"

BASE_URL = f"https://ndcp.cgsi.cn/SWZXFILE/file/yanxinImages/{ZZJGDM}/{DH}_{ZKBBH}/YT_IMG/"

OUTPUT_DIR = f"images/{DH}_{ZKBBH}"

# 测试图片
TEST_IMAGES = [
    "T00000022710004000200.jpg",
    "HC51-1.jpg",
    "T00000022810004000210.jpg",
]


def download_image(filename, output_dir=OUTPUT_DIR):
    """下载单张图片"""
    os.makedirs(output_dir, exist_ok=True)
    
    url = BASE_URL + filename
    output_path = os.path.join(output_dir, filename)
    
    if os.path.exists(output_path):
        print(f"已存在: {filename}")
        return True
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
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


def download_images(filenames, max_workers=5):
    """批量下载图片"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"开始下载 {len(filenames)} 张图片到 {OUTPUT_DIR}/")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(download_image, fn): fn for fn in filenames}
        
        success = 0
        failed = 0
        for future in as_completed(futures):
            if future.result():
                success += 1
            else:
                failed += 1
    
    print(f"\n下载完成: 成功 {success}, 失败 {failed}")


if __name__ == "__main__":
    # 测试下载
    print("测试图片可访问性...")
    for img in TEST_IMAGES:
        url = BASE_URL + img
        try:
            response = requests.head(url, timeout=10)
            status = response.status_code
        except:
            status = "错误"
        print(f"  {img}: {status}")
    
    print(f"\n图片URL格式: {BASE_URL}{{filename}}")
    print("""
使用说明：
1. 需要先获取图片文件名列表
2. 可以通过分析网页/JavaScript代码获取图片名称
3. 或者使用浏览器开发者工具捕获API响应

示例文件名格式：
- T00000022710004000200.jpg (四川大学仪器)
- HC51-1.jpg (荆州华孚仪器)
- S前缀为缩略图
""")