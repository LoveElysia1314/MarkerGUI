import os
import json
from pathlib import Path
from PySide6.QtWidgets import QMessageBox

class ConfigManager:
    CONFIG_DIR = os.path.join(str(Path.home()), ".marker_gui")
    PRESET_DIR = os.path.join(CONFIG_DIR, "presets")
    USER_DIR = os.path.join(CONFIG_DIR, "user_configs")
    
    def __init__(self):
        self.create_directories()
        self.load_presets()
        
    def create_directories(self):
        """创建必要的配置目录"""
        os.makedirs(self.PRESET_DIR, exist_ok=True)
        os.makedirs(self.USER_DIR, exist_ok=True)
    
    def load_presets(self):
        """加载预设配置"""
        self.presets = {
            "默认配置": {},
            "高质量转换": {
                "use_llm": True,
                "format_lines": True,
                "redo_inline_math": True
            },
            "表格提取": {
                "converter_cls": "marker.converters.table.TableConverter",
                "output_format": "json",
                "force_layout_block": "Table"
            },
            "纯OCR处理": {
                "converter_cls": "marker.converters.ocr.OCRConverter",
                "force_ocr": True
            }
        }
        
        # 保存预设到文件
        for name, config in self.presets.items():
            preset_path = os.path.join(self.PRESET_DIR, f"{name}.json")
            if not os.path.exists(preset_path):
                with open(preset_path, 'w') as f:
                    json.dump(config, f, indent=4)
    
    def get_user_configs(self):
        """获取用户保存的所有配置"""
        configs = {}
        if os.path.exists(self.USER_DIR):
            for file in os.listdir(self.USER_DIR):
                if file.endswith(".json"):
                    name = file[:-5]  # 移除.json扩展名
                    configs[name] = os.path.join(self.USER_DIR, file)
        return configs
    
    def get_all_configs(self):
        """获取所有可用配置（预设+用户）"""
        all_configs = {}
        
        # 添加预设配置
        for name in self.presets.keys():
            all_configs[name] = os.path.join(self.PRESET_DIR, f"{name}.json")
        
        # 添加用户配置
        all_configs.update(self.get_user_configs())
        return all_configs
    
    def save_config(self, config_name, config_data):
        """保存配置到用户目录"""
        # 检查是否覆盖系统预设
        if config_name in self.presets:
            reply = QMessageBox.question(
                None, "覆盖预设", 
                f"'{config_name}' 是一个系统预设配置。\n您确定要覆盖它吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return False
            config_path = os.path.join(self.PRESET_DIR, f"{config_name}.json")
        else:
            config_path = os.path.join(self.USER_DIR, f"{config_name}.json")
        
        # 检查文件是否存在
        if os.path.exists(config_path):
            reply = QMessageBox.question(
                None, "覆盖配置", 
                f"配置 '{config_name}' 已存在。\n您确定要覆盖它吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return False
        
        # 保存配置
        try:
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=4)
            return True
        except Exception as e:
            QMessageBox.critical(None, "保存失败", f"保存配置时出错: {str(e)}")
            return False
    
    def load_config(self, config_name):
        """从文件加载配置"""
        all_configs = self.get_all_configs()
        if config_name not in all_configs:
            return None
        
        config_path = all_configs[config_name]
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            QMessageBox.critical(None, "加载失败", f"加载配置时出错: {str(e)}")
            return None