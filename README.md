# 电商平台数据分析工具 - 功能指南

## 项目概述
这是一个**电商数据采集与分析系统**，基于 Selenium + Streamlit 构建，专门用于天猫/淘宝平台的商品数据采集、分析和商业洞察。
本项目是一款面向电商场景的专业化数据分析工具，依托AI辅助开发模式完成全流程研发，致力于为电商业务提供高效、便捷、可视化的数据采集与分析解决方案，助力从业者实现业务数据的精细化运营与决策支撑。

在开发架构层面，项目采用AI协同开发体系搭建技术研发流程

一、需求研究与业务拆解阶段

借助ChatGPT进行需求解构、场景化分析能力，深度挖掘电商从业者数据采集、多维分析、可视化展示、报告导出等核心痛点，梳理标准化业务流程与功能诉求；利用GLM5.1的中文垂直领域优化优势，精准适配国内电商平台业务规则，完成需求可行性分析、竞品功能对比、核心功能优先级排序；再由Gemini进行多维度信息整合，输出完整的需求说明书、业务框架图与功能清单，明确项目开发边界与核心目标，为后续开发奠定精准方向。

二、技术方案与架构设计阶段

ChatGPT主导技术栈选型、系统架构设计，结合电商数据分析工具的功能需求，敲定前端交互、数据采集、数据分析、存储可视化等模块的技术方案，输出模块化架构图、开发规范与接口设计文档；利用Gemini的逻辑推理与技术整合能力，完成技术方案可行性验证、性能瓶颈预判、安全机制设计，优化整体架构的扩展性与稳定性；通过GLM5.1细化本土化技术适配方案，针对国内电商平台数据接口、数据格式特点，调整架构适配逻辑，Cloud Code智能代理同步完成云端开发环境的初步配置，形成完整可执行的技术开发方案。

三、代码开发与功能实现阶段

以Codex、Cloud Code为执行层智能代理，三大模型分工协作完成代码编写与功能落地。Codex依托专业代码生成能力，在ChatGPT的指令驱动下，完成核心业务代码、功能模块代码的批量生成，覆盖数据采集逻辑、数据分析算法、可视化界面搭建、数据存储交互等核心代码开发；GLM5.1针对中文开发场景、国内电商平台特殊逻辑，完成代码本土化优化、语法修正、注释完善，保障代码适配性与可读性；Gemini负责复杂逻辑代码调试、代码结构优化、多模块代码整合，解决模块间耦合问题；全程以VS Code为开发工作台、Trae为辅助工具，智能代理实时同步代码进度，实现需求意图到代码实现的无缝转化，高效推进各功能模块开发。

四、测试调试与漏洞修复阶段

构建多模型联动的测试调试体系，保障项目功能稳定性。由ChatGPT生成全面测试用例，覆盖功能测试、兼容性测试、性能测试、数据安全测试等全场景，明确测试标准与校验规则；Gemini凭借强大的问题排查能力，对代码运行报错、功能异常、数据采集偏差等问题进行精准定位，快速分析故障根源并生成修复方案；GLM5.1针对测试中出现的本土化适配漏洞、平台规则适配问题，完成针对性修复与优化；Cloud Code智能代理同步执行测试脚本，实时反馈测试结果，形成“测试-定位-修复-复测”的闭环，全面消除项目运行隐患。

五、优化迭代与项目落地阶段

完成项目最终优化与上线落地，实现产品化交付。ChatGPT基于用户体验视角，梳理功能优化点，提出界面交互、操作流程、数据展示效果的优化建议；Gemini从系统性能、运行效率、扩展性角度，对代码进行精简优化，提升工具运行速度与后续迭代灵活性；GLM5.1完善项目说明文档、使用教程、操作指引等本土化配套内容，降低工具使用门槛；智能代理完成项目打包、环境配置、部署测试，最终实现电商平台数据分析工具的完整落地，确保工具可稳定运行、开箱即用，满足电商数据精细化分析与运营决策支撑的核心需求。

工具聚焦电商平台业务数据处理痛点，搭建了从数据采集、清洗、分析到可视化展示的全闭环功能体系，可实现电商业务数据的自动化抓取、多维度数据分析、交互式图表生成、数据报告导出等核心能力，具备操作便捷、扩展性强、适配性优等特点，能够有效满足电商从业者对平台运营数据、用户数据、交易数据的全方位分析需求。
 
