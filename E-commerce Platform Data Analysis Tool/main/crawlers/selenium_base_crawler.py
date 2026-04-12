import random
import time
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.common.exceptions import (TimeoutException, 
                                      NoSuchElementException, 
                                      StaleElementReferenceException,
                                      WebDriverException)
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.chrome import ChromeDriverManager


class SeleniumBaseCrawler(ABC):
    """Selenium 爬虫基类 - 封装通用操作和反检测措施"""

    def __init__(self, headless: bool = False, browser: str = 'edge'):
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config()
        
        try:
            self.driver = self._setup_browser(headless, browser)
            self._apply_anti_detection()
            self.logger.info(f"Browser started successfully: {browser} (headless={headless})")
        except Exception as e:
            self.logger.error(f"Browser startup failed: {e}")
            raise
        
        self.base_url = ""
        self.request_count = 0

    def _load_config(self) -> Dict:
        """加载爬虫配置"""
        try:
            from config.config_manager import ConfigManager
            config_manager = ConfigManager()
            return config_manager.get_crawler_config()
        except:
            return {
                'headless': False,
                'request_delay_min': 1,
                'request_delay_max': 3,
                'max_retries': 3
            }

    def _setup_browser(self, headless: bool, browser: str):
        """设置并启动浏览器 - 带完整反检测配置"""
        if browser == 'edge':
            from selenium.webdriver.edge.service import Service as EdgeService
            
            options = EdgeOptions()
            
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)
            
            options.add_argument('--disable-gpu')
            options.add_argument('--no-first-run')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-infobars')
            options.add_argument('--disable-background-networking')
            options.add_argument('--disable-client-side-phishing-detection')
            options.add_argument('--disable-sync')
            
            if headless:
                options.add_argument('--headless=new')
            
            try:
                service = EdgeService(EdgeChromiumDriverManager().install())
                driver = webdriver.Edge(service=service, options=options)
            except:
                driver = webdriver.Edge(options=options)
            
        elif browser == 'chrome':
            options = ChromeOptions()
            
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)
            
            if headless:
                options.add_argument('--headless=new')
            
            driver = webdriver.Chrome(options=options)
        else:
            raise ValueError(f"Unsupported browser: {browser}")
        
        screen_width = random.choice([1920, 1366, 1536, 1440])
        screen_height = random.choice([1080, 768, 864, 900])
        driver.set_window_size(screen_width, screen_height)
        
        x_pos = random.randint(0, 100)
        y_pos = random.randint(0, 50)
        driver.set_window_position(x_pos, y_pos)
        
        return driver

    def _apply_anti_detection(self):
        """应用全面的反检测措施 - 绕过自动化识别（增强版）"""
        try:
            # 第一层：核心属性伪装（基础版）
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    // 隐藏 webdriver 属性
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined,
                        configurable: true
                    });
                    
                    // 伪装插件信息
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5],
                        configurable: true
                    });
                    
                    // 伪装语言设置
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['zh-CN', 'zh', 'en'],
                        configurable: true
                    });
                    
                    // 伪造 Chrome 对象
                    window.chrome = {
                        runtime: {},
                        loadTimes: function() {},
                        csi: function() {},
                        app: {}
                    };
                    
                    // 权限查询伪装
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) =>
                        parameters.name === 'notifications' ?
                            Promise.resolve({ state: Notification.permission }) :
                            originalQuery(parameters);
                '''
            })
            
            # 第二层：高级反检测（针对淘宝/天猫）
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    // 隐藏 Selenium 特征
                    delete navigator.__proto__.webdriver;
                    
                    // 伪造 permissions
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) =>
                        parameters.name === 'notifications' ?
                            Promise.resolve({ state: Notification.permission }) :
                            originalQuery(parameters);
                    
                    // 伪装 WebGL 渲染器（防止指纹识别）
                    const getParameter = WebGLRenderingContext.prototype.getParameter;
                    WebGLRenderingContext.prototype.getParameter = function(parameter) {
                        if (parameter === 37445) {
                            return 'Intel Inc.';
                        }
                        if (parameter === 37446) {
                            return 'Intel Iris OpenGL Engine';
                        }
                        return getParameter.call(this, parameter);
                    };
                    
                    // 伪装 canvas 指纹
                    const toDataURL = HTMLCanvasElement.prototype.toDataURL;
                    HTMLCanvasElement.prototype.toDataURL = function(type) {
                        if (type === 'image/png' && this.width === 220 && this.height === 30) {
                            // 针对常见的验证码canvas
                            return toDataURL.call(this, type);
                        }
                        return toDataURL.apply(this, arguments);
                    };
                    
                    // 禁用自动化相关API检测
                    Object.defineProperty(navigator, 'maxTouchPoints', {
                        get: () => 0,
                        configurable: true
                    });
                    
                    // 伪造硬件并发数
                    Object.defineProperty(navigator, 'hardwareConcurrency', {
                        get: () => 8,
                        configurable: true
                    });
                    
                    // 伪造设备内存
                    Object.defineProperty(navigator, 'deviceMemory', {
                        get: () => 8,
                        configurable: true
                    });
                    
                    // 防止 navigator.platform 检测
                    Object.defineProperty(navigator, 'platform', {
                        get: () => 'Win32',
                        configurable: true
                    });
                    
                    // 伪装 connection 信息
                    Object.defineProperty(navigator, 'connection', {
                        get: () => ({
                            effectiveType: '4g',
                            rtt: 50,
                            downlink: 10
                        }),
                        configurable: true
                    });
                '''
            })
            
            # 第三层：User-Agent 伪装（使用最新Edge版本）
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'
            ]
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                'userAgent': random.choice(user_agents),
                'platform': 'Win32',
                'acceptLanguage': 'zh-CN,zh;q=0.9,en;q=0.8'
            })
            
            # 第四层：移除自动化相关的变量和属性
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    // 清除 $cdc_ 和 $chrome_ 变量（Selenium特征）
                    try {
                        for (const key of Object.keys(window)) {
                            if (key.startsWith('$cdc_') || key.startsWith('$chrome_') || key.startsWith('__')) {
                                delete window[key];
                            }
                        }
                    } catch(e) {}
                    
                    // 覆盖 toString 方法防止检测
                    const originalToString = Function.prototype.toString;
                    Function.prototype.toString = function() {
                        if (this === navigator.webdriver) {
                            return 'function webdriver() { [native code] }';
                        }
                        return originalToString.call(this);
                    };
                '''
            })
            
            self.logger.info("✅ 增强版反检测措施已应用")
            
        except Exception as e:
            self.logger.warning(f"⚠️ 反检测设置部分失败: {e}")

    def human_like_wait(self, min_sec: float = None, max_sec: float = None):
        """人类化随机等待 - 模拟真实用户行为模式"""
        min_sec = min_sec or self.config.get('request_delay_min', 1)
        max_sec = max_sec or self.config.get('request_delay_max', 3)
        
        base_wait = random.uniform(min_sec, max_sec)
        extra_delay = random.uniform(0, 0.5)
        
        total_wait = base_wait + extra_delay
        time.sleep(total_wait)
        
        return total_wait

    def simulate_mouse_movement(self):
        """模拟鼠标移动 - 增加真实感"""
        try:
            actions = ActionChains(self.driver)
            
            for _ in range(random.randint(1, 3)):
                x_offset = random.randint(-200, 200)
                y_offset = random.randint(-100, 100)
                actions.move_by_offset(x_offset, y_offset)
                actions.pause(random.uniform(0.05, 0.2))
            
            actions.perform()
            
        except Exception as e:
            self.logger.debug(f"Mouse movement simulation failed: {e}")

    def simulate_scrolling(self, direction: str = 'down', distance: int = None):
        """模拟人类滚动行为 - 不是瞬间滚动，而是渐进式"""
        distance = distance or random.randint(300, 800)
        
        try:
            if direction == 'down':
                steps = random.randint(3, 6)
                step_distance = distance // steps
                
                for i in range(steps):
                    self.driver.execute_script(f"window.scrollBy(0, {step_distance});")
                    time.sleep(random.uniform(0.1, 0.3))
                    
            elif direction == 'up':
                steps = random.randint(3, 6)
                step_distance = distance // steps
                
                for i in range(steps):
                    self.driver.execute_script(f"window.scrollBy(0, {-step_distance});")
                    time.sleep(random.uniform(0.1, 0.3))
            
            self.human_like_wait(0.3, 0.8)
            
        except Exception as e:
            self.logger.warning(f"Scrolling simulation failed: {e}")

    def open_page(self, url: str) -> bool:
        """打开页面 - 带重试机制和弹窗处理"""
        self.request_count += 1
        self.logger.info(f"Request #{self.request_count}: {url[:80]}...")
        
        max_retries = self.config.get('max_retries', 3)
        
        for attempt in range(max_retries):
            try:
                self.driver.get(url)
                
                time.sleep(2)
                
                self.start_popup_monitor(interval=3.0)
                
                self.close_login_popup(max_attempts=3)
                
                self.simulate_mouse_movement()
                self.human_like_wait()
                
                self.logger.info(f"Page opened successfully (attempt {attempt + 1}/{max_retries})")
                return True
                
            except Exception as e:
                self.logger.warning(f"Failed to open page (attempt {attempt + 1}/{max_retries}): {str(e)[:80]}")
                
                if attempt < max_retries - 1:
                    self.human_like_wait(2, 5)
                else:
                    raise
        
        return False

    def start_popup_monitor(self, interval: float = 3.0):
        """启动持续弹窗监控 - 使用 JavaScript 定时器"""
        try:
            monitor_js = f'''
            (function() {{
                if (window.__popupMonitorActive) {{
                    console.log('[Popup Monitor] Already running');
                    return;
                }}
                window.__popupMonitorActive = true;
                
                console.log('[Popup Monitor] Starting (interval: {interval}s)');
                
                function removeLoginPopups() {{
                    let removed = 0;
                    
                    const selectors = [
                        '[class*="login-dialog"]',
                        '[class*="login-box"]',
                        '[class*="tm-login"]',
                        '[class*="login-popup"]',
                        '[class*="login-layer"]',
                        '#login-dialog'
                    ];
                    
                    selectors.forEach(selector => {{
                        try {{
                            const elements = document.querySelectorAll(selector);
                            elements.forEach(el => {{
                                if (el && el.parentNode) {{
                                    el.style.display = 'none';
                                    setTimeout(() => {{
                                        if (el.parentNode) el.remove();
                                    }}, 100);
                                    removed++;
                                }}
                            }});
                        }} catch(e) {{}}
                    }});
                    
                    return removed;
                }}
                
                removeLoginPopups();
                
                setInterval(removeLoginPopups, {int(interval * 1000)});
                
                window.__popupMonitor = {{
                    isRunning: () => window.__popupMonitorActive,
                    stop: () => {{
                        window.__popupMonitorActive = false;
                    }},
                    forceClose: removeLoginPopups
                }};
                
                console.log('[Popup Monitor] Started');
            }})();
            '''
            
            self.driver.execute_script(monitor_js)
            time.sleep(0.5)
            
            status = self.driver.execute_script(
                'return window.__popupMonitor ? window.__popupMonitor.isRunning() : false'
            )
            
            if status:
                self.logger.info(f"Popup monitor started (interval: {interval}s)")
            else:
                self.logger.warning("Popup monitor may not have started properly")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start popup monitor: {e}")
            return False

    def stop_popup_monitor(self):
        """停止弹窗监控"""
        try:
            self.driver.execute_script('''
                if (window.__popupMonitor) {
                    window.__popupMonitor.stop();
                    return true;
                }
                return false;
            ''')
            self.logger.info("Popup monitor stopped")
            return True
        except Exception as e:
            self.logger.error(f"Failed to stop popup monitor: {e}")
            return False

    def close_login_popup(self, max_attempts: int = 10) -> bool:
        """关闭登录弹窗 - 多策略组合"""
        total_closed = 0
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            self.logger.debug(f"Closing popup attempt {attempt}/{max_attempts}")
            time.sleep(0.3)
            
            popup_found = False
            
            try:
                monitor_result = self.driver.execute_script('''
                    if (window.__popupMonitor) {
                        return window.__popupMonitor.forceClose();
                    }
                    return 0;
                ''')
                if monitor_result and monitor_result > 0:
                    self.logger.info(f"Monitor closed {monitor_result} popups")
                    total_closed += monitor_result
                    continue
            except:
                pass
            
            try:
                js_code = '''
                var selectors = [
                    '.login-dialog', '.modal-overlay',
                    '[class*="login-dialog"]', '[class*="login-box"]',
                    '[class*="tm-login"]', '#login-dialog'
                ];
                
                var removed = 0;
                selectors.forEach(function(selector) {
                    var elements = document.querySelectorAll(selector);
                    elements.forEach(function(el) {
                        el.style.display = 'none';
                        el.remove();
                        removed++;
                    });
                });
                
                var overlays = document.querySelectorAll('[style*="position: fixed"]');
                overlays.forEach(function(overlay) {
                    var rect = overlay.getBoundingClientRect();
                    if (rect.width > window.innerWidth * 0.9 && rect.height > window.innerHeight * 0.9) {
                        overlay.remove();
                        removed++;
                    }
                });
                
                return removed;
                '''
                
                removed_count = self.driver.execute_script(js_code)
                if removed_count and removed_count > 0:
                    self.logger.info(f"JS removed {removed_count} popups")
                    popup_found = True
                    total_closed += removed_count
                    continue
                    
            except Exception as e:
                self.logger.debug(f"JS method failed: {e}")
            
            close_selectors = [
                '#J_LoginClose', '.login-dialog-close', '.tm-login-close',
                '.close-btn', 'button.close', '[aria-label="Close"]',
                '[title="Close"]', '.modal-close'
            ]
            
            for selector in close_selectors:
                try:
                    elements = self.find_elements(selector)
                    for elem in elements:
                        if elem.is_displayed():
                            self._human_click(elem)
                            self.logger.info(f"Clicked close button: {selector}")
                            popup_found = True
                            total_closed += 1
                            time.sleep(0.8)
                            break
                    if popup_found:
                        break
                except:
                    continue
            
            if not popup_found:
                try:
                    ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                    popup_found = True
                    total_closed += 1
                    self.logger.debug("Used ESC key to close")
                except:
                    pass
            
            if not popup_found:
                time.sleep(1)
                remaining = self.driver.execute_script('''
                    var popups = document.querySelectorAll(
                        '[class*="login"], [class*="dialog"]'
                    );
                    var visibleCount = 0;
                    popups.forEach(function(p) {
                        if (p.offsetParent !== null) visibleCount++;
                    });
                    return visibleCount;
                ''')
                
                if not remaining or remaining == 0:
                    self.logger.info(f"All popups closed (total processed: {total_closed})")
                    break
        
        return total_closed > 0

    def _human_click(self, element):
        """模拟人类点击 - 带随机偏移"""
        try:
            actions = ActionChains(self.driver)
            
            actions.move_to_element(element)
            actions.pause(random.uniform(0.1, 0.3))
            actions.click()
            actions.perform()
            
        except Exception as e:
            element.click()

    def load_cookies(self, cookies_file: str = None) -> bool:
        """加载Cookie"""
        from pathlib import Path
        import json
        
        if cookies_file is None:
            cookies_file = Path(__file__).parent.parent / "config" / "cookies.json"
        
        if not Path(cookies_file).exists():
            self.logger.warning(f"Cookie file not found: {cookies_file}")
            return False
        
        try:
            with open(cookies_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except:
                    pass
            
            self.logger.info(f"Successfully loaded {len(cookies)} cookies")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load cookies: {e}")
            return False

    def save_cookies(self, cookies_file: str = None) -> bool:
        """保存Cookie"""
        from pathlib import Path
        import json
        
        if cookies_file is None:
            cookies_file = Path(__file__).parent.parent / "config" / "cookies.json"
        
        try:
            cookies = self.driver.get_cookies()
            
            with open(cookies_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Cookies saved to: {cookies_file}")
            print(f"\nCookies saved! Login state will be used next time")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save cookies: {e}")
            return False

    def find_element(self, by: By, selector: str, timeout: int = 10):
        """查找单个元素 - 带显式等待"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            return element
        except TimeoutException:
            self.logger.debug(f"Element not found [{selector}] (timeout {timeout}s)")
            return None
        except Exception as e:
            self.logger.debug(f"Element lookup exception [{selector}]: {e}")
            return None

    def find_elements(self, by: By, selector: str, timeout: int = 10):
        """查找多个元素"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            return self.driver.find_elements(by, selector)
        except TimeoutException:
            return []
        except Exception as e:
            self.logger.debug(f"Element list lookup exception [{selector}]: {e}")
            return []

    def find_element_by_css(self, css_selector: str, timeout: int = 10):
        """通过CSS选择器查找元素"""
        return self.find_element(By.CSS_SELECTOR, css_selector, timeout)

    def find_elements_by_css(self, css_selector: str, timeout: int = 10):
        """通过CSS选择器查找多个元素"""
        return self.find_elements(By.CSS_SELECTOR, css_selector, timeout)

    def safe_get_text(self, element, default: str = '') -> str:
        """安全获取元素文本"""
        if element is None:
            return default
        try:
            text = element.text.strip()
            return text if text else default
        except StaleElementReferenceException:
            return default
        except:
            return default

    def safe_get_attr(self, element, attr: str, default: str = '') -> str:
        """安全获取元素属性"""
        if element is None:
            return default
        try:
            value = element.get_attribute(attr)
            return value if value else default
        except StaleElementReferenceException:
            return default
        except:
            return default

    def execute_javascript(self, script: str, *args):
        """执行JavaScript代码"""
        try:
            return self.driver.execute_script(script, *args)
        except Exception as e:
            self.logger.error(f"JavaScript execution failed: {e}")
            return None

    def scroll_to_bottom(self):
        """滚动到页面底部"""
        try:
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            self.human_like_wait(1, 2)
        except Exception as e:
            self.logger.warning(f"Scroll to bottom failed: {e}")

    def download_image(self, url: str, save_path: str) -> bool:
        """下载图片"""
        import requests
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': self.base_url
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            self.logger.info(f"Image downloaded successfully: {save_path}")
            return True
        except Exception as e:
            self.logger.error(f"Image download failed [{url}]: {e}")
            return False

    def take_screenshot(self, filename: str = 'screenshot.png') -> bool:
        """截图保存"""
        try:
            from pathlib import Path
            output_dir = Path(__file__).parent.parent / "output"
            output_dir.mkdir(exist_ok=True)
            
            filepath = output_dir / filename
            self.driver.save_screenshot(str(filepath))
            self.logger.info(f"Screenshot saved: {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Screenshot failed: {e}")
            return False

    def close(self):
        """关闭浏览器"""
        try:
            if hasattr(self, 'driver') and self.driver:
                self.driver.quit()
                self.logger.info("Browser closed")
        except Exception as e:
            self.logger.error(f"Failed to close browser: {e}")

    @abstractmethod
    def search_products(self, keyword: str, page: int = 1) -> List[Dict]:
        """搜索商品（子类必须实现）"""
        pass

    @abstractmethod
    def get_product_detail(self, product_url: str) -> Dict:
        """获取商品详情（子类必须实现）"""
        pass

    @abstractmethod
    def get_product_reviews(self, product_id: str, max_count: int = 100) -> List[Dict]:
        """获取商品评价（子类必须实现）"""
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
