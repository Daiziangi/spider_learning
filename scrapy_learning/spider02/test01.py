from utils import create_chrome_driver,add_cookies

browser = create_chrome_driver()
'''
1.访问登录页面 browser.get('https://')
2.  2.0 在获取和保存cookies文件的代码如下:

with open('cookies.json','w') as file:
    json.dump(browser.get_cookies(),file)

    2.1 添加cookie信息  add_cookies(browser, 'cookies.json') 
3.再次访问登录后的页面 browser.get('https://')
'''
browser.get('https://www.hao123.com')