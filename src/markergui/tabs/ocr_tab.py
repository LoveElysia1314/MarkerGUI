from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QCheckBox,
    QSpinBox,
    QFormLayout,
    QScrollArea,
)
from PySide6.QtCore import Qt


def create_ocr_tab(parent):
    # 创建滚动区域
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)

    # 创建内容容器
    content = QWidget()
    layout = QVBoxLayout(content)
    scroll.setWidget(content)

    # OCR基础选项
    ocr_basic_group = QGroupBox("OCR基础选项")
    ocr_basic_layout = QVBoxLayout()

    parent.format_lines = QCheckBox("格式化行 (移除多余空格)")
    ocr_basic_layout.addWidget(parent.format_lines)

    # OCR处理模式（互斥选择）
    ocr_mode_layout = QHBoxLayout()
    ocr_mode_layout.addWidget(QLabel("OCR处理模式:"))
    parent.ocr_mode = QComboBox()
    parent.ocr_mode.addItems(["标准OCR (默认)", "禁用OCR", "强制OCR (扫描所有)"])
    parent.ocr_mode.setToolTip("选择如何处理PDF中的OCR文本")
    ocr_mode_layout.addWidget(parent.ocr_mode)
    ocr_mode_layout.addStretch()
    ocr_basic_layout.addLayout(ocr_mode_layout)

    parent.strip_existing_ocr = QCheckBox("移除现有OCR文本")
    ocr_basic_layout.addWidget(parent.strip_existing_ocr)

    ocr_task_layout = QHBoxLayout()
    ocr_task_layout.addWidget(QLabel("OCR任务模式:"))
    parent.ocr_task_name = QComboBox()
    parent.ocr_task_name.addItems(
        ["ocr_with_boxes", "ocr_with_paragraphs", "ocr_with_tables"]
    )
    ocr_task_layout.addWidget(parent.ocr_task_name)
    ocr_task_layout.addStretch()
    ocr_basic_layout.addLayout(ocr_task_layout)

    parent.disable_ocr_math = QCheckBox("禁用OCR数学公式识别")
    ocr_basic_layout.addWidget(parent.disable_ocr_math)

    parent.drop_repeated_text = QCheckBox("移除重复文本")
    ocr_basic_layout.addWidget(parent.drop_repeated_text)

    ocr_basic_group.setLayout(ocr_basic_layout)
    layout.addWidget(ocr_basic_group)

    layout.addStretch()
    return scroll
