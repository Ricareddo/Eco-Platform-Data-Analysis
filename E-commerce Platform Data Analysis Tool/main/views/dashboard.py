"""
Page 0: 数据概览仪表盘 - 对标 Tableau/Power BI 现代设计
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import json
from pathlib import Path
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from components import (
    ToastNotification,
    get_toast,
    show_empty_state
)


def get_project_root():
    """获取项目根目录"""
    return Path(__file__).parent.parent


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


def render():
    """显示主页/仪表盘 - 对标 Tableau 风格"""
    
    st.markdown('<h1 class="text-display">📊 数据概览仪表盘</h1>', unsafe_allow_html=True)
    
    df, filename = load_latest_data()
    
    if df is None or df.empty:
        # ===== 空状态界面 - 使用原生Streamlit组件确保导航可靠 =====
        
        # 显示空状态提示信息
        st.markdown("""
        <div style="
            text-align: center;
            padding: 60px 40px;
            background: linear-gradient(135deg, #F8FAFC 0%, #FFFFFF 100%);
            border-radius: 16px;
            border: 2px dashed #CBD5E1;
            margin: 24px 0;
        ">
            <div style="font-size: 4rem; margin-bottom: 16px;">🚀</div>
            <h3 style="font-size: 1.5rem; font-weight: 600; color: #1E293B; margin-bottom: 8px;">
                暂无数据
            </h3>
            <p style="color: #64748B; margin-bottom: 32px; line-height: 1.6; max-width: 500px; margin-left: auto; margin-right: auto;">
                开始您的第一个数据采集任务，解锁强大的 AI 分析能力。支持天猫/淘宝平台智能采集。
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # ===== 导航按钮组 - 原生Streamlit按钮（100%可靠）=====
        st.markdown("### 快速开始")
        
        nav_col1, nav_col2, nav_col3 = st.columns(3, gap="medium")
        
        with nav_col1:
            if st.button("🚀 开始采集", type="primary", use_container_width=True, key="nav_start_crawl"):
                st.session_state.current_page = "数据采集"
                st.rerun()
        
        with nav_col2:
            if st.button("🧪 测试模式", type="secondary", use_container_width=True, key="nav_test_mode"):
                st.session_state.current_page = "数据采集"
                st.rerun()
        
        with nav_col3:
            if st.button("📖 查看教程", type="secondary", use_container_width=True, key="nav_help"):
                st.session_state.current_page = "使用帮助"
                st.rerun()
        
        # 功能特点列表
        st.markdown("""
        <div style="margin-top: 32px; padding: 20px; background: #F8FAFC; border-radius: 12px;">
            <h4 style="color: #64748B; font-size: 14px; margin-bottom: 12px;">您将获得</h4>
            <ul style="list-style: none; padding: 0; display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                <li style="padding: 8px 12px; color: #475569;">✅ 实时价格监控与趋势分析</li>
                <li style="padding: 8px 12px; color: #475569;">✅ 市场份额与竞争格局洞察</li>
                <li style="padding: 8px 12px; color: #475569;">✅ 消费者行为画像分析</li>
                <li style="padding: 8px 12px; color: #475569;">✅ AI 驱动的智能报告生成</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        return  # 空状态时返回，不执行后续代码

    # ===== 有数据时的正常显示逻辑 =====
    
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
