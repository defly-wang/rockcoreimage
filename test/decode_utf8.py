import re
from selenium import webdriver

driver = webdriver.Edge()

try:
    driver.get(r'C:\defly\png\综合数据展示.htm')
    import time
    time.sleep(5)
    
    page_source = driver.page_source
    
    content = page_source.encode('utf-8').decode('utf-8', errors='replace')
    
    ysmc_pattern = r'<td[^>]*field="YSMC"[^>]*>.*?<span[^>]*>([^<]+)</span>'
    ysmc = re.findall(ysmc_pattern, content, re.DOTALL)
    print('YSMC:')
    for i, y in enumerate(ysmc[:10]):
        print(f'  {i+1}. {y}')
    
    hd_pattern = r'<td[^>]*field="HD"[^>]*>.*?<span[^>]*>(\d+\.\d+)</span>'
    hd = re.findall(hd_pattern, content, re.DOTALL)
    print('\nHD:')
    for h in hd[:10]:
        print(f'  {h}')
    
finally:
    driver.quit()