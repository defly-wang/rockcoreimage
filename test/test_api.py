import requests

# 使用已有参数尝试API调用
test_params = [
    {'zkbh': 'ZK13-4-2', 'dh': '000010'},
    {'xmmc': '四川省会理县拉拉厂铜矿床地质特征及成矿规律研究', 'zkbh': 'ZK13-4-2', 'dh': '000010'},
]

url = 'https://ndcp.cgsi.cn/SWZX/zkxxComm/queryZztTableData'

for params in test_params:
    try:
        r = requests.get(url, params=params, timeout=15)
        print('Params:', params)
        print('Status:', r.status_code)
        data = r.json()
        print('Response:', data.get('code'), data.get('msg', '')[:50] if data.get('msg') else '')
        if data.get('code') == 200:
            print('Data rows:', len(data.get('data', [])))
            break
        print()
    except Exception as e:
        print('Error:', e)