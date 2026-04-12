#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据分析工具 - 展示采集数据的商业价值

功能：
1. 价格分布分析
2. 品类关键词统计
3. 店铺排名与市场份额
4. 热门品牌识别
5. 生成分析报告
"""

import sys
import os

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
from collections import Counter
from datetime import datetime


def load_latest_data():
    """加载最新的采集数据"""
    output_dir = "output"
    
    # 查找最新的JSON文件
    json_files = [
        f for f in os.listdir(output_dir)
        if f.startswith('intelligent_crawl_') and f.endswith('.json')
    ]
    
    if not json_files:
        print("ERROR: No data files found!")
        return None, None
    
    # 按时间排序，取最新的
    json_files.sort(reverse=True)
    latest_file = os.path.join(output_dir, json_files[0])
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data, latest_file


def analyze_price_distribution(products):
    """价格分布分析"""
    print("\n" + "="*70)
    print("📊 PRICE DISTRIBUTION ANALYSIS")
    print("="*70)
    
    prices = [p['price'] for p in products]
    
    # 基础统计
    avg_price = sum(prices) / len(prices)
    min_price = min(prices)
    max_price = max(prices)
    median_price = sorted(prices)[len(prices)//2]
    
    print(f"\nBasic Statistics:")
    print(f"  ├─ Total Products: {len(products)}")
    print(f"  ├─ Average Price:   ¥{avg_price:.2f}")
    print(f"  ├─ Median Price:    ¥{median_price:.2f}")
    print(f"  ├─ Min Price:       ¥{min_price:.2f}")
    print(f"  └─ Max Price:       ¥{max_price:.2f}")
    
    # 价格区间分布
    ranges = {
        'Budget (¥0-10)': 0,
        'Economy (¥11-30)': 0,
        'Standard (¥31-60)': 0,
        'Premium (¥61-100)': 0,
        'Luxury (¥101+)': 0
    }
    
    for price in prices:
        if price <= 10:
            ranges['Budget (¥0-10)'] += 1
        elif price <= 30:
            ranges['Economy (¥11-30)'] += 1
        elif price <= 60:
            ranges['Standard (¥31-60)'] += 1
        elif price <= 100:
            ranges['Premium (¥61-100)'] += 1
        else:
            ranges['Luxury (¥101+)'] += 1
    
    print(f"\nPrice Range Distribution:")
    for range_name, count in sorted(ranges.items(), key=lambda x: x[1], reverse=True):
        pct = (count / len(products)) * 100
        bar = '█' * int(pct / 5) + '░' * (20 - int(pct / 5))
        print(f"  {range_name:<20}: {count:>3} ({pct:>5.1f}%) {bar}")
    
    # Top 5 最贵和最便宜
    print(f"\nTop 5 Most Expensive:")
    sorted_products = sorted(products, key=lambda x: x['price'], reverse=True)
    for i, p in enumerate(sorted_products[:5], 1):
        print(f"  {i}. ¥{p['price']:>7.0f} | {p['name'][:45]}")
    
    print(f"\nTop 5 Most Affordable:")
    for i, p in enumerate(sorted_products[-5:], 1):
        print(f"  {i}. ¥{p['price']:>7.0f} | {p['name'][:45]}")
    
    return {
        'average': avg_price,
        'median': median_price,
        'ranges': ranges
    }


def analyze_categories(products):
    """品类关键词分析"""
    print("\n" + "="*70)
    print("🏷️  CATEGORY KEYWORD ANALYSIS")
    print("="*70)
    
    # 定义品类关键词
    category_keywords = {
        '零食/Light Snacks': ['零食', '小吃', '解馋', '休闲'],
        '卤味/Meat Products': ['卤味', '牛肉', '鸡爪', '鸭翅', '鸡翅', '肉食', '香肠', '鸡胸肉'],
        '饼干/Biscuits': ['饼干', '曲奇', '糕点', '面包', '蛋糕', '蛋黄酥'],
        '方便面/Instant Noodles': ['方便面', '泡面', '火鸡面', '拌面', '干脆面'],
        '坚果/Nuts & Dried Fruits': ['坚果', '干果', '花生', '核桃', '燕窝'],
        '传统糕点/Traditional': ['粽子', '月饼', '绿豆糕', '酥饼'],
        '健康食品/Health Food': ['无糖', '低脂', '代餐', '健身', '控糖'],
        '海鲜/Seafood': ['鱼仔', '小鱼', '虾', '蟹'],
        '地方特产/Specialty': ['湖南', '四川', '丹东', '嘉兴']
    }
    
    # 统计每个品类的商品数
    category_counts = {}
    product_categories = {}  # 每个商品所属的品类
    
    for idx, product in enumerate(products):
        name = product.get('name', '')
        found_category = None
        
        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in name:
                    found_category = category
                    break
            if found_category:
                break
        
        if found_category:
            category_counts[found_category] = category_counts.get(found_category, 0) + 1
            product_categories[idx] = found_category
        else:
            product_categories[idx] = '其他/Other'
            category_counts['其他/Other'] = category_counts.get('其他/Other', 0) + 1
    
    # 显示结果
    print(f"\nCategory Distribution:")
    print(f"{'Category':<25} {'Count':>6} {'Percentage':>10} {'Visual'}")
    print("-"*70)
    
    total = len(products)
    for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        pct = (count / total) * 100
        bar = '█' * int(pct / 2)
        print(f"{cat:<25} {count:>6} {pct:>9.1f}%  {bar}")
    
    # 热门关键词
    all_keywords = []
    for product in products:
        name = product.get('name', '')
        words = name.replace(' ', '').split()
        all_keywords.extend([w for w in words if len(w) >= 2])
    
    top_keywords = Counter(all_keywords).most_common(15)
    
    print(f"\nTop 15 Keywords:")
    for i, (keyword, count) in enumerate(top_keywords, 1):
        print(f"  {i:2d}. {keyword:<15} ({count}次)")
    
    return {
        'categories': category_counts,
        'keywords': top_keywords
    }


def analyze_shops(products):
    """店铺排名与市场份额"""
    print("\n" + "="*70)
    print("🏪 SHOP RANKING & MARKET SHARE")
    print("="*70)
    
    shop_stats = {}
    
    for product in products:
        shop_raw = product.get('shop_name', '')
        
        # 提取店铺名（去除销量前缀）
        if '\n' in shop_raw:
            parts = shop_raw.split('\n')
            shop_name = parts[-1] if len(parts) > 1 else parts[0]
            sales_info = parts[0] if parts[0].startswith('回头客') else ''
        else:
            shop_name = shop_raw
            sales_info = ''
        
        # 清理店铺名
        shop_name = shop_name.strip().replace('旗舰店', '').replace('专营店', '').replace('专卖店', '')
        
        if shop_name not in shop_stats:
            shop_stats[shop_name] = {
                'count': 0,
                'products': [],
                'sales_rank': '',
                'total_price': 0
            }
        
        shop_stats[shop_name]['count'] += 1
        shop_stats[shop_name]['products'].append(product.get('name', '')[:40])
        shop_stats[shop_name]['total_price'] += product.get('price', 0)
        if sales_info and not shop_stats[shop_name]['sales_rank']:
            shop_stats[shop_name]['sales_rank'] = sales_info
    
    # 排序
    sorted_shops = sorted(shop_stats.items(), key=lambda x: x[1]['count'], reverse=True)
    
    print(f"\nTop 15 Shops by Product Count:")
    print(f"{'Rank':<6} {'Shop Name':<22} {'Products':>9} {'Avg Price':>10} {'Sales Rank':>12}")
    print("-"*70)
    
    for rank, (shop_name, stats) in enumerate(sorted_shops[:15], 1):
        count = stats['count']
        avg_price = stats['total_price'] / count
        sales = stats['sales_rank']
        
        market_share = (count / len(products)) * 100
        
        print(f"{rank:<6} {shop_name:<22} {count:>9} ¥{avg_price:>8.2f} {sales:>12}")
    
    # 市场集中度（CR5, CR10）
    cr5 = sum(stats['count'] for _, stats in sorted_shops[:5])
    cr10 = sum(stats['count'] for _, stats in sorted_shops[:10])
    
    print(f"\nMarket Concentration:")
    print(f"  ├─ CR5 (Top 5 shops):  {cr5}/{len(products)} ({(cr5/len(products)*100):.1f}%)")
    print(f"  └─ CR10 (Top 10 shops): {cr10}/{len(products)} ({(cr10/len(products)*100):.1f}%)")
    
    # 识别旗舰店数量
    flagship_count = sum(1 for _, stats in sorted_shops if any(
        isinstance(p, str) and p.endswith('旗舰店') for p in stats['products']
    ))
    
    print(f"\n  Flagship Stores: {flagship_count}/{len(sorted_shops)}")
    
    return {
        'shops': dict(sorted_shops),
        'cr5': cr5,
        'cr10': cr10
    }


def identify_top_brands(products):
    """识别热门品牌"""
    print("\n" + "="*70)
    print("🏆 TOP BRANDS IDENTIFICATION")
    print("="*70)
    
    brand_patterns = [
        ('三只松鼠', r'三只松鼠'),
        ('良品铺子', r'良品铺子'),
        ('比比赞', r'比比赞'),
        ('盐津铺子', r'盐津铺子'),
        ('百草味', r'百草味'),
        ('来伊份', r'来伊份'),
        ('卫龙', r'卫龙'),
        ('旺旺', r'旺旺'),
        ('好丽友', r'好丽友'),
        ('奥利奥', r'奥利奥'),
        ('小仙炖', r'小仙炖'),
        ('百亿补贴', r'百亿补贴'),
        ('白象', r'白象'),
        ('阿宽', r'阿宽'),
        ('友臣', r'友臣'),
    ]
    
    brand_stats = {}
    
    for pattern_name, pattern_re in brand_patterns:
        import re as regex_module
        matches = [p for p in products if regex_module.search(pattern_re, p.get('name', ''))]
        if matches:
            brand_stats[pattern_name] = {
                'count': len(matches),
                'avg_price': sum(m['price'] for m in matches) / len(matches),
                'products': [m['name'][:35] for m in matches[:3]]
            }
    
    if brand_stats:
        print(f"\nIdentified Brands ({len(brand_stats)}):")
        print(f"{'Brand':<12} {'Products':>9} {'Avg Price':>10} {'Sample Products'}")
        print("-"*70)
        
        for brand, stats in sorted(brand_stats.items(), key=lambda x: x[1]['count'], reverse=True)[:10]:
            samples = ', '.join(stats['products'][:2])
            print(f"{brand:<12} {stats['count']:>9} ¥{stats['avg_price']:>8.2f}  {samples}")
    else:
        print("\nNo major brands identified from product names")
    
    return brand_stats


def generate_summary_report(data, filename):
    """生成总结报告"""
    report_file = filename.replace('.json', '_analysis_report.md')
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 食品电商数据分析报告\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## 数据概览\n\n")
        f.write(f"- **采集商品数**: {data['metadata']['total_products']}\n")
        f.write(f"- **搜索关键词**: {data['metadata']['keyword']}\n")
        f.write(f"- **采集模式**: {data['metadata']['mode']}\n")
        f.write(f"- **数据文件**: {filename}\n\n")
        
        f.write("## 主要发现\n\n")
        f.write("### 1. 价格分析\n")
        prices = [p['price'] for p in data['products']]
        f.write(f"- 平均价格: ¥{sum(prices)/len(prices):.2f}\n")
        f.write(f"- 价格区间: ¥{min(prices)} - ¥{max(prices)}\n")
        budget_pct = len([p for p in data['products'] if p['price'] <= 10]) / len(data['products']) * 100
        f.write(f"- 平价商品占比 (≤¥10): {budget_pct:.1f}%\n\n")
        
        f.write("### 2. 店铺分析\n")
        shops = {}
        for p in data['products']:
            shop = p['shop_name'].split('\n')[-1] if '\n' in p['shop_name'] else p['shop_name']
            shops[shop] = shops.get(shop, 0) + 1
        
        top_shops = sorted(shops.items(), key=lambda x: x[1], reverse=True)[:5]
        f.write("**Top 5 店铺:**\n")
        for shop, count in top_shops:
            f.write(f"- {shop}: {count}个商品 ({count/len(data['products']*100):.1f}%)\n")
        f.write("\n")
        
        f.write("---\n")
        f.write("*报告由 Selenium 爬虫系统自动生成*\n")
    
    print(f"\n✅ Report saved to: {report_file}")
    return report_file


def main():
    print("\n" + "="*80)
    print("  DATA ANALYSIS TOOL - Business Intelligence")
    print("="*80)
    print(f"  Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # 加载数据
    print("\n[LOAD] Loading latest crawl data...")
    data, filename = load_latest_data()
    
    if not data:
        return False
    
    products = data['products']
    metadata = data['metadata']
    
    print(f"     ✓ Loaded {len(products)} products from: {filename}")
    print(f"     ✓ Keyword: {metadata['keyword']} | Mode: {metadata['mode']}")
    
    # 执行分析
    results = {}
    
    results['price_analysis'] = analyze_price_distribution(products)
    results['category_analysis'] = analyze_categories(products)
    results['shop_analysis'] = analyze_shops(products)
    results['brands'] = identify_top_brands(products)
    
    # 生成报告
    print("\n" + "="*70)
    print("📝 GENERATING SUMMARY REPORT")
    print("="*70)
    
    report_path = generate_summary_report(data, filename)
    
    # 最终统计
    print("\n" + "="*80)
    print("✅ ANALYSIS COMPLETE!")
    print("="*80)
    print(f"\nData Analyzed: {len(products)} products")
    print(f"Reports Generated:")
    print(f"  - Analysis Report: {report_path}")
    print(f"  - Source Data: {filename}")
    print(f"\nKey Insights:")
    
    avg_price = sum(p['price'] for p in products) / len(products)
    unique_shops = len(set(p['shop_name'].split('\n')[-1] if '\n' in p['shop_name'] else p['shop_name'] for p in products))
    
    print(f"  💰 Average Price: ¥{avg_price:.2f}")
    print(f"  🏪 Unique Shops: {unique_shops}")
    print(f"  📦 Price Range: ¥{min(p['price'] for p in products)} - ¥{max(p['price'] for p in products)}")
    
    print(f"\nEnd Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
