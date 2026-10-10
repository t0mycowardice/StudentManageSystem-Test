# 学生选课管理系统 - Pytest UI 自动化测试框架

基于 Python + Selenium + Pytest + Allure 的 UI 自动化测试框架，采用 **PO（Page Object）设计模式 + JSON 数据驱动**，
被测系统为 [StudentManageSystem](https://github.com/)（Vue 前端 + Spring Boot 后端 + MySQL）。

## 一、目录结构

```
Pytest_TestFramework
├── base
│   └── page_base.py            # 页面基类：元素定位、常用操作、Element-UI 公共组件（提示/校验/表格/气泡确认）
├── page                        # PO 页面层
│   ├── driver_start.py         # 浏览器启动参数（chromedriver 路径、无头模式）
│   ├── page_login.py           # 登录页
│   ├── page_admin.py           # 管理员首页 / 后台左侧菜单导航
│   ├── page_student_manage.py  # 学生管理（添加/查询/编辑/删除）
│   ├── page_teacher_manage.py  # 教师管理（添加/查询/编辑/删除）
│   └── page_course_manage.py   # 课程管理（添加/查询/编辑/删除）
├── data                        # 测试数据（JSON 数据驱动）
│   ├── login_data.json         # 登录用例数据（正向 + 逆向）
│   ├── student_data.json       # 学生表单校验负向数据
│   ├── teacher_data.json       # 教师表单校验负向数据
│   └── course_data.json        # 课程表单校验负向数据
├── script                      # 测试脚本层
│   ├── __init__.py             # 统一初始化 log，用例中 from script import log
│   ├── test_00_smoke.py        # 环境自检（chromedriver / 前端是否可访问）
│   ├── test_01_login.py        # 登录模块
│   ├── test_02_student_manage.py  # 学生管理模块
│   ├── test_03_teacher_manage.py  # 教师管理模块
│   └── test_04_course_manage.py   # 课程管理模块
├── imgs                        # 失败截图（自动生成）
├── log                         # 运行日志（按天切分，自动生成）
├── config.py                   # 全局配置：地址、chromedriver、测试账号、随机测试数据
├── conftest.py                 # pytest 夹具 + Allure 集成
├── tools.py                    # 公共工具：浏览器驱动、JSON 读取、日志
├── pytest.ini                  # pytest 配置（testpaths / markers / allure）
└── cmd_allure.py               # 手动生成 Allure 离线报告
```

## 二、环境准备

| 依赖 | 说明 |
| --- | --- |
| Python 3.x | 建议 3.8 及以上（本机为 3.14） |
| selenium | `pip install selenium` |
| pytest / allure-pytest | `pip install pytest allure-pytest` |
| faker | `pip install faker`（生成随机测试数据） |
| chromedriver | 版本需与本地 Chrome 一致，路径在 `config.py` 的 `CHROME_DRIVER` 中配置 |
| Allure | 生成 HTML 报告需要安装 Allure 命令行工具并加入 PATH |

被测系统需要先启动（前端 `npm run serve`，后端 `java -jar student_server.jar`，数据库 MySQL），
地址可在 `config.py` 中修改，也支持环境变量覆盖：

```bash
set BASE_URL=http://localhost:8081
set HEADLESS=true
```

## 三、执行方式

```bash
cd Pytest_TestFramework

# 执行全部用例（自动生成 allure 结果到 ./report）
pytest

# 按模块执行
pytest -m login        # 登录模块
pytest -m student      # 学生管理模块
pytest -m teacher      # 教师管理模块
pytest -m course       # 课程管理模块
pytest script/test_02_student_manage.py

# 只跑冒烟（环境自检）
pytest script/test_00_smoke.py
```

执行结束后会自动调用 `allure generate ./report -o ./new_report --clean` 生成离线报告，
也可手动执行 `python cmd_allure.py`。查看报告：

```bash
allure open ./new_report
```

## 四、用例设计说明

| 模块 | 用例要点 |
| --- | --- |
| 登录 | 管理员/教师/学生登录成功、密码错误、登录类型不匹配（admin 类型 + 非 admin 账号）、空表单校验、登录态写入 sessionStorage、越权安全用例 |
| 学生管理 | 左侧菜单渲染与跳转、添加学生、姓名/密码表单校验、添加-查询-编辑-删除全流程、按姓名模糊查询、按学号精确查询 |
| 教师管理 | 添加教师、表单校验、admin 不可添加业务规则、编辑与删除全流程、按姓名/工号查询 |
| 课程管理 | 添加课程、表单校验（含学分非数字）、添加-编辑-删除全流程、按学分下限查询并校验结果区间 |

设计要点：

1. **数据驱动**：用例参数与测试数据分离，数据文件放在 `data/` 目录，`tools.read_json` / `read_json_dict` 读取。
2. **用例自清理**：增删改用例使用 `faker` 随机生成的数据，删除用例只操作自动化自己新增的数据，不破坏初始数据。
3. **异步渲染等待**：列表查询是异步渲染的，框架用 `wait_until` + 条件等待（而不是固定 sleep）判断结果，避免误判。
4. **失败可追溯**：用例失败自动截图保存到 `imgs/` 并 attach 到 Allure 报告，同时写入 `log/web.log`。
5. **失败场景用例**：`xfail` 标记的用例如实反映系统现有缺陷，不影响流水线绿灯。

## 五、已知缺陷（自动化用例中如实体现）

1. **垂直越权**：前端路由仅校验 `sessionStorage` 的 `token` / `type`，后端接口无鉴权，
   学生账号篡改 `type=admin` 后可直接进入管理员后台（`test_01_login.py::test_05_student_privilege_escalation`，标记 `xfail`）。
2. **接口未授权访问**：`GET /teacher/findById/{tid}` 无 Token 也能返回教师（含管理员）明文密码。
3. **前端残留调试按钮**：登录页、学生/教师/课程新增页均保留 `test` 按钮，点击后控制台输出表单数据。

## 六、后续可扩展

1. 补充 **开课表管理**（`/CourseTeacher`）与 **成绩管理**（`/gradeCourseManage`）模块用例。
2. 补充教师、学生角色登录后的业务流程用例（教师开课、学生选课、成绩录入）。
3. 增加接口层用例（requests + 数据库校验），用于快速造数据与清理数据，形成 UI + 接口的分层测试。
4. 接入 Jenkins 定时执行，配合 `AUTO_ALLURE_REPORT` / `HEADLESS` 环境变量在流水线中生成测试报告。
