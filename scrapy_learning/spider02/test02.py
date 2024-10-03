from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from utils import create_chrome_driver

browser = create_chrome_driver()

browser.get('https://www.') #进入登录页面
#隐式等待
browser.implicitly_wait(10) 

#获取页面元素模拟用户的输入和点击行为进行登录以获取cookies
username_input = browser.find_element(By.CSS_SELECTOR,'css选择到的用户名输入框')
username_input.send_keys('用户名')
password_input = browser.find_element(By.CSS_SELECTOR,'css选择到的密码输入框')
password_input.send_keys('密码')
login_button = browser.find_element(By.CSS_SELECTOR,'css选择到的登录按钮')
login_button.click()
#显示等待
wait_obj = WebDriverWait(browser,10)
wait_obj.until(EC.presence_of_element_located((By.CSS_SELECTOR,'css选择要等到出现的元素')))
'''
EC.presence_of_all_elements_located() 是等到所有对应元素出现
EC.presence_of_element_located() 是等到出现一个对应元素就行
'''
'''
指定在10s以内进行等待,若10s以内出现对应判断条件成立,则结束等待继续往下执行.
否则继续等待,若超过10s则报错.
'''
#将cookies写入文件
with open('cookies.json','w') as file:
    json.dump(browser.get_cookies(),file)



