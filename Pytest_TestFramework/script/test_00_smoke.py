# -*- coding: utf-8 -*-
"""
环境自检用例
@Desc: 验证 chromedriver / 被测系统前端是否可正常访问
"""
import allure

from page.page_login import PageLogin


@allure.feature("环境自检")
class TestSmoke:
    """冒烟测试：跑通说明测试环境可用"""

    def test_01_open_login_page(self, login_page):
        """打开系统首页，校验登录页面加载正常"""
        with allure.step("校验登录页面元素"):
            assert login_page.is_element_exist(login_page.login_button), "登录页面加载失败：未找到登录按钮"
            assert "" != login_page.base_text(login_page.login_button), "登录按钮文本为空"

    def test_02_open_login_page_by_page_object(self, driver):
        """登录页面对象的 __init__ 与 open_url 可用"""
        with allure.step("打开登录页面"):
            page = PageLogin(driver)
            page.open_url()
            assert page.is_element_exist(page.user_id), "登录页面加载失败：未找到用户 id 输入框"
