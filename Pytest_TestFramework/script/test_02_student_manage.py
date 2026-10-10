# -*- coding: utf-8 -*-
"""
学生管理模块测试用例
@Desc: 左侧菜单导航 + 添加 / 查询 / 编辑 / 删除 + 表单校验（管理员角色）
"""
import allure
import pytest

from config import random_name, random_password
from page.page_student_manage import PageStudentManage
from script import log
from tools import read_json_dict

pytestmark = pytest.mark.student

student_data = read_json_dict("student_data.json")


@allure.epic("学生选课管理系统")
@allure.feature("学生管理模块")
class TestStudentManage:
    """学生管理功能测试类"""

    def test_01_menu_navigation(self, admin_page):
        """后台左侧菜单：菜单渲染与菜单跳转"""
        with allure.step("校验左侧菜单渲染"):
            menus = admin_page.get_menu_sub_titles()
            log.info(f"左侧菜单：{menus}")
            for name in ["学生管理", "教师管理", "课程管理", "开课表管理"]:
                assert name in menus, f"左侧菜单缺少：{name}，实际：{menus}"
        with allure.step("点击 学生管理 - 添加学生"):
            admin_page.click_menu("学生管理", "添加学生")
            admin_page.wait_url_contains("/addStudent")
            assert admin_page.is_element_exist(
                PageStudentManage(admin_page.driver).sname_input
            ), "未打开添加学生页面"

    def test_02_add_student_success(self, admin_page):
        """添加学生：输入姓名与初始密码，提交成功并跳转学生列表"""
        sname = random_name()
        password = random_password()
        page = PageStudentManage(admin_page.driver)
        with allure.step(f"填写并提交学生信息：{sname} / {password}"):
            page.open_add()
            tip = page.add_student(sname, password)
            log.info(f"添加学生提示：{tip}")
            assert "插入成功" in tip, f"添加学生失败，实际提示：{tip}"
        with allure.step("校验提交后自动跳转学生列表页面"):
            page.wait_url_contains("/studentList")

    @pytest.mark.parametrize("case", student_data, ids=[c["desc"] for c in student_data])
    def test_03_add_student_form_validate(self, admin_page, case):
        """添加学生表单校验（负向用例，数据驱动）"""
        page = PageStudentManage(admin_page.driver)
        with allure.step(f"用例场景：{case['desc']}"):
            page.open_add()
            page.base_input(page.sname_input, case["sname"])
            page.base_input(page.password_input, case["password"])
            page.submit_form()
            errors = page.get_form_errors()
            log.info(f"表单校验提示：{errors}")
            allure.attach(str(errors), name="表单校验提示", attachment_type=allure.attachment_type.TEXT)
            assert case["expect"] in errors, f"期望提示包含 {case['expect']}，实际提示：{errors}"
        with allure.step("校验表单未通过时不会提交"):
            assert "/addStudent" in page.driver.current_url, "表单校验未通过却提交成功了"

    def test_04_add_query_editor_delete_student(self, admin_page):
        """学生管理完整流程：添加 -> 查询 -> 编辑 -> 删除 -> 校验"""
        page = PageStudentManage(admin_page.driver)
        sname = random_name()
        new_name = random_name()
        password = random_password()

        with allure.step(f"新增学生：{sname} / {password}"):
            page.open_add()
            tip = page.add_student(sname, password)
            assert "插入成功" in tip, f"新增学生失败，实际提示：{tip}"

        with allure.step(f"按姓名查询新增的学生：{sname}"):
            page.open_query()
            page.query_student(sname=sname)
            student = page.wait_student_by_name(sname)
            log.info(f"查询结果：{student}")
            assert student["password"] == password, "查询到的学生密码与新增的不一致"
            sid = student["sid"]

        with allure.step(f"编辑学生 sid={sid}，姓名改为：{new_name}"):
            page.open_editor(sid)
            tip = page.edit_student(new_name, password)
            log.info(f"编辑学生提示：{tip}")
            assert "编辑成功" in tip, f"编辑学生失败，实际提示：{tip}"

        with allure.step(f"校验编辑结果：按新姓名 {new_name} 查询"):
            page.open_query()
            page.query_student(sname=new_name)
            student = page.wait_student_by_name(new_name)
            assert student["sid"] == sid, f"编辑后学号发生变化：{student}"

        with allure.step(f"删除学生：{new_name}"):
            tip = page.delete_student(new_name)
            log.info(f"删除学生提示：{tip}")
            assert "删除成功" in tip, f"删除学生失败，实际提示：{tip}"

        with allure.step(f"校验删除结果：再次查询 {new_name} 应无数据"):
            page.open_query()
            page.query_student(sname=new_name)
            assert page.wait_student_absent(new_name), f"学生 {new_name} 未被删除"

    def test_05_query_existing_student(self, admin_page):
        """查询初始数据中的学生：按姓名模糊查询、按学号精确查询"""
        page = PageStudentManage(admin_page.driver)
        with allure.step("按姓名模糊查询：阮"):
            page.open_query()
            page.query_student(sname="阮")
            student = page.wait_student_by_name("阮健乘")
            log.info(f"查询结果：{student}")
            assert student["sid"] == "1", f"查询结果异常：{student}"
        with allure.step("按学号精确查询：1"):
            page.open_query()
            page.query_student(sid=1)
            student = page.wait_student_by_name("阮健乘")
            assert student["sid"] == "1", f"查询结果异常：{student}"
