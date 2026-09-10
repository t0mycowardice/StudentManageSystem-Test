import os
from tools import GetLog
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import PATH

class BasePage(object):
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.default_timeout = timeout

    def fd_element(self, loc):
        try:
            element = WebDriverWait(self.driver, self.default_timeout).until(EC.presence_of_element_located(loc))
            return element
        except Exception as e:
            GetLog.get_log().error(f"元素定位超时，定位信息：{loc}，错误详情：{e}")
            raise

    def base_input(self, loc, text):
        ele = self.fd_element(loc)
        ele.clear()
        ele.send_keys(text)

    def base_click(self, loc):
        self.fd_element(loc).click()

    def get_shot(self, file_name):
        file_path = os.path.join(PATH, "img", file_name)
        self.driver.get_screenshot_as_file(file_path)