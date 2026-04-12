"""
Utils - 可视化工具集
图表生成 | 数据展示 | 报告导出
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime
from pathlib import Path
from collections import Counter


class Visualizer:
    """可视化工具类 - 封装所有图表生成和数据分析功能"""

    def __init__(self):
        """初始化可视化器"""
        pass

    @staticmethod
    def load_data(file_path: str = None) -> tuple:
        """
        加载数据文件
        
        Args:
            file_path: 文件路径（可选，默认加载最新的）
            
        Returns:
            tuple: (DataFrame, filename)
        """
        output_dir = Path(__file__).parent.parent / "output"
        
        if not output_dir.exists():
            return None, None
        
        if file_path and Path(file_path).exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            # 查找最新文件
            json_files = sorted([
                f for f in output_dir.glob('*.json')
                if 'intelligent_crawl' in f.name or 'crawl' in f.name
            ], key=lambda x: x.stat().st_mtime, reverse=True)
            
            if not json_files:
                return None, None
            
            file_path = json_files[0]
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                print(f"[ERROR] 加载数据失败: {e}")
                return None, None
        
        products = data.get('products', [])
        df = pd.DataFrame(products) if products else pd.DataFrame()
        
        return df, file_path.name if isinstance(file_path, Path) else file_path

    def create_price_histogram(self, df: pd.DataFrame) -> go.Figure:
        """
        创建价格分布直方图
        
        Args:
            df: 商品数据DataFrame
            
        Returns:
            plotly Figure
        """
        fig = px.histogram(
            df, 
            x='price', 
            nbins=40,
            title='价格分布直方图',
            labels={'price': '价格 (¥)', 'count': '数量'},
            color_discrete_sequence=['#2563EB']
        )
        
        fig.update_layout(
            height=400, 
            template="plotly_white",
            title_font_size=16
        )
        fig.update_traces(
            marker_line_color='#1E40AF', 
            marker_line_width=1
        )
        
        return fig

    def create_price_boxplot(self, df: pd.DataFrame) -> go.Figure:
        """
        创建价格箱线图
        
        Args:
            df: 商品数据DataFrame
            
        Returns:
            plotly Figure
        """
        fig = px.box(
            df, 
            y='price', 
            title='价格箱线图',
            color_discrete_sequence=['#7C3AED']
        )
        
        fig.update_layout(
            height=400, 
            template="plotly_white"
        )
        
        return fig

    def create_price_pie_chart(self, df: pd.DataFrame) -> go.Figure:
        """
        创建价格区间饼图
        
        Args:
            df: 商品数据DataFrame
            
        Returns:
            plotly Figure
        """
        price_ranges = {
            '¥0-10 (大众)': (df['price'] <= 10).sum(),
            '¥11-30 (经济)': ((df['price'] > 10) & (df['price'] <= 30)).sum(),
            '¥31-60 (标准)': ((df['price'] > 30) & (df['price'] <= 60)).sum(),
            '¥61-100 (高端)': ((df['price'] > 60) & (df['price'] <= 100)).sum(),
            '¥101+ (奢侈)': (df['price'] > 100).sum()
        }
        
        range_df = pd.DataFrame(list(price_ranges.items()), columns=['价格区间', '商品数量'])
        
        fig = px.pie(
            range_df, 
            values='商品数量', 
            names='价格区间',
            title='价格区间分布',
            hole=0.4,
            color_discrete_sequence=['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6']
        )
        
        fig.update_traces(
            textposition='inside', 
            textinfo='percent+label'
        )
        fig.update_layout(template="plotly_white")
        
        return fig

    def create_shop_bar_chart(self, df: pd.DataFrame, top_n: int = 15) -> go.Figure:
        """
        创建店铺商品数量柱状图
        
        Args:
            df: 商品数据DataFrame
            top_n: 显示前N名店铺
            
        Returns:
            plotly Figure
        """
        shop_stats = df.groupby('shop_name').agg({
            'price': ['mean', 'count', 'min', 'max']
        }).round(2)
        
        shop_stats.columns = ['平均价格', '商品数量', '最低价', '最高价']
        shop_stats = shop_stats.sort_values('商品数量', ascending=False)
        
        top_shops = shop_stats.head(top_n)
        
        fig = px.bar(
            top_shops, 
            x='商品数量', 
            y=top_shops.index,
            orientation='h',
            title=f'Top {top_n} 店铺商品数量排行',
            color='平均价格',
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(
            height=500, 
            yaxis={'categoryorder': 'total ascending'}, 
            template="plotly_white"
        )
        
        return fig

    def create_sunburst_chart(self, df: pd.DataFrame) -> go.Figure:
        """
        创建店铺价值旭日图
        
        Args:
            df: 商品数据DataFrame
            
        Returns:
            plotly Figure
        """
        fig = px.sunburst(
            df,
            path=['shop_name'],
            values='price',
            title='店铺价值分布',
            color='price',
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(template="plotly_white")
        
        return fig

    def analyze_price_distribution(self, df: pd.DataFrame) -> dict:
        """
        价格分布分析
        
        Args:
            df: 商品数据DataFrame
            
        Returns:
            dict: 分析结果
        """
        if 'price' not in df.columns:
            return {'error': '缺少价格字段'}
        
        prices = df['price']
        
        result = {
            'basic_stats': {
                'total_products': len(df),
                'average': prices.mean(),
                'median': prices.median(),
                'std': prices.std(),
                'min': prices.min(),
                'max': prices.max()
            },
            'ranges': {
                '¥0-10 (大众)': int((prices <= 10).sum()),
                '¥11-30 (经济)': int(((prices > 10) & (prices <= 30)).sum()),
                '¥31-60 (标准)': int(((prices > 30) & (prices <= 60)).sum()),
                '¥61-100 (高端)': int(((prices > 60) & (prices <= 100)).sum()),
                '¥101+ (奢侈)': int((prices > 100).sum())
            },
            'top_expensive': df.nlargest(5, 'price')[['name', 'price', 'shop_name']].to_dict('records'),
            'top_cheap': df.nsmallest(5, 'price')[['name', 'price', 'shop_name']].to_dict('records')
        }
        
        return result

    def analyze_brand_market(self, df: pd.DataFrame) -> dict:
        """
        品牌市场分析
        
        Args:
            df: 商品数据DataFrame
            
        Returns:
            dict: 分析结果
        """
        if 'shop_name' not in df.columns:
            return {'error': '缺少店铺名称字段'}
        
        shop_stats = df.groupby('shop_name').agg({
            'price': ['mean', 'count', 'min', 'max']
        }).round(2)
        
        shop_stats.columns = ['平均价格', '商品数量', '最低价', '最高价']
        shop_stats = shop_stats.sort_values('商品数量', ascending=False)
        shop_stats['市场份额 (%)'] = (shop_stats['商品数量'] / len(df) * 100).round(2)
        
        # 市场集中度
        sorted_shops = shop_stats.sort_values('商品数量', ascending=False)
        cr5 = sorted_shops.head(5)['商品数量'].sum()
        cr10 = sorted_shops.head(10)['商品数量'].sum()
        
        result = {
            'shop_stats': shop_stats.head(20).to_dict('index'),
            'market_concentration': {
                'CR5': f"{cr5}/{len(df)} ({cr5/len(df)*100:.1f}%)",
                'CR10': f"{cr10}/{len(df)} ({cr10/len(df)*100:.1f}%)"
            },
            'flagship_count': len(df[df['shop_name'].str.contains('旗舰店|官方店', na=False)])
        }
        
        return result

    def generate_analysis_report(self, df: pd.DataFrame, output_format: str = "Markdown") -> str:
        """
        生成综合分析报告
        
        Args:
            df: 商品数据DataFrame
            output_format: 输出格式（Markdown/JSON/CSV）
            
        Returns:
            str: 报告内容或文件路径
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        unique_shops = df['shop_name'].nunique() if 'shop_name' in df.columns else 0
        
        report_content = f"""
## 📊 数据概览

本次分析共涵盖 **{len(df):,}** 个食品类商品，来自 **{unique_shops:,}** 家不同店铺。

### 💰 价格分析

"""
        
        if 'price' in df.columns:
            report_content += f"""- **平均价格**: ¥{df['price'].mean():.2f}
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
                
                report_content += f"""- **CR5 (前5名店铺)**: {cr5:.1f}% - {'高度集中' if cr5 > 50 else '适度分散'}
