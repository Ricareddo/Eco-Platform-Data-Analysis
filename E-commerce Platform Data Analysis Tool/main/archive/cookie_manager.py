import sys
import os
import io

# Windows中文乱码解决方案 - 终极版
def setup_chinese_encoding():
    """配置Windows控制台支持UTF-8中文显示"""
    if sys.platform == 'win32':
        try:
            # 方法1: 使用ctypes设置控制台编码（最可靠）
            import ctypes
            kernel32 = ctypes.windll.kernel32

            # 设置控制台输出为UTF-8 (CP65001)
            kernel32.SetConsoleOutputCP(65001)
            kernel32.SetConsoleCP(65001)

            # 重新配置stdout和stderr
            if hasattr(sys.stdout, 'buffer'):
                sys.stdout = io.TextIOWrapper(
                    sys.stdout.buffer,
                    encoding='utf-8',
                    errors='replace',
                    newline=None,
                    write_through=True
                )
            if hasattr(sys.stderr, 'buffer'):
                sys.stderr = io.TextIOWrapper(
                    sys.stderr.buffer,
                    encoding='utf-8',
                    errors='replace',
                    newline=None,
                    write_through=True
                )

        except Exception as e:
            # 如果方法1失败，尝试方法2
            try:
                os.system('chcp 65001 > nul 2>&1')
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
            except:
                pass

setup_chinese_encoding()

import time
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def cookie_manager():
    """Cookie管理工具 - 用于保存/加载淘宝/天猫登录状态"""

    print("\n" + "="*70)
    print("   淘宝/天猫 Cookie 管理工具")
    print("="*70 + "\n")

    from crawlers.tmall_crawler import TmallCrawler

    cookies_file = Path(__file__).parent / "config" / "cookies.json"
    cookies_file.parent.mkdir(exist_ok=True)

    with TmallCrawler(headless=False) as crawler:

        while True:
            print("\n请选择操作:")
            print("  1. 手动登录并保存Cookie（推荐首次使用）")
            print("  2. 加载已有Cookie并测试")
            print("  3. 删除已保存的Cookie")
            print("  4. 退出")

            try:
                choice = input("\n请输入选项 (1-4): ").strip()
            except (UnicodeDecodeError, UnicodeEncodeError, EOFError):
                print("\n[输入错误，请重试]")
                continue

            if choice == '1':
                print("\n步骤 1: 打开淘宝登录页面...")
                crawler.open_page("https://login.taobao.com/")
                time.sleep(2)

                print("\n步骤 2: 请在浏览器中完成登录...")
                print("   提示: 可以使用扫码登录或账号密码登录")
                try:
                    input("   登录完成后按回车键继续...")
                except:
                    pass

                # 保存Cookie
                if crawler.save_cookies(str(cookies_file)):
                    print(f"\n成功! Cookie已保存!")
                    print(f"   位置: {cookies_file}")
                    print(f"   下次运行爬虫将自动使用此Cookie")

            elif choice == '2':
                print(f"\n尝试加载Cookie: {cookies_file}")

                if not cookies_file.exists():
                    print("[错误] Cookie文件不存在! 请先执行选项1进行登录")
                    continue

                if crawler.load_cookies(str(cookies_file)):
                    print("\n测试Cookie有效性...")
                    crawler.open_page("https://www.taobao.com/")
                    time.sleep(3)

                    current_url = crawler.page.url
                    page_title = crawler.page.title

                    print(f"当前URL: {current_url}")
                    print(f"页面标题: {page_title}")

                    if 'login' in current_url.lower():
                        print("\n[警告] Cookie可能已过期，建议重新登录")
                    else:
                        print("\n[成功] Cookie有效! 可以正常使用")

            elif choice == '3':
                if cookies_file.exists():
                    cookies_file.unlink()
                    print(f"\n已删除Cookie文件: {cookies_file}")
                else:
                    print("\n[提示] Cookie文件不存在")

            elif choice == '4':
                print("\n再见!")
                break

            else:
                print("\n无效选项，请重新输入")

if __name__ == "__main__":
    try:
        cookie_manager()
    except KeyboardInterrupt:
        print("\n\n用户中断程序")
    except Exception as e:
        logger.error(f"程序出错: {e}", exc_info=True)
        print(f"\n[错误] {e}")
