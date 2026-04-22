"""
岩心图像批量下载脚本 - 全国数字岩心平台
ZK13-4-2钻孔
"""

import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# 配置参数
ZZJGDM = "12100000400014276N"
DH = "000010"
ZKBH = "ZK13-4-2"
XMM = "四川省第四届岩石矿物学会"

BASE_URL = f"https://ndcp.cgsi.cn/SWZXFILE/file/yanxinImages/{ZZJGDM}/{DH}_{ZKBH}/"
OUTPUT_DIR = f"images/{DH}_{ZKBH}"


def get_st_url(filename):
    """生成缩略图URL - T开头文件需要加ST前缀"""
    if filename.startswith('T'):
        return BASE_URL + "ST_IMG/ST" + filename
    elif filename.startswith('HC') or filename.startswith('S'):
        return BASE_URL + "ST_IMG/" + filename
    return BASE_URL + "ST_IMG/" + filename


def get_yt_url(filename):
    """生成原图URL"""
    return BASE_URL + "YT_IMG/" + filename


def download_image(filename, output_dir=OUTPUT_DIR, image_type='st'):
    """下载单张图片"""
    os.makedirs(output_dir, exist_ok=True)
    
    if image_type == 'st':
        url = get_st_url(filename)
    else:
        url = get_yt_url(filename)
    
    output_path = os.path.join(output_dir, filename)
    
    if os.path.exists(output_path):
        return True
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200 and len(response.content) > 1000:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
        return False
    except:
        return False


def batch_download(filenames, output_dir=OUTPUT_DIR, image_type='st', max_workers=5):
    """批量下载"""
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"开始下载 {len(filenames)} 张{('缩略图' if image_type == 'st' else '原图')}...")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(download_image, fn, output_dir, image_type): fn for fn in filenames}
        
        success = 0
        for future in as_completed(futures):
            if future.result():
                success += 1
    
    print(f"下载完成: {success}/{len(filenames)} 成功")
    return success


if __name__ == "__main__":
    # 测试下载
    test_files = [
        'T00000022710005000100.jpg',
        'T00000022710004000200.jpg',
        'T00000022710005000210.jpg',
    ]
    
    print("=" * 50)
    print(f"钻孔: {ZKBH}")
    print(f"档号: {DH}")
    print(f"ZZJGDM: {ZZJGDM}")
    print("=" * 50)
    print()
    
    print("测试缩略图下载...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    success = 0
    for f in test_files:
        st_url = get_st_url(f)
        print(f"\n文件: {f}")
        print(f"URL: {st_url}")
        
        if download_image(f, OUTPUT_DIR, 'st'):
            print("状态: 成功 ✓")
            success += 1
        else:
            print("状态: 失败 ✗")
    
    print()
    print(f"测试完成: {success}/{len(test_files)} 成功")
    print(f"输出目录: {OUTPUT_DIR}")