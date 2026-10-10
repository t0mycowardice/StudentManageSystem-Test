# -*- coding: utf-8 -*-
"""
管理员首页 / 后台公共导航
@Desc: 对应 student_client/src/views/Admin/home.vue 与 components/r-aside.vue
"""
from selenium.webdriver.common.by import By

from base.page_base import BasePage
from config import BASE_URL


class PageAdminHome(BasePage):
    """管理员首页类（后台左侧菜单、顶部信息、退出登录）"""

    def __init__(self, driver):
        super().__init__(driver)
        # 首页标识
        self.home_title = (By.XPATH, "//h1[normalize-space()='admin home']")
        # 顶部登录人姓名（r-header 组件）
        self.header_name = (By.XPATH, "//i[contains(@class,'el-icon-user')]/following-sibling::span[1]")
        # 左侧菜单：一级菜单标题 / 二级菜单项
        self.menu_sub_titles = (By.XPATH, "//aside//div[contains(@class,'el-submenu__title')]")
        self.menu_sub_title = (
            By.XPATH,
            "//aside//div[contains(@class,'el-submenu__title')][contains(normalize-space(.), '%s')]",
        )
        self.menu_item = (
            By.XPATH,
            "//aside//li[contains(@class,'el-menu-item')][contains(normalize-space(.), '%s')]",
        )
        # 退出登录按钮（首页 logout 按钮）
        self.logout_button = (By.XPATH, "//button[.//span[normalize-space()='logout']]")

    def open_url(self):
        """打开管理员首页"""
        self.driver.get(BASE_URL + "/adminHome")

    def goto(self, path):
        """通过地址栏跳转到后台指定路由，如 goto('/studentList')"""
        self.driver.get(BASE_URL + path)
        return self

    def is_admin_home(self):
        """是否进入管理员首页"""
        return self.is_element_exist(self.home_title, timeout=5)

    def get_login_name(self):
        """获取顶部显示的用户名"""
        return self.base_text(self.header_name)

    def get_menu_sub_titles(self):
        """获取左侧一级菜单标题（包含未展开的菜单）"""
        return self.base_texts_content(self.menu_sub_titles)

    def click_menu(self, sub_title, item_name):
        """
        点击左侧菜单：先展开一级菜单，再点击二级菜单
        :param sub_title: 一级菜单名，如 学生管理
        :param item_name: 二级菜单名，如 添加学生
        """
        self.base_click((self.menu_sub_title[0], self.menu_sub_title[1] % sub_title))
        self.base_click((self.menu_item[0], self.menu_item[1] % item_name))

    def logout(self):
        """退出登录"""
        self.base_click(self.logout_button)
        self.confirm_pop("好的")
