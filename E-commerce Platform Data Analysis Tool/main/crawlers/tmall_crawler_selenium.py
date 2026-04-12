import re
import json
import time
import logging
from typing import List, Dict, Optional
from urllib.parse import urljoin
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (TimeoutException,
                                      StaleElementReferenceException,
                                      NoSuchElementException)
from .selenium_base_crawler import SeleniumBaseCrawler


class TmallCrawlerSelenium(SeleniumBaseCrawler):
    """
    天猫爬虫 - Selenium版本
    
    特点：
    1. 完整的反检测机制
    2. 模拟人类行为（鼠标移动、滚动、随机等待）
    3. 多策略搜索和数据提取
    4. 强大的弹窗处理能力
    """

    def __init__(self, headless: bool = False):
        super().__init__(headless=headless, browser='edge')
        self.base_url = "https://www.tmall.com"
        self.logger = logging.getLogger(__name__)
        self._visited_urls = set()

    def _setup_anti_detection(self):
        """设置额外的天猫特定反检测"""
        try:
            # 设置特定的请求头
            self.driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {
                'headers': {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'Cache-Control': 'no-cache',
                    'Referer': 'https://www.tmall.com/'
                }
            })
            
            self.logger.debug("✅ 天猫特定反检测设置完成")
            
        except Exception as e:
            self.logger.warning(f"⚠️ 反检测设置失败: {e}")

    def search_products(self, keyword: str = "食品", page: int = 1, max_products: int = 50) -> List[Dict]:
        """
        搜索商品 - 多策略实现
        
        策略优先级：
        1. 淘宝搜索页面（带天猫筛选）
        2. 天猫列表搜索
        3. JavaScript 直接提取（备用）
        4. 分类页面导航（最后备用）
        
        Args:
            keyword: 搜索关键词
            page: 页码
            max_products: 最大采集数量
        Returns:
            商品列表
        """
        products = []
        
        try:
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"🔍 开始搜索商品: {keyword}")
            self.logger.info(f"{'='*60}\n")
            
            # 加载Cookie建立会话
            self.load_cookies()
            
            # 设置额外的反检测
            self._setup_anti_detection()
            
            # 搜索策略列表（按优先级排序）
            search_strategies = [
                f"https://s.taobao.com/search?fromTmallRedirect=true&tab=mall&q={keyword}&s={((page - 1) * 44)}",
                f"https://list.tmall.com/search_product.htm?q={keyword}&s={((page - 1) * 60)}",
            ]
            
            for idx, search_url in enumerate(search_strategies, 1):
                self.logger.info(f"\n📋 尝试搜索策略 {idx}/{len(search_strategies)}...")
                
                try:
                    # 打开搜索页面
                    success = self.open_page(search_url)
                    
                    if not success:
                        self.logger.warning(f"❌ 策略 {idx}: 页面打开失败")
                        continue
                    
                    # 额外等待让页面完全加载
                    self.human_like_wait(2, 4)
                    
                    current_url = self.driver.current_url
                    page_title = self.driver.title
                    
                    self.logger.info(f"   当前URL: {current_url[:80]}")
                    self.logger.info(f"   页面标题: {page_title[:50]}")
                    
                    # 检查是否被重定向到错误/登录页面
                    if any(kw in current_url.lower() for kw in ['error', 'login', 'passport']):
                        self.logger.warning(f"⚠️ 策略 {idx}: 被重定向到错误/登录页面")
                        continue
                    
                    if any(kw in page_title for kw in ['找不到', '登录']):
                        self.logger.warning(f"⚠️ 策略 {idx}: 页面显示异常内容")
                        continue
                    
                    # 模拟人类浏览行为
                    self.simulate_scrolling('down', distance=random.randint(200, 400))
                    self.human_like_wait(1, 2)
                    
                    # 查找商品元素
                    product_items = self._find_product_elements()
                    
                    if len(product_items) > 0:
                        self.logger.info(f"✅ 策略 {idx} 成功! 找到 {len(product_items)} 个商品元素")
                        
                        # 解析商品数据
                        for item_idx, item in enumerate(product_items[:max_products]):
                            try:
                                product_data = self._parse_product_item(item)
                                
                                if product_data and product_data.get('name'):
                                    products.append(product_data)
                                    self.logger.debug(
                                        f"   [{item_idx + 1}/{len(product_items)}] "
                                        f"{product_data['name'][:40]}..."
                                    )
                                    
                                    # 每10个商品模拟一次休息
                                    if (item_idx + 1) % 10 == 0:
                                        self.human_like_wait(1, 2)
                                        self.simulate_mouse_movement()
                                        
                            except Exception as e:
                                self.logger.warning(f"   解析商品项失败: {e}")
                                continue
                        
                        if products:
                            self.logger.info(f"\n🎉 策略 {idx} 成功采集 {len(products)} 个商品!")
                            break  # 成功获取数据，退出循环
                            
                    else:
                        self.logger.warning(f"⚠️ 策略 {idx}: 未找到商品元素")
                        
                        # 尝试JavaScript提取
                        self.logger.info("   🔄 尝试JavaScript直接提取...")
                        js_products = self._extract_products_via_javascript(max_products)
                        
                        if js_products:
                            self.logger.info(f"✅ JavaScript提取成功! 获取 {len(js_products)} 个商品")
                            products.extend(js_products)
                            break
                        else:
                            continue
                
                except Exception as e:
                    self.logger.error(f"❌ 策略 {idx} 执行异常: {e}")
                    import traceback
                    self.logger.debug(traceback.format_exc())
                    continue
            
            # 如果所有主要策略都失败，使用备用方案
            if not products:
                self.logger.warning("\n⚠️ 所有主要策略均未成功，尝试备用方案...")
                products = self._fallback_search(keyword, max_products)
            
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"📊 搜索完成! 共采集 {len(products)} 个商品")
            self.logger.info(f"{'='*60}\n")
            
        except Exception as e:
            self.logger.error(f"❌ 搜索商品过程异常: {e}")
            raise
        
        return products

    def _find_product_elements(self):
        """
        智能查找商品元素 - 多策略组合
        
        返回Selenium WebElement对象列表
        """
        elements = []
        
        # 策略1: 通过ID属性查找（最可靠）
        try:
            id_elements = self.find_elements_by_css('[id^="item_id_"]', timeout=5)
            if id_elements:
                self.logger.info(f"   ✅ 通过 [id^='item_id_'] 找到 {len(id_elements)} 个元素")
                elements = id_elements[:50]
                return elements
        except Exception as e:
            self.logger.debug(f"   策略1失败: {e}")
        
        # 策略2: 通过天猫详情链接查找
        try:
            link_elements = self.find_elements_by_css(
                'a[href*="detail.tmall.com/item.htm"]', timeout=5
            )
            if link_elements:
                visible_links = [el for el in link_elements if el.is_displayed()]
                if visible_links:
                    self.logger.info(f"   ✅ 通过天猫链接找到 {len(visible_links)} 个元素")
                    elements = visible_links[:50]
                    return elements
        except Exception as e:
            self.logger.debug(f"   策略2失败: {e}")
        
        # 策略3: 通过淘宝链接查找
        try:
            taobao_links = self.find_elements_by_css(
                'a[href*="item.taobao.com/item.htm"]', timeout=5
            )
            if taobao_links:
                visible_links = [el for el in taobao_links if el.is_displayed()]
                if visible_links:
                    self.logger.info(f"   ✅ 通过淘宝链接找到 {len(visible_links)} 个元素")
                    elements = visible_links[:50]
                    return elements
        except Exception as e:
            self.logger.debug(f"   策略3失败: {e}")
        
        # 策略4: 通过class特征查找
        class_selectors = [
            '[class*="doubleCardWrapperAdapt"]',
            '[class*="doubleCard"]',
            '[class*="productItem"]',
            '[class*="cardWrapper"]'
        ]
        
        for selector in class_selectors:
            try:
                items = self.find_elements_by_css(selector, timeout=3)
                if items:
                    self.logger.info(f"   ✅ 通过 '{selector}' 找到 {len(items)} 个元素")
                    elements = items[:50]
                    return elements
            except:
                continue
        
        if not elements:
            self.logger.warning("   ❌ 未找到任何商品元素")
        
        return elements

    def _parse_product_item(self, item) -> Optional[Dict]:
        """
        解析单个商品项 - 从WebElement提取数据
        """
        try:
            # 提取名称
            name_elem = None
            name_selectors = [
                '.productTitle',
                '[class*="titleText"]',
                '[class*="Title--"]',
                'tag:h2', 'tag:h3',
                '[class*="title"]'
            ]
            
            for selector in name_selectors:
                try:
                    name_elem = item.find_element(By.CSS_SELECTOR, selector)
                    if name_elem and name_elem.text.strip():
                        break
                except:
                    continue
            
            if not name_elem or not name_elem.text.strip():
                # 如果找不到子元素，尝试获取链接文本
                name = item.text.strip()[:150]
                if not name:
                    return None
            else:
                name = name_elem.text.strip()
            
            # 提取价格
            price = 0.0
            price_selectors = [
                '.productPrice',
                '[class*="price--"]',
                '[class*="Price--"]',
                '.price',
                '[class*="price"]'
            ]
            
            for selector in price_selectors:
                try:
                    price_elem = item.find_element(By.CSS_SELECTOR, selector)
                    price_text = price_elem.text.strip()
                    price_match = re.search(r'[\d.]+', price_text.replace(',', ''))
                    if price_match:
                        price = float(price_match.group())
                        break
                except:
                    continue
            
            # 提取销量
            sales = 0
            sales_selectors = [
                '.productSales',
                '[class*="sale"]',
                '[class*="count"]'
            ]
            
            for selector in sales_selectors:
                try:
                    sales_elem = item.find_element(By.CSS_SELECTOR, selector)
                    sales_text = sales_elem.text.strip()
                    sales_match = re.search(r'[\d]+', sales_text.replace('+', '').replace(',', ''))
                    if sales_match:
                        sales = int(sales_match.group())
                        break
                except:
                    continue
            
            # 提取店铺名
            shop_name = ''
            shop_selectors = [
                '.productShop-name',
                '[class*="shop"]',
                '[class*="store"]'
            ]
            
            for selector in shop_selectors:
                try:
                    shop_elem = item.find_element(By.CSS_SELECTOR, selector)
                    shop_name = shop_elem.text.strip()
                    if shop_name:
                        break
                except:
                    continue
            
            # 提取详情URL
            detail_url = ''
            link_selectors = [
                'tag:a@txt=查看详情',
                '.productTitle',
                'a[href*="detail.tmall.com"]',
                'a[href*="item.taobao.com"]'
            ]
            
            for selector in link_selectors:
                try:
                    link_elem = item.find_element(By.CSS_SELECTOR, selector.split('@')[0])
                    href = link_elem.get_attribute('href')
                    if href:
                        detail_url = href
                        if not detail_url.startswith('http'):
                            detail_url = urljoin(self.base_url, detail_url)
                        break
                except:
                    continue
            
            # 提取平台ID
            platform_id = self._extract_platform_id(detail_url)
            
            return {
                'platform_product_id': platform_id,
                'name': name[:150],
                'price': price,
                'sales_count': sales,
                'shop_name': shop_name,
                'detail_url': detail_url,
                'ingredient_img_url': None,
                'nutrition_img_url': None
            }
            
        except StaleElementReferenceException:
            self.logger.warning("元素已失效（StaleElement）")
            return None
        except Exception as e:
            self.logger.error(f"解析商品项异常: {e}")
            return None

    def _extract_platform_id(self, url: str) -> str:
        """从URL提取平台商品ID"""
        if not url:
            return ''
        match = re.search(r'id=(\d+)', url)
        return match.group(1) if match else ''

    def _extract_products_via_javascript(self, max_products: int = 50) -> List[Dict]:
        """
        使用纯JavaScript提取商品数据 - 当常规方法失败时的备用方案
        
        这种方法可以绕过一些复杂的DOM结构和动态加载问题
        """
        self.logger.info(f"\n   🔄 开始JavaScript提取 (max={max_products})...")
        
        try:
            # 先检查DOM状态
            check_js = '''
            (function() {
                var elements = document.querySelectorAll('[id^="item_id_"]');
                return {
                    count: elements.length,
                    firstId: elements.length > 0 ? elements[0].id : 'none',
                    firstHref: elements.length > 0 ? (elements[0].href || 'no href') : 'none'
                };
            })();
            '''
            
            check_result = self.execute_javascript(check_js)
            if check_result:
                count = check_result.get('count', 0)
                self.logger.info(f"   DOM检查: 找到 {count} 个 [id^='item_id_'] 元素")
                
                if count > 0:
                    self.logger.info(f"      第一个元素ID: {check_result.get('firstId')}")
            
            # 主要的JavaScript提取代码
            js_code = f'''
            (function() {{
                var products = [];
                
                // 查找所有商品元素
                var productElements = document.querySelectorAll('[id^="item_id_"]');
                
                console.log('[JS-Extract] Found productElements:', productElements.length);
                
                productElements.forEach(function(item, index) {{
                    if (index >= {max_products}) return;
                    
                    try {{
                        // 1. 提取商品ID和URL
                        var itemId = item.id.replace('item_id_', '') || '';
                        var url = item.href || '';
                        if (!url.startsWith('http')) {{
                            url = 'https:' + url;
                        }}
                        
                        // 2. 提取图片
                        var img = item.querySelector('img[class*="mainPic"]') ||
                                 item.querySelector('img');
                        var image = img ? (img.src || img.getAttribute('data-src') || '') : '';
                        if (image && !image.startsWith('http')) {{
                            image = 'https:' + image;
                        }}
                        
                        // 3. 提取标题
                        var title = '';
                        var titleSelectors = [
                            '[class*="titleText"]',
                            '[class*="Title--"]',
                            '.productTitle',
                            '[class*="name"]',
                            '[class*="Name"]'
                        ];
                        
                        for (var i = 0; i < titleSelectors.length; i++) {{
                            var titleEl = item.querySelector(titleSelectors[i]);
                            if (titleEl) {{
                                title = titleEl.textContent.trim();
                                if (title) break;
                            }}
                        }}
                        
                        if (!title) {{
                            title = item.textContent.substring(0, 200).trim();
                            title = title.replace(/\\s+/g, ' ').substring(0, 150);
                        }}
                        
                        // 4. 提取价格
                        var price = '';
                        var priceSelectors = [
                            '[class*="price--"]',
                            '[class*="Price--"]',
                            '.price',
                            '[class*="price"]'
                        ];
                        
                        for (var j = 0; j < priceSelectors.length; j++) {{
                            var priceEl = item.querySelector(priceSelectors[j]);
                            if (priceEl) {{
                                price = priceEl.textContent.trim();
                                if (price) break;
                            }}
                        }}
                        
                        price = price.replace(/[^0-9.¥元]/g, '');
                        
                        // 5. 提取销量
                        var sales = '';
                        var salesEl = item.querySelector('[class*="sale"], [class*="Sales"]');
                        if (salesEl) {{
                            sales = salesEl.textContent.trim();
                        }}
                        
                        // 6. 提取店铺名
                        var shop = '';
                        var shopEl = item.querySelector('[class*="shop"], [class*="Shop"], [class*="store"]');
                        if (shopEl) {{
                            shop = shopEl.textContent.trim();
                        }}
                        
                        // 只添加有效数据
                        if (title && itemId) {{
                            products.push({{
                                id: itemId,
                                name: title,
                                price: price,
                                url: url,
                                image: image,
                                sales: sales,
                                shop: shop,
                                platform: url.includes('tmall.com') ? '天猫' : '淘宝'
                            }});
                            
                            if (products.length <= 3) {{
                                console.log('[JS-Extract] Product #' + products.length + ':', 
                                           title.substring(0, 50));
                            }}
                        }}
                        
                    }} catch(e) {{
                        console.error('Error parsing item:', e);
                    }}
                }});
                
                console.log('[JS-Extract] Total products extracted:', products.length);
                return products;
            }})();
            '''
            
            # 执行JavaScript并获取结果
            result = self.execute_javascript(js_code)
            
            self.logger.info(f"   run_js() 返回值类型: {type(result).__name__}")
            
            if result is None:
                self.logger.warning("   ⚠️ 返回值为None")
                return []
            elif isinstance(result, list):
                if len(result) > 0:
                    self.logger.info(f"   ✅ JavaScript成功提取 {len(result)} 个商品!")
                    
                    # 转换为统一格式
                    converted_products = []
                    for item in result:
                        converted_products.append({
                            'platform_product_id': item.get('id', ''),
                            'name': item.get('name', ''),
                            'price': float(re.sub(r'[^0-9.]', '', str(item.get('price', '0'))) or 0),
                            'sales_count': int(re.sub(r'[^0-9]', '', str(item.get('sales', '0'))) or 0),
                            'shop_name': item.get('shop', ''),
                            'detail_url': item.get('url', ''),
                            'ingredient_img_url': None,
                            'nutrition_img_url': None
                        })
                    
                    return converted_products
                else:
                    self.logger.warning("   ⚠️ 返回空列表")
                    return []
            else:
                self.logger.warning(f"   ⚠️ 返回值类型异常: {type(result)}")
                return []
                
        except Exception as e:
            self.logger.error(f"   ❌ JavaScript提取异常: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return []

    def get_product_detail(self, product_url: str) -> Dict:
        """
        获取商品详情页信息
        
        Args:
            product_url: 商品详情页URL
        Returns:
            商品详情字典
        """
        detail_data = {}
        
        try:
            self.logger.info(f"\n📄 正在获取商品详情: {product_url[:60]}...")
            
            self.open_page(product_url)
            self.human_like_wait(2, 3)
            
            detail_data['detail_url'] = product_url
            
            # 提取标题
            title_selectors = [
                '.ItemHeader--mainTitle--3CIjwTM',
                '[class*="mainTitle"]',
                'h1',
                '[class*="title"]'
            ]
            
            for selector in title_selectors:
                title_elem = self.find_element_by_css(selector, timeout=3)
                if title_elem:
                    detail_data['name'] = self.safe_get_text(title_elem)
                    break
            
            if 'name' not in detail_data:
                detail_data['name'] = self.driver.title
            
            # 提取价格
            price_selectors = [
                '.Price--priceText--2nBRPpf',
                '[class*="priceText"]',
                '[class*="price"]',
                '.price'
            ]
            
            for selector in price_selectors:
                price_elem = self.find_element_by_css(selector, timeout=3)
                if price_elem:
                    price_text = self.safe_get_text(price_elem, '0')
                    price_match = re.search(r'[\d.]+', price_text.replace(',', ''))
                    detail_data['price'] = float(price_match.group()) if price_match else 0.0
                    break
            
            if 'price' not in detail_data:
                detail_data['price'] = 0.0
            
            # 提取店铺名
            shop_selectors = [
                '.ShopInfo--TextAndPic--yH0AZfx',
                '[class*="ShopInfo"]',
                '[class*="shopName"]'
            ]
            
            for selector in shop_selectors:
                shop_elem = self.find_element_by_css(selector, timeout=3)
                if shop_elem:
                    detail_data['shop_name'] = self.safe_get_text(shop_elem)
                    break
            
            # 查找配料表和营养成分表图片
            detail_images = self._find_detail_images()
            detail_data['ingredient_img_url'] = detail_images.get('ingredient')
            detail_data['nutrition_img_url'] = detail_images.get('nutrition')
            
            self.logger.info(f"   ✅ 详情获取成功: {detail_data.get('name', 'Unknown')[:40]}")
            
        except Exception as e:
            self.logger.error(f"   ❌ 获取商品详情失败: {e}")
            raise
        
        return detail_data

    def _find_detail_images(self) -> Dict[str, Optional[str]]:
        """
        在详情页查找配料表和营养成分表图片
        Returns:
            {'ingredient': url, 'nutrition': url}
        """
        images = {'ingredient': None, 'nutrition': None}
        
        try:
            # 滚动页面以加载图片
            self.simulate_scrolling('down', distance=500)
            self.human_like_wait(1, 2)
            
            img_selectors = [
                '.Content--image--2vXlCh6 img',
                '[class*="content"] img',
                '[class*="detail"] img',
                '#J_DivItemDesc img'
            ]
            
            for selector in img_selectors:
                img_elements = self.find_elements_by_css(selector, timeout=3)
                
                for img in img_elements:
                    try:
                        src = self.safe_get_attr(img, 'src', '')
                        alt_text = self.safe_get_attr(img, 'alt', '').lower()
                        
                        # 根据alt文本或src判断图片类型
                        if any(kw in alt_text for kw in ['配料', '成分', '原料']):
                            images['ingredient'] = src
                        elif any(kw in src.lower() for kw in ['ingredient', 'pei', 'lia']):
                            images['ingredient'] = src
                            
                        if any(kw in alt_text for kw in ['营养', '成分表', '能量']):
                            images['nutrition'] = src
                        elif any(kw in src.lower() for kw in ['nutrition', 'ying']):
                            images['nutrition'] = src
                        
                        # 如果都找到了，提前退出
                        if images['ingredient'] and images['nutrition']:
                            break
                            
                    except StaleElementReferenceException:
                        continue
                
                if images['ingredient'] and images['nutrition']:
                    break
                    
        except Exception as e:
            self.logger.warning(f"   ⚠️ 查找详情图片失败: {e}")
        
        return images

    def get_product_reviews(self, product_id: str, max_count: int = 100) -> List[Dict]:
        """
        获取商品评价
        
        Args:
            product_id: 平台商品ID
            max_count: 最大采集数量
        Returns:
            评价列表
        """
        reviews = []
        
        try:
            self.logger.info(f"\n💬 正在获取评价 (ID: {product_id}, 最大数量: {max_count})...")
            
            review_url = (
                f"https://rate.tmall.com/listDetailRate.htm?"
                f"itemId={product_id}&currentPage=1&pageSize={max_count}"
            )
            
            self.open_page(review_url)
            self.human_like_wait(2, 3)
            
            # 获取页面源码
            page_source = self.driver.page_source
            review_data = self._parse_review_response(page_source)
            
            if review_data:
                reviews = review_data.get('rateList', [])
                self.logger.info(f"   ✅ 获取到 {len(reviews)} 条评价")
            else:
                self.logger.warning("   ⚠️ 未找到评价数据")
                
        except Exception as e:
            self.logger.error(f"   ❌ 获取评价失败: {e}")
        
        return reviews

    def _parse_review_response(self, html_content: str) -> Optional[Dict]:
        """解析评价接口返回的数据"""
        try:
            match = re.search(r'jsonp\d+\((.*)\)', html_content)
            if match:
                data_str = match.group(1)
                return json.loads(data_str)
        except Exception as e:
            self.logger.error(f"解析评价数据失败: {e}")
        return None

    def _fallback_search(self, keyword: str, max_products: int) -> List[Dict]:
        """
        备用搜索方案 - 使用天猫分类导航
        """
        products = []
        
        try:
            self.logger.info("\n🔄 执行备用方案：使用天猫分类页面...")
            
            category_urls = [
                "https://www.tmall.com/category.htm?spm=a220m.1000862.0.0.5e8f6c7b",
                "https://pages.tmall.com/wow/s/act/tmall/tmall-map.html",
            ]
            
            for cat_url in category_urls:
                try:
                    self.open_page(cat_url)
                    self.human_like_wait(3, 4)
                    
                    # 查找所有商品链接
                    links = self.find_elements_by_css('a[href*="detail.tmall.com"]', timeout=10)
                    
                    visible_links = [link for link in links if link.is_displayed()]
                    
                    if len(visible_links) > 0:
                        self.logger.info(f"   分类页面找到 {len(visible_links)} 个商品链接")
                        
                        for link in visible_links[:max_products]:
                            try:
                                href = link.get_attribute('href')
                                name = link.text.strip()
                                
                                if name and href:
                                    if not href.startswith('http'):
                                        href = urljoin(self.base_url, href)
                                    
                                    products.append({
                                        'platform_product_id': self._extract_platform_id(href),
                                        'name': name[:150],
                                        'price': 0.0,
                                        'sales_count': 0,
                                        'shop_name': '',
                                        'detail_url': href,
                                        'ingredient_img_url': None,
                                        'nutrition_img_url': None
                                    })
                            except StaleElementReferenceException:
                                continue
                        
                        if products:
                            self.logger.info(f"   ✅ 备用方案成功! 获取 {len(products)} 个商品")
                            break
                            
                except Exception as e:
                    self.logger.warning(f"   分类URL访问失败: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"❌ 备用方案执行失败: {e}")
        
        return products

    def crawl_top_brands(self, category: str = "食品", top_n: int = 50) -> List[Dict]:
        """
        采集TOP N品牌商品数据（主入口）
        
        Args:
            category: 商品分类
            top_n: 采集数量
        Returns:
            商品数据列表
        """
        all_products = []
        
        self.logger.info(f"\n{'='*70}")
        self.logger.info(f"🚀 开始采集天猫{category}类目 TOP {top_n} 商品")
        self.logger.info(f"{'='*70}\n")
        
        # 第一步：搜索商品
        products = self.search_products(keyword=category, max_products=top_n)
        
        # 第二步：逐个获取详情
        for idx, product in enumerate(products, 1):
            try:
                self.logger.info(f"\n[{idx}/{len(products)}] 📦 正在采集: {product['name'][:50]}...")
                
                if product.get('detail_url'):
                    detail = self.get_product_detail(product['detail_url'])
                    product.update(detail)
                    
                    # 模拟人类浏览节奏
                    self.human_like_wait(2, 4)
                    self.simulate_mouse_movement()
                
                all_products.append(product)
                
            except Exception as e:
                self.logger.error(f"   ❌ 采集商品失败 [{product.get('name')}]: {e}")
                continue
        
        self.logger.info(f"\n{'='*70}")
        self.logger.info(f"🎉 采集完成！共获取 {len(all_products)} 个商品")
        self.logger.info(f"{'='*70}\n")
        
        return all_products

    def crawl_reviews_batch(self, products: List[Dict], max_reviews_per_product: int = 50) -> List[Dict]:
        """
        批量采集商品评价
        
        Args:
            products: 商品列表
            max_reviews_per_product: 每个商品最大评价数
        Returns:
            所有评价列表
        """
        all_reviews = []
        
        self.logger.info(f"\n{'='*70}")
        self.logger.info(f"💬 开始批量采集评价 ({len(products)} 个商品)")
        self.logger.info(f"{'='*70}\n")
        
        for idx, product in enumerate(products, 1):
            try:
                product_id = product.get('platform_product_id')
                if not product_id:
                    self.logger.warning(f"   [{idx}] 缺少商品ID，跳过")
                    continue
                
                self.logger.info(f"[{idx}/{len(products)}] 采集评价: {product.get('name', '')[:40]}...")
                
                reviews = self.get_product_reviews(product_id, max_reviews_per_product)
                
                for review in reviews:
                    review['product_id_temp'] = product.get('platform_product_id')
                    all_reviews.append(review)
                
                # 控制请求频率
                self.human_like_wait(1, 3)
                self.simulate_mouse_movement()
                
            except Exception as e:
                self.logger.error(f"   ❌ 采集评价失败: {e}")
                continue
        
        self.logger.info(f"\n{'='*70}")
        self.logger.info(f"✅ 评价采集完成！共获取 {len(all_reviews)} 条评价")
        self.logger.info(f"{'='*70}\n")
        
        return all_reviews


# 导入random模块用于scrolling方法
import random
