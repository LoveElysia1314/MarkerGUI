from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea

class BaseTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 创建滚动区域
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        
        # 创建内容容器
        self.content = QWidget()
        self.layout = QVBoxLayout(self.content)
        
        # 设置滚动区域的内容
        self.scroll.setWidget(self.content)
        
        # 设置主布局
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.scroll)
        main_layout.setContentsMargins(0, 0, 0, 0)