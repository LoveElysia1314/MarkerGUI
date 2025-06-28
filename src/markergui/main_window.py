import os
import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QComboBox,
    QTextEdit,
    QFileDialog,
    QMessageBox,
    QSpinBox,
    QFormLayout,
    QInputDialog,
    QApplication,
    QSplitter,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from .config_manager import ConfigManager
from .tabs.basic_tab import create_basic_tab
from .tabs.ocr_tab import create_ocr_tab
from .tabs.llm_tab import create_llm_tab
from .tabs.advanced_tab import AdvancedTab
from .command_generator import generate_command
from .utils import EmittingStream


class MarkerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Marker Document Converter")
        # 设置初始最小尺寸
        self.setMinimumWidth(720)
        self.setMinimumHeight(480)

        # 初始化配置管理器
        self.config_manager = ConfigManager()

        # 创建主分割器
        main_splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(main_splitter)

        # 左面板
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)

        # 右面板
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

        # 设置运行日志组和命令组比例 1:1
        console_splitter.setSizes([300, 300])

        # 输入和输出设置组
        input_output_group = QGroupBox("输入和输出设置")
        input_output_layout = QFormLayout()

        self.input_path = QLineEdit()
        self.browse_input_btn = QPushButton("浏览...")
        self.browse_input_btn.clicked.connect(lambda: self.browse_input("file"))
        self.browse_folder_btn = QPushButton("浏览文件夹...")
        self.browse_folder_btn.clicked.connect(lambda: self.browse_input("folder"))

        input_output_layout.addRow(
            "输入文件/目录:",
            self.create_h_widget(
                [self.input_path, self.browse_input_btn, self.browse_folder_btn]
            ),
        )

        self.output_dir = QLineEdit()
        self.browse_output_btn = QPushButton("浏览...")
        self.browse_output_btn.clicked.connect(self.browse_output)
        input_output_layout.addRow(
            "输出目录:", self.create_h_widget([self.output_dir, self.browse_output_btn])
        )

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
        self.converter_cls.addItems(
            [
                "marker.converters.pdf.PdfConverter (默认)",
                "marker.converters.table.TableConverter",
                "marker.converters.ocr.OCRConverter",
                "marker.converters.extraction.ExtractionConverter",
            ]
        )
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
            path, _ = QFileDialog.getOpenFileName(
                self, "选择输入文件", "", "所有文件 (*.*)"
            )
        else:  # folder
            path = QFileDialog.getExistingDirectory(self, "选择输入文件夹")

        if path:
            self.input_path.setText(path)
            # 当选择文件且输出目录为空时，自动设置为文件所在目录
            if input_type == "file" and not self.output_dir.text().strip():
                self.output_dir.setText(os.path.dirname(path))

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

    # 配置项映射表 (属性名, 获取方法, 设置方法)
    _CONFIG_MAP = {
        # 基本设置
        "input_path": ("input_path", "text", "setText"),
        "output_dir": ("output_dir", "text", "setText"),
        "output_format": ("output_format", "currentText", "setCurrentText"),
        "page_range": ("page_range", "text", "setText"),
        # 基本选项
        "paginate_output": ("paginate_output", "isChecked", "setChecked"),
        "image_extraction_mode": (
            "image_extraction_mode",
            "currentText",
            "setCurrentText",
        ),
        "disable_multiprocessing": (
            "disable_multiprocessing",
            "isChecked",
            "setChecked",
        ),
        "debug_mode": ("debug_mode", "isChecked", "setChecked"),
        "pdftext_workers": ("pdftext_workers", "value", "setValue"),
        # OCR选项
        "format_lines": ("format_lines", "isChecked", "setChecked"),
        "ocr_mode": ("ocr_mode", "currentText", "setCurrentText"),
        "strip_existing_ocr": ("strip_existing_ocr", "isChecked", "setChecked"),
        "ocr_task_name": ("ocr_task_name", "currentText", "setCurrentText"),
        "disable_ocr_math": ("disable_ocr_math", "isChecked", "setChecked"),
        "drop_repeated_text": ("drop_repeated_text", "isChecked", "setChecked"),
        # LLM选项
        "use_llm": ("use_llm", "isChecked", "setChecked"),
        "redo_inline_math": ("redo_inline_math", "isChecked", "setChecked"),
        "llm_service": ("llm_service", "currentText", "setCurrentText"),
        "gemini_api_key": ("gemini_api_key", "text", "setText"),
        "gemini_model_name": ("gemini_model_name", "text", "setText"),
        "vertex_project_id": ("vertex_project_id", "text", "setText"),
        "vertex_location": ("vertex_location", "text", "setText"),
        "ollama_base_url": ("ollama_base_url", "text", "setText"),
        "ollama_model": ("ollama_model", "text", "setText"),
        "claude_api_key": ("claude_api_key", "text", "setText"),
        "claude_model_name": ("claude_model_name", "text", "setText"),
        "openai_api_key": ("openai_api_key", "text", "setText"),
        "openai_model": ("openai_model", "text", "setText"),
        "openai_base_url": ("openai_base_url", "text", "setText"),
        "max_concurrency": ("max_concurrency", "value", "setValue"),
        "timeout": ("timeout", "value", "setValue"),
        "max_retries": ("max_retries", "value", "setValue"),
        # 输出内容控制
        "keep_pageheader_in_output": (
            "keep_pageheader_in_output",
            "isChecked",
            "setChecked",
        ),
        "keep_pagefooter_in_output": (
            "keep_pagefooter_in_output",
            "isChecked",
            "setChecked",
        ),
        "disable_links": ("disable_links", "isChecked", "setChecked"),
    }

    def _get_advanced_tab(self):
        """获取高级设置标签页，并缓存结果以避免重复查找"""
        if not hasattr(self, "_advanced_tab"):
            for i in range(self.tabs.count()):
                if self.tabs.tabText(i) == "高级设置":
                    self._advanced_tab = self.tabs.widget(i)
                    break
            else:
                self._advanced_tab = None
        return self._advanced_tab

    def get_current_config(self):
        """获取当前UI配置数据"""
        config = {}
        advanced_tab = self._get_advanced_tab()

        # 处理基本配置项
        for key, (attr, getter, _) in self._CONFIG_MAP.items():
            if hasattr(self, attr):
                widget = getattr(self, attr)
                config[key] = getattr(widget, getter)()
            else:
                config[key] = None

        # 特殊处理项 (不在映射表中的)
        config["converter_cls"] = (
            self.converter_cls.currentText() if hasattr(self, "converter_cls") else ""
        )
        config["force_layout_block"] = (
            self.force_layout_block.text()
            if hasattr(self, "force_layout_block")
            else ""
        )

        # 高级标签页配置
        if advanced_tab:
            config["processors"] = (
                advanced_tab.processors.text()
                if hasattr(advanced_tab, "processors")
                else ""
            )
            config["num_devices"] = (
                advanced_tab.num_devices.value()
                if hasattr(advanced_tab, "num_devices")
                else 1
            )
            config["debug_data_folder"] = (
                advanced_tab.debug_data_folder.text()
                if hasattr(advanced_tab, "debug_data_folder")
                else ""
            )
            config["debug_layout_images"] = (
                advanced_tab.debug_layout_images.isChecked()
                if hasattr(advanced_tab, "debug_layout_images")
                else False
            )
            config["debug_pdf_images"] = (
                advanced_tab.debug_pdf_images.isChecked()
                if hasattr(advanced_tab, "debug_pdf_images")
                else False
            )
            config["debug_json"] = (
                advanced_tab.debug_json.isChecked()
                if hasattr(advanced_tab, "debug_json")
                else False
            )
            config["num_workers"] = (
                advanced_tab.num_workers.value()
                if hasattr(advanced_tab, "num_workers")
                else 32
            )

        return config

    def apply_config(self, config_data):
        """应用配置到UI"""
        # 使用配置映射表应用基本配置
        for key, (attr, _, setter) in self._CONFIG_MAP.items():
            if key in config_data and hasattr(self, attr):
                widget = getattr(self, attr)
                value = config_data[key]

                # 特殊处理组合框设置
                if setter == "setCurrentText" and isinstance(widget, QComboBox):
                    self.set_combo_text(widget, value)
                else:
                    getattr(widget, setter)(value)

        # 特殊处理项 (不在映射表中的)
        if "converter_cls" in config_data and hasattr(self, "converter_cls"):
            self.set_combo_text(self.converter_cls, config_data["converter_cls"])

        if "force_layout_block" in config_data and hasattr(self, "force_layout_block"):
            self.force_layout_block.setText(config_data["force_layout_block"])

        # 高级标签页配置
        advanced_tab = self._get_advanced_tab()
        if advanced_tab:
            advanced_configs = [
                ("processors", "processors", "setText"),
                ("num_devices", "num_devices", "setValue"),
                ("debug_data_folder", "debug_data_folder", "setText"),
                ("debug_layout_images", "debug_layout_images", "setChecked"),
                ("debug_pdf_images", "debug_pdf_images", "setChecked"),
                ("debug_json", "debug_json", "setChecked"),
                ("num_workers", "num_workers", "setValue"),
            ]

            for key, attr, setter in advanced_configs:
                if key in config_data and hasattr(advanced_tab, attr):
                    widget = getattr(advanced_tab, attr)
                    getattr(widget, setter)(config_data[key])

        print("[INFO] 配置已成功应用到UI")

    def save_config(self):
        # 获取当前配置名称
        current_config = self.preset_combo.currentText()
        config_name, ok = QInputDialog.getText(
            self, "保存配置", "输入配置名称:", QLineEdit.EchoMode.Normal, current_config
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
            overwrite=True,
        ):
            print("[INFO] 保存成功: 配置已成功保存")
            self.refresh_config_list()
            self.preset_combo.setCurrentText(config_name)
        else:
            print("[ERROR] 保存失败: 无法保存配置")

    def delete_preset(self):
        """删除当前选中的预设"""
        preset_name = self.preset_combo.currentText()
        if not preset_name:
            print("[WORRY] 删除失败: 没有选中的预设")
            return

        if preset_name == "default":
            print("[ERROR] 删除失败: 不能删除默认预设")
            return

        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要永久删除预设 '{preset_name}' 吗?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.No:
            return

        # 从配置管理器中删除预设
        if self.config_manager.delete_preset(preset_name):
            print(f"[INFO] 删除成功: 预设 '{preset_name}' 已删除")
            self.refresh_config_list()
        else:
            print(f"[ERROR] 删除失败: 无法删除预设 '{preset_name}'")

    def refresh_config_list(self):
        """刷新配置列表"""
        if hasattr(self, "preset_combo"):
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
        """重置配置逻辑"""
        current_preset = self.preset_combo.currentText()

        # 如果当前预设存在，则复位该预设
        if current_preset and self.config_manager.preset_exists(current_preset):
            preset_config = self.config_manager.load_preset(current_preset)
            self.apply_config(preset_config)
            print(f"[INFO] 配置已复位到预设 '{current_preset}'")
        else:
            # 否则清空当前配置并应用默认配置
            self.config_manager.reset_to_default()
            self.apply_config(self.config_manager.default_config)
            self.refresh_config_list()  # 刷新预设列表
            print("[INFO] 配置已重置为默认值")

    def reset_preset(self):
        """将当前预设复位到command_generator.py中定义的状态"""
        from .command_generator import get_preset_config

        preset_name = self.preset_combo.currentText()
        if not preset_name:
            print("[WORRY] 重置预设失败: 没有选中的预设")
            return

        # 获取预设配置
        preset_config = get_preset_config(preset_name)
        if preset_config:
            self.apply_config(preset_config)
            print(f"[INFO] 预设 '{preset_name}' 已复位到command_generator定义的状态")
        else:
            # 获取默认配置
            default_config = get_preset_config("default")
            self.apply_config(default_config)
            print("[INFO] 预设已复位到command_generator的默认状态")
