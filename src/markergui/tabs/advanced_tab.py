from .base_tab import BaseTab
from PySide6.QtWidgets import (
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QCheckBox,
    QSpinBox,
    QFormLayout,
    QVBoxLayout,
)
from PySide6.QtCore import Qt


class AdvancedTab(BaseTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = parent.config_manager

        # 处理器设置
        processor_group = QGroupBox("处理器设置")
        processor_layout = QFormLayout()

        self.processors = QLineEdit()
        processor_layout.addRow("自定义处理器链:", self.processors)
        processor_layout.addRow(QLabel("格式: processor1,processor2,..."))

        processor_group.setLayout(processor_layout)
        self.add_to_layout(processor_group)

        # 多GPU设置
        gpu_group = QGroupBox("多GPU设置")
        gpu_layout = QFormLayout()

        num_devices_layout = QHBoxLayout()
        num_devices_layout.addWidget(QLabel("GPU数量:"))
        self.num_devices = QSpinBox()
        self.num_devices.setRange(1, 8)
        self.num_devices.setValue(1)
        num_devices_layout.addWidget(self.num_devices)
        gpu_layout.addRow(num_devices_layout)

        num_workers_layout = QHBoxLayout()
        num_workers_layout.addWidget(QLabel("每GPU工作进程数:"))
        self.num_workers = QSpinBox()
        self.num_workers.setRange(1, 64)
        self.num_workers.setValue(32)
        num_workers_layout.addWidget(self.num_workers)
        gpu_layout.addRow(num_workers_layout)

        gpu_group.setLayout(gpu_layout)
        self.add_to_layout(gpu_group)

        # 连接信号：当GPU数量改变时更新工作进程状态
        self.num_devices.valueChanged.connect(self.update_workers_state)
        # 初始化工作进程状态
        self.update_workers_state()

        # 调试设置
        debug_group = QGroupBox("调试设置")
        debug_layout = QFormLayout()

        self.debug_data_folder = QLineEdit()
        debug_layout.addRow("调试数据存储目录:", self.debug_data_folder)

        debug_check_layout = QVBoxLayout()
        self.debug_layout_images = QCheckBox("保存布局分析图像")
        debug_check_layout.addWidget(self.debug_layout_images)
        self.debug_pdf_images = QCheckBox("保存PDF解析图像")
        debug_check_layout.addWidget(self.debug_pdf_images)
        self.debug_json = QCheckBox("保存中间JSON数据")
        debug_check_layout.addWidget(self.debug_json)
        debug_layout.addRow("调试选项:", debug_check_layout)

        debug_group.setLayout(debug_layout)
        self.add_to_layout(debug_group)

        self.add_stretch()

    def update_workers_state(self):
        """根据GPU数量启用或禁用工作进程设置"""
        if self.num_devices.value() == 1:
            self.num_workers.setEnabled(False)
        else:
            self.num_workers.setEnabled(True)
