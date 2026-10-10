# -*- coding: utf-8 -*-
"""
课程管理页面
@Desc: 对应 Admin/courseManage 下的 addCourse / courseList / queryCourse / editorCourse
"""
import time

from selenium.webdriver.common.by import By

from base.page_base import BasePage
from config import BASE_URL


class PageCourseManage(BasePage):
    """课程管理页面类：添加 / 查询 / 编辑 / 删除课程"""

    def __init__(self, driver):
        super().__init__(driver)
        # 添加、编辑课程表单（添加页 label 为"课程名"，编辑页为"课程名称"）
        self.cname_input = (By.XPATH, "//label[contains(text(),'课程名')]/following::input[1]")
        self.ccredit_input = (By.XPATH, "//label[contains(text(),'学分')]/following::input[1]")
        self.submit_button = (By.XPATH, "//button[.//span[normalize-space()='提交']]")
        # 课程列表查询表单（输入即触发查询）
        self.query_cname = (By.XPATH, "//label[normalize-space()='课程名']/following::input[1]")
        self.query_low_bound = (By.XPATH, "//label[normalize-space()='学分下限']/following::input[1]")
        self.query_high_bound = (By.XPATH, "//label[normalize-space()='学分上限']/following::input[1]")

    # ------------------------------------------------------------------ 页面跳转
    def open_add(self):
        """打开添加课程页面"""
        self.driver.get(BASE_URL + "/addCourse")

    def open_list(self):
        """打开课程列表页面"""
        self.driver.get(BASE_URL + "/queryCourse")

    def open_editor(self, cid):
        """打开编辑课程页面"""
        self.driver.get(BASE_URL + f"/editorCourse?cid={cid}")

    # ------------------------------------------------------------------ 业务操作
    def add_course(self, cname, ccredit):
        """添加课程：填写表单并提交，返回提示信息"""
        self.base_input(self.cname_input, cname)
        self.base_input(self.ccredit_input, ccredit)
        self.submit_form()
        return self.get_message()

    def edit_course(self, cname, ccredit):
        """编辑课程：修改表单并提交，返回提示信息"""
        self.base_input(self.cname_input, cname)
        self.base_input(self.ccredit_input, ccredit)
        self.submit_form()
        return self.get_message()

    def submit_form(self):
        """提交表单"""
        self.base_click(self.submit_button)

    def filter_by_cname(self, cname):
        """按课程名过滤列表（列表监听表单变化自动查询）"""
        self.base_input(self.query_cname, cname)

    def filter_by_credit(self, low_bound=None, high_bound=None):
        """按学分区间过滤列表"""
        if low_bound is not None:
            self.base_input(self.query_low_bound, low_bound)
        if high_bound is not None:
            self.base_input(self.query_high_bound, high_bound)

    def wait_filtered_by_name(self, cname, timeout=10):
        """
        等待按课程名过滤的结果返回（表格中每一行都包含该课程名）
        过滤后无数据也视为查询完成，用于校验"数据已被删除"
        """
        self.wait_until(
            lambda x: all(cname in course["cname"] for course in self.get_course_list()),
            timeout,
            f"课程列表过滤结果未返回：{cname}",
        )
        return self.get_course_list()

    # ------------------------------------------------------------------ 列表数据
    def get_course_list(self):
        """读取课程列表表格数据，列顺序：课程号 / 课程名 / 学分"""
        return self.get_table_data(["cid", "cname", "ccredit"])

    def get_course_by_name(self, cname):
        """按课程名查找课程，未找到返回 None"""
        return self.find_in_data(self.get_course_list(), cname=cname)

    def wait_course_by_name(self, cname, timeout=10):
        """等待课程出现在列表中"""
        self.wait_until(
            lambda x: self.get_course_by_name(cname) is not None,
            timeout,
            f"列表中未找到课程：{cname}",
        )
        return self.get_course_by_name(cname)

    def wait_course_absent(self, cname, timeout=10, settle=1.0):
        """等待课程从列表中消失，并确认结果稳定"""
        self.wait_until(
            lambda x: self.get_course_by_name(cname) is None,
            timeout,
            f"课程 {cname} 仍然在列表中",
        )
        time.sleep(settle)
        return self.get_course_by_name(cname) is None

    def wait_credit_range(self, low_bound, high_bound=None, timeout=10):
        """等待列表查询完成，并校验学分均在查询区间内"""
        def _in_range(x):
            data = self.get_course_list()
            if not data:
                return False
            for course in data:
                credit = float(course["ccredit"])
                if credit < low_bound:
                    return False
                if high_bound is not None and credit > high_bound:
                    return False
            return True

        self.wait_until(_in_range, timeout, f"学分区间过滤失败：{low_bound} ~ {high_bound}")
        return self.get_course_list()

    def delete_course(self, cname):
        """按课程名删除课程：点击行内删除按钮并确认，返回提示信息"""
        course = self.get_course_by_name(cname)
        if course is None:
            return ""
        self.click_row_button(course["row"], "删除")
        self.confirm_pop("删除")
        return self.get_message()
