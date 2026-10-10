# -*- coding: utf-8 -*-
"""
登录页面
@Desc: 对应 student_client/src/views/login/index.vue
"""
import time

from selenium.webdriver.common.by import By

from base.page_base import BasePage
from config import BASE_URL


class PageLogin(BasePage):
    """登录页面类"""

    # 业务用户类型 -> 页面单选框文案
    USER_TYPE_LABEL = {"student": "学生", "teacher": "老师", "admin": "admin"}

    def __init__(self, driver):
        super().__init__(driver)
        # 定位元素：用户 id / 用户密码 / 用户类型 / 登录按钮
        self.user_id = (By.XPATH, "//label[contains(text(),'用户 id')]/following::input[1]")
        self.password = (By.XPATH, "//label[contains(text(),'用户密码')]/following::input[1]")
        self.radio_type = (
            By.XPATH,
            "//span[contains(@class,'el-radio__label')][normalize-space()='%s']",
        )
        self.login_button = (By.XPATH, "//button[.//span[normalize-space()='登陆']]")

    def open_url(self):
        """打开登录页面"""
        self.driver.get(BASE_URL + "/login")

    def login(self, user_id, password, user_type="admin"):
        """
        执行登录操作
        :param user_id: 用户 id（学生为学号、教师为工号、管理员为工号）
        :param password: 密码
        :param user_type: 用户类型 student / teacher / admin
        """
        # 输入用户 id
        self.base_input(self.user_id, user_id)
        # 输入用户密码
        self.base_input(self.password, password)
        # 选择用户类型
        self.select_type(user_type)
        # 点击登录
        self.base_click(self.login_button)
        time.sleep(0.5)  # 等待接口响应与提示弹出

    def select_type(self, user_type):
        """选择用户类型：student / teacher / admin"""
        label = self.USER_TYPE_LABEL.get(user_type, user_type)
        self.base_click((self.radio_type[0], self.radio_type[1] % label))

    def get_user_name(self):
        """获取登录后写入 sessionStorage 的用户名"""
        return self.get_session("name")
