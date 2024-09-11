'''
这个脚本针对  
http://bbs.51testing.com/thread-1420791-1-1.html
这个网站的登录,用selenium模拟自动化签到功能.
2024.9.11
'''
import re
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 设置Selenium使用的浏览器驱动
#在scrapy项目中,只需要将驱动文件(.exe文件)放在环境目录(.venv)下的bin(也可能是Script)中即可
driver_path = 'E:\2web\spider\spider01\chromedriver.exe'  # 替换为你的chromedriver路径
options = webdriver.ChromeOptions()
# options.add_argument('--headless')  # 无头模式
driver = webdriver.Chrome(options=options)

#先登录
# 访问登录页面
url = "http://bbs.51testing.com/thread-1420791-1-1.html"
driver.get(url)

# 等待页面加载完成
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#ls_password')))

#找到对应的输入框输入用户名和密码
elem1 = driver.find_element(By.ID, 'ls_username')
elem2 = driver.find_element(By.ID, 'ls_password')
username = '对应的用户名'
elem1.send_keys(username)
password = '对应的密码'
elem2.send_keys(password)

# 等待登录按钮出现
login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.pn.vm')))
login_button.click()

# 等待模态对话框中的关闭按钮出现并点击它
close_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, ".flbc"))
)
# print(close_button)
close_button.click()
#在指定时间内,当指定元素消失后继续往下执行,否则报错.
# wait.until(EC.invisibility_of_element_located(loading_element))
'''
这里对于那些原本就不在页面中的元素,可能在元素出现之前就进行了检测,
检测结果直接就为"元素已消失",因此直接往下执行代码,而出现"不等待"的情况.
针对这种情况,可以用逆向思维:
先等待元素出现,然后当元素出现后点击关闭按钮将其关闭.
'''
# 登录后获取 cookies
cookies = driver.get_cookies()
# 将 cookies 转换为 JSON 格式并保存到文件
with open('cookies.json', 'w') as file:
    json.dump(cookies, file)
    
# 后续访问时，从文件中读取 cookies 并添加到 WebDriver
with open('cookies.json', 'r') as file:
    cookies = json.load(file)

# 添加 cookies
for cookie in cookies:
    if 'expiry' in cookie:
        del cookie['expiry']  # 必须删除expiry，因为重新添加时不能有expiry
    driver.add_cookie(cookie)

#进行签到
signpage_url_elem = driver.find_element(By.CSS_SELECTOR,'#mn_N462e a')
signpage_url = signpage_url_elem.get_attribute('href')
print(signpage_url)
driver.get(signpage_url)

# 定位到对应的单选按钮元素
radio_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='radio'][name='qdmode'][value='2']")))
# 选中并点击该单选按钮
radio_button.click()
#定位到对应的"心情"选择
mood_button = driver.find_element(By.CSS_SELECTOR,'#ym')
# 选中并点击该单选按钮
mood_button.click()
# 定位到对应的签到按钮元素
# 这里假设按钮是页面中唯一的一个具有特定src的<img>标签的<a>标签
sign_in_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='qiandao']/table[1]/tbody/tr/td/div/a")))

# 选中并点击该签到按钮
sign_in_button.click()

