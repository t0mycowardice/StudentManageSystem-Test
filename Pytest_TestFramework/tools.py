# -*- coding: utf-8 -*-
"""
公共工具层
@Desc: 浏览器驱动、JSON 测试数据读取、日志
"""
import json
import logging
import time
from logging import handlers

from config import LOG_PATH, PATH
from page.driver_start import getdriver


class DriverTools:
    """浏览器驱动类：整个测试用例共用一个 driver 实例"""

    driver = None

    @classmethod
    def get_driver(cls):
        """获得浏览器驱动"""
        if cls.driver is None:
            cls.driver = getdriver()  # 打开 chrome 浏览器
            cls.driver.maximize_window()  # 浏览器窗口最大化
            cls.driver.implicitly_wait(5)  # 隐式等待
        return cls.driver

    @classmethod
    def quit_driver(cls):
        """退出浏览器驱动"""
        if cls.driver is not None:
            time.sleep(1)  # 等待 1 秒，方便观察结果
            cls.driver.quit()  # 退出浏览器
            cls.driver = None  # 置空


def read_json(file_name):
    """
    读取 data 目录下的 json 数据文件
    :return: 数据转换为元组列表，方便 pytest.mark.parametrize 数据驱动使用
    """
    data = []
    file_path = PATH + "/data/" + file_name
    with open(file_path, mode="r", encoding="utf-8") as f:
        tmp = json.load(f)  # 读取 json 文件并转换为 Python 对象
        for i in tmp:
            a = tuple(i.values())
            data.append(a)
        return data


def read_json_dict(file_name):
    """
    读取 data 目录下的 json 数据文件（保留字典结构）
    :return: 字典列表，按字段名取值，用例可读性更好
    """
    file_path = PATH + "/data/" + file_name
    with open(file_path, mode="r", encoding="utf-8") as f:
        return json.load(f)


class GetLog:
    """日志类：单例模式，按天切分日志文件"""

    __log = None

    @classmethod
    def get_log(cls):
        if cls.__log is None:
            # 获取日志器
            cls.__log = logging.getLogger(__name__)
            # 设置日志级别
            cls.__log.setLevel(logging.INFO)
            if not cls.__log.handlers:
                # 获取处理器
                filename = LOG_PATH + "/web.log"
                tf = handlers.TimedRotatingFileHandler(
                    filename=filename,  # 日志文件名
                    when="midnight",  # 日志归档时间：每天归档一次
                    interval=1,
                    backupCount=3,  # 保留三天
                    encoding="utf-8",
                )
                # 获取格式器
                fmt = "%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s"
                tf.setFormatter(logging.Formatter(fmt))
                # 将格式器添加到处理器，将处理器添加到日志器
                cls.__log.addHandler(tf)
        # 注意：return 必须放在 if 外面，否则第二次调用拿到的是 None
        return cls.__log


if __name__ == "__main__":
    log = GetLog.get_log()
    log.info("日志测试")
    print(read_json("login_data.json"))
