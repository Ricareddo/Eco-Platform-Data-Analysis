"""
Page 2: 数据分析工作台 - B端专业版 v3.0
多维度深度分析 | AI驱动洞察
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from components import (
    ToastNotification,
    get_toast,
    show_empty_state
)
from views.data_collection import load_latest_data


def render():
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
        empty_html += '</div>'
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
    
    unique_shops = df['shop_name'].nunique() if 'shop_name' in df.columns else 0
    
    report_content = f"""
    ## 📊 数据概览
    
    本次分析共涵盖 **{len(df):,}** 个商品，来自 **{unique_shops:,}** 家不同店铺。
    
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

    if st.button("导出报告", type="primary"):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        from pathlib import Path
        output_dir = Path(__file__).parent.parent / "output"
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
