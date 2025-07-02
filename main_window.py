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
from tabs.advanced_tab import AdvancedTab  # 更新导入

class MarkerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Marker Document Converter")
        # 设置初始最小宽度，允许根据内容自动调整
        self.setMinimumWidth(400)
        self.setMinimumHeight(400)
        
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
        self.tabs.addTab(AdvancedTab(self), "高级设置")
        
        # 命令输出区域
        output_group = QGroupBox("生成的命令")
        output_layout = QVBoxLayout()
        self.command_output = QTextEdit()
        self.command_output.setReadOnly(True)
        self.command_output.setFont(QFont("Courier New", 10))
        self.command_output.setLineWrapMode(QTextEdit.WidgetWidth)  # 设置自动换行，避免水平滚动条
        output_layout.addWidget(self.command_output)
        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)
        
        # 底部按钮（保留必要功能）
        button_layout = QHBoxLayout()
        self.generate_btn = QPushButton("生成命令")
        self.generate_btn.clicked.connect(self.generate_command)
        self.copy_btn = QPushButton("复制命令")
        self.copy_btn.clicked.connect(self.copy_command)
        
        button_layout.addWidget(self.generate_btn)
        button_layout.addWidget(self.copy_btn)
        self.run_btn = QPushButton("运行命令")
        self.run_btn.clicked.connect(self.run_command)
        button_layout.addWidget(self.run_btn)
        
        main_layout.addLayout(button_layout)
        # 初始化UI状态
        # 初始化配置为默认值
        self.config_manager.reset_to_default()
        self.toggle_llm_options(False)
        
        # 添加自适应宽度逻辑
        self.adjustSize()

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

    # 移除不再使用的配置管理方法


    def generate_command(self):
        try:
            command = ""
            input_path = self.input_path.text().strip()
            
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
            
            # 高级选项 - 从AdvancedTab获取
            advanced_tab = self.tabs.widget(3)  # 第4个标签页是AdvancedTab
            if hasattr(advanced_tab, 'processors') and advanced_tab.processors:
                processors = advanced_tab.processors.text().strip()
                if processors:
                    command += f' --processors "{processors}"'
            
            # 调试选项
            if hasattr(advanced_tab, 'debug_data_folder') and advanced_tab.debug_data_folder:
                debug_folder = advanced_tab.debug_data_folder.text().strip()
                if debug_folder:
                    command += f' --debug_data_folder "{debug_folder}"'
            if hasattr(advanced_tab, 'debug_layout_images') and advanced_tab.debug_layout_images:
                if advanced_tab.debug_layout_images.isChecked():
                    command += " --debug_layout_images"
            if hasattr(advanced_tab, 'debug_pdf_images') and advanced_tab.debug_pdf_images:
                if advanced_tab.debug_pdf_images.isChecked():
                    command += " --debug_pdf_images"
            if hasattr(advanced_tab, 'debug_json') and advanced_tab.debug_json:
                if advanced_tab.debug_json.isChecked():
                    command += " --debug_json"
            
            # 多GPU设置
            if hasattr(advanced_tab, 'num_devices') and advanced_tab.num_devices:
                num_devices = advanced_tab.num_devices.value()
                if num_devices > 1:
                    num_workers = advanced_tab.num_workers.value() if hasattr(advanced_tab, 'num_workers') else 1
                    command = f'NUM_DEVICES={num_devices} NUM_WORKERS={num_workers} marker_chunk_convert "{input_path}" "{output_dir if output_dir else "output_dir"}"'
            
            self.command_output.setText(command)
        except Exception as e:
            QMessageBox.critical(self, "生成命令错误", f"发生错误: {str(e)}")
            command += "marker "
    def copy_command(self):
        command = self.command_output.toPlainText()
        if command:
            QApplication.clipboard().setText(command)
            QMessageBox.information(self, "复制成功", "命令已复制到剪贴板")
        else:
            QMessageBox.warning(self, "复制错误", "没有可复制的命令")
            
    def run_command(self):
        """运行生成的命令"""
        command = self.command_output.toPlainText().strip()
        if not command:
            QMessageBox.warning(self, "错误", "没有可运行的命令")
            return
        
        try:
            # 将命令发送到VSCode终端
            print(f"\n[MarkerGUI] 运行命令:\n{command}\n")
            print("[MarkerGUI] 命令已发送到终端，请查看终端输出")
        except Exception as e:
            QMessageBox.critical(self, "运行错误", f"执行命令时出错: {str(e)}")

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
            "debug_data_folder": advanced_tab.debug_data_folder.text() if hasattr(advanced_tab, 'debug_data_folder') else "",
            "debug_layout_images": advanced_tab.debug_layout_images.isChecked() if hasattr(advanced_tab, 'debug_layout_images') else False,
            "debug_pdf_images": advanced_tab.debug_pdf_images.isChecked() if hasattr(advanced_tab, 'debug_pdf_images') else False,
            "debug_json": advanced_tab.debug_json.isChecked() if hasattr(advanced_tab, 'debug_json') else False
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
            QMessageBox.information(self, "保存成功", "配置已成功保存")
            self.refresh_config_list()
            self.preset_combo.setCurrentText(config_name)



    def set_combo_text(self, combo, text):
        index = combo.findText(text)
        if index >= 0:
            combo.setCurrentIndex(index)
        else:
            combo.addItem(text)
            combo.setCurrentIndex(combo.count() - 1)