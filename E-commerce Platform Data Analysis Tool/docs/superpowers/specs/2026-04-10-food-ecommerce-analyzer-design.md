# 食品电商AI分析工具 - 设计文档

## 1. 项目概述

### 1.1 背景
为电商运营场景提供一个轻量化的食品类目AI分析工具，帮助运营人员快速了解市场竞品信息、分析用户评价情感倾向，辅助决策。

### 1.2 目标
- 采集天猫/京东/拼多多三大平台TOP200食品品牌商品数据
- 实现配料表与营养成分表的结构化识别
- 对用户评价进行情感极性和主题双维度标注
- 以静态HTML形式展示分析结果

### 1.3 开发策略
采用**渐进式MVP**策略，分阶段实现：
- **Phase 1**：天猫爬虫 + 基础数据采集 + 存储（3-4天）
- **Phase 2**：OCR识别 + 情感分析 + HTML展示（3-4天）
- **Phase 3**：扩展京东/拼多多平台（后续迭代）

---

## 2. 技术选型

| 模块 | 技术方案 | 说明 |
|------|----------|------|
| 爬虫框架 | DrissionPage | 模拟浏览器操作，绕过反爬 |
| 数据存储 | SQLite + CSV/JSON | 轻量级本地存储 |
| OCR识别 | 百度OCR API | 国内稳定，支持表格识别 |
| 情感分析 | 大模型API（DeepSeek/通义千问） | 高精度情感分析 |
| 前端展示 | 静态HTML + Chart.js + Tailwind CSS | 无需服务端，双击打开 |
| 部署环境 | 本地环境 | Python 3.9+ |

---

## 3. 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        数据采集层                                │
├─────────────┬─────────────┬─────────────┬─────────────────────┤
│  天猫爬虫    │  京东爬虫    │ 拼多多爬虫   │  本地多进程调度器    │
│(DrissionPage)│(DrissionPage)│(DrissionPage)│  (multiprocessing) │
└──────┬──────┴──────┬──────┴──────┬──────┴──────────┬──────────┘
       │             │             │                 │
       └─────────────┴──────┬──────┴─────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        数据存储层                                │
├─────────────────────────────┬───────────────────────────────────┤
│        SQLite               │         CSV/JSON 导出             │
│  - 商品基础信息              │   - 分析报告导出                  │
│  - 评价数据                  │   - 数据备份                      │
│  - 识别结果                  │                                   │
└─────────────────────────────┴───────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        分析处理层                                │
├─────────────────────────────┬───────────────────────────────────┤
│    百度OCR API              │        大模型API                  │
│  - 配料表结构化识别          │   - 情感极性分析（正/中/负）       │
│  - 营养成分表识别            │   - 主题标注（口感/健康/包装/价格）│
└─────────────────────────────┴───────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        展示层                                    │
├─────────────────────────────────────────────────────────────────┤
│                    静态HTML页面                                  │
│  - 商品概览仪表盘    - 情感分析图表    - 数据导出               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. 项目结构

```
food_analyzer/
├── crawlers/                     # 爬虫模块
│   ├── __init__.py
│   ├── base_crawler.py           # DrissionPage基类
│   ├── tmall_crawler.py          # 天猫爬虫
│   ├── jd_crawler.py             # 京东爬虫（Phase 3）
│   ├── pdd_crawler.py            # 拼多多爬虫（Phase 3）
│   └── scheduler.py              # 多进程调度器
├── analyzers/                    # 分析模块
│   ├── __init__.py
│   ├── ocr_processor.py          # OCR识别处理器
│   └── sentiment_analyzer.py     # 情感分析处理器
├── database/                     # 数据库模块
│   ├── __init__.py
│   ├── models.py                 # 数据模型定义
│   └── db_manager.py             # 数据库操作
├── output/                       # 输出目录
│   ├── data/                     # 导出数据
│   │   ├── products.json
│   │   └── reviews.json
│   └── report/                   # HTML报告
│       ├── index.html
│       ├── css/
│       ├── js/
│       └── data/
├── config/                       # 配置模块
│   ├── __init__.py
│   └── config_manager.py         # 交互式配置管理
├── main.py                       # 主入口
├── requirements.txt              # 依赖清单
└── README.md                     # 使用说明
```

