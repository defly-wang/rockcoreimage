import os
import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QMenuBar, QMenu, QStatusBar, QFileDialog, QMessageBox, QTableWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction

from app.modules.data_cleaner import DataCleaner
from app.modules.preprocessor import ImagePreprocessor
from app.modules.trainer import ModelTrainer
from app.modules.recognizer import ImageRecognizer
from app.modules.data_processor import DataProcessor

from app.ui.widgets import ClickableLabel
from app.ui.sidebar import Sidebar
from app.ui.home_page import HomePage
from app.ui.data_page import DataPage
from app.ui.process_page import ProcessPage
from app.ui.preprocess_page import PreprocessPage
from app.ui.training_page import TrainingPage
from app.ui.recognition_page import RecognitionPage


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
        
        self.sidebar = Sidebar.create(self)
        main_layout.addWidget(self.sidebar)
        
        self.content_widget = QStackedWidget()
        main_layout.addWidget(self.content_widget, 1)
        
        self.content_widget.addWidget(HomePage.create(self))
        self.content_widget.addWidget(DataPage.create(self))
        self.content_widget.addWidget(ProcessPage.create(self))
        self.content_widget.addWidget(PreprocessPage.create(self))
        self.content_widget.addWidget(TrainingPage.create(self))
        self.content_widget.addWidget(RecognitionPage.create(self))
        
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
    
    def show_about(self):
        QMessageBox.about(self, "关于", 
            "岩心图像识别系统 RockCoreImage\n\n"
            "基于PyQt6和PyTorch开发的岩心图像分类识别系统\n\n"
            "支持预训练模型: ResNet, VGG, EfficientNet\n\n"
            "版本: 1.0.0"
        )
    
    def select_source_directory(self):
        folder = QFileDialog.getExistingDirectory(self, "选择数据目录")
        if folder:
            self.source_directory = folder
            self.source_path_label.setText(os.path.basename(folder))
            self.process_log.append(f"已选择数据源: {folder}")
    
    def select_output_directory(self):
        folder = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if folder:
            self.output_directory = folder
            self.output_path_label.setText(os.path.basename(folder))
            self.process_log.append(f"已选择输出目录: {folder}")
    
    def start_data_processing(self):
        if not hasattr(self, 'source_directory') or not self.source_directory:
            QMessageBox.warning(self, "警告", "请先选择数据源目录")
            return
        
        if not hasattr(self, 'output_directory') or not self.output_directory:
            QMessageBox.warning(self, "警告", "请先选择输出目录")
            return
        
        self.process_status_label.setText("正在初始化...")
        self.process_status_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #FF9800;
            padding: 8px;
            background-color: #FFF3E0;
            border: 1px solid #FF9800;
            border-radius: 4px;
        """)
        self.process_progress.setValue(0)
        self.process_log.clear()
        self.process_log.append("开始处理数据...")
        
        try:
            self.data_processor.progress_updated.disconnect()
            self.data_processor.processing_finished.disconnect()
            self.data_processor.error_occurred.disconnect()
        except TypeError:
            pass
        
        self.data_processor.progress_updated.connect(self.on_processing_progress)
        self.data_processor.processing_finished.connect(self.on_processing_finished)
        self.data_processor.error_occurred.connect(self.on_processing_error)
        
        from threading import Thread
        self.process_thread = Thread(
            target=self.data_processor.process,
            args=(self.source_directory, self.output_directory),
            daemon=True
        )
        self.process_thread.start()
    
    def on_processing_progress(self, value, message):
        self.process_progress.setValue(value)
        self.process_log.append(message)
        self.status_bar.showMessage(message)
        
        if value < 30:
            self.process_status_label.setText("正在扫描项目...")
            self.process_status_label.setStyleSheet("""
                font-size: 14px;
                font-weight: bold;
                color: #2196F3;
                padding: 8px;
                background-color: #E3F2FD;
                border: 1px solid #2196F3;
                border-radius: 4px;
            """)
        elif value < 90:
            self.process_status_label.setText("正在处理数据...")
            self.process_status_label.setStyleSheet("""
                font-size: 14px;
                font-weight: bold;
                color: #FF9800;
                padding: 8px;
                background-color: #FFF3E0;
                border: 1px solid #FF9800;
                border-radius: 4px;
            """)
        else:
            self.process_status_label.setText("正在保存结果...")
            self.process_status_label.setStyleSheet("""
                font-size: 14px;
                font-weight: bold;
                color: #9C27B0;
                padding: 8px;
                background-color: #F3E5F5;
                border: 1px solid #9C27B0;
                border-radius: 4px;
            """)
    
    def on_processing_finished(self, output_file, stats):
        self.process_progress.setValue(100)
        
        if stats.get('total_images', 0) > 0:
            self.process_status_label.setText(f"处理完成 - 共 {stats['total_images']} 张图片，{stats['total_projects']} 个项目")
            self.process_status_label.setStyleSheet("""
                font-size: 14px;
                font-weight: bold;
                color: #4CAF50;
                padding: 8px;
                background-color: #E8F5E9;
                border: 1px solid #4CAF50;
                border-radius: 4px;
            """)
            self.classify_btn.setEnabled(True)
            self.classify_output_file = output_file
            
            lithology_stats = stats.get('lithology_stats', {})
            
            self.process_table.setColumnCount(3)
            self.process_table.setHorizontalHeaderLabels(["岩性名称", "图片数", "岩性描述"])
            self.process_table.setColumnWidth(0, 120)
            self.process_table.setColumnWidth(1, 80)
            self.process_table.setColumnWidth(2, 300)
            
            sorted_lith = sorted(lithology_stats.items(), key=lambda x: -x[1]['count'])
            self.process_table.setRowCount(len(sorted_lith))
            
            for i, (lith_name, info) in enumerate(sorted_lith):
                self.process_table.setItem(i, 0, QTableWidgetItem(lith_name))
                self.process_table.setItem(i, 1, QTableWidgetItem(str(info['count'])))
                desc = info['description']
                self.process_table.setItem(i, 2, QTableWidgetItem(desc.replace('\n', ' ')))
            
            self.process_table.resizeRowsToContents()
        else:
            self.process_status_label.setText("处理完成 - 未找到数据")
            self.process_status_label.setStyleSheet("""
                font-size: 14px;
                font-weight: bold;
                color: #9E9E9E;
                padding: 8px;
                background-color: #F5F5F5;
                border: 1px solid #9E9E9E;
                border-radius: 4px;
            """)
        
        self.process_log.append(f"处理完成!")
        self.process_log.append(f"共处理图片: {stats.get('total_images', 0)} 张")
        self.process_log.append(f"项目数量: {stats.get('total_projects', 0)} 个")
        self.process_log.append(f"描述文件: {output_file}")
        
        self.status_bar.showMessage("处理完成")
        
        if stats.get('total_images', 0) > 0:
            QMessageBox.information(self, "处理完成", 
                f"共处理图片: {stats['total_images']} 张\n"
                f"项目数量: {stats['total_projects']} 个\n"
                f"描述文件: {output_file}")
    
    def on_processing_error(self, error_msg):
        self.process_log.append(f"错误: {error_msg}")
    
    def start_lithology_classify(self):
        if hasattr(self, 'classify_output_file') and self.classify_output_file:
            json_file = self.classify_output_file
            reply = QMessageBox.question(
                self, "确认", 
                f"使用之前生成的文件?\n{json_file}\n\n点击'是'使用该文件，点击'否'选择其他文件",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                json_file, _ = QFileDialog.getOpenFileName(
                    self, "选择JSON文件", "", "JSON文件 (*.json)"
                )
                if not json_file:
                    return
        else:
            json_file, _ = QFileDialog.getOpenFileName(
                self, "选择JSON文件", "", "JSON文件 (*.json)"
            )
            if not json_file:
                return
        
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        project_root = os.path.dirname(app_dir)
        config_file = os.path.join(project_root, 'config', 'rock_types_flat.json')
        
        if not os.path.exists(config_file):
            QMessageBox.warning(self, "错误", f"找不到配置文件: {config_file}\n请检查config目录是否存在")
            return
        
        output_file = json_file.replace('.json', '_classified.json')
        
        self.process_status_label.setText("正在初始化...")
        self.process_status_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #FF9800;
            padding: 8px;
            background-color: #FFF3E0;
            border: 1px solid #FF9800;
            border-radius: 4px;
        """)
        self.process_progress.setValue(0)
        self.process_log.clear()
        self.process_log.append("开始岩性分类...")
        
        try:
            self.data_processor.progress_updated.disconnect()
            self.data_processor.processing_finished.disconnect()
            self.data_processor.error_occurred.disconnect()
        except TypeError:
            pass
        
        self.data_processor.progress_updated.connect(self.on_classify_progress)
        self.data_processor.processing_finished.connect(self.on_classify_finished)
        self.data_processor.error_occurred.connect(self.on_processing_error)
        
        from threading import Thread
        self.classify_thread = Thread(
            target=self.data_processor.classify_lithology,
            args=(json_file, config_file, output_file),
            daemon=True
        )
        self.classify_thread.start()
    
    def on_classify_progress(self, value, message):
        self.process_progress.setValue(value)
        self.process_log.append(message)
        self.status_bar.showMessage(message)
        
        self.process_status_label.setText(message)
    
    def on_classify_finished(self, output_file, stats):
        self.process_progress.setValue(100)
        
        self.process_status_label.setText(f"分类完成 - 匹配 {stats['matched']}/{stats['total']} 条")
        self.process_status_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #4CAF50;
            padding: 8px;
            background-color: #E8F5E9;
            border: 1px solid #4CAF50;
            border-radius: 4px;
        """)
        
        self.process_log.append(f"分类完成!")
        self.process_log.append(f"总记录数: {stats['total']}")
        self.process_log.append(f"匹配成功: {stats['matched']} 条")
        self.process_log.append(f"匹配种类: {stats['types']} 种")
        self.process_log.append(f"输出文件: {output_file}")
        
        mapping = stats['mapping']
        unmatched = stats.get('unmatched', {})
        
        total_rows = len(mapping)
        if unmatched:
            total_rows += 1
        
        self.process_table.setColumnCount(4)
        self.process_table.setHorizontalHeaderLabels(["标准岩性", "对应原始岩性", "图片数", "分类数"])
        self.process_table.setColumnWidth(0, 100)
        self.process_table.setColumnWidth(1, 350)
        self.process_table.setColumnWidth(2, 80)
        self.process_table.setColumnWidth(3, 80)
        self.process_table.setRowCount(total_rows)
        
        row = 0
        for standard_rock, info in sorted(mapping.items(), key=lambda x: -x[1]['count']):
            lithologies_str = ", ".join(sorted(info['lithologies']))
            self.process_table.setItem(row, 0, QTableWidgetItem(standard_rock))
            self.process_table.setItem(row, 1, QTableWidgetItem(lithologies_str))
            self.process_table.setItem(row, 2, QTableWidgetItem(str(info['count'])))
            self.process_table.setItem(row, 3, QTableWidgetItem(str(len(info['lithologies']))))
            row += 1
        
        if unmatched:
            unmatched_str = ", ".join(sorted(unmatched.keys()))
            unmatched_count = sum(unmatched.values())
            self.process_table.setItem(row, 0, QTableWidgetItem("未发现分类"))
            self.process_table.setItem(row, 1, QTableWidgetItem(unmatched_str))
            self.process_table.setItem(row, 2, QTableWidgetItem(str(unmatched_count)))
            self.process_table.setItem(row, 3, QTableWidgetItem(str(len(unmatched))))
        
        self.process_table.resizeRowsToContents()
        
        self.status_bar.showMessage("分类完成")
    
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
        from PyQt6.QtWidgets import QFrame
        for i, img_path in enumerate(self.image_paths[:20]):
            row = i // cols
            col = i % cols
            
            frame = QFrame()
            frame.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 4px;")
            layout = QVBoxLayout()
            
            from PyQt6.QtGui import QPixmap
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