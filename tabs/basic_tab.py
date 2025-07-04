from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QLineEdit, QPushButton, QComboBox, QCheckBox, QSpinBox, QFormLayout, QScrollArea, QSizePolicy, QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

def create_basic_tab(parent):
    # 创建滚动区域
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 禁用水平滚动条
    
    # 创建内容容器
    content = QWidget()
    content.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)  # 设置尺寸策略
    layout = QVBoxLayout(content)
    layout.setAlignment(Qt.AlignTop)  # 顶部对齐
    scroll.setWidget(content)
    
    
    # 基本选项
    basic_group = QGroupBox("基本选项")
    basic_layout = QVBoxLayout()
    
    parent.paginate_output = QCheckBox("分页输出 (每个页面单独文件)")
    basic_layout.addWidget(parent.paginate_output)
    
    parent.disable_image_extraction = QCheckBox("禁用图片提取")
    basic_layout.addWidget(parent.disable_image_extraction)
    
    parent.disable_multiprocessing = QCheckBox("禁用多进程处理")
    basic_layout.addWidget(parent.disable_multiprocessing)
    
    parent.debug_mode = QCheckBox("启用调试模式")
    basic_layout.addWidget(parent.debug_mode)
    
    pdftext_layout = QHBoxLayout()
    pdftext_layout.addWidget(QLabel("PDF文本提取工作进程数:"))
    parent.pdftext_workers = QSpinBox()
    parent.pdftext_workers.setRange(1, 16)
    parent.pdftext_workers.setValue(4)
    pdftext_layout.addWidget(parent.pdftext_workers)
    pdftext_layout.addStretch()
    basic_layout.addLayout(pdftext_layout)
    
    basic_group.setLayout(basic_layout)
    layout.addWidget(basic_group)
    
    # OCR基础选项
    ocr_basic_group = QGroupBox("OCR基础选项")
    ocr_basic_layout = QVBoxLayout()
    
    parent.format_lines = QCheckBox("格式化行 (移除多余空格)")
    ocr_basic_layout.addWidget(parent.format_lines)
    
    parent.force_ocr = QCheckBox("强制OCR (忽略现有文本)")
    ocr_basic_layout.addWidget(parent.force_ocr)
    
    parent.strip_existing_ocr = QCheckBox("移除现有OCR文本")
    ocr_basic_layout.addWidget(parent.strip_existing_ocr)
    
    ocr_task_layout = QHBoxLayout()
    ocr_task_layout.addWidget(QLabel("OCR任务模式:"))
    parent.ocr_task_name = QComboBox()
    parent.ocr_task_name.addItems([
        "ocr_with_boxes", 
        "ocr_with_paragraphs", 
        "ocr_with_tables"
    ])
    ocr_task_layout.addWidget(parent.ocr_task_name)
    ocr_task_layout.addStretch()
    ocr_basic_layout.addLayout(ocr_task_layout)
    
    parent.disable_ocr_math = QCheckBox("禁用OCR数学公式识别")
    ocr_basic_layout.addWidget(parent.disable_ocr_math)
    
    parent.drop_repeated_text = QCheckBox("移除重复文本")
    ocr_basic_layout.addWidget(parent.drop_repeated_text)
    
    ocr_basic_group.setLayout(ocr_basic_layout)
    layout.addWidget(ocr_basic_group)
    
    # 配置管理
    config_group = QGroupBox("配置管理")
    config_layout = QFormLayout()
    
    parent.preset_combo = QComboBox()
    config_layout.addRow("当前预设:", parent.preset_combo)
    
    # 刷新配置列表函数
    def refresh_config_list():
        parent.preset_combo.clear()
        presets = parent.config_manager.get_available_presets()
        for preset in presets:
            parent.preset_combo.addItem(preset)
    
    # 预设切换处理函数
    def on_preset_changed(preset_name):
        if not preset_name:
            return
        preset_config = parent.config_manager.load_preset(preset_name)
        # 确保配置是字典类型
        if not preset_config or not isinstance(preset_config, dict):
            print(f"[ERROR] 加载预设失败: '{preset_name}' 无效的配置格式")
            return
        current_config = parent.get_current_config()
        for key in preset_config:
            if key in current_config:
                current_config[key] = preset_config[key]
        parent.apply_config(current_config)
    
    # 连接信号
    parent.preset_combo.currentTextChanged.connect(on_preset_changed)
    refresh_config_list()  # 初始刷新
    
    # 使用网格布局实现换行效果
    config_btn_layout = QGridLayout()
    parent.save_config_btn = QPushButton("保存配置")
    parent.save_config_btn.clicked.connect(parent.save_config)
    parent.reset_config_btn = QPushButton("重置配置")
    parent.reset_config_btn.clicked.connect(parent.reset_config)
    parent.delete_config_btn = QPushButton("删除预设")
    parent.delete_config_btn.clicked.connect(parent.delete_preset)
    parent.reset_preset_btn = QPushButton("重置预设")
    parent.reset_preset_btn.clicked.connect(parent.reset_preset)
    
    # 将按钮添加到网格布局中，每行最多2个按钮
    config_btn_layout.addWidget(parent.save_config_btn, 0, 0)
    config_btn_layout.addWidget(parent.reset_config_btn, 0, 1)
    config_btn_layout.addWidget(parent.delete_config_btn, 1, 0)
    config_btn_layout.addWidget(parent.reset_preset_btn, 1, 1)
    
    # 添加布局到表单
    config_layout.addRow(config_btn_layout)
    
    config_group.setLayout(config_layout)
    layout.addWidget(config_group)
    
    layout.addStretch()
    return scroll
