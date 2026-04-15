import os
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem


class LithologyHandler:
    def __init__(self, main_window):
        self.main_window = main_window
    
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
        if hasattr(self.main_window, 'classify_btn'):
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
        if hasattr(self.main_window, 'classify_btn'):
            self.main_window.classify_btn.setEnabled(True)
        self.main_window.status_bar.showMessage("分类完成")
    
    def view_lithology_classification(self):
        from PyQt6.QtWidgets import QFileDialog
        json_file, _ = QFileDialog.getOpenFileName(
            self.main_window, "选择岩性分类后的JSON文件", "", "JSON文件 (*.json)"
        )
        if not json_file:
            return
        
        import json
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            QMessageBox.warning(self.main_window, "错误", f"无法读取文件: {str(e)}")
            return
        
        self.main_window.process_log.clear()
        self.main_window.process_log.append(f"已加载岩性分类结果: {json_file}")
        self.main_window.process_log.append(f"总记录数: {len(data)}")
        
        rock_groups = {}
        for item in data:
            rock_name = item.get('岩性名称', '') or '未分类'
            lithology = item.get('lithology', '')
            if rock_name not in rock_groups:
                rock_groups[rock_name] = {'lithologies': set(), 'count': 0}
            rock_groups[rock_name]['lithologies'].add(lithology)
            rock_groups[rock_name]['count'] += 1
        
        self.main_window.process_table.setColumnCount(4)
        self.main_window.process_table.setHorizontalHeaderLabels(["标准岩性", "图片数", "分类数", "对应原始岩性"])
        self.main_window.process_table.setColumnWidth(0, 100)
        self.main_window.process_table.setColumnWidth(1, 80)
        self.main_window.process_table.setColumnWidth(2, 80)
        self.main_window.process_table.horizontalHeader().setStretchLastSection(True)
        
        sorted_rocks = sorted(rock_groups.items(), key=lambda x: -x[1]['count'])
        self.main_window.process_table.setRowCount(len(sorted_rocks))
        
        for row, (rock_name, info) in enumerate(sorted_rocks):
            lithologies_str = ", ".join(sorted(info['lithologies']))
            self.main_window.process_table.setItem(row, 0, QTableWidgetItem(rock_name))
            self.main_window.process_table.setItem(row, 1, QTableWidgetItem(str(info['count'])))
            self.main_window.process_table.setItem(row, 2, QTableWidgetItem(str(len(info['lithologies']))))
            self.main_window.process_table.setItem(row, 3, QTableWidgetItem(lithologies_str))
        
        self.main_window.process_table.resizeRowsToContents()
        
        self.main_window.process_status_label.setText(f"显示岩性分类 - 共 {len(rock_groups)} 种岩性")
        self.main_window.process_status_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #2196F3;
            padding: 8px;
            background-color: #E3F2FD;
            border: 1px solid #2196F3;
            border-radius: 4px;
        """)
        
        self.main_window.current_json_file = json_file
        self.main_window.status_bar.showMessage("已加载岩性分类结果")
