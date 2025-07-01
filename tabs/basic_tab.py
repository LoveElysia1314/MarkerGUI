from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QLineEdit, QPushButton, QComboBox, QCheckBox, QSpinBox, QFormLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

def create_basic_tab(parent):
    tab = QWidget()
    layout = QVBoxLayout()
    tab.setLayout(layout)
    
    # 输入设置
    input_group = QGroupBox("输入设置")
    input_layout = QFormLayout()
    
    parent.input_path = QLineEdit()
    parent.browse_input_btn = QPushButton("浏览...")
    parent.browse_input_btn.clicked.connect(lambda: parent.browse_input("file"))
    parent.browse_folder_btn = QPushButton("浏览文件夹...")
    parent.browse_folder_btn.clicked.connect(lambda: parent.browse_input("folder"))
    
    input_layout.addRow("输入文件/目录:", parent.create_h_widget([
        parent.input_path, 
        parent.browse_input_btn, 
        parent.browse_folder_btn
    ]))
    
    parent.output_dir = QLineEdit()
    parent.browse_output_btn = QPushButton("浏览...")
    parent.browse_output_btn.clicked.connect(parent.browse_output)
    input_layout.addRow("输出目录:", parent.create_h_widget([
        parent.output_dir, 
        parent.browse_output_btn
    ]))
    
    parent.output_format = QComboBox()
    parent.output_format.addItems(["markdown", "text", "json"])
    input_layout.addRow("输出格式:", parent.output_format)
    
    parent.page_range = QLineEdit()
    input_layout.addRow("页面范围 (如 1-5,8):", parent.page_range)
    
    input_group.setLayout(input_layout)
    layout.addWidget(input_group)
    
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
    return tab