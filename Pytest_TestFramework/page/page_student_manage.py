# -*- coding: utf-8 -*-
"""
学生管理页面
@Desc: 对应 Admin/studentManage 下的 addStudent / studentList / queryStudent / editorStudent
"""
import time

from selenium.webdriver.common.by import By

from base.page_base import BasePage
from config import BASE_URL


class PageStudentManage(BasePage):
    """学生管理页面类：添加 / 查询 / 编辑 / 删除学生"""

    def __init__(self, driver):
        super().__init__(driver)
        # 添加、编辑学生表单
        self.sname_input = (By.XPATH, "//label[contains(text(),'学生姓名')]/following::input[1]")
        self.password_input = (By.XPATH, "//label[contains(text(),'初始密码')]/following::input[1]")
        self.submit_button = (By.XPATH, "//button[.//span[normalize-space()='提交']]")
        # 查询学生表单
        self.query_sid = (By.XPATH, "//label[normalize-space()='学号']/following::input[1]")
        self.query_sname = (By.XPATH, "//label[normalize-space()='学生姓名']/following::input[1]")
        self.query_button = (By.XPATH, "//button[.//span[normalize-space()='查询']]")

    # ------------------------------------------------------------------ 页面跳转
    def open_add(self):
        """打开添加学生页面"""
        self.driver.get(BASE_URL + "/addStudent")

    def open_list(self):
        """打开学生列表页面"""
        self.driver.get(BASE_URL + "/studentList")

    def open_query(self):
        """打开查询学生页面"""
        self.driver.get(BASE_URL + "/queryStudent")

    def open_editor(self, sid):
        """打开编辑学生页面"""
        self.driver.get(BASE_URL + f"/editorStudent?sid={sid}")

    # ------------------------------------------------------------------ 业务操作
    def add_student(self, sname, password):
        """添加学生：填写表单并提交，返回提示信息"""
        self.base_input(self.sname_input, sname)
        self.base_input(self.password_input, password)
        self.submit_form()
        return self.get_message()

    def edit_student(self, sname, password):
        """编辑学生：修改表单并提交，返回提示信息"""
        self.base_input(self.sname_input, sname)
        self.base_input(self.password_input, password)
        self.submit_form()
        return self.get_message()

    def submit_form(self):
        """提交表单"""
        self.base_click(self.submit_button)

    def query_student(self, sid=None, sname=None, fuzzy=True):
        """
        按条件查询学生（查询结果展示在 /queryStudent/studentList 子路由中）
        :param sid: 学号，不传表示不限制
        :param sname: 学生姓名，不传表示不限制
        :param fuzzy: 是否模糊查询
        """
        if sid is not None:
            self.base_input(self.query_sid, sid)
        if sname is not None:
            self.base_input(self.query_sname, sname)
        self.base_click(self.query_button)
        self.wait_url_contains("studentList")

    # ------------------------------------------------------------------ 列表数据
    def get_student_list(self):
        """读取学生列表表格数据，列顺序：学号 / 姓名 / 密码"""
        return self.get_table_data(["sid", "sname", "password"])

    def get_student_by_name(self, sname):
        """按姓名查找学生，未找到返回 None"""
        return self.find_in_data(self.get_student_list(), sname=sname)

    def wait_student_by_name(self, sname, timeout=10):
        """等待学生出现在列表中（查询结果异步渲染）"""
        self.wait_until(
            lambda x: self.get_student_by_name(sname) is not None,
            timeout,
            f"列表中未找到学生：{sname}",
        )
        return self.get_student_by_name(sname)

    def wait_student_absent(self, sname, timeout=10, settle=1.0):
        """
        等待学生从列表中消失，并确认结果稳定（避免查询请求未返回造成误判）
        用于校验删除操作是否生效
        """
        self.wait_until(
            lambda x: self.get_student_by_name(sname) is None,
            timeout,
            f"学生 {sname} 仍然在列表中",
        )
        time.sleep(settle)
        return self.get_student_by_name(sname) is None

    def delete_student(self, sname):
        """按姓名删除学生：点击行内删除按钮并确认，返回提示信息"""
        student = self.get_student_by_name(sname)
        if student is None:
            return ""
        self.click_row_button(student["row"], "删除")
        self.confirm_pop("删除")
        return self.get_message()