本项目依托AI辅助开发技术优势，打破传统代码开发的效率瓶颈，实现了开发意图到功能落地的快速转化，既具备实用的电商数据处理落地价值，也为AI赋能软件开发、垂直领域数据分析工具研发提供了可参考的实践方案，推动电商数据分析工具向轻量化、智能化、易用化方向发展。
**技术栈：**
- Python 3.8+
- Streamlit (Web UI框架)
- Selenium 4.x（浏览器自动化）
- Plotly (数据可视化)
- SQLite (数据存储)

**架构特点：**
- ✅ 对标电商后台分层设计
- ✅ 模块化页面架构（7个独立页面）
- ✅ 实时登录模式（无需手动管理Cookie）
- ✅ B端专业版UI/UX设计
- ✅ 动态导航状态同步
### 核心特性
1. **实时登录模式**：无需预先保存Cookie，每次采集自动打开浏览器等待用户登录
2. **动态导航同步**：程序化导航后侧边栏状态自动更新（使用动态key机制）
3. **智能文件过滤**：使用`any()`动态查找替代`in`操作符（兼容Streamlit环境）
4. **状态机架构**：数据采集采用状态机设计（IDLE → BROWSER_OPEN → LOGIN_CONFIRMED → CRAWLING → COMPLETE）
## 🚀 运行方式
### 方式1: GUI模式（推荐）
```bash
cd food_analyzer
streamlit run main.py
**访问地址:** http://localhost:8501
**功能特性：**
- 🎨 现代化B端UI设计（对标Tableau/Power BI）
- 🔄 实时交互（无需刷新页面）
- 📊 丰富的可视化图表（Plotly交互式图表）
- 🔐 安全的实时登录模式
### 方式2: CLI模式（批处理）
```bash
# 完整流程
python main.py --mode full

# 仅数据采集
python main.py --mode crawl --products 100

# 仅数据分析
python main.py --mode analyze

# 测试模式（使用模拟数据）
python main.py --mode test --test-count 20

# 无头模式（服务器环境）
python main.py --mode full --headless
## 📄 页面模块详细说明

### Page 0: 数据概览仪表盘 (`views/dashboard.py`)

**功能：**
- KPI指标卡片（商品数、均价、店铺数、价格区间）
- 空状态引导界面（一键跳转到数据采集）
- 快速导航按钮组（开始采集、测试模式、查看教程）

**技术实现：**
```python
from views.dashboard import render
render()  # 渲染仪表盘页面
```

**导航按钮：**
- "🚀 开始采集" → 跳转到 `数据采集` 页面
- "🧪 测试模式" → 跳转到 `数据采集` 页面（测试模式）
- "📖 查看教程" → 跳转到 `使用帮助` 页面
### Page 1: 数据采集中心 (`views/data_collection.py`) 
**功能：**
- 参数化配置（关键词、数量、评价数、运行模式）
- 实时登录流程（自动打开浏览器 → 等待登录 → 确认继续）
- 状态机架构（5个状态：IDLE/BROWSER_OPEN/LOGIN_CONFIRMED/CRAWLING/COMPLETE）
- 实时进度显示
- 正式采集与测试模式切换
- 无头模式支持

**工作流程：**
```
1. 用户配置参数并点击"开始采集"
2. 系统自动启动Edge浏览器并跳转淘宝登录页
3. 用户在浏览器中完成扫码/密码登录
4. 登录成功后返回工具界面点击"✅ 我已完成登录"
5. 系统开始数据采集（带实时进度显示）
6. 采集完成后数据自动保存到output/目录
```

**状态常量：**
```python
STATE_IDLE = "idle"
STATE_BROWSER_OPEN = "browser_open"
STATE_LOGIN_CONFIRMED = "login_confirmed"
STATE_CRAWLING = "crawling"
STATE_COMPLETE = "complete"
```
### Page 2: 数据分析工作台 (`views/data_analysis.py`)

**功能：**
- 4大分析维度：
  1. 📈 价格分布分析（直方图+箱线图+统计值）
  2. 🏪 品牌市场分析（市场份额饼图+TOP排行柱状图）
  3. 👥 消费者画像（评分分布+评价关键词云图）
  4. 📋 综合报告生成
- Plotly交互式图表
- 空状态引导（跳转到数据采集页面）

