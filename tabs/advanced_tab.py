from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QLineEdit, QPushButton, QComboBox, QCheckBox, QSpinBox, QFormLayout
)
from PyQt6.QtCore import Qt

def create_advanced_tab(parent):
    tab = QWidget()
    layout = QVBoxLayout()
    tab.setLayout(layout)
    
    # 处理器设置
    processor_group = QGroupBox("处理器设置")
    processor_layout = QFormLayout()
    
    parent.processors = QLineEdit()
    processor_layout.addRow("自定义处理器链:", parent.processors)
    processor_layout.addRow(QLabel("格式: processor1,processor2,..."))
    
    processor_group.setLayout(processor_layout)
    layout.addWidget(processor_group)
    
    # 多GPU设置
    gpu_group = QGroupBox("多GPU设置")
    gpu_layout = QFormLayout()
    
    num_devices_layout = QHBoxLayout()
    num_devices_layout.addWidget(QLabel("GPU数量:"))
    parent.num_devices = QSpinBox()
    parent.num_devices.setRange(1, 8)
    parent.num_devices.setValue(1)
    num_devices_layout.addWidget(parent.num_devices)
    gpu_layout.addRow(num_devices_layout)
    
    num_workers_layout = QHBoxLayout()
    num_workers_layout.addWidget(QLabel("每GPU工作进程数:"))
    parent.num_workers = QSpinBox()
    parent.num_workers.setRange(1, 64)
    parent.num_workers.setValue(15)
    num_workers_layout.addWidget(parent.num_workers)
    gpu_layout.addRow(num_workers_layout)
    
    gpu_group.setLayout(gpu_layout)
    layout.addWidget(gpu_group)
    
    # 调试设置
    debug_group = QGroupBox("调试设置")
    debug_layout = QFormLayout()
    
    parent.debug_data_folder = QLineEdit()
    debug_layout.addRow("调试数据存储目录:", parent.debug_data_folder)
    
    debug_check_layout = QVBoxLayout()
    parent.debug_layout_images = QCheckBox("保存布局分析图像")
    debug_check_layout.addWidget(parent.debug_layout_images)
    parent.debug_pdf_images = QCheckBox("保存PDF解析图像")
    debug_check_layout.addWidget(parent.debug_pdf_images)
    parent.debug_json = QCheckBox("保存中间JSON数据")
    debug_check_layout.addWidget(parent.debug_json)
    debug_layout.addRow("调试选项:", debug_check_layout)
    
    debug_group.setLayout(debug_layout)
    layout.addWidget(debug_group)
    
    # 配置管理
    config_group = QGroupBox("配置管理")
    config_layout = QFormLayout()
    
    parent.preset_combo = QComboBox()
    config_layout.addRow("当前预设:", parent.preset_combo)
    parent.refresh_config_list()
    
    config_btn_layout = QHBoxLayout()
    parent.apply_preset_btn = QPushButton("应用预设")
    parent.apply_preset_btn.clicked.connect(parent.apply_preset)
    parent.save_config_btn = QPushButton("保存配置")
    parent.save_config_btn.clicked.connect(parent.save_config)
    parent.load_config_btn = QPushButton("加载配置")
    parent.load_config_btn.clicked.connect(parent.load_config)
    parent.reset_config_btn = QPushButton("重置配置")
    parent.reset_config_btn.clicked.connect(parent.reset_config)
    
    config_btn_layout.addWidget(parent.apply_preset_btn)
    config_btn_layout.addWidget(parent.save_config_btn)
    config_btn_layout.addWidget(parent.load_config_btn)
    config_btn_layout.addWidget(parent.reset_config_btn)
    config_layout.addRow(config_btn_layout)
    
    config_group.setLayout(config_layout)
    layout.addWidget(config_group)
    
    layout.addStretch()
    return tab