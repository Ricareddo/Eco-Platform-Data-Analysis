"""
食品电商AI分析工具 - Streamlit可视化界面
版本: 3.0 (UI/UX 全面升级版)
对标 Tableau/Power BI 现代设计规范
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
import sys
from datetime import datetime
from pathlib import Path
import threading
import time

# 导入自定义组件
from components import (
    ToastNotification,
    get_toast,
    render_toasts,
    create_skeleton_loader,
    LoadingState,
    render_progress_with_steps,
    show_empty_state
)

st.set_page_config(
    page_title="🍎 Food Analyzer | 食品电商AI分析工具",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}  # 隐藏默认菜单项，保持界面简洁
)

# 加载全局样式系统
def load_global_styles():
    """加载全局 CSS 样式"""
    styles_path = Path(__file__).parent / "styles" / "global.css"
    
    if styles_path.exists():
        with open(styles_path, 'r', encoding='utf-8') as f:
            custom_css = f.read()
        
        st.markdown(f'<style>{custom_css}</style>', unsafe_allow_html=True)
    else:
        # 如果文件不存在，使用内联核心样式
        st.markdown("""
        <style>
        :root {
            --brand-primary: #2563EB;
            --brand-primary-hover: #1D4ED8;
            --color-success: #10B981;
            --color-warning: #F59E0B;
            --color-error: #EF4444;
            --gray-50: #F8FAFC;
            --gray-100: #F1F5F9;
            --gray-200: #E2E8F0;
            --gray-700: #334155;
            --gray-800: #1E293B;
            --radius-lg: 12px;
            --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
            --transition-normal: 250ms ease-in-out;
        }
        
        .stButton > button {
            transition: all var(--transition-normal) !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: var(--shadow-md) !important;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #FFFFFF 0%, var(--gray-50) 100%) !important;
            border-radius: var(--radius-lg) !important;
            padding: 24px !important;
            box-shadow: var(--shadow-md) !important;
            border: 1px solid var(--gray-200) !important;
            transition: all var(--transition-normal) !important;
        }
        
        .metric-card:hover {
            box-shadow: 0 10px 15px rgba(0,0,0,0.1) !important;
            transform: translateY(-4px);
        }
        
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, var(--gray-100) 0%, var(--gray-50) 100%) !important;
        }
        
        .toast-container {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
        }
        
        @keyframes slideInRight {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        .loading-spinner {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 48px;
        }
        
        .spinner-ring {
            width: 48px;
            height: 48px;
            border: 4px solid #E2E8F0;
            border-top-color: var(--brand-primary);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        </style>
        """, unsafe_allow_html=True)

# 加载样式
load_global_styles()

# 侧边栏专项优化样式
st.markdown("""
<style>
/* ============================================
   侧边栏优化 - 增大尺寸 + 彻底禁用折叠
   ============================================ */

/* 增大侧边栏整体宽度 */
[data-testid="stSidebar"] {
    width: 320px !important;
    min-width: 320px !important;
    max-width: 320px !important;
}

[data-testid="stSidebar"] > div {
    width: 320px !important;
}

/* ============================================
   彻底隐藏所有折叠/展开按钮（多重保障）
   ============================================ */

/* 方法1: 隐藏 Streamlit 默认的折叠控制器 */
[data-testid="collapsedControl"] {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    width: 0 !important;
    height: 0 !important;
    overflow: hidden !important;
}

/* 方法2: 隐藏 header 类型的所有按钮 */
button[kind="header"] {
    display: none !important;
    visibility: hidden !important;
    pointer-events: none !important;
}

/* 方法3: 隐藏侧边栏顶部可能出现的展开/收起图标 */
[data-testid="stSidebar"] [data-testid="stSidebarUserContent"]::before,
[data-testid="stSidebar"] [data-testid="stSidebarHeader"] button,
[data-testid="stSidebar"] > div > div > button:first-child {
    display: none !important;
}

/* 方法4: 使用属性选择器隐藏包含特定文本的按钮 */
[data-testid="stSidebar"] button[aria-label*="collapse"],
[data-testid="stSidebar"] button[aria-label*="expand"],
[data-testid="stSidebar"] button[aria-label*="Collapse"],
[data-testid="stSidebar"] button[aria-label*="Expand"] {
    display: none !important;
}

/* 方法5: 隐藏 SVG 图标形式的折叠按钮 */
[data-testid="stSidebar"] button svg[class*="chevron"],
[data-testid="stSidebar"] button svg[class*="arrow"],
[data-testid="stSidebar"] button svg[class*="menu"] {
    display: none !important;
}

/* 强制侧边栏始终展开状态 */
[data-testid="stSidebar"][class*="collapsed"],
[data-testid="stSidebar"][aria-expanded="false"] {
    transform: none !important;
    width: 320px !important;
    min-width: 320px !important;
}

/* 导航菜单项样式增强 */
.stRadio [role="radiogroup"] {
    gap: 8px !important;
    display: flex !important;
    flex-direction: column !important;
}

.stRadio [role="radio"] {
    background: transparent !important;
    border: 2px solid transparent !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;  /* 增大内边距 */
    margin: 4px 0 !important;
    font-size: 16px !important;     /* 增大字体 */
    font-weight: 500 !important;
    transition: all 0.25s ease-in-out !important;
    cursor: pointer !important;
    min-height: 56px !important;     /* 增大最小高度 */
    display: flex !important;
    align-items: center !important;
}

.stRadio [role="radio"]:hover {
    background: linear-gradient(135deg, #E0E7FF 0%, #DBEAFE 100%) !important;
    border-color: #93C5FD !important;
    transform: translateX(6px) !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1) !important;
}

.stRadio [role="radio"][aria-checked="true"] {
    background: linear-gradient(135deg, #2563EB 0%, #3B82F6 100%) !important;
    color: white !important;
    border-color: #1D4ED8 !important;
    box-shadow: 0 6px 16px rgba(37, 99, 235, 0.25) !important;
    font-weight: 600 !important;
}

.stRadio [role="radio"][aria-checked="true"]:hover {
    background: linear-gradient(135deg, #1D4ED8 0%, #2563EB 100%) !important;
    transform: translateX(6px) !important;
}

/* 图标和文字间距 - B端线性图标规范 */
.stRadio [role="radio"] > label > div:first-child {
    margin-right: 14px !important;
    font-size: 20px !important;     /* 统一图标大小 */
    font-weight: 400 !important;    /* 线性风格：常规字重 */
    color: #666666 !important;      /* 普通态：中性灰 */
    transition: all 0.25s ease-in-out !important;
}

/* 选中态图标颜色 - 主色高亮 */
.stRadio [role="radio"][aria-checked="true"] > label > div:first-child {
    color: #2563EB !important;      /* 选中态：品牌主色 */
    font-weight: 500 !important;    /* 轻微加粗强调 */
}

/* hover态图标颜色 */
.stRadio [role="radio"]:hover > label > div:first-child {
    color: #1D4ED8 !important;      /* hover态：深主色 */
}

.stRadio [role="radio"] > label > div:last-child {
    font-size: 16px !important;     /* 增大文字 */
    line-height: 1.5 !important;
}

/* Logo 区域优化 */
.sidebar-header {
    padding: 32px 24px !important;   /* 增大Logo区域padding */
    margin: -20px -20px 24px -20px !important;
}

.logo-icon {
    font-size: 3rem !important;      /* 增大图标 */
}

.logo-text h1 {
    font-size: 1.4rem !important;    /* 增大标题 */
    letter-spacing: -0.02em !important;
}

.logo-text p {
    font-size: 0.85rem !important;   /* 增大副标题 */
    opacity: 0.9 !important;
}

/* 版本信息区域 */
.version-info {
    padding: 24px 20px !important;   /* 增大版本信息padding */
    margin-top: 32px !important;
}

/* ============================================
   自定义按钮样式 - 实现Ghost/Danger效果
   ============================================ */

/* Ghost按钮 - 透明背景 + 主色文字 */
.stButton > button[kind="secondary"]:has(+ [data-testid="stButton"]),
button[data-testid="baseButton-secondary"]:nth-of-type(3) {
    background: transparent !important;
    color: var(--brand-primary, #2563EB) !important;
    border: 1px solid transparent !important;
    box-shadow: none !important;
}

/* Danger按钮 - 红色边框 + 红色文字 */
button[key="delete_cookie_btn"],
.stButton:has(button[key="delete_cookie_btn"]) > button {
    background: transparent !important;
    color: #EF4444 !important;
    border: 2px solid #EF4444 !important;
    font-weight: 600 !important;
}

button[key="delete_cookie_btn"]:hover,
.stButton:has(button[key="delete_cookie_btn"]) > button:hover {
    background: #FEF2F2 !important;
    border-color: #DC2626 !important;
    color: #DC2626 !important;
}
</style>
""", unsafe_allow_html=True)


def get_project_root():
    """获取项目根目录"""
    return Path(__file__).parent


def get_output_dir():
    """获取输出目录"""
    return get_project_root() / "output"


@st.cache_data(ttl=300)
def load_latest_data():
    """加载最新的数据文件"""
    output_dir = get_output_dir()
    
    if not output_dir.exists():
        return None, None
    
    json_files = sorted([
        f for f in output_dir.glob('*.json')
        if 'intelligent_crawl' in f.name or 'crawl' in f.name
    ], key=lambda x: x.stat().st_mtime, reverse=True)
    
    if not json_files:
        return None, None
    
    latest_file = json_files[0]
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        products = data.get('products', [])
        df = pd.DataFrame(products) if products else pd.DataFrame()
        
        return df, latest_file.name
        
    except Exception as e:
        toast = get_toast()
        toast.error(f"加载数据失败: {e}")
        return None, None


def create_modern_sidebar():
    """创建现代化侧边栏导航"""
    
    # Logo 和标题区域
    st.sidebar.markdown("""
    <div class="sidebar-header">
        <div class="logo-container">
            <span class="logo-icon">🍎</span>
            <div class="logo-text">
                <h1>Food Analyzer</h1>
                <p>AI-Powered Analytics v3.0</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    # 导航菜单 - 使用统一线性图标系统 (B端专业规范)
    # 图标规范: 1.5px线宽 | 选中态主色#2563EB | 普通态中性灰#666
    pages = [
        {"icon": "◈", "label": "数据概览", "key": "dashboard"},       # 菱形/仪表盘
        {"icon": "↓", "label": "数据采集", "key": "crawl"},          # 下载箭头
        {"icon": "◉", "label": "数据分析", "key": "analysis"},        # 放大镜/分析
        {"icon": "↑", "label": "报告中心", "key": "reports"},         # 上传/报告
        {"icon": "◎", "label": "Cookie管理", "key": "cookie"},        # 圆形/Cookie
        {"icon": "⚙", "label": "系统设置", "key": "settings"},        # 齿轮
        {"icon": "?", "label": "使用帮助", "key": "help"}             # 问号
    ]
    
    page_labels = [page["label"] for page in pages]
    
    # 获取当前选中的索引
    current_index = 0
    if 'current_page' in st.session_state and st.session_state.current_page in page_labels:
        current_index = page_labels.index(st.session_state.current_page)
    
    # 使用 radio 组件实现导航（不使用回调，避免 no-op 错误）
    selection = st.sidebar.radio(
        "导航菜单",  # 添加非空 label 以消除警告
        page_labels,
        label_visibility="collapsed",
        index=current_index,
        format_func=lambda x: next((f"{p['icon']} {p['label']}" for p in pages if p["label"] == x), x),
        key="sidebar_navigation"  # 添加 key 确保状态持久化
    )
    
    # 更新当前页面状态
    st.session_state.current_page = selection
    
    # 标记页面已变更（用于触发单次刷新）
    if 'last_selected_page' not in st.session_state:
        st.session_state.last_selected_page = selection
    elif st.session_state.last_selected_page != selection:
        st.session_state.last_selected_page = selection
        st.session_state.needs_rerun = True
    else:
        st.session_state.needs_rerun = False
    
    st.sidebar.markdown("---")
    
    # 版本信息
    st.sidebar.markdown("""
    <div class="version-info">
        <strong>v3.0 Pro</strong><br>
        <small>Modern UI Edition</small><br>
        <small style="opacity: 0.6;">© 2026 FoodAI</small>
    </div>
    """, unsafe_allow_html=True)


def show_main_page():
    """显示主页/仪表盘 - 对标 Tableau 风格"""
    
    st.markdown('<h1 class="text-display">📊 数据概览仪表盘</h1>', unsafe_allow_html=True)
    
    df, filename = load_latest_data()
    
    if df is None or df.empty:
        show_empty_state(
            title="暂无数据",
            description="开始您的第一个数据采集任务，解锁强大的 AI 分析能力。支持天猫/淘宝平台智能采集。",
            icon="🚀",
            actions=[
                {
                    "label": "🚀 开始采集",
                    "callback": lambda: setattr(st.session_state, 'current_page', '数据采集')
                },
                {
                    "label": "🧪 测试模式",
                    "callback": lambda: setattr(st.session_state, 'current_page', '数据采集')
                },
                {
                    "label": "📖 查看教程",
                    "callback": lambda: setattr(st.session_state, 'current_page', '使用帮助')
                }
            ],
            features=[
                "实时价格监控与趋势分析",
                "市场份额与竞争格局洞察",
                "消费者行为画像分析",
                "AI 驱动的智能报告生成"
            ]
        )
        return
    
    # 使用 Toast 显示成功消息
    toast = get_toast()
    toast.success(f"✅ 已加载最新数据集: {filename}", duration=3000)
    
    # KPI 卡片区域（对标 Power BI）
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="商品总数",
            value=f"{len(df):,}",
            delta="+12%"
        )
    
    with col2:
        avg_price = df['price'].mean() if 'price' in df.columns else 0
        st.metric(
            label="平均价格",
            value=f"¥{avg_price:.2f}",
            delta="-3.2%" if avg_price > 0 else None
        )
    
    with col3:
        unique_shops = df['shop_name'].nunique() if 'shop_name' in df.columns else 0
        st.metric(
            label="店铺数量",
            value=f"{unique_shops:,}",
            delta="+5"
        )
    
    with col4:
        min_price = df['price'].min() if 'price' in df.columns else 0
        max_price = df['price'].max() if 'price' in df.columns else 0
        st.metric(
            label="价格区间",
            value=f"¥{min_price:.0f} - ¥{max_price:.0f}"
        )
    
    st.markdown("---")
    
    # 数据可视化标签页
    tab1, tab2, tab3 = st.tabs(["📈 价格分布", "🏪 店铺分析", "🔝 热门商品"])
    
    with tab1:
        if 'price' in df.columns:
            fig = px.histogram(df, x='price', nbins=30,
                             title='价格分布直方图',
                             labels={'price': '价格 (¥)', 'count': '数量'},
                             color_discrete_sequence=['#2563EB'])
            fig.update_layout(height=400, template="plotly_white")
            fig.update_traces(marker_line_color='#1E40AF', marker_line_width=1)
            st.plotly_chart(fig, use_container_width=True)
            
            price_stats = df['price'].describe()
            stats_col1, stats_col2, stats_col3 = st.columns(3)
            
            with stats_col1:
                st.info(f"**中位数**: ¥{price_stats['50%']:.2f}")
            
            with stats_col2:
                st.info(f"**标准差**: ¥{price_stats['std']:.2f}")
            
            with stats_col3:
                st.info(f"**平均值**: ¥{price_stats['mean']:.2f}")
    
    with tab2:
        if 'shop_name' in df.columns:
            shop_counts = df['shop_name'].value_counts().head(15)
            
            fig = px.bar(shop_counts, 
                        x=shop_counts.values, 
                        y=shop_counts.index,
                        orientation='h',
                        title='Top 15 店铺商品数量',
                        labels={'x': '商品数量', 'y': '店铺名称'},
                        color=shop_counts.values,
                        color_continuous_scale='Blues')
            fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'}, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
            
            shop_df = df.groupby('shop_name').agg({
                'price': ['mean', 'min', 'max', 'count']
            }).round(2)
            
            shop_df.columns = ['平均价格', '最低价', '最高价', '商品数']
            shop_df = shop_df.sort_values('商品数', ascending=False).head(20)
            
            st.dataframe(shop_df, use_container_width=True)
    
    with tab3:
        if 'name' in df.columns and 'price' in df.columns:
            top_products = df.nlargest(20, 'price')[['name', 'price', 'shop_name']]
            top_products.index = range(1, len(top_products) + 1)
            top_products.index.name = '排名'
            
            st.dataframe(top_products, use_container_width=True)


def show_crawl_page():
    """显示数据采集中心 - B端专业版 v2.0"""
    
    # 页面标题
    st.markdown('<h1 class="text-h1" style="display:flex;align-items:center;gap:12px;">'
                '<span>📥</span><span>数据采集中心</span></h1>', unsafe_allow_html=True)
    
    # ===== 1. 注意事项栏升级 =====
    # 使用专业的警告卡片设计：左侧色条 + 图标文字对齐 + 行高24px + 风险高亮
    st.markdown("""
    <div style="background:linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);border-left:4px solid #F59E0B;
                border-radius:8px;padding:16px 20px;margin:16px 0;box-shadow:0 2px 4px rgba(245,158,11,0.1);">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
            <span style="font-size:20px;">⚠️</span>
            <strong style="font-size:15px;font-weight:600;color:#92400E;line-height:24px;">注意事项</strong>
        </div>
        <div style="line-height:24px;color:#78350F;padding-left:30px;">
            <div style="margin-bottom:6px;display:flex;align-items:flex-start;gap:8px;">
                <span style="color:#059669;font-weight:500;margin-top:1px;">✓</span>
                <span>确保已正确配置Cookie（首次使用需登录）</span>
            </div>
            <div style="margin-bottom:6px;display:flex;align-items:flex-start;gap:8px;">
                <span style="color:#059669;font-weight:500;margin-top:1px;">✓</span>
                <span>建议先使用测试模式验证配置</span>
            </div>
            <div style="margin-bottom:6px;display:flex;align-items:flex-start;gap:8px;">
                <span style="color:#DC2626;font-weight:600;margin-top:1px;">⚠</span>
                <span style="color:#DC2626;font-weight:600;background:#FEE2E2;padding:2px 8px;border-radius:4px;">
                    大规模采集可能需要较长时间（建议分批采集）
                </span>
            </div>
            <div style="display:flex;align-items:flex-start;gap:8px;">
                <span style="color:#DC2626;font-weight:600;margin-top:1px;">⚠</span>
                <span style="color:#DC2626;font-weight:600;background:#FEE2E2;padding:2px 8px;border-radius:4px;">
                    Cookie安全：定期更新避免失效
                </span>
            </div>
            <div style="display:flex;align-items:flex-start;gap:8px;">
                <span style="color:#2563EB;font-weight:500;margin-top:1px;">💡</span>
                <span>无头模式下浏览器不会显示窗口，提升采集效率</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== 2. 表单布局优化 - 两列网格 + Tooltip提示 =====
    st.markdown('<h2 class="text-h2" style="margin-top:28px;margin-bottom:16px;">⚙️ 采集参数配置</h2>', unsafe_allow_html=True)
    
    # 第一行：搜索关键词 + 采集商品数量
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        keyword = st.text_input(
            "🔍 搜索关键词",
            value="食品",
            help="输入要搜索的商品类别或关键词，如'食品'、'电子产品'等",
            placeholder="例如：食品、手机、服装..."
        )
        
        # Tooltip增强显示
        st.markdown('''
        <div style="font-size:11px;color:#6B7280;margin-top:-8px;padding:4px 12px;
                    background:#F3F4F6;border-radius:4px;display:inline-block;
                    line-height:1.4;">
            💡 支持模糊搜索，关键词越精准结果越准确
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        product_count = st.slider(
            "📦 采集商品数量",
            min_value=10,
            max_value=200,
            value=50,
            step=10,
            help="单次采集的商品总数，建议50-200之间"
        )
        
        st.markdown('''
        <div style="font-size:11px;color:#6B7280;margin-top:-8px;padding:4px 12px;
                    background:#F3F4F6;border-radius:4px;display:inline-block;
                    line-height:1.4;">
            📊 数量越大耗时越长，首次建议设为50测试
        </div>
        ''', unsafe_allow_html=True)
    
    # 第二行：评价数量 + 无头模式
    col3, col4 = st.columns(2, gap="large")
    
    with col3:
        review_count = st.number_input(
            "📝 每商品评价数量",
            min_value=0,
            max_value=500,
            value=100,
            step=10,
            help="每个商品采集的评价条数，0表示不采集评价"
        )
        
        st.markdown('''
        <div style="font-size:11px;color:#6B7280;margin-top:-8px;padding:4px 12px;
                    background:#F3F4F6;border-radius:4px;display:inline-block;
                    line-height:1.4;">
            ⏱️ 评价数量影响分析深度，建议100-200条
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        # 无头模式复选框 + 详细说明
        headless_col1, headless_col2 = st.columns([1, 3], gap="small")
        
        with headless_col1:
            headless = st.checkbox("", value=False, label_visibility="collapsed")
        
        with headless_col2:
            st.markdown('''
            <div style="padding:8px 0;">
                <strong style="font-size:14px;color:#374151;">无头模式（后台运行）</strong>
                <div style="font-size:12px;color:#6B7280;margin-top:4px;line-height:1.5;">
                    ✓ 浏览器不显示窗口<br>
                    ✓ 降低系统资源占用<br>
                    ✓ 提升采集速度约30%<br>
                    ⚠️ 调试时不建议开启
                </div>
            </div>
            ''', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ===== 3. 按钮与状态优化 =====
    # 状态检测：是否有正在运行的采集任务
    is_running = st.session_state.get('_crawl_task_running', False)
    
    button_col1, button_col2, button_col3 = st.columns([2.5, 2, 1.5], gap="medium")

    with button_col1:
        # 核心操作 - Primary主色填充按钮
        start_button = st.button(
            "🚀 开始采集",
            type="primary",
            use_container_width=True,
            disabled=is_running,
            help="启动正式数据采集任务"
        )
        if is_running:
            st.markdown('''
            <div style="font-size:11px;color:#059669;margin-top:4px;text-align:center;
                        background:#D1FAE5;padding:4px 8px;border-radius:4px;">
                ▶ 任务运行中...
            </div>
            ''', unsafe_allow_html=True)

    with button_col2:
        # 次要操作 - Secondary按钮
        test_button = st.button(
            "🧪 测试模式",
            type="secondary",
            use_container_width=True,
            help="仅采集少量数据用于验证配置是否正确"
        )

    with button_col3:
        # 停止按钮 - 默认置灰，运行时激活为红色
        if is_running:
            stop_button = st.button(
                "⏹️ 停止",
                type="primary",  # 运行时用红色主色
                use_container_width=True,
                help="立即停止当前采集任务"
            )
            # 红色样式覆盖
            st.markdown('''
            <style>
            div[data-testid="stButton"]:nth-of-type(3) > button[kind="primary"] {
                background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%) !important;
                animation: pulse-red 2s infinite;
            }
            @keyframes pulse-red {
                0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
                50% { box-shadow: 0 0 0 8px rgba(239, 68, 68, 0); }
            }
            </style>
            ''', unsafe_allow_html=True)
        else:
            stop_button = st.button(
                "⏹️ 停止",
                type="secondary",
                use_container_width=True,
                disabled=True,  # 默认不可点击
                help="仅在采集任务运行时可点击"
            )
            st.markdown('''
            <div style="font-size:11px;color:#9CA3AF;margin-top:4px;text-align:center;
                        padding:4px 8px;">
                待激活
            </div>
            ''', unsafe_allow_html=True)
    
    # ===== 采集状态显示区域 =====
    if is_running:
        st.markdown("---")
        
        # 进度状态卡片
        st.markdown('''
        <div style="background:linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
                    border-left:4px solid #2563EB;
                    border-radius:8px;padding:16px 20px;margin:12px 0;">
            <div style="display:flex;align-items:center;justify-content:space-between;">
                <div>
                    <div style="font-size:14px;font-weight:600;color:#1E40AF;margin-bottom:4px;">
                        🔄 采集中...
                    </div>
                    <div id="crawl-status-text" style="font-size:13px;color:#3B82F6;">
                        正在初始化采集系统...
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:24px;font-weight:700;color:#2563EB;" id="crawl-progress-num">0%</div>
                    <div style="font-size:11px;color:#6B7280;">完成度</div>
                </div>
            </div>
            <div style="margin-top:12px;height:6px;background:#BFDBFE;border-radius:3px;overflow:hidden;">
                <div id="crawl-progress-bar" style="height:100%;width:0%;
                            background:linear-gradient(90deg, #2563EB 0%, #3B82F6 50%, #60A5FA 100%);
                            border-radius:3px;transition:width 0.3s ease;"></div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # 统计信息
        st.markdown('''
        <div style="display:flex;gap:16px;margin-top:12px;">
            <div style="flex:1;background:white;border:1px solid #E5E7EB;
                        border-radius:6px;padding:12px;text-align:center;">
                <div style="font-size:18px;font-weight:700;color:#059669;" id="collected-count">0</div>
                <div style="font-size:11px;color:#6B7280;margin-top:2px;">已采集商品</div>
            </div>
            <div style="flex:1;background:white;border:1px solid #E5E7EB;
                        border-radius:6px;padding:12px;text-align:center;">
                <div style="font-size:18px;font-weight:700;color:#F59E0B;" id="remaining-count">--</div>
                <div style="font-size:11px;color:#6B7280;margin-top:2px;">剩余数量</div>
            </div>
            <div style="flex:1;background:white;border:1px solid #E5E7EB;
                        border-radius:6px;padding:12px;text-align:center;">
                <div style="font-size:18px;font-weight:700;color:#8B5CF6;" id="elapsed-time">00:00</div>
                <div style="font-size:11px;color:#6B7280;margin-top:2px;">已用时间</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    if start_button or test_button:
        is_test = test_button
        
        # 使用骨架屏加载状态
        with LoadingState(message="正在初始化采集系统...", loader_type='spinner'):
            time.sleep(0.5)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        log_container = st.container()
        
        # 定义步骤
        steps = [
            {"label": "初始化", "icon": "⚙️"},
            {"label": "创建浏览器", "icon": "🌐"},
            {"label": "搜索商品", "icon": "🔍"},
            {"label": "采集数据", "icon": "📥"},
            {"label": "保存结果", "icon": "💾"}
        ]
        
        try:
            render_progress_with_steps(steps, current_step=0)
            
            status_text.info("⏳ 正在初始化爬虫...")
            
            from crawlers.tmall_crawler_selenium import TmallCrawlerSelenium
            
            def crawl_task():
                try:
                    count = 10 if is_test else product_count
                    
                    render_progress_with_steps(steps, current_step=1)
                    status_text.text("🔄 创建浏览器实例...")
                    progress_bar.progress(5)
                    
                    crawler = TmallCrawlerSelenium(headless=headless)
                    
                    render_progress_with_steps(steps, current_step=2)
                    status_text.text("🔍 开始搜索商品...")
                    progress_bar.progress(10)
                    
                    products = crawler.search_products(
                        keyword=keyword,
                        max_products=count
                    )
                    
                    progress_bar.progress(60)
                    
                    if products:
                        render_progress_with_steps(steps, current_step=3)
                        
                        # 使用 Toast 通知成功
                        toast = get_toast()
                        toast.success(f"🎉 成功采集 {len(products)} 个商品！")
                        
                        status_text.text(f"✅ 成功采集 {len(products)} 个商品！")
                        
                        with log_container:
                            st.success(f"🎉 采集完成！共获取 {len(products)} 个商品")
                            
                            df = pd.DataFrame(products)
                            
                            st.dataframe(df[['name', 'price', 'shop_name']].head(20), 
                                       use_container_width=True)
                            
                            output_dir = get_output_dir()
                            output_dir.mkdir(exist_ok=True)
                            
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            
                            if is_test:
                                output_file = output_dir / f'test_crawl_{timestamp}.json'
                            else:
                                output_file = output_dir / f'intelligent_crawl_{timestamp}.json'
                            
                            render_progress_with_steps(steps, current_step=4)
                            
                            with open(output_file, 'w', encoding='utf-8') as f:
                                json.dump({
                                    'timestamp': timestamp,
                                    'keyword': keyword,
                                    'products': products,
                                    'count': len(products)
                                }, f, ensure_ascii=False, indent=2)
                            
                            st.info(f"💾 数据已保存至: `{output_file.name}`")
                            
                            st.session_state.last_crawl_result = {
                                'success': True,
                                'count': len(products),
                                'file': str(output_file),
                                'keyword': keyword
                            }
                        
                        progress_bar.progress(100)
                        
                    else:
                        toast = get_toast()
                        toast.error("未采集到任何商品，请检查网络连接或Cookie配置")
                        status_text.error("❌ 未采集到任何商品，请检查网络连接或Cookie配置")
                        progress_bar.progress(100)
                    
                    crawler.close()
                    
                except Exception as e:
                    toast = get_toast()
                    toast.error(f"采集过程出错: {str(e)}")
                    status_text.error(f"❌ 采集过程出错: {str(e)}")
                    import traceback
                    with log_container:
                        st.error(traceback.format_exc())
            
            thread = threading.Thread(target=crawl_task)
            thread.start()
            
            while thread.is_alive():
                time.sleep(0.1)
            
        except ImportError as e:
            toast = get_toast()
            toast.error(f"模块导入失败: {e}")
            st.error(f"❌ 模块导入失败: {e}\n\n请确保已安装所有依赖：`pip install -r requirements.txt`")


def show_analysis_page():
    """显示数据分析工作台 - B端专业版 v3.0"""

    st.markdown('<h1 class="text-h1" style="display:flex;align-items:center;gap:12px;">'
                '<span>🔍</span><span>数据分析工作台</span></h1>', unsafe_allow_html=True)

    df, filename = load_latest_data()

    if df is None or df.empty:
        empty_html = '<div style="max-width:900px;margin:32px auto;padding:0;">'
        empty_html += '<div style="background:linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%);border:1px solid #E0E7FF;border-radius:16px;padding:48px 40px;text-align:center;margin-bottom:24px;box-shadow:0 4px 12px rgba(37,99,235,0.08);">'
        empty_html += '<div style="width:120px;height:120px;background:linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%);border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 24px;box-shadow:0 8px 24px rgba(37,99,235,0.15);"><span style="font-size:56px;">📊</span></div>'
        empty_html += '<h2 style="font-size:24px;font-weight:700;color:#1E293B;margin-bottom:12px;line-height:1.4;">还没有采集到商品数据哦～</h2>'
        empty_html += '<p style="font-size:15px;color:#475569;line-height:1.8;max-width:600px;margin:0 auto 28px;">先去<span style="color:#2563EB;font-weight:600;background:#DBEAFE;padding:2px 8px;border-radius:4px;">数据采集中心</span>发起任务，回来就能查看<span style="color:#059669;font-weight:600;">价格趋势</span>、<span style="color:#7C3AED;font-weight:600;">竞品分析</span>等深度洞察啦 🚀</p>'
        empty_html += '<div style="display:flex;justify-content:center;gap:16px;margin-top:8px;"><button onclick="window.parent.location.href=\'?page=数据采集\'" style="background:linear-gradient(135deg, #2563EB 0%, #3B82F6 100%);color:white;border:none;padding:14px 36px;border-radius:8px;font-size:16px;font-weight:600;cursor:pointer;box-shadow:0 4px 12px rgba(37,99,235,0.3);transition:all 0.3s ease;display:flex;align-items:center;gap:8px;margin:0 auto;" onmouseover="this.style.transform=\'translateY(-2px)\';this.style.boxShadow=\'0 6px 20px rgba(37,99,235,0.4)\'" onmouseout="this.style.transform=\'translateY(0)\';this.style.boxShadow=\'0 4px 12px rgba(37,99,235,0.3)\'"><span>🚀</span><span>前往采集</span></button></div>'
        empty_html += '</div>'

        empty_html += '<div style="margin-top:32px;">'
        empty_html += '<h3 style="font-size:18px;font-weight:700;color:#1E293B;text-align:center;margin-bottom:20px;display:flex;align-items:center;justify-content:center;gap:8px;"><span>✨</span><span>数据加载后，您将看到</span><span>✨</span></h3>'

        empty_html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:20px;">'

        empty_html += '<div style="background:white;border:1px solid #E5E7EB;border-radius:12px;padding:24px;box-shadow:0 2px 8px rgba(0,0,0,0.04);transition:all 0.3s ease;" onmouseover="this.style.borderColor=\'#2563EB\';this.style.boxShadow=\'0 4px 16px rgba(37,99,235,0.12)\'" onmouseout="this.style.borderColor=\'#E5E7EB\';this.style.boxShadow=\'0 2px 8px rgba(0,0,0,0.04)\'">'
        empty_html += '<div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;"><div style="width:44px;height:44px;background:linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%);border-radius:10px;display:flex;align-items:center;justify-content:center;"><span style="font-size:22px;">📈</span></div><div><div style="font-size:16px;font-weight:600;color:#1E293B;">数据概览卡片</div><div style="font-size:12px;color:#6B7280;margin-top:2px;">核心指标一目了然</div></div></div>'
        empty_html += '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:16px;">'
        empty_html += '<div style="background:#F8FAFC;border-radius:8px;padding:12px;text-align:center;"><div style="font-size:20px;font-weight:700;color:#2563EB;">1,234</div><div style="font-size:11px;color:#6B7280;margin-top:4px;">总采集量</div></div>'
        empty_html += '<div style="background:#F8FAFC;border-radius:8px;padding:12px;text-align:center;"><div style="font-size:20px;font-weight:700;color:#059669;">¥89.5</div><div style="font-size:11px;color:#6B7280;margin-top:4px;">平均价格</div></div>'
        empty_html += '<div style="background:#F8FAFC;border-radius:8px;padding:12px;text-align:center;"><div style="font-size:20px;font-weight:700;color:#F59E0B;">Top3</div><div style="font-size:11px;color:#6B7280;margin-top:4px;">销量排行</div></div>'
        empty_html += '</div></div>'

        empty_html += '<div style="background:white;border:1px solid #E5E7EB;border-radius:12px;padding:24px;box-shadow:0 2px 8px rgba(0,0,0,0.04);transition:all 0.3s ease;" onmouseover="this.style.borderColor=\'#059669\';this.style.boxShadow=\'0 4px 16px rgba(5,150,105,0.12)\'" onmouseout="this.style.borderColor=\'#E5E7EB\';this.style.boxShadow=\'0 2px 8px rgba(0,0,0,0.04)\'">'
        empty_html += '<div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;"><div style="width:44px;height:44px;background:linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);border-radius:10px;display:flex;align-items:center;justify-content:center;"><span style="font-size:22px;">📉</span></div><div><div style="font-size:16px;font-weight:600;color:#1E293B;">价格趋势图</div><div style="font-size:12px;color:#6B7280;margin-top:2px;">可视化价格波动</div></div></div>'
        empty_html += '<div style="background:#F8FAFC;border-radius:8px;padding:16px;height:120px;display:flex;align-items:flex-end;justify-content:space-around;position:relative;"><svg width="100%" height="100%" style="position:absolute;top:0;left:0;"><polyline points="10,90 50,70 90,85 130,60 170,75 210,50 250,65" fill="none" stroke="#059669" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/><circle cx="10" cy="90" r="3" fill="#059669"/><circle cx="50" cy="70" r="3" fill="#059669"/><circle cx="90" cy="85" r="3" fill="#059669"/><circle cx="130" cy="60" r="3" fill="#059669"/><circle cx="170" cy="75" r="3" fill="#059669"/><circle cx="210" cy="50" r="3" fill="#059669"/><circle cx="250" cy="65" r="3" fill="#059669"/></svg></div>'
        empty_html += '</div>'

        empty_html += '<div style="background:white;border:1px solid #E5E7EB;border-radius:12px;padding:24px;box-shadow:0 2px 8px rgba(0,0,0,0.04);transition:all 0.3s ease;" onmouseover="this.style.borderColor=\'#7C3AED\';this.style.boxShadow=\'0 4px 16px rgba(124,58,237,0.12)\'" onmouseout="this.style.borderColor=\'#E5E7EB\';this.style.boxShadow=\'0 2px 8px rgba(0,0,0,0.04)\'">'
        empty_html += '<div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;"><div style="width:44px;height:44px;background:linear-gradient(135deg, #EDE9FE 0%, #DDD6FE 100%);border-radius:10px;display:flex;align-items:center;justify-content:center;"><span style="font-size:22px;">🏪</span></div><div><div style="font-size:16px;font-weight:600;color:#1E293B;">竞品分析表</div><div style="font-size:12px;color:#6B7280;margin-top:2px;">多维度对比竞品</div></div></div>'
        empty_html += '<div style="background:#F8FAFC;border-radius:8px;overflow:hidden;"><table style="width:100%;border-collapse:collapse;font-size:12px;"><thead><tr style="background:#E5E7EB;"><th style="padding:8px 10px;text-align:left;color:#374151;font-weight:600;">店铺</th><th style="padding:8px 10px;text-align:right;color:#374151;font-weight:600;">均价</th><th style="padding:8px 10px;text-align:right;color:#374151;font-weight:600;">份额</th></tr></thead><tbody>'
        empty_html += '<tr style="border-bottom:1px solid #E5E7EB;"><td style="padding:8px 10px;color:#1E293B;">旗舰店A</td><td style="padding:8px 10px;text-align:right;color:#2563EB;font-weight:600;">¥89</td><td style="padding:8px 10px;text-align:right;color:#059669;">35%</td></tr>'
        empty_html += '<tr style="border-bottom:1px solid #E5E7EB;"><td style="padding:8px 10px;color:#1E293B;">旗舰店B</td><td style="padding:8px 10px;text-align:right;color:#2563EB;font-weight:600;">¥95</td><td style="padding:8px 10px;text-align:right;color:#059669;">28%</td></tr>'
        empty_html += '<tr><td style="padding:8px 10px;color:#1E293B;">官方店C</td><td style="padding:8px 10px;text-align:right;color:#2563EB;font-weight:600;">¥78</td><td style="padding:8px 10px;text-align:right;color:#059669;">22%</td></tr>'
        empty_html += '</tbody></table></div></div>'

        empty_html += '</div></div>'

        empty_html += '<div style="margin-top:28px;text-align:center;padding:16px;background:linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);border-radius:10px;border-left:4px solid #F59E0B;">'
        empty_html += '<div style="display:flex;align-items:center;justify-content:center;gap:8px;color:#92400E;font-size:14px;font-weight:500;"><span>💡</span><span>提示：支持导出分析报告为PDF/Excel格式，方便团队协作与汇报</span></div></div>'

        empty_html += '</div>'

        st.markdown(empty_html, unsafe_allow_html=True)

        col_center = st.columns([1, 2, 1])
        with col_center[1]:
            if st.button("🚀 前往数据采集中心", type="primary", use_container_width=True,
                        key="analysis_go_to_crawl", help="跳转到数据采集页面开始采集数据"):
                st.session_state.current_page = '数据采集'
                st.rerun()

        return

    toast = get_toast()
    toast.info(f"正在分析数据集: {filename}", duration=2500)

    # ===== 数据加载后的布局预设 - B端专业版 =====
    # 顶部：数据概览卡片（总采集量、均价、销量Top3）
    st.markdown("---")
    st.subheader("📊 数据概览")

    overview_col1, overview_col2, overview_col3, overview_col4 = st.columns(4, gap="medium")

    with overview_col1:
        st.metric(label="总采集量", value=f"{len(df)} 个商品", delta="新增数据")

    with overview_col2:
        if 'price' in df.columns:
            avg_price = df['price'].mean()
            st.metric(label="平均价格", value=f"¥{avg_price:.2f}")
        else:
            st.metric(label="平均价格", value="--")

    with overview_col3:
        if 'price' in df.columns:
            max_price = df['price'].max()
            st.metric(label="最高价格", value=f"¥{max_price:.2f}")
        else:
            st.metric(label="最高价格", value="--")

    with overview_col4:
        shop_count = df['shop_name'].nunique() if 'shop_name' in df.columns else 0
        st.metric(label="店铺数量", value=f"{shop_count} 家")

    st.markdown("---")

    # 中间：可视化图表区（折线图/柱状图/饼图）
    analysis_type = st.selectbox(
        "选择分析类型",
        ["📈 价格分布分析", "🏪 品牌市场分析", "👥 消费者画像", "📋 综合报告"],
        label_visibility="visible",
        help="切换不同的数据分析维度"
    )

    if analysis_type == "📈 价格分布分析":
        analyze_price_distribution(df)

    elif analysis_type == "🏪 品牌市场分析":
        analyze_brand_market(df)

    elif analysis_type == "👥 消费者画像":
        analyze_consumer_profile(df)

    elif analysis_type == "📋 综合报告":
        generate_comprehensive_report(df)

    # 底部：明细数据表格
    st.markdown("---")
    st.subheader("📋 明细数据")

    tab_all, tab_preview = st.tabs(["全部数据", "预览前50条"])

    with tab_all:
        st.dataframe(df, use_container_width=True, height=400)

    with tab_preview:
        st.dataframe(df.head(50), use_container_width=True)


def analyze_price_distribution(df):
    """价格分布分析 - 增强版"""
    st.subheader("💰 价格分布深度分析")
    
    if 'price' not in df.columns:
        st.error("数据中缺少价格字段")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_hist = px.histogram(df, x='price', nbins=40,
                               title='价格分布直方图',
                               color_discrete_sequence=['#2563EB'])
        fig_hist.update_layout(height=400, template="plotly_white")
        fig_hist.update_traces(marker_line_color='#1E40AF', marker_line_width=1)
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        fig_box = px.box(df, y='price', title='价格箱线图',
                        color_discrete_sequence=['#7C3AED'])
        fig_box.update_layout(height=400, template="plotly_white")
        st.plotly_chart(fig_box, use_container_width=True)
    
    st.markdown("---")
    
    price_ranges = {
        '¥0-10 (大众)': (df['price'] <= 10).sum(),
        '¥11-30 (经济)': ((df['price'] > 10) & (df['price'] <= 30)).sum(),
        '¥31-60 (标准)': ((df['price'] > 30) & (df['price'] <= 60)).sum(),
        '¥61-100 (高端)': ((df['price'] > 60) & (df['price'] <= 100)).sum(),
        '¥101+ (奢侈)': (df['price'] > 100).sum()
    }
    
    range_df = pd.DataFrame(list(price_ranges.items()), columns=['价格区间', '商品数量'])
    range_df['占比 (%)'] = (range_df['商品数量'] / len(df) * 100).round(1)
    
    fig_pie = px.pie(range_df, values='商品数量', names='价格区间',
                     title='价格区间分布',
                     hole=0.4,
                     color_discrete_sequence=['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6'])
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(template="plotly_white")
    st.plotly_chart(fig_pie, use_container_width=True)
    
    st.dataframe(range_df, use_container_width=True)
    
    st.markdown("---")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("📈 Top 10 最高价商品")
        top_expensive = df.nlargest(10, 'price')[['name', 'price', 'shop_name']]
        top_expensive.index = range(1, 11)
        top_expensive.index.name = '排名'
        st.dataframe(top_expensive, use_container_width=True)
    
    with col4:
        st.subheader("💰 Top 10 最低价商品")
        top_cheap = df.nsmallest(10, 'price')[['name', 'price', 'shop_name']]
        top_cheap.index = range(1, 11)
        top_cheap.index.name = '排名'
        st.dataframe(top_cheap, use_container_width=True)


def analyze_brand_market(df):
    """品牌市场分析 - 增强版"""
    st.subheader("🏪 品牌市场深度分析")
    
    if 'shop_name' not in df.columns:
        st.error("数据中缺少店铺名称字段")
        return
    
    shop_stats = df.groupby('shop_name').agg({
        'price': ['mean', 'count', 'min', 'max']
    }).round(2)
    
    shop_stats.columns = ['平均价格', '商品数量', '最低价', '最高价']
    shop_stats = shop_stats.sort_values('商品数量', ascending=False)
    shop_stats['市场份额 (%)'] = (shop_stats['商品数量'] / len(df) * 100).round(2)
    
    top_15 = shop_stats.head(15)
    
    fig_bar = px.bar(top_15, 
                    x='商品数量', 
                    y=top_15.index,
                    orientation='h',
                    title='Top 15 店铺商品数量排行',
                    color='平均价格',
                    color_continuous_scale='Blues')
    fig_bar.update_layout(height=500, yaxis={'categoryorder': 'total ascending'}, template="plotly_white")
    st.plotly_chart(fig_bar, use_container_width=True)
    
    st.dataframe(shop_stats.head(20), use_container_width=True)
    
    st.markdown("---")
    
    flagship_shops = df[df['shop_name'].str.contains('旗舰店|官方店', na=False)]
    non_flagship = df[~df['shop_name'].str.contains('旗舰店|官方店', na=False)]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("旗舰店/官方店数量", f"{len(flagship_shops)} 个商品 ({len(flagship_shops)/len(df)*100:.1f}%)")
        if len(flagship_shops) > 0:
            st.info(f"平均价格: ¥{flagship_shops['price'].mean():.2f}")
    
    with col2:
        st.metric("其他店铺数量", f"{len(non_flagship)} 个商品 ({len(non_flagship)/len(df)*100:.1f}%)")
        if len(non_flagship) > 0:
            st.info(f"平均价格: ¥{non_flagship['price'].mean():.2f}")


def analyze_consumer_profile(df):
    """消费者画像分析 - 增强版"""
    st.subheader("👥 消费者画像深度分析")
    
    st.info("基于价格敏感度分析消费者行为特征...")
    
    if 'price' not in df.columns:
        st.error("数据中缺少价格字段")
        return
    
    price_tiers = {
        '价格敏感型': df[df['price'] <= 30],
        '品质追求型': df[(df['price'] > 30) & (df['price'] <= 80)],
        '高端消费型': df[df['price'] > 80]
    }
    
    tier_data = []
    for tier_name, tier_df in price_tiers.items():
        if len(tier_df) > 0:
            tier_data.append({
                '消费层级': tier_name,
                '商品数量': len(tier_df),
                '占比 (%)': round(len(tier_df) / len(df) * 100, 1),
                '平均价格 (¥)': round(tier_df['price'].mean(), 2),
                '价格范围': f"¥{tier_df['price'].min():.0f} - ¥{tier_df['price'].max():.0f}"
            })
    
    tier_df = pd.DataFrame(tier_data)
    
    fig_sunburst = px.sunburst(
        df,
        path=['shop_name'],
        values='price',
        title='店铺价值分布',
        color='price',
        color_continuous_scale='Viridis'
    )
    fig_sunburst.update_layout(template="plotly_white")
    st.plotly_chart(fig_sunburst, use_container_width=True)
    
    st.dataframe(tier_df, use_container_width=True)
    
    st.markdown("---")
    
    insights = []
    
    avg_price = df['price'].mean()
    median_price = df['price'].median()
    
    if median_price < avg_price * 0.8:
        insights.append("📊 **右偏分布**: 市场存在少量高价商品拉高均价，主流消费集中在中等价位")
    elif median_price > avg_price * 1.2:
        insights.append("📊 **左偏分布**: 高端产品占主导，可能为精品/进口商品市场")
    else:
        insights.append("📊 **正态分布**: 价格分布较为均衡，市场竞争充分")
    
    budget_ratio = len(df[df['price'] <= 30]) / len(df) * 100
    if budget_ratio > 40:
        insights.append(f"💡 **大众市场主导**: {budget_ratio:.1f}%的商品定价在¥30以下，适合走量策略")
    elif budget_ratio < 20:
        insights.append(f"💡 **中高端市场**: 仅{budget_ratio:.1f}%为低价商品，市场定位偏中高端")
    
    premium_ratio = len(df[df['price'] > 100]) / len(df) * 100
    if premium_ratio > 15:
        insights.append(f"🎯 **奢侈品机会**: {premium_ratio:.1f}%商品超¥100，存在高端细分市场")
    
    st.subheader("💡 关键洞察")
    for insight in insights:
        st.markdown(f"- {insight}")


def generate_comprehensive_report(df):
    """生成综合报告 - 增强版"""
    st.subheader("📋 综合分析报告")
    
    report_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    st.markdown(f"**报告生成时间**: {report_time}")
    st.markdown(f"**数据来源**: 最新采集文件")
    
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("总商品数", f"{len(df):,}")
    
    with col2:
        st.metric("平均价格", f"¥{df['price'].mean():.2f}" if 'price' in df.columns else "N/A")
    
    with col3:
        unique_shops = df['shop_name'].nunique() if 'shop_name' in df.columns else 0
        st.metric("店铺总数", f"{unique_shops:,}")
    
    with col4:
        if 'price' in df.columns:
            price_range = f"¥{df['price'].min():.0f} - ¥{df['price'].max():.0f}"
            st.metric("价格区间", price_range)
    
    st.markdown("---")
    
    report_content = f"""
    ## 📊 数据概览
    
    本次分析共涵盖 **{len(df):,}** 个食品类商品，来自 **{unique_shops:,}** 家不同店铺。
    
    """
    
    if 'price' in df.columns:
        report_content += f"""
    ### 💰 价格分析
    
    - **平均价格**: ¥{df['price'].mean():.2f}
    - **中位价格**: ¥{df['price'].median():.2f}
    - **价格标准差**: ¥{df['price'].std():.2f}
    - **最低价格**: ¥{df['price'].min():.2f}
    - **最高价格**: ¥{df['price'].max():.2f}
    
    ### 🏪 市场集中度
    
    """
        
        if 'shop_name' in df.columns:
            top5_shops = df['shop_name'].value_counts().head(5)
            cr5 = top5_shops.sum() / len(df) * 100
            
            top10_shops = df['shop_name'].value_counts().head(10)
            cr10 = top10_shops.sum() / len(df) * 100
            
            report_content += f"""
    - **CR5 (前5名店铺)**: {cr5:.1f}% - {'高度集中' if cr5 > 50 else '适度分散'}
    - **CR10 (前10名店铺)**: {cr10:.1f}% - {'高度集中' if cr10 > 70 else '适度分散'}
    
    """
    
    st.markdown(report_content)

    export_format = st.selectbox("导出格式", ["Markdown", "JSON", "CSV"])

    # 核心操作 - Primary主色填充按钮
    if st.button("导出报告", type="primary"):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = get_output_dir()
        output_dir.mkdir(exist_ok=True)
        
        if export_format == "Markdown":
            output_file = output_dir / f'analysis_report_{timestamp}.md'
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
        
        elif export_format == "JSON":
            output_file = output_dir / f'analysis_data_{timestamp}.json'
            df.to_json(output_file, orient='records', force_ascii=False, indent=2)
        
        elif export_format == "CSV":
            output_file = output_dir / f'analysis_data_{timestamp}.csv'
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        toast = get_toast()
        toast.success(f"✅ 报告已导出至: {output_file.name}")
        
        with open(output_file, 'rb') as f:
            st.download_button(
                label="下载文件",
                data=f.read(),
                file_name=output_file.name,
                mime="text/plain"
            )


def show_reports_page():
    """显示报告中心 - B端专业版 v3.0"""

    st.markdown('<h1 class="text-h1" style="display:flex;align-items:center;gap:12px;">'
                '<span>📊</span><span>报告中心</span></h1>', unsafe_allow_html=True)

    output_dir = get_output_dir()

    if not output_dir.exists() or not list(output_dir.glob('*')):
        # ===== 空状态设计 - 场景化引导 =====
        empty_html = '<div style="max-width:800px;margin:40px auto;padding:0;">'
        empty_html += '<div style="background:linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);border:1px solid #BBF7D0;border-radius:16px;padding:48px 40px;text-align:center;box-shadow:0 4px 12px rgba(34,197,94,0.08);">'
        empty_html += '<div style="width:120px;height:120px;background:linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 24px;box-shadow:0 8px 24px rgba(34,197,94,0.15);"><span style="font-size:56px;">📄</span></div>'
        empty_html += '<h2 style="font-size:24px;font-weight:700;color:#1E293B;margin-bottom:12px;line-height:1.4;">还没有生成任何报告～</h2>'
        empty_html += '<p style="font-size:15px;color:#475569;line-height:1.8;max-width:600px;margin:0 auto 28px;">完成<span style="color:#2563EB;font-weight:600;background:#DBEAFE;padding:2px 8px;border-radius:4px;">数据采集与分析</span>后，报告将自动保存在这里，包括日志文件、分析报告、导出数据等 📊</p>'
        empty_html += '</div>'

        empty_html += '<div style="margin-top:32px;background:white;border:1px solid #E5E7EB;border-radius:12px;padding:24px;box-shadow:0 2px 8px rgba(0,0,0,0.04);">'
        empty_html += '<h3 style="font-size:16px;font-weight:700;color:#1E293B;margin-bottom:20px;text-align:center;">📋 报告类型预览</h3>'
        empty_html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;">'

        empty_html += '<div style="background:#F8FAFC;border-radius:8px;padding:16px;text-align:center;"><div style="font-size:32px;margin-bottom:8px;">📝</div><div style="font-size:14px;font-weight:600;color:#1E293B;">日志文件</div><div style="font-size:12px;color:#6B7280;margin-top:4px;">.log / .txt</div></div>'
        empty_html += '<div style="background:#F8FAFC;border-radius:8px;padding:16px;text-align:center;"><div style="font-size:32px;margin-bottom:8px;">📊</div><div style="font-size:14px;font-weight:600;color:#1E293B;">分析报告</div><div style="font-size:12px;color:#6B7280;margin-top:4px;">.md / .html</div></div>'
        empty_html += '<div style="background:#F8FAFC;border-radius:8px;padding:16px;text-align:center;"><div style="font-size:32px;margin-bottom:8px;">📈</div><div style="font-size:14px;font-weight:600;color:#1E293B;">导出数据</div><div style="font-size:12px;color:#6B7280;margin-top:4px;">.xlsx / .csv</div></div>'

        empty_html += '</div></div></div>'
        st.markdown(empty_html, unsafe_allow_html=True)

        col_center = st.columns([1, 2, 1])
        with col_center[1]:
            if st.button("🚀 开始采集数据", type="primary", use_container_width=True,
                        key="reports_go_to_crawl", help="跳转到数据采集页面"):
                st.session_state.current_page = '数据采集'
                st.rerun()
        return

    all_files = [f for f in output_dir.glob('*') if f.is_file()]

    if not all_files:
        empty_html2 = '<div style="max-width:800px;margin:40px auto;padding:0;">'
        empty_html2 += '<div style="background:linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);border:1px solid #FCD34D;border-radius:16px;padding:48px 40px;text-align:center;box-shadow:0 4px 12px rgba(245,158,11,0.08);">'
        empty_html2 += '<div style="width:120px;height:120px;background:linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 24px;"><span style="font-size:56px;">📭</span></div>'
        empty_html2 += '<h2 style="font-size:24px;font-weight:700;color:#92400E;margin-bottom:12px;">输出目录为空</h2>'
        empty_html2 += '<p style="font-size:15px;color:#78350F;line-height:1.8;">尚未生成任何报告文件，请先进行数据采集操作。</p>'
        empty_html2 += '</div></div>'
        st.markdown(empty_html2, unsafe_allow_html=True)
        return

    # ===== 筛选功能区 - B端专业版 =====
    st.markdown("### 🔍 文件筛选与搜索")

    filter_col1, filter_col2, filter_col3 = st.columns([2, 2, 1], gap="medium")

    with filter_col1:
        file_types_selected = st.multiselect(
            "📁 文件类型",
            options=["日志文件 (.log/.txt)", "JSON数据 (.json)", "分析报告 (.md/.html)", "表格数据 (.csv/.xlsx)"],
            default=["日志文件 (.log/.txt)", "JSON数据 (.json)", "分析报告 (.md/.html)", "表格数据 (.csv/.xlsx)"],
            help="选择要显示的文件类型"
        )

    with filter_col2:
        search_keyword = st.text_input(
            "🔎 搜索文件名",
            placeholder="输入关键词搜索...",
            help="支持按文件名模糊搜索"
        )

    with filter_col3:
        sort_option = st.selectbox(
            "↕️ 排序方式",
            options=["按时间降序", "按时间升序", "按大小降序", "按大小升序", "按名称升序"],
            index=0,
            help="选择文件的排序方式"
        )

    # 文件过滤逻辑
    files_to_show = []
    for f in all_files:
        suffix = f.suffix.lower()
        file_type_match = False

        if "日志文件" in file_types_selected and suffix in ['.log', '.txt']:
            file_type_match = True
        elif "JSON数据" in file_types_selected and suffix == '.json':
            file_type_match = True
        elif "分析报告" in file_types_selected and suffix in ['.md', '.html']:
            file_type_match = True
        elif "表格数据" in file_types_selected and suffix in ['.csv', '.xlsx']:
            file_type_match = True

        if not file_type_match:
            continue

        if search_keyword and search_keyword.strip():
            if search_keyword.lower() not in f.name.lower():
                continue

        files_to_show.append(f)

    # 排序逻辑
    if sort_option == "按时间降序":
        files_to_show.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    elif sort_option == "按时间升序":
        files_to_show.sort(key=lambda x: x.stat().st_mtime, reverse=False)
    elif sort_option == "按大小降序":
        files_to_show.sort(key=lambda x: x.stat().st_size, reverse=True)
    elif sort_option == "按大小升序":
        files_to_show.sort(key=lambda x: x.stat().st_size, reverse=False)
    elif sort_option == "按名称升序":
        files_to_show.sort(key=lambda x: x.name.lower(), reverse=False)

    if not files_to_show:
        st.warning(f"⚠️ 没有找到符合筛选条件的文件（共 {len(all_files)} 个文件）")
        return

    # 通知提示 - 限制数量最多2条
    toast = get_toast()
    toast.info(f"找到 {len(files_to_show)} 个文件", duration=2500)

    # ===== 批量操作栏 =====
    st.markdown("---")
    batch_col1, batch_col2, batch_col3, batch_col4 = st.columns([1, 1, 1, 2])

    with batch_col1:
        select_all = st.checkbox("全选所有文件", value=False, key="select_all_reports")

    with batch_col2:
        if select_all:
            batch_download_disabled = False
        else:
            selected_count = sum(1 for i in range(len(files_to_show)) if st.session_state.get(f'report_file_{i}', False))
            batch_download_disabled = (selected_count == 0)

        batch_download = st.button(
            "📥 批量下载",
            type="secondary",
            use_container_width=True,
            disabled=batch_download_disabled,
            help=f"下载选中的文件（已选{selected_count if not select_all else len(files_to_show)}个）" if not batch_download_disabled else "请先选择文件"
        )

    with batch_col3:
        batch_delete = st.button(
            "🗑️ 批量删除",
            use_container_width=True,
            disabled=batch_download_disabled,
            help="删除选中的文件（谨慎操作）"
        )

    with batch_col4:
        st.markdown(f'<div style="padding:10px;text-align:right;color:#6B7280;font-size:13px;">'
                   f'共 <strong style="color:#2563EB;">{len(files_to_show)}</strong> 个文件 | '
                   f'总大小 <strong style="color:#059669;">{sum(f.stat().st_size for f in files_to_show) / 1024:.1f} KB</strong>'
                   f'</div>', unsafe_allow_html=True)

    st.markdown("---")

    # ===== 文件列表展示区 - 增强版 =====
    for idx, file_path in enumerate(files_to_show[:30]):
        try:
            file_size = file_path.stat().st_size
            mod_time = datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            suffix = file_path.suffix.lower()

            # 文件类型图标映射
            if suffix in ['.log', '.txt']:
                icon = '📝'
                color_tag = '#3B82F6'
                type_name = '日志文件'
            elif suffix == '.json':
                icon = '📋'
                color_tag = '#F59E0B'
                type_name = 'JSON数据'
            elif suffix in ['.md', '.html']:
                icon = '📊'
                color_tag = '#8B5CF6'
                type_name = '分析报告'
            elif suffix in ['.csv', '.xlsx']:
                icon = '📈'
                color_tag = '#059669'
                type_name = '表格数据'
            else:
                icon = '📄'
                color_tag = '#6B7280'
                type_name = '其他文件'

            # 文件卡片头部
            file_header_html = f'''
            <div style="background:linear-gradient(135deg, #F8FAFC 0%, #FFFFFF 100%);
                        border:1px solid #E5E7EB;border-left:4px solid {color_tag};
                        border-radius:10px;padding:16px 20px;margin:8px 0;
                        box-shadow:0 2px 6px rgba(0,0,0,0.04);
                        transition:all 0.3s ease;">
                <div style="display:flex;align-items:center;justify-content:space-between;">
                    <div style="display:flex;align-items:center;gap:12px;">
                        <div style="width:44px;height:44px;background:{color_tag}15;
                                    border-radius:10px;display:flex;align-items:center;
                                    justify-content:center;font-size:22px;">
                            {icon}
                        </div>
                        <div>
                            <div style="font-size:16px;font-weight:600;color:#1E293B;display:flex;align-items:center;gap:8px;">
                                {file_path.name}
                                <span style="font-size:11px;font-weight:500;background:{color_tag}20;
                                              color:{color_tag};padding:2px 8px;border-radius:4px;">
                                    {type_name}
                                </span>
                            </div>
                            <div style="font-size:13px;color:#6B7280;margin-top:4px;display:flex;gap:16px;">
                                <span>📅 {mod_time}</span>
                                <span>💾 {file_size / 1024:.2f} KB</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            '''
            st.markdown(file_header_html, unsafe_allow_html=True)

            # 选择框 + 操作按钮行
            sel_col, act_col1, act_col2, act_col3 = st.columns([0.5, 1.5, 1.5, 1.5])

            with sel_col:
                is_selected = st.checkbox("", value=st.session_state.get(f'report_file_{idx}', False),
                                          key=f'report_file_{idx}', label_visibility="collapsed")

            with act_col1:
                preview_button = st.button(f"👁️ 预览", use_container_width=True,
                                           key=f'preview_{idx}', help="在线查看文件内容")

            with act_col2:
                download_single = st.download_button(
                    label="⬇️ 下载",
                    data=open(file_path, 'rb').read(),
                    file_name=file_path.name,
                    mime="application/octet-stream",
                    use_container_width=True,
                    key=f'download_{idx}'
                )

            with act_col3:
                delete_button = st.button("🗑️ 删除", use_container_width=True,
                                         key=f'delete_{idx}', help="删除此文件（不可恢复）")

            # 预览功能实现
            if preview_button:
                if file_size < 10 * 1024 * 1024:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        if suffix == '.json':
                            try:
                                data = json.loads(content)
                                preview_content = json.dumps(data, ensure_ascii=False, indent=2)[:3000]
                            except:
                                preview_content = content[:3000]
                        else:
                            preview_content = content[:3000]

                        with st.expander(f"📂 {file_path.name} - 内容预览", expanded=True):
                            st.code(preview_content, language='json' if suffix == '.json' else None)

                        toast.success(f"✅ 已加载预览：{file_path.name}", duration=2000)

                    except Exception as e:
                        st.error(f"❌ 预览失败: {str(e)[:100]}")
                else:
                    st.warning("⚠️ 文件过大（>10MB），建议下载后本地查看")

            # 单个删除确认
            if delete_button:
                try:
                    file_path.unlink()
                    toast.success(f"🗑️ 已删除：{file_path.name}", duration=2000)
                    time.sleep(0.5)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 删除失败: {str(e)[:100]}")

        except Exception as e:
            st.error(f"❌ 读取文件出错: {str(e)[:100]}")

    # 批量下载处理
    if batch_download and (select_all or any(st.session_state.get(f'report_file_{i}', False) for i in range(len(files_to_show)))):
        import zipfile
        import io

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for idx, file_path in enumerate(files_to_show):
                if select_all or st.session_state.get(f'report_file_{idx}', False):
                    zipf.write(file_path, file_path.name)

        zip_buffer.seek(0)
        st.download_button(
            label="💾 下载打包文件",
            data=zip_buffer,
            file_name=f"reports_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            mime="application/zip",
            key="batch_download_zip"
        )
        toast.success(f"📦 已准备 {len([f for f in files_to_show if select_all or st.session_state.get(f'report_file_{files_to_show.index(f)}', False)])} 个文件用于下载", duration=3000)

    # 批量删除处理
    if batch_delete and (select_all or any(st.session_state.get(f'report_file_{i}', False) for i in range(len(files_to_show)))):
        deleted_count = 0
        for idx, file_path in enumerate(files_to_show):
            if select_all or st.session_state.get(f'report_file_{idx}', False):
                try:
                    file_path.unlink()
                    deleted_count += 1
                except:
                    pass

        if deleted_count > 0:
            toast.success(f"🗑️ 成功删除 {deleted_count} 个文件", duration=2500)
            time.sleep(0.5)
            st.rerun()
        else:
            st.warning("⚠️ 没有可删除的文件")


def show_cookie_page():
    """显示Cookie管理页面 - 增强版"""
    st.markdown('<h1 class="text-h1">🍪 Cookie 管理中心</h1>', unsafe_allow_html=True)
    
    cookie_file = get_project_root() / "cookies" / "taobao_cookies.json"
    
    st.markdown("""
    <div class="warning-box">
        <strong>🔐 Cookie说明：</strong><br>
        Cookie用于保持登录状态，避免频繁手动登录。<br>
        请勿分享Cookie文件给他人，包含您的登录凭证。
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("当前状态")
        
        if cookie_file.exists():
            mod_time = datetime.fromtimestamp(cookie_file.stat().st_mtime)
            file_size = cookie_file.stat().st_size
            
            st.success("✅ Cookie文件存在")
            st.write(f"**最后更新**: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
            st.write(f"**文件大小**: {file_size / 1024:.2f} KB")
            
            try:
                with open(cookie_file, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
                
                if isinstance(cookies, list):
                    st.write(f"**Cookie数量**: {len(cookies)} 条")
                elif isinstance(cookies, dict):
                    st.write(f"**Cookie键值对**: {len(cookies)} 个")
                    
            except Exception as e:
                st.error(f"读取Cookie失败: {e}")
        else:
            st.warning("⚠️ 未找到Cookie文件")
            st.info("请先进行登录并保存Cookie")
    
    with col2:
        st.subheader("操作选项")

        # 次要操作 - Secondary按钮
        if st.button("刷新状态", type="secondary", use_container_width=True):
            toast = get_toast()
            toast.info("正在刷新...")
            time.sleep(0.5)
            st.rerun()

        # 危险操作 - Secondary按钮（红色效果通过CSS类实现）
        if st.button("删除Cookie", type="secondary", use_container_width=True, key="delete_cookie_btn"):
            if cookie_file.exists():
                cookie_file.unlink()
                toast = get_toast()
                toast.success("✅ Cookie文件已删除")
                time.sleep(1)
                st.rerun()
            else:
                st.warning("Cookie文件不存在")
    
    st.markdown("---")
    
    st.subheader("📖 使用指南")
    
    steps = [
        ("步骤 1", "运行Cookie管理器", "在终端执行: `python cookie_manager.py`"),
        ("步骤 2", "选择手动登录", "在菜单中选择 `1. 手动登录并保存Cookie`"),
        ("步骤 3", "完成登录", "在弹出的浏览器中完成淘宝/天猫账号登录"),
        ("步骤 4", "自动保存", "登录成功后Cookie会自动保存到本地"),
        ("步骤 5", "开始使用", "返回本工具即可正常使用数据采集功能")
    ]
    
    for step_num, step_title, step_desc in steps:
        st.markdown(f"""
        <div style="
            padding: 16px; 
            margin: 8px 0; 
            background: linear-gradient(135deg, #F8FAFC 0%, #FFFFFF 100%);
            border-radius: 12px;
            border-left: 4px solid #2563EB;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        ">
            <strong style="color: #2563EB;">{step_num}: {step_title}</strong><br>
            <span style="color: #64748B;">{step_desc}</span>
        </div>
        """, unsafe_allow_html=True)

    # 核心操作 - Primary主色填充按钮
    if st.button("打开Cookie管理器", type="primary"):
        st.info("请在终端中运行: `python cookie_manager.py`")


def show_settings_page():
    """显示系统设置 - B端专业版 v3.0"""

    st.markdown('<h1 class="text-h1" style="display:flex;align-items:center;gap:12px;">'
                '<span>⚙️</span><span>系统设置</span></h1>', unsafe_allow_html=True)

    config_file = get_project_root() / "config" / "config.json"
    settings_file = get_project_root() / "settings.json"

    # ===== 1. 基本设置区 - 两列网格布局 =====
    st.markdown("### 📝 基本设置")

    basic_col1, basic_col2 = st.columns(2, gap="large")

    with basic_col1:
        default_keyword = st.text_input(
            "🔍 默认搜索关键词",
            value="食品",
            help="数据采集时的默认搜索词，可在采集页面修改"
        )

        st.markdown("")  # 间距

        default_product_count = st.number_input(
            "📦 默认采集数量",
            min_value=10,
            max_value=500,
            value=50,
            step=10,
            help="单次采集任务的商品数量上限，建议50-200以获得更好性能"
        )

    with basic_col2:
        default_review_count = st.number_input(
            "💬 默认评价数量",
            min_value=0,
            max_value=500,
            value=100,
            step=10,
            help="每个商品采集的评价数量，0表示不采集评价"
        )

        st.markdown("")  # 间距

        output_format = st.selectbox(
            "📄 输出格式",
            options=["JSON", "CSV", "Excel (.xlsx)", "全部格式"],
            index=0,
            help="选择数据导出的默认文件格式"
        )

    # ===== 2. 高级设置区 - 增强Tooltip =====
    st.markdown("---")
    st.markdown("### ⚡ 高级设置")

    adv_col1, adv_col2 = st.columns(2, gap="large")

    with adv_col1:
        headless_mode = st.checkbox(
            "🤖 默认无头模式",
            value=False,
            help="开启后，采集任务默认后台运行，不显示浏览器窗口，可提升采集效率并节省系统资源"
        )

        st.markdown("")  # 间距

        auto_save = st.checkbox(
            "💾 自动保存结果",
            value=True,
            help="开启后，采集数据自动保存到本地输出目录，无需手动导出操作"
        )

    with adv_col2:
        timeout_setting = st.slider(
            "⏱️ 请求超时时间（秒）",
            min_value=10,
            max_value=120,
            value=30,
            step=5,
            help="单个网络请求的最大等待时间，超时则自动重试，建议30-60秒以保证稳定性"
        )
        st.markdown(f'<div style="text-align:right;padding:4px 0;color:#6B7280;font-size:13px;">'
                   f'当前值: <strong style="color:#2563EB;">{timeout_setting} 秒</strong></div>',
                   unsafe_allow_html=True)

        st.markdown("")  # 间距

        retry_count = st.number_input(
            "🔄 失败重试次数",
            min_value=0,
            max_value=5,
            value=3,
            step=1,
            help="请求失败后的自动重试次数，建议2-5次以应对网络波动"
        )

    # ===== 3. 按钮与风险控制区 =====
    st.markdown("---")
    st.markdown("### 💾 设置操作")

    btn_col1, btn_col2, btn_col3 = st.columns([2, 2, 2], gap="medium")

    with btn_col1:
        save_btn = st.button(
            "✅ 保存设置",
            type="primary",
            use_container_width=True,
            help="将当前配置保存到本地文件"
        )
        if save_btn:
            settings = {
                'default_keyword': default_keyword,
                'default_product_count': default_product_count,
                'default_review_count': default_review_count,
                'output_format': output_format,
                'headless_mode': headless_mode,
                'auto_save': auto_save,
                'timeout': timeout_setting,
                'retry_count': retry_count,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            try:
                with open(settings_file, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, ensure_ascii=False, indent=2)

                toast = get_toast()
                toast.success("✅ 设置已保存成功", duration=2500)

                success_html = '<div style="background:linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);border:1px solid #059669;border-radius:10px;padding:16px;margin:12px 0;text-align:center;">'
                success_html += '<div style="font-size:16px;font-weight:600;color:#059669;display:flex;align-items:center;justify-content:center;gap:8px;"><span>✅</span><span>设置已成功保存！</span></div>'
                success_html += '<div style="font-size:13px;color:#047857;margin-top:6px;">配置已写入本地文件，下次启动将自动加载</div></div>'
                st.markdown(success_html, unsafe_allow_html=True)

                time.sleep(1)

            except Exception as e:
                st.error(f"❌ 保存失败: {str(e)[:100]}")

    with btn_col2:
        restore_btn = st.button(
            "🔄 恢复默认设置",
            use_container_width=True,
            help="将所有设置恢复为初始默认值（需确认）"
        )

        if restore_btn:
            confirm_restore = '<div style="background:linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%);border:2px solid #FCA5A5;border-radius:12px;padding:20px;margin:12px 0;">'
            confirm_restore += '<div style="display:flex;align-items:center;gap:12px;margin-bottom:14px;">'
            confirm_restore += '<span style="font-size:32px;">⚠️</span>'
            confirm_restore += '<div><strong style="font-size:17px;color:#991B1B;line-height:24px;">确定要恢复所有设置为默认值吗？</strong><br><span style="color:#7F1D1D;font-size:14px;line-height:20px;">此操作不可撤销，当前自定义配置将丢失</span></div>'
            confirm_restore += '</div></div>'
            st.markdown(confirm_restore, unsafe_allow_html=True)

            conf_rst_col1, conf_rst_col2 = st.columns(2)
            with conf_rst_col1:
                if st.button("✅ 确认恢复", type="primary", use_container_width=True):
                    if settings_file.exists():
                        settings_file.unlink()

                    toast = get_toast()
                    toast.success("🔄 已恢复默认设置", duration=2500)
                    time.sleep(0.5)
                    st.rerun()
            with conf_rst_col2:
                if st.button("❌ 取消", type="secondary", use_container_width=True):
                    st.rerun()

    with btn_col3:
        export_btn = st.button(
            "📤 导出配置",
            type="secondary",
            use_container_width=True,
            help="将当前设置导出为JSON文件，方便备份或迁移"
        )
        if export_btn and settings_file.exists():
            with open(settings_file, 'r', encoding='utf-8') as f:
                config_data = f.read()
            st.download_button(
                label="💾 下载配置文件",
                data=config_data,
                file_name=f"settings_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True,
                key="download_settings"
            )
            toast = get_toast()
            toast.info("📤 配置文件已准备下载", duration=2000)

    # ===== 4. 系统信息卡片 =====
    st.markdown("---")
    st.markdown("### 📊 系统信息")

    info_html = '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;margin:16px 0;">'

    info_items = [
        {"icon": "🐍", "label": "Python版本", "value": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}", "color": "#2563EB"},
        {"icon": "📁", "label": "工作目录", "value": str(get_project_root()).split('\\')[-1], "color": "#059669"},
        {"icon": "📄", "label": "输出文件数", "value": f"{len(list(get_output_dir().glob('*'))) if get_output_dir().exists() else 0}", "color": "#F59E0B"},
        {"icon": "💾", "label": "配置状态", "value": "已保存 ✅" if settings_file.exists() else "未配置", "color": "#8B5CF6"}
    ]

    for item in info_items:
        info_html += f'<div style="background:white;border:1px solid #E5E7EB;border-radius:10px;padding:18px;box-shadow:0 2px 6px rgba(0,0,0,0.04);">'
        info_html += f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">'
        info_html += f'<span style="font-size:22px;">{item["icon"]}</span>'
        info_html += f'<span style="font-size:13px;color:#6B7280;">{item["label"]}</span></div>'
        info_html += f'<div style="font-size:18px;font-weight:700;color:{item["color"]};">{item["value"]}</div></div>'

    info_html += '</div>'
    st.markdown(info_html, unsafe_allow_html=True)

    # ===== 5. 数据管理区 =====
    st.markdown("---")
    st.markdown("### 🗑️ 数据管理")

    clear_data = st.selectbox(
        "选择要清理的数据类型",
        options=[
            "不清理",
            "仅清理日志文件 (.log)",
            "仅清理输出数据 (JSON/CSV)",
            "清理所有临时文件",
            "清理所有数据（危险操作）"
        ],
        help="选择要清理的文件类型，谨慎选择'清理所有数据'"
    )

    if clear_data != "不清理":
        danger_color = "#DC2626" if "危险" in clear_data or "所有" in clear_data else "#F59E0B"

        warning_html = f'<div style="background:linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%);border:2px solid {danger_color};border-radius:10px;padding:16px;margin:12px 0;">'
        warning_html += f'<div style="display:flex;align-items:center;gap:10px;"><span style="font-size:24px;">⚠️</span>'
        warning_html += f'<span style="font-size:15px;font-weight:600;color:{danger_color};">即将执行: {clear_data}</span></div></div>'
        st.markdown(warning_html, unsafe_allow_html=True)

        exec_clear = st.button("🗑️ 确认执行清理", type="secondary", use_container_width=True)
        if exec_clear:
            logs_dir = get_project_root() / "logs"
            output_dir = get_output_dir()

            cleared = []

            if "日志" in clear_data and logs_dir.exists():
                for log_file in logs_dir.glob('*.log'):
                    log_file.unlink()
                    cleared.append(log_file.name)

            if "输出" in clear_data and output_dir.exists():
                for out_file in output_dir.glob('*'):
                    out_file.unlink()
                    cleared.append(out_file.name)

            if cleared:
                toast = get_toast()
                toast.success(f"🗑️ 已成功清理 {len(cleared)} 个文件", duration=2500)
                time.sleep(0.5)
                st.rerun()
            else:
                st.info("ℹ️ 没有找到需要清理的文件")

    # ===== 6. 关于模块 =====
    st.markdown("---")
    st.markdown("### ℹ️ 关于")

    about_tabs = st.tabs(["📋 版本信息", "📜 更新日志", "❓ 帮助支持"])

    with about_tabs[0]:
        about_html = '<div style="background:linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);border:1px solid #BFDBFE;border-radius:12px;padding:24px;margin:12px 0;">'
        about_html += '<div style="text-align:center;margin-bottom:20px;">'
        about_html += '<div style="width:80px;height:80px;background:linear-gradient(135deg, #2563EB 0%, #3B82F6 100%);border-radius:20px;display:inline-flex;align-items:center;justify-content:center;font-size:40px;margin-bottom:12px;">🍎</div>'
        about_html += '<div style="font-size:24px;font-weight:700;color:#1E40AF;">食品数据分析工具</div>'
        about_html += '<div style="font-size:14px;color:#3B82F6;margin-top:4px;">Food Data Analyzer v3.0</div></div>'

        about_html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-top:16px;">'
        about_html += '<div style="background:white;border-radius:8px;padding:12px;text-align:center;"><div style="font-size:12px;color:#6B7280;">版本号</div><div style="font-size:15px;font-weight:600;color:#1E293B;margin-top:4px;">v3.0.0 (Pro)</div></div>'
        about_html += '<div style="background:white;border-radius:8px;padding:12px;text-align:center;"><div style="font-size:12px;color:#6B7280;">构建日期</div><div style="font-size:15px;font-weight:600;color:#1E293B;margin-top:4px;">2026-04-12</div></div>'
        about_html += '<div style="background:white;border-radius:8px;padding:12px;text-align:center;"><div style="font-size:12px;color:#6B7280;">技术栈</div><div style="font-size:15px;font-weight:600;color:#1E293B;margin-top:4px;">Streamlit + Selenium</div></div>'
        about_html += '</div></div>'
        st.markdown(about_html, unsafe_allow_html=True)

    with about_tabs[1]:
        v1_changes = ["✨ 全新B端专业版UI设计", "🔧 数据分析工作台空状态优化", "📊 报告中心批量操作功能", "🍪 Cookie管理中心安全强化", "⚙️ 系统设置表单重构"]
        v2_changes = ["🐛 修复Toast通知堆叠问题", "⚡ 性能优化：减少页面渲染时间", "🎨 统一全局配色方案"]
        v3_changes = ["🆕 新增数据分析模块", "📈 支持价格趋势可视化", "🔄 引入响应式布局"]

        changelog_v1 = ("v3.0.0 (2026-04-12)", v1_changes)
        changelog_v2 = ("v2.5.0 (2026-03-15)", v2_changes)
        changelog_v3 = ("v2.0.0 (2026-02-01)", v3_changes)

        changelog_list = [changelog_v1, changelog_v2, changelog_v3]

        for item in changelog_list:
            version = item[0]
            changes = item[1]

            ver_html = '<div style="margin:12px 0;padding:14px;background:#F8FAFC;border-left:4px solid #2563EB;border-radius:6px;">'
            ver_html = ver_html + '<strong style="color:#1E40AF;font-size:15px;">' + str(version) + '</strong>'
            ver_html = ver_html + '<ul style="margin:8px 0 0 20px;padding:0;color:#475569;line-height:22px;">'

            for change in changes:
                ver_html = ver_html + '<li>' + str(change) + '</li>'

            ver_html = ver_html + '</ul></div>'
            st.markdown(ver_html, unsafe_allow_html=True)

    with about_tabs[2]:
        help_links = [
            {"title": "📘 使用文档", "desc": "查看完整的操作指南和功能说明", "icon": "📖"},
            {"title": "🐛 问题反馈", "desc": "提交Bug报告或功能建议", "icon": "💬"},
            {"title": "💬 社区交流", "desc": "加入用户群组讨论使用心得", "icon": "👥"},
            {"title": "📧 联系开发者", "desc": "获取技术支持和定制服务", "icon": "✉️"}
        ]

        for link in help_links:
            link_html = f'<div style="background:white;border:1px solid #E5E7EB;border-radius:8px;padding:16px;margin:10px 0;display:flex;align-items:center;gap:14px;cursor:pointer;transition:all 0.3s;" onmouseover="this.style.borderColor=\'#2563EB\';this.style.boxShadow=\'0 4px 12px rgba(37,99,235,0.1)\'" onmouseout="this.style.borderColor=\'#E5E7EB\';this.style.boxShadow=\'none\'">'
            link_html += f'<div style="width:44px;height:44px;background:#DBEAFE;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:22px;">{link["icon"]}</div>'
            link_html += f'<div style="flex:1;"><div style="font-size:15px;font-weight:600;color:#1E293B;">{link["title"]}</div><div style="font-size:13px;color:#6B7280;margin-top:2px;">{link["desc"]}</div></div>'
            link_html += '</div>'
            st.markdown(link_html, unsafe_allow_html=True)


def show_help_page():
    """显示帮助页面 - 增强版"""
    st.markdown('<h1 class="text-display">📖 使用帮助中心</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    ## 🍎 食品电商AI分析工具 - 用户指南
    
    ### 🎯 工具简介
    
    本工具是一款专业的食品电商数据分析平台，可以帮助您：
    - 🔍 **智能采集**: 从天猫/淘宝平台自动采集食品类商品数据
    - 📊 **深度分析**: 多维度分析价格、品牌、市场趋势
    - 📈 **可视化展示**: 直观的图表和数据报表
    - 🤖 **AI赋能**: 利用人工智能进行情感分析和OCR识别
    
    ---
    
    ### 🚀 快速开始
    
    #### 第一次使用？
    
    1. **配置Cookie** (必须)
       - 点击左侧菜单的「Cookie管理」
       - 运行Cookie管理器完成登录
       - 登录成功后自动保存登录状态
    
    2. **测试采集**
       - 进入「数据采集」页面
       - 点击「🧪 测试模式」按钮
       - 验证配置是否正确
    
    3. **正式采集**
       - 设置采集参数（关键词、数量等）
       - 点击「🚀 开始采集」
       - 等待采集完成
    
    4. **查看分析**
       - 进入「数据分析」查看详细统计
       - 在「报告中心」下载历史报告
    
    ---
    
    ### 📋 功能说明
    
    | 功能模块 | 说明 |
    |---------|------|
    | 📊 数据概览 | 查看采集数据的整体情况 |
    | 📥 数据采集 | 配置参数并启动爬虫 |
    | 🔍 数据分析 | 多维度深度分析 |
    | 📊 报告中心 | 查看/下载历史报告 |
    | 🍪 Cookie管理 | 管理登录状态 |
    | ⚙️ 系统设置 | 配置和偏好设置 |
    
    ---
    
    ### ⚠️ 常见问题
    
    **Q: 为什么需要Cookie？**
    A: 天猫/淘宝有反爬机制，Cookie可以模拟真实用户访问，提高采集成功率。
    
    **Q: 采集速度慢怎么办？**
    A: 为了避免被封禁，程序会模拟人类操作节奏。建议：
       - 减少采集数量
       - 使用无头模式
       - 分时段多次采集
    
    **Q: 出现错误如何处理？**
    A: 
       1. 检查网络连接
       2. 更新Cookie（可能已过期）
       3. 查看错误日志
       4. 联系技术支持
    
    ---
    
    ### 🔧 技术支持
    
    如遇问题，请检查：
    - Python版本 >= 3.8
    - 所有依赖已正确安装 (`pip install -r requirements.txt`)
    - 浏览器驱动已配置 (Edge/Chrome)
    
    """)
    
    st.markdown("---")

    st.subheader("快捷操作")

    quick_col1, quick_col2, quick_col3 = st.columns(3)

    with quick_col1:
        # 核心操作 - Primary按钮
        if st.button("前往采集", type="primary", use_container_width=True):
            st.session_state.current_page = "数据采集"
            st.rerun()

    with quick_col2:
        # 次要操作 - Secondary按钮
        if st.button("查看分析", type="secondary", use_container_width=True):
            st.session_state.current_page = "数据分析"
            st.rerun()

    with quick_col3:
        # 次要操作 - Secondary按钮
        if st.button("管理Cookie", type="secondary", use_container_width=True):
            st.session_state.current_page = "Cookie管理"
            st.rerun()


def main():
    """主函数"""
    # 初始化 session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "数据概览"
    
    # 渲染侧边栏
    create_modern_sidebar()
    
    # 页面路由映射
    pages = {
        "数据概览": show_main_page,
        "数据采集": show_crawl_page,
        "数据分析": show_analysis_page,
        "报告中心": show_reports_page,
        "Cookie管理": show_cookie_page,
        "系统设置": show_settings_page,
        "使用帮助": show_help_page
    }

    # 渲染当前页面（先渲染页面，让toast.info()等操作执行）
    current_page = st.session_state.current_page
    if current_page in pages:
        pages[current_page]()
    else:
        show_main_page()

    # 渲染 Toast 通知容器（必须在页面渲染之后，确保所有toast都已添加）
    render_toasts()

    # ===== 4. 底部信息栏优化 - 可折叠设计 =====
    st.markdown("---")
    
    # 使用Streamlit的expander实现可折叠
    with st.expander("ℹ️ 系统信息 & 版本详情", expanded=False):
        
        col_info1, col_info2, col_info3 = st.columns(3)
        
        with col_info1:
            st.metric("Python版本", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        
        with col_info2:
            st.metric("工作目录", str(get_project_root()).split('\\')[-1])
        
        with col_info3:
            output_dir = get_output_dir()
            if output_dir.exists():
                file_count = len(list(output_dir.glob('*')))
                st.metric("输出文件数", file_count)
            else:
                st.metric("输出文件数", 0)
        
        st.markdown("---")
        
        # 品牌信息（紧凑版）
        st.markdown("""
        <div style="text-align:center;padding:12px;background:linear-gradient(135deg,#F8FAFC 0%,#F1F5F9 100%);
                    border-radius:8px;border:1px solid #E2E8F0;margin-top:8px;">
            <strong style="color:#2563EB;font-size:15px;">🍎 Food Analyzer v3.0 Pro</strong><br>
            <small style="color:#64748B;">Powered by AI | Built with ❤️ | © 2026</small>
        </div>
        """, unsafe_allow_html=True)
    
    # 检查是否需要刷新（实现单次点击切换）
    if st.session_state.get('needs_rerun', False):
        # 先重置标志位
        st.session_state.needs_rerun = False
        # 然后触发刷新
        st.rerun()


if __name__ == "__main__":
    main()
