from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt


class Sidebar:
    @staticmethod
    def create(main_window):
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("background-color: #1E3A5F;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(5)
        
        title_label = QLabel("岩心图像识别")
        title_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold; padding: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        layout.addSpacing(20)
        
        buttons = [
            ("首页", 0),
            ("数据管理", 1),
            ("数据处理", 2),
            ("图像预处理", 3),
            ("模型训练", 4),
            ("图像识别", 5),
        ]
        
        main_window.nav_buttons = []
        for text, page_idx in buttons:
            btn = QPushButton(text)
            btn.setFixedHeight(45)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, idx=page_idx: main_window.navigate_to_page(idx))
            main_window.nav_buttons.append(btn)
            layout.addWidget(btn)
        
        layout.addStretch()
        
        sidebar.setLayout(layout)
        main_window.update_nav_buttons()
        
        return sidebar