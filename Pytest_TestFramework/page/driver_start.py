# -*- coding: utf-8 -*-
"""
浏览器驱动启动模块
@Desc: 统一在此处配置 chrome 启动参数，其它模块只调用 getdriver()
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from config import CHROME_DRIVER, HEADLESS


def getdriver():
    """启动 chrome 浏览器并返回驱动对象"""
    options = Options()
    if HEADLESS:
        # 无头模式：CI / 服务器环境使用，不弹出浏览器窗口
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
    # 去掉"Chrome 正受到自动测试软件的控制"提示
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_experimental_option("useAutomationExtension", False)
    service = Service(executable_path=CHROME_DRIVER)
    return webdriver.Chrome(service=service, options=options)
