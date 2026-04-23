from playwright.sync_api import sync_playwright

# 安装浏览器
print("Installing browsers...")
from playwright._impl._driver import driver
driver.install()

print("Done")