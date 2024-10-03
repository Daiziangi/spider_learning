import json
from selenium import webdriver


'''
需要将对应版本的ChromeDriver驱动复制到scrapy项目的虚拟环境的Scripts文件夹下
(也可能是bin文件夹下).总之要与Python.exe/pip.exe在同级中.
这个文件是专门用来写一些工具函数的,这些函数可以被其他模块调用.
'''

#前面的'*'表示接下来的参数都是关键字参数,
#headless默认为False,即默认为非无头模式
def create_chrome_driver(*, headless=False):
    options = webdriver.ChromeOptions()
    if headless: #如果headless为True,则开启无头模式,也就是没有浏览器窗口显示.
        options.add_argument('--headless')
    #这里是为了防止网站检测到是自动化测试工具而导致无法访问
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    browser = webdriver.Chrome(options=options)
    #这里是为了防止网站检测到是自动化测试工具而导致无法访问
    browser.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",   #这个方法是在每次打开新页面时都会执行一次里面的JS代码
        #这里是接下来要执行的JS代码,
        # 目的是将浏览器中内置的navigator对象(代表着我使用的浏览器)
        # 将这个对象中的webdriver属性设置为undefined,以伪装浏览器.
        # 用selenium驱动的浏览器这个值默认为TRUE.
        # 这样就可以防止网站检测到是自动化测试工具而导致无法访问
        {"source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
    })
    return browser

# def add_cookies(browser:webdriver.Chrome, cookie_file):  #这样写的话,下面browser.add_cookie()函数会自动出现补全提示.
def add_cookies(browser, cookie_file):
    with open(cookie_file,'r') as f:
        cookies_list = json.load(f)
        for cookie_dict in cookies_list:
            if  cookie_dict['secure']:
                browser.add_cookie(cookie_dict)