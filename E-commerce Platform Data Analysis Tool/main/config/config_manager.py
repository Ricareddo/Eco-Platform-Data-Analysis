import os
import json
import logging
from pathlib import Path

class ConfigManager:
    """配置管理器 - 交互式配置API密钥"""

    def __init__(self):
        self.config_dir = Path(__file__).parent.parent / "config"
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)

    def setup(self):
        """首次运行时交互式配置"""
        print("\n" + "="*60)
        print("   食品电商AI分析工具 - 配置向导")
        print("="*60)

        print("\n【步骤 1/2】OCR配置 - 百度智能云")
        print("请前往 https://console.bce.baidu.com/ai/#/ai/ocr/overview/index 获取密钥")
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

        self.save(config)
        print("\n✅ 配置已保存到:", self.config_file)
        return config

    def load(self):
        """加载配置"""
        if not self.config_file.exists():
            print("\n⚠️  未找到配置文件，启动配置向导...")
            return self.setup()

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.logger.info("配置加载成功")
                return config
        except Exception as e:
            self.logger.error(f"配置加载失败: {e}")
            print(f"\n❌ 配置文件损坏: {e}")
            return self.setup()

    def save(self, config):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

    def get_ocr_config(self):
        """获取OCR配置"""
        config = self.load()
        return config.get('ocr', {})

    def get_llm_config(self):
        """获取大模型配置"""
        config = self.load()
        return config.get('llm', {})

    def get_crawler_config(self):
        """获取爬虫配置"""
        config = self.load()
        return config.get('crawler', {})
