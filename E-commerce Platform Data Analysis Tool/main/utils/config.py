"""
Utils - 统一配置管理
系统配置 | 环境变量 | 设置持久化
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Optional, Any


class Config:
    """统一配置管理类 - 对标电商后台配置中心"""

    _instance = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.project_root = Path(__file__).parent.parent
        self.config_dir = self.project_root / "config"
        self.config_file = self.config_dir / "config.json"
        self.settings_file = self.project_root / "settings.json"
        self.cookies_file = self.config_dir / "cookies.json"
        
        self.config_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        self._config = {}
        self._settings = {}
        
        # 加载配置
        self.load_config()
        self.load_settings()
        
        self._initialized = True

    def load_config(self) -> Dict:
        """
        加载主配置文件
        
        Returns:
            dict: 配置数据
        """
        if not self.config_file.exists():
            self.logger.warning("配置文件不存在，使用默认配置")
            return self.get_default_config()
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
            self.logger.info("配置加载成功")
            return self._config
            
        except Exception as e:
            self.logger.error(f"配置加载失败: {e}")
            return self.get_default_config()

    def load_settings(self) -> Dict:
        """
        加载用户设置
        
        Returns:
            dict: 设置数据
        """
        if not self.settings_file.exists():
            return self.get_default_settings()
        
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                self._settings = json.load(f)
            return self._settings
            
        except Exception as e:
            self.logger.error(f"设置加载失败: {e}")
            return self.get_default_settings()

    def save_config(self, config: Dict) -> bool:
        """
        保存主配置
        
        Args:
            config: 配置数据
            
        Returns:
            bool: 是否成功
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            self._config = config
            self.logger.info("配置保存成功")
            return True
            
        except Exception as e:
            self.logger.error(f"配置保存失败: {e}")
            return False

    def save_settings(self, settings: Dict) -> bool:
        """
        保存用户设置
        
        Args:
            settings: 设置数据
            
        Returns:
            bool: 是否成功
        """
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            
            self._settings = settings
            self.logger.info("设置保存成功")
            return True
            
        except Exception as e:
            self.logger.error(f"设置保存失败: {e}")
            return False

    def get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "ocr": {
                "app_id": "",
                "api_key": "",
                "secret_key": ""
            },
            "llm": {
                "provider": "deepseek",
                "api_key": "",
                "base_url": "https://api.deepseek.com/v1"
            },
            "crawler": {
                "headless": False,
                "browser": "edge",
                "request_delay_min": 1,
                "request_delay_max": 3,
                "max_retries": 3
            }
        }

    def get_default_settings(self) -> Dict:
        """获取默认设置"""
        return {
            'default_keyword': '食品',
            'default_product_count': 50,
            'default_review_count': 100,
            'output_format': 'JSON',
            'headless_mode': False,
            'auto_save': True,
            'timeout': 30,
            'retry_count': 3,
            'last_updated': ''
        }

    @property
    def ocr_config(self) -> Dict:
        """获取OCR配置"""
        return self._config.get('ocr', {})

    @property
    def llm_config(self) -> Dict:
        """获取大模型配置"""
        return self._config.get('llm', {})

    @property
    def crawler_config(self) -> Dict:
        """获取爬虫配置"""
        crawler_cfg = self._config.get('crawler', {})
        # 合并用户设置中的爬虫相关配置
        crawler_cfg['headless'] = self._settings.get('headless_mode', crawler_cfg.get('headless', False))
        return crawler_config

    @property
    def keyword(self) -> str:
        """获取默认搜索关键词"""
        return self._settings.get('default_keyword', '食品')

    @property
    def product_count(self) -> int:
        """获取默认采集数量"""
        return self._settings.get('default_product_count', 50)

    @property
    def review_count(self) -> int:
        """获取默认评价数量"""
        return self._settings.get('default_review_count', 100)

    def get_output_dir(self) -> Path:
        """获取输出目录"""
        output_dir = self.project_root / "output"
        output_dir.mkdir(exist_ok=True)
        return output_dir

    def get_logs_dir(self) -> Path:
        """获取日志目录"""
        logs_dir = self.project_root / "logs"
        logs_dir.mkdir(exist_ok=True)
        return logs_dir

    def get_data_dir(self) -> Path:
        """获取数据目录"""
        data_dir = self.project_root / "data"
        data_dir.mkdir(exist_ok=True)
        return data_dir

    def cookies_exist(self) -> bool:
        """检查Cookie文件是否存在"""
        return self.cookies_file.exists()

    def setup_interactive(self) -> Dict:
        """
        交互式配置向导（首次运行时使用）
        
        Returns:
            dict: 配置结果
        """
        print("\n" + "="*60)
        print("   食品电商AI分析工具 - 配置向导")
        print("="*60)

        print("\n【步骤 1/2】OCR配置 - 百度智能云")
        print("请前往 https://console.bce.baidu.com/ai/#/ai/ocr/overview/index 获取密钥")
        
        try:
            ocr_app_id = input("  请输入 APP_ID: ").strip()
            ocr_api_key = input("  请输入 API_KEY: ").strip()
            ocr_secret_key = input("  请输入 SECRET_KEY: ").strip()

            if not all([ocr_app_id, ocr_api_key, ocr_secret_key]):
                raise ValueError("OCR配置不能为空！")

            print("\n【步骤 2/2】大模型配置")
            print("支持的服务商: deepseek / qwen / zhipu")
            
            llm_provider = input("  请选择服务商 (默认: deepseek): ").strip() or "deepseek"

            if llm_provider == "deepseek":
                llm_base_url = "https://api.deepseek.com/v1"
            elif llm_provider == "qwen":
                llm_base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
            elif llm_provider == "zhipu":
                llm_base_url = "https://open.bigmodel.cn/api/paas/v4"
            else:
                raise ValueError(f"不支持的大模型服务商: {llm_provider}")

            llm_api_key = input(f"  请输入 {llm_provider} API Key: ").strip()

            if not llm_api_key:
                raise ValueError("大模型API Key不能为空！")

            config = {
                "ocr": {
                    "app_id": ocr_app_id,
                    "api_key": ocr_api_key,
                    "secret_key": ocr_secret_key
                },
                "llm": {
                    "provider": llm_provider,
                    "api_key": llm_api_key,
                    "base_url": llm_base_url
                },
                "crawler": {
                    "headless": False,
                    "browser": "edge",
                    "request_delay_min": 1,
                    "request_delay_max": 3,
                    "max_retries": 3
                }
            }

            self.save_config(config)
            print("\n✅ 配置已保存到:", self.config_file)
            return config

        except (KeyboardInterrupt, EOFError) as e:
            print("\n\n❌ 用户取消配置")
            return {}

        except Exception as e:
            print(f"\n❌ 配置失败: {e}")
            return {}

    def reset_to_defaults(self) -> bool:
        """
        重置为默认设置
        
        Returns:
            bool: 是否成功
        """
        try:
            if self.settings_file.exists():
                self.settings_file.unlink()
            
            self._settings = self.get_default_settings()
            self.logger.info("已恢复默认设置")
            return True
            
        except Exception as e:
            self.logger.error(f"重置失败: {e}")
            return False

    def export_settings(self) -> Optional[str]:
        """
        导出配置文件
        
        Returns:
            str or None: 导出文件路径
        """
        from datetime import datetime
        
        if not self.settings_file.exists():
            return None
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            export_path = self.get_output_dir() / f'settings_backup_{timestamp}.json'
            
            import shutil
            shutil.copy2(self.settings_file, export_path)
            
            self.logger.info(f"配置已导出到: {export_path}")
            return str(export_path)
            
        except Exception as e:
            self.logger.error(f"导出失败: {e}")
            return None

    def get_system_info(self) -> Dict:
        """
        获取系统信息
        
        Returns:
            dict: 系统信息
        """
        import sys
        
        output_dir = self.get_output_dir()
        file_count = len(list(output_dir.glob('*'))) if output_dir.exists() else 0
        
        return {
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'project_root': str(self.project_root),
            'output_files': file_count,
            'config_status': '已保存 ✅' if self.config_file.exists() else '未配置',
            'cookies_status': '已配置 ✅' if self.cookies_exist() else '未配置'
        }

    def cleanup_data(self, data_type: str = "不清理") -> int:
        """
        清理数据文件
        
        Args:
            data_type: 清理类型
            
        Returns:
            int: 清理的文件数
        """
        cleared = []
        
        logs_dir = self.get_logs_dir()
        output_dir = self.get_output_dir()
        
        if "日志" in data_type and logs_dir.exists():
            for log_file in logs_dir.glob('*.log'):
                log_file.unlink()
                cleared.append(log_file.name)

        if "输出" in data_type and output_dir.exists():
            for out_file in output_dir.glob('*'):
                out_file.unlink()
                cleared.append(out_file.name)
        
        if cleared:
            self.logger.info(f"已清理 {len(cleared)} 个文件")
        
        return len(cleared)


# 全局单例实例
config = Config()


def get_config() -> Config:
    """
    获取配置实例（便捷函数）
    
    Returns:
        Config: 配置实例
    """
    return config
