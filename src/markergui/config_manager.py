import os
import json
from pathlib import Path
from PySide6.QtWidgets import QMessageBox


class ConfigManager:
    CONFIG_DIR = "config"
    DEFAULT_PRESET_FILE = os.path.join(CONFIG_DIR, "default.json")

    def __init__(self):
        # 确保配置文件存在
        self.ensure_default_config()
        self.presets = self.load_default_presets()
        self.current_config = {}

    def ensure_default_config(self):
        """确保默认配置文件存在，如果不存在则创建"""
        if not os.path.exists(self.DEFAULT_PRESET_FILE):
            config_dir = Path(self.CONFIG_DIR)
            config_dir.mkdir(exist_ok=True)

            default_configs = {
                "default": {
                    "description": "默认配置",
                    "settings": {"output_format": "markdown", "use_llm": False},
                },
                "high_quality": {
                    "description": "高质量转换",
                    "settings": {
                        "output_format": "markdown",
                        "use_llm": True,
                        "llm_service": "Google Gemini",
                        "gemini_model_name": "gemini-2.0-flash",
                    },
                },
                "table_extraction": {
                    "description": "表格提取",
                    "settings": {
                        "converter_cls": "marker.converters.table.TableConverter",
                        "image_extraction_mode": "禁用图片提取",
                    },
                },
                "pure_ocr": {
                    "description": "纯OCR处理",
                    "settings": {
                        "converter_cls": "marker.converters.ocr.OCRConverter",
                        "ocr_mode": "强制OCR (扫描所有)",
                        "use_llm": False,
                    },
                },
            }

            with open(self.DEFAULT_PRESET_FILE, "w", encoding="utf-8") as f:
                json.dump(default_configs, f, indent=2, ensure_ascii=False)

    def load_default_presets(self):
        """从default.json加载预设配置"""
        if not os.path.exists(self.DEFAULT_PRESET_FILE):
            return {}

        try:
            with open(self.DEFAULT_PRESET_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            QMessageBox.critical(None, "配置错误", f"加载默认配置失败: {str(e)}")
            return {}

    def get_available_presets(self):
        """获取可用预设列表"""
        return list(self.presets.keys())

    def preset_exists(self, preset_name):
        """检查预设是否存在"""
        return preset_name in self.presets

    def delete_preset(self, preset_name):
        """删除指定的预设"""
        if preset_name not in self.presets:
            return False

        if preset_name == "default":
            return False

        # 从预设字典中删除
        del self.presets[preset_name]

        # 保存更新后的预设到文件
        try:
            with open(self.DEFAULT_PRESET_FILE, "w", encoding="utf-8") as f:
                json.dump(self.presets, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[ERROR] 删除预设失败: {str(e)}")
            return False

    def load_preset(self, preset_name):
        """加载指定预设"""
        if preset_name not in self.presets:
            QMessageBox.warning(None, "配置错误", f"预设 '{preset_name}' 不存在")
            return {}

        self.current_config = self.presets[preset_name].get("settings", {})
        return self.current_config

    def save_preset(self, preset_name, config_data, description="", overwrite=False):
        """保存当前配置为新预设"""
        if preset_name in self.presets and not overwrite:
            reply = QMessageBox.question(
                None,
                "覆盖预设",
                f"预设 '{preset_name}' 已存在。是否覆盖？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.No:
                return False

        # 更新预设
        self.presets[preset_name] = {
            "description": description,
            "settings": config_data,
        }

        # 保存到文件
        try:
            with open(self.DEFAULT_PRESET_FILE, "w", encoding="utf-8") as f:
                json.dump(self.presets, f, indent=2, ensure_ascii=False)
            # 更新当前配置为新保存的配置
            self.current_config = config_data
            return True
        except Exception as e:
            QMessageBox.critical(None, "保存失败", f"保存预设时出错: {str(e)}")
            return False

    def reset_to_default(self):
        """重置为默认预设"""
        if "default" in self.presets:
            config = self.load_preset("default")
            self.current_config = config  # 确保更新当前配置
            return config
        return {}

    def get_current_config(self):
        """获取当前配置"""
        return self.current_config.copy()  # 返回副本防止意外修改
