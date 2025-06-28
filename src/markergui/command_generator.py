import os
from PySide6.QtWidgets import QMessageBox

# 预设配置数据
PRESET_CONFIGS = {
    "default": {
        "output_format": "markdown",
        "image_extraction_mode": "提取图片 (默认)",
        "debug_mode": False,
        "pdftext_workers": 4,
        "format_lines": False,
        "ocr_mode": "标准OCR (默认)",
        "strip_existing_ocr": False,
        "ocr_task_name": "ocr_with_boxes",
        "disable_ocr_math": False,
        "drop_repeated_text": False,
        "converter_cls": "marker.converters.pdf.PdfConverter (默认)",
        "use_llm": False,
        "keep_pageheader_in_output": False,
        "keep_pagefooter_in_output": False,
        "disable_links": False,
    },
    "high_quality": {
        "output_format": "markdown",
        "use_llm": True,
        "llm_service": "Google Gemini",
        "gemini_model_name": "gemini-2.0-flash",
    },
    "table_extraction": {
        "converter_cls": "marker.converters.table.TableConverter",
        "image_extraction_mode": "禁用图片提取",
    },
    "pure_ocr": {
        "converter_cls": "marker.converters.ocr.OCRConverter",
        "ocr_mode": "强制OCR (扫描所有)",
        "use_llm": False,
    },
}


def get_preset_config(preset_name):
    """获取预设配置"""
    return PRESET_CONFIGS.get(preset_name, PRESET_CONFIGS["default"])


