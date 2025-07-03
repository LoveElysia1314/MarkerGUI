from .base_tab import BaseTab
from PySide6.QtWidgets import (
    QHBoxLayout, QGroupBox, QLabel, QLineEdit, QPushButton,
    QComboBox, QCheckBox, QSpinBox, QFormLayout, QVBoxLayout
)
from PySide6.QtCore import Qt, Signal

class AdvancedTab(BaseTab):
    preset_changed = Signal(str)  # 预设切换信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = parent.config_manager
        self.main_window = parent
        
        # 处理器设置
        processor_group = QGroupBox("处理器设置")
        processor_layout = QFormLayout()
        
        self.processors = QLineEdit()
        processor_layout.addRow("自定义处理器链:", self.processors)
        processor_layout.addRow(QLabel("格式: processor1,processor2,..."))
        
        processor_group.setLayout(processor_layout)
        self.add_to_layout(processor_group)
        
        # 多GPU设置
        gpu_group = QGroupBox("多GPU设置")
        gpu_layout = QFormLayout()
        
        num_devices_layout = QHBoxLayout()
        num_devices_layout.addWidget(QLabel("GPU数量:"))
        self.num_devices = QSpinBox()
        self.num_devices.setRange(1, 8)
        self.num_devices.setValue(1)
        num_devices_layout.addWidget(self.num_devices)
        gpu_layout.addRow(num_devices_layout)
        
        num_workers_layout = QHBoxLayout()
        num_workers_layout.addWidget(QLabel("每GPU工作进程数:"))
        self.num_workers = QSpinBox()
        self.num_workers.setRange(1, 64)
        self.num_workers.setValue(15)
        num_workers_layout.addWidget(self.num_workers)
        gpu_layout.addRow(num_workers_layout)
        
        gpu_group.setLayout(gpu_layout)
        self.add_to_layout(gpu_group)
        
        # 调试设置
        debug_group = QGroupBox("调试设置")
        debug_layout = QFormLayout()
        
        self.debug_data_folder = QLineEdit()
        debug_layout.addRow("调试数据存储目录:", self.debug_data_folder)
        
        debug_check_layout = QVBoxLayout()
        self.debug_layout_images = QCheckBox("保存布局分析图像")
        debug_check_layout.addWidget(self.debug_layout_images)
        self.debug_pdf_images = QCheckBox("保存PDF解析图像")
        debug_check_layout.addWidget(self.debug_pdf_images)
        self.debug_json = QCheckBox("保存中间JSON数据")
        debug_check_layout.addWidget(self.debug_json)
        debug_layout.addRow("调试选项:", debug_check_layout)
        
        debug_group.setLayout(debug_layout)
        self.add_to_layout(debug_group)
        
        # 配置管理
        config_group = QGroupBox("配置管理")
        config_layout = QFormLayout()
        
        self.preset_combo = QComboBox()
        self.preset_combo.currentTextChanged.connect(self.on_preset_changed)
        config_layout.addRow("当前预设:", self.preset_combo)
        self.refresh_config_list()
        
        config_btn_layout = QHBoxLayout()
        self.save_config_btn = QPushButton("保存配置")
        self.save_config_btn.clicked.connect(self.save_config)
        self.load_config_btn = QPushButton("加载配置")
        self.load_config_btn.clicked.connect(self.load_config)
        self.reset_config_btn = QPushButton("重置配置")
        self.reset_config_btn.clicked.connect(self.reset_config)
        
        config_btn_layout.addWidget(self.save_config_btn)
        config_btn_layout.addWidget(self.load_config_btn)
        config_btn_layout.addWidget(self.reset_config_btn)
        config_layout.addRow(config_btn_layout)
        
        config_group.setLayout(config_layout)
        self.add_to_layout(config_group)
        
        self.add_stretch()
    
    def refresh_config_list(self):
        """刷新配置列表"""
        self.preset_combo.clear()
        presets = self.config_manager.get_available_presets()
        for preset in presets:
            self.preset_combo.addItem(preset)
    
    def on_preset_changed(self, preset_name):
        """预设切换时自动应用部分更新"""
        if not preset_name:
            return
            
        # 加载预设配置
        preset_config = self.config_manager.load_preset(preset_name)
        if not preset_config:
            return
            
        # 获取当前配置
        current_config = self.main_window.get_current_config()
        
        # 部分更新：只覆盖预设中定义的设置
        for key in preset_config:
            if key in current_config:
                current_config[key] = preset_config[key]
                
        # 应用更新后的配置
        self.main_window.apply_config(current_config)
    
    def save_config(self):
        """保存当前配置"""
        self.main_window.save_config()
    
    def load_config(self):
        """加载配置文件"""
        self.main_window.load_config()
    
    def reset_config(self):
        """重置配置为默认值"""
        self.config_manager.reset_to_default()
        self.main_window.update_ui_from_config()

def create_advanced_tab(parent):
    return AdvancedTab(parent)