---

## 5. 数据库设计

### 5.1 品牌表 (brands)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | TEXT | 品牌名称 |
| platform | TEXT | 平台（天猫/京东/拼多多） |
| category | TEXT | 食品细分类目 |
| created_at | DATETIME | 创建时间 |

### 5.2 商品表 (products)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| brand_id | INTEGER | 品牌ID（外键） |
| platform_product_id | TEXT | 平台商品ID |
| name | TEXT | 商品名称 |
| price | REAL | 价格 |
| sales_count | INTEGER | 销量 |
| shop_name | TEXT | 店铺名称 |
| ingredient_img_url | TEXT | 配料表图片URL |
| nutrition_img_url | TEXT | 营养成分表图片URL |
| detail_url | TEXT | 商品详情页URL |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### 5.3 评价表 (reviews)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| product_id | INTEGER | 商品ID（外键） |
| review_id | TEXT | 评价ID |
| user_name | TEXT | 用户名 |
| rating | INTEGER | 评分（1-5） |
| content | TEXT | 评价内容 |
| review_time | TEXT | 评价时间 |
| sentiment | TEXT | 情感（正面/中性/负面） |
| topic | TEXT | 主题（口感/健康/包装/价格/其他） |
| created_at | DATETIME | 创建时间 |

### 5.4 配料识别结果表 (ingredient_results)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| product_id | INTEGER | 商品ID（外键） |
| ingredient_text | TEXT | 识别出的配料文本 |
| structured_data | TEXT | JSON格式结构化数据 |
| created_at | DATETIME | 创建时间 |

### 5.5 营养成分识别结果表 (nutrition_results)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| product_id | INTEGER | 商品ID（外键） |
| nutrition_text | TEXT | 识别出的营养成分文本 |
| structured_data | TEXT | JSON格式结构化数据 |
| created_at | DATETIME | 创建时间 |

---

## 6. 爬虫模块设计

### 6.1 DrissionPage基类

```python
from DrissionPage import ChromiumPage
import random
import time

class BaseCrawler:
    """爬虫基类，封装DrissionPage通用操作"""

    def __init__(self, headless=False, browser='edge'):
        # 支持Edge/Chrome浏览器，Edge优先
        from DrissionPage import ChromiumOptions
        co = ChromiumOptions()
        if browser == 'edge':
            co.set_browser_path(r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe')
        co.headless(headless)
        self.page = ChromiumPage(co)
        self.base_url = ""

    def random_wait(self, min_sec=1, max_sec=3):
        """随机等待，模拟人类行为"""
        time.sleep(random.uniform(min_sec, max_sec))

    def open_page(self, url):
        """打开页面"""
        self.page.get(url)
        self.random_wait()

    def scroll_down(self, distance=500):
        """向下滚动"""
        self.page.scroll.down(distance)
        self.random_wait(0.5, 1.5)

    def get_element(self, selector):
        """获取元素"""
        return self.page.ele(selector)

    def get_elements(self, selector):
        """获取多个元素"""
        return self.page.eles(selector)

    def close(self):
        """关闭浏览器"""
        self.page.quit()
```

### 6.2 天猫爬虫

```python
class TmallCrawler(BaseCrawler):
    """天猫爬虫"""

    def __init__(self):
        super().__init__()
        self.base_url = "https://www.tmall.com"

    def search_products(self, keyword, page=1):
        """搜索商品"""
        pass

    def get_product_detail(self, product_url):
        """获取商品详情"""
        pass

    def get_product_reviews(self, product_id, max_count=500):
        """获取商品评价"""
        pass

    def download_image(self, url, save_path):
        """下载图片"""
        pass
```

