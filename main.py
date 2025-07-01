import sys
from PySide6.QtWidgets import QApplication
from main_window import MarkerGUI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle("Fusion")
    
    # 创建主窗口
    window = MarkerGUI()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())