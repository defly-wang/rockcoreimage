from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QGroupBox, QFrame, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit, QProgressBar
)


class TrainingPage:
    @staticmethod
    def create(main_window):
        page = QWidget()
        layout = QVBoxLayout()
        
        main_content = QHBoxLayout()
        
        left_panel = QFrame()
        left_panel.setFixedWidth(300)
        left_layout = QVBoxLayout()
        
        data_group = QGroupBox("数据集")
        data_layout = QVBoxLayout()
        
        select_data_btn = QPushButton("选择数据集")
        select_data_btn.clicked.connect(main_window.select_training_data)
        data_layout.addWidget(select_data_btn)
        
        main_window.data_path_label = QLabel("未选择数据集")
        main_window.data_path_label.setStyleSheet("color: #666; font-size: 12px;")
        data_layout.addWidget(main_window.data_path_label)
        
        data_group.setLayout(data_layout)
        left_layout.addWidget(data_group)
        
        model_group = QGroupBox("模型设置")
        model_layout = QVBoxLayout()
        
        model_layout.addWidget(QLabel("预训练模型:"))
        main_window.model_combo = QComboBox()
        main_window.model_combo.addItems(["ResNet18", "ResNet50", "VGG16", "EfficientNet-B0"])
        model_layout.addWidget(main_window.model_combo)
        
        model_layout.addWidget(QLabel("学习率:"))
        main_window.lr_spin = QDoubleSpinBox()
        main_window.lr_spin.setRange(0.00001, 0.1)
        main_window.lr_spin.setValue(0.001)
        main_window.lr_spin.setDecimals(5)
        model_layout.addWidget(main_window.lr_spin)
        
        model_layout.addWidget(QLabel("批次大小:"))
        main_window.batch_spin = QSpinBox()
        main_window.batch_spin.setRange(8, 128)
        main_window.batch_spin.setValue(32)
        model_layout.addWidget(main_window.batch_spin)
        
        model_layout.addWidget(QLabel("训练轮数:"))
        main_window.epoch_spin = QSpinBox()
        main_window.epoch_spin.setRange(1, 200)
        main_window.epoch_spin.setValue(20)
        model_layout.addWidget(main_window.epoch_spin)
        
        model_group.setLayout(model_layout)
        left_layout.addWidget(model_group)
        
        left_panel.setLayout(left_layout)
        
        main_content.addWidget(left_panel)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        main_window.training_log = QTextEdit()
        main_window.training_log.setReadOnly(True)
        main_window.training_log.setMaximumHeight(150)
        main_window.training_log.setStyleSheet("background-color: white; color: #333333; border: 1px solid #E0E0E0; border-radius: 4px;")
        right_layout.addWidget(QLabel("训练日志:"))
        right_layout.addWidget(main_window.training_log)
        
        main_window.loss_plot = QLabel("训练曲线区域")
        main_window.loss_plot.setStyleSheet("background-color: white; border: 1px solid #ddd;")
        main_window.loss_plot.setMinimumHeight(250)
        right_layout.addWidget(QLabel("损失曲线:"))
        right_layout.addWidget(main_window.loss_plot)
        
        main_window.train_progress = QProgressBar()
        right_layout.addWidget(main_window.train_progress)
        
        right_panel.setLayout(right_layout)
        
        main_content.addWidget(right_panel, 1)
        
        layout.addLayout(main_content)
        
        button_panel = QGroupBox("操作")
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        train_btn = QPushButton("开始训练")
        train_btn.setStyleSheet("""
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
        """)
        train_btn.clicked.connect(main_window.start_training)
        button_layout.addWidget(train_btn)
        
        button_panel.setLayout(button_layout)
        layout.addWidget(button_panel)
        
        page.setLayout(layout)
        return page