**可视化工具：**
```python
from utils.visualizer import Visualizer, quick_analyze

viz = Visualizer()
df, filename = viz.load_data()

# 创建图表
fig_histogram = viz.create_price_histogram(df)
fig_boxplot = viz.create_price_boxplot(df)
fig_pie = viz.create_price_pie_chart(df)
fig_bar = viz.create_shop_bar_chart(df, top_n=15)

# 快速分析
result = quick_analyze()
### Page 3: 报告中心 (`views/report_center.py`) 
**功能：**
- 文件列表展示（日志/JSON/报告/表格）
- 高级筛选系统：
  - 文件类型多选筛选
  - 关键词搜索
  - 多种排序方式
- 批量操作（下载打包ZIP、批量删除）
- 在线预览（支持JSON格式化展示）
- 一键"显示全部文件"按钮
**技术要点（重要）：**
```python
# 使用 any() 动态查找替代 in 操作符（兼容Streamlit环境）
actual_selection = st.session_state.get('report_file_filter', [])

# ✅ 正确方式：动态查找
has_json_option = any("JSON" in item for item in actual_selection)

# ❌ 避免方式：直接对列表使用 in（在Streamlit中可能异常）
has_json_option = "JSON数据" in actual_selection  # 可能失败！
**支持的文件类型：**
- `.log/.txt` - 日志文件
- `.json` - JSON数据（采集结果）
- `.md/.html` - 分析报告
- `.csv/.xlsx` - 表格数据
### Page 4: Cookie管理 (`views/cookie_management.py`) 

**当前模式：实时登录（推荐）**

**重要变更**：本版本已移除传统的Cookie管理模式，改用更安全便捷的**实时登录模式**。

**工作原理：**
1. 无需预先保存Cookie到本地
2. 每次数据采集时自动打开浏览器
3. 用户在浏览器中完成登录
4. 登录会话在浏览器生命周期内保持有效
5. 采集完成后浏览器可关闭

**优势：**
- ✅ **安全性更高**：不在本地存储敏感Cookie信息
- ✅ **稳定性更好**：避免Cookie过期导致采集失败
- ✅ **操作简单**：无需学习Cookie管理知识
- ✅ **自动适配**：支持扫码、密码等多种登录方式
**页面内容：**
- 模式说明（为什么使用实时登录）
- 5步操作流程指引
- 常见问题解答
### Page 5: 系统设置 (`views/system_settings.py`)
**功能：**
- 基本设置（默认关键词、默认采集数量、默认评价数量、输出格式）
- 高级设置（无头模式开关、请求延迟时间、超时时间、重试次数）
- 设置持久化（保存到settings.json）
- 数据清理功能（清理日志/输出文件）
- 导出/恢复默认配置
**配置示例：**
```python
from utils.config import Config
config = Config()
# 获取配置
print(config.keyword)           # 默认搜索词
print(config.product_count)     # 默认采集数量
# 保存用户设置
config.save_settings({
    'default_keyword': '零食',
    'headless_mode': True,
    'timeout': 60
})
# 重置为默认
config.reset_to_defaults()
### Page 6: 使用帮助
**功能：**
- v3.0 Pro完整用户指南
- 3步快速开始指南（基于实时登录模式）
- 功能模块详解表（7个模块详细描述）
- 高级功能说明（测试模式对比、实时登录优势、4大分析维度）
- 7个常见问题FAQ
- 系统要求与技术规格
- 快捷操作按钮（前往采集、查看分析、管理Cookie）

**快捷导航按钮：**
- "前往采集" → 使用 `pending_navigation` 机制跳转
- "查看分析" → 直接修改 `current_page`
- "管理Cookie" → 跳转到Cookie管理说明页
## 🔧 导航系统技术细节
### 动态Key机制（解决侧边栏状态同步问题）
**问题背景：**
当用户通过页面内的按钮进行程序化导航时，侧边栏的radio组件不会自动更新选中状态。
**解决方案：**
```python
# main.py 中的实现
# 维护版本计数器
if 'nav_version' not in st.session_state:
    st.session_state.nav_version = 0
# 动态生成radio组件的key
radio_key = f"sidebar_navigation_v{st.session_state.nav_version}"
# 创建radio组件
selection = st.sidebar.radio(
    "导航菜单",
    page_labels,
    index=current_index,
    key=radio_key  # 每次key不同 = 强制重新创建组件
)

