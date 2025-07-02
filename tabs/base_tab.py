from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QHBoxLayout, QGroupBox, QScrollArea, QSizePolicy
from PySide6.QtCore import Qt

class BaseTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建滚动区域
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        main_layout.addWidget(self.scroll)
        
        # 创建内容容器
        self.content = QWidget()
        self.content.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.layout = QVBoxLayout(self.content)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setContentsMargins(10, 10, 10, 10)  # 添加内边距
        self.scroll.setWidget(self.content)
    
    def create_form_group(self, title):
        """创建表单组"""
        group = QGroupBox(title)
        form_layout = QFormLayout()
        group.setLayout(form_layout)
        self.layout.addWidget(group)
        return form_layout
    
    def create_h_widget(self, widgets):
        """创建水平布局控件"""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        for w in widgets:
            layout.addWidget(w)
        widget.setLayout(layout)
        return widget
    
    def add_to_layout(self, widget):
        """添加控件到主布局"""
        self.layout.addWidget(widget)
    
    def add_stretch(self):
        """添加伸缩空间"""
        self.layout.addStretch()