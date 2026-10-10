# -*- coding: utf-8 -*-
"""
教师管理页面
@Desc: 对应 Admin/teacherManage 下的 addTeacher / queryTeacher / editorTeacher
"""
import time

from selenium.webdriver.common.by import By

from base.page_base import BasePage
from config import BASE_URL


class PageTeacherManage(BasePage):
    """教师管理页面类：添加 / 查询 / 删除教师"""

    def __init__(self, driver):
        super().__init__(driver)
        # 添加教师表单
        self.tname_input = (By.XPATH, "//label[contains(text(),'教师姓名')]/following::input[1]")
        self.password_input = (By.XPATH, "//label[contains(text(),'初始密码')]/following::input[1]")
        self.submit_button = (By.XPATH, "//button[.//span[normalize-space()='提交']]")
        # 教师列表查询表单（输入即触发查询）
        self.query_tid = (By.XPATH, "//label[normalize-space()='工号']/following::input[1]")
        self.query_tname = (By.XPATH, "//label[normalize-space()='教师姓名']/following::input[1]")

    # ------------------------------------------------------------------ 页面跳转
    def open_add(self):
        """打开添加教师页面"""
        self.driver.get(BASE_URL + "/addTeacher")

    def open_list(self):
        """打开教师列表页面"""
        self.driver.get(BASE_URL + "/queryTeacher")

    def open_editor(self, tid):
        """打开编辑教师页面"""
        self.driver.get(BASE_URL + f"/editorTeacher?tid={tid}")

    # ------------------------------------------------------------------ 业务操作
    def add_teacher(self, tname, password):
        """添加教师：填写表单并提交，返回提示信息"""
        self.base_input(self.tname_input, tname)
        self.base_input(self.password_input, password)
        self.submit_form()
        return self.get_message()

    def submit_form(self):
        """提交表单"""
        self.base_click(self.submit_button)

    def edit_teacher(self, tname, password):
        """编辑教师：修改表单并提交，返回提示信息"""
        self.base_input(self.tname_input, tname)
        self.base_input(self.password_input, password)
        self.submit_form()
        return self.get_message()

    def filter_by_tname(self, tname):
        """按教师姓名过滤列表（列表监听表单变化自动查询）"""
        self.base_input(self.query_tname, tname)

    def filter_by_tid(self, tid):
        """按工号过滤列表"""
        self.base_input(self.query_tid, tid)

    def wait_filtered_by_name(self, tname, timeout=10):
        """
        等待按姓名过滤的结果返回（表格中每一行都包含该姓名）
        过滤后无数据也视为查询完成，用于校验"数据已被删除"
        """
        self.wait_until(
            lambda x: all(tname in teacher["tname"] for teacher in self.get_teacher_list()),
            timeout,
            f"教师列表过滤结果未返回：{tname}",
        )
        return self.get_teacher_list()

    # ------------------------------------------------------------------ 列表数据
    def get_teacher_list(self):
        """读取教师列表表格数据，列顺序：工号 / 姓名 / 密码"""
        return self.get_table_data(["tid", "tname", "password"])

    def get_teacher_by_name(self, tname):
        """按姓名查找教师，未找到返回 None"""
        return self.find_in_data(self.get_teacher_list(), tname=tname)

    def wait_teacher_by_name(self, tname, timeout=10):
        """等待教师出现在列表中"""
        self.wait_until(
            lambda x: self.get_teacher_by_name(tname) is not None,
            timeout,
            f"列表中未找到教师：{tname}",
        )
        return self.get_teacher_by_name(tname)

    def wait_teacher_absent(self, tname, timeout=10, settle=1.0):
        """等待教师从列表中消失，并确认结果稳定"""
        self.wait_until(
            lambda x: self.get_teacher_by_name(tname) is None,
            timeout,
            f"教师 {tname} 仍然在列表中",
        )
        time.sleep(settle)
        return self.get_teacher_by_name(tname) is None

    def delete_teacher(self, tname):
        """按姓名删除教师：点击行内删除按钮并确认，返回提示信息"""
        teacher = self.get_teacher_by_name(tname)
        if teacher is None:
            return ""
        self.click_row_button(teacher["row"], "删除")
        self.confirm_pop("删除")
        return self.get_message()
