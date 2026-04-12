import json
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from aip import AipOcr

class OCRProcessor:
    """百度OCR识别处理器 - 配料表与营养成分表结构化识别"""

    def __init__(self, config: Dict = None):
        self.logger = logging.getLogger(__name__)
        
        if config is None:
            from config.config_manager import ConfigManager
            config_manager = ConfigManager()
            config = config_manager.get_ocr_config()

        try:
            self.client = AipOcr(
                config['app_id'],
                config['api_key'],
                config['secret_key']
            )
            self.logger.info("百度OCR客户端初始化成功")
        except Exception as e:
            self.logger.error(f"OCR客户端初始化失败: {e}")
            raise

    def recognize_ingredient(self, image_path: str) -> Dict:
        """
        识别配料表图片
        Args:
            image_path: 图片路径
        Returns:
            {'text': 原始文本, 'structured': 结构化数据}
        """
        result = {
            'text': '',
            'structured': {
                'ingredients': [],
                'allergens': [],
                'additives': []
            }
        }
        
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            ocr_result = self.client.basicGeneral(image_data)
            
            if 'words_result' in ocr_result:
                texts = [item['words'] for item in ocr_result['words_result']]
                result['text'] = '\n'.join(texts)
                result['structured'] = self._parse_ingredient_text(result['text'])
            
            self.logger.info(f"配料表识别完成: {image_path}")
            
        except Exception as e:
            self.logger.error(f"配料表识别失败 [{image_path}]: {e}")
        
        return result

    def recognize_nutrition(self, image_path: str) -> Dict:
        """
        识别营养成分表（表格识别）
        Args:
            image_path: 图片路径
        Returns:
            {'text': 原始文本, 'structured': 结构化营养数据}
        """
        result = {
            'text': '',
            'structured': {
                'energy': None,
                'protein': None,
                'fat': None,
                'carbohydrate': None,
                'sodium': None,
                'nutrients': []
            }
        }
        
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            ocr_result = self.client.tableRecognition(image_data)
            
            if 'result' in ocr_result:
                table_result = json.loads(ocr_result['result'])
                if 'tableBody' in table_result:
                    cells = []
                    for row in table_result['tableBody']:
                        for cell in row:
                            if cell.get('word'):
                                cells.append(cell['word'])
                    result['text'] = ' | '.join(cells)
                    result['structured'] = self._parse_nutrition_table(cells)
            
            self.logger.info(f"营养成分表识别完成: {image_path}")
            
        except Exception as e:
            self.logger.error(f"营养成分表识别失败 [{image_path}]: {e}")
        
        return result

    def _parse_ingredient_text(self, text: str) -> Dict:
        """解析配料表文本，提取结构化信息"""
        structured = {
            'ingredients': [],
            'allergens': [],
            'additives': []
        }
        
        allergen_keywords = ['含麸质', '花生', '大豆', '坚果', '牛奶', '鸡蛋', '鱼类', '甲壳类']
        additive_patterns = [
            r'[^、]+?(?:色素|香精|防腐剂|抗氧化剂|增稠剂|乳化剂|稳定剂|甜味剂)'
        ]
        
        lines = text.replace('\n', '，').split('，')
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 2:
                continue
            
            if any(keyword in line for keyword in allergen_keywords):
                structured['allergens'].append(line)
            
            import re
            for pattern in additive_patterns:
                if re.search(pattern, line):
                    structured['additives'].append(line)
                    break
            
            if line and not any(line in item for item in structured['allergens'] + structured['additives']):
                structured['ingredients'].append(line)
        
        return structured

    def _parse_nutrition_table(self, cells: List[str]) -> Dict:
        """解析营养成分表格"""
        nutrition_data = {
            'energy': None,
            'protein': None,
            'fat': None,
            'carbohydrate': None,
            'sodium': None,
            'nutrients': []
        }
        
        nutrition_keywords = {
            '能量': 'energy',
            '蛋白质': 'protein',
            '脂肪': 'fat',
            '碳水化合物': 'carbohydrate',
            '钠': 'sodium'
        }
        
        import re
        
        for i, cell in enumerate(cells):
            cell = cell.strip()
            for keyword, key in nutrition_keywords.items():
                if keyword in cell:
                    value_match = re.search(r'[\d.]+', cells[i+1] if i+1 < len(cells) else '')
                    if value_match:
                        nutrition_data[key] = float(value_match.group())
                    break
            
            if any(keyword in cell for keyword in nutrition_keywords.keys()):
                continue
            
            value_match = re.search(r'([\u4e00-\u9fa5]+)[：:\s]*([\d.]+)\s*(g|mg|kJ|kcal)?', cell)
            if value_match:
                nutrition_data['nutrients'].append({
                    'name': value_match.group(1),
                    'value': float(value_match.group(2)),
                    'unit': value_match.group(3) or 'g'
                })
        
        return nutrition_data

    def process_product_images(self, product_id: int, ingredient_img_url: str = None,
                              nutrition_img_url: str = None, download_dir: str = None) -> Tuple[Dict, Dict]:
        """
        处理单个商品的配料表和营养成分表图片
        Returns:
            (ingredient_result, nutrition_result)
        """
        import requests

        if download_dir is None:
            download_dir = Path(__file__).parent.parent / "output" / "images"
            download_dir.mkdir(parents=True, exist_ok=True)

        ingredient_result = {'text': '', 'structured': {}}
        nutrition_result = {'text': '', 'structured': {}}

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            if ingredient_img_url:
                img_path = download_dir / f"ingredient_{product_id}.jpg"
                try:
                    response = requests.get(ingredient_img_url, headers=headers, timeout=10)
                    response.raise_for_status()
                    with open(img_path, 'wb') as f:
                        f.write(response.content)
                    ingredient_result = self.recognize_ingredient(str(img_path))
                except Exception as e:
                    self.logger.warning(f"下载配料表图片失败: {e}")

            if nutrition_img_url:
                img_path = download_dir / f"nutrition_{product_id}.jpg"
                try:
                    response = requests.get(nutrition_img_url, headers=headers, timeout=10)
                    response.raise_for_status()
                    with open(img_path, 'wb') as f:
                        f.write(response.content)
                    nutrition_result = self.recognize_nutrition(str(img_path))
                except Exception as e:
                    self.logger.warning(f"下载营养成分表图片失败: {e}")

        except Exception as e:
            self.logger.error(f"处理商品图片失败: {e}")

        return ingredient_result, nutrition_result

    def process_all_products(self, db_manager=None):
        """批量处理所有商品的图片识别"""
        if db_manager is None:
            from database.db_manager import DatabaseManager
            db_manager = DatabaseManager()

        products = db_manager.get_products(limit=1000)
        self.logger.info(f"开始批量处理 {len(products)} 个商品的图片")

        success_count = 0
        fail_count = 0

        for idx, product in enumerate(products, 1):
            try:
                product_id = product['id']
                self.logger.info(f"[{idx}/{len(products)}] 处理商品ID: {product_id}")

                ingredient_result, nutrition_result = self.process_product_images(
                    product_id=product_id,
                    ingredient_img_url=product.get('ingredient_img_url'),
                    nutrition_img_url=product.get('nutrition_img_url')
                )

                if ingredient_result.get('text'):
                    db_manager.insert_ingredient_result(
                        product_id, 
                        ingredient_result['text'], 
                        ingredient_result['structured']
                    )

                if nutrition_result.get('text'):
                    db_manager.insert_nutrition_result(
                        product_id, 
                        nutrition_result['text'], 
                        nutrition_result['structured']
                    )

                success_count += 1
                import time
                time.sleep(0.5)

            except Exception as e:
                self.logger.error(f"处理商品失败 [{product.get('name')}]: {e}")
                fail_count += 1
                continue

        self.logger.info(f"批量处理完成！成功: {success_count}, 失败: {fail_count}")
