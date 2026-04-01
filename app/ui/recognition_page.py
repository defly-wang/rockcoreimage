from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox, QFrame, QTextEdit
)
from PyQt6.QtCore import Qt


class RecognitionPage:
    @staticmethod
    def create(main_window):
        page = QWidget()
        layout = QVBoxLayout()
        
        main_content = QHBoxLayout()
        
        left_panel = QFrame()
        left_panel.setFixedWidth(300)
        left_layout = QVBoxLayout()
        
        model_group = QGroupBox("模型")
        model_layout = QVBoxLayout()
        
        load_model_btn = QPushButton("加载模型")
        load_model_btn.clicked.connect(main_window.load_model_for_recognition)
        model_layout.addWidget(load_model_btn)
        
        main_window.model_label = QLabel("未加载模型")
        main_window.model_label.setStyleSheet("color: #666; font-size: 12px;")
        model_layout.addWidget(main_window.model_label)
        
        model_group.setLayout(model_layout)
        left_layout.addWidget(model_group)
        
        input_group = QGroupBox("输入")
        input_layout = QVBoxLayout()
        
        single_btn = QPushButton("单图识别")
        single_btn.setStyleSheet("""
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
        single_btn.clicked.connect(main_window.recognize_single_image)
        input_layout.addWidget(single_btn)
        
        batch_btn = QPushButton("批量识别")
        batch_btn.setStyleSheet("""
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
        batch_btn.clicked.connect(main_window.recognize_batch_images)
        input_layout.addWidget(batch_btn)
        
        input_group.setLayout(input_layout)
        left_layout.addWidget(input_group)
        
        export_group = QGroupBox("导出")
        export_layout = QVBoxLayout()
        
        export_csv_btn = QPushButton("导出CSV")
        export_csv_btn.setStyleSheet("""
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
        export_csv_btn.clicked.connect(lambda: main_window.export_recognition_results('csv'))
        export_layout.addWidget(export_csv_btn)
        
        export_json_btn = QPushButton("导出JSON")
        export_json_btn.setStyleSheet("""
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
        export_json_btn.clicked.connect(lambda: main_window.export_recognition_results('json'))
        export_layout.addWidget(export_json_btn)
        
        export_group.setLayout(export_layout)
        left_layout.addWidget(export_group)
        
        left_panel.setLayout(left_layout)
        
        main_content.addWidget(left_panel)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        result_group = QGroupBox("识别结果")
        result_layout = QVBoxLayout()
        
        main_window.result_image_label = QLabel("图像预览")
        main_window.result_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_window.result_image_label.setStyleSheet("""
            background-color: #f0f0f0;
            border: 1px solid #ddd;
            min-height: 300px;
        """)
        result_layout.addWidget(main_window.result_image_label)
        
        main_window.result_label = QLabel("预测结果: --")
        main_window.result_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #1E3A5F;")
        result_layout.addWidget(main_window.result_label)
        
        main_window.confidence_label = QLabel("置信度: --")
        main_window.confidence_label.setStyleSheet("font-size: 14px; color: #666;")
        result_layout.addWidget(main_window.confidence_label)
        
        result_group.setLayout(result_layout)
        right_layout.addWidget(result_group)
        
        main_window.recognition_results = QTextEdit()
        main_window.recognition_results.setReadOnly(True)
        main_window.recognition_results.setMaximumHeight(150)
        main_window.recognition_results.setStyleSheet("background-color: white; color: #333333; border: 1px solid #E0E0E0; border-radius: 4px;")
        right_layout.addWidget(QLabel("识别详情:"))
        right_layout.addWidget(main_window.recognition_results)
        
        right_panel.setLayout(right_layout)
        
        main_content.addWidget(right_panel, 1)
        
        layout.addLayout(main_content)
        
        page.setLayout(layout)
        return page