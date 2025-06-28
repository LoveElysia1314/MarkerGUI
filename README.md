# 📄 MarkerGUI - Marker 文档转换 GUI 工具

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![Status](https://img.shields.io/badge/status-stable-brightgreen)

> 一个功能丰富的图形界面工具，用于将 PDF 和其他文档快速准确地转换为 Markdown、JSON、HTML 等格式。

## ✨ 主要特性

- 🎯 **直观的 GUI 界面** - 无需命令线，用户友好的图形界面
- 📚 **多格式支持** - PDF、图片、PPTX、DOCX、XLSX、HTML、EPUB
- 🔄 **多格式输出** - Markdown、JSON、HTML、Chunks
- 🎨 **智能参数配置** - 表格、方程式、公式、代码块格式化
- 🖼️ **图像处理** - 自动提取并保存图像
- 🚀 **LLM 增强** - 集成 Google Gemini、OpenAI 等 LLM 服务提升准确度
- 💾 **配置预设管理** - 保存常用配置预设，快速切换
- 🔧 **高级选项** - 多 GPU、自定义处理器、调试模式等
- 📊 **OCR 支持** - 多种 OCR 处理模式和参数调整
- 💬 **实时日志** - 查看命令执行过程和输出结果

## 📚 文档导航

| 文档 | 描述 |
|-----|------|
| [🏠 README.md](README.md) | 你在这里 - 项目概览和快速开始 |
| [📖 功能性参数手册](功能性参数使用手册.md) | 中文功能参数详细说明 |
| [ 更新日志](CHANGELOG.md) | 版本历史和更新说明 |
| [📚 参数手册](功能性参数使用手册.md) | 中文功能参数详细说明 |
| [⚙️ Marker 官方参数](https://github.com/VikParuchuri/marker#usage) | Marker 工具原始参数参考（外部链接） |

## 🚀 快速开始

### 系统要求

- Windows / macOS / Linux
- Python 3.8 或更高版本
- PySide6 (Qt for Python)

### 安装

1. **克隆仓库**
```bash
git clone https://github.com/LoveElysia1314/MarkerGUI.git
cd MarkerGUI
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **运行应用**
```bash
python main.py
```

## 🏗️ 打包与分发 (PyInstaller)

如果你想将 GUI 打包成独立可执行文件（Windows），请查看 `BUILD.md` 获取更详尽的步骤。常见要点：

- 使用 `python -m PyInstaller` 而不是 `python -m pyinstaller`（注意大小写）。
- 如果使用 `src/` 布局，确保传入 `--paths src` 使 PyInstaller 能找到 `markergui` 包。
- 将 `config` 文件夹加入 `--add-data "config;config"` 以便 `config/default.json` 随构建一起发布。
- 对于 Qt 应用，PyInstaller 的 hooks 会处理大多数 PySide6 插件；若运行时出现 platform 插件错误，请重新安装 PySide6 并重建，或将 Qt 插件路径显式包含进 build（可在 `.spec` 中设置）。

如果你想要一键构建，请参阅仓库根目录中的 `build_pyinstaller.py` 或 `BUILD.md` 中的 PyInstaller 说明。

## 📖 使用指南

### 基本工作流

1. **选择输入文件/目录**
   - 点击"浏览..."选择单个文件
   - 或点击"浏览文件夹..."选择整个目录

2. **设置输出目录**
   - 选择转换后文件的保存位置
   - 如果不选择，默认为输入文件所在目录

3. **配置转换参数**
   - 在各个标签页中选择所需参数
   - 使用预设快速应用常见配置

4. **生成命令**
   - 点击"生成命令"按钮生成对应的命令行
   - 可在"生成的命令"框中查看完整命令

5. **执行转换**
   - 点击"运行命令"在新窗口执行转换
   - 实时查看运行日志

### 标签页说明

#### 📋 基本设置
- **分页输出** - 每个页面单独生成一个输出文件
- **图片处理** - 选择是否从文档中提取图片
- **多进程处理** - 控制是否使用多进程加快转换速度
- **调试模式** - 启用详细的调试输出信息
- **输出格式** - 选择输出格式：Markdown、JSON、HTML 等
- **页面范围** - 指定要转换的页面范围（如：1-5,8）

#### 🎯 OCR 设置
- **OCR 处理模式** - 标准、禁用或强制 OCR
- **格式化行** - 移除多余的空格和格式化文本
- **移除现有OCR** - 删除PDF中原有的OCR文本
- **OCR 任务模式** - 不同的OCR识别模式
- **禁用OCR数学** - 禁用数学公式识别
- **移除重复文本** - 删除OCR结果中的重复内容

#### 🤖 LLM 设置
- **启用LLM处理** - 使用大语言模型增强转换质量
- **LLM 服务选择** - 支持 Google Gemini、Vertex、Ollama、Claude、OpenAI
- **服务配置** - 针对不同服务的具体配置
  - API密钥、模型名称、端点等
- **高级选项** - 并发数、超时时间、重试次数

#### ⚙️ 高级设置
- **自定义处理器** - 指定处理器链
- **多GPU支持** - 配置使用的GPU数量和工作进程
- **调试选项** - 保存调试数据、布局图像等

#### 📁 配置管理
- **当前预设** - 显示当前使用的预设配置
- **保存配置** - 保存当前配置为新预设
- **重置配置** - 恢复当前预设或默认配置
- **删除预设** - 删除用户创建的预设
- **重置预设** - 将预设恢复到原始定义状态

## 🎨 功能详解

### 参数转换模式

应用采用**互斥参数单选框设计**，提升用户体验：

```
图片处理模式：
  • 提取图片(默认)          → 不添加标志
  • 禁用图片提取             → 生成 --disable_image_extraction

OCR处理模式：
  • 标准OCR(默认)            → 不添加标志
  • 禁用OCR                  → 生成 --disable_ocr
  • 强制OCR(扫描所有)        → 生成 --force_ocr
```

### 预设配置

应用预置了 4 个常用预设：

| 预设名 | 描述 | 适用场景 |
|-------|------|--------|
| **default** | 默认配置 | 通用文档转换 |
| **high_quality** | 高质量转换 | 启用LLM，提高准确度 |
| **table_extraction** | 表格提取 | 禁用图片，专注表格提取 |
| **pure_ocr** | 纯OCR模式 | 扫描件或图像类文档 |

### 命令行参数对应

生成的命令行示例：

```bash
# 基础转换
marker_single "input.pdf" --output_dir "./output" --output_format markdown

# 启用LLM和高级OCR
marker "input_folder/" --use_llm --gemini_api_key "YOUR_KEY" --force_ocr

# 表格提取模式
marker "document.pdf" --converter_cls marker.converters.table.TableConverter

# 多GPU处理
NUM_DEVICES=2 NUM_WORKERS=32 marker_chunk_convert "input.pdf" "output/"
```

## 🔧 配置文件

### 默认配置位置

- Windows: `config/default.json`
- Linux/macOS: `config/default.json`

### 配置格式

```json
{
  "default": {
    "description": "默认配置",
    "settings": {
      "output_format": "markdown",
      "image_extraction_mode": "提取图片 (默认)",
      "use_llm": false
    }
  }
}
```

## 📝 工作原理

```
用户输入 → 参数映射 → 命令生成 → 执行转换 → 结果输出
  ↓         ↓         ↓        ↓        ↓
配置UI    _CONFIG_MAP  shell  Marker   日志显示
                                      ↓
                                   实时反馈
```

### 关键组件

- **src/markergui/main_window.py** - 主窗口和核心逻辑，UI布局和事件处理
- **src/markergui/command_generator.py** - 命令行参数映射和生成器，预设定义
- **src/markergui/config_manager.py** - 配置文件加载、预设管理、持久化存储
- **src/markergui/tabs/** - 各个功能标签页模块，分离不同功能区域
- **src/markergui/utils.py** - 工具函数和输出重定向，日志处理

## 🎯 标签页结构优化

```
基本设置 (基础参数)
├── 基本选项
├── 输出内容控制
└── 配置管理

OCR设置 (OCR专用)
└── OCR基础选项

LLM设置 (LLM服务)
├── 服务选择
├── 各服务配置
└── 高级选项

高级设置 (系统级)
├── 处理器配置
├── 多GPU设置
└── 调试选项
```

## 🚀 高级使用

### 自定义处理器

在高级设置中指定处理器链：
```
processor1,processor2,processor3
```

### 多GPU处理

1. 在高级设置中设置 GPU 数量
2. 配置每 GPU 工作进程数
3. 生成命令会自动设置环境变量

### 调试模式

启用调试模式会：
- 保存中间处理结果
- 生成布局分析图像
- 导出 JSON 调试数据

## 📊 系统要求

| 项目 | 要求 |
|------|------|
| 操作系统 | Windows 10+ / macOS 10.14+ / Linux |
| Python | 3.8 或更高版本 |
| 内存 | 最少 4GB，推荐 8GB+ |
| 存储 | 200MB+ 用于模型和依赖 |
| GPU | 可选，NVIDIA CUDA 推荐用于高性能 |

## 🛠️ 开发和贡献

### 项目结构

```
MarkerGUI/
├── src/                               # 源代码目录
│   └── markergui/                     # 应用包
│       ├── __init__.py                # 包初始化
│       ├── main_window.py             # 主窗口和核心逻辑
│       ├── command_generator.py       # 命令生成器和预设定义
│       ├── config_manager.py          # 配置管理和预设持久化
│       ├── utils.py                   # 工具函数和输出重定向
│       ├── tabs/                      # 标签页模块
│       │   ├── __init__.py           # 模块初始化
│       │   ├── base_tab.py           # 标签页基类
│       │   ├── basic_tab.py          # 基本设置标签页
│       │   ├── ocr_tab.py            # OCR设置标签页
│       │   ├── llm_tab.py            # LLM设置标签页
│       │   └── advanced_tab.py       # 高级设置标签页
│       └── config/                    # 配置管理模块
│           ├── __init__.py           # 模块初始化
│           └── config_manager.py     # 配置管理逻辑
├── config/                            # 预设配置文件
│   └── default.json                   # 默认预设配置
├── main.py                            # 应用入口点
├── requirements.txt                   # 项目依赖
├── README.md                          # 本文件
├── .gitignore                         # Git忽略文件
└── .git/                              # Git仓库
```

### 代码组织

- **main.py** - 应用入口点，配置Python路径并启动GUI
- **src/markergui/** - 主应用包，包含所有核心代码
- **tabs/** - 各个功能标签页的实现模块
- **config_manager.py** - 配置持久化和预设管理
- **command_generator.py** - 命令行参数映射和生成逻辑

### 项目设置和开发

#### 环境配置

1. **创建虚拟环境**（推荐）
```bash
# 使用 venv
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

在提交与开发代码之前，建议在本地运行 `python main.py` 验证界面是否能正确启动并手动检查常见功能（例如命令生成、配置加载）。

#### 运行应用

```bash
# 从项目根目录运行
python main.py
```

#### 导入说明

项目采用 **src 布局** 模式，所有应用代码都在 `src/markergui/` 目录下：

```python
# 项目根目录的 main.py 会自动将 src 添加到 Python 路径
# 这样可以直接导入 markergui 包
from markergui.main_window import MarkerGUI
from markergui.config_manager import ConfigManager
from markergui.tabs.basic_tab import create_basic_tab
```

### 常见问题

**Q: 如何添加新的预设？**

A: 在基本设置标签页配置好参数后，点击"保存配置"按钮，输入预设名称即可保存。

**Q: 如何使用自定义的 LLM 服务？**

A: 在 LLM 设置标签页选择对应的服务，填入 API 密钥和端点信息即可。

**Q: 命令执行失败怎么办？**

A: 查看运行日志获取错误信息，确保已安装 Marker 工具并添加到 PATH。

**Q: 如何在 Linux/macOS 上使用？**

A: 安装 Python 和 PySide6，然后运行 `python main.py` 即可。

## 📚 相关资源

- [Marker 官方文档](https://github.com/VikParuchuri/marker)
- [Marker 命令行参数](https://github.com/VikParuchuri/marker#usage)
- [PySide6 文档](https://doc.qt.io/qtforpython/)

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🤝 支持与反馈

- 🐛 报告 Bug：[GitHub Issues](https://github.com/LoveElysia1314/MarkerGUI/issues)
- 💬 讨论功能：[GitHub Discussions](https://github.com/LoveElysia1314/MarkerGUI/discussions)
- ⭐ 如果有帮助，请给个Star！

## 📝 更新日志

### v1.0.1 (2025-11-14)

📦 **项目结构重构**

- ✅ 采用 src 布局模式组织代码
- ✅ 所有源代码迁移到 `src/markergui/` 目录
- ✅ 改进项目的可维护性和可扩展性
- ✅ 更新 .gitignore 规则
- ✅ 完整的项目文档更新

**改动说明：**
- 主应用代码现在位于 `src/markergui/` 包中
- 项目根目录 `main.py` 作为入口点，自动配置 Python 路径
- 支持更清晰的包结构和更好的命名空间隔离
- 便于未来打包和发布

### v1.0.0 (2025-11-14)

✨ **首次发布**

- ✅ 完整的 GUI 界面
- ✅ 支持所有主要 Marker 参数
- ✅ 配置预设管理
- ✅ 多 LLM 服务集成
- ✅ 高级参数配置
- ✅ 代码清洁和优化完成
  - 删除所有向后兼容代码
  - 删除所有未使用代码
  - 执行 OCR 标签页重组

---

**Made with ❤️ for the Marker Community**
