import time
from selenium.webdriver.common.by import By
from base.page_base import BasePage
from config import BASE_URL

class PageLogin(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        # 定位元素（利用页面文本辅助定位）
        self.user_id = (By.XPATH, "//label[contains(text(),'用户 id')]/following::input[1]")
        self.password = (By.XPATH, "//label[contains(text(),'用户密码')]/following::input[1]")
        # 由于单选框有"老师"、"学生"、"admin"，我们统一默认选"admin"
        self.radio_admin = (By.XPATH, "//span[contains(text(),'admin')]")
        # 登录按钮
        self.login_btn = (By.XPATH, "//span[contains(text(),'登陆')]")
        # 登录成功后的提示信息（欢迎 xxx）
        self.success_msg = (By.XPATH, "//p[contains(text(),'登陆成功')]")

    def open_url(self):
        """打开学生管理系统首页"""
        self.driver.get(BASE_URL)

    def login(self, user_id, password):
        """执行登录操作"""
        # 输入用户ID
        self.base_input(self.user_id, user_id)
        # 输入密码
        self.base_input(self.password, password)
        # 选择用户类型（默认选admin，如果你想选老师可以改这里）
        self.base_click(self.radio_admin)
        # 点击登录
        self.base_click(self.login_btn)
        time.sleep(2)  # 等待页面响应

    def get_success_result(self):
        """获取登录成功后的提示"""
        try:
            return self.fd_element(self.success_msg).text
        except Exception:
            return "获取成功提示失败"