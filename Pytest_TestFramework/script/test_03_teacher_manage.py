# -*- coding: utf-8 -*-
"""
教师管理模块测试用例
@Desc: 添加 / 查询 / 编辑 / 删除 + 表单校验 + 业务规则（admin 不可添加）
"""
import allure
import pytest

from config import random_name, random_password
from page.page_teacher_manage import PageTeacherManage
from script import log
from tools import read_json_dict

pytestmark = pytest.mark.teacher

teacher_data = read_json_dict("teacher_data.json")


@allure.epic("学生选课管理系统")
@allure.feature("教师管理模块")
class TestTeacherManage:
    """教师管理功能测试类"""

    def test_01_add_teacher_success(self, admin_page):
        """添加教师：提交成功并可在教师列表中查询到"""
        tname = random_name()
        password = random_password()
        page = PageTeacherManage(admin_page.driver)
        with allure.step(f"填写并提交教师信息：{tname} / {password}"):
            page.open_add()
            tip = page.add_teacher(tname, password)
            log.info(f"添加教师提示：{tip}")
            assert "插入成功" in tip, f"添加教师失败，实际提示：{tip}"
        with allure.step(f"在教师列表页按姓名过滤：{tname}"):
            page.open_list()
            page.filter_by_tname(tname)
            teacher = page.wait_teacher_by_name(tname)
            log.info(f"过滤结果：{teacher}")
            assert teacher["password"] == password, "教师密码与新增的不一致"

    @pytest.mark.parametrize("case", teacher_data, ids=[c["desc"] for c in teacher_data])
    def test_02_add_teacher_form_validate(self, admin_page, case):
        """添加教师表单校验（负向用例，数据驱动）"""
        page = PageTeacherManage(admin_page.driver)
        with allure.step(f"用例场景：{case['desc']}"):
            page.open_add()
            page.base_input(page.tname_input, case["tname"])
            page.base_input(page.password_input, case["password"])
            page.submit_form()
            errors = page.get_form_errors()
            log.info(f"表单校验提示：{errors}")
            allure.attach(str(errors), name="表单校验提示", attachment_type=allure.attachment_type.TEXT)
            assert case["expect"] in errors, f"期望提示包含 {case['expect']}，实际提示：{errors}"
        with allure.step("校验表单未通过时不会提交"):
            assert "/addTeacher" in page.driver.current_url, "表单校验未通过却提交成功了"

    def test_03_add_teacher_admin_forbidden(self, admin_page):
        """业务规则：教师姓名不能为 admin"""
        page = PageTeacherManage(admin_page.driver)
        with allure.step("使用 admin 作为教师姓名提交"):
            page.open_add()
            tip = page.add_teacher("admin", random_password())
            log.info(f"提交提示：{tip}")
            assert "admin 不可添加" in tip, f"未拦截 admin 教师，实际提示：{tip}"
        with allure.step("校验未提交并停留在添加页面"):
            assert "/addTeacher" in page.driver.current_url, "admin 教师被提交成功"

    def test_04_editor_delete_teacher(self, admin_page):
        """教师编辑与删除（只操作自动化新增的数据，不影响初始数据）"""
        page = PageTeacherManage(admin_page.driver)
        tname = random_name()
        new_name = random_name()
        password = random_password()
        with allure.step(f"新增教师：{tname} / {password}"):
            page.open_add()
            assert "插入成功" in page.add_teacher(tname, password), "新增教师失败"
        with allure.step(f"在列表中过滤并获取工号：{tname}"):
            page.open_list()
            page.filter_by_tname(tname)
            teacher = page.wait_teacher_by_name(tname)
            tid = teacher["tid"]
        with allure.step(f"编辑教师 tid={tid}，姓名改为：{new_name}"):
            page.open_editor(tid)
            tip = page.edit_teacher(new_name, password)
            log.info(f"编辑教师提示：{tip}")
            assert "编辑成功" in tip, f"编辑教师失败，实际提示：{tip}"
        with allure.step(f"校验编辑结果：按新姓名 {new_name} 过滤"):
            page.open_list()
            page.filter_by_tname(new_name)
            teacher = page.wait_teacher_by_name(new_name)
            assert teacher["tid"] == tid, f"编辑后工号发生变化：{teacher}"
        with allure.step(f"删除教师：{new_name}"):
            tip = page.delete_teacher(new_name)
            log.info(f"删除教师提示：{tip}（删除后列表页会自动刷新，以列表结果为准）")
        with allure.step(f"校验删除结果：按姓名 {new_name} 过滤应无数据"):
            page.open_list()
            page.filter_by_tname(new_name)
            page.wait_filtered_by_name(new_name)
            assert page.get_teacher_by_name(new_name) is None, f"教师 {new_name} 未被删除"

    def test_05_query_existing_teacher(self, admin_page):
        """查询初始数据中的教师：按姓名查询、按工号查询"""
        page = PageTeacherManage(admin_page.driver)
        with allure.step("按姓名过滤：李玉民"):
            page.open_list()
            page.filter_by_tname("李玉民")
            teacher = page.wait_teacher_by_name("李玉民")
            log.info(f"过滤结果：{teacher}")
            assert teacher["tid"] == "4", f"查询结果异常：{teacher}"
        with allure.step("按工号过滤：6"):
            page.open_list()
            page.filter_by_tid(6)
            page.wait_until(
                lambda x: page.get_teacher_by_name("admin") is not None,
                timeout=10,
                message="按工号 6 未查询到 admin",
            )
            assert page.get_teacher_by_name("admin")["tid"] == "6"
