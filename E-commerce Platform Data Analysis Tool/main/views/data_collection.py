"""
Page 1: 数据采集中心 - 稳定版
智能爬虫控制台 | 实时登录模式 | 状态机架构
"""

import streamlit as st
import pandas as pd
import json
import os
import sys
import random
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from components import (
    get_toast,
    render_progress_with_steps
)


def get_project_root():
    return Path(__file__).parent.parent


def get_output_dir():
    return get_project_root() / "output"


# ===== 状态常量 =====
STATE_IDLE = "idle"
STATE_BROWSER_OPEN = "browser_open"
STATE_LOGIN_CONFIRMED = "login_confirmed"
STATE_CRAWLING = "crawling"
STATE_COMPLETE = "complete"


def render():
    """显示数据采集中心 - 基于状态机的稳定版"""
    
    # ===== 页面UI =====
    st.title("📥 数据采集中心")
    st.info("💡 **使用提示**：点击下方按钮后，系统会自动打开浏览器等待您登录淘宝账号")
    
    # 添加CSS样式：隐藏滑块原生数值标签
    st.markdown("""
    <style>
    /* 隐藏slider的原生数值显示 */
    div[data-testid="stSlider"] > div > div > label > div {
        display: none !important;
    }
    
    /* 优化slider整体布局 */
    div[data-testid="stSlider"] {
        margin-top: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 参数配置区
    st.subheader("⚙️ 采集参数配置")
    
    col1, col2 = st.columns(2)
    with col1:
        keyword = st.text_input("🔍 搜索关键词", value="食品")
    with col2:
        product_count = st.slider(
            "📦 采集商品数量",
            min_value=10,
            max_value=200,
            value=50,
            step=10,
            help="单次采集的商品总数",
            label_visibility="visible"
        )
        # 在滑块下方显示当前值
        st.caption(f"当前选择: **{product_count}** 个商品")
    
    col3, col4 = st.columns(2)
    with col3:
        review_count = st.number_input("📝 每商品评价数量", 0, 500, 100, 10)
    with col4:
        headless = st.checkbox("🔇 无头模式", value=False)
    
    st.markdown("---")
    
    # 操作按钮
    button_col1, button_col2, button_col3 = st.columns([2.5, 2, 1.5])
    
    with button_col1:
        start_button = st.button("🚀 开始采集", type="primary", use_container_width=True)
    
    with button_col2:
        test_button = st.button("🧪 测试模式", type="secondary", use_container_width=True)
    
    with button_col3:
        stop_button = st.button("⏹️ 重置", type="secondary", use_container_width=True)
    
    # ===== 重置按钮处理 =====
    if stop_button:
        _cleanup_session()
        st.rerun()
    
    # ===== 初始化状态 =====
    current_state = st.session_state.get('crawl_state', STATE_IDLE)
    
    # ===== 状态转换逻辑 =====
    
    # 转换：IDLE -> BROWSER_OPEN
    if (start_button or test_button) and current_state == STATE_IDLE:
        is_test_mode = bool(test_button)
        
        st.session_state.crawl_state = STATE_BROWSER_OPEN
        st.session_state.is_test_mode = is_test_mode
        st.session_state.crawl_params = {
            'keyword': keyword,
            'product_count': product_count,
            'review_count': review_count,
            'headless': headless
        }
        st.rerun()
    
    # 根据当前状态执行对应逻辑
    if current_state == STATE_IDLE:
        _render_idle_state()
    
    elif current_state == STATE_BROWSER_OPEN:
        _handle_browser_open_state(keyword, product_count, headless)
    
    elif current_state == STATE_LOGIN_CONFIRMED:
        _handle_login_confirmed_state()
    
    elif current_state in [STATE_CRAWLING, STATE_COMPLETE]:
        st.success("✅ 采集任务已完成或正在进行中")


def _cleanup_session():
    """清理所有session状态"""
    keys_to_clean = [
        'crawler_instance', 'crawl_state', 'is_test_mode',
        'crawl_params', 'waiting_for_login'
    ]
    for key in keys_to_clean:
        if key in st.session_state:
            del st.session_state[key]


def _render_idle_state():
    """渲染空闲状态的提示"""
    st.caption("💡 请点击上方按钮开始数据采集任务")


def _create_browser(headless: bool):
    """创建并初始化浏览器实例"""
    from crawlers.tmall_crawler_selenium import TmallCrawlerSelenium
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    steps = [
        {"label": "初始化", "icon": "⚙️"},
        {"label": "打开浏览器", "icon": "🌐"},
        {"label": "等待登录", "icon": "🔐"},
        {"label": "搜索商品", "icon": "🔍"},
        {"label": "保存结果", "icon": "💾"}
    ]
    
    try:
        render_progress_with_steps(steps, current_step=0)
        status_text.info("⏳ 正在初始化爬虫系统...")
        
        crawler = TmallCrawlerSelenium(headless=headless)
        
        render_progress_with_steps(steps, current_step=1)
        status_text.text("🔄 正在启动浏览器...")
        progress_bar.progress(5)
        
        render_progress_with_steps(steps, current_step=2)
        status_text.warning("🔐 正在打开淘宝登录页面...")
        progress_bar.progress(10)
        
        crawler.open_page("https://login.taobao.com/")
        
        status_text.text("⏳ 等待页面加载完成...")
        time.sleep(3)
        
        try:
            crawler.simulate_mouse_movement()
            crawler.human_like_wait(1, 2)
            crawler.simulate_scrolling('down', random.randint(100, 300))
        except:
            pass
        
        max_retries = 2
        for retry in range(max_retries + 1):
            try:
                page_source = crawler.driver.page_source
                is_blank = len(page_source.strip()) < 500 or 'about:blank' in crawler.driver.current_url
                
                if is_blank:
                    if retry < max_retries:
                        status_text.warning(f"⚠️ 页面异常，正在刷新... (第{retry + 1}次)")
                        crawler.driver.refresh()
                        time.sleep(3)
                    else:
                        status_text.error("❌ 页面加载失败，请手动刷新浏览器")
                else:
                    break
            except Exception as e:
                if retry < max_retries:
                    time.sleep(2)
                else:
                    break
        
        progress_bar.progress(15)
        status_text.success("✅ 登录页面已准备就绪！")
        
        st.session_state.crawler_instance = crawler
        
        return True, None
        
    except Exception as e:
        error_msg = f"初始化失败: {str(e)}"
        status_text.error(f"❌ {error_msg}")
        import traceback
        st.error(traceback.format_exc())
        _cleanup_session()
        return False, error_msg


def _handle_browser_open_state(keyword, product_count, headless):
    """处理浏览器已打开状态（等待登录）"""
    
    progress_bar = st.progress(15)
    status_text = st.empty()
    
    # 检查/创建浏览器实例
    crawler = st.session_state.get('crawler_instance')
    
    if crawler is None:
        success, error = _create_browser(headless)
        if not success:
            st.session_state.crawl_state = STATE_IDLE
            st.stop()
        crawler = st.session_state.get('crawler_instance')
    
    # 验证浏览器是否可用
    try:
        browser_url = crawler.driver.current_url
        st.caption(f"📍 当前浏览器地址: `{browser_url}`")
    except Exception as e:
        st.warning("⚠️ 浏览器会话已失效，正在重新启动...")
        _cleanup_session()
        st.session_state.crawl_state = STATE_IDLE
        st.rerun()
    
    # 显示登录等待界面
    st.warning("""
    🌐 **浏览器已打开！** 请在弹出的Edge浏览器窗口中完成以下操作：
    1. 使用**扫码登录**或**账号密码**登录淘宝/天猫
    2. 登录成功后，返回此页面点击下方的确认按钮
    
    ⚠️ **重要提示**：
    - 请勿手动关闭浏览器窗口
    """)
    
    confirm_login = st.button(
        "✅ 我已完成登录，继续采集",
        type="primary",
        use_container_width=True,
        key="confirm_login_btn"
    )
    
    if not confirm_login:
        status_text.warning("⏸️ 等待您完成登录...请在浏览器中登录后点击上方按钮")
        st.stop()
    
    # 用户点击确认 -> 转换状态
    st.session_state.crawl_state = STATE_LOGIN_CONFIRMED
    st.success("✅ 登录确认成功！正在准备数据采集...")
    st.rerun()


def _handle_login_confirmed_state():
    """处理登录已确认状态（执行采集）"""
    
    params = st.session_state.get('crawl_params', {})
    is_test_mode = st.session_state.get('is_test_mode', False)
    
    count = 10 if is_test_mode else params.get('product_count', 50)
    keyword = params.get('keyword', '食品')
    
    crawler = st.session_state.get('crawler_instance')
    
    if crawler is None:
        st.error("❌ 浏览器实例丢失，请重新开始")
        _cleanup_session()
        st.session_state.crawl_state = STATE_IDLE
        st.rerun()
    
    progress_bar = st.progress(20)
    status_text = st.empty()
    log_container = st.container()
    
    steps = [
        {"label": "初始化", "icon": "⚙️"},
        {"label": "打开浏览器", "icon": "🌐"},
        {"label": "等待登录", "icon": "🔐"},
        {"label": "搜索商品", "icon": "🔍"},
        {"label": "保存结果", "icon": "💾"}
    ]
    
    toast = get_toast()
    toast.success("🎉 开始搜索商品...")
    
    render_progress_with_steps(steps, current_step=3)
    status_text.text("🔍 正在搜索商品...")
    progress_bar.progress(25)
    
    try:
        products = crawler.search_products(
            keyword=keyword,
            max_products=count
        )
        
        progress_bar.progress(80)
        
        if products:
            render_progress_with_steps(steps, current_step=4)
            
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
                
                if is_test_mode:
                    output_file = output_dir / f'test_crawl_{timestamp}.json'
                else:
                    output_file = output_dir / f'intelligent_crawl_{timestamp}.json'
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'timestamp': timestamp,
                        'keyword': keyword,
                        'products': products,
                        'count': len(products),
                        'login_mode': 'realtime'
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
            toast.error("未采集到任何商品，请重新登录后重试")
            status_text.error("❌ 未采集到任何商品")
            progress_bar.progress(100)
        
        # 关闭浏览器并清理
        try:
            crawler.close()
        except:
            pass
        
        _cleanup_session()
        st.session_state.crawl_state = STATE_COMPLETE
        
    except Exception as e:
        toast.error(f"采集过程出错: {str(e)}")
        status_text.error(f"❌ 采集过程出错: {str(e)}")
        import traceback
        with log_container:
            st.error(traceback.format_exc())
        
        try:
            crawler.close()
        except:
            pass
        _cleanup_session()
        st.session_state.crawl_state = STATE_IDLE


@st.cache_data(ttl=300)
def load_latest_data():
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
        return None, None
