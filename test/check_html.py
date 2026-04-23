from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Edge()

try:
    driver.get(r'C:\defly\png\综合数据展示.htm')
    import time
    time.sleep(5)
    
    ysmc_cell = driver.find_element(By.CSS_SELECTOR, 'td[field="YSMC"]')
    html = ysmc_cell.get_attribute('outerHTML')
    print('YSMC HTML:', html[:500])
    
finally:
    driver.quit()