### 6.3 数据采集字段

**商品基础信息**：
- 商品ID、名称、品牌、价格、销量、店铺名

**商品详情**：
- 配料表图片URL、营养成分表图片URL、详情页URL

**用户评价**：
- 评价ID、用户名、评分、内容、时间、图片

---

## 7. 分析模块设计

### 7.1 OCR识别

```python
from aip import AipOcr

class OCRProcessor:
    """配料表与营养成分表识别"""

    def __init__(self):
        # 首次运行时交互式输入API配置
        self.config = self.load_config()
        self.client = AipOcr(
            self.config['app_id'],
            self.config['api_key'],
            self.config['secret_key']
        )

    def recognize_ingredient(self, image_path):
        """识别配料表"""
        with open(image_path, 'rb') as f:
            result = self.client.general(f.read())
        return self.parse_ingredient_text(result)

    def recognize_nutrition(self, image_path):
        """识别营养成分表（表格识别）"""
        with open(image_path, 'rb') as f:
            result = self.client.tableRecognition(f.read())
        return self.parse_nutrition_table(result)
```

### 7.2 情感分析

```python
class SentimentAnalyzer:
    """评价情感分析"""

    def __init__(self):
        # 首次运行时交互式输入API配置
        self.config = self.load_config()

    def analyze_single(self, review_text):
        """分析单条评价"""
        prompt = f"""
        请分析以下食品类商品用户评价的情感和主题：

        评价内容：{review_text}

        请严格按以下JSON格式返回，不要包含其他内容：
        {{
            "sentiment": "正面/中性/负面",
            "topic": "口感/健康/包装/价格/其他",
            "keyword": "关键词（1-3个）"
        }}
        """
        return self.call_llm(prompt)

    def batch_analyze(self, reviews, batch_size=50):
        """批量分析"""
        results = []
        for i in range(0, len(reviews), batch_size):
            batch = reviews[i:i+batch_size]
            for review in batch:
                result = self.analyze_single(review['content'])
                results.append({
                    'review_id': review['id'],
                    **result
                })
            time.sleep(1)  # API限流
        return results
```

---

## 8. 前端设计

### 8.1 技术栈
- HTML5 + CSS3 + JavaScript（原生）
- Tailwind CSS（CDN引入）
- Chart.js（图表渲染）
- 无需构建工具，双击打开即可

### 8.2 配色方案
- 主色：#3B82F6（蓝色）
- 正面情感：#10B981（绿色）
- 中性情感：#F59E0B（橙色）
- 负面情感：#EF4444（红色）
- 背景：#F8FAFC（浅灰）
- 文字：#1E293B（深灰）

### 8.3 页面结构

**Tab 1: 商品概览**
- 统计卡片：商品数、评价数、品牌数、平均评分
- 筛选栏：平台选择、品牌搜索、价格范围、排序
- 商品卡片网格：图片、名称、价格、销量、情感评分

**Tab 2: 配料分析**
- 商品选择器
- 配料表图片 + 识别结果
- 营养成分表展示
- 多商品营养成分对比雷达图

**Tab 3: 情感分析**
- 情感分布饼图（正面/中性/负面）
- 主题分布柱状图（口感/健康/包装/价格）
- 情感趋势折线图
- 关键词词云

**Tab 4: 评价详情**
- 筛选栏：情感、主题、关键词搜索
- 评价列表：情感标签、主题标签、评价内容
- 分页功能

### 8.4 交互设计
- 点击商品卡片弹出详情Modal
- 图表hover显示详情
- 筛选/搜索实时响应
- 支持键盘导航
- 一键导出CSV/JSON

---

## 9. 配置管理

采用**交互式输入**方式配置API密钥：

