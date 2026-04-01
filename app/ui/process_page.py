from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QGroupBox, QProgressBar, QTextEdit, QTableWidget
)
from PyQt6.QtWidgets import QHeaderView


class ProcessPage:
    @staticmethod
    def create(main_window):
        page = QWidget()
        layout = QVBoxLayout()
        
        main_content = QHBoxLayout()
        
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        main_window.process_status_label = QLabel("等待开始...")
        main_window.process_status_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #1E3A5F;
            padding: 8px;
            background-color: white;
            border: 1px solid #E0E0E0;
            border-radius: 4px;
        """)
        right_layout.addWidget(main_window.process_status_label)
        
        main_window.process_progress = QProgressBar()
        main_window.process_progress.setTextVisible(True)
        main_window.process_progress.setFormat("%p%")
        right_layout.addWidget(main_window.process_progress)
        
        main_window.process_log = QTextEdit()
        main_window.process_log.setReadOnly(True)
        main_window.process_log.setStyleSheet("background-color: white; color: #333333; border: 1px solid #E0E0E0; border-radius: 4px;")
        right_layout.addWidget(QLabel("处理日志:"))
        right_layout.addWidget(main_window.process_log)
        
        main_window.process_table = QTableWidget()
        main_window.process_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #E0E0E0;
                background-color: white;
                color: #333333;
            }
            QTableWidget::item {
                padding: 5px;
                word-wrap: break-word;
                color: #333333;
            }
            QHeaderView::section {
                background-color: #1E3A5F;
                color: white;
                padding: 5px;
                font-weight: bold;
            }
        """)
        main_window.process_table.setWordWrap(True)
        main_window.process_table.setColumnWidth(0, 120)
        main_window.process_table.setColumnWidth(1, 80)
        main_window.process_table.horizontalHeader().setStretchLastSection(True)
        main_window.process_table.resizeRowsToContents()
        
        right_layout.addWidget(QLabel("统计表格:"))
        right_layout.addWidget(main_window.process_table, 1)
        
        right_panel.setLayout(right_layout)
        
        main_content.addWidget(right_panel, 1)
        
        layout.addLayout(main_content)
        
        button_panel = QGroupBox("操作")
        button_layout = QHBoxLayout()
        
        select_source_btn = QPushButton("选择数据目录")
        select_source_btn.setStyleSheet("""
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
        select_source_btn.clicked.connect(main_window.process_handler.select_source_directory)
        button_layout.addWidget(select_source_btn)
        
        main_window.source_path_label = QLabel("未选择")
        main_window.source_path_label.setStyleSheet("color: #666; font-size: 12px; min-width: 200px;")
        button_layout.addWidget(main_window.source_path_label)
        
        select_output_btn = QPushButton("选择输出目录")
        select_output_btn.setStyleSheet("""
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
        select_output_btn.clicked.connect(main_window.process_handler.select_output_directory)
        button_layout.addWidget(select_output_btn)
        
        main_window.output_path_label = QLabel("未选择")
        main_window.output_path_label.setStyleSheet("color: #666; font-size: 12px; min-width: 200px;")
        button_layout.addWidget(main_window.output_path_label)
        
        button_layout.addStretch()
        
        main_window.process_btn = QPushButton("开始处理")
        main_window.process_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 12px 30px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """)
        main_window.process_btn.clicked.connect(main_window.process_handler.start_data_processing)
        button_layout.addWidget(main_window.process_btn)
        
        main_window.classify_btn = QPushButton("岩性分类")
        main_window.classify_btn.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """)
        main_window.classify_btn.clicked.connect(main_window.process_handler.start_lithology_classify)
        button_layout.addWidget(main_window.classify_btn)
        
        main_window.alteration_btn = QPushButton("蚀变分析")
        main_window.alteration_btn.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 20px;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """)
        main_window.alteration_btn.clicked.connect(main_window.process_handler.start_alteration_analysis)
        button_layout.addWidget(main_window.alteration_btn)
        
        button_panel.setLayout(button_layout)
        layout.addWidget(button_panel)
        
        page.setLayout(layout)
        return page