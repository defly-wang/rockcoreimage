import requests
import json

params = {
    'xmmc': '四川省会理县拉拉厂铜矿床地质特征及成矿规律研究',
    'zkbh': 'ZK13-4-2',
    'dh': '000010',
    'zkid': 'FBE0109B220146338492888681930853'
}

url = 'https://ndcp.cgsi.cn/SWZX/zkxxComm/queryZztTableData'

try:
    r = requests.get(url, params=params, timeout=30)
    print('Status:', r.status_code)
    if r.status_code == 200:
        data = r.json()
        print('Code:', data.get('code'))
        if data.get('code') == 200:
            rows = data.get('data', [])
            print('Rows:', len(rows))
            for i, row in enumerate(rows[:10]):
                print(i+1, row)
        else:
            print('Error:', data)
except Exception as e:
    print('Error:', e)