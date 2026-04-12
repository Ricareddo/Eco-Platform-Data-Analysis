import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class ReportGenerator:
    """静态HTML报告生成器"""

    def __init__(self, db_manager=None):
        self.logger = logging.getLogger(__name__)
        
        if db_manager is None:
            from database.db_manager import DatabaseManager
            self.db = DatabaseManager()
        else:
            self.db = db_manager
        
        self.output_dir = Path(__file__).parent.parent / "output" / "report"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self):
        """生成完整报告"""
        self.logger.info("开始生成HTML报告...")
        
        try:
            data = self._collect_data()
            
            html_content = self._generate_html(data)
            
            html_path = self.output_dir / "index.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            data_path = self.output_dir / "data" / "report_data.json"
            data_path.parent.mkdir(exist_ok=True)
            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"报告生成成功: {html_path}")
            print(f"\n✅ 报告已生成！")
            print(f"   请打开: {html_path}")
            
        except Exception as e:
            self.logger.error(f"报告生成失败: {e}")
            raise

    def _collect_data(self) -> Dict:
        """收集报告所需的所有数据"""
        statistics = self.db.get_statistics()
        products = self.db.get_products(limit=200)
        reviews = self.db.get_reviews(limit=1000)
        
        sentiment_dist = statistics.get('sentiment_distribution', {})
        
        topic_distribution = {}
        for review in reviews:
            if review.get('topic'):
                topic = review['topic']
                topic_distribution[topic] = topic_distribution.get(topic, 0) + 1
        
        keywords_count = {}
        for review in reviews:
            if review.get('content'):
                words = review['content'].split()
                for word in words[:5]:
                    if len(word) > 1:
                        keywords_count[word] = keywords_count.get(word, 0) + 1
        
        top_keywords = sorted(keywords_count.items(), key=lambda x: x[1], reverse=True)[:50]
        
        return {
            'statistics': statistics,
            'products': products,
            'reviews': reviews,
            'sentiment_distribution': sentiment_dist,
            'topic_distribution': topic_distribution,
            'top_keywords': top_keywords,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def _generate_html(self, data: Dict) -> str:
        """生成HTML内容"""
        stats = data['statistics']
        sentiment_data = json.dumps(data['sentiment_distribution'], ensure_ascii=False)
        topic_data = json.dumps(data['topic_distribution'], ensure_ascii=False)
        products_json = json.dumps(data['products'], ensure_ascii=False)
        reviews_json = json.dumps(data['reviews'], ensure_ascii=False)
        keywords_json = json.dumps([{'text': k[0], 'size': k[1]} for k in data['top_keywords']], ensure_ascii=False)

        return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>食品电商AI分析报告</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }}
        .tab-active {{ border-bottom: 3px solid #3B82F6; color: #3B82F6; }}
        .card-hover:hover {{ transform: translateY(-2px); box-shadow: 0 10px 25px rgba(0,0,0,0.1); }}
        .modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000; }}
        .modal.show {{ display: flex; align-items: center; justify-content: center; }}
    </style>
