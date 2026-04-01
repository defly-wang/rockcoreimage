import os
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem


class ProcessHandler:
    def __init__(self, main_window):
        self.main_window = main_window
    
    def select_source_directory(self):
        from PyQt6.QtWidgets import QFileDialog
        folder = QFileDialog.getExistingDirectory(self.main_window, "选择数据目录")
        if folder:
            self.main_window.source_directory = folder
            self.main_window.source_path_label.setText(os.path.basename(folder))
            self.main_window.process_log.append(f"已选择数据源: {folder}")
    
    def select_output_directory(self):
        from PyQt6.QtWidgets import QFileDialog
        folder = QFileDialog.getExistingDirectory(self.main_window, "选择输出目录")
        if folder:
            self.main_window.output_directory = folder
            self.main_window.output_path_label.setText(os.path.basename(folder))
            self.main_window.process_log.append(f"已选择输出目录: {folder}")
    
    def start_data_processing(self):
        if not hasattr(self.main_window, 'source_directory') or not self.main_window.source_directory:
            QMessageBox.warning(self.main_window, "警告", "请先选择数据源目录")
            return
        
        if not hasattr(self.main_window, 'output_directory') or not self.main_window.output_directory:
            QMessageBox.warning(self.main_window, "警告", "请先选择输出目录")
            return
        
        self.main_window.process_btn.setEnabled(False)
        self.main_window.classify_btn.setEnabled(False)
        self.main_window.process_status_label.setText("正在初始化...")
        self.main_window.process_status_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #FF9800;
            padding: 8px;
            background-color: #FFF3E0;
            border: 1px solid #FF9800;
            border-radius: 4px;
        """)
        self.main_window.process_progress.setValue(0)
        self.main_window.process_log.clear()
        self.main_window.process_log.append("开始处理数据...")
        
        try:
            self.main_window.data_processor.progress_updated.disconnect()
            self.main_window.data_processor.processing_finished.disconnect()
            self.main_window.data_processor.error_occurred.disconnect()
        except TypeError:
            pass
        
        self.main_window.data_processor.progress_updated.connect(self.on_processing_progress)
        self.main_window.data_processor.processing_finished.connect(self.on_processing_finished)
        self.main_window.data_processor.error_occurred.connect(self.on_processing_error)
        
        from threading import Thread
        self.main_window.process_thread = Thread(
            target=self.main_window.data_processor.process,
            args=(self.main_window.source_directory, self.main_window.output_directory),
            daemon=True
        )
        self.main_window.process_thread.start()
    
    def on_processing_progress(self, value, message):
        self.main_window.process_progress.setValue(value)
        self.main_window.process_log.append(message)
        self.main_window.status_bar.showMessage(message)
        
        if value < 30:
            self.main_window.process_status_label.setText("正在扫描项目...")
            self.main_window.process_status_label.setStyleSheet("""
                font-size: 14px;
                font-weight: bold;
                color: #2196F3;
                padding: 8px;
                background-color: #E3F2FD;
                border: 1px solid #2196F3;
                border-radius: 4px;
            """)
        elif value < 90:
            self.main_window.process_status_label.setText("正在处理数据...")
            self.main_window.process_status_label.setStyleSheet("""
                font-size: 14px;
                font-weight: bold;
                color: #FF9800;
                padding: 8px;
                background-color: #FFF3E0;
                border: 1px solid #FF9800;
                border-radius: 4px;
            """)
        else:
            self.main_window.process_status_label.setText("正在保存结果...")
            self.main_window.process_status_label.setStyleSheet("""
                font-size: 14px;
                font-weight: bold;
                color: #9C27B0;
                padding: 8px;
                background-color: #F3E5F5;
                border: 1px solid #9C27B0;
                border-radius: 4px;
            """)
    
    def on_processing_finished(self, output_file, stats):
        self.main_window.process_progress.setValue(100)
        
        if stats.get('total_images', 0) > 0:
            self.main_window.process_status_label.setText(f"处理完成 - 共 {stats['total_images']} 张图片，{stats['total_projects']} 个项目")
            self.main_window.process_status_label.setStyleSheet("""
                font-size: 14px;
                font-weight: bold;
                color: #4CAF50;
                padding: 8px;
                background-color: #E8F5E9;
                border: 1px solid #4CAF50;
                border-radius: 4px;
            """)
            self.main_window.process_btn.setEnabled(True)
            self.main_window.classify_btn.setEnabled(True)
            self.main_window.classify_output_file = output_file
            
            lithology_stats = stats.get('lithology_stats', {})
            
            self.main_window.process_table.setColumnCount(3)
            self.main_window.process_table.setHorizontalHeaderLabels(["岩性名称", "图片数", "岩性描述"])
            self.main_window.process_table.setColumnWidth(0, 120)
            self.main_window.process_table.setColumnWidth(1, 80)
            self.main_window.process_table.horizontalHeader().setStretchLastSection(True)
            
            sorted_lith = sorted(lithology_stats.items(), key=lambda x: -x[1]['count'])
            self.main_window.process_table.setRowCount(len(sorted_lith))
            
            for i, (lith_name, info) in enumerate(sorted_lith):
                self.main_window.process_table.setItem(i, 0, QTableWidgetItem(lith_name))
                self.main_window.process_table.setItem(i, 1, QTableWidgetItem(str(info['count'])))
                desc = info['description']
                self.main_window.process_table.setItem(i, 2, QTableWidgetItem(desc.replace('\n', ' ')))
            
            self.main_window.process_table.resizeRowsToContents()
        else:
            self.main_window.process_status_label.setText("处理完成 - 未找到数据")
            self.main_window.process_status_label.setStyleSheet("""
                font-size: 14px;
                font-weight: bold;
                color: #9E9E9E;
                padding: 8px;
                background-color: #F5F5F5;
                border: 1px solid #9E9E9E;
                border-radius: 4px;
            """)
            self.main_window.process_btn.setEnabled(True)
            self.main_window.classify_btn.setEnabled(True)
        
        self.main_window.process_log.append(f"处理完成!")
        self.main_window.process_log.append(f"共处理图片: {stats.get('total_images', 0)} 张")
        self.main_window.process_log.append(f"项目数量: {stats.get('total_projects', 0)} 个")
        self.main_window.process_log.append(f"描述文件: {output_file}")
        
        self.main_window.status_bar.showMessage("处理完成")
        
        if stats.get('total_images', 0) > 0:
            QMessageBox.information(self.main_window, "处理完成", 
                f"共处理图片: {stats['total_images']} 张\n"
                f"项目数量: {stats['total_projects']} 个\n"
                f"描述文件: {output_file}")
    
    def on_processing_error(self, error_msg):
        self.main_window.process_log.append(f"错误: {error_msg}")
        self.main_window.process_btn.setEnabled(True)
        self.main_window.classify_btn.setEnabled(True)
    
    def start_lithology_classify(self):
        from PyQt6.QtWidgets import QFileDialog
        json_file, _ = QFileDialog.getOpenFileName(
            self.main_window, "选择JSON文件", "", "JSON文件 (*.json)"
        )
        if not json_file:
            return
        
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        project_root = os.path.dirname(app_dir)
        config_file = os.path.join(project_root, 'config', 'rock_types_flat.json')
        
        if not os.path.exists(config_file):
            QMessageBox.warning(self.main_window, "错误", f"找不到配置文件: {config_file}\n请检查config目录是否存在")
            return
        
        output_file = json_file.replace('.json', '_classified.json')
        
        self.main_window.process_btn.setEnabled(False)
        self.main_window.classify_btn.setEnabled(False)
        self.main_window.process_status_label.setText("正在初始化...")
        self.main_window.process_status_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #FF9800;
            padding: 8px;
            background-color: #FFF3E0;
            border: 1px solid #FF9800;
            border-radius: 4px;
        """)
        self.main_window.process_progress.setValue(0)
        self.main_window.process_log.clear()
        self.main_window.process_log.append("开始岩性分类...")
        
        try:
            self.main_window.data_processor.progress_updated.disconnect()
            self.main_window.data_processor.processing_finished.disconnect()
            self.main_window.data_processor.error_occurred.disconnect()
        except TypeError:
            pass
        
        self.main_window.data_processor.progress_updated.connect(self.on_classify_progress)
        self.main_window.data_processor.processing_finished.connect(self.on_classify_finished)
        self.main_window.data_processor.error_occurred.connect(self.on_processing_error)
        
        from threading import Thread
        self.main_window.classify_thread = Thread(
            target=self.main_window.data_processor.classify_lithology,
            args=(json_file, config_file, output_file),
            daemon=True
        )
        self.main_window.classify_thread.start()
    
    def on_classify_progress(self, value, message):
        self.main_window.process_progress.setValue(value)
        self.main_window.process_log.append(message)
        self.main_window.status_bar.showMessage(message)
        
        self.main_window.process_status_label.setText(message)
    
    def on_classify_finished(self, output_file, stats):
        self.main_window.process_progress.setValue(100)
        
        self.main_window.process_status_label.setText(f"分类完成 - 匹配 {stats['matched']}/{stats['total']} 条")
        self.main_window.process_status_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #4CAF50;
            padding: 8px;
            background-color: #E8F5E9;
            border: 1px solid #4CAF50;
            border-radius: 4px;
        """)
        
        self.main_window.process_log.append(f"分类完成!")
        self.main_window.process_log.append(f"总记录数: {stats['total']}")
        self.main_window.process_log.append(f"匹配成功: {stats['matched']} 条")
        self.main_window.process_log.append(f"匹配种类: {stats['types']} 种")
        self.main_window.process_log.append(f"输出文件: {output_file}")
        
        mapping = stats['mapping']
        unmatched = stats.get('unmatched', {})
        
        total_rows = len(mapping)
        if unmatched:
            total_rows += 1
        
        self.main_window.process_table.setColumnCount(4)
        self.main_window.process_table.setHorizontalHeaderLabels(["标准岩性", "图片数", "分类数", "对应原始岩性"])
        self.main_window.process_table.setColumnWidth(0, 100)
        self.main_window.process_table.setColumnWidth(1, 80)
        self.main_window.process_table.setColumnWidth(2, 80)
        self.main_window.process_table.horizontalHeader().setStretchLastSection(True)
        self.main_window.process_table.setRowCount(total_rows)
        
        row = 0
        for standard_rock, info in sorted(mapping.items(), key=lambda x: -x[1]['count']):
            lithologies_str = ", ".join(sorted(info['lithologies']))
            self.main_window.process_table.setItem(row, 0, QTableWidgetItem(standard_rock))
            self.main_window.process_table.setItem(row, 1, QTableWidgetItem(str(info['count'])))
            self.main_window.process_table.setItem(row, 2, QTableWidgetItem(str(len(info['lithologies']))))
            self.main_window.process_table.setItem(row, 3, QTableWidgetItem(lithologies_str))
            row += 1
        
        if unmatched:
            unmatched_str = ", ".join(sorted(unmatched.keys()))
            unmatched_count = sum(unmatched.values())
            self.main_window.process_table.setItem(row, 0, QTableWidgetItem("未发现分类"))
            self.main_window.process_table.setItem(row, 1, QTableWidgetItem(str(unmatched_count)))
            self.main_window.process_table.setItem(row, 2, QTableWidgetItem(str(len(unmatched))))
            self.main_window.process_table.setItem(row, 3, QTableWidgetItem(unmatched_str))
        
        self.main_window.process_table.resizeRowsToContents()
        
        self.main_window.process_btn.setEnabled(True)
        self.main_window.classify_btn.setEnabled(True)
        self.main_window.status_bar.showMessage("分类完成")
    
    def start_alteration_analysis(self):
        from PyQt6.QtWidgets import QFileDialog
        json_file, _ = QFileDialog.getOpenFileName(
            self.main_window, "选择岩性分析后的JSON文件", "", "JSON文件 (*.json)"
        )
        if not json_file:
            return
        
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        project_root = os.path.dirname(app_dir)
        alteration_config_file = os.path.join(project_root, 'config', 'alteration_types.json')
        
        if not os.path.exists(alteration_config_file):
            QMessageBox.warning(self.main_window, "错误", f"找不到蚀变配置文件: {alteration_config_file}\n请检查config目录是否存在")
            return
        
        output_file = json_file.replace('.json', '_alteration.json')
        
        self.main_window.process_btn.setEnabled(False)
        self.main_window.classify_btn.setEnabled(False)
        if hasattr(self.main_window, 'alteration_btn'):
            self.main_window.alteration_btn.setEnabled(False)
        self.main_window.process_status_label.setText("正在初始化...")
        self.main_window.process_status_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #FF9800;
            padding: 8px;
            background-color: #FFF3E0;
            border: 1px solid #FF9800;
            border-radius: 4px;
        """)
        self.main_window.process_progress.setValue(0)
        self.main_window.process_log.clear()
        self.main_window.process_log.append("开始蚀变分析...")
        
        try:
            self.main_window.data_processor.progress_updated.disconnect()
            self.main_window.data_processor.processing_finished.disconnect()
            self.main_window.data_processor.error_occurred.disconnect()
        except TypeError:
            pass
        
        self.main_window.data_processor.progress_updated.connect(self.on_alteration_progress)
        self.main_window.data_processor.processing_finished.connect(self.on_alteration_finished)
        self.main_window.data_processor.error_occurred.connect(self.on_processing_error)
        
        from threading import Thread
        self.main_window.alteration_thread = Thread(
            target=self.main_window.data_processor.analyze_alteration,
            args=(json_file, alteration_config_file, output_file),
            daemon=True
        )
        self.main_window.alteration_thread.start()
    
    def on_alteration_progress(self, value, message):
        self.main_window.process_progress.setValue(value)
        self.main_window.process_log.append(message)
        self.main_window.status_bar.showMessage(message)
        self.main_window.process_status_label.setText(message)
    
    def on_alteration_finished(self, output_file, stats):
        import json
        
        self.main_window.process_progress.setValue(100)
        
        records_with_alt = stats.get('records_with_alteration', 0)
        total_records = stats.get('total_records', 0)
        total_alterations = stats.get('total_alterations', 0)
        alteration_types = stats.get('alteration_types', 0)
        
        self.main_window.process_status_label.setText(f"蚀变分析完成 - {records_with_alt}/{total_records} 条含蚀变")
        self.main_window.process_status_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #4CAF50;
            padding: 8px;
            background-color: #E8F5E9;
            border: 1px solid #4CAF50;
            border-radius: 4px;
        """)
        
        self.main_window.process_log.append(f"蚀变分析完成!")
        self.main_window.process_log.append(f"总记录数: {total_records}")
        self.main_window.process_log.append(f"含蚀变记录: {records_with_alt} 条")
        self.main_window.process_log.append(f"蚀变类型数: {alteration_types} 种")
        self.main_window.process_log.append(f"总蚀变次数: {total_alterations}")
        self.main_window.process_log.append(f"输出文件: {output_file}")
        
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        records = [(item.get('岩性名称', '') or '未分类', item.get('lithology', ''), item.get('蚀变类型', '')) for item in data]
        records.sort(key=lambda x: (x[0], x[1]))
        
        self.main_window.process_table.setColumnCount(5)
        self.main_window.process_table.setHorizontalHeaderLabels(["标准岩性", "图片数", "分类数", "原始岩性", "蚀变类型"])
        self.main_window.process_table.setColumnWidth(0, 100)
        self.main_window.process_table.setColumnWidth(1, 60)
        self.main_window.process_table.setColumnWidth(2, 60)
        self.main_window.process_table.setColumnWidth(3, 250)
        self.main_window.process_table.horizontalHeader().setStretchLastSection(True)
        
        rock_groups = {}
        for rock_name, lithology, alteration in records:
            if rock_name not in rock_groups:
                rock_groups[rock_name] = {}
            if lithology not in rock_groups[rock_name]:
                rock_groups[rock_name][lithology] = {'count': 0, 'alterations': set()}
            rock_groups[rock_name][lithology]['count'] += 1
            if alteration:
                rock_groups[rock_name][lithology]['alterations'].add(alteration)
        
        rows = []
        for rock_name in sorted(rock_groups.keys()):
            for lithology, info in rock_groups[rock_name].items():
                alterations_str = ", ".join(sorted(info['alterations'])) if info['alterations'] else "-"
                rows.append((rock_name, str(info['count']), "1", lithology, alterations_str))
        
        self.main_window.process_table.setRowCount(len(rows))
        for row, (rock_name, count, _, lithology, alteration) in enumerate(rows):
            self.main_window.process_table.setItem(row, 0, QTableWidgetItem(rock_name))
            self.main_window.process_table.setItem(row, 1, QTableWidgetItem(count))
            self.main_window.process_table.setItem(row, 2, QTableWidgetItem("1"))
            self.main_window.process_table.setItem(row, 3, QTableWidgetItem(lithology))
            self.main_window.process_table.setItem(row, 4, QTableWidgetItem(alteration))
        
        self.main_window.process_table.resizeRowsToContents()
        
        self.main_window.process_btn.setEnabled(True)
        self.main_window.classify_btn.setEnabled(True)
        if hasattr(self.main_window, 'alteration_btn'):
            self.main_window.alteration_btn.setEnabled(True)
        self.main_window.status_bar.showMessage("蚀变分析完成")