def generate_command(window):
    """
    根据主窗口的UI设置生成Marker命令
    """
    try:
        command = ""
        input_path = window.input_path.text().strip()

        # 确定是单文件还是批量处理
        if input_path and os.path.isdir(input_path):
            command += "marker "
            # 当输入是文件夹且输出路径为空时打印警告
            output_dir = window.output_dir.text().strip()
            if not output_dir:
                print("[WARNING]当前未设置输出路径")
        elif input_path:
            command += "marker_single "
        else:
            QMessageBox.warning(window, "输入错误", "请输入有效的文件或目录路径")
            return ""

        command += f'"{input_path}"'

        # 输出目录
        output_dir = window.output_dir.text().strip()
        if output_dir:
            command += f' --output_dir "{output_dir}"'

        # 输出格式
        output_format = window.output_format.currentText()
        if output_format != "markdown":
            command += f" --output_format {output_format}"

        # 页面范围
        page_range = window.page_range.text().strip()
        if page_range:
            command += f' --page_range "{page_range}"'

        # 基本选项
        if window.paginate_output.isChecked():
            command += " --paginate_output"

        # 图片处理模式
        image_mode = window.image_extraction_mode.currentText()
        if "禁用" in image_mode:
            command += " --disable_image_extraction"
        # "提取图片 (默认)"不需要标志

        if window.debug_mode.isChecked():
            command += " --debug"
        if window.disable_multiprocessing.isChecked():
            command += " --disable_multiprocessing"

        # PDF文本提取工作进程数
        pdftext_workers = window.pdftext_workers.value()
        if pdftext_workers != 4:
            command += f" --pdftext_workers {pdftext_workers}"

        # OCR选项
        if window.format_lines.isChecked():
            command += " --format_lines"

        # OCR处理模式
        ocr_mode = window.ocr_mode.currentText()
        if "禁用OCR" in ocr_mode:
            command += " --disable_ocr"
        elif "强制OCR" in ocr_mode:
            command += " --force_ocr"
        # "标准OCR (默认)"不需要添加标志

        if window.strip_existing_ocr.isChecked():
            command += " --strip_existing_ocr"

        # OCR任务模式
        ocr_task = window.ocr_task_name.currentText()
        if ocr_task != "ocr_with_boxes":
            command += f" --ocr_task_name {ocr_task}"
        if window.disable_ocr_math.isChecked():
            command += " --disable_ocr_math"
        if window.drop_repeated_text.isChecked():
            command += " --drop_repeated_text"

        # 转换器设置
        converter_cls = window.converter_cls.currentText()
        if "TableConverter" in converter_cls:
            command += " --converter_cls marker.converters.table.TableConverter"
        elif "OCRConverter" in converter_cls:
            command += " --converter_cls marker.converters.ocr.OCRConverter"
        elif "ExtractionConverter" in converter_cls:
            command += (
                " --converter_cls marker.converters.extraction.ExtractionConverter"
            )

        force_layout = window.force_layout_block.text().strip()
        if force_layout:
            command += f" --force_layout_block {force_layout}"

        # 输出内容控制
        if window.keep_pageheader_in_output.isChecked():
            command += " --keep_pageheader_in_output"
        if window.keep_pagefooter_in_output.isChecked():
            command += " --keep_pagefooter_in_output"
        if window.disable_links.isChecked():
            command += " --disable_links"

        # LLM选项
        if window.use_llm.isChecked():
            command += " --use_llm"

            if window.redo_inline_math.isChecked():
                command += " --redo_inline_math"

            # LLM服务配置
            service = window.llm_service.currentText()
            if "Vertex" in service:
                command += " --llm_service marker.services.vertex.GoogleVertexService"
                if window.vertex_project_id.text().strip():
                    command += f' --vertex_project_id "{window.vertex_project_id.text().strip()}"'
                if window.vertex_location.text().strip():
                    command += (
                        f' --vertex_location "{window.vertex_location.text().strip()}"'
                    )
            elif "Ollama" in service:
                command += " --llm_service marker.services.ollama.OllamaService"
                if window.ollama_base_url.text().strip():
                    command += (
                        f' --ollama_base_url "{window.ollama_base_url.text().strip()}"'
                    )
                if window.ollama_model.text().strip():
                    command += f' --ollama_model "{window.ollama_model.text().strip()}"'
            elif "Claude" in service:
                command += " --llm_service marker.services.claude.ClaudeService"
                if window.claude_api_key.text().strip():
                    command += (
                        f' --claude_api_key "{window.claude_api_key.text().strip()}"'
                    )
                if window.claude_model_name.text().strip():
                    command += f' --claude_model_name "{window.claude_model_name.text().strip()}"'
            elif "OpenAI" in service:
                command += " --llm_service marker.services.openai.OpenAIService"
                if window.openai_api_key.text().strip():
                    command += (
                        f' --openai_api_key "{window.openai_api_key.text().strip()}"'
                    )
                if window.openai_model.text().strip():
                    command += f' --openai_model "{window.openai_model.text().strip()}"'
                if window.openai_base_url.text().strip():
                    command += (
                        f' --openai_base_url "{window.openai_base_url.text().strip()}"'
                    )
            else:  # Gemini
                if window.gemini_api_key.text().strip():
                    command += (
                        f' --gemini_api_key "{window.gemini_api_key.text().strip()}"'
                    )
                if window.gemini_model_name.text().strip() != "gemini-2.0-flash":
                    command += f' --gemini_model_name "{window.gemini_model_name.text().strip()}"'

            # LLM高级选项
            if window.max_concurrency.value() != 3:
                command += f" --max_concurrency {window.max_concurrency.value()}"
            if window.timeout.value() != 30:
                command += f" --timeout {window.timeout.value()}"
            if window.max_retries.value() != 2:
                command += f" --max_retries {window.max_retries.value()}"

        # 高级选项 - 从AdvancedTab获取
        advanced_tab = window.tabs.widget(3)  # 第4个标签页是AdvancedTab
        if (
            hasattr(advanced_tab, "processors")
            and advanced_tab.processors.text().strip()
        ):
            processors = advanced_tab.processors.text().strip()
            command += f' --processors "{processors}"'

        # 调试选项
        if (
            hasattr(advanced_tab, "debug_data_folder")
            and advanced_tab.debug_data_folder.text().strip()
        ):
            debug_folder = advanced_tab.debug_data_folder.text().strip()
            command += f' --debug_data_folder "{debug_folder}"'
        if (
            hasattr(advanced_tab, "debug_layout_images")
            and advanced_tab.debug_layout_images.isChecked()
        ):
            command += " --debug_layout_images"
        if (
            hasattr(advanced_tab, "debug_pdf_images")
            and advanced_tab.debug_pdf_images.isChecked()
        ):
            command += " --debug_pdf_images"
        if hasattr(advanced_tab, "debug_json") and advanced_tab.debug_json.isChecked():
            command += " --debug_json"

        # 多GPU设置
        if (
            hasattr(advanced_tab, "num_devices")
            and advanced_tab.num_devices.value() > 1
        ):
            num_devices = advanced_tab.num_devices.value()
            num_workers = (
                advanced_tab.num_workers.value()
                if hasattr(advanced_tab, "num_workers")
                else 1
            )
            command = f'NUM_DEVICES={num_devices} NUM_WORKERS={num_workers} marker_chunk_convert "{input_path}" "{output_dir if output_dir else "output_dir"}"'

        return command
    except Exception as e:
        QMessageBox.critical(window, "生成命令错误", f"发生错误: {str(e)}")
        return ""
