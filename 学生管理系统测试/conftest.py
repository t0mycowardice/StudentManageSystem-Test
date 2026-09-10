import pytest
from page.page_login import PageLogin
from tools import DriverTools, read_json, GetLog

log = GetLog.get_log()


class TestLogin:

    def setup_method(self):
        # 前置操作：启动驱动、初始化页面
        driver = DriverTools.get_driver()
        self.page_login = PageLogin(driver)
        self.page_login.open_url()

    def teardown_method(self):
        # 后置操作：退出驱动
        DriverTools.quit_driver()

    @pytest.mark.parametrize("user_id,password,expect", read_json("login_data.json"))
    def test_01_login(self, user_id, password, expect):
        """数据驱动登录测试"""
        # 1. 执行登录
        self.page_login.login(user_id, password)

        # 2. 获取实际结果
        if "成功" in expect:
            # 为了防止找不到欢迎文本报错，多用一个判断
            try:
                result = self.page_login.get_success_result()
                log.info(f"登录成功提示：{result}")
                assert expect in result
            except Exception as e:
                log.error(f"获取成功提示失败: {e}")
                assert False
        else:
            # 登录失败时，页面上可能不弹出成功提示，直接断言页面未跳转
            log.info("登录失败场景验证完成")
            # 断言：URL没变
            assert "login" in self.page_login.driver.current_url or self.page_login.driver.current_url == "http://localhost:8081/"