import os
import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QGroupBox, QLabel, QLineEdit, QPushButton, QCheckBox, QComboBox,
    QTextEdit, QFileDialog, QMessageBox, QSpinBox, QFormLayout, QInputDialog, QApplication
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from config_manager import ConfigManager
from tabs.basic_tab import create_basic_tab
from tabs.ocr_tab import create_ocr_tab
from tabs.llm_tab import create_llm_tab
from tabs.advanced_tab import create_advanced_tab

class MarkerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Marker Document Converter")
        self.setGeometry(100, 100, 500, 400)
        
        # 初始化配置管理器
        self.config_manager = ConfigManager()
        
        # 创建主布局
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # 创建标签页
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # 添加标签页
        self.tabs.addTab(create_basic_tab(self), "基本设置")
        self.tabs.addTab(create_ocr_tab(self), "OCR设置")
        self.tabs.addTab(create_llm_tab(self), "LLM设置")
        self.tabs.addTab(create_advanced_tab(self), "高级设置")
        
        # 命令输出区域
        output_group = QGroupBox("生成的命令")
        output_layout = QVBoxLayout()
        self.command_output = QTextEdit()
        self.command_output.setReadOnly(True)
        self.command_output.setFont(QFont("Courier New", 10))
        output_layout.addWidget(self.command_output)
        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        self.generate_btn = QPushButton("生成命令")
        self.generate_btn.clicked.connect(self.generate_command)
        self.copy_btn = QPushButton("复制命令")
        self.copy_btn.clicked.connect(self.copy_command)
        self.save_btn = QPushButton("保存配置")
        self.save_btn.clicked.connect(self.save_config)
        self.load_btn = QPushButton("加载配置")
        self.load_btn.clicked.connect(self.load_config)
        self.reset_btn = QPushButton("重置配置")
        self.reset_btn.clicked.connect(self.reset_config)
        
        button_layout.addWidget(self.generate_btn)
        button_layout.addWidget(self.copy_btn)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.load_btn)
        button_layout.addWidget(self.reset_btn)
        main_layout.addLayout(button_layout)
        
        # 初始化UI状态
        self.reset_config()
        self.toggle_llm_options(False)

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

    def refresh_config_list(self):
        """刷新配置列表"""
        self.preset_combo.clear()
        all_configs = self.config_manager.get_all_configs()
        for config_name in all_configs.keys():
            self.preset_combo.addItem(config_name)

    def apply_preset(self):
        config_name = self.preset_combo.currentText()
        if not config_name:
            return
        
        config_data = self.config_manager.load_config(config_name)
        if config_data is None:
            return
        
        # 应用配置
        self.input_path.setText(config_data.get("input_path", ""))
        self.output_dir.setText(config_data.get("output_dir", ""))
        
        # 设置下拉框选项
        self.set_combo_text(self.output_format, config_data.get("output_format", "markdown"))
        self.set_combo_text(self.converter_cls, config_data.get("converter_cls", "marker.converters.pdf.PdfConverter (默认)"))
        self.set_combo_text(self.llm_service, config_data.get("llm_service", "Google Gemini (默认)"))
        self.set_combo_text(self.ocr_task_name, config_data.get("ocr_task_name", "ocr_with_boxes"))
        
        # 设置复选框
        self.paginate_output.setChecked(config_data.get("paginate_output", False))
        self.disable_image_extraction.setChecked(config_data.get("disable_image_extraction", False))
        self.disable_multiprocessing.setChecked(config_data.get("disable_multiprocessing", False))
        self.debug_mode.setChecked(config_data.get("debug_mode", False))
        self.format_lines.setChecked(config_data.get("format_lines", False))
        self.force_ocr.setChecked(config_data.get("force_ocr", False))
        self.strip_existing_ocr.setChecked(config_data.get("strip_existing_ocr", False))
        self.disable_ocr_math.setChecked(config_data.get("disable_ocr_math", False))
        self.drop_repeated_text.setChecked(config_data.get("drop_repeated_text", False))
        self.use_llm.setChecked(config_data.get("use_llm", False))
        self.redo_inline_math.setChecked(config_data.get("redo_inline_math", False))
        self.debug_layout_images.setChecked(config_data.get("debug_layout_images", False))
        self.debug_pdf_images.setChecked(config_data.get("debug_pdf_images", False))
        self.debug_json.setChecked(config_data.get("debug_json", False))
        
        # 设置数值字段
        self.pdftext_workers.setValue(config_data.get("pdftext_workers", 4))
        self.max_concurrency.setValue(config_data.get("max_concurrency", 3))
        self.timeout.setValue(config_data.get("timeout", 30))
        self.max_retries.setValue(config_data.get("max_retries", 2))
        self.num_devices.setValue(config_data.get("num_devices", 1))
        self.num_workers.setValue(config_data.get("num_workers", 15))
        
        # 设置文本字段
        self.page_range.setText(config_data.get("page_range", ""))
        self.force_layout_block.setText(config_data.get("force_layout_block", ""))
        self.gemini_api_key.setText(config_data.get("gemini_api_key", ""))
        self.gemini_model_name.setText(config_data.get("gemini_model_name", "gemini-2.0-flash"))
        self.vertex_project_id.setText(config_data.get("vertex_project_id", ""))
        self.vertex_location.setText(config_data.get("vertex_location", "us-central1"))
        self.ollama_base_url.setText(config_data.get("ollama_base_url", "http://localhost:11434"))
        self.ollama_model.setText(config_data.get("ollama_model", "llama3.2-vision"))
        self.claude_api_key.setText(config_data.get("claude_api_key", ""))
        self.claude_model_name.setText(config_data.get("claude_model_name", "claude-3-7-sonnet-20250219"))
        self.openai_api_key.setText(config_data.get("openai_api_key", ""))
        self.openai_model.setText(config_data.get("openai_model", "gpt-4o-mini"))
        self.openai_base_url.setText(config_data.get("openai_base_url", "https://api.openai.com/v1"))
        self.processors.setText(config_data.get("processors", ""))
        self.debug_data_folder.setText(config_data.get("debug_data_folder", ""))
        
        self.generate_command()

    def generate_command(self):
        command = ""
        
        # 输入路径
        input_path = self.input_path.text().strip()
        if not input_path:
            self.command_output.setText("错误: 请选择输入文件或目录")
            return
        
        # 确定是单文件还是批量处理
        if Path(input_path).is_dir():
            command += "marker "
        else:
            command += "marker_single "
        
        command += f'"{input_path}"'
        
        # 输出目录
        output_dir = self.output_dir.text().strip()
        if output_dir:
            command += f' --output_dir "{output_dir}"'
        
        # 输出格式
        output_format = self.output_format.currentText()
        if output_format != "markdown":
            command += f' --output_format {output_format}'
        
        # 页面范围
        page_range = self.page_range.text().strip()
        if page_range:
            command += f' --page_range "{page_range}"'
        
        # 基本选项
        if self.paginate_output.isChecked():
            command += " --paginate_output"
        if self.disable_image_extraction.isChecked():
            command += " --disable_image_extraction"
        if self.debug_mode.isChecked():
            command += " --debug"
        if self.disable_multiprocessing.isChecked():
            command += " --disable_multiprocessing"
        
        # PDF文本提取工作进程数
        pdftext_workers = self.pdftext_workers.value()
        if pdftext_workers != 4:
            command += f' --pdftext_workers {pdftext_workers}'
        
        # OCR选项
        if self.format_lines.isChecked():
            command += " --format_lines"
        if self.force_ocr.isChecked():
            command += " --force_ocr"
        if self.strip_existing_ocr.isChecked():
            command += " --strip_existing_ocr"
        
        # OCR任务模式
        ocr_task = self.ocr_task_name.currentText()
        if ocr_task != "ocr_with_boxes":
            command += f' --ocr_task_name {ocr_task}'
        if self.disable_ocr_math.isChecked():
            command += " --disable_ocr_math"
        if self.drop_repeated_text.isChecked():
            command += " --drop_repeated_text"
        
        # 转换器设置
        converter_cls = self.converter_cls.currentText()
        if "TableConverter" in converter_cls:
            command += ' --converter_cls marker.converters.table.TableConverter'
        elif "OCRConverter" in converter_cls:
            command += ' --converter_cls marker.converters.ocr.OCRConverter'
        elif "ExtractionConverter" in converter_cls:
            command += ' --converter_cls marker.converters.extraction.ExtractionConverter'
        
        force_layout = self.force_layout_block.text().strip()
        if force_layout:
            command += f' --force_layout_block {force_layout}'
        
        # LLM选项
        if self.use_llm.isChecked():
            command += " --use_llm"
            
            if self.redo_inline_math.isChecked():
                command += " --redo_inline_math"
            
            # LLM服务配置
            service = self.llm_service.currentText()
            if "Vertex" in service:
                command += ' --llm_service marker.services.vertex.GoogleVertexService'
                if self.vertex_project_id.text().strip():
                    command += f' --vertex_project_id "{self.vertex_project_id.text().strip()}"'
                if self.vertex_location.text().strip():
                    command += f' --vertex_location "{self.vertex_location.text().strip()}"'
            elif "Ollama" in service:
                command += ' --llm_service marker.services.ollama.OllamaService'
                if self.ollama_base_url.text().strip():
                    command += f' --ollama_base_url "{self.ollama_base_url.text().strip()}"'
                if self.ollama_model.text().strip():
                    command += f' --ollama_model "{self.ollama_model.text().strip()}"'
            elif "Claude" in service:
                command += ' --llm_service marker.services.claude.ClaudeService'
                if self.claude_api_key.text().strip():
                    command += f' --claude_api_key "{self.claude_api_key.text().strip()}"'
                if self.claude_model_name.text().strip():
                    command += f' --claude_model_name "{self.claude_model_name.text().strip()}"'
            elif "OpenAI" in service:
                command += ' --llm_service marker.services.openai.OpenAIService'
                if self.openai_api_key.text().strip():
                    command += f' --openai_api_key "{self.openai_api_key.text().strip()}"'
                if self.openai_model.text().strip():
                    command += f' --openai_model "{self.openai_model.text().strip()}"'
                if self.openai_base_url.text().strip():
                    command += f' --openai_base_url "{self.openai_base_url.text().strip()}"'
            else:  # Gemini
                if self.gemini_api_key.text().strip():
                    command += f' --gemini_api_key "{self.gemini_api_key.text().strip()}"'
                if self.gemini_model_name.text().strip() != "gemini-2.0-flash":
                    command += f' --gemini_model_name "{self.gemini_model_name.text().strip()}"'
            
            # LLM高级选项
            if self.max_concurrency.value() != 3:
                command += f' --max_concurrency {self.max_concurrency.value()}'
            if self.timeout.value() != 30:
                command += f' --timeout {self.timeout.value()}'
            if self.max_retries.value() != 2:
                command += f' --max_retries {self.max_retries.value()}'
        
        # 高级选项
        processors = self.processors.text().strip()
        if processors:
            command += f' --processors "{processors}"'
        
        # 调试选项
        if self.debug_data_folder.text().strip():
            command += f' --debug_data_folder "{self.debug_data_folder.text().strip()}"'
        if self.debug_layout_images.isChecked():
            command += " --debug_layout_images"
        if self.debug_pdf_images.isChecked():
            command += " --debug_pdf_images"
        if self.debug_json.isChecked():
            command += " --debug_json"
        
        # 多GPU设置
        if self.num_devices.value() > 1:
            command = f'NUM_DEVICES={self.num_devices.value()} NUM_WORKERS={self.num_workers.value()} marker_chunk_convert "{input_path}" "{output_dir if output_dir else "output_dir"}"'
        
        self.command_output.setText(command)

    def copy_command(self):
        command = self.command_output.toPlainText()
        if command:
            QApplication.clipboard().setText(command)
            QMessageBox.information(self, "复制成功", "命令已复制到剪贴板")

    def get_current_config(self):
        """获取当前UI配置数据"""
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
            "processors": self.processors.text(),
            "num_devices": self.num_devices.value(),
            "num_workers": self.num_workers.value(),
            "debug_data_folder": self.debug_data_folder.text(),
            "debug_layout_images": self.debug_layout_images.isChecked(),
            "debug_pdf_images": self.debug_pdf_images.isChecked(),
            "debug_json": self.debug_json.isChecked()
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
        if self.config_manager.save_config(config_name, config_data):
            QMessageBox.information(self, "保存成功", "配置已成功保存")
            self.refresh_config_list()
            self.preset_combo.setCurrentText(config_name)

    def load_config(self):
        # 获取要加载的配置名称
        config_name = self.preset_combo.currentText()
        if not config_name:
            return
        
        # 加载配置
        self.apply_preset()

    def reset_config(self):
        # 重置所有控件到默认状态
        self.input_path.clear()
        self.output_dir.clear()
        self.output_format.setCurrentIndex(0)
        self.page_range.clear()
        self.paginate_output.setChecked(False)
        self.disable_image_extraction.setChecked(False)
        self.disable_multiprocessing.setChecked(False)
        self.debug_mode.setChecked(False)
        self.pdftext_workers.setValue(4)
        self.format_lines.setChecked(False)
        self.force_ocr.setChecked(False)
        self.strip_existing_ocr.setChecked(False)
        self.ocr_task_name.setCurrentIndex(0)
        self.disable_ocr_math.setChecked(False)
        self.drop_repeated_text.setChecked(False)
        self.converter_cls.setCurrentIndex(0)
        self.force_layout_block.clear()
        self.use_llm.setChecked(False)
        self.redo_inline_math.setChecked(False)
        self.llm_service.setCurrentIndex(0)
        self.gemini_api_key.clear()
        self.gemini_model_name.setText("gemini-2.0-flash")
        self.vertex_project_id.clear()
        self.vertex_location.setText("us-central1")
        self.ollama_base_url.setText("http://localhost:11434")
        self.ollama_model.setText("llama3.2-vision")
        self.claude_api_key.clear()
        self.claude_model_name.setText("claude-3-7-sonnet-20250219")
        self.openai_api_key.clear()
        self.openai_model.setText("gpt-4o-mini")
        self.openai_base_url.setText("https://api.openai.com/v1")
        self.max_concurrency.setValue(3)
        self.timeout.setValue(30)
        self.max_retries.setValue(2)
        self.processors.clear()
        self.preset_combo.setCurrentIndex(0)
        self.num_devices.setValue(1)
        self.num_workers.setValue(15)
        self.debug_data_folder.clear()
        self.debug_layout_images.setChecked(False)
        self.debug_pdf_images.setChecked(False)
        self.debug_json.setChecked(False)
        self.command_output.clear()
        
        self.toggle_llm_options(False)
        self.refresh_config_list()

    def set_combo_text(self, combo, text):
        index = combo.findText(text)
        if index >= 0:
            combo.setCurrentIndex(index)
        else:
            combo.addItem(text)
            combo.setCurrentIndex(combo.count() - 1)