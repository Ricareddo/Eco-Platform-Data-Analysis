import json
import time
import logging
import re
from typing import Dict, List, Optional
from openai import OpenAI

class SentimentAnalyzer:
    """评价情感分析器 - 使用大模型API进行情感极性和主题标注"""

    def __init__(self, config: Dict = None):
        self.logger = logging.getLogger(__name__)

        if config is None:
            from config.config_manager import ConfigManager
            config_manager = ConfigManager()
            config = config_manager.get_llm_config()

        try:
            self.client = OpenAI(
                api_key=config['api_key'],
                base_url=config.get('base_url', 'https://api.deepseek.com/v1')
            )
            self.model_name = self._get_model_name(config.get('provider', 'deepseek'))
            self.logger.info(f"大模型客户端初始化成功: {config.get('provider')}")
        except Exception as e:
            self.logger.error(f"大模型客户端初始化失败: {e}")
            raise

    def _get_model_name(self, provider: str) -> str:
        """根据服务商获取模型名称"""
        models = {
            'deepseek': 'deepseek-chat',
            'qwen': 'qwen-turbo',
            'zhipu': 'glm-4-flash'
        }
        return models.get(provider, 'deepseek-chat')

    def analyze_single(self, review_text: str) -> Dict:
        """
        分析单条评价的情感和主题
        Args:
            review_text: 评价内容
        Returns:
            {'sentiment': str, 'topic': str, 'keyword': List[str]}
        """
        prompt = f"""请分析以下食品类商品用户评价的情感倾向和主题：

评价内容：{review_text}

请严格按以下JSON格式返回，不要包含其他文字：
{{
    "sentiment": "正面/中性/负面",
    "topic": "口感/健康/包装/价格/其他",
    "keywords": ["关键词1", "关键词2"]
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "你是一个专业的电商评论情感分析师，专门分析食品类商品的用户评价。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )

            result_text = response.choices[0].message.content.strip()
            
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                
                sentiment = result.get('sentiment', '中性')
                topic = result.get('topic', '其他')
                keywords = result.get('keywords', [])
                
                valid_sentiments = ['正面', '中性', '负面']
                valid_topics = ['口感', '健康', '包装', '价格', '其他']
                
                return {
                    'sentiment': sentiment if sentiment in valid_sentiments else '中性',
                    'topic': topic if topic in valid_topics else '其他',
                    'keywords': keywords[:3]
                }
            
            return {'sentiment': '中性', 'topic': '其他', 'keywords': []}

        except Exception as e:
            self.logger.error(f"情感分析失败: {e}")
            return {'sentiment': '中性', 'topic': '其他', 'keywords': []}

    def batch_analyze(self, reviews: List[Dict], batch_size: int = 20) -> List[Dict]:
        """
        批量分析评价
        Args:
            reviews: 评价列表 [{'id': int, 'content': str}, ...]
            batch_size: 批次大小
        Returns:
            分析结果列表
        """
        results = []
        total = len(reviews)

        for i in range(0, total, batch_size):
            batch = reviews[i:i + batch_size]
            self.logger.info(f"正在分析批次 {(i // batch_size) + 1}/{(total + batch_size - 1) // batch_size}")

            for review in batch:
                try:
                    analysis = self.analyze_single(review.get('content', ''))
                    results.append({
                        'review_id': review.get('id'),
                        **analysis
                    })
                    
                    time.sleep(0.5)
                    
                except Exception as e:
                    self.logger.error(f"分析单条评价失败 [{review.get('id')}]: {e}")
                    results.append({
                        'review_id': review.get('id'),
                        'sentiment': '中性',
                        'topic': '其他',
                        'keywords': [],
                        'error': str(e)
                    })

            time.sleep(1)

        return results

    def analyze_all_reviews(self, db_manager=None):
        """分析所有未处理的评价"""
        if db_manager is None:
            from database.db_manager import DatabaseManager
            db_manager = DatabaseManager()

        unanalyzed_reviews = db_manager.get_unanalyzed_reviews(limit=100)
        
        if not unanalyzed_reviews:
            self.logger.info("没有需要分析的评价")
            return

        self.logger.info(f"开始分析 {len(unanalyzed_reviews)} 条未分析的评价")

        results = self.batch_analyze(unanalyzed_reviews)

        success_count = 0
        for result in results:
            try:
                db_manager.update_review_sentiment(
                    review_id=result['review_id'],
                    sentiment=result['sentiment'],
                    topic=result['topic']
                )
                success_count += 1
            except Exception as e:
                self.logger.error(f"更新评价分析结果失败: {e}")

        self.logger.info(f"情感分析完成！成功更新 {success_count}/{len(results)} 条")

    def get_sentiment_statistics(self, reviews: List[Dict]) -> Dict:
        """获取情感统计信息"""
        stats = {
            'total': len(reviews),
            'positive': 0,
            'neutral': 0,
            'negative': 0,
            'topics': {},
            'top_keywords': {}
        }

        for review in reviews:
            sentiment = review.get('sentiment', '中性')
            if sentiment == '正面':
                stats['positive'] += 1
            elif sentiment == '负面':
                stats['negative'] += 1
            else:
                stats['neutral'] += 1

            topic = review.get('topic', '其他')
            stats['topics'][topic] = stats['topics'].get(topic, 0) + 1

            keywords = review.get('keywords', [])
            for kw in keywords:
                stats['top_keywords'][kw] = stats['top_keywords'].get(kw, 0) + 1

        stats['top_keywords'] = dict(sorted(stats['top_keywords'].items(), 
                                           key=lambda x: x[1], reverse=True)[:20])

        return stats
