"""
Pages模块 - 电商平台数据分析工具的核心页面
对标电商后台分层设计 | B端专业版UI/UX
"""

from . import dashboard
from . import data_collection
from . import data_analysis
from . import report_center
from . import cookie_management
from . import system_settings
from . import help_guide

__all__ = [
    'dashboard',
    'data_collection', 
    'data_analysis',
    'report_center',
    'cookie_management',
    'system_settings',
    'help_guide'
]
