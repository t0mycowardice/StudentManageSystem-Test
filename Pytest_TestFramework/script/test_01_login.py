# -*- coding: utf-8 -*-
"""
登录模块测试用例
@Desc: 数据驱动（data/login_data.json）+ 页面跳转 + 表单校验 + 越权安全用例
"""
import allure
import pytest

from config import ADMIN_ID, ADMIN_PASSWORD, BASE_URL, STUDENT_ID, STUDENT_PASSWORD
from page.page_admin import PageAdminHome
from script import log
from tools import read_json

pytestmark = pytest.mark.login


@allure.epic("学生选课管理系统")
@allure.feature("登录模块")
class TestLogin:
    """登录功能测试类"""

    @pytest.mark.parametrize("user_type,user_id,password,expect", read_json("login_data.json"))
    def test_01_login(self, assert_login, user_type, user_id, password, expect):
        """数据驱动登录测试：管理员 / 教师 / 学生登录，含密码错误与登录类型错误场景"""
        allure.dynamic.story(f"{user_type} 用户登录")
        log.info(f"登录用例：{user_type} - {user_id} / {password}，期望：{expect}")
        assert_login(user_id, password, user_type, expect)

    def test_02_login_success_jump(self, login_page):
        """管理员登录成功：提示登录成功、跳转后台首页并写入 sessionStorage"""
        with allure.step("输入管理员账号密码并登录"):
            login_page.login(ADMIN_ID, ADMIN_PASSWORD, "admin")
        with allure.step("校验跳转到管理员首页"):
            login_page.wait_url_contains("/adminHome")
            assert PageAdminHome(login_page.driver).is_admin_home(), "登录成功后未进入管理员首页"
        with allure.step("校验登录态写入 sessionStorage"):
            assert login_page.get_session("token") == "true", "token 未写入 sessionStorage"
            assert login_page.get_session("type") == "admin", "用户类型未写入 sessionStorage"
            assert login_page.get_session("name") == "admin", "用户名未写入 sessionStorage"

    def test_03_login_form_validate(self, login_page):
        """登录表单必填校验：不输入任何内容直接点击登陆"""
        with allure.step("空表单点击登陆"):
            login_page.base_click(login_page.login_button)
            errors = login_page.get_form_errors()
            log.info(f"表单校验提示：{errors}")
        with allure.step("校验必填项提示"):
            assert "请输入用户 id" in errors, f"未提示用户 id 必填，实际提示：{errors}"
            assert "请输入密码" in errors, f"未提示密码必填，实际提示：{errors}"

    def test_04_login_fail_stay_login_page(self, login_page):
        """登录失败场景：停留在登录页面，不写入登录态"""
        with allure.step("使用错误密码登录"):
            login_page.login(ADMIN_ID, "error_pwd", "admin")
            tip = login_page.get_message()
            log.info(f"登录失败提示：{tip}")
            assert "登陆失败" in tip, f"密码错误时未提示登陆失败，实际提示：{tip}"
        with allure.step("校验未跳转且未写入登录态"):
            assert "/login" in login_page.driver.current_url, "登录失败后却跳转了页面"
            assert login_page.get_session("token") is None, "登录失败却写入了 token"

    @pytest.mark.security
    @pytest.mark.xfail(
        reason="已确认缺陷：前端仅校验 sessionStorage.type，后端无鉴权，学生可越权进入管理员后台",
        strict=False,
    )
    def test_05_student_privilege_escalation(self, login_page):
        """安全测试：学生登录后篡改 sessionStorage 的 type 为 admin，应被拦截"""
        with allure.step("学生账号登录"):
            login_page.login(STUDENT_ID, STUDENT_PASSWORD, "student")
            login_page.wait_url_contains("/student")
            assert "登陆成功" in login_page.get_message(), "学生账号登录失败"
        with allure.step("篡改 sessionStorage：type 由 student 改为 admin"):
            login_page.set_session("type", "admin")
        with allure.step("访问管理员首页，期望被重定向回登录页"):
            login_page.driver.get(BASE_URL + "/adminHome")
            assert "/login" in login_page.driver.current_url, "存在垂直越权漏洞：学生可直接访问管理员后台"
