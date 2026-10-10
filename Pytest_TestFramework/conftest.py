# -*- coding: utf-8 -*-
"""
conftest.py
@Desc: pytest 夹具（浏览器驱动 / 页面对象 / 断言）+ Allure 集成（失败自动截图、会话结束自动生成报告）
"""
import os
import platform
import shutil
import subprocess
import time

import allure
import pytest

from config import ADMIN_ID, ADMIN_PASSWORD, BASE_URL
from page.page_admin import PageAdminHome
from page.page_login import PageLogin
from tools import DriverTools, GetLog

# 获取日志器
log = GetLog.get_log()

# Allure 结果 / 报告目录
ALLURE_RESULTS_DIR = "./report"
ALLURE_REPORT_DIR = "./new_report"


# -------------------- 浏览器驱动 fixture --------------------
@pytest.fixture(scope="function")
def driver():
    """提供浏览器驱动，自动启动和退出"""
    driver = DriverTools.get_driver()
    yield driver
    DriverTools.quit_driver()


# -------------------- 页面对象 fixtures（打开页面） --------------------
@pytest.fixture(scope="function")
def login_page(driver):
    """返回已打开登录页面的 PageLogin 实例"""
    with allure.step("打开登录页面"):
        page = PageLogin(driver)
        page.open_url()
    return page


@pytest.fixture(scope="function")
def admin_page(driver):
    """管理员登录后返回已进入后台首页的 PageAdminHome 实例"""
    with allure.step("管理员登录"):
        login = PageLogin(driver)
        login.open_url()
        login.login(ADMIN_ID, ADMIN_PASSWORD, "admin")
        tip = login.get_message()
        assert "登陆成功" in tip, f"管理员登录失败：{tip}"
    with allure.step("进入管理员首页"):
        page = PageAdminHome(driver)
        page.open_url()
        assert page.is_admin_home(), "未进入管理员首页 /adminHome"
    return page


# -------------------- 断言 fixtures（含 Allure 步骤与附件） --------------------
@pytest.fixture
def assert_login(login_page):
    """提供登录断言函数，自动记录 Allure 步骤，失败时 attach 截图"""

    def _assert_login(user_id, password, user_type, expected_result):
        with allure.step(f"执行登录断言 - 期望结果：{expected_result}"):
            with allure.step(f"输入账号：{user_id}，密码：{password}，类型：{user_type}"):
                login_page.login(user_id, password, user_type)

            actual = login_page.get_message()
            log.info(f"登录断言：期望 -> {expected_result}, 实际 -> {actual}")
            allure.attach(
                f"期望：{expected_result}\n实际：{actual}",
                name="断言详情",
                attachment_type=allure.attachment_type.TEXT,
            )

            if expected_result not in actual:
                screenshot_path = login_page.get_shot(f"login_fail_{int(time.time())}.png")
                with open(screenshot_path, "rb") as f:
                    allure.attach(
                        f.read(),
                        name="登录失败截图",
                        attachment_type=allure.attachment_type.PNG,
                    )
                raise AssertionError(f"登录断言失败：期望包含 '{expected_result}'，实际为 '{actual}'")

    return _assert_login


# -------------------- pytest 钩子：失败时截图并 attach 到 Allure --------------------
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """测试失败时自动截图并 attach 到 Allure 报告"""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        try:
            driver = item.funcargs.get("driver")
            if driver:
                filename = os.path.join("imgs", f"{item.name}_{int(time.time())}.png")
                driver.save_screenshot(filename)
                log.info(f"测试失败，截图已保存：{filename}")
                with open(filename, "rb") as f:
                    allure.attach(
                        f.read(),
                        name=f"失败截图_{item.name}",
                        attachment_type=allure.attachment_type.PNG,
                    )
        except Exception as e:
            log.warning(f"截图失败：{e}")


# -------------------- pytest 钩子：会话结束自动生成 Allure 报告 --------------------
def _write_allure_environment(results_dir):
    """向 allure 结果目录写入环境信息，报告中可查看"""
    try:
        os.makedirs(results_dir, exist_ok=True)
        with open(os.path.join(results_dir, "environment.properties"), "w", encoding="utf-8") as f:
            f.write(f"BaseUrl={BASE_URL}\n")
            f.write("Browser=Chrome\n")
            f.write(f"Python={platform.python_version()}\n")
            f.write(f"Platform={platform.system()} {platform.release()}\n")
    except Exception as e:
        log.warning(f"写入 Allure 环境信息失败：{e}")


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """
    整个测试会话结束后自动调用 allure generate 生成离线 HTML 报告
    可通过环境变量控制：
        AUTO_ALLURE_REPORT = true/false（默认 true，是否自动生成报告）
        ALLURE_RESULTS_DIR = ./report（默认）
        ALLURE_REPORT_DIR  = ./new_report（默认）
        OPEN_ALLURE_REPORT = true/false（默认 false，是否自动打开报告）
    """
    if os.getenv("AUTO_ALLURE_REPORT", "true").lower() != "true":
        log.info("已禁用自动生成 Allure 报告（AUTO_ALLURE_REPORT=false）")
        return

    results_dir = os.getenv("ALLURE_RESULTS_DIR", ALLURE_RESULTS_DIR)
    report_dir = os.getenv("ALLURE_REPORT_DIR", ALLURE_REPORT_DIR)
    _write_allure_environment(results_dir)

    if not os.path.isdir(results_dir):
        log.warning(f"Allure 结果目录不存在：{results_dir}，跳过报告生成")
        return
    if not shutil.which("allure"):
        log.error("未找到 allure 命令行工具，请安装 Allure 并添加到 PATH")
        return

    cmd = f"allure generate {results_dir} -o {report_dir} --clean"
    log.info(f"正在生成 Allure 离线报告：{cmd}")
    try:
        subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        log.info(f"Allure 报告已生成：{os.path.abspath(report_dir)}")
        if os.getenv("OPEN_ALLURE_REPORT", "false").lower() == "true":
            log.info("正在打开 Allure 报告")
            subprocess.Popen(f"allure open {report_dir}", shell=True)
    except subprocess.CalledProcessError as e:
        log.error(f"生成 Allure 报告失败：{e.stderr}")
    except Exception as e:
        log.error(f"生成 Allure 报告异常：{e}")
