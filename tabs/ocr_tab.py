from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QLineEdit, QPushButton, QComboBox, QCheckBox, QSpinBox, QFormLayout, QScrollArea
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
    
    # OCR引擎设置
    engine_group = QGroupBox("OCR引擎设置")
    engine_layout = QVBoxLayout()
    
    # OCR模型选择
    model_layout = QHBoxLayout()
    model_layout.addWidget(QLabel("OCR模型:"))
    parent.ocr_model = QComboBox()
    parent.ocr_model.addItems([
        "donut-base (默认)", 
        "nougat-base", 
        "pix2struct-base"
    ])
    model_layout.addWidget(parent.ocr_model)
    model_layout.addStretch()
    engine_layout.addLayout(model_layout)
    
    # 语言选择
    lang_layout = QHBoxLayout()
    lang_layout.addWidget(QLabel("语言:"))
    parent.ocr_lang = QComboBox()
    parent.ocr_lang.addItems([
        "中文", "英文", "日文", "韩文", "法文", "德文", "西班牙文", "多语言"
    ])
    parent.ocr_lang.setCurrentText("中文")
    lang_layout.addWidget(parent.ocr_lang)
    lang_layout.addStretch()
    engine_layout.addLayout(lang_layout)
    
    # 设备选择
    device_layout = QHBoxLayout()
    device_layout.addWidget(QLabel("运行设备:"))
    parent.ocr_device = QComboBox()
    parent.ocr_device.addItems(["自动", "CPU", "GPU"])
    device_layout.addWidget(parent.ocr_device)
    device_layout.addStretch()
    engine_layout.addLayout(device_layout)
    
    engine_group.setLayout(engine_layout)
    layout.addWidget(engine_group)
    
    # OCR高级选项
    advanced_group = QGroupBox("OCR高级选项")
    advanced_layout = QVBoxLayout()
    
    # 批处理大小
    batch_layout = QHBoxLayout()
    batch_layout.addWidget(QLabel("批处理大小:"))
    parent.ocr_batch_size = QSpinBox()
    parent.ocr_batch_size.setRange(1, 32)
    parent.ocr_batch_size.setValue(4)
    batch_layout.addWidget(parent.ocr_batch_size)
    batch_layout.addStretch()
    advanced_layout.addLayout(batch_layout)
    
    # 最大图像尺寸
    img_size_layout = QHBoxLayout()
    img_size_layout.addWidget(QLabel("最大图像尺寸:"))
    parent.ocr_max_size = QSpinBox()
    parent.ocr_max_size.setRange(100, 4096)
    parent.ocr_max_size.setValue(2048)
    parent.ocr_max_size.setSuffix(" px")
    img_size_layout.addWidget(parent.ocr_max_size)
    img_size_layout.addStretch()
    advanced_layout.addLayout(img_size_layout)
    
    # 文本置信度阈值
    conf_layout = QHBoxLayout()
    conf_layout.addWidget(QLabel("文本置信度阈值:"))
    parent.ocr_confidence = QSpinBox()
    parent.ocr_confidence.setRange(0, 100)
    parent.ocr_confidence.setValue(85)
    parent.ocr_confidence.setSuffix("%")
    conf_layout.addWidget(parent.ocr_confidence)
    conf_layout.addStretch()
    advanced_layout.addLayout(conf_layout)
    
    # 高级选项复选框
    parent.ocr_keep_original_images = QCheckBox("保留原始图像（不压缩）")
    advanced_layout.addWidget(parent.ocr_keep_original_images)
    
    parent.ocr_skip_text_detection = QCheckBox("跳过文本检测（直接使用OCR）")
    advanced_layout.addWidget(parent.ocr_skip_text_detection)
    
    parent.ocr_ignore_layout_analysis = QCheckBox("忽略布局分析")
    advanced_layout.addWidget(parent.ocr_ignore_layout_analysis)
    
    parent.ocr_use_custom_vocab = QCheckBox("使用自定义词汇表")
    advanced_layout.addWidget(parent.ocr_use_custom_vocab)
    
    # 自定义词汇表路径
    vocab_layout = QHBoxLayout()
    vocab_layout.addWidget(QLabel("自定义词汇表路径:"))
    parent.ocr_vocab_path = QLineEdit()
    parent.browse_vocab_btn = QPushButton("浏览...")
    parent.browse_vocab_btn.clicked.connect(lambda: parent.browse_file("词汇表文件", parent.ocr_vocab_path))
    vocab_layout.addWidget(parent.ocr_vocab_path)
    vocab_layout.addWidget(parent.browse_vocab_btn)
    advanced_layout.addLayout(vocab_layout)
    
    advanced_group.setLayout(advanced_layout)
    layout.addWidget(advanced_group)
    
    # 后处理选项
    post_group = QGroupBox("后处理选项")
    post_layout = QVBoxLayout()
    
    parent.ocr_merge_paragraphs = QCheckBox("合并相邻段落")
    post_layout.addWidget(parent.ocr_merge_paragraphs)
    
    parent.ocr_remove_hyphens = QCheckBox("移除连字符")
    post_layout.addWidget(parent.ocr_remove_hyphens)
    
    parent.ocr_preserve_line_breaks = QCheckBox("保留换行符")
    post_layout.addWidget(parent.ocr_preserve_line_breaks)
    
    parent.ocr_correct_spelling = QCheckBox("自动拼写校正")
    post_layout.addWidget(parent.ocr_correct_spelling)
    
    # 拼写校正语言
    spell_lang_layout = QHBoxLayout()
    spell_lang_layout.addWidget(QLabel("拼写校正语言:"))
    parent.ocr_spell_lang = QComboBox()
    parent.ocr_spell_lang.addItems(["英文", "法文", "德文", "西班牙文"])
    spell_lang_layout.addWidget(parent.ocr_spell_lang)
    spell_lang_layout.addStretch()
    post_layout.addLayout(spell_lang_layout)
    
    post_group.setLayout(post_layout)
    layout.addWidget(post_group)
    
    layout.addStretch()
    return scroll