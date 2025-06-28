from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QCheckBox,
    QSpinBox,
    QFormLayout,
    QScrollArea,
)
from PySide6.QtCore import Qt


def create_llm_tab(parent):
    # 创建滚动区域
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)

    # 创建内容容器
    content = QWidget()
    layout = QVBoxLayout(content)
    scroll.setWidget(content)

    # LLM服务设置
    service_group = QGroupBox("LLM服务设置")
    service_layout = QVBoxLayout()

    # 启用LLM处理
    parent.use_llm = QCheckBox("启用LLM处理 (增强文本质量)")
    parent.use_llm.toggled.connect(parent.toggle_llm_options)
    service_layout.addWidget(parent.use_llm)

    # LLM服务选择
    service_layout.addWidget(QLabel("选择LLM服务:"))
    parent.llm_service = QComboBox()
    parent.llm_service.addItems(
        ["Google Gemini (默认)", "Google Vertex", "Ollama", "Claude", "OpenAI"]
    )
    service_layout.addWidget(parent.llm_service)

    # 数学公式处理
    parent.redo_inline_math = QCheckBox("重新处理行内数学公式")
    service_layout.addWidget(parent.redo_inline_math)

    service_group.setLayout(service_layout)
    layout.addWidget(service_group)

    # 隐藏所有服务控件组
    def toggle_service_visibility(index):
        service_groups = [
            gemini_group,
            vertex_group,
            ollama_group,
            claude_group,
            openai_group,
        ]
        for i, group in enumerate(service_groups):
            group.setVisible(i == index)

    # 监听服务选择变化
    parent.llm_service.currentIndexChanged.connect(toggle_service_visibility)

    # Gemini设置
    gemini_group = QGroupBox("Google Gemini设置")
    gemini_layout = QFormLayout()
    gemini_group.setVisible(False)

    parent.gemini_api_key = QLineEdit()
    gemini_layout.addRow("API密钥:", parent.gemini_api_key)
    parent.gemini_model_name = QLineEdit("gemini-2.0-flash")
    gemini_layout.addRow("模型名称:", parent.gemini_model_name)

    gemini_group.setLayout(gemini_layout)
    layout.addWidget(gemini_group)

    # Vertex设置
    vertex_group = QGroupBox("Google Vertex设置")
    vertex_layout = QFormLayout()
    vertex_group.setVisible(False)

    parent.vertex_project_id = QLineEdit()
    vertex_layout.addRow("项目ID:", parent.vertex_project_id)
    parent.vertex_location = QLineEdit("us-central1")
    vertex_layout.addRow("位置:", parent.vertex_location)

    vertex_group.setLayout(vertex_layout)
    layout.addWidget(vertex_group)

    # Ollama设置
    ollama_group = QGroupBox("Ollama设置")
    ollama_layout = QFormLayout()
    ollama_group.setVisible(False)

    parent.ollama_base_url = QLineEdit("http://localhost:11434")
    ollama_layout.addRow("基础URL:", parent.ollama_base_url)
    parent.ollama_model = QLineEdit("llama3.2-vision")
    ollama_layout.addRow("模型名称:", parent.ollama_model)

    ollama_group.setLayout(ollama_layout)
    layout.addWidget(ollama_group)

    # Claude设置
    claude_group = QGroupBox("Claude设置")
    claude_layout = QFormLayout()
    claude_group.setVisible(False)

    parent.claude_api_key = QLineEdit()
    claude_layout.addRow("API密钥:", parent.claude_api_key)
    parent.claude_model_name = QLineEdit("claude-3-7-sonnet-20250219")
    claude_layout.addRow("模型名称:", parent.claude_model_name)

    claude_group.setLayout(claude_layout)
    layout.addWidget(claude_group)

    # OpenAI设置
    openai_group = QGroupBox("OpenAI设置")
    openai_layout = QFormLayout()
    openai_group.setVisible(False)

    parent.openai_api_key = QLineEdit()
    openai_layout.addRow("API密钥:", parent.openai_api_key)
    parent.openai_model = QLineEdit("gpt-4o-mini")
    openai_layout.addRow("模型名称:", parent.openai_model)
    parent.openai_base_url = QLineEdit("https://api.openai.com/v1")
    openai_layout.addRow("自定义API端点:", parent.openai_base_url)

    openai_group.setLayout(openai_layout)
    layout.addWidget(openai_group)

    # 默认显示第一个服务的控件组
    toggle_service_visibility(0)

    # LLM高级选项
    advanced_group = QGroupBox("LLM高级选项")
    advanced_layout = QFormLayout()

    max_concurrency_layout = QHBoxLayout()
    max_concurrency_layout.addWidget(QLabel("最大并发请求数:"))
    parent.max_concurrency = QSpinBox()
    parent.max_concurrency.setRange(1, 20)
    parent.max_concurrency.setValue(3)
    max_concurrency_layout.addWidget(parent.max_concurrency)
    advanced_layout.addRow(max_concurrency_layout)

    timeout_layout = QHBoxLayout()
    timeout_layout.addWidget(QLabel("请求超时时间 (秒):"))
    parent.timeout = QSpinBox()
    parent.timeout.setRange(10, 600)
    parent.timeout.setValue(30)
    timeout_layout.addWidget(parent.timeout)
    advanced_layout.addRow(timeout_layout)

    retries_layout = QHBoxLayout()
    retries_layout.addWidget(QLabel("最大重试次数:"))
    parent.max_retries = QSpinBox()
    parent.max_retries.setRange(0, 10)
    parent.max_retries.setValue(2)
    retries_layout.addWidget(parent.max_retries)
    advanced_layout.addRow(retries_layout)

    advanced_group.setLayout(advanced_layout)
    layout.addWidget(advanced_group)

    layout.addStretch()
    return scroll
