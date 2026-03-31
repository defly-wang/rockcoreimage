import os
import sys
import json
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QStackedWidget, QFrame, QFileDialog,
    QComboBox, QSpinBox, QDoubleSpinBox, QProgressBar, QTextEdit,
    QScrollArea, QGridLayout, QGroupBox, QCheckBox, QSlider, QDialog,
    QDialogButtonBox, QMessageBox, QSplitter, QStatusBar, QMenuBar,
    QMenu
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QPixmap, QAction, QFont, QColor, QPalette

from app.modules.data_cleaner import DataCleaner
from app.modules.preprocessor import ImagePreprocessor
from app.modules.trainer import ModelTrainer
from app.modules.recognizer import ImageRecognizer
from app.modules.data_processor import DataProcessor


class ClickableLabel(QLabel):
    clicked = pyqtSignal()
    
    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("岩心图像识别系统 - RockCoreImage")
        self.setMinimumSize(1200, 700)
        self.resize(1400, 900)
        
        self.current_page = 0
        self.image_paths = []
        self.current_category = None
        self.categories = []
        self.model_path = ""
        self.train_history = {
            'train_loss': [],
            'train_acc': [],
            'val_loss': [],
            'val_acc': []
        }
        
        self.data_cleaner = DataCleaner()
        self.preprocessor = ImagePreprocessor()
        self.trainer = ModelTrainer()
        self.recognizer = ImageRecognizer()
        self.data_processor = DataProcessor()
        
        self.setup_ui()
        self.apply_stylesheet()
    
    def setup_ui(self):
        self.setup_menu_bar()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)
        
        self.content_widget = QStackedWidget()
        main_layout.addWidget(self.content_widget, 1)
        
        self.content_widget.addWidget(self.create_home_page())
        self.content_widget.addWidget(self.create_data_page())
        self.content_widget.addWidget(self.create_process_page())
        self.content_widget.addWidget(self.create_preprocess_page())
        self.content_widget.addWidget(self.create_training_page())
        self.content_widget.addWidget(self.create_recognition_page())
        
        central_widget.setLayout(main_layout)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
    
    def setup_menu_bar(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("文件")
        
        open_action = QAction("打开数据集", self)
        open_action.triggered.connect(lambda: self.navigate_to_page(1))
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        help_menu = menubar.addMenu("帮助")
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_sidebar(self):
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
        
        self.nav_buttons = []
        for text, page_idx in buttons:
            btn = QPushButton(text)
            btn.setFixedHeight(45)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, idx=page_idx: self.navigate_to_page(idx))
            self.nav_buttons.append(btn)
            layout.addWidget(btn)
        
        layout.addStretch()
        
        sidebar.setLayout(layout)
        self.update_nav_buttons()
        
        return sidebar
    
    def update_nav_buttons(self):
        for i, btn in enumerate(self.nav_buttons):
            if i == self.current_page:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        border: none;
                        border-left: 4px solid white;
                        font-size: 14px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: #B0BEC5;
                        border: none;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #2D5A87;
                        color: white;
                    }
                """)
    
    def navigate_to_page(self, page_idx):
        self.current_page = page_idx
        self.content_widget.setCurrentIndex(page_idx)
        self.update_nav_buttons()
        self.status_bar.showMessage(f"当前: {self.nav_buttons[page_idx].text()}")
    
    def create_home_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        title = QLabel("欢迎使用岩心图像识别系统")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #1E3A5F;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        layout.addSpacing(30)
        
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
        btn1.clicked.connect(lambda: self.navigate_to_page(1))
        quick_layout.addWidget(btn1)
        
        btn2 = QPushButton("开始训练")
        btn2.clicked.connect(lambda: self.navigate_to_page(4))
        quick_layout.addWidget(btn2)
        
        btn3 = QPushButton("图像识别")
        btn3.clicked.connect(lambda: self.navigate_to_page(5))
        quick_layout.addWidget(btn3)
        
        quick_start.setLayout(quick_layout)
        layout.addWidget(quick_start)
        
        page.setLayout(layout)
        return page
    
    def create_data_page(self):
        page = QWidget()
        layout = QHBoxLayout()
        
        left_panel = QFrame()
        left_panel.setFixedWidth(250)
        left_layout = QVBoxLayout()
        
        import_btn = QPushButton("导入图像")
        import_btn.clicked.connect(self.import_images)
        left_layout.addWidget(import_btn)
        
        import_folder_btn = QPushButton("导入文件夹")
        import_folder_btn.clicked.connect(self.import_folder)
        left_layout.addWidget(import_folder_btn)
        
        left_layout.addSpacing(10)
        
        clean_btn = QPushButton("数据清洗")
        clean_btn.clicked.connect(self.start_data_cleaning)
        left_layout.addWidget(clean_btn)
        
        left_layout.addSpacing(10)
        
        self.category_list = QListWidget()
        self.category_list.itemClicked.connect(self.on_category_clicked)
        left_layout.addWidget(QLabel("类别列表:"))
        left_layout.addWidget(self.category_list)
        
        left_panel.setLayout(left_layout)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        self.image_grid = QScrollArea()
        self.image_grid.setWidgetResizable(True)
        self.image_grid.setStyleSheet("border: none;")
        
        self.image_grid_content = QWidget()
        self.image_grid_layout = QGridLayout()
        self.image_grid_content.setLayout(self.image_grid_layout)
        self.image_grid.setWidget(self.image_grid_content)
        
        right_layout.addWidget(self.image_grid)
        
        self.data_progress = QProgressBar()
        self.data_progress.setVisible(False)
        right_layout.addWidget(self.data_progress)
        
        right_panel.setLayout(right_layout)
        
        layout.addWidget(left_panel)
        layout.addWidget(right_panel, 1)
        
        page.setLayout(layout)
        return page
    
    def create_process_page(self):
        page = QWidget()
        layout = QHBoxLayout()
        
        left_panel = QFrame()
        left_panel.setFixedWidth(300)
        left_layout = QVBoxLayout()
        
        source_group = QGroupBox("数据源")
        source_layout = QVBoxLayout()
        
        select_source_btn = QPushButton("选择数据目录")
        select_source_btn.clicked.connect(self.select_source_directory)
        source_layout.addWidget(select_source_btn)
        
        self.source_path_label = QLabel("未选择")
        self.source_path_label.setStyleSheet("color: #666; font-size: 12px; word-wrap: break-word;")
        source_layout.addWidget(self.source_path_label)
        
        source_group.setLayout(source_layout)
        left_layout.addWidget(source_group)
        
        output_group = QGroupBox("输出目录")
        output_layout = QVBoxLayout()
        
        select_output_btn = QPushButton("选择输出目录")
        select_output_btn.clicked.connect(self.select_output_directory)
        output_layout.addWidget(select_output_btn)
        
        self.output_path_label = QLabel("未选择")
        self.output_path_label.setStyleSheet("color: #666; font-size: 12px; word-wrap: break-word;")
        output_layout.addWidget(self.output_path_label)
        
        output_group.setLayout(output_layout)
        left_layout.addWidget(output_group)
        
        process_btn = QPushButton("开始处理")
        process_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        process_btn.clicked.connect(self.start_data_processing)
        left_layout.addWidget(process_btn)
        
        left_panel.setLayout(left_layout)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        self.process_log = QTextEdit()
        self.process_log.setReadOnly(True)
        right_layout.addWidget(QLabel("处理日志:"))
        right_layout.addWidget(self.process_log)
        
        self.process_progress = QProgressBar()
        right_layout.addWidget(self.process_progress)
        
        right_panel.setLayout(right_layout)
        
        layout.addWidget(left_panel)
        layout.addWidget(right_panel, 1)
        
        page.setLayout(layout)
        return page
    
    def select_source_directory(self):
        folder = QFileDialog.getExistingDirectory(self, "选择数据目录")
        if folder:
            self.source_directory = folder
            self.source_path_label.setText(folder)
            self.process_log.append(f"已选择数据源: {folder}")
    
    def select_output_directory(self):
        folder = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if folder:
            self.output_directory = folder
            self.output_path_label.setText(folder)
            self.process_log.append(f"已选择输出目录: {folder}")
    
    def start_data_processing(self):
        if not hasattr(self, 'source_directory') or not self.source_directory:
            QMessageBox.warning(self, "警告", "请先选择数据源目录")
            return
        
        if not hasattr(self, 'output_directory') or not self.output_directory:
            QMessageBox.warning(self, "警告", "请先选择输出目录")
            return
        
        self.process_log.append("开始处理数据...")
        
        self.data_processor.progress_updated.connect(self.on_processing_progress)
        self.data_processor.processing_finished.connect(self.on_processing_finished)
        self.data_processor.error_occurred.connect(self.on_processing_error)
        
        self.data_processor.process(self.source_directory, self.output_directory)
    
    def on_processing_progress(self, value, message):
        self.process_progress.setValue(value)
        self.process_log.append(message)
        self.status_bar.showMessage(message)
    
    def on_processing_finished(self, output_file, stats):
        self.process_log.append(f"处理完成!")
        self.process_log.append(f"共处理图片: {stats['total_images']} 张")
        self.process_log.append(f"项目数量: {stats['total_projects']} 个")
        self.process_log.append(f"描述文件: {output_file}")
        
        QMessageBox.information(self, "处理完成", 
            f"共处理图片: {stats['total_images']} 张\n"
            f"项目数量: {stats['total_projects']} 个\n"
            f"描述文件: {output_file}")
    
    def on_processing_error(self, error_msg):
        self.process_log.append(f"错误: {error_msg}")
    
    def create_preprocess_page(self):
        page = QWidget()
        layout = QHBoxLayout()
        
        left_panel = QFrame()
        left_panel.setFixedWidth(300)
        left_layout = QVBoxLayout()
        
        size_group = QGroupBox("图像尺寸")
        size_layout = QVBoxLayout()
        self.size_combo = QComboBox()
        self.size_combo.addItems(["224x224", "256x256", "512x512", "自定义"])
        size_layout.addWidget(QLabel("目标尺寸:"))
        self.size_combo.addItem("224x224")
        self.size_combo.addItem("256x256")
        self.size_combo.addItem("512x512")
        size_layout.addWidget(self.size_combo)
        size_group.setLayout(size_layout)
        left_layout.addWidget(size_group)
        
        augment_group = QGroupBox("数据增强")
        augment_layout = QVBoxLayout()
        self.augment_flip = QCheckBox("随机翻转")
        self.augment_flip.setChecked(True)
        augment_layout.addWidget(self.augment_flip)
        
        self.augment_rotate = QCheckBox("随机旋转")
        self.augment_rotate.setChecked(True)
        augment_layout.addWidget(self.augment_rotate)
        
        self.augment_color = QCheckBox("颜色抖动")
        self.augment_color.setChecked(True)
        augment_layout.addWidget(self.augment_color)
        
        self.augment_noise = QCheckBox("添加噪声")
        augment_layout.addWidget(self.augment_noise)
        augment_group.setLayout(augment_layout)
        left_layout.addWidget(augment_group)
        
        preview_btn = QPushButton("预览增强效果")
        preview_btn.clicked.connect(self.preview_augmentation)
        left_layout.addWidget(preview_btn)
        
        apply_btn = QPushButton("应用预处理")
        apply_btn.clicked.connect(self.apply_preprocessing)
        left_layout.addWidget(apply_btn)
        
        left_panel.setLayout(left_layout)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        self.preview_label = QLabel("预览区域")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("""
            background-color: #f0f0f0;
            border: 2px dashed #ccc;
            min-height: 400px;
        """)
        right_layout.addWidget(self.preview_label)
        
        page.setLayout(layout)
        return page
    
    def create_training_page(self):
        page = QWidget()
        layout = QHBoxLayout()
        
        left_panel = QFrame()
        left_panel.setFixedWidth(300)
        left_layout = QVBoxLayout()
        
        data_group = QGroupBox("数据集")
        data_layout = QVBoxLayout()
        
        select_data_btn = QPushButton("选择数据集")
        select_data_btn.clicked.connect(self.select_training_data)
        data_layout.addWidget(select_data_btn)
        
        self.data_path_label = QLabel("未选择数据集")
        self.data_path_label.setStyleSheet("color: #666; font-size: 12px;")
        data_layout.addWidget(self.data_path_label)
        
        data_group.setLayout(data_layout)
        left_layout.addWidget(data_group)
        
        model_group = QGroupBox("模型设置")
        model_layout = QVBoxLayout()
        
        model_layout.addWidget(QLabel("预训练模型:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["ResNet18", "ResNet50", "VGG16", "EfficientNet-B0"])
        model_layout.addWidget(self.model_combo)
        
        model_layout.addWidget(QLabel("学习率:"))
        self.lr_spin = QDoubleSpinBox()
        self.lr_spin.setRange(0.00001, 0.1)
        self.lr_spin.setValue(0.001)
        self.lr_spin.setDecimals(5)
        model_layout.addWidget(self.lr_spin)
        
        model_layout.addWidget(QLabel("批次大小:"))
        self.batch_spin = QSpinBox()
        self.batch_spin.setRange(8, 128)
        self.batch_spin.setValue(32)
        model_layout.addWidget(self.batch_spin)
        
        model_layout.addWidget(QLabel("训练轮数:"))
        self.epoch_spin = QSpinBox()
        self.epoch_spin.setRange(1, 200)
        self.epoch_spin.setValue(20)
        model_layout.addWidget(self.epoch_spin)
        
        model_group.setLayout(model_layout)
        left_layout.addWidget(model_group)
        
        train_btn = QPushButton("开始训练")
        train_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        train_btn.clicked.connect(self.start_training)
        left_layout.addWidget(train_btn)
        
        left_panel.setLayout(left_layout)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        self.training_log = QTextEdit()
        self.training_log.setReadOnly(True)
        self.training_log.setMaximumHeight(150)
        right_layout.addWidget(QLabel("训练日志:"))
        right_layout.addWidget(self.training_log)
        
        self.loss_plot = QLabel("训练曲线区域")
        self.loss_plot.setStyleSheet("background-color: white; border: 1px solid #ddd;")
        self.loss_plot.setMinimumHeight(250)
        right_layout.addWidget(QLabel("损失曲线:"))
        right_layout.addWidget(self.loss_plot)
        
        self.train_progress = QProgressBar()
        right_layout.addWidget(self.train_progress)
        
        page.setLayout(layout)
        return page
    
    def create_recognition_page(self):
        page = QWidget()
        layout = QHBoxLayout()
        
        left_panel = QFrame()
        left_panel.setFixedWidth(300)
        left_layout = QVBoxLayout()
        
        model_group = QGroupBox("模型")
        model_layout = QVBoxLayout()
        
        load_model_btn = QPushButton("加载模型")
        load_model_btn.clicked.connect(self.load_model_for_recognition)
        model_layout.addWidget(load_model_btn)
        
        self.model_label = QLabel("未加载模型")
        self.model_label.setStyleSheet("color: #666; font-size: 12px;")
        model_layout.addWidget(self.model_label)
        
        model_group.setLayout(model_layout)
        left_layout.addWidget(model_group)
        
        input_group = QGroupBox("输入")
        input_layout = QVBoxLayout()
        
        single_btn = QPushButton("单图识别")
        single_btn.clicked.connect(self.recognize_single_image)
        input_layout.addWidget(single_btn)
        
        batch_btn = QPushButton("批量识别")
        batch_btn.clicked.connect(self.recognize_batch_images)
        input_layout.addWidget(batch_btn)
        
        input_group.setLayout(input_layout)
        left_layout.addWidget(input_group)
        
        export_group = QGroupBox("导出")
        export_layout = QVBoxLayout()
        
        export_csv_btn = QPushButton("导出为CSV")
        export_csv_btn.clicked.connect(lambda: self.export_recognition_results('csv'))
        export_layout.addWidget(export_csv_btn)
        
        export_json_btn = QPushButton("导出为JSON")
        export_json_btn.clicked.connect(lambda: self.export_recognition_results('json'))
        export_layout.addWidget(export_json_btn)
        
        export_group.setLayout(export_layout)
        left_layout.addWidget(export_group)
        
        left_panel.setLayout(left_layout)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        result_group = QGroupBox("识别结果")
        result_layout = QVBoxLayout()
        
        self.result_image_label = QLabel("图像预览")
        self.result_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_image_label.setStyleSheet("""
            background-color: #f0f0f0;
            border: 1px solid #ddd;
            min-height: 300px;
        """)
        result_layout.addWidget(self.result_image_label)
        
        self.result_label = QLabel("预测结果: --")
        self.result_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #1E3A5F;")
        result_layout.addWidget(self.result_label)
        
        self.confidence_label = QLabel("置信度: --")
        self.confidence_label.setStyleSheet("font-size: 14px; color: #666;")
        result_layout.addWidget(self.confidence_label)
        
        result_group.setLayout(result_layout)
        right_layout.addWidget(result_group)
        
        self.recognition_results = QTextEdit()
        self.recognition_results.setReadOnly(True)
        self.recognition_results.setMaximumHeight(150)
        right_layout.addWidget(QLabel("识别详情:"))
        right_layout.addWidget(self.recognition_results)
        
        page.setLayout(layout)
        return page
    
    def apply_stylesheet(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F5F7FA;
            }
            QPushButton {
                background-color: #1E3A5F;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2D5A87;
            }
            QPushButton:pressed {
                background-color: #152d4a;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QListWidget {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                background-color: white;
            }
            QListWidget::item:selected {
                background-color: #1E3A5F;
                color: white;
            }
            QProgressBar {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
            QTextEdit {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                background-color: white;
            }
            QComboBox {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }
            QSpinBox, QDoubleSpinBox {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }
            QCheckBox {
                spacing: 8px;
            }
            QLabel {
                color: #333;
            }
        """)
    
    def show_about(self):
        QMessageBox.about(self, "关于", 
            "岩心图像识别系统 RockCoreImage\n\n"
            "基于PyQt6和PyTorch开发的岩心图像分类识别系统\n\n"
            "支持预训练模型: ResNet, VGG, EfficientNet\n\n"
            "版本: 1.0.0"
        )
    
    def import_images(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择图像", "", "图像文件 (*.jpg *.jpeg *.png *.bmp)"
        )
        if files:
            self.image_paths.extend(files)
            self.status_bar.showMessage(f"已导入 {len(files)} 张图像")
    
    def import_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder:
            self.current_category = os.path.basename(folder)
            if self.current_category not in self.categories:
                self.categories.append(self.current_category)
                self.category_list.addItem(self.current_category)
            
            for root, _, files in os.walk(folder):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                        self.image_paths.append(os.path.join(root, file))
            
            self.display_images()
            self.status_bar.showMessage(f"已导入文件夹: {folder}")
    
    def display_images(self):
        while self.image_grid_layout.count():
            item = self.image_grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        cols = 4
        for i, img_path in enumerate(self.image_paths[:20]):
            row = i // cols
            col = i % cols
            
            frame = QFrame()
            frame.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 4px;")
            layout = QVBoxLayout()
            
            label = QLabel()
            pixmap = QPixmap(img_path)
            if pixmap.width() > 150:
                pixmap = pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio)
            label.setPixmap(pixmap)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
            
            name_label = QLabel(os.path.basename(img_path))
            name_label.setStyleSheet("font-size: 10px;")
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            name_label.setWordWrap(True)
            layout.addWidget(name_label)
            
            frame.setLayout(layout)
            self.image_grid_layout.addWidget(frame, row, col)
    
    def on_category_clicked(self, item):
        self.current_category = item.text()
    
    def start_data_cleaning(self):
        if not self.image_paths:
            QMessageBox.warning(self, "警告", "请先导入图像")
            return
        
        self.data_progress.setVisible(True)
        self.data_progress.setValue(0)
        
        blurry, corrupted, small = self.data_cleaner.clean_dataset(self.image_paths)
        
        self.data_progress.setValue(100)
        self.data_progress.setVisible(False)
        
        result = f"清洗完成:\n"
        result += f"- 模糊图像: {len(blurry)} 张\n"
        result += f"- 损坏图像: {len(corrupted)} 张\n"
        result += f"- 过小图像: {len(small)} 张"
        
        QMessageBox.information(self, "数据清洗", result)
    
    def preview_augmentation(self):
        if not self.image_paths:
            QMessageBox.warning(self, "警告", "请先导入图像")
            return
        
        img_path = self.image_paths[0]
        augmented = self.preprocessor.augment_batch(img_path, 4)
        
        if augmented:
            first_aug = augmented[0]
            pixmap = QPixmap.fromImage(
                first_aug.convert("RGBA").toqimage()
            )
            self.preview_label.setPixmap(pixmap.scaled(
                400, 400, Qt.AspectRatioMode.KeepAspectRatio
            ))
    
    def apply_preprocessing(self):
        QMessageBox.information(self, "提示", "预处理设置已应用")
    
    def select_training_data(self):
        folder = QFileDialog.getExistingDirectory(self, "选择数据集文件夹")
        if folder:
            self.training_data_dir = folder
            self.data_path_label.setText(folder)
    
    def start_training(self):
        if not hasattr(self, 'training_data_dir'):
            QMessageBox.warning(self, "警告", "请先选择数据集")
            return
        
        model_name = self.model_combo.currentText().lower().replace('-', '_').replace(' ', '_')
        batch_size = self.batch_spin.value()
        num_epochs = self.epoch_spin.value()
        learning_rate = self.lr_spin.value()
        
        self.training_log.append("正在加载数据...")
        
        try:
            train_count, val_count, num_classes = self.trainer.load_data(
                self.training_data_dir, batch_size=batch_size
            )
            self.training_log.append(f"训练集: {train_count}, 验证集: {val_count}, 类别数: {num_classes}")
            
            self.training_log.append(f"正在创建 {model_name} 模型...")
            self.trainer.create_model(model_name, num_classes)
            
            save_path = QFileDialog.getSaveFileName(
                self, "保存模型", "", "PyTorch模型 (*.pth)"
            )[0]
            
            if not save_path:
                return
            
            self.training_log.append("开始训练...")
            
            self.train_thread = self.trainer.start_training(
                num_epochs, learning_rate, save_path
            )
            
            self.train_thread.progress_updated.connect(self.on_training_progress)
            self.train_thread.epoch_finished.connect(self.on_epoch_finished)
            self.train_thread.training_finished.connect(self.on_training_finished)
            
            self.train_thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"训练失败: {str(e)}")
            self.training_log.append(f"错误: {str(e)}")
    
    def on_training_progress(self, value, message):
        self.train_progress.setValue(value)
        self.status_bar.showMessage(message)
    
    def on_epoch_finished(self, epoch, train_loss, train_acc, val_loss, val_acc):
        log = f"Epoch {epoch}: 训练损失={train_loss:.4f}, 训练准确率={train_acc:.2f}%, "
        log += f"验证损失={val_loss:.4f}, 验证准确率={val_acc:.2f}%"
        self.training_log.append(log)
        
        self.train_history['train_loss'].append(train_loss)
        self.train_history['train_acc'].append(train_acc)
        self.train_history['val_loss'].append(val_loss)
        self.train_history['val_acc'].append(val_acc)
    
    def on_training_finished(self, save_path, best_acc):
        self.training_log.append(f"训练完成! 最佳验证准确率: {best_acc:.2f}%")
        self.model_path = save_path
        QMessageBox.information(self, "训练完成", f"模型已保存到: {save_path}\n最佳准确率: {best_acc:.2f}%")
    
    def load_model_for_recognition(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择模型", "", "PyTorch模型 (*.pth)"
        )
        if path:
            try:
                self.recognizer.load_model(path)
                self.model_path = path
                self.model_label.setText(os.path.basename(path))
                self.status_bar.showMessage(f"已加载模型: {path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载模型失败: {str(e)}")
    
    def recognize_single_image(self):
        if not self.model_path:
            QMessageBox.warning(self, "警告", "请先加载模型")
            return
        
        path, _ = QFileDialog.getOpenFileName(
            self, "选择图像", "", "图像文件 (*.jpg *.jpeg *.png *.bmp)"
        )
        if path:
            try:
                result = self.recognizer.recognize_single(path)
                
                pixmap = QPixmap(path)
                self.result_image_label.setPixmap(pixmap.scaled(
                    400, 300, Qt.AspectRatioMode.KeepAspectRatio
                ))
                
                self.result_label.setText(f"预测结果: {result['predicted_class']}")
                self.confidence_label.setText(f"置信度: {result['confidence']:.2f}%")
                
                details = json.dumps(result['all_probabilities'], indent=2, ensure_ascii=False)
                self.recognition_results.setText(details)
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"识别失败: {str(e)}")
    
    def recognize_batch_images(self):
        if not self.model_path:
            QMessageBox.warning(self, "警告", "请先加载模型")
            return
        
        folder = QFileDialog.getExistingDirectory(self, "选择图像文件夹")
        if not folder:
            return
        
        image_files = []
        for f in os.listdir(folder):
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                image_files.append(os.path.join(folder, f))
        
        if not image_files:
            QMessageBox.warning(self, "警告", "文件夹中没有图像")
            return
        
        results = self.recognizer.recognize_batch(image_files)
        self.recognition_results.setText(
            json.dumps(results, indent=2, ensure_ascii=False)
        )
        
        QMessageBox.information(self, "完成", f"已完成 {len(results)} 张图像的识别")
    
    def export_recognition_results(self, format_type):
        if not self.recognition_results.toPlainText():
            QMessageBox.warning(self, "警告", "没有可导出的结果")
            return
        
        path, _ = QFileDialog.getSaveFileName(
            self, "保存结果", "", 
            f"{format_type.upper()}文件 (*.{format_type})" if format_type == "csv" else "JSON文件 (*.json)"
        )
        
        if path:
            QMessageBox.information(self, "完成", f"结果已导出到: {path}")
