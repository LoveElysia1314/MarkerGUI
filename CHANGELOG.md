# 更新日志

所有值得注意的项目更改都会记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)，
此项目遵循 [Semantic Versioning](https://semver.org/spec/v2.0.0.html)。

## [1.0.1] - 2025-11-14

### 新增

- 采用 src 布局模式重新组织项目结构
- 完整的项目开发文档
- 详细的环境配置指南
- CHANGELOG.md 文件

### 变更

- **项目结构重大调整**
  - 所有源代码现在位于 `src/markergui/` 目录
  - 项目根目录 `main.py` 作为应用入口点
  - 移除项目根目录中的源代码文件，保持项目根目录整洁
  
- **目录结构更新**
  ```
  旧结构:
  MarkerGUI/
  ├── main.py
  ├── main_window.py
  ├── config_manager.py
  ├── command_generator.py
  ├── utils.py
  ├── tabs/
  └── config/
  
  新结构:
  MarkerGUI/
  ├── src/
  │   └── markergui/
  │       ├── main_window.py
  │       ├── config_manager.py
  │       ├── command_generator.py
  │       ├── utils.py
  │       ├── tabs/
  │       └── config/
  ├── main.py (入口点)
  └── config/
  ```

- **导入路径更新**
  - 所有内部导入已更新为相对于 `src/markergui/` 包
  - 项目根目录的 `main.py` 自动配置 Python 路径

### 改进

- 更好的代码组织和命名空间隔离
- 提高了项目的可维护性
- 便于未来的包管理和发布
- 更清晰的目录结构便于新开发者理解

### 移除

- 项目根目录中的旧源代码文件
- 项目根目录中的 `tabs/` 目录

### 技术细节

#### src 布局的优点

1. **命名空间隔离** - 所有应用代码都在一个清晰的包命名空间下
2. **发布友好** - 便于使用 `setuptools` 等工具打包
3. **项目根目录整洁** - 配置文件和文档独立于代码
4. **类型检查友好** - 更容易配置 Mypy 和其他类型检查工具
5. **测试组织** - 测试代码可以清晰地从项目根目录组织

#### 运行应用

```bash
# 从项目根目录运行
python main.py
```

#### 开发中导入

```python
# 项目根目录中创建的 main.py 会自动添加 src 到 sys.path
# 因此可以直接导入 markergui 包

from markergui.main_window import MarkerGUI
from markergui.config_manager import ConfigManager
from markergui.command_generator import generate_command
```

## [1.0.0] - 2025-11-14

### 首次发布

- 完整的 GUI 界面
- 支持所有主要 Marker 参数
- 配置预设管理系统
- 多 LLM 服务集成
  - Google Gemini
  - Google Vertex
  - Ollama
  - Claude
  - OpenAI
- 高级参数配置选项
- 实时日志输出
- 代码优化完成
  - 删除所有向后兼容代码
  - 删除所有未使用代码
  - 重组 OCR 标签页

---

**维护者**: [LoveElysia1314](https://github.com/LoveElysia1314)

**许可证**: MIT
