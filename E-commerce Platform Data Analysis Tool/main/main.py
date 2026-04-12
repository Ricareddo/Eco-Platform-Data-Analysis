"""
🍎 电商平台数据分析工具 - 电商数据分析系统
主入口文件 | Streamlit可视化界面 | 对标电商后台分层设计

版本: 3.0 Pro (Modern UI Edition)
架构:
  - pages/: 6个核心页面模块
  - utils/: 工具集（采集、可视化、配置）
  - components/: UI组件库
  - crawlers/: 爬虫引擎
  - database/: 数据持久化
  - analyzers/: AI分析模块

运行方式:
  - GUI模式: streamlit run main.py
  - CLI模式: python main.py --mode full/crawl/analyze/report/test
"""

import sys
import io
import os

# Windows中文乱码解决方案（仅在非Streamlit环境下执行）
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, Exception):
        # Streamlit环境下stdout已被处理，跳过重定向
        pass

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import argparse
import logging
from pathlib import Path
from datetime import datetime


def setup_logging():
    """配置日志系统"""
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)


def run_cli_mode(args):
    """运行命令行模式（保留原有功能）"""
    logger = setup_logging()
    
    print("\n" + "="*70)
    print("   电商平台数据分析工具 v1.0 (CLI Mode)")
    print("="*70 + "\n")

    try:
        from config.config_manager import ConfigManager
        from database.db_manager import DatabaseManager
        from analyzers.report_generator import ReportGenerator

        config_manager = ConfigManager()
        config = config_manager.load()
        db = DatabaseManager()

        if args.mode == 'test':
            print("\n🧪 测试模式：使用模拟数据演示完整流程")
            print("-" * 50)
            
            try:
                from utils.test_data_generator import TestDataGenerator
                
                generator = TestDataGenerator()
                result = generator.populate_database(
                    db, 
                    product_count=args.test_count, 
                    reviews_per_product=args.reviews
                )
                
                print(f"\n✅ 测试数据生成完成！")
                print(f"   商品数: {result['products']}")
                print(f"   评价数: {result['reviews']}")
            except ImportError:
                print("⚠️ 测试数据生成器未找到，跳过")

        if args.mode in ['full', 'crawl']:
            print("\n📥 阶段 1/3: 数据采集")
            print("-" * 50)
            
            from crawlers.tmall_crawler_selenium import TmallCrawlerSelenium
            
            with TmallCrawlerSelenium(headless=args.headless) as crawler:
                products = crawler.crawl_top_brands(
                    category="食品",
                    top_n=args.products
                )
                
                for product in products:
                    brand_id = db.insert_brand(
                        name=product.get('shop_name', '未知品牌'),
                        platform="天猫",
                        category="食品"
                    )
                    product['brand_id'] = brand_id
                    
                    product_id = db.insert_product(product)
                    product['id'] = product_id
                
                print(f"\n✅ 数据采集完成！共获取 {len(products)} 个商品")

                if products and args.reviews > 0:
                    print(f"\n📝 开始采集评价（每商品最多 {args.reviews} 条）...")
                    reviews_data = crawler.crawl_reviews_batch(
                        products, 
                        max_reviews_per_product=args.reviews
                    )
                    
                    for review in reviews_data:
                        review['product_id'] = review.pop('product_id_temp', None)
                        db.insert_review(review)
                    
                    print(f"✅ 评价采集完成！共获取 {len(reviews_data)} 条评价")

        if args.mode in ['full', 'analyze', 'test']:
            print("\n🔍 阶段 2/3: AI分析")
            print("-" * 50)
            
            from analyzers.ocr_processor import OCRProcessor
            from analyzers.sentiment_analyzer import SentimentAnalyzer
            
            ocr_config = config.get('ocr')
            llm_config = config.get('llm')
            
            if ocr_config and all(ocr_config.values()):
                print("\n[1/2] OCR识别配料表和营养成分表...")
                ocr = OCRProcessor(ocr_config)
                ocr.process_all_products(db)
                print("✅ OCR识别完成")
            else:
                print("⚠️  未配置OCR，跳过图片识别")
            
            if llm_config and llm_config.get('api_key'):
                print("\n[2/2] 情感分析用户评价...")
                analyzer = SentimentAnalyzer(llm_config)
                analyzer.analyze_all_reviews(db)
                print("✅ 情感分析完成")
            else:
                print("⚠️  未配置大模型API，跳过情感分析")

        if args.mode in ['full', 'report', 'test']:
            print("\n📊 阶段 3/3: 生成报告")
            print("-" * 50)
            
            report_gen = ReportGenerator(db)
            report_gen.generate()
            
            stats = db.get_statistics()
            print(f"\n📈 统计摘要:")
            print(f"   商品总数: {stats.get('total_products', 0)}")
            print(f"   评价总数: {stats.get('total_reviews', 0)}")
            print(f"   品牌数量: {stats.get('total_brands', 0)}")
            print(f"   平均评分: {stats.get('avg_rating', 0)}")

        db.close()
        
        print("\n" + "="*70)
        print("   ✅ 全部流程执行完成！")
        print("="*70 + "\n")

    except KeyboardInterrupt:
        print("\n\n❌ 用户中断程序")
        sys.exit(1)
    except Exception as e:
        logger.error(f"程序运行出错: {e}", exc_info=True)
        print(f"\n❌ 程序出错: {e}")
        sys.exit(1)


