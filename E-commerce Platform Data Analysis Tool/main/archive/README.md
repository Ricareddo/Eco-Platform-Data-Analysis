# Archive - 旧版文件归档

此目录包含项目早期版本的文件，已整合到新的模块化架构中。

## 文件说明

| 文件名 | 原功能 | 替代方案 |
|--------|--------|---------|
| `gui_streamlit.py` | 旧版Streamlit GUI入口 | `main.py` + `views/` 目录 |
| `cookie_manager.py` | 旧版Cookie管理工具 | `views/cookie_management.py` (实时登录模式) |
| `crawl_intelligent.py` | 旧版智能采集脚本 | `views/data_collection.py` + `crawlers/` |
| `analyze_data.py` | 旧版数据分析脚本 | `views/data_analysis.py` |
| `show_data_value.py` | 旧版数据查看工具 | `views/dashboard.py` |

## 重要提示

**这些文件仅作存档参考，不应再使用。**

所有功能已整合到新的架构中：
- 统一入口：`main.py`
- 页面模块：`views/` 目录
- 工具集：`utils/`, `components/`, `crawlers/`

## 归档日期

2026-04-12
