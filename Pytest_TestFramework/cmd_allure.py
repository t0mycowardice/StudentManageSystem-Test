# -*- coding: utf-8 -*-
"""
Allure 报告生成脚本
@Desc: 手动生成离线报告：python cmd_allure.py
"""
import os

run_cmd = "allure generate ./report -o ./new_report --clean"
os.system(run_cmd)
