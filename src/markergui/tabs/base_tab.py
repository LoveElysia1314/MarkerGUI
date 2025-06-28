from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QHBoxLayout,
    QGroupBox,
    QScrollArea,
    QSizePolicy,
)
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

    def add_to_layout(self, widget):
        """向布局中添加组件"""
        self.layout.addWidget(widget)

    def add_stretch(self):
        """向布局末尾添加伸缩空间"""
        self.layout.addStretch()