</head>
<body class="bg-gray-50">
    <!-- 导航栏 -->
    <nav class="bg-white shadow-sm sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 py-4">
            <div class="flex items-center justify-between">
                <h1 class="text-xl font-bold text-gray-800">🍎 食品电商AI分析工具</h1>
                <div class="text-sm text-gray-500">生成时间: {data['generated_at']}</div>
            </div>
        </div>
    </nav>

    <!-- Tab导航 -->
    <div class="bg-white border-b">
        <div class="max-w-7xl mx-auto px-4">
            <div class="flex space-x-8">
                <button onclick="showTab('overview')" id="tab-overview" class="py-4 px-2 font-medium tab-active">商品概览</button>
                <button onclick="showTab('ingredient')" id="tab-ingredient" class="py-4 px-2 font-medium text-gray-600 hover:text-blue-600">配料分析</button>
                <button onclick="showTab('sentiment')" id="tab-sentiment" class="py-4 px-2 font-medium text-gray-600 hover:text-blue-600">情感分析</button>
                <button onclick="showTab('reviews')" id="tab-reviews" class="py-4 px-2 font-medium text-gray-600 hover:text-blue-600">评价详情</button>
            </div>
        </div>
    </div>

    <div class="max-w-7xl mx-auto px-4 py-6">
        <!-- Tab 1: 商品概览 -->
        <div id="content-overview" class="tab-content">
            <!-- 统计卡片 -->
            <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <div class="bg-white rounded-lg shadow p-6 card-hover transition-all">
                    <div class="text-3xl font-bold text-blue-600">{stats.get('total_products', 0)}</div>
                    <div class="text-gray-600 mt-1">商品总数</div>
                </div>
                <div class="bg-white rounded-lg shadow p-6 card-hover transition-all">
                    <div class="text-3xl font-bold text-green-600">{stats.get('total_reviews', 0)}</div>
                    <div class="text-gray-600 mt-1">评价总数</div>
                </div>
                <div class="bg-white rounded-lg shadow p-6 card-hover transition-all">
                    <div class="text-3xl font-bold text-purple-600">{stats.get('total_brands', 0)}</div>
                    <div class="text-gray-600 mt-1">品牌数量</div>
                </div>
                <div class="bg-white rounded-lg shadow p-6 card-hover transition-all">
                    <div class="text-3xl font-bold text-orange-600">{stats.get('avg_rating', 0)}</div>
                    <div class="text-gray-600 mt-1">平均评分</div>
                </div>
            </div>

            <!-- 筛选栏 -->
            <div class="bg-white rounded-lg shadow p-4 mb-6">
                <div class="flex flex-wrap gap-4 items-center">
                    <input type="text" id="search-input" placeholder="搜索商品..." 
                           class="border rounded px-3 py-2 flex-1 min-w-[200px]" onkeyup="filterProducts()">
                    <select id="sort-select" class="border rounded px-3 py-2" onchange="filterProducts()">
                        <option value="">默认排序</option>
                        <option value="price_asc">价格从低到高</option>
                        <option value="price_desc">价格从高到低</option>
                        <option value="sales_desc">销量排序</option>
                    </select>
                </div>
            </div>

            <!-- 商品网格 -->
            <div id="products-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            </div>
        </div>

        <!-- Tab 2: 配料分析 -->
        <div id="content-ingredient" class="tab-content hidden">
            <div class="bg-white rounded-lg shadow p-6">
                <h2 class="text-xl font-bold mb-4">配料与营养成分分析</h2>
                <p class="text-gray-600">选择商品查看详细的配料表和营养成分信息</p>
                
                <select id="product-select" class="w-full border rounded px-3 py-2 mt-4" onchange="showProductDetail()">
                    <option value="">请选择商品...</option>
                </select>
                
                <div id="product-detail" class="mt-6 hidden">
                </div>
            </div>
        </div>

        <!-- Tab 3: 情感分析 -->
        <div id="content-sentiment" class="tab-content hidden">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="text-lg font-bold mb-4">情感分布</h3>
                    <canvas id="sentiment-chart"></canvas>
                </div>
                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="text-lg font-bold mb-4">主题分布</h3>
                    <canvas id="topic-chart"></canvas>
                </div>
            </div>
            
            <div class="bg-white rounded-lg shadow p-6">
                <h3 class="text-lg font-bold mb-4">关键词云</h3>
                <div id="wordcloud" class="min-h-[300px] flex flex-wrap items-center justify-center gap-2">
                </div>
            </div>
        </div>

        <!-- Tab 4: 评价详情 -->
        <div id="content-reviews" class="tab-content hidden">
            <div class="bg-white rounded-lg shadow p-6">
                <div class="flex justify-between items-center mb-4">
                    <h2 class="text-xl font-bold">评价列表</h2>
                    <div class="flex gap-4">
                        <select id="sentiment-filter" class="border rounded px-3 py-2" onchange="filterReviews()">
                            <option value="">全部情感</option>
                            <option value="正面">正面</option>
                            <option value="中性">中性</option>
                            <option value="负面">负面</option>
                        </select>
                        <button onclick="exportData()" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                            📥 导出数据
                        </button>
                    </div>
                </div>
                
                <div id="reviews-list" class="space-y-4 max-h-[800px] overflow-y-auto">
                </div>
                
                <div id="pagination" class="mt-6 flex justify-center gap-2">
                </div>
            </div>
        </div>
    </div>

    <!-- Modal -->
    <div id="modal" class="modal">
        <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div class="p-6">
                <div class="flex justify-between items-start mb-4">
                    <h3 id="modal-title" class="text-xl font-bold"></h3>
                    <button onclick="closeModal()" class="text-gray-400 hover:text-gray-600 text-2xl">&times;</button>
                </div>
                <div id="modal-body"></div>
            </div>
        </div>
    </div>

    <script>
        // 数据
        const products = {products_json};
        const reviews = {reviews_json};
        const sentimentData = {sentiment_data};
        const topicData = {topic_data};
        const keywords = {keywords_json};
        
        let currentReviewsPage = 1;
        const reviewsPerPage = 20;

        // Tab切换
        function showTab(tabName) {{
            document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
            document.querySelectorAll('[id^="tab-"]').forEach(el => {{
                el.classList.remove('tab-active');
                el.classList.add('text-gray-600');
            }});
            
            document.getElementById('content-' + tabName).classList.remove('hidden');
            document.getElementById('tab-' + tabName).classList.add('tab-active');
            document.getElementById('tab-' + tabName).classList.remove('text-gray-600');
            
            if (tabName === 'overview') renderProducts();
            if (tabName === 'sentiment') renderCharts();
            if (tabName === 'reviews') renderReviews();
            if (tabName === 'ingredient') populateProductSelect();
        }}

        // 渲染商品列表
        function renderProducts() {{
            const grid = document.getElementById('products-grid');
            const searchTerm = document.getElementById('search-input').value.toLowerCase();
            const sortBy = document.getElementById('sort-select').value;
            
            let filtered = products.filter(p => 
                p.name.toLowerCase().includes(searchTerm)
            );
            
            if (sortBy === 'price_asc') filtered.sort((a, b) => a.price - b.price);
            else if (sortBy === 'price_desc') filtered.sort((a, b) => b.price - a.price);
            else if (sortBy === 'sales_desc') filtered.sort((a, b) => b.sales_count - a.sales_count);
            
            grid.innerHTML = filtered.map(p => `
                <div class="bg-white rounded-lg shadow p-5 card-hover cursor-pointer transition-all" onclick="showProductModal(${{p.id}})">
                    <h3 class="font-semibold text-gray-800 mb-2 line-clamp-2">${{p.name}}</h3>
                    <div class="flex justify-between items-center mb-3">
                        <span class="text-2xl font-bold text-red-600">¥${{p.price || '0.00'}}</span>
                        <span class="text-sm text-gray-500">销量 ${{p.sales_count || 0}}</span>
                    </div>
                    <div class="text-sm text-gray-600">
                        <p>店铺: ${{p.shop_name || '-'}}</p>
                    </div>
                </div>
            `).join('');
        }}

        // 显示商品详情弹窗
        function showProductModal(productId) {{
            const product = products.find(p => p.id === productId);
            if (!product) return;
            
            document.getElementById('modal-title').textContent = product.name;
            document.getElementById('modal-body').innerHTML = `
                <div class="space-y-4">
                    <div><strong>价格:</strong> ¥${{product.price || '0.00'}}</div>
                    <div><strong>销量:</strong> ${{product.sales_count || 0}}</div>
                    <div><strong>店铺:</strong> ${{product.shop_name || '-'}}</div>
                    ${{product.detail_url ? `<a href="${{product.detail_url}}" target="_blank" class="text-blue-600">查看详情页 →</a>` : ''}}
                </div>
            `;
            document.getElementById('modal').classList.add('show');
        }}

        function closeModal() {{
            document.getElementById('modal').classList.remove('show');
        }}

        // 填充商品选择下拉框
        function populateProductSelect() {{
            const select = document.getElementById('product-select');
            select.innerHTML = '<option value="">请选择商品...</option>' + 
                products.map(p => `<option value="${{p.id}}">${{p.name}}</option>`).join('');
        }}

        // 显示商品详情（配料与营养成分）
        function showProductDetail() {{
            const productId = document.getElementById('product-select').value;
            const detailEl = document.getElementById('product-detail');
            
            if (!productId) {{
                detailEl.classList.add('hidden');
                return;
            }}
            
            const product = products.find(p => p.id == productId);
            if (!product) return;
            
            // 模拟配料数据（实际应从数据库获取）
            const mockIngredients = [
                {{name: '小麦粉', percentage: '45%'}},
                {{name: '白砂糖', percentage: '20%'}},
                {{name: '植物油', percentage: '15%'}},
                {{name: '食用盐', percentage: '3%'}},
                {{name: '食品添加剂', percentage: '2%'}}
            ];
            
            // 模拟营养数据（符合GB 28050-2011国家标准）
            const mockNutrition = [
                {{name: '能量', value: '2000', unit: 'kJ'}},
                {{name: '蛋白质', value: '8.0', unit: 'g'}},
                {{name: '脂肪', value: '15.0', unit: 'g'}},
                {{name: '碳水化合物', value: '65.0', unit: 'g'}},
                {{name: '钠', value: '500', unit: 'mg'}}
            ];
            
            detailEl.innerHTML = `
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <!-- 商品基本信息 -->
                    <div class="bg-gray-50 rounded-lg p-4">
                        <h3 class="font-bold text-lg mb-3 text-gray-800">${{product.name}}</h3>
                        <div class="space-y-2 text-sm">
                            <p><span class="text-gray-500">价格:</span> <span class="text-red-600 font-semibold">¥${{product.price || '0.00'}}</span></p>
                            <p><span class="text-gray-500">销量:</span> ${{product.sales_count || 0}}</p>
                            <p><span class="text-gray-500">店铺:</span> ${{product.shop_name || '-'}}</p>
                        </div>
                    </div>
                    
                    <!-- 配料表 -->
                    <div class="bg-blue-50 rounded-lg p-4">
                        <h3 class="font-bold text-lg mb-3 text-blue-800">📋 配料表</h3>
                        <div class="space-y-2">
                            ${{mockIngredients.map(ing => `
                                <div class="flex justify-between items-center bg-white rounded px-3 py-2 text-sm">
                                    <span>${{ing.name}}</span>
                                    <span class="text-blue-600 font-medium">${{ing.percentage}}</span>
                                </div>
                            `).join('')}}
                        </div>
                    </div>
                    
                    <!-- 营养成分表 -->
                    <div class="bg-green-50 rounded-lg p-4 md:col-span-2">
                        <h3 class="font-bold text-lg mb-3 text-green-800">🥗 营养成分表（每100g）</h3>
                        <div class="overflow-x-auto">
                            <table class="w-full text-sm">
                                <thead>
                                    <tr class="border-b border-green-200">
                                        <th class="text-left py-2 px-3">营养成分</th>
                                        <th class="text-right py-2 px-3">含量</th>
                                        <th class="text-right py-2 px-3">NRV%</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${{mockNutrition.map(nut => `
                                        <tr class="border-b border-green-100">
                                            <td class="py-2 px-3 font-medium">${{nut.name}}</td>
                                            <td class="text-right py-2 px-3">
                                                <span class="font-mono font-semibold">${{nut.value}}</span>
                                                <span class="text-gray-500 ml-1">${{nut.unit}}</span>
                                            </td>
                                            <td class="text-right py-2 px-3 text-green-600 font-medium">${{Math.floor(Math.random() * 30 + 5)}}%</td>
                                        </tr>
                                    `).join('')}}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
                
                <div class="mt-4 p-3 bg-yellow-50 rounded text-sm text-yellow-700">
                    ⚠️ 注：当前为演示数据。如需真实数据，请运行完整采集流程并完成OCR识别。
                </div>
            `;
            
            detailEl.classList.remove('hidden');
        }}

        // 渲染图表
        function renderCharts() {{
            // 情感分布饼图
            new Chart(document.getElementById('sentiment-chart'), {{
                type: 'pie',
                data: {{
                    labels: Object.keys(sentimentData),
                    datasets: [{{
                        data: Object.values(sentimentData),
                        backgroundColor: ['#10B981', '#F59E0B', '#EF4444']
                    }}]
                }},
                options: {{ responsive: true }}
            }});
            
            // 主题分布柱状图
            new Chart(document.getElementById('topic-chart'), {{
                type: 'bar',
                data: {{
                    labels: Object.keys(topicData),
                    datasets: [{{
                        label: '评价数',
                        data: Object.values(topicData),
                        backgroundColor: '#3B82F6'
                    }}]
                }},
                options: {{ responsive: true }}
            }});
            
            // 关键词云
            const wordcloudEl = document.getElementById('wordcloud');
            const maxSize = Math.max(...keywords.map(k => k.size), 1);
            wordcloudEl.innerHTML = keywords.map(k => `
                <span style="font-size: ${{12 + (k.size / maxSize) * 24}}px; 
                             color: hsl(${{Math.random() * 360}}, 70%, 50%);
                             padding: 4px;">
                    ${{k.text}}
                </span>
            `).join('');
        }}

        // 渲染评价列表
        function renderReviews() {{
            const filter = document.getElementById('sentiment-filter').value;
            let filtered = reviews;
            
            if (filter) {{
                filtered = filtered.filter(r => r.sentiment === filter);
            }}
            
            const start = (currentReviewsPage - 1) * reviewsPerPage;
            const end = start + reviewsPerPage;
            const pageReviews = filtered.slice(start, end);
            
            const listEl = document.getElementById('reviews-list');
            listEl.innerHTML = pageReviews.map(r => `
                <div class="border-b pb-4">
                    <div class="flex justify-between items-start mb-2">
                        <div class="flex gap-2">
                            <span class="px-2 py-1 rounded text-xs font-medium ${{r.sentiment === '正面' ? 'bg-green-100 text-green-700' : r.sentiment === '负面' ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700'}}">
                                ${{r.sentiment || '中性'}}
                            </span>
                            <span class="px-2 py-1 rounded text-xs bg-blue-100 text-blue-700">
                                ${{r.topic || '其他'}}
                            </span>
                        </div>
                        <div class="text-yellow-500">${{'⭐'.repeat(r.rating || 0)}}</div>
                    </div>
                    <p class="text-gray-700">${{r.content}}</p>
                    <div class="text-xs text-gray-400 mt-2">${{r.user_name || '匿名用户'}} · ${{r.review_time || ''}}</div>
                </div>
            `).join('');
            
            // 分页控制
            const totalPages = Math.ceil(filtered.length / reviewsPerPage);
            const hasData = filtered.length > 0;
            const isFirstPage = currentReviewsPage <= 1;
            const isLastPage = currentReviewsPage >= totalPages;
            const isSinglePage = totalPages <= 1;
            
            let paginationHTML = '';
            
            if (hasData) {{
                // 上一页按钮
                const prevDisabled = isFirstPage || isSinglePage;
                paginationHTML += `
                    <button onclick="goToReviewPage(${{currentReviewsPage - 1}})" 
                            ${{prevDisabled ? 'disabled' : ''}}
                            class="px-4 py-2 border rounded-lg transition-all ${{prevDisabled ? 'bg-gray-100 text-gray-400 cursor-not-allowed opacity-60' : 'bg-white text-gray-700 hover:bg-blue-50 hover:border-blue-300 hover:text-blue-600'}}">
                        ← 上一页
                    </button>
                `;
                
                // 页码信息
                paginationHTML += `
                    <span class="px-4 py-2 text-sm text-gray-600">
                        <span class="font-medium text-blue-600">${{currentReviewsPage}}</span> / ${{totalPages}} 页
                        <span class="ml-2 text-gray-400">|</span>
                        <span class="ml-2">共 ${{filtered.length}} 条</span>
                    </span>
                `;
                
                // 下一页按钮
                const nextDisabled = isLastPage || isSinglePage;
                paginationHTML += `
                    <button onclick="goToReviewPage(${{currentReviewsPage + 1}})" 
                            ${{nextDisabled ? 'disabled' : ''}}
                            class="px-4 py-2 border rounded-lg transition-all ${{nextDisabled ? 'bg-gray-100 text-gray-400 cursor-not-allowed opacity-60' : 'bg-white text-gray-700 hover:bg-blue-50 hover:border-blue-300 hover:text-blue-600'}}">
                        下一页 →
                    </button>
                `;
            }} else {{
                paginationHTML = '<span class="text-gray-400 text-sm">暂无评价数据</span>';
            }}
            
            document.getElementById('pagination').innerHTML = paginationHTML;
        }}

        function goToReviewPage(page) {{
            const filter = document.getElementById('sentiment-filter').value;
            let filtered = reviews;
            
            if (filter) {{
                filtered = filtered.filter(r => r.sentiment === filter);
            }}
            
            const totalPages = Math.ceil(filtered.length / reviewsPerPage) || 1;
            
            // 边界保护：限制页码在有效范围内
            if (page < 1) page = 1;
            if (page > totalPages) page = totalPages;
            
            currentReviewsPage = page;
            renderReviews();
        }}

        function filterReviews() {{
            currentReviewsPage = 1;
            renderReviews();
        }}

        function filterProducts() {{
            renderProducts();
        }}

        function exportData() {{
            const dataStr = JSON.stringify({{products, reviews}}, null, 2);
            const blob = new Blob([dataStr], {{type: 'application/json'}});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'food_analyzer_export_' + new Date().toISOString().slice(0,10) + '.json';
            a.click();
        }}

        // 初始化
        window.onload = function() {{
            showTab('overview');
        }};
    </script>
</body>
</html>'''

    def close(self):
        """关闭资源"""
        if hasattr(self, 'db'):
            self.db.close()