def load_global_styles():
    """加载全局 CSS 样式（保持原有设计不变）"""
    styles_path = Path(__file__).parent / "styles" / "global.css"
    
    if styles_path.exists():
        with open(styles_path, 'r', encoding='utf-8') as f:
            custom_css = f.read()
        
        st.markdown(f'<style>{custom_css}</style>', unsafe_allow_html=True)
    else:
        # 内联核心样式（备用）
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
        
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, var(--gray-100) 0%, var(--gray-50) 100%) !important;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        </style>
        """, unsafe_allow_html=True)


def create_modern_sidebar():
    """创建现代化侧边栏导航（保持原有设计不变）"""
    
    # Logo 和标题区域
    st.sidebar.markdown("""
    <div class="sidebar-header">
        <div class="logo-container">
            <div class="logo-text">
                <h1>电商平台数据分析工具</h1>
                <p>AI-Powered Analytics v3.0</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    # 导航菜单 - 简洁版（无图标）
    pages = [
        {"label": "数据概览", "key": "dashboard"},
        {"label": "数据采集", "key": "crawl"},
        {"label": "数据分析", "key": "analysis"},
        {"label": "报告中心", "key": "reports"},
        {"label": "Cookie管理", "key": "cookie"},
        {"label": "系统设置", "key": "settings"},
        {"label": "使用帮助", "key": "help"}
    ]
    
    page_labels = [page["label"] for page in pages]
    
    # 获取当前选中的索引
    current_index = 0
    if 'current_page' in st.session_state and st.session_state.current_page in page_labels:
        current_index = page_labels.index(st.session_state.current_page)
    
    # 动态key机制：确保程序化导航后radio组件能正确更新选中状态
    # 原理：通过改变key强制Streamlit重新创建radio组件，使其读取新的index值
    if 'nav_version' not in st.session_state:
        st.session_state.nav_version = 0
    
    # 检测是否发生了程序化导航（current_page被外部改变）
    # 通过比较当前current_page和上次radio选择值来判断
    if 'last_radio_selection' not in st.session_state:
        st.session_state.last_radio_selection = page_labels[0]  # 默认值
    
    radio_key = f"sidebar_navigation_v{st.session_state.nav_version}"
    
    # 使用 radio 组件实现导航
    selection = st.sidebar.radio(
        "导航菜单",
        page_labels,
        label_visibility="collapsed",
        index=current_index,
        key=radio_key
    )
    
    # 更新当前页面状态
    pending_nav = st.session_state.get('pending_navigation', None)
    
    if pending_nav and pending_nav in page_labels:
        # 情况1: 有显式的程序化跳转请求（通过pending_navigation）
        st.session_state.current_page = pending_nav
        st.session_state.pending_navigation = None  # 清除标记
        # 增加版本号，下次渲染时会用新的key创建radio组件
        st.session_state.nav_version += 1
    elif (st.session_state.current_page != selection and 
          st.session_state.current_page != st.session_state.last_radio_selection):
        # 情况2: current_page被外部改变（如快捷操作按钮），且不是来自radio的上次选择
        # 这说明是程序化导航，需要更新版本号以同步radio状态
        st.session_state.nav_version += 1
    else:
        # 情况3: 用户手动点击侧边栏，使用 radio 的选择
        if st.session_state.current_page != selection:
            st.session_state.current_page = selection
    
    # 记录本次radio的选择值，用于下次判断
    st.session_state.last_radio_selection = selection
    
    # 标记页面是否变更
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
        <small style="opacity: 0.6;">© 2026 电商数据分析</small>
    </div>
    """, unsafe_allow_html=True)


def main():
    """
    主函数 - Streamlit GUI模式（默认）
    
    运行方式: streamlit run main.py
    """
    
    # ===== 页面配置 =====
    st.set_page_config(
        page_title="电商平台数据分析工具 | 电商数据分析系统",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={}
    )
    
    # 加载全局样式系统
    load_global_styles()
    
    # 侧边栏专项优化样式（保持原有设计 - 仅隐藏折叠按钮）
    st.markdown("""
    <style>
    /* 侧边栏优化 - 强制常驻展开 */
    [data-testid="stSidebar"] {
        width: 320px !important;
        min-width: 320px !important;
        max-width: 320px !important;
        position: relative !important;
        transform: none !important;
        transition: none !important;
    }

    [data-testid="stSidebar"] > div {
        width: 320px !important;
        min-width: 320px !important;
        transform: none !important;
    }

    /* ====== 精准隐藏折叠按钮（不影响其他按钮）===== */

    /* 仅针对已知的折叠控件选择器 */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarNavCollapse"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
        position: absolute !important;
        left: -99999px !important;
        top: -99999px !important;
        width: 0 !important;
        height: 0 !important;
        overflow: hidden !important;
        z-index: -9999 !important;
    }

    /* 禁止侧边栏收缩动画和变换 */
    @keyframes sidebar-animation {
        from { transform: translateX(0); }
        to { transform: translateX(0); }
    }

    [data-testid="stSidebar"] {
        animation: none !important;
        left: 0 !important;
        right: auto !important;
        transform: none !important;
        transition-property: none !important;
    }

    [data-testid="stSidebar"]:hover {
        transform: none !important;
    }

    /* 确保侧边栏内容始终可见且不可收缩 */
    [data-testid="stSidebar"] [class*="content"],
    [data-testid="stSidebar"] main,
    [data-testid="stSidebar"] section {
        opacity: 1 !important;
        visibility: visible !important;
        display: block !important;
        overflow: visible !important;
        max-width: none !important;
        min-width: 100% !important;
    }

    /* 导航菜单项样式 */
    .stRadio [role="radiogroup"] {
        gap: 8px !important;
        display: flex !important;
        flex-direction: column !important;
    }

    .stRadio [role="radio"] {
        background: transparent !important;
        border: 2px solid transparent !important;
        border-radius: 12px !important;
        padding: 16px 20px !important;
        margin: 4px 0 !important;
        font-size: 16px !important;
        font-weight: 500 !important;
        transition: all 0.25s ease-in-out !important;
        cursor: pointer !important;
        min-height: 56px !important;
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

    /* Logo区域 */
    .sidebar-header {
        padding: 32px 24px !important;
        margin: -20px -20px 24px -20px !important;
    }

    .logo-icon {
        font-size: 3rem !important;
    }

    .version-info {
        padding: 24px 20px !important;
        margin-top: 32px !important;
    }

    /* 确保所有普通按钮可点击 */
    .stButton > button,
    button:not([data-testid="collapsedControl"]):not([data-testid="stSidebarNavCollapse"]) {
        pointer-events: auto !important;
        cursor: pointer !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 初始化 session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "数据概览"
    
    # 渲染侧边栏
    create_modern_sidebar()
    
    # ===== 页面路由映射（使用新的pages模块）=====
    pages_router = {
        "数据概览": ("dashboard", "render"),
        "数据采集": ("data_collection", "render"),
        "数据分析": ("data_analysis", "render"),
        "报告中心": ("report_center", "render"),
        "Cookie管理": ("cookie_management", "render"),
        "系统设置": ("system_settings", "render"),
        "使用帮助": ("help_guide", "render")
    }
    
    # 渲染当前页面
    current_page = st.session_state.current_page
    
    if current_page in pages_router:
        module_name, render_func = pages_router[current_page]
        
        try:
            # 动态导入并渲染页面模块
            module = __import__(f'views.{module_name}', fromlist=[render_func])
            page_renderer = getattr(module, render_func)
            page_renderer()
            
        except Exception as e:
            st.error(f"❌ 页面加载失败: {str(e)}")
            st.error("请检查项目结构是否完整")
    else:
        # 默认显示仪表盘
        from views.dashboard import render as show_dashboard
        show_dashboard()
    
    # 渲染 Toast 通知容器
    try:
        from components import render_toasts
        render_toasts()
    except:
        pass
    
    # 底部信息栏
    st.markdown("---")
    
    with st.expander("ℹ️ 系统信息 & 版本详情", expanded=False):
        col_info1, col_info2, col_info3 = st.columns(3)
        
        with col_info1:
            st.metric("Python版本", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        
        with col_info2:
            st.metric("工作目录", str(Path(__file__).parent).split('\\')[-1])
        
        with col_info3:
            output_dir = Path(__file__).parent / "output"
            if output_dir.exists():
                file_count = len(list(output_dir.glob('*')))
                st.metric("输出文件数", file_count)
            else:
                st.metric("输出文件数", 0)
        
        st.markdown("---")
        
        st.markdown("""
        <div style="text-align:center;padding:12px;background:linear-gradient(135deg,#F8FAFC 0%,#F1F5F9 100%);
                    border-radius:8px;border:1px solid #E2E8F0;margin-top:8px;">
            <strong style="color:#2563EB;font-size:15px;">电商平台数据分析工具 v3.0 Pro</strong><br>
            <small style="color:#64748B;">Powered by AI | Built with ❤️ | © 2026</small>
        </div>
        """, unsafe_allow_html=True)
    
    # 检查是否需要刷新（实现单次点击切换）
    if st.session_state.get('needs_rerun', False):
        st.session_state.needs_rerun = False
        st.rerun()

    # ===== 精准移除折叠按钮（仅针对特定元素）=====
    st.markdown("""
    <script>
    // 仅移除已知的折叠按钮，不影响其他功能按钮
    function removeCollapseButtons() {
        try {
            // 只选择明确的折叠控件
            const collapseButtons = document.querySelectorAll(
                '[data-testid="collapsedControl"], ' +
                '[data-testid="stSidebarNavCollapse"]'
            );

            collapseButtons.forEach(el => {
                if (el) {
                    el.style.display = 'none';
                    el.style.visibility = 'hidden';
                    el.style.pointerEvents = 'none';
                    console.log('✅ 已隐藏折叠按钮');
                }
            });
        } catch (e) {
            console.log('折叠按钮处理完成');
        }
    }

    // 延迟执行一次即可
    setTimeout(removeCollapseButtons, 500);
    setTimeout(removeCollapseButtons, 1000);

    console.log('🚀 折叠按钮隐藏脚本已启动（精准模式）');
    </script>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    try:
        # 检测运行模式（仅在非Streamlit环境下执行）
        parser = argparse.ArgumentParser(description='电商平台数据分析工具')
        parser.add_argument('--mode', choices=['full', 'crawl', 'analyze', 'report', 'test'], 
                           default=None, help='CLI运行模式（不指定则启动GUI）')
        parser.add_argument('--headless', action='store_true', help='无头浏览器模式')
        parser.add_argument('--products', type=int, default=50, help='采集商品数量')
        parser.add_argument('--reviews', type=int, default=100, help='每商品评价数量')
        parser.add_argument('--test-count', type=int, default=10, help='测试模式商品数量')
        args = parser.parse_args()
        
        # 如果指定了mode参数，使用CLI模式；否则启动GUI
        if args.mode:
            run_cli_mode(args)
        else:
            # Streamlit会自动调用main()函数
            main()
    except (ValueError, SystemExit):
        # Streamlit环境下的兼容性处理
        main()