- **CR10 (前10名店铺)**: {cr10:.1f}% - {'高度集中' if cr10 > 70 else '适度分散'}

"""
        
        report_content += f"---\n*报告由 AI 分析系统自动生成于 {timestamp}*\n"
        
        # 根据格式保存
        output_dir = Path(__file__).parent.parent / "output"
        output_dir.mkdir(exist_ok=True)
        
        timestamp_file = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if output_format == "Markdown":
            output_file = output_dir / f'analysis_report_{timestamp_file}.md'
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
                
        elif output_format == "JSON":
            output_file = output_dir / f'analysis_data_{timestamp_file}.json'
            df.to_json(output_file, orient='records', force_ascii=False, indent=2)
            report_content = str(output_file)
            
        elif output_format == "CSV":
            output_file = output_dir / f'analysis_data_{timestamp_file}.csv'
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            report_content = str(output_file)
        
        return str(output_file)


def quick_analyze(data_file: str = None) -> dict:
    """
    快速分析函数（便捷接口）
    
    Args:
        data_file: 数据文件路径
        
    Returns:
        dict: 分析结果
    """
    visualizer = Visualizer()
    df, filename = visualizer.load_data(data_file)
    
    if df is None or df.empty:
        return {'error': '未找到数据'}
    
    result = {
        'filename': filename,
        'total_products': len(df),
        'price_analysis': visualizer.analyze_price_distribution(df),
        'market_analysis': visualizer.analyze_brand_market(df)
    }
    
    return result
