import logging
import multiprocessing
from typing import List, Dict, Optional
from crawlers.tmall_crawler import TmallCrawler

class CrawlerScheduler:
    """多进程爬虫调度器"""

    def __init__(self, max_workers: int = 3):
        self.max_workers = min(max_workers, multiprocessing.cpu_count())
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"初始化调度器，最大工作进程数: {self.max_workers}")

    def crawl_products_parallel(self, keywords: List[str], products_per_keyword: int = 20) -> List[Dict]:
        """
        并行采集多个关键词的商品数据
        Args:
            keywords: 搜索关键词列表
            products_per_keyword: 每个关键词采集数量
        Returns:
            所有商品列表
        """
        all_products = []
        
        if len(keywords) <= 1 or self.max_workers <= 1:
            for keyword in keywords:
                try:
                    with TmallCrawler(headless=True) as crawler:
                        products = crawler.search_products(
                            keyword=keyword, 
                            max_products=products_per_keyword
                        )
                        all_products.extend(products)
                except Exception as e:
                    self.logger.error(f"采集失败 [{keyword}]: {e}")
            
            return all_products
        
        self.logger.info(f"开始并行采集 {len(keywords)} 个关键词")
        
        with multiprocessing.Pool(processes=self.max_workers) as pool:
            results = pool.starmap(
                self._crawl_single_keyword,
                [(keyword, products_per_keyword) for keyword in keywords]
            )
            
            for products in results:
                if products:
                    all_products.extend(products)
        
        self.logger.info(f"并行采集完成，共获取 {len(all_products)} 个商品")
        return all_products

    @staticmethod
    def _crawl_single_keyword(keyword: str, max_count: int) -> List[Dict]:
        """单个关键词的采集任务（用于多进程）"""
        try:
            with TmallCrawler(headless=True) as crawler:
                return crawler.search_products(keyword=keyword, max_products=max_count)
        except Exception as e:
            logging.getLogger(__name__).error(f"采集失败 [{keyword}]: {e}")
            return []

    def crawl_with_retry(self, crawler_func, max_retries: int = 3, **kwargs):
        """
        带重试机制的采集
        Args:
            crawler_func: 采集函数
            max_retries: 最大重试次数
            **kwargs: 函数参数
        Returns:
            采集结果或None
        """
        for attempt in range(max_retries):
            try:
                result = crawler_func(**kwargs)
                return result
            except Exception as e:
                self.logger.warning(f"采集失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2 ** (attempt + 1))
        
        self.logger.error(f"采集最终失败，已重试 {max_retries} 次")
        return None

    def run_sequential(self, tasks: List[Dict]) -> List[Dict]:
        """
        顺序执行多个采集任务
        Args:
            tasks: 任务列表 [{'func': callable, 'args': {}, 'desc': str}, ...]
        Returns:
            所有结果列表
        """
        results = []
        
        for idx, task in enumerate(tasks, 1):
            desc = task.get('desc', f'任务{idx}')
            func = task.get('func')
            args = task.get('args', {})
            
            self.logger.info(f"[{idx}/{len(tasks)}] 执行: {desc}")
            
            try:
                result = self.crawl_with_retry(func, **args)
                if result:
                    results.extend(result if isinstance(result, list) else [result])
            except Exception as e:
                self.logger.error(f"任务执行失败 [{desc}]: {e}")
                continue
        
        return results
