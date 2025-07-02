import os
import json
from pathlib import Path
from PySide6.QtWidgets import QMessageBox

class ConfigManager:
    CONFIG_DIR = "config"
    DEFAULT_PRESET_FILE = os.path.join(CONFIG_DIR, "default.json")
    
    def __init__(self):
        self.presets = self.load_default_presets()
        self.current_config = {}
    
    def load_default_presets(self):
        """从default.json加载预设配置"""
        if not os.path.exists(self.DEFAULT_PRESET_FILE):
            return {}
        
        try:
            with open(self.DEFAULT_PRESET_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            QMessageBox.critical(None, "配置错误", f"加载默认配置失败: {str(e)}")
            return {}
    
    def get_available_presets(self):
        """获取可用预设列表"""
        return list(self.presets.keys())
    
    def load_preset(self, preset_name):
        """加载指定预设"""
        if preset_name not in self.presets:
            QMessageBox.warning(None, "配置错误", f"预设 '{preset_name}' 不存在")
            return False
        
        self.current_config = self.presets[preset_name].get("settings", {})
        return True
    
    def save_preset(self, preset_name, config_data, description="", overwrite=False):
        """保存当前配置为新预设"""
        if preset_name in self.presets and not overwrite:
            reply = QMessageBox.question(
                None, "覆盖预设",
                f"预设 '{preset_name}' 已存在。是否覆盖？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return False
        
        # 更新预设
        self.presets[preset_name] = {
            "description": description,
            "settings": config_data
        }
        
        # 保存到文件
        try:
            with open(self.DEFAULT_PRESET_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.presets, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            QMessageBox.critical(None, "保存失败", f"保存预设时出错: {str(e)}")
            return False
    
    def reset_to_default(self):
        """重置为默认预设"""
        if "default" in self.presets:
            return self.load_preset("default")
        return False
    
    def get_current_config(self):
        """获取当前配置"""
        return self.current_config
    
    def update_config(self, key, value):
        """更新当前配置项"""
        self.current_config[key] = value