import os
import sys
import shlex
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QGroupBox, QLabel, QLineEdit, QPushButton, QCheckBox, QComboBox,
    QTextEdit, QFileDialog, QMessageBox, QSpinBox, QFormLayout, QInputDialog, QApplication, QSplitter
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from config_manager import ConfigManager
from tabs.basic_tab import create_basic_tab
from tabs.ocr_tab import create_ocr_tab
from tabs.llm_tab import create_llm_tab
from tabs.advanced_tab import AdvancedTab
from command_generator import generate_command
from utils import EmittingStream

class MarkerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Marker Document Converter")
        # 设置初始最小尺寸
        self.setMinimumWidth(800)
        self.setMinimumHeight(400)
        
        # 初始化配置管理器
        self.config_manager = ConfigManager()
        # 不再使用QProcess，改为直接执行命令
        self.process = None  # 保留变量但设为None以防引用错误
        
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
        
        # 左面板分页
        self.left_tabs = QTabWidget()
        left_layout.addWidget(self.left_tabs)
        
        # 第一页：控制台
        console_page = QWidget()
        console_page_layout = QVBoxLayout()
        console_page.setLayout(console_page_layout)
        self.left_tabs.addTab(console_page, "控制台")
        
        # 控制台页垂直分割器
        console_splitter = QSplitter(Qt.Vertical)
        console_page_layout.addWidget(console_splitter)
        
        # 运行日志组（新终端控件）
        runtime_log_group = QGroupBox("运行日志")
        runtime_log_layout = QVBoxLayout()
        self.runtime_log = QTextEdit()
        self.runtime_log.setReadOnly(True)
        self.runtime_log.setFont(QFont("Courier New", 9))
        runtime_log_layout.addWidget(self.runtime_log)
        runtime_log_group.setLayout(runtime_log_layout)
        console_splitter.addWidget(runtime_log_group)
        
        # 生成的命令组
        command_group = QGroupBox("生成的命令")
        command_layout = QVBoxLayout()
        self.command_output = QTextEdit()
        self.command_output.setReadOnly(True)
        self.command_output.setFont(QFont("Courier New", 10))
        self.command_output.setLineWrapMode(QTextEdit.WidgetWidth)
        command_layout.addWidget(self.command_output)
        
        # 命令组按钮
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
        console_splitter.addWidget(command_group)
        
        # 设置运行日志组和命令组比例 2:1
        console_splitter.setSizes([400, 200])
        
        # 输入和输出设置组
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
        console_page_layout.addWidget(input_output_group)
        
        # 转换器设置组（从基本设置页迁移）
        converter_group = QGroupBox("转换器设置")
        converter_layout = QVBoxLayout()
        
        converter_type_layout = QHBoxLayout()
        converter_type_layout.addWidget(QLabel("转换器类型:"))
        self.converter_cls = QComboBox()
        self.converter_cls.addItems([
            "marker.converters.pdf.PdfConverter (默认)",
            "marker.converters.table.TableConverter",
            "marker.converters.ocr.OCRConverter",
            "marker.converters.extraction.ExtractionConverter"
        ])
        converter_type_layout.addWidget(self.converter_cls)
        converter_type_layout.addStretch()
        converter_layout.addLayout(converter_type_layout)
        
        force_layout_layout = QHBoxLayout()
        force_layout_layout.addWidget(QLabel("强制布局块 (高级):"))
        self.force_layout_block = QLineEdit()
        force_layout_layout.addWidget(self.force_layout_block)
        converter_layout.addLayout(force_layout_layout)
        
        converter_group.setLayout(converter_layout)
        console_page_layout.addWidget(converter_group)
        
        
        # 右面板：标签页
        self.tabs = QTabWidget()
        right_layout.addWidget(self.tabs)
        
        # 添加标签页（基本设置页已移除转换器设置）
        self.tabs.addTab(create_basic_tab(self), "基本设置")
        self.tabs.addTab(create_ocr_tab(self), "OCR设置")
        self.tabs.addTab(create_llm_tab(self), "LLM设置")
        self.tabs.addTab(AdvancedTab(self), "高级设置")
        
        # 初始化输出重定向到运行日志
        self.init_output_redirection()
        
        # 初始化配置
        self.config_manager.reset_to_default()
        self.toggle_llm_options(False)
        
        # 添加自适应宽度逻辑
        self.adjustSize()
        
    def init_output_redirection(self):
        """初始化输出重定向"""
        # 程序日志重定向到运行日志
        self.program_stream = EmittingStream()
        sys.stdout = self.program_stream
        self.program_stream.textWritten.connect(self.handle_runtime_output)
        
    def handle_runtime_output(self, text):
        """处理运行日志输出"""
        self.runtime_log.append(text)
        
    def handle_console_output(self, text):
        """处理命令行输出（历史日志）"""
        self.console_output.append(text)
        
    def clear_console(self):
        """清除历史日志"""
        self.console_output.clear()
        
    def clear_runtime_log(self):
        """清除运行日志"""
        self.runtime_log.clear()
        
        # 初始化输出重定向
        self.init_output_redirection()
        
        # 初始化配置
        self.config_manager.reset_to_default()
        self.toggle_llm_options(False)
        
        # 添加自适应宽度逻辑
        self.adjustSize()
        
    def handle_runtime_output(self, text):
        """处理运行日志输出"""
        self.runtime_log.append(text)
        
    def handle_console_output(self, text):
        """处理命令行输出（历史日志）"""
        self.console_output.append(text)
        
    def clear_runtime_log(self):
        """清除运行日志"""
        self.runtime_log.clear()
        
    def clear_console(self):
        """清除历史日志"""
        self.console_output.clear()
        
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
        """在新cmd窗口中执行命令"""
        command = self.command_output.toPlainText().strip()
        if not command:
            print("[WORRY] 运行错误: 没有可运行的命令")
            return
        
        # 使用os.system在新窗口执行命令
        full_command = f'start cmd /k "{command}"'
        print(f"[INFO] 在新窗口执行命令: {command}")
        os.system(full_command)
    
    
    
    

    def get_current_config(self):
        """获取当前UI配置数据"""
        # 获取高级标签页（索引可能变化，改为按名称查找）
        advanced_tab = None
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == "高级设置":
                advanced_tab = self.tabs.widget(i)
                break
        
        # 添加属性存在性检查
        return {
            "input_path": self.input_path.text(),
            "output_dir": self.output_dir.text(),
            "output_format": self.output_format.currentText(),
            "page_range": self.page_range.text(),
            "paginate_output": getattr(self, 'paginate_output', None).isChecked() if hasattr(self, 'paginate_output') else False,
            "disable_image_extraction": getattr(self, 'disable_image_extraction', None).isChecked() if hasattr(self, 'disable_image_extraction') else False,
            "disable_multiprocessing": getattr(self, 'disable_multiprocessing', None).isChecked() if hasattr(self, 'disable_multiprocessing') else False,
            "debug_mode": getattr(self, 'debug_mode', None).isChecked() if hasattr(self, 'debug_mode') else False,
            "pdftext_workers": getattr(self, 'pdftext_workers', None).value() if hasattr(self, 'pdftext_workers') else 4,
            "format_lines": getattr(self, 'format_lines', None).isChecked() if hasattr(self, 'format_lines') else False,
            "force_ocr": getattr(self, 'force_ocr', None).isChecked() if hasattr(self, 'force_ocr') else False,
            "strip_existing_ocr": getattr(self, 'strip_existing_ocr', None).isChecked() if hasattr(self, 'strip_existing_ocr') else False,
            "ocr_task_name": getattr(self, 'ocr_task_name', None).currentText() if hasattr(self, 'ocr_task_name') else "",
            "disable_ocr_math": getattr(self, 'disable_ocr_math', None).isChecked() if hasattr(self, 'disable_ocr_math') else False,
            "drop_repeated_text": getattr(self, 'drop_repeated_text', None).isChecked() if hasattr(self, 'drop_repeated_text') else False,
            "converter_cls": getattr(self, 'converter_cls', None).currentText() if hasattr(self, 'converter_cls') else "",
            "force_layout_block": getattr(self, 'force_layout_block', None).text() if hasattr(self, 'force_layout_block') else "",
            "use_llm": getattr(self, 'use_llm', None).isChecked() if hasattr(self, 'use_llm') else False,
            "redo_inline_math": getattr(self, 'redo_inline_math', None).isChecked() if hasattr(self, 'redo_inline_math') else False,
            "llm_service": getattr(self, 'llm_service', None).currentText() if hasattr(self, 'llm_service') else "",
            "gemini_api_key": getattr(self, 'gemini_api_key', None).text() if hasattr(self, 'gemini_api_key') else "",
            "gemini_model_name": getattr(self, 'gemini_model_name', None).text() if hasattr(self, 'gemini_model_name') else "",
            "vertex_project_id": getattr(self, 'vertex_project_id', None).text() if hasattr(self, 'vertex_project_id') else "",
            "vertex_location": getattr(self, 'vertex_location', None).text() if hasattr(self, 'vertex_location') else "",
            "ollama_base_url": getattr(self, 'ollama_base_url', None).text() if hasattr(self, 'ollama_base_url') else "",
            "ollama_model": getattr(self, 'ollama_model', None).text() if hasattr(self, 'ollama_model') else "",
            "claude_api_key": getattr(self, 'claude_api_key', None).text() if hasattr(self, 'claude_api_key') else "",
            "claude_model_name": getattr(self, 'claude_model_name', None).text() if hasattr(self, 'claude_model_name') else "",
            "openai_api_key": getattr(self, 'openai_api_key', None).text() if hasattr(self, 'openai_api_key') else "",
            "openai_model": getattr(self, 'openai_model', None).text() if hasattr(self, 'openai_model') else "",
            "openai_base_url": getattr(self, 'openai_base_url', None).text() if hasattr(self, 'openai_base_url') else "",
            "max_concurrency": getattr(self, 'max_concurrency', None).value() if hasattr(self, 'max_concurrency') else 1,
            "timeout": getattr(self, 'timeout', None).value() if hasattr(self, 'timeout') else 30,
            "max_retries": getattr(self, 'max_retries', None).value() if hasattr(self, 'max_retries') else 3,
            "processors": advanced_tab.processors.text() if advanced_tab and hasattr(advanced_tab, 'processors') else "",
            "num_devices": advanced_tab.num_devices.value() if advanced_tab and hasattr(advanced_tab, 'num_devices') else 1,
            "debug_data_folder": advanced_tab.debug_data_folder.text() if advanced_tab and hasattr(advanced_tab, 'debug_data_folder') else "",
            "debug_layout_images": advanced_tab.debug_layout_images.isChecked() if advanced_tab and hasattr(advanced_tab, 'debug_layout_images') else False,
            "debug_pdf_images": advanced_tab.debug_pdf_images.isChecked() if advanced_tab and hasattr(advanced_tab, 'debug_pdf_images') else False,
            "debug_json": advanced_tab.debug_json.isChecked() if advanced_tab and hasattr(advanced_tab, 'debug_json') else False,
            "num_workers": advanced_tab.num_workers.value() if advanced_tab and hasattr(advanced_tab, 'num_workers') else 15,
        }
    
    def load_config(self):
        """加载配置文件"""
        # 获取当前配置名称
        current_config = self.preset_combo.currentText()
        config_name, ok = QInputDialog.getText(
            self, "加载配置", "输入配置名称:",
            QLineEdit.EchoMode.Normal, current_config
        )
        
        if not ok or not config_name:
            return
        
        # 加载配置
        config_data = self.config_manager.load_preset(config_name)
        if not config_data:
            print(f"[ERROR] 加载失败: 配置 '{config_name}' 不存在")
            return
        
        # 应用配置到UI
        self.apply_config(config_data)
        print(f"[INFO] 加载成功: 配置 '{config_name}' 已应用")
    
    def apply_config(self, config_data):
        """应用配置到UI"""
        # 基本设置
        self.input_path.setText(config_data.get("input_path", ""))
        self.output_dir.setText(config_data.get("output_dir", ""))
        self.output_format.setCurrentText(config_data.get("output_format", "markdown"))
        self.page_range.setText(config_data.get("page_range", ""))
        
        # 基本选项
        if hasattr(self, 'paginate_output'):
            self.paginate_output.setChecked(config_data.get("paginate_output", False))
        if hasattr(self, 'disable_image_extraction'):
            self.disable_image_extraction.setChecked(config_data.get("disable_image_extraction", False))
        if hasattr(self, 'disable_multiprocessing'):
            self.disable_multiprocessing.setChecked(config_data.get("disable_multiprocessing", False))
        if hasattr(self, 'debug_mode'):
            self.debug_mode.setChecked(config_data.get("debug_mode", False))
        if hasattr(self, 'pdftext_workers'):
            self.pdftext_workers.setValue(config_data.get("pdftext_workers", 4))
        
        # OCR选项
        if hasattr(self, 'format_lines'):
            self.format_lines.setChecked(config_data.get("format_lines", False))
        if hasattr(self, 'force_ocr'):
            self.force_ocr.setChecked(config_data.get("force_ocr", False))
        if hasattr(self, 'strip_existing_ocr'):
            self.strip_existing_ocr.setChecked(config_data.get("strip_existing_ocr", False))
        if hasattr(self, 'ocr_task_name'):
            self.set_combo_text(self.ocr_task_name, config_data.get("ocr_task_name", ""))
        if hasattr(self, 'disable_ocr_math'):
            self.disable_ocr_math.setChecked(config_data.get("disable_ocr_math", False))
        if hasattr(self, 'drop_repeated_text'):
            self.drop_repeated_text.setChecked(config_data.get("drop_repeated_text", False))
        
        # 转换器设置
        if hasattr(self, 'converter_cls'):
            self.set_combo_text(self.converter_cls, config_data.get("converter_cls", ""))
        if hasattr(self, 'force_layout_block'):
            self.force_layout_block.setText(config_data.get("force_layout_block", ""))
        
        # LLM设置
        if hasattr(self, 'use_llm'):
            self.use_llm.setChecked(config_data.get("use_llm", False))
        if hasattr(self, 'redo_inline_math'):
            self.redo_inline_math.setChecked(config_data.get("redo_inline_math", False))
        if hasattr(self, 'llm_service'):
            self.set_combo_text(self.llm_service, config_data.get("llm_service", ""))
        if hasattr(self, 'gemini_api_key'):
            self.gemini_api_key.setText(config_data.get("gemini_api_key", ""))
        if hasattr(self, 'gemini_model_name'):
            self.gemini_model_name.setText(config_data.get("gemini_model_name", ""))
        if hasattr(self, 'vertex_project_id'):
            self.vertex_project_id.setText(config_data.get("vertex_project_id", ""))
        if hasattr(self, 'vertex_location'):
            self.vertex_location.setText(config_data.get("vertex_location", ""))
        if hasattr(self, 'ollama_base_url'):
            self.ollama_base_url.setText(config_data.get("ollama_base_url", ""))
        if hasattr(self, 'ollama_model'):
            self.ollama_model.setText(config_data.get("ollama_model", ""))
        if hasattr(self, 'claude_api_key'):
            self.claude_api_key.setText(config_data.get("claude_api_key", ""))
        if hasattr(self, 'claude_model_name'):
            self.claude_model_name.setText(config_data.get("claude_model_name", ""))
        if hasattr(self, 'openai_api_key'):
            self.openai_api_key.setText(config_data.get("openai_api_key", ""))
        if hasattr(self, 'openai_model'):
            self.openai_model.setText(config_data.get("openai_model", ""))
        if hasattr(self, 'openai_base_url'):
            self.openai_base_url.setText(config_data.get("openai_base_url", ""))
        if hasattr(self, 'max_concurrency'):
            self.max_concurrency.setValue(config_data.get("max_concurrency", 1))
        if hasattr(self, 'timeout'):
            self.timeout.setValue(config_data.get("timeout", 30))
        if hasattr(self, 'max_retries'):
            self.max_retries.setValue(config_data.get("max_retries", 3))
        
        # 高级设置
        advanced_tab = None
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == "高级设置":
                advanced_tab = self.tabs.widget(i)
                break
        
        if advanced_tab:
            if hasattr(advanced_tab, 'processors'):
                advanced_tab.processors.setText(config_data.get("processors", ""))
            if hasattr(advanced_tab, 'num_devices'):
                advanced_tab.num_devices.setValue(config_data.get("num_devices", 1))
            if hasattr(advanced_tab, 'debug_data_folder'):
                advanced_tab.debug_data_folder.setText(config_data.get("debug_data_folder", ""))
            if hasattr(advanced_tab, 'debug_layout_images'):
                advanced_tab.debug_layout_images.setChecked(config_data.get("debug_layout_images", False))
            if hasattr(advanced_tab, 'debug_pdf_images'):
                advanced_tab.debug_pdf_images.setChecked(config_data.get("debug_pdf_images", False))
            if hasattr(advanced_tab, 'debug_json'):
                advanced_tab.debug_json.setChecked(config_data.get("debug_json", False))
            if hasattr(advanced_tab, 'num_workers'):
                advanced_tab.num_workers.setValue(config_data.get("num_workers", 15))
        
        print("[INFO] 配置已成功应用到UI")
    
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

    def refresh_config_list(self):
        """刷新配置列表"""
        if hasattr(self, 'preset_combo'):
            self.preset_combo.clear()
            presets = self.config_manager.get_available_presets()
            for preset in presets:
                self.preset_combo.addItem(preset)
    
    def set_combo_text(self, combo, text):
        index = combo.findText(text)
        if index >= 0:
            combo.setCurrentIndex(index)
        else:
            combo.addItem(text)
            combo.setCurrentIndex(combo.count() - 1)

    def reset_config(self):
        """重置配置为默认值"""
        self.config_manager.reset_to_default()
        self.apply_config(self.config_manager.default_config)
        self.refresh_config_list()  # 刷新预设列表
        print("[INFO] 配置已重置为默认值")
