import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

class DatabaseManager:
    """SQLite数据库管理器"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / "data" / "food_analyzer.db"

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self.conn = None
        self._init_db()

    def _get_connection(self):
        """获取数据库连接"""
        if self.conn is None:
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def _init_db(self):
        """初始化数据库表结构"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS brands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                platform TEXT NOT NULL,
                category TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand_id INTEGER,
                platform_product_id TEXT UNIQUE,
                name TEXT NOT NULL,
                price REAL,
                sales_count INTEGER,
                shop_name TEXT,
                ingredient_img_url TEXT,
                nutrition_img_url TEXT,
                detail_url TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (brand_id) REFERENCES brands(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                review_id TEXT,
                user_name TEXT,
                rating INTEGER,
                content TEXT,
                review_time TEXT,
                sentiment TEXT,
                topic TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ingredient_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                ingredient_text TEXT,
                structured_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nutrition_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                nutrition_text TEXT,
                structured_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        ''')

        conn.commit()
        self.logger.info("数据库初始化完成")

    def insert_brand(self, name: str, platform: str, category: str = None) -> int:
        """插入品牌记录"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO brands (name, platform, category)
                VALUES (?, ?, ?)
            ''', (name, platform, category))
            conn.commit()
            brand_id = cursor.lastrowid
            self.logger.debug(f"插入品牌: {name}, ID: {brand_id}")
            return brand_id
        except Exception as e:
            self.logger.error(f"插入品牌失败: {e}")
            raise

    def insert_product(self, product_data: Dict) -> int:
        """插入商品记录"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO products 
                (brand_id, platform_product_id, name, price, sales_count, shop_name, 
                 ingredient_img_url, nutrition_img_url, detail_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                product_data.get('brand_id'),
                product_data.get('platform_product_id'),
                product_data.get('name'),
                product_data.get('price'),
                product_data.get('sales_count'),
                product_data.get('shop_name'),
                product_data.get('ingredient_img_url'),
                product_data.get('nutrition_img_url'),
                product_data.get('detail_url')
            ))
            conn.commit()
            product_id = cursor.lastrowid
            self.logger.debug(f"插入商品: {product_data.get('name')}, ID: {product_id}")
            return product_id
        except Exception as e:
            self.logger.error(f"插入商品失败: {e}")
            raise

    def insert_review(self, review_data: Dict) -> int:
        """插入评价记录"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO reviews 
                (product_id, review_id, user_name, rating, content, review_time, sentiment, topic)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                review_data.get('product_id'),
                review_data.get('review_id'),
                review_data.get('user_name'),
                review_data.get('rating'),
                review_data.get('content'),
                review_data.get('review_time'),
                review_data.get('sentiment'),
                review_data.get('topic')
            ))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"插入评价失败: {e}")
            raise

    def insert_ingredient_result(self, product_id: int, ingredient_text: str, structured_data: Dict):
        """插入配料识别结果"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO ingredient_results 
                (product_id, ingredient_text, structured_data)
                VALUES (?, ?, ?)
            ''', (product_id, ingredient_text, json.dumps(structured_data, ensure_ascii=False)))
            conn.commit()
            self.logger.debug(f"保存配料识别结果, 商品ID: {product_id}")
        except Exception as e:
            self.logger.error(f"保存配料识别结果失败: {e}")
            raise

    def insert_nutrition_result(self, product_id: int, nutrition_text: str, structured_data: Dict):
        """插入营养成分识别结果"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO nutrition_results 
                (product_id, nutrition_text, structured_data)
                VALUES (?, ?, ?)
            ''', (product_id, nutrition_text, json.dumps(structured_data, ensure_ascii=False)))
            conn.commit()
            self.logger.debug(f"保存营养成分识别结果, 商品ID: {product_id}")
        except Exception as e:
            self.logger.error(f"保存营养成分识别结果失败: {e}")
            raise

    def get_products(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """获取商品列表"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products ORDER BY id LIMIT ? OFFSET ?', (limit, offset))
        return [dict(row) for row in cursor.fetchall()]

    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """根据ID获取商品"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_reviews(self, product_id: int = None, limit: int = 100) -> List[Dict]:
        """获取评价列表"""
        conn = self._get_connection()
        cursor = conn.cursor()
        if product_id:
            cursor.execute('SELECT * FROM reviews WHERE product_id = ? ORDER BY id LIMIT ?', 
                          (product_id, limit))
        else:
            cursor.execute('SELECT * FROM reviews ORDER BY id LIMIT ?', (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def get_unanalyzed_reviews(self, limit: int = 50) -> List[Dict]:
        """获取未分析的评价"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM reviews 
            WHERE sentiment IS NULL 
            ORDER BY id 
            LIMIT ?
        ''', (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def update_review_sentiment(self, review_id: int, sentiment: str, topic: str):
        """更新评价的情感分析结果"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE reviews SET sentiment = ?, topic = ? WHERE id = ?
        ''', (sentiment, topic, review_id))
        conn.commit()

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        conn = self._get_connection()
        cursor = conn.cursor()

        stats = {}
        
        cursor.execute('SELECT COUNT(*) as count FROM products')
        stats['total_products'] = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM reviews')
        stats['total_reviews'] = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM brands')
        stats['total_brands'] = cursor.fetchone()['count']
        
        cursor.execute('SELECT AVG(rating) as avg_rating FROM reviews WHERE rating IS NOT NULL')
        result = cursor.fetchone()
        stats['avg_rating'] = round(result['avg_rating'], 2) if result['avg_rating'] else 0
        
        cursor.execute('''
            SELECT sentiment, COUNT(*) as count 
            FROM reviews 
            WHERE sentiment IS NOT NULL 
            GROUP BY sentiment
        ''')
        stats['sentiment_distribution'] = {row['sentiment']: row['count'] for row in cursor.fetchall()}
        
        return stats

    def export_to_json(self, output_path: str):
        """导出数据为JSON"""
        data = {
            'products': self.get_products(limit=10000),
            'reviews': self.get_reviews(limit=10000),
            'statistics': self.get_statistics(),
            'export_time': datetime.now().isoformat()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.info(f"数据已导出到: {output_path}")

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None
