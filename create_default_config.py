import os
import json
from pathlib import Path

# 创建 config 目录
config_dir = Path("config")
config_dir.mkdir(exist_ok=True)

# 定义默认配置
default_configs = {
    "default": {
        "description": "默认配置",
        "settings": {
            "output_format": "markdown",
            "disable_image_extraction": False,
            "use_llm": False
        }
    },
    "high_quality": {
        "description": "高质量转换",
        "settings": {
            "output_format": "markdown",
            "use_llm": True,
            "llm_service": "Google Gemini",
            "gemini_model_name": "gemini-2.0-flash"
        }
    },
    "table_extraction": {
        "description": "表格提取",
        "settings": {
            "converter_cls": "marker.converters.table.TableConverter",
            "disable_image_extraction": True
        }
    },
    "pure_ocr": {
        "description": "纯OCR处理",
        "settings": {
            "converter_cls": "marker.converters.ocr.OCRConverter",
            "force_ocr": True,
            "use_llm": False
        }
    }
}

# 写入 default.json
config_path = config_dir / "default.json"
with open(config_path, "w", encoding="utf-8") as f:
    json.dump(default_configs, f, indent=2, ensure_ascii=False)

print(f"默认配置文件已创建: {config_path}")