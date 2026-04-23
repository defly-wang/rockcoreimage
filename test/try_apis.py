import requests

# 尝试不同的API端点
endpoints = [
    'https://ndcp.cgsi.cn/SWZX/zkxxComm/queryZztTableData',
    'https://ndcp.cgsi.cn/SWZX/zkxxComm/zkdzzhsj',
    'https://ndcp.cgsi.cn/SWZX/zkxxComm/queryZztData',
    'https://ndcp.cgsi.cn/SWZX/front/zkzzt/queryZztTableData',
]

params = {
    'xmmc': '四川省会理县拉拉厂铜矿床地质特征及成矿规律研究',
    'zkbh': 'ZK13-4-2',
    'dh': '000010'
}

for url in endpoints:
    try:
        r = requests.get(url, params=params, timeout=10)
        print('URL:', url.split('/')[-1])
        print('Status:', r.status_code)
        data = r.json()
        print('Code:', data.get('code'), 'Msg:', str(data.get('msg', ''))[:30])
        if data.get('code') == 200:
            rows = data.get('data', [])
            print('Rows:', len(rows))
            print('First row:', rows[0] if rows else 'None')
            break
        print()
    except Exception as e:
        print('Error:', str(e)[:50])
        print()