```python
class ConfigManager:
    """配置管理器"""

    def __init__(self):
        self.config_file = "config.json"

    def setup(self):
        """首次运行时交互式配置"""
        print("=== 食品电商AI分析工具 配置向导 ===")

        print("\n【OCR配置 - 百度智能云】")
        print("请前往 https://console.bce.baidu.com/ai/#/ai/ocr/overview/index 获取")
        ocr_app_id = input("请输入 APP_ID: ")
        ocr_api_key = input("请输入 API_KEY: ")
        ocr_secret_key = input("请输入 SECRET_KEY: ")

        print("\n【大模型配置】")
        print("支持: deepseek / qwen / zhipu")
        llm_provider = input("请选择服务商 (默认: deepseek): ") or "deepseek"
        llm_api_key = input(f"请输入 {llm_provider} API Key: ")

        config = {
            "ocr": {
                "app_id": ocr_app_id,
                "api_key": ocr_api_key,
                "secret_key": ocr_secret_key
            },
            "llm": {
                "provider": llm_provider,
                "api_key": llm_api_key
            }
        }

        self.save(config)
        print("\n配置已保存！")

    def load(self):
        """加载配置"""
        if not os.path.exists(self.config_file):
            return self.setup()
        with open(self.config_file, 'r') as f:
            return json.load(f)
```

---

## 10. 主程序流程

```python
# main.py

def main():
    # 1. 配置检查
    config = ConfigManager().load()

    # 2. 数据采集
    print("开始数据采集...")
    crawler = TmallCrawler()
    products = crawler.crawl_top_brands(top_n=200)
    reviews = crawler.crawl_reviews(products)

    # 3. 数据存储
    print("保存数据...")
    db = DatabaseManager()
    db.save_products(products)
    db.save_reviews(reviews)

    # 4. OCR识别
    print("OCR识别配料表和营养成分表...")
    ocr = OCRProcessor(config['ocr'])
    ocr.process_all_products()

    # 5. 情感分析
    print("情感分析...")
    analyzer = SentimentAnalyzer(config['llm'])
    analyzer.analyze_all_reviews()

    # 6. 生成报告
    print("生成HTML报告...")
    ReportGenerator().generate()

    print("完成！请打开 output/report/index.html 查看结果")

if __name__ == "__main__":
    main()
```

---

## 11. 开发计划

### Phase 1: 核心爬虫（3-4天）
- [ ] 项目初始化，安装依赖
- [ ] DrissionPage基类封装
- [ ] 天猫爬虫实现
- [ ] SQLite数据库设计
- [ ] 数据存储逻辑

### Phase 2: 分析与展示（3-4天）
- [ ] 百度OCR集成
- [ ] 大模型API集成
- [ ] 情感分析逻辑
- [ ] 静态HTML报告生成
- [ ] 图表渲染

### Phase 3: 扩展平台（后续迭代）
- [ ] 京东爬虫
- [ ] 拼多多爬虫
- [ ] 多平台数据整合

---

## 12. 验证方案

### 功能验证
1. 爬虫测试：采集天猫TOP50食品品牌商品数据
2. OCR测试：手动上传配料表/营养成分表图片验证识别准确率
3. 情感分析测试：人工抽检100条评价分析结果

### 性能验证
1. 爬虫效率：单商品页面采集时间 < 5秒
2. OCR响应：单图片识别时间 < 3秒
3. 情感分析：批量处理速度 > 100条/分钟

### 数据验证
1. 数据完整性：商品信息字段完整率 > 95%
2. 评价覆盖：每商品评价采集数 > 100条
3. 分析准确率：情感分析准确率 > 85%

---

## 13. 风险与应对

| 风险 | 应对措施 |
|------|----------|
| 平台反爬升级 | 降低频率、增加随机等待、模拟人类行为 |
| OCR识别失败 | 人工校验机制，失败记录日志 |
| API调用限制 | 批量处理、合理限流、缓存结果 |
| 大模型成本 | 选择性价比高的模型、控制批量大小 |
