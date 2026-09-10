# StudentManageSystem-Test
# 学生选课管理系统测试项目

## 📖 项目简介
本项目是一个前后端分离的选课管理系统。我独立完成了测试环境搭建，并进行了功能测试、接口测试、性能测试、UI自动化测试及基础安全测试。

## 🛠️ 技术栈与工具
- 测试管理：Xmind (测试点梳理), Excel (测试用例设计)
- 接口测试：Postman (断言, 集合导出)
- 性能测试：JMeter (20并发登录压测)
- UI自动化：Python + Selenium + Pytest (PO设计模式, JSON数据驱动)
- 数据库校验：DataGrip + MySQL
- 抓包工具：Chrome F12

## 📂 目录结构
- `学生管理系统.xmind`: 业务流与单模块测试点脑图
- `学生管理系统接口测试.postman_collection.json`: Postman 接口集合
- `登录接口测试.jmx`: JMeter 性能测试脚本
- `学生管理系统测试/`: Pytest 自动化测试代码（包含 base 层、page 层、data 数据）
- `imgs/`: 测试报告相关截图（含致命漏洞截图）
- `测试报告.md` 

## 🔍 核心发现与测试亮点
1. **致命越权漏洞**：通过 F12 修改本地 sessionStorage 的 type 字段，学生可直接越权至管理员后台。
2. **接口未授权访问**：通过 Postman 无 Token 直接请求 `GET /teacher/findById/6`，直接泄露管理员明文密码。
3. **系统遗留Bug**：前端残留测试用 `Test` 按钮，点击后控制台会打印表单信息，存在安全隐患。
