import time
import json
import logging
from logging import handlers
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from config import PATH

class DriverTools:
    driver = None

    @classmethod
    def get_driver(cls):
        if cls.driver is None:
            #  chromedriver 路径
            path = r"C:\Users\lenovo\AppData\Local\Programs\Python\Python314\chromedriver.exe"
            service = Service(executable_path=path)
            cls.driver = webdriver.Chrome(service=service)
            cls.driver.maximize_window()
            cls.driver.implicitly_wait(5)
        return cls.driver

    @classmethod
    def quit_driver(cls):
        if cls.driver is not None:
            time.sleep(1)
            cls.driver.quit()
            cls.driver = None

def read_json(file_name):
    data = []
    file_path = PATH + "/data/" + file_name
    with open(file_path, mode='r', encoding='utf-8') as f:
        tmp = json.load(f)
        for i in tmp:
            a = tuple(i.values())
            data.append(a)
        return data

class GetLog:
    __log = None
    @classmethod
    def get_log(cls):
        if cls.__log is None:
            cls.__log = logging.getLogger(__name__)
            cls.__log.setLevel(logging.INFO)
            # 日志保存在当前目录下
            filename = PATH + "/web.log"
            tf = logging.handlers.TimedRotatingFileHandler(filename=filename, when='midnight', interval=1, backupCount=3, encoding='utf-8')
            fmt = "%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s"
            tf.setFormatter(logging.Formatter(fmt))
            cls.__log.addHandler(tf)
        return cls.__log