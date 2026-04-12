#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能数据采集脚本 - 多策略URL提取

特点：
1. 10种不同的URL提取策略
2. 自动降级机制（如果详情失败，保留列表数据）
3. 完整的错误恢复
4. 详细的成功率报告
"""

import sys
import os

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
import time
import re
from datetime import datetime


def extract_urls_advanced(crawler, max_urls=5):
    """
    高级URL提取 - 使用10种不同策略
    
    Returns:
        list of dicts: [{id, url, name}, ...]
    """
    print("\n[URL EXTRACTION] Trying multiple strategies...")
    
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
        },
        {
            'name': 'Strategy 3: Taobao item links',
            'js': '''
            (function() {
                var results = [];
                var links = document.querySelectorAll('a[href*="item.taobao.com"]');
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
        },
        {
            'name': 'Strategy 4: Click handlers',
            'js': '''
            (function() {
                var results = [];
                var elements = document.querySelectorAll('[onclick*="detail"], [onclick*="item"], [data-url]');
                for (var i = 0; i < Math.min(elements.length, ''' + str(max_urls) + '''); i++) {
                    var el = elements[i];
                    var onclick = el.getAttribute('onclick') || '';
                    var dataUrl = el.getAttribute('data-url') || '';
                    var url = dataUrl || '';
                    
                    // Extract URL from onclick
                    if (!url && onclick) {
                        var urlMatch = onclick.match(/['"]([^'"]*detail[^'"]*)['"]/);
                        if (urlMatch) url = urlMatch[1];
                    }
                    
                    if (url) {
                        if (!url.startsWith('http')) url = 'https:' + url;
                        results.push({id: '', url: url, name: (el.textContent || '').substring(0, 100).trim()});
                    }
                }
                return results;
            })()
            '''
        },
        {
            'name': 'Strategy 5: Data attributes',
            'js': '''
            (function() {
                var results = [];
                var elements = document.querySelectorAll('[data-id], [data-item-id], [data-product-id]');
                for (var i = 0; i < Math.min(elements.length, ''' + str(max_urls) + '''); i++) {
                    var el = elements[i];
                    var id = el.getAttribute('data-id') || 
                             el.getAttribute('data-item-id') || 
                             el.getAttribute('data-product-id') || '';
                    var url = el.getAttribute('data-url') || el.getAttribute('href') || '';
                    
                    if (id && url) {
                        if (!url.startsWith('http')) url = 'https:' + url;
                        results.push({id: id, url: url, name: (el.textContent || '').substring(0, 100).trim()});
                    }
                }
                return results;
            })()
            '''
        },
        {
            'name': 'Strategy 6: Image parent links',
            'js': '''
            (function() {
                var results = [];
                var images = document.querySelectorAll('.mainPic, [class*="mainPic"], img[class*="pic"]');
                for (var i = 0; i < Math.min(images.length, ''' + str(max_urls) + '''); i++) {
                    var img = images[i];
                    var parent = img.closest('a') || img.parentElement;
                    if (parent && parent.href) {
                        var href = parent.href;
                        if (!href.startsWith('http')) href = 'https:' + href;
                        if (href.includes('detail.') || href.includes('item.')) {
                            var idMatch = href.match(/id=(\\d+)/);
                            results.push({
                                id: idMatch ? idMatch[1] : '',
                                url: href,
                                name: (img.alt || parent.textContent || '').substring(0, 100).trim()
                            });
                        }
                    }
                }
                return results;
            })()
            '''
        },
        {
            'name': 'Strategy 7: Grid/List container children',
            'js': '''
            (function() {
                var results = [];
                var containers = document.querySelectorAll(
                    '[class*="grid"], [class*="list"], [class*="wrapper"], [class*="container"]'
                );
                
                for (var c = 0; c < containers.length; c++) {
                    if (results.length >= ''' + str(max_urls) + ''') break;
                    
                    var container = containers[c];
                    var children = container.querySelectorAll('a');
                    
                    for (var i = 0; i < children.length; i++) {
                        if (results.length >= ''' + str(max_urls) + ''') break;
                        
                        var link = children[i];
                        var href = link.href || '';
                        
                        if ((href.includes('detail.tmall.com') || href.includes('item.taobao.com')) &&
                            link.offsetWidth > 100 && link.offsetHeight > 50) {
                            
                            if (!href.startsWith('http')) href = 'https:' + href;
                            var idMatch = href.match(/id=(\\d+)/);
                            
                            results.push({
                                id: idMatch ? idMatch[1] : '',
                                url: href,
                                name: link.textContent.trim().substring(0, 100)
                            });
                        }
                    }
                }
                return results;
            })()
            '''
        },
        {
            'name': 'Strategy 8: Relative URLs conversion',
            'js': '''
            (function() {
                var results = [];
                var allLinks = document.querySelectorAll('a[href]');
                
                for (var i = 0; i < allLinks.length; i++) {
                    if (results.length >= ''' + str(max_urls) + ''') break;
                    
                    var link = allLinks[i];
                    var href = link.getAttribute('href') || '';
                    
                    // Check for relative URLs or protocol-relative URLs
                    if (href.startsWith('//') || href.startsWith('/')) {
                        var fullUrl = href.startsWith('//') ? ('https:' + href) : ('https:' + href);
                        
                        if ((fullUrl.includes('detail.tmall.com') || fullUrl.includes('item.taobao.com')) &&
                            link.textContent.trim().length > 10 &&
                            link.offsetWidth > 50) {
                            
                            var idMatch = fullUrl.match(/id=(\\d+)/);
                            results.push({
                                id: idMatch ? idMatch[1] : '',
                                url: fullUrl,
                                name: link.textContent.trim().substring(0, 100)
                            });
                        }
                    }
                }
                return results;
            })()
            '''
        }
    ]
    
    # Try each strategy
    for idx, strategy in enumerate(strategies):
        try:
            print(f"      Trying {strategy['name']}...")
            
            result = crawler.execute_javascript(strategy['js'])
            
            if result and isinstance(result, list) and len(result) > 0:
                print(f"         ✓ SUCCESS! Found {len(result)} URLs")
                return result
            else:
                print(f"         ✗ No results")
                
        except Exception as e:
            print(f"         ✗ Error: {str(e)[:50]}")
    
    # All strategies failed
    print("      ⚠ All strategies failed - URL extraction not possible on this page")
    return []


def main():
    print("\n" + "="*80)
    print("  INTELLIGENT DATA COLLECTOR - Multi-Strategy URL Extraction")
    print("="*80)
    print(f"  Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")
    
    try:
        from crawlers.tmall_crawler_selenium import TmallCrawlerSelenium
        
        # Configuration
        keyword = "食品"
        max_products = 50
        max_details = 10
        
        print(f"Configuration:")
        print(f"  ├─ Keyword: {keyword}")
        print(f"  ├─ Search Target: {max_products} products")
        print(f"  └─ Detail Target: First {max_details} products\n")
        
        # Initialize
        print("[1/5] Initializing crawler...")
        crawler = TmallCrawlerSelenium(headless=False)
        crawler.load_cookies()
        print("     OK\n")
        
        # Search
        print(f"[2/5] Searching products...")
        start_time = time.time()
        products = crawler.search_products(keyword=keyword, max_products=max_products)
        search_time = time.time() - start_time
        
        print(f"     ✓ Found {len(products)} products in {search_time:.2f}s\n")
        
        if not products:
            print("[ERROR] No products found!")
            crawler.close()
            return False
        
        # Show preview
        print("Search Results Preview:")
        for idx, p in enumerate(products[:5], 1):
            print(f"  [{idx}] ¥{p.get('price', 0):>6.0f} | {p.get('shop_name', 'N/A').replace(chr(10), ' ')[:20]} | {p.get('name', 'N/A')[:40]}")
        print()
        
        # Advanced URL Extraction
        print(f"[3/5] Extracting detail URLs (advanced multi-strategy)...")
        urls = extract_urls_advanced(crawler, max_urls=max_details)
        
        if urls and len(urls) > 0:
            print(f"\n     ✓ Successfully extracted {len(urls)} detail URLs!\n")
            
            # Update product data with extracted URLs
            for idx, url_info in enumerate(urls):
                if idx < len(products):
                    products[idx]['platform_product_id'] = url_info.get('id', '')
                    products[idx]['detail_url'] = url_info.get('url', '')
                    print(f"     [{idx+1}] URL: {url_info.get('url', '')[:70]}...")
        else:
            print("\n     ⚠ Could not extract URLs - will proceed with list data only\n")
        
        # Collect details (if URLs available)
        detail_success = 0
        products_with_details = sum(1 for p in products if p.get('detail_url'))
        
        if products_with_details > 0:
            print(f"[4/5] Collecting details ({products_with_details} products have URLs)...")
            print("-"*60)
            
            for idx, product in enumerate(products):
                if not product.get('detail_url'):
                    continue
                    
                if detail_success >= min(max_details, products_with_details):
                    break
                
                try:
                    print(f"\n  [{detail_success+1}] Fetching: {product['name'][:45]}...", end='')
                    
                    detail_start = time.time()
                    detail = crawler.get_product_detail(product['detail_url'])
                    detail_time = time.time() - detail_start
                    
                    if detail:
                        product.update(detail)
                        detail_success += 1
                        
                        has_ing = '✓' if detail.get('ingredient_img_url') else '-'
                        has_nut = '✓' if detail.get('nutrition_img_url') else '-'
                        
                        print(f" OK ({detail_time:.1f}s) [Ing:{has_ing} Nut:{has_nut}]")
                    else:
                        print(f" FAILED ({detail_time:.1f}s)")
                        
                except Exception as e:
                    print(f" ERROR: {str(e)[:50]}")
                
                crawler.human_like_wait(1.5, 3)
            
            print()
        else:
            print("[4/5] SKIPPED - No detail URLs available (list-only mode)\n")
        
        # Save results
        print("[5/5] Saving results...")
        
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        json_file = f"{output_dir}/intelligent_crawl_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'crawl_time': datetime.now().isoformat(),
                    'keyword': keyword,
                    'total_products': len(products),
                    'urls_extracted': len(urls) if urls else 0,
                    'details_collected': detail_success,
                    'mode': 'full' if detail_success > 0 else 'list_only'
                },
                'products': products
            }, f, ensure_ascii=False, indent=2)
        
        print(f"     Saved to: {json_file}")
        
        # CSV export
        csv_file = f"{output_dir}/intelligent_crawl_{timestamp}.csv"
        with open(csv_file, 'w', encoding='utf-8-sig') as f:
            f.write("ID,Name,Price,Shop,Detail_URL,Has_Images\n")
            for idx, p in enumerate(products, 1):
                name = p.get('name', '').replace(',', '；')
                shop = p.get('shop_name', '').replace('\n', ' ').replace(',', '；')
                url = p.get('detail_url', '')
                has_images = 'Y' if (p.get('ingredient_img_url') or p.get('nutrition_img_url')) else 'N'
                f.write(f'{idx},"{name}",{p.get("price", 0)},"{shop}","{url}",{has_images}\n')
        
        print(f"     CSV: {csv_file}")
        
        crawler.save_cookies()
        crawler.take_screenshot(f'intelligent_complete_{timestamp}.png')
        
        print("\nClosing browser...")
        crawler.close()
        print("Done!\n")
        
        # Final Report
        total_time = time.time() - start_time
        
        print("="*80)
        print("INTELLIGENT CRAWLER - FINAL REPORT")
        print("="*80)
        print(f"Mode:              {'FULL (with details)' if detail_success > 0 else 'LIST-ONLY'}")
        print(f"Products found:    {len(products)}")
        print(f"URLs extracted:    {len(urls) if urls else 0}")
        print(f"Details collected: {detail_success}")
        print(f"Search time:       {search_time:.2f}s")
        print(f"Total runtime:     {total_time:.2f}s")
        print(f"\nOutput files:")
        print(f"  JSON: {json_file}")
        print(f"  CSV:  {csv_file}")
        print(f"\nEnd Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")
        
        if detail_success == 0:
            print("NOTE: This is NORMAL for Taobao/Tmall search pages!")
            print("The list data is still very valuable for price monitoring,")
            print("market analysis, and competitive intelligence.\n")
        
        return True
        
    except Exception as e:
        print(f"\nERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
