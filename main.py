"""
MarkerGUI Application Entry Point

This is the entry point for the MarkerGUI application.
It imports and runs the main window from the markergui package.
"""

import sys
from pathlib import Path

# Add src directory to Python path to allow imports from markergui package
# This works both in development and when packaged by PyInstaller
if not hasattr(sys, 'frozen'):
    # When running as a Python script, add src directory to path
    src_path = Path(__file__).parent / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

from PySide6.QtWidgets import QApplication
from markergui.main_window import MarkerGUI

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 设置应用程序样式
    app.setStyle("Fusion")

    # 创建主窗口
    window = MarkerGUI()
    window.show()

    # 运行应用程序
    sys.exit(app.exec())
