import sys
import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QGroupBox, QLabel, QLineEdit, QPushButton, QCheckBox, QComboBox,
    QTextEdit, QScrollArea, QFileDialog, QMessageBox, QSpinBox, QFormLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon


class MarkerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Marker Document Converter")
        self.setGeometry(100, 100, 600, 400)
        
        # 预设配置 - 在创建标签页之前初始化
        self.presets = {
            "默认配置": {},
            "高质量转换": {
                "use_llm": True,
                "format_lines": True,
                "redo_inline_math": True
            },
            "表格提取": {
                "converter_cls": "marker.converters.table.TableConverter",
                "output_format": "json",
                "force_layout_block": "Table"
            },
            "纯OCR处理": {
                "converter_cls": "marker.converters.ocr.OCRConverter",
                "force_ocr": True
            }
        }
        
        # 创建主布局
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # 创建标签页
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # 添加标签页
        self.tabs.addTab(self.create_basic_tab(), "基本设置")
        self.tabs.addTab(self.create_ocr_tab(), "OCR设置")
        self.tabs.addTab(self.create_llm_tab(), "LLM设置")
        self.tabs.addTab(self.create_advanced_tab(), "高级设置")
        
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

    def create_basic_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # 文件选择
        file_group = QGroupBox("文件设置")
        file_layout = QFormLayout()
        self.input_path = QLineEdit()
        self.input_path.setPlaceholderText("选择输入文件或目录")
        self.input_browse = QPushButton("浏览...")
        self.input_browse.clicked.connect(self.browse_input)
        
        self.output_dir = QLineEdit()
        self.output_dir.setPlaceholderText("选择输出目录")
        self.output_browse = QPushButton("浏览...")
        self.output_browse.clicked.connect(self.browse_output)
        
        file_layout.addRow("输入文件/目录:", self.create_h_widget([self.input_path, self.input_browse]))
        file_layout.addRow("输出目录:", self.create_h_widget([self.output_dir, self.output_browse]))
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # 输出设置
        output_group = QGroupBox("输出设置")
        output_layout = QFormLayout()
        
        self.output_format = QComboBox()
        self.output_format.addItems(["markdown", "json", "html"])
        self.paginate_output = QCheckBox("添加分页标记")
        self.disable_image_extraction = QCheckBox("禁用图像提取")
        
        output_layout.addRow("输出格式:", self.output_format)
        output_layout.addRow("", self.paginate_output)
        output_layout.addRow("", self.disable_image_extraction)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # 页面范围
        page_group = QGroupBox("页面范围")
        page_layout = QFormLayout()
        self.page_range = QLineEdit()
        self.page_range.setPlaceholderText("例如: 1,3-5,8")
        page_layout.addRow("指定页面:", self.page_range)
        page_group.setLayout(page_layout)
        layout.addWidget(page_group)
        
        # 处理设置
        process_group = QGroupBox("处理设置")
        process_layout = QFormLayout()
        self.pdftext_workers = QSpinBox()
        self.pdftext_workers.setRange(1, 32)
        self.pdftext_workers.setValue(4)
        self.disable_multiprocessing = QCheckBox("禁用多进程处理")
        self.debug_mode = QCheckBox("启用调试模式")
        
        process_layout.addRow("PDF文本提取工作进程数:", self.pdftext_workers)
        process_layout.addRow("", self.disable_multiprocessing)
        process_layout.addRow("", self.debug_mode)
        process_group.setLayout(process_layout)
        layout.addWidget(process_group)
        
        layout.addStretch()
        return tab

    def create_ocr_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # OCR选项组
        ocr_group = QGroupBox("OCR处理选项")
        ocr_layout = QFormLayout()
        
        self.format_lines = QCheckBox("格式化所有文本行")
        self.format_lines.setToolTip("使用本地OCR模型重新格式化所有文本行（处理内联数学、下划线、粗体等）")
        self.force_ocr = QCheckBox("强制全文OCR")
        self.force_ocr.setToolTip("即使页面包含可提取文本，也进行OCR处理")
        self.strip_existing_ocr = QCheckBox("去除现有OCR文本")
        self.strip_existing_ocr.setToolTip("移除文档中所有现有OCR文本并使用surya重新OCR")
        
        ocr_layout.addRow(self.format_lines)
        ocr_layout.addRow(self.force_ocr)
        ocr_layout.addRow(self.strip_existing_ocr)
        ocr_group.setLayout(ocr_layout)
        layout.addWidget(ocr_group)
        
        # 转换器设置
        converter_group = QGroupBox("转换器设置")
        converter_layout = QFormLayout()
        
        self.converter_cls = QComboBox()
        self.converter_cls.addItems([
            "marker.converters.pdf.PdfConverter (默认)",
            "marker.converters.table.TableConverter",
            "marker.converters.ocr.OCRConverter",
            "marker.converters.extraction.ExtractionConverter"
        ])
        self.force_layout_block = QLineEdit()
        self.force_layout_block.setPlaceholderText("例如: Table")
        
        converter_layout.addRow("转换器类:", self.converter_cls)
        converter_layout.addRow("强制布局块:", self.force_layout_block)
        converter_group.setLayout(converter_layout)
        layout.addWidget(converter_group)
        
        # OCR高级设置
        ocr_adv_group = QGroupBox("OCR高级设置")
        ocr_adv_layout = QFormLayout()
        
        self.ocr_task_name = QComboBox()
        self.ocr_task_name.addItems(["ocr_with_boxes", "ocr_without_boxes"])
        self.ocr_task_name.setCurrentIndex(0)
        self.disable_ocr_math = QCheckBox("禁用OCR数学公式识别")
        self.drop_repeated_text = QCheckBox("删除重复文本")
        
        ocr_adv_layout.addRow("OCR任务模式:", self.ocr_task_name)
        ocr_adv_layout.addRow("", self.disable_ocr_math)
        ocr_adv_layout.addRow("", self.drop_repeated_text)
        ocr_adv_group.setLayout(ocr_adv_layout)
        layout.addWidget(ocr_adv_group)
        
        layout.addStretch()
        return tab

    def create_llm_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # LLM启用
        llm_group = QGroupBox("LLM增强")
        llm_layout = QFormLayout()
        
        self.use_llm = QCheckBox("使用LLM提高准确性")
        self.use_llm.stateChanged.connect(lambda: self.toggle_llm_options(self.use_llm.isChecked()))
        self.redo_inline_math = QCheckBox("高质量内联数学公式")
        self.redo_inline_math.setToolTip("使用LLM获得最高质量的内联数学公式转换")
        
        llm_layout.addRow(self.use_llm)
        llm_layout.addRow(self.redo_inline_math)
        llm_group.setLayout(llm_layout)
        layout.addWidget(llm_group)
        
        # LLM服务
        service_group = QGroupBox("LLM服务配置")
        service_layout = QFormLayout()
        
        self.llm_service = QComboBox()
        self.llm_service.addItems([
            "Google Gemini (默认)",
            "Google Vertex",
            "Ollama (本地模型)",
            "Claude",
            "OpenAI"
        ])
        
        # Gemini 配置
        self.gemini_api_key = QLineEdit()
        self.gemini_api_key.setPlaceholderText("输入Gemini API密钥")
        self.gemini_model_name = QLineEdit()
        self.gemini_model_name.setPlaceholderText("例如: gemini-2.0-flash")
        self.gemini_model_name.setText("gemini-2.0-flash")
        
        # Vertex 配置
        self.vertex_project_id = QLineEdit()
        self.vertex_project_id.setPlaceholderText("输入Vertex项目ID")
        self.vertex_location = QLineEdit()
        self.vertex_location.setPlaceholderText("例如: us-central1")
        self.vertex_location.setText("us-central1")
        
        # Ollama 配置
        self.ollama_base_url = QLineEdit()
        self.ollama_base_url.setPlaceholderText("例如: http://localhost:11434")
        self.ollama_base_url.setText("http://localhost:11434")
        self.ollama_model = QLineEdit()
        self.ollama_model.setPlaceholderText("例如: llama3")
        self.ollama_model.setText("llama3.2-vision")
        
        # Claude 配置
        self.claude_api_key = QLineEdit()
        self.claude_api_key.setPlaceholderText("输入Claude API密钥")
        self.claude_model_name = QLineEdit()
        self.claude_model_name.setPlaceholderText("例如: claude-3-sonnet")
        self.claude_model_name.setText("claude-3-7-sonnet-20250219")
        
        # OpenAI 配置
        self.openai_api_key = QLineEdit()
        self.openai_api_key.setPlaceholderText("输入OpenAI API密钥")
        self.openai_model = QLineEdit()
        self.openai_model.setPlaceholderText("例如: gpt-4o")
        self.openai_model.setText("gpt-4o-mini")
        self.openai_base_url = QLineEdit()
        self.openai_base_url.setPlaceholderText("例如: https://api.openai.com/v1")
        self.openai_base_url.setText("https://api.openai.com/v1")
        
        service_layout.addRow("LLM服务:", self.llm_service)
        service_layout.addRow("Gemini API密钥:", self.gemini_api_key)
        service_layout.addRow("Gemini模型名称:", self.gemini_model_name)
        service_layout.addRow("Vertex项目ID:", self.vertex_project_id)
        service_layout.addRow("Vertex位置:", self.vertex_location)
        service_layout.addRow("Ollama基础URL:", self.ollama_base_url)
        service_layout.addRow("Ollama模型:", self.ollama_model)
        service_layout.addRow("Claude API密钥:", self.claude_api_key)
        service_layout.addRow("Claude模型名称:", self.claude_model_name)
        service_layout.addRow("OpenAI API密钥:", self.openai_api_key)
        service_layout.addRow("OpenAI模型:", self.openai_model)
        service_layout.addRow("OpenAI基础URL:", self.openai_base_url)
        
        service_group.setLayout(service_layout)
        layout.addWidget(service_group)
        
        # LLM高级设置
        llm_adv_group = QGroupBox("LLM高级设置")
        llm_adv_layout = QFormLayout()
        
        self.max_concurrency = QSpinBox()
        self.max_concurrency.setRange(1, 32)
        self.max_concurrency.setValue(3)
        self.timeout = QSpinBox()
        self.timeout.setRange(10, 300)
        self.timeout.setValue(30)
        self.max_retries = QSpinBox()
        self.max_retries.setRange(1, 10)
        self.max_retries.setValue(2)
        
        llm_adv_layout.addRow("最大并发请求数:", self.max_concurrency)
        llm_adv_layout.addRow("请求超时(秒):", self.timeout)
        llm_adv_layout.addRow("最大重试次数:", self.max_retries)
        llm_adv_group.setLayout(llm_adv_layout)
        layout.addWidget(llm_adv_group)
        
        layout.addStretch()
        return tab

    def create_advanced_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # 处理器设置
        processor_group = QGroupBox("处理器覆盖")
        processor_layout = QFormLayout()
        
        self.processors = QLineEdit()
        self.processors.setPlaceholderText("例如: module1.processor1,module2.processor2")
        
        processor_layout.addRow("自定义处理器:", self.processors)
        processor_group.setLayout(processor_layout)
        layout.addWidget(processor_group)
        
        # 配置导入/导出
        config_group = QGroupBox("配置管理")
        config_layout = QFormLayout()
        
        self.config_json = QLineEdit()
        self.config_json.setPlaceholderText("选择JSON配置文件")
        self.config_browse = QPushButton("浏览...")
        self.config_browse.clicked.connect(self.browse_config)
        
        # 预设选择
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(list(self.presets.keys()))
        self.preset_combo.currentIndexChanged.connect(self.apply_preset)
        
        config_layout.addRow("配置文件:", self.create_h_widget([self.config_json, self.config_browse]))
        config_layout.addRow("预设配置:", self.preset_combo)
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # 多GPU设置
        gpu_group = QGroupBox("多GPU设置")
        gpu_layout = QFormLayout()
        
        self.num_devices = QSpinBox()
        self.num_devices.setRange(1, 8)
        self.num_devices.setValue(1)
        self.num_workers = QSpinBox()
        self.num_workers.setRange(1, 32)
        self.num_workers.setValue(15)
        
        gpu_layout.addRow("GPU数量:", self.num_devices)
        gpu_layout.addRow("每GPU工作进程:", self.num_workers)
        gpu_group.setLayout(gpu_layout)
        layout.addWidget(gpu_group)
        
        # 调试设置
        debug_group = QGroupBox("调试设置")
        debug_layout = QFormLayout()
        
        self.debug_data_folder = QLineEdit()
        self.debug_data_folder.setPlaceholderText("例如: debug_data")
        self.debug_layout_images = QCheckBox("保存布局调试图像")
        self.debug_pdf_images = QCheckBox("保存PDF调试图像")
        self.debug_json = QCheckBox("保存JSON调试数据")
        
        debug_layout.addRow("调试数据目录:", self.debug_data_folder)
        debug_layout.addRow("", self.debug_layout_images)
        debug_layout.addRow("", self.debug_pdf_images)
        debug_layout.addRow("", self.debug_json)
        debug_group.setLayout(debug_layout)
        layout.addWidget(debug_group)
        
        layout.addStretch()
        return tab

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

    def browse_input(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择输入文件", "", "所有文件 (*.*)")
        if path:
            self.input_path.setText(path)

    def browse_output(self):
        path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if path:
            self.output_dir.setText(path)

    def browse_config(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择配置文件", "", "JSON文件 (*.json)")
        if path:
            self.config_json.setText(path)

    def apply_preset(self):
        preset_name = self.preset_combo.currentText()
        if preset_name in self.presets:
            preset = self.presets[preset_name]
            # 应用预设配置
            self.use_llm.setChecked(preset.get("use_llm", False))
            self.format_lines.setChecked(preset.get("format_lines", False))
            self.redo_inline_math.setChecked(preset.get("redo_inline_math", False))
            
            # 转换器类预设
            converter_cls = preset.get("converter_cls", "marker.converters.pdf.PdfConverter (默认)")
            index = self.converter_cls.findText(converter_cls)
            if index >= 0:
                self.converter_cls.setCurrentIndex(index)
            
            # 输出格式预设
            output_format = preset.get("output_format", "markdown")
            index = self.output_format.findText(output_format)
            if index >= 0:
                self.output_format.setCurrentIndex(index)
            
            # 强制布局块预设
            self.force_layout_block.setText(preset.get("force_layout_block", ""))
            
            # 强制OCR预设
            self.force_ocr.setChecked(preset.get("force_ocr", False))
            
            # 生成命令
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
        
        config_json = self.config_json.text().strip()
        if config_json:
            command += f' --config_json "{config_json}"'
        
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

    def save_config(self):
        # 收集配置数据
        config = {
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
        
        # 保存到文件
        path, _ = QFileDialog.getSaveFileName(self, "保存配置", "", "JSON文件 (*.json)")
        if path:
            try:
                with open(path, 'w') as f:
                    json.dump(config, f, indent=4)
                QMessageBox.information(self, "保存成功", "配置已成功保存")
            except Exception as e:
                QMessageBox.critical(self, "保存失败", f"保存配置时出错: {str(e)}")

    def load_config(self):
        path, _ = QFileDialog.getOpenFileName(self, "加载配置", "", "JSON文件 (*.json)")
        if path:
            try:
                with open(path, 'r') as f:
                    config = json.load(f)
                
                # 应用配置
                self.input_path.setText(config.get("input_path", ""))
                self.output_dir.setText(config.get("output_dir", ""))
                
                # 设置下拉框选项
                self.set_combo_text(self.output_format, config.get("output_format", "markdown"))
                self.set_combo_text(self.converter_cls, config.get("converter_cls", "marker.converters.pdf.PdfConverter (默认)"))
                self.set_combo_text(self.llm_service, config.get("llm_service", "Google Gemini (默认)"))
                self.set_combo_text(self.ocr_task_name, config.get("ocr_task_name", "ocr_with_boxes"))
                
                # 设置复选框
                self.paginate_output.setChecked(config.get("paginate_output", False))
                self.disable_image_extraction.setChecked(config.get("disable_image_extraction", False))
                self.disable_multiprocessing.setChecked(config.get("disable_multiprocessing", False))
                self.debug_mode.setChecked(config.get("debug_mode", False))
                self.format_lines.setChecked(config.get("format_lines", False))
                self.force_ocr.setChecked(config.get("force_ocr", False))
                self.strip_existing_ocr.setChecked(config.get("strip_existing_ocr", False))
                self.disable_ocr_math.setChecked(config.get("disable_ocr_math", False))
                self.drop_repeated_text.setChecked(config.get("drop_repeated_text", False))
                self.use_llm.setChecked(config.get("use_llm", False))
                self.redo_inline_math.setChecked(config.get("redo_inline_math", False))
                self.debug_layout_images.setChecked(config.get("debug_layout_images", False))
                self.debug_pdf_images.setChecked(config.get("debug_pdf_images", False))
                self.debug_json.setChecked(config.get("debug_json", False))
                
                # 设置数值字段
                self.pdftext_workers.setValue(config.get("pdftext_workers", 4))
                self.max_concurrency.setValue(config.get("max_concurrency", 3))
                self.timeout.setValue(config.get("timeout", 30))
                self.max_retries.setValue(config.get("max_retries", 2))
                self.num_devices.setValue(config.get("num_devices", 1))
                self.num_workers.setValue(config.get("num_workers", 15))
                
                # 设置文本字段
                self.page_range.setText(config.get("page_range", ""))
                self.force_layout_block.setText(config.get("force_layout_block", ""))
                self.gemini_api_key.setText(config.get("gemini_api_key", ""))
                self.gemini_model_name.setText(config.get("gemini_model_name", "gemini-2.0-flash"))
                self.vertex_project_id.setText(config.get("vertex_project_id", ""))
                self.vertex_location.setText(config.get("vertex_location", "us-central1"))
                self.ollama_base_url.setText(config.get("ollama_base_url", "http://localhost:11434"))
                self.ollama_model.setText(config.get("ollama_model", "llama3.2-vision"))
                self.claude_api_key.setText(config.get("claude_api_key", ""))
                self.claude_model_name.setText(config.get("claude_model_name", "claude-3-7-sonnet-20250219"))
                self.openai_api_key.setText(config.get("openai_api_key", ""))
                self.openai_model.setText(config.get("openai_model", "gpt-4o-mini"))
                self.openai_base_url.setText(config.get("openai_base_url", "https://api.openai.com/v1"))
                self.processors.setText(config.get("processors", ""))
                self.config_json.setText(config.get("config_json", ""))
                self.debug_data_folder.setText(config.get("debug_data_folder", ""))
                
                QMessageBox.information(self, "加载成功", "配置已成功加载")
                self.generate_command()
                
            except Exception as e:
                QMessageBox.critical(self, "加载失败", f"加载配置时出错: {str(e)}")

    def set_combo_text(self, combo, text):
        index = combo.findText(text)
        if index >= 0:
            combo.setCurrentIndex(index)
        else:
            combo.addItem(text)
            combo.setCurrentIndex(combo.count() - 1)

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
        self.config_json.clear()
        self.preset_combo.setCurrentIndex(0)
        self.num_devices.setValue(1)
        self.num_workers.setValue(15)
        self.debug_data_folder.clear()
        self.debug_layout_images.setChecked(False)
        self.debug_pdf_images.setChecked(False)
        self.debug_json.setChecked(False)
        self.command_output.clear()
        
        self.toggle_llm_options(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # 设置应用程序图标
    try:
        app.setWindowIcon(QIcon("marker_icon.png"))
    except:
        pass
    
    window = MarkerGUI()
    window.show()
    sys.exit(app.exec())