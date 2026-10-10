# -*- coding: utf-8 -*-
"""
全局配置模块
@Desc: 学生选课管理系统 UI 自动化测试 - 路径 / 被测地址 / 测试数据配置
"""
import os

from faker import Faker

# 框架根目录（Pytest_TestFramework）
PATH = os.path.dirname(os.path.abspath(__file__))

# 被测系统地址（可用环境变量覆盖，方便切换测试环境）
BASE_URL = os.getenv("BASE_URL", "http://localhost:8081")  # 前端 Vue 地址（vue-cli 默认 8080）
API_URL = os.getenv("API_URL", "http://localhost:10086")  # 后端 Spring Boot 地址

# chromedriver 路径（与本机 Python 环境保持一致）
CHROME_DRIVER = os.getenv(
    "CHROME_DRIVER",
    r"C:\Users\lenovo\AppData\Local\Programs\Python\Python314\chromedriver.exe"
)

# 是否无头模式运行（CI 环境可设置环境变量：HEADLESS=true）
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"

# 截图 / 日志目录
IMG_PATH = os.path.join(PATH, "imgs")
LOG_PATH = os.path.join(PATH, "log")
for _dir in (IMG_PATH, LOG_PATH):
    if not os.path.exists(_dir):
        os.makedirs(_dir)

# 初始化账号（数据来源：StudentManageSystem/mysql/studentms.sql）
ADMIN_ID, ADMIN_PASSWORD = 6, "123"  # t 表：admin
TEACHER_ID, TEACHER_PASSWORD = 4, "123"  # t 表：李玉民
STUDENT_ID, STUDENT_PASSWORD = 2, "123"  # s 表：张四

fk = Faker(locale="zh_CN")


def random_name():
    """
    生成符合前端校验（2~5 个字符）的随机中文姓名
    追加随机数字后缀，避免与历史测试数据重名
    """
    name = fk.last_name() + fk.first_name()
    suffix = str(fk.random_int(min=10, max=99))
    return name[: 5 - len(suffix)] + suffix


def random_password(length=6):
    """生成随机数字密码"""
    return str(fk.random_number(digits=length, fix_len=True))


def random_credit():
    """生成 1~10 之间的随机学分"""
    return fk.random_int(min=1, max=10)


def random_course_name():
    """生成随机课程名（带随机后缀，避免与历史数据重名）"""
    return f"自动化{fk.last_name()}{fk.random_int(min=1000, max=9999)}"


if __name__ == "__main__":
    print(f"BASE_URL = {BASE_URL}")
    print(f"API_URL = {API_URL}")
    print(f"随机姓名 = {random_name()}, 随机密码 = {random_password()}, 随机学分 = {random_credit()}")
