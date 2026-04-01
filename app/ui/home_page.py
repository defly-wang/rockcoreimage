from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt


class HomePage:
    @staticmethod
    def create(main_window):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        title = QLabel("欢迎使用岩心图像识别系统")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #1E3A5F;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        layout.addSpacing(30)
        
        from PyQt6.QtWidgets import QFrame
        info_card = QFrame()
        info_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #E0E0E0;
            }
        """)
        info_layout = QVBoxLayout()
        
        intro_text = QLabel("""
            <h3>功能概述</h3>
            <ul style="font-size: 14px; line-height: 1.8;">
                <li><b>数据管理</b> - 导入、浏览和管理岩心图像数据集</li>
                <li><b>数据清洗</b> - 自动检测模糊、损坏或重复的图像</li>
                <li><b>图像预处理</b> - 归一化、尺寸调整和数据增强</li>
                <li><b>模型训练</b> - 使用预训练深度学习模型进行训练</li>
                <li><b>图像识别</b> - 对岩心图像进行分类识别</li>
            </ul>
        """)
        intro_text.setStyleSheet("color: #333;")
        info_layout.addWidget(intro_text)
        info_card.setLayout(info_layout)
        layout.addWidget(info_card)
        
        layout.addStretch()
        
        quick_start = QGroupBox("快速开始")
        quick_layout = QHBoxLayout()
        
        btn1 = QPushButton("导入数据集")
        btn1.clicked.connect(lambda: main_window.navigate_to_page(1))
        quick_layout.addWidget(btn1)
        
        btn2 = QPushButton("开始训练")
        btn2.clicked.connect(lambda: main_window.navigate_to_page(4))
        quick_layout.addWidget(btn2)
        
        btn3 = QPushButton("图像识别")
        btn3.clicked.connect(lambda: main_window.navigate_to_page(5))
        quick_layout.addWidget(btn3)
        
        quick_start.setLayout(quick_layout)
        layout.addWidget(quick_start)
        
        page.setLayout(layout)
        return page