# 检测程序化导航
if pending_nav and pending_nav in page_labels:
    st.session_state.current_page = pending_nav
    st.session_state.pending_navigation = None
    st.session_state.nav_version += 1  # 增加版本号
elif (st.session_state.current_page != selection and 
      st.session_state.current_page != st.session_state.last_radio_selection):
    # 检测外部页面变更
    st.session_state.nav_version += 1
## 🛠️ 故障排除（已验证的解决方案）

### 问题1：ValueError - stdout重定向错误

**症状：** `ValueError: This app has encountered an error related to stdout redirection`

**原因：** Windows环境下stdout重定向与Streamlit冲突

**解决：**
```python
# main.py 开头
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, Exception):
        pass  # Streamlit环境下跳过
```

### 问题2：报告中心文件不显示

**症状：** 筛选条件正确但文件列表为空

**原因：** Streamlit环境中Python的`in`操作符对列表的包含检查行为异常

**解决：**
```python
# ❌ 失败的方式
has_json = "JSON数据" in actual_selection  # 可能返回False！

# ✅ 成功的方式
has_json = any("JSON" in item for item in actual_selection)  # 100%可靠
```

### 问题3：侧边栏导航状态不更新

**症状：** 点击页面内按钮跳转后，左侧导航栏高亮位置不变

**原因：** Streamlit radio组件是有状态widget，不会跟随index参数变化

**解决：** 使用动态key机制（见上文"导航系统技术细节"）

### 问题4：argparse冲突

**症状：** 启动时报错 argparse 相关错误

**原因：** argparse与Streamlit的命令行参数处理冲突

**解决：**
```python
if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(...)
        args = parser.parse_args()
        if args.mode:
            run_cli_mode(args)
        else:
            main()
    except (ValueError, SystemExit):
        main()  # Streamlit环境兼容处理
## 📈 性能优化建议
### 1. 提高采集速度
```python
# 编辑 utils/config.py 或在系统设置中调整
{
    "crawler": {
        "request_delay_min": 0.5,  # 原来1秒
        "request_delay_max": 1.5   # 原来3秒
    }
}
```

### 2. 增加稳定性

```python
{
    "crawler": {
        "max_retries": 5  # 原来3次
    }
}
```

### 3. Headless模式（服务器环境）

```bash
# CLI模式
python main.py --mode full --headless

# 或在系统设置中开启"默认无头模式"
## 🎯 最佳实践
### ✅ 推荐做法
1. **首次使用**：先用"🧪 测试模式"（10-20个商品）验证配置
2. **分时段采集**：避免高峰期（早9-11点，晚8-10点）
3. **多关键词覆盖**：细分到具体品类
4. **定期备份数据**：每周复制 `output/` 目录
5. **遵守robots协议**：合理设置请求间隔（建议1-3秒）
6. **保持浏览器开启**：采集中不要关闭弹出的Edge窗口
### ❌ 避免事项
1. **高频采集**：同IP每天不超过500次请求
2. **并发过高**：单线程顺序采集最稳定
3. **忽略异常**：及时检查 `logs/` 目录排查问题
4. **过度依赖**：爬虫可能随时失效，要有备用方案
5. **关闭浏览器**：采集中关闭浏览器会导致任务中断
## 📝 版本信息

- **当前版本**: v3.0 Pro (Modern UI Edition)

## 🎉 总结
**核心优势：**
- ✅ **架构先进**: 对标电商后台分层设计，模块化清晰
- ✅ **UI现代化**: B端专业版设计，对标Tableau/Power BI
- ✅ **功能完整**: 7大页面 + 3大工具集 + AI分析引擎
- ✅ **易于使用**: GUI零代码操作 + CLI批处理支持
- ✅ **安全可靠**: 实时登录模式 + 反检测技术
- ✅ **可扩展性强**: 新增功能只需添加页面模块
*部分内容由Cloud code，Codex，Gemini，Chatgpt，GLM -5.1赞助*

**祝使用愉快！** 

*已发现的BUG*

**1.等待用户登录阶段，登录页面内容丢失，为淘宝网页反爬机制所致，主动F5刷新后正常登录即可**

**2.数值选择条上方滑块显示异常，为Streamlit渲染异常所致，正常使用即可**
