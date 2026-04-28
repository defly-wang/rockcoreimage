import os
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QGroupBox, QFrame, QComboBox, QListWidget, QListWidgetItem,
    QFileDialog, QMessageBox, QProgressBar, QGridLayout, QScrollArea,
    QSpinBox, QCheckBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QImage


class PreprocessPage:
    @staticmethod
    def create(main_window):
        page = QWidget()
        layout = QVBoxLayout()
        
        info_panel = QGroupBox("信息")
        info_layout = QVBoxLayout()
        
        main_window.preprocess_status_label = QLabel("等待开始...")
        main_window.preprocess_status_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #1E3A5F;
            padding: 8px;
            background-color: white;
            border: 1px solid #E0E0E0;
            border-radius: 4px;
        """)
        info_layout.addWidget(main_window.preprocess_status_label)
        
        main_window.preprocess_progress = QProgressBar()
        main_window.preprocess_progress.setTextVisible(True)
        main_window.preprocess_progress.setFormat("%p%")
        main_window.preprocess_progress.setVisible(False)
        info_layout.addWidget(main_window.preprocess_progress)
        
        info_panel.setLayout(info_layout)
        layout.addWidget(info_panel)
        
        main_content = QHBoxLayout()
        
        settings_panel = QGroupBox("处理设置")
        settings_panel.setFixedWidth(200)
        settings_layout = QVBoxLayout()
        
        size_group = QGroupBox("图像尺寸")
        size_layout = QVBoxLayout()
        main_window.target_size_combo = QComboBox()
        main_window.target_size_combo.addItems(["224x224", "256x256", "512x512", "自定义"])
        main_window.target_size_combo.currentTextChanged.connect(
            lambda: PreprocessPage.on_size_changed(main_window)
        )
        size_layout.addWidget(main_window.target_size_combo)
        
        main_window.custom_size_layout = QHBoxLayout()
        main_window.custom_width = QSpinBox()
        main_window.custom_width.setRange(64, 1024)
        main_window.custom_width.setValue(224)
        main_window.custom_width.setVisible(False)
        main_window.custom_size_layout.addWidget(QLabel("宽:"))
        main_window.custom_size_layout.addWidget(main_window.custom_width)
        
        main_window.custom_height = QSpinBox()
        main_window.custom_height.setRange(64, 1024)
        main_window.custom_height.setValue(224)
        main_window.custom_height.setVisible(False)
        main_window.custom_size_layout.addWidget(QLabel("高:"))
        main_window.custom_size_layout.addWidget(main_window.custom_height)
        size_layout.addLayout(main_window.custom_size_layout)
        size_group.setLayout(size_layout)
        settings_layout.addWidget(size_group)
        
        aug_group = QGroupBox("数据增强选项")
        aug_layout = QVBoxLayout()
        
        main_window.aug_brightness = QCheckBox("亮度增强")
        main_window.aug_brightness.setChecked(True)
        aug_layout.addWidget(main_window.aug_brightness)
        
        main_window.aug_contrast = QCheckBox("对比度增强")
        main_window.aug_contrast.setChecked(True)
        aug_layout.addWidget(main_window.aug_contrast)
        
        main_window.aug_saturation = QCheckBox("饱和度增强")
        main_window.aug_saturation.setChecked(True)
        aug_layout.addWidget(main_window.aug_saturation)
        
        main_window.aug_flip = QCheckBox("水平翻转")
        main_window.aug_flip.setChecked(True)
        aug_layout.addWidget(main_window.aug_flip)
        
        main_window.aug_rotation = QCheckBox("随机旋转")
        main_window.aug_rotation.setChecked(True)
        aug_layout.addWidget(main_window.aug_rotation)
        
        main_window.aug_noise = QCheckBox("添加高斯噪声")
        aug_layout.addWidget(main_window.aug_noise)
        
        main_window.aug_blur = QCheckBox("高斯模糊")
        aug_layout.addWidget(main_window.aug_blur)
        
        aug_group.setLayout(aug_layout)
        settings_layout.addWidget(aug_group)
        
        settings_layout.addStretch()
        settings_panel.setLayout(settings_layout)
        main_content.addWidget(settings_panel)
        
        list_panel = QGroupBox("图像列表")
        list_panel.setMinimumWidth(400)
        list_layout = QVBoxLayout()
        
        scroll_area_list = QScrollArea()
        scroll_area_list.setWidgetResizable(True)
        scroll_area_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        main_window.image_list_widget = QWidget()
        main_window.image_grid = QGridLayout()
        main_window.image_list_widget.setLayout(main_window.image_grid)
        
        scroll_area_list.setWidget(main_window.image_list_widget)
        list_layout.addWidget(scroll_area_list)
        
        pagination_layout = QHBoxLayout()
        main_window.prev_page_btn = QPushButton("<")
        main_window.prev_page_btn.setFixedWidth(40)
        main_window.prev_page_btn.clicked.connect(lambda: PreprocessPage.prev_page(main_window))
        pagination_layout.addWidget(main_window.prev_page_btn)
        
        main_window.page_label = QLabel("0/0")
        main_window.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pagination_layout.addWidget(main_window.page_label)
        
        main_window.next_page_btn = QPushButton(">")
        main_window.next_page_btn.setFixedWidth(40)
        main_window.next_page_btn.clicked.connect(lambda: PreprocessPage.next_page(main_window))
        pagination_layout.addWidget(main_window.next_page_btn)
        
        list_layout.addLayout(pagination_layout)
        list_panel.setLayout(list_layout)
        main_content.addWidget(list_panel)
        
        preview_panel = QGroupBox("处理后预览")
        preview_layout = QVBoxLayout()
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        main_window.preview_container = QWidget()
        main_window.preview_grid = QGridLayout()
        main_window.preview_container.setLayout(main_window.preview_grid)
        
        scroll_area.setWidget(main_window.preview_container)
        preview_layout.addWidget(scroll_area)
        
        preview_panel.setLayout(preview_layout)
        main_content.addWidget(preview_panel, 1)
        
        layout.addLayout(main_content)
        
        button_panel = QGroupBox("操作")
        button_layout = QHBoxLayout()
        
        select_input_btn = QPushButton("选择输入目录")
        select_input_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-size: 13px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        select_input_btn.clicked.connect(lambda: PreprocessPage.select_input_dir(main_window))
        button_layout.addWidget(select_input_btn)
        
        main_window.input_dir_label = QLabel("未选择")
        main_window.input_dir_label.setStyleSheet("color: #666; font-size: 12px; max-width: 150px;")
        main_window.input_dir_label.setWordWrap(True)
        button_layout.addWidget(main_window.input_dir_label)
        
        button_layout.addSpacing(80)
        
        select_output_btn = QPushButton("选择输出目录")
        select_output_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                font-size: 13px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        select_output_btn.clicked.connect(lambda: PreprocessPage.select_output_dir(main_window))
        button_layout.addWidget(select_output_btn)
        
        main_window.output_dir_label = QLabel("未选择")
        main_window.output_dir_label.setStyleSheet("color: #666; font-size: 12px; max-width: 150px;")
        main_window.output_dir_label.setWordWrap(True)
        button_layout.addWidget(main_window.output_dir_label)
        
        button_layout.addStretch()
        
        start_btn = QPushButton("开始处理")
        start_btn.setStyleSheet("""
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
        start_btn.clicked.connect(lambda: PreprocessPage.start_processing(main_window))
        button_layout.addWidget(start_btn)
        
        button_panel.setLayout(button_layout)
        layout.addWidget(button_panel)
        
        page.setLayout(layout)
        
        main_window.input_dir = ""
        main_window.output_dir = ""
        main_window.image_files = []
        main_window.current_page_idx = 0
        main_window.images_per_page = 12
        main_window.current_preview_image = None
        main_window.selected_image_index = -1
        
        return page
    
    @staticmethod
    def select_input_dir(main_window):
        folder = QFileDialog.getExistingDirectory(main_window, "选择输入目录")
        if folder:
            images_dir = os.path.join(folder, 'images')
            if not os.path.exists(images_dir):
                QMessageBox.warning(main_window, "警告", 
                    f"所选目录中没有images子目录:\n{images_dir}")
                return
            
            main_window.input_dir = folder
            short_name = os.path.basename(folder)
            main_window.input_dir_label.setText(short_name)
            main_window.input_dir_label.setToolTip(folder)
            main_window.image_files = []
            
            for f in os.listdir(images_dir):
                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                    main_window.image_files.append(os.path.join(images_dir, f))
            
            main_window.current_page_idx = 0
            main_window.selected_image_index = -1
            PreprocessPage.update_image_grid(main_window)
            main_window.status_bar.showMessage(f"已加载 {len(main_window.image_files)} 张图像")
            main_window.preprocess_status_label.setText(f"已加载 {len(main_window.image_files)} 张图像")
    
    @staticmethod
    def select_output_dir(main_window):
        folder = QFileDialog.getExistingDirectory(main_window, "选择输出目录")
        if folder:
            main_window.output_dir = folder
            short_name = os.path.basename(folder)
            main_window.output_dir_label.setText(short_name)
            main_window.output_dir_label.setToolTip(folder)
            main_window.status_bar.showMessage(f"输出目录: {folder}")
    
    @staticmethod
    def update_image_grid(main_window):
        while main_window.image_grid.count():
            item = main_window.image_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        start_idx = main_window.current_page_idx * main_window.images_per_page
        end_idx = min(start_idx + main_window.images_per_page, len(main_window.image_files))
        
        cols = 3
        for i, img_idx in enumerate(range(start_idx, end_idx)):
            img_path = main_window.image_files[img_idx]
            row = i // cols
            col = i % cols
            
            frame = QFrame()
            frame.setFixedWidth(110)
            frame.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 4px; padding: 5px;")
            if img_idx == main_window.selected_image_index:
                frame.setStyleSheet("background-color: #e3f2fd; border: 2px solid #2196F3; border-radius: 4px; padding: 5px;")
            
            layout = QVBoxLayout()
            
            try:
                pixmap = QPixmap(img_path)
                if pixmap.width() > 90:
                    pixmap = pixmap.scaled(90, 90, Qt.AspectRatioMode.KeepAspectRatio)
                
                label = QLabel()
                label.setPixmap(pixmap)
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(label)
            except:
                label = QLabel("无法加载")
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(label)
            
            name_label = QLabel(os.path.basename(img_path))
            name_label.setStyleSheet("font-size: 10px;")
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            name_label.setWordWrap(True)
            name_label.setMaximumWidth(100)
            layout.addWidget(name_label)
            
            frame.setLayout(layout)
            
            frame.mousePressEvent = lambda event, idx=img_idx: PreprocessPage.on_image_clicked(main_window, idx)
            
            main_window.image_grid.addWidget(frame, row, col)
        
        total_pages = (len(main_window.image_files) + main_window.images_per_page - 1) // main_window.images_per_page
        current_page = main_window.current_page_idx + 1
        main_window.page_label.setText(f"{current_page}/{total_pages}")
        
        main_window.prev_page_btn.setEnabled(main_window.current_page_idx > 0)
        main_window.next_page_btn.setEnabled(end_idx < len(main_window.image_files))
    
    @staticmethod
    def on_image_clicked(main_window, img_idx):
        main_window.selected_image_index = img_idx
        PreprocessPage.update_image_grid(main_window)
        
        img_path = main_window.image_files[img_idx]
        main_window.current_preview_image = img_path
        PreprocessPage.update_preview(main_window, img_path)
    
    @staticmethod
    def prev_page(main_window):
        if main_window.current_page_idx > 0:
            main_window.current_page_idx -= 1
            main_window.selected_image_index = -1
            PreprocessPage.update_image_grid(main_window)
    
    @staticmethod
    def next_page(main_window):
        total_pages = (len(main_window.image_files) + main_window.images_per_page - 1) // main_window.images_per_page
        if main_window.current_page_idx < total_pages - 1:
            main_window.current_page_idx += 1
            main_window.selected_image_index = -1
            PreprocessPage.update_image_grid(main_window)
    
    @staticmethod
    def update_preview(main_window, img_path):
        while main_window.preview_grid.count():
            item = main_window.preview_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        target_size = PreprocessPage.get_target_size(main_window)
        
        try:
            from app.modules.preprocessor import ImagePreprocessor
            preprocessor = ImagePreprocessor()
            
            split_images = preprocessor.split_image(img_path, target_size)
            
            augmented_images = []
            for split_img in split_images:
                augmented_images.append(split_img)
                
                if PreprocessPage.should_augment(main_window):
                    augmented = preprocessor.augment_image_with_options(split_img, 
                        brightness=main_window.aug_brightness.isChecked(),
                        contrast=main_window.aug_contrast.isChecked(),
                        saturation=main_window.aug_saturation.isChecked(),
                        flip=main_window.aug_flip.isChecked(),
                        rotation=main_window.aug_rotation.isChecked(),
                        noise=main_window.aug_noise.isChecked(),
                        blur=main_window.aug_blur.isChecked()
                    )
                    augmented_images.extend(augmented)
            
            cols = 4
            for i, img in enumerate(augmented_images):
                row = i // cols
                col = i % cols
                
                frame = QFrame()
                frame.setFixedWidth(130)
                frame.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 4px;")
                layout = QVBoxLayout()
                
                img_rgb = np.array(img)
                height, width = img_rgb.shape[:2]
                qimg = QImage(img_rgb.data, width, height, 3 * width, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(qimg)
                
                if pixmap.width() > 120:
                    pixmap = pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio)
                
                label = QLabel()
                label.setPixmap(pixmap)
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(label)
                
                name_label = QLabel(f"切片{i}")
                name_label.setStyleSheet("font-size: 10px;")
                name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                name_label.setWordWrap(True)
                name_label.setMaximumWidth(120)
                layout.addWidget(name_label)
                
                frame.setLayout(layout)
                main_window.preview_grid.addWidget(frame, row, col)
        
        except Exception as e:
            error_label = QLabel(f"预览失败: {str(e)}")
            error_label.setStyleSheet("color: red;")
            main_window.preview_grid.addWidget(error_label, 0, 0)
    
    @staticmethod
    def should_augment(main_window):
        return (main_window.aug_brightness.isChecked() or 
                main_window.aug_contrast.isChecked() or 
                main_window.aug_saturation.isChecked() or 
                main_window.aug_flip.isChecked() or 
                main_window.aug_rotation.isChecked() or 
                main_window.aug_noise.isChecked() or 
                main_window.aug_blur.isChecked())
    
    @staticmethod
    def get_target_size(main_window):
        text = main_window.target_size_combo.currentText()
        if text == "224x224":
            return (224, 224)
        elif text == "256x256":
            return (256, 256)
        elif text == "512x512":
            return (512, 512)
        else:
            return (main_window.custom_width.value(), main_window.custom_height.value())
    
    @staticmethod
    def on_size_changed(main_window):
        is_custom = main_window.target_size_combo.currentText() == "自定义"
        main_window.custom_width.setVisible(is_custom)
        main_window.custom_height.setVisible(is_custom)
    
    @staticmethod
    def start_processing(main_window):
        if not main_window.input_dir:
            QMessageBox.warning(main_window, "警告", "请先选择输入目录")
            return
        
        if not main_window.output_dir:
            QMessageBox.warning(main_window, "警告", "请先选择输出目录")
            return
        
        target_size = PreprocessPage.get_target_size(main_window)
        
        try:
            from app.modules.preprocessor import ImagePreprocessor
            preprocessor = ImagePreprocessor()
            
            main_window.preprocess_progress.setVisible(True)
            main_window.preprocess_progress.setValue(0)
            main_window.preprocess_status_label.setText("正在处理...")
            
            def progress_callback(value, message):
                main_window.preprocess_progress.setValue(value)
                main_window.status_bar.showMessage(message)
                main_window.preprocess_status_label.setText(message)
            
            total_processed, total_images = preprocessor.process_and_save_with_options(
                main_window.input_dir, main_window.output_dir, target_size,
                brightness=main_window.aug_brightness.isChecked(),
                contrast=main_window.aug_contrast.isChecked(),
                saturation=main_window.aug_saturation.isChecked(),
                flip=main_window.aug_flip.isChecked(),
                rotation=main_window.aug_rotation.isChecked(),
                noise=main_window.aug_noise.isChecked(),
                blur=main_window.aug_blur.isChecked(),
                progress_callback=progress_callback
            )
            
            main_window.preprocess_progress.setValue(100)
            main_window.preprocess_status_label.setText(f"处理完成 - 共 {total_processed} 张图像")
            
            QMessageBox.information(main_window, "完成", 
                f"处理完成!\n\n"
                f"输入图像: {total_images} 张\n"
                f"输出图像: {total_processed} 张\n"
                f"保存位置: {os.path.join(main_window.output_dir, 'images')}")
            
            main_window.status_bar.showMessage(f"处理完成: {total_processed} 张图像")
        
        except Exception as e:
            main_window.preprocess_status_label.setText(f"错误: {str(e)}")
            QMessageBox.critical(main_window, "错误", f"处理失败: {str(e)}")
        finally:
            main_window.preprocess_progress.setVisible(False)
