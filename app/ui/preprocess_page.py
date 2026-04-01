from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QGroupBox, QFrame, QComboBox, QCheckBox
)
from PyQt6.QtCore import Qt


class PreprocessPage:
    @staticmethod
    def create(main_window):
        page = QWidget()
        layout = QVBoxLayout()
        
        main_content = QHBoxLayout()
        
        left_panel = QFrame()
        left_panel.setFixedWidth(300)
        left_layout = QVBoxLayout()
        
        size_group = QGroupBox("图像尺寸")
        size_layout = QVBoxLayout()
        main_window.size_combo = QComboBox()
        main_window.size_combo.addItems(["224x224", "256x256", "512x512", "自定义"])
        size_layout.addWidget(QLabel("目标尺寸:"))
        main_window.size_combo.addItem("224x224")
        main_window.size_combo.addItem("256x256")
        main_window.size_combo.addItem("512x512")
        size_layout.addWidget(main_window.size_combo)
        size_group.setLayout(size_layout)
        left_layout.addWidget(size_group)
        
        augment_group = QGroupBox("数据增强")
        augment_layout = QVBoxLayout()
        main_window.augment_flip = QCheckBox("随机翻转")
        main_window.augment_flip.setChecked(True)
        augment_layout.addWidget(main_window.augment_flip)
        
        main_window.augment_rotate = QCheckBox("随机旋转")
        main_window.augment_rotate.setChecked(True)
        augment_layout.addWidget(main_window.augment_rotate)
        
        main_window.augment_color = QCheckBox("颜色抖动")
        main_window.augment_color.setChecked(True)
        augment_layout.addWidget(main_window.augment_color)
        
        main_window.augment_noise = QCheckBox("添加噪声")
        augment_layout.addWidget(main_window.augment_noise)
        augment_group.setLayout(augment_layout)
        left_layout.addWidget(augment_group)
        
        left_panel.setLayout(left_layout)
        
        main_content.addWidget(left_panel)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        main_window.preview_label = QLabel("预览区域")
        main_window.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_window.preview_label.setStyleSheet("""
            background-color: #f0f0f0;
            border: 2px dashed #ccc;
            min-height: 400px;
        """)
        right_layout.addWidget(main_window.preview_label)
        
        right_panel.setLayout(right_layout)
        
        main_content.addWidget(right_panel, 1)
        
        layout.addLayout(main_content)
        
        button_panel = QGroupBox("操作")
        button_layout = QHBoxLayout()
        
        preview_btn = QPushButton("预览增强效果")
        preview_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 20px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        preview_btn.clicked.connect(main_window.preview_augmentation)
        button_layout.addWidget(preview_btn)
        
        button_layout.addStretch()
        
        apply_btn = QPushButton("应用预处理")
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 20px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        apply_btn.clicked.connect(main_window.apply_preprocessing)
        button_layout.addWidget(apply_btn)
        
        button_panel.setLayout(button_layout)
        layout.addWidget(button_panel)
        
        page.setLayout(layout)
        return page