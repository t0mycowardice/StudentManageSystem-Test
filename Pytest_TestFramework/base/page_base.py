# -*- coding: utf-8 -*-
"""
页面基类
@Desc: 封装元素定位、常用操作以及 Element-UI 公共组件（提示框 / 表单校验 / 表格 / 气泡确认）
"""
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from config import IMG_PATH
from tools import GetLog


class BasePage(object):
    """所有页面类的父类"""

    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.default_timeout = timeout
        self.log = GetLog.get_log()

        # Element-UI 公共组件定位信息
        # el-message 的文本节点是 <p class="el-message__content">，取最后一条提示
        self.message = (By.XPATH, "(//*[contains(@class,'el-message__content')])[last()]")
        self.form_error = (By.CSS_SELECTOR, ".el-form-item__error")
        self.pop_confirm = (
            By.XPATH,
            "//div[contains(@class,'el-popconfirm__action')]//button[.//span[normalize-space()='%s']]",
        )
        self.table_rows = (By.XPATH, "//table//tr[contains(@class,'el-table__row')]")
        self.table_cell = (By.CSS_SELECTOR, "td .cell")

    # ------------------------------------------------------------------ 元素定位
    def fd_element(self, loc, timeout=None):
        """定位单个元素（元素存在即可），loc 为定位信息，如 (By.ID, "username")"""
        timeout = timeout or self.default_timeout
        try:
            element = WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(loc))
            return element
        except Exception as e:
            self.log.error(f"元素定位超时，定位信息：{loc}，错误详情：{e}")
            raise

    def fd_visible(self, loc, timeout=None):
        """定位可见元素（等待元素可见，避免元素被遮挡无法操作）"""
        timeout = timeout or self.default_timeout
        try:
            element = WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(loc))
            return element
        except Exception as e:
            self.log.error(f"元素可见等待超时，定位信息：{loc}，错误详情：{e}")
            raise

    def fd_elements(self, loc, timeout=None):
        """定位一组元素，未找到时返回空列表"""
        timeout = timeout or self.default_timeout
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(loc))
        except Exception:
            self.log.warning(f"未定位到元素：{loc}")
            return []
        return self.driver.find_elements(*loc)

    def is_element_exist(self, loc, timeout=3):
        """判断元素是否存在"""
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(loc))
            return True
        except Exception:
            return False

    def wait_until(self, condition, timeout=None, message=""):
        """等待自定义条件成立（condition 为 lambda，参数是 driver）"""
        timeout = timeout or self.default_timeout
        try:
            return WebDriverWait(self.driver, timeout, poll_frequency=0.5).until(condition)
        except Exception as e:
            self.log.error(f"等待条件超时：{message or condition}，错误详情：{e}")
            raise

    # ------------------------------------------------------------------ 常用操作
    def base_input(self, loc, text):
        """输入：先清空再输入"""
        ele = self.fd_visible(loc)
        ele.clear()
        ele.send_keys(str(text))

    def base_click(self, loc):
        """点击元素"""
        self.fd_element(loc).click()

    def base_click_visible(self, loc):
        """点击元素（等待元素可见后再点击）"""
        self.fd_visible(loc).click()

    def base_text(self, loc):
        """获取元素文本"""
        return self.fd_element(loc).text

    def base_texts(self, loc):
        """获取一组元素的文本"""
        return [ele.text for ele in self.fd_elements(loc)]

    def base_texts_content(self, loc):
        """获取一组元素的文本（包含隐藏元素，用于菜单展开 / 收起等场景）"""
        return [ele.get_attribute("textContent").strip() for ele in self.driver.find_elements(*loc)]

    def base_scroll(self, loc):
        """滚动到元素位置并返回元素"""
        ele = self.fd_element(loc)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", ele)
        return ele

    def wait_url_contains(self, part, timeout=None):
        """等待地址栏包含指定内容"""
        timeout = timeout or self.default_timeout
        return self.wait_until(lambda x: part in x.current_url, timeout, f"地址栏未包含：{part}")

    def get_shot(self, file_name):
        """截图保存到 imgs 目录"""
        if not os.path.exists(IMG_PATH):
            os.makedirs(IMG_PATH)
        file_path = os.path.join(IMG_PATH, file_name)
        self.driver.get_screenshot_as_file(file_path)
        return file_path

    # ------------------------------------------------------------------ 窗口 / 表单切换
    def base_switch_handle(self, loc):
        """切换到新窗口并返回页面元素"""
        WebDriverWait(self.driver, self.default_timeout).until(lambda x: len(x.window_handles) > 1)
        handles = self.driver.window_handles
        self.driver.switch_to.window(handles[-1])
        return self.fd_element(loc)

    def base_default_handle(self, close=True):
        """关闭当前窗口并回到原窗口"""
        handles = self.driver.window_handles
        if len(handles) > 1:
            if close:
                self.driver.close()
            self.driver.switch_to.window(handles[0])

    def base_switch_frame(self, loc):
        """切换表单"""
        self.driver.switch_to.frame(self.fd_element(loc))

    def base_default_frame(self):
        """回到最外层表单"""
        self.driver.switch_to.default_content()

    # ------------------------------------------------------------------ sessionStorage
    def set_session(self, key, value):
        """写入 sessionStorage（本系统使用 sessionStorage 保存登录态）"""
        self.driver.execute_script(f"window.sessionStorage.setItem('{key}', '{value}')")

    def get_session(self, key):
        """读取 sessionStorage"""
        return self.driver.execute_script(f"return window.sessionStorage.getItem('{key}')")

    # ------------------------------------------------------------------ Element-UI 公共组件
    def get_message(self, timeout=5):
        """获取顶部提示信息（el-message）文本，取最后一条"""
        try:
            return self.fd_visible(self.message, timeout).text
        except Exception:
            self.log.warning("未捕获到 el-message 提示信息")
            return ""

    def get_form_errors(self, timeout=5):
        """获取表单校验错误提示（el-form-item__error）"""
        try:
            self.fd_visible(self.form_error, timeout)
        except Exception:
            self.log.warning("未捕获到表单校验错误提示")
            return []
        return self.base_texts(self.form_error)

    def confirm_pop(self, text="删除"):
        """点击气泡确认框（el-popconfirm）中的确认按钮"""
        self.base_click((self.pop_confirm[0], self.pop_confirm[1] % text))

    def cancel_pop(self, text="取消"):
        """点击气泡确认框（el-popconfirm）中的取消按钮"""
        self.base_click((self.pop_confirm[0], self.pop_confirm[1] % text))

    # ------------------------------------------------------------------ el-table 表格
    def find_rows(self):
        """获取表格当前所有数据行（不等待，用于判断渲染结果）"""
        return self.driver.find_elements(*self.table_rows)

    def get_table_data(self, keys):
        """
        读取表格当前页数据
        :param keys: 列名列表，如 ["sid", "sname", "password"]
        """
        data = []
        for row in self.find_rows():
            cells = row.find_elements(*self.table_cell)
            if len(cells) < len(keys):
                continue
            item = {key: cells[index].text for index, key in enumerate(keys)}
            item["row"] = row
            data.append(item)
        return data

    @staticmethod
    def find_in_data(data, **kwargs):
        """在表格数据中按字段查找一行，如 find_in_data(data, sid="3")"""
        for item in data:
            if all(item.get(key) == str(value) for key, value in kwargs.items()):
                return item
        return None

    def click_row_button(self, row, text):
        """点击表格行内的按钮（如 删除 / 编辑）"""
        row.find_element(By.XPATH, f".//button[.//span[normalize-space()='{text}']]").click()
