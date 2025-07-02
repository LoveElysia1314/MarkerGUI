import os
import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QGroupBox, QLabel, QLineEdit, QPushButton, QCheckBox, QComboBox,
    QTextEdit, QFileDialog, QMessageBox, QSpinBox, QFormLayout, QInputDialog, QApplication, QSplitter
)
from PySide6.QtCore import Qt, Signal, QProcess, QThread, QObject
from PySide6.QtGui import QFont
from config_manager import ConfigManager
from tabs.basic_tab import create_basic_tab
from tabs.ocr_tab import create_ocr_tab
from tabs.llm_tab import create_llm_tab
from tabs.advanced_tab import AdvancedTab
from command_generator import generate_command
from utils import EmittingStream

class CommandWorker(QObject):
    """异步执行命令的工作线程"""
    output = Signal(str)
    finished = Signal(int)
    error = Signal(str)
    
    def __init__(self, command):
        super().__init__()
        self.command = command
        self.process = None
    
    def run(self):
        """执行命令并捕获输出"""
        try:
            self.process = QProcess()
            self.process.readyReadStandardOutput.connect(self.handle_output)
            self.process.readyReadStandardError.connect(self.handle_error)
            self.process.finished.connect(self.handle_finished)
            
            # 在Windows上使用cmd.exe执行命令
            self.process.start("cmd.exe", ["/c", self.command])
            if not self.process.waitForStarted():
                self.error.emit("无法启动命令进程")
                return
                
            # 等待命令完成（使用事件循环）
            self.process.waitForFinished(-1)
                
        except Exception as e:
            self.error.emit(str(e))
    
    def handle_output(self):
        """处理标准输出"""
        output = self.process.readAllStandardOutput().data().decode().strip()
        if output:
            self.output.emit(output)
    
    def handle_error(self):
        """处理错误输出"""
        error = self.process.readAllStandardError().data().decode().strip()
        if error:
            self.error.emit(error)
    
    def handle_finished(self, exit_code):
        """命令执行完成"""
        self.finished.emit(exit_code)
        
    def terminate(self):
        """终止命令执行"""
        if self.process and self.process.state() == QProcess.Running:
            self.process.terminate()

class MarkerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Marker Document Converter")
        # 设置初始最小尺寸
        self.setMinimumWidth(800)
        self.setMinimumHeight(400)
        
        # 初始化配置管理器
        self.config_manager = ConfigManager()
        self.worker = None  # 异步工作线程
        self.thread = None  # QThread实例
        
        # 创建主分割器（水平3:2）
        main_splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(main_splitter)
        
        # 左面板（60%）
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)
        
        # 右面板（40%）
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)
        
        # 添加左右面板到主分割器
        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(right_widget)
        main_splitter.setSizes([600, 400])  # 初始比例3:2
        
        # 左面板垂直分割（上功能区40%，下功能区60%）
        left_splitter = QSplitter(Qt.Vertical)
        left_layout.addWidget(left_splitter)
        
        # 上功能区：命令行输出
        console_group = QGroupBox("命令行输出")
        console_layout = QVBoxLayout()
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setFont(QFont("Courier New", 9))
        console_layout.addWidget(self.console_output)
        
        # 控制按钮
        control_btn_layout = QHBoxLayout()
        self.clear_btn = QPushButton("清除命令行")
        self.clear_btn.clicked.connect(self.clear_console)
        self.stop_btn = QPushButton("终止运行")
        self.stop_btn.clicked.connect(self.stop_command)
        control_btn_layout.addWidget(self.clear_btn)
        control_btn_layout.addWidget(self.stop_btn)
        console_layout.addLayout(control_btn_layout)
        
        console_group.setLayout(console_layout)
        left_splitter.addWidget(console_group)
        
        # 下功能区：生成的命令
        command_group = QGroupBox("生成的命令")
        command_layout = QVBoxLayout()
        self.command_output = QTextEdit()
        self.command_output.setReadOnly(True)
        self.command_output.setFont(QFont("Courier New", 10))
        self.command_output.setLineWrapMode(QTextEdit.WidgetWidth)
        command_layout.addWidget(self.command_output)
        
        # 命令组按钮（在文本控件下方）
        command_btn_layout = QHBoxLayout()
        self.generate_btn = QPushButton("生成命令")
        self.generate_btn.clicked.connect(self.generate_command)
        self.copy_btn = QPushButton("复制命令")
        self.copy_btn.clicked.connect(self.copy_command)
        self.run_btn = QPushButton("运行命令")
        self.run_btn.clicked.connect(self.run_command)
        command_btn_layout.addWidget(self.generate_btn)
        command_btn_layout.addWidget(self.copy_btn)
        command_btn_layout.addWidget(self.run_btn)
        
        command_layout.addLayout(command_btn_layout)
        command_group.setLayout(command_layout)
        left_splitter.addWidget(command_group)
        
        # 输入和输出设置 (从基本设置页移出)
        input_output_group = QGroupBox("输入和输出设置")
        input_output_layout = QFormLayout()
        
        self.input_path = QLineEdit()
        self.browse_input_btn = QPushButton("浏览...")
        self.browse_input_btn.clicked.connect(lambda: self.browse_input("file"))
        self.browse_folder_btn = QPushButton("浏览文件夹...")
        self.browse_folder_btn.clicked.connect(lambda: self.browse_input("folder"))
        
        input_output_layout.addRow("输入文件/目录:", self.create_h_widget([
            self.input_path, 
            self.browse_input_btn, 
            self.browse_folder_btn
        ]))
        
        self.output_dir = QLineEdit()
        self.browse_output_btn = QPushButton("浏览...")
        self.browse_output_btn.clicked.connect(self.browse_output)
        input_output_layout.addRow("输出目录:", self.create_h_widget([
            self.output_dir, 
            self.browse_output_btn
        ]))
        
        self.output_format = QComboBox()
        self.output_format.addItems(["markdown", "text", "json"])
        input_output_layout.addRow("输出格式:", self.output_format)
        
        self.page_range = QLineEdit()
        input_output_layout.addRow("页面范围 (如 1-5,8):", self.page_range)
        
        input_output_group.setLayout(input_output_layout)
        left_splitter.addWidget(input_output_group)
        
        # 调整分割器大小比例 (3:2:2)
        left_splitter.setSizes([600, 400, 400])  
        
        # 右面板：标签页
        self.tabs = QTabWidget()
        right_layout.addWidget(self.tabs)
        
        # 添加标签页 (移除基本设置页中的输入输出控件)
        self.tabs.addTab(create_basic_tab(self), "基本设置")
        self.tabs.addTab(create_ocr_tab(self), "OCR设置")
        self.tabs.addTab(create_llm_tab(self), "LLM设置")
        self.tabs.addTab(AdvancedTab(self), "高级设置")
        
        # 初始化输出重定向
        self.init_output_redirection()
        
        # 初始化配置
        self.config_manager.reset_to_default()
        self.toggle_llm_options(False)
        
        # 添加自适应宽度逻辑
        self.adjustSize()
        
    def init_output_redirection(self):
        """初始化输出重定向到命令行控件"""
        self.output_stream = EmittingStream()
        sys.stdout = self.output_stream
        self.output_stream.textWritten.connect(self.handle_console_output)
        
    def handle_console_output(self, text):
        """处理控制台输出"""
        self.console_output.append(text)  # 直接附加文本，无颜色格式化
        
    def clear_console(self):
        """清除命令行输出"""
        self.console_output.clear()
        
    def create_h_widget(self, widgets):
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        for w in widgets:
            layout.addWidget(w)
        widget.setLayout(layout)
        return widget

    def toggle_llm_options(self, enabled):
        # 启用或禁用LLM相关选项
        self.redo_inline_math.setEnabled(enabled)
        self.llm_service.setEnabled(enabled)
        self.gemini_api_key.setEnabled(enabled)
        self.gemini_model_name.setEnabled(enabled)
        self.vertex_project_id.setEnabled(enabled)
        self.vertex_location.setEnabled(enabled)
        self.ollama_base_url.setEnabled(enabled)
        self.ollama_model.setEnabled(enabled)
        self.claude_api_key.setEnabled(enabled)
        self.claude_model_name.setEnabled(enabled)
        self.openai_api_key.setEnabled(enabled)
        self.openai_model.setEnabled(enabled)
        self.openai_base_url.setEnabled(enabled)
        self.max_concurrency.setEnabled(enabled)
        self.timeout.setEnabled(enabled)
        self.max_retries.setEnabled(enabled)

    def browse_input(self, input_type):
        """浏览输入文件或文件夹"""
        if input_type == "file":
            path, _ = QFileDialog.getOpenFileName(self, "选择输入文件", "", "所有文件 (*.*)")
        else:  # folder
            path = QFileDialog.getExistingDirectory(self, "选择输入文件夹")
        
        if path:
            self.input_path.setText(path)

    def browse_output(self):
        path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if path:
            self.output_dir.setText(path)

    def generate_command(self):
        """使用外部命令生成器生成命令"""
        command = generate_command(self)
        if command:
            self.command_output.setText(command)
            
    def copy_command(self):
        command = self.command_output.toPlainText()
        if command:
            QApplication.clipboard().setText(command)
            print("[INFO] 复制成功: 命令已复制到剪贴板")
        else:
            print("[WORRY] 复制错误: 没有可复制的命令")
            
    def run_command(self):
        """异步运行生成的命令"""
        command = self.command_output.toPlainText().strip()
        if not command:
            print("[WORRY] 运行错误: 没有可运行的命令")
            return
        
        # 创建并启动工作线程
        self.worker = CommandWorker(command)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        
        # 连接信号
        self.worker.output.connect(self.handle_command_output)
        self.worker.error.connect(self.handle_command_error)
        self.worker.finished.connect(self.on_command_finished)
        self.thread.started.connect(self.worker.run)
        
        print(f"[INFO] 开始执行命令: {command}")
        self.thread.start()
    
    def handle_command_output(self, text):
        """处理命令输出"""
        print(text)
    
    def handle_command_error(self, error):
        """处理命令错误"""
        print(f"[ERROR] {error}")
    
    def on_command_finished(self, exit_code):
        """命令执行完成"""
        self.thread.quit()
        self.thread.wait()
        if exit_code == 0:
            print("[INFO] 命令执行成功")
        else:
            print(f"[WORRY] 命令异常退出，代码: {exit_code}")
    
    def stop_command(self):
        """终止正在运行的命令"""
        if hasattr(self, 'worker') and self.worker:
            self.worker.terminate()
            print("[INFO] 命令运行已终止")
        else:
            print("[WORRY] 没有正在运行的命令")

    def get_current_config(self):
        """获取当前UI配置数据"""
        # 获取高级标签页
        advanced_tab = self.tabs.widget(3)  # 第4个标签页是高级设置
        
        return {
            "input_path": self.input_path.text(),
            "output_dir": self.output_dir.text(),
            "output_format": self.output_format.currentText(),
            "page_range": self.page_range.text(),
            "paginate_output": self.paginate_output.isChecked(),
            "disable_image_extraction": self.disable_image_extraction.isChecked(),
            "disable_multiprocessing": self.disable_multiprocessing.isChecked(),
            "debug_mode": self.debug_mode.isChecked(),
            "pdftext_workers": self.pdftext_workers.value(),
            "format_lines": self.format_lines.isChecked(),
            "force_ocr": self.force_ocr.isChecked(),
            "strip_existing_ocr": self.strip_existing_ocr.isChecked(),
            "ocr_task_name": self.ocr_task_name.currentText(),
            "disable_ocr_math": self.disable_ocr_math.isChecked(),
            "drop_repeated_text": self.drop_repeated_text.isChecked(),
            "converter_cls": self.converter_cls.currentText(),
            "force_layout_block": self.force_layout_block.text(),
            "use_llm": self.use_llm.isChecked(),
            "redo_inline_math": self.redo_inline_math.isChecked(),
            "llm_service": self.llm_service.currentText(),
            "gemini_api_key": self.gemini_api_key.text(),
            "gemini_model_name": self.gemini_model_name.text(),
            "vertex_project_id": self.vertex_project_id.text(),
            "vertex_location": self.vertex_location.text(),
            "ollama_base_url": self.ollama_base_url.text(),
            "ollama_model": self.ollama_model.text(),
            "claude_api_key": self.claude_api_key.text(),
            "claude_model_name": self.claude_model_name.text(),
            "openai_api_key": self.openai_api_key.text(),
            "openai_model": self.openai_model.text(),
            "openai_base_url": self.openai_base_url.text(),
            "max_concurrency": self.max_concurrency.value(),
            "timeout": self.timeout.value(),
            "max_retries": self.max_retries.value(),
            "processors": advanced_tab.processors.text() if hasattr(advanced_tab, 'processors') else "",
            "num_devices": advanced_tab.num_devices.value() if hasattr(advanced_tab, 'num_devices') else 1,
            "debug_data_folder": advanced_tab.debug_data_folder.text() if hasattr(advanced_tab, 'debug_data_folder') else "",
            "debug_layout_images": advanced_tab.debug_layout_images.isChecked() if hasattr(advanced_tab, 'debug_layout_images') else False,
            "debug_pdf_images": advanced_tab.debug_pdf_images.isChecked() if hasattr(advanced_tab, 'debug_pdf_images') else False,
            "debug_json": advanced_tab.debug_json.isChecked() if hasattr(advanced_tab, 'debug_json') else False,
            "num_workers": advanced_tab.num_workers.value() if hasattr(advanced_tab, 'num_workers') else 15,
        }
    
    def save_config(self):
        # 获取当前配置名称
        current_config = self.preset_combo.currentText()
        config_name, ok = QInputDialog.getText(
            self, "保存配置", "输入配置名称:",
            QLineEdit.EchoMode.Normal, current_config
        )
        
        if not ok or not config_name:
            return
        
        # 获取当前UI配置
        config_data = self.get_current_config()
        
        # 保存配置
        if self.config_manager.save_preset(
            config_name,
            config_data,
            description=f"用户自定义配置: {config_name}",
            overwrite=True
        ):
            print("[INFO] 保存成功: 配置已成功保存")
            self.refresh_config_list()
            self.preset_combo.setCurrentText(config_name)
        else:
            print("[ERROR] 保存失败: 无法保存配置")

    def set_combo_text(self, combo, text):
        index = combo.findText(text)
        if index >= 0:
            combo.setCurrentIndex(index)
        else:
            combo.addItem(text)
            combo.setCurrentIndex(combo.count() - 1)
