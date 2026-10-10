# -*- coding: utf-8 -*-
"""
课程管理模块测试用例
@Desc: 添加 / 查询 / 编辑 / 删除 + 表单校验 + 学分区间查询
"""
import allure
import pytest

from config import random_credit, random_course_name
from page.page_course_manage import PageCourseManage
from script import log
from tools import read_json_dict

pytestmark = pytest.mark.course

course_data = read_json_dict("course_data.json")


@allure.epic("学生选课管理系统")
@allure.feature("课程管理模块")
class TestCourseManage:
    """课程管理功能测试类"""

    def test_01_add_course_success(self, admin_page):
        """添加课程：提交成功并可在课程列表中查询到"""
        cname = random_course_name()
        ccredit = random_credit()
        page = PageCourseManage(admin_page.driver)
        with allure.step(f"填写并提交课程信息：{cname} / 学分 {ccredit}"):
            page.open_add()
            tip = page.add_course(cname, ccredit)
            log.info(f"添加课程提示：{tip}")
            assert "插入成功" in tip, f"添加课程失败，实际提示：{tip}"
        with allure.step(f"在课程列表页按课程名过滤：{cname}"):
            page.open_list()
            page.filter_by_cname(cname)
            course = page.wait_course_by_name(cname)
            log.info(f"过滤结果：{course}")
            assert course["ccredit"] == str(ccredit), f"课程学分与新增的不一致：{course}"

    @pytest.mark.parametrize("case", course_data, ids=[c["desc"] for c in course_data])
    def test_02_add_course_form_validate(self, admin_page, case):
        """添加课程表单校验（负向用例，数据驱动）"""
        page = PageCourseManage(admin_page.driver)
        with allure.step(f"用例场景：{case['desc']}"):
            page.open_add()
            page.base_input(page.cname_input, case["cname"])
            if case["ccredit"] != "":
                page.base_input(page.ccredit_input, case["ccredit"])
            page.submit_form()
            errors = page.get_form_errors()
            log.info(f"表单校验提示：{errors}")
            allure.attach(str(errors), name="表单校验提示", attachment_type=allure.attachment_type.TEXT)
            assert case["expect"] in errors, f"期望提示包含 {case['expect']}，实际提示：{errors}"
        with allure.step("校验表单未通过时不会提交"):
            assert "/addCourse" in page.driver.current_url, "表单校验未通过却提交成功了"

    def test_03_add_editor_delete_course(self, admin_page):
        """课程管理完整流程：添加 -> 查询 -> 编辑 -> 删除 -> 校验"""
        page = PageCourseManage(admin_page.driver)
        cname = random_course_name()
        new_name = random_course_name()
        ccredit = random_credit()

        with allure.step(f"新增课程：{cname} / 学分 {ccredit}"):
            page.open_add()
            assert "插入成功" in page.add_course(cname, ccredit), "新增课程失败"

        with allure.step(f"在列表中过滤并获取课程号：{cname}"):
            page.open_list()
            page.filter_by_cname(cname)
            course = page.wait_course_by_name(cname)
            cid = course["cid"]
            log.info(f"过滤结果：{course}")

        with allure.step(f"编辑课程 cid={cid}，课程名改为：{new_name}"):
            page.open_editor(cid)
            tip = page.edit_course(new_name, ccredit)
            log.info(f"编辑课程提示：{tip}")
            assert "编辑成功" in tip, f"编辑课程失败，实际提示：{tip}"

        with allure.step(f"校验编辑结果：按新课程名 {new_name} 过滤"):
            page.open_list()
            page.filter_by_cname(new_name)
            course = page.wait_course_by_name(new_name)
            assert course["cid"] == cid, f"编辑后课程号发生变化：{course}"

        with allure.step(f"删除课程：{new_name}"):
            tip = page.delete_course(new_name)
            log.info(f"删除课程提示：{tip}（删除后列表页会自动刷新，以列表结果为准）")

        with allure.step(f"校验删除结果：按课程名 {new_name} 过滤应无数据"):
            page.open_list()
            page.filter_by_cname(new_name)
            page.wait_filtered_by_name(new_name)
            assert page.get_course_by_name(new_name) is None, f"课程 {new_name} 未被删除"

    def test_04_query_course_by_credit(self, admin_page):
        """按学分区间查询：学分下限为 5，返回结果的学分均应不小于 5"""
        page = PageCourseManage(admin_page.driver)
        with allure.step("按学分下限 5 过滤课程列表"):
            page.open_list()
            page.filter_by_credit(low_bound=5)
            data = page.wait_credit_range(5)
            log.info(f"过滤结果：{data}")
            allure.attach(str(data), name="过滤结果", attachment_type=allure.attachment_type.TEXT)
        with allure.step("校验返回结果的学分均在查询区间内"):
            assert len(data) >= 1, "学分下限为 5 时结果为空（初始数据中存在学分不小于 5 的课程）"
            for course in data:
                assert float(course["ccredit"]) >= 5, f"课程学分不在查询区间：{course}"
