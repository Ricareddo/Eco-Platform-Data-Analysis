"""
Utils - 数据采集工具集
智能爬虫控制 | 多策略采集 | 数据提取
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path


class DataCollector:
    """数据采集工具类 - 封装所有采集相关功能"""

    def __init__(self, headless: bool = False):
        """
        初始化数据采集器
        
        Args:
            headless: 是否使用无头模式（不显示浏览器窗口）
        """
        self.headless = headless
        self.crawler = None

    def get_project_root(self) -> Path:
        """获取项目根目录"""
        return Path(__file__).parent.parent

    def get_output_dir(self) -> Path:
        """获取输出目录"""
        output_dir = self.get_project_root() / "output"
        output_dir.mkdir(exist_ok=True)
        return output_dir

    def initialize_crawler(self):
        """初始化爬虫实例"""
        try:
            from crawlers.tmall_crawler_selenium import TmallCrawlerSelenium
            
            self.crawler = TmallCrawlerSelenium(headless=self.headless)
            self.crawler.load_cookies()
            return True
            
        except Exception as e:
            print(f"[ERROR] 初始化爬虫失败: {e}")
            return False

    def search_products(self, keyword: str, max_products: int = 50) -> list:
        """
        搜索商品
        
        Args:
            keyword: 搜索关键词
            max_products: 最大商品数量
            
        Returns:
            list: 商品列表
        """
        if not self.crawler:
            if not self.initialize_crawler():
                return []
        
        try:
            products = self.crawler.search_products(
                keyword=keyword,
                max_products=max_products
            )
            return products
            
        except Exception as e:
            print(f"[ERROR] 搜索商品失败: {e}")
            return []

    def extract_detail_urls(self, max_urls: int = 10) -> list:
        """
        高级URL提取 - 使用多策略
        
        Args:
            max_urls: 最大URL数量
            
        Returns:
            list: URL列表
        """
        if not self.crawler:
            return []
            
        strategies = [
            {
                'name': 'Strategy 1: ID-based elements',
                'js': '''
                (function() {
                    var results = [];
                    var items = document.querySelectorAll('[id^="item_id_"]');
                    for (var i = 0; i < Math.min(items.length, ''' + str(max_urls) + '''); i++) {
                        var item = items[i];
                        var href = item.href || item.getAttribute('data-href') || '';
                        var id = item.id.replace('item_id_', '') || '';
                        if (href && id) {
                            if (!href.startsWith('http')) href = 'https:' + href;
                            results.push({id: id, url: href, name: (item.textContent || '').substring(0, 100).trim()});
                        }
                    }
                    return results;
                })()
                '''
            },
            {
                'name': 'Strategy 2: Tmall detail links',
                'js': '''
                (function() {
                    var results = [];
                    var links = document.querySelectorAll('a[href*="detail.tmall.com"]');
                    for (var i = 0; i < Math.min(links.length, ''' + str(max_urls) + '''); i++) {
                        var link = links[i];
                        var href = link.href || '';
                        if (href && link.textContent.trim().length > 5) {
                            if (!href.startsWith('http')) href = 'https:' + href;
                            var idMatch = href.match(/id=(\\d+)/);
                            results.push({
                                id: idMatch ? idMatch[1] : '',
                                url: href,
                                name: link.textContent.trim().substring(0, 100)
                            });
                        }
                    }
                    return results;
                })()
                '''
            }
        ]
        
        for strategy in strategies:
            try:
                result = self.crawler.execute_javascript(strategy['js'])
                
                if result and isinstance(result, list) and len(result) > 0:
                    print(f"[SUCCESS] {strategy['name']}: Found {len(result)} URLs")
                    return result
                    
            except Exception as e:
                print(f"[FAILED] {strategy['name']}: {str(e)[:50]}")
        
        return []

    def collect_product_details(self, products: list, max_details: int = 10) -> int:
        """
        采集商品详情
        
        Args:
            products: 商品列表
            max_details: 最大详情数量
            
        Returns:
            int: 成功采集的数量
        """
        if not self.crawler:
            return 0
        
        detail_success = 0
        products_with_details = sum(1 for p in products if p.get('detail_url'))
        
        if products_with_details == 0:
            print("[INFO] No detail URLs available")
            return 0
        
        for idx, product in enumerate(products):
            if not product.get('detail_url'):
                continue
                
            if detail_success >= min(max_details, products_with_details):
                break
            
            try:
                print(f"[{detail_success+1}] Fetching: {product['name'][:45]}...", end='')
                
                detail_start = time.time()
                detail = self.crawler.get_product_detail(product['detail_url'])
                detail_time = time.time() - detail_start
                
                if detail:
                    product.update(detail)
                    detail_success += 1
                    print(f" OK ({detail_time:.1f}s)")
                else:
                    print(f" FAILED ({detail_time:.1f}s)")
                    
            except Exception as e:
                print(f" ERROR: {str(e)[:50]}")
            
            # 人性化等待
            time.sleep(1.5 + (idx % 3))
        
        return detail_success

    def save_results(self, products: list, keyword: str = "食品", is_test: bool = False) -> dict:
        """
        保存采集结果
        
        Args:
            products: 商品列表
            keyword: 搜索关键词
            is_test: 是否为测试模式
            
        Returns:
            dict: 保存结果信息
        """
        output_dir = self.get_output_dir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if is_test:
            json_file = output_dir / f'test_crawl_{timestamp}.json'
        else:
            json_file = output_dir / f'intelligent_crawl_{timestamp}.json'
        
        # 保存JSON
        data = {
            'metadata': {
                'crawl_time': datetime.now().isoformat(),
                'keyword': keyword,
                'total_products': len(products),
                'mode': 'test' if is_test else 'full'
            },
            'products': products
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 保存CSV
        csv_file = output_dir / f'{("test_" if is_test else "intelligent_")}{timestamp}.csv'
        with open(csv_file, 'w', encoding='utf-8-sig') as f:
            f.write("ID,Name,Price,Shop,Detail_URL\n")
            for idx, p in enumerate(products, 1):
                name = p.get('name', '').replace(',', '；')
                shop = p.get('shop_name', '').replace('\n', ' ').replace(',', '；')
                url = p.get('detail_url', '')
                f.write(f'{idx},"{name}",{p.get("price", 0)},"{shop}","{url}"\n')
        
        return {
            'json_file': str(json_file),
            'csv_file': str(csv_file),
            'product_count': len(products),
            'timestamp': timestamp
        }

    def close(self):
        """关闭爬虫"""
        if self.crawler:
            try:
                self.crawler.save_cookies()
                self.crawler.close()
            except:
                pass
            finally:
                self.crawler = None


def run_intelligent_crawl(keyword: str = "食品", max_products: int = 50, 
                          headless: bool = False, is_test: bool = False) -> bool:
    """
    运行智能数据采集（便捷函数）
    
    Args:
        keyword: 搜索关键词
        max_products: 商品数量上限
        headless: 无头模式
        is_test: 测试模式
        
    Returns:
        bool: 是否成功
    """
    print("\n" + "="*80)
    print("  INTELLIGENT DATA COLLECTOR - Multi-Strategy URL Extraction")
    print("="*80)
    
    collector = DataCollector(headless=headless)
    
    try:
        # 初始化
        print("[1/5] Initializing crawler...")
        if not collector.initialize_crawler():
            return False
        print("     OK\n")
        
        # 搜索
        count = 10 if is_test else max_products
        print(f"[2/5] Searching products (keyword={keyword}, max={count})...")
        start_time = time.time()
        products = collector.search_products(keyword=keyword, max_products=count)
        search_time = time.time() - start_time
        
        print(f"     ✓ Found {len(products)} products in {search_time:.2f}s\n")
        
        if not products:
            print("[ERROR] No products found!")
            collector.close()
            return False
        
        # 提取URL
        print("[3/5] Extracting detail URLs...")
        urls = collector.extract_detail_urls(max_urls=10)
        
        if urls:
            print(f"     ✓ Extracted {len(urls)} URLs\n")
            for idx, url_info in enumerate(urls[:count]):
                if idx < len(products):
                    products[idx]['platform_product_id'] = url_info.get('id', '')
                    products[idx]['detail_url'] = url_info.get('url', '')
        
        # 采集详情
        print("[4/5] Collecting details...")
        detail_success = collector.collect_product_details(products, max_details=10)
        print(f"\n     Collected details for {detail_success} products\n")
        
        # 保存结果
        print("[5/5] Saving results...")
        result = collector.save_results(products, keyword=keyword, is_test=is_test)
        print(f"     JSON: {result['json_file']}")
        print(f"     CSV:  {result['csv_file']}")
        
        collector.close()
        
        # 最终报告
        total_time = time.time() - start_time
        print("\n" + "="*80)
        print("FINAL REPORT:")
        print(f"  Products found:    {len(products)}")
        print(f"  Details collected: {detail_success}")
        print(f"  Total runtime:     {total_time:.2f}s")
        print("="*80 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        collector.close()
        return False
