from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QListWidget, QScrollArea, QGridLayout, QGroupBox, QFrame, QProgressBar
)
from PyQt6.QtCore import Qt


class DataPage:
    @staticmethod
    def create(main_window):
        page = QWidget()
        layout = QVBoxLayout()
        
        main_content = QHBoxLayout()
        
        left_panel = QFrame()
        left_panel.setFixedWidth(250)
        left_layout = QVBoxLayout()
        
        import_btn = QPushButton("导入图像")
        import_btn.clicked.connect(main_window.import_images)
        left_layout.addWidget(import_btn)
        
        import_folder_btn = QPushButton("导入文件夹")
        import_folder_btn.clicked.connect(main_window.import_folder)
        left_layout.addWidget(import_folder_btn)
        
        left_layout.addSpacing(10)
        
        main_window.category_list = QListWidget()
        main_window.category_list.itemClicked.connect(main_window.on_category_clicked)
        left_layout.addWidget(QLabel("类别列表:"))
        left_layout.addWidget(main_window.category_list)
        
        left_panel.setLayout(left_layout)
        
        main_content.addWidget(left_panel)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        main_window.image_grid = QScrollArea()
        main_window.image_grid.setWidgetResizable(True)
        main_window.image_grid.setStyleSheet("border: none;")
        
        main_window.image_grid_content = QWidget()
        main_window.image_grid_layout = QGridLayout()
        main_window.image_grid_content.setLayout(main_window.image_grid_layout)
        main_window.image_grid.setWidget(main_window.image_grid_content)
        
        right_layout.addWidget(main_window.image_grid)
        
        main_window.data_progress = QProgressBar()
        main_window.data_progress.setVisible(False)
        right_layout.addWidget(main_window.data_progress)
        
        right_panel.setLayout(right_layout)
        
        main_content.addWidget(right_panel, 1)
        
        layout.addLayout(main_content)
        
        button_panel = QHBoxLayout()
        
        clean_btn = QPushButton("数据清洗")
        clean_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 20px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        clean_btn.clicked.connect(main_window.start_data_cleaning)
        button_panel.addWidget(clean_btn)
        
        button_panel.addStretch()
        
        import_btn2 = QPushButton("导入图像")
        import_btn2.setStyleSheet("""
            QPushButton {
                background-color: #1E3A5F;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 20px;
            }
            QPushButton:hover {
                background-color: #2D5A87;
            }
        """)
        import_btn2.clicked.connect(main_window.import_images)
        button_panel.addWidget(import_btn2)
        
        import_folder_btn2 = QPushButton("导入文件夹")
        import_folder_btn2.setStyleSheet("""
            QPushButton {
                background-color: #1E3A5F;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 20px;
            }
            QPushButton:hover {
                background-color: #2D5A87;
            }
        """)
        import_folder_btn2.clicked.connect(main_window.import_folder)
        button_panel.addWidget(import_folder_btn2)
        
        layout.addLayout(button_panel)
        
        page.setLayout(layout)
        return page