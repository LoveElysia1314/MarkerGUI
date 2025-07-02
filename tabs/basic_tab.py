from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QLineEdit, QPushButton, QComboBox, QCheckBox, QSpinBox, QFormLayout, QScrollArea,QSizePolicy
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
    
    # 转换器设置
    converter_group = QGroupBox("转换器设置")
    converter_layout = QVBoxLayout()
    
    converter_type_layout = QHBoxLayout()
    converter_type_layout.addWidget(QLabel("转换器类型:"))
    parent.converter_cls = QComboBox()
    parent.converter_cls.addItems([
        "marker.converters.pdf.PdfConverter (默认)",
        "marker.converters.table.TableConverter",
        "marker.converters.ocr.OCRConverter",
        "marker.converters.extraction.ExtractionConverter"
    ])
    converter_type_layout.addWidget(parent.converter_cls)
    converter_type_layout.addStretch()
    converter_layout.addLayout(converter_type_layout)
    
    force_layout_layout = QHBoxLayout()
    force_layout_layout.addWidget(QLabel("强制布局块 (高级):"))
    parent.force_layout_block = QLineEdit()
    force_layout_layout.addWidget(parent.force_layout_block)
    converter_layout.addLayout(force_layout_layout)
    
    converter_group.setLayout(converter_layout)
    layout.addWidget(converter_group)
    
    layout.addStretch()
    return scroll
