import os
import json
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem


class DataProcessHandler:
    def __init__(self, main_window):
        self.main_window = main_window
    
    def start_data_processing(self):
        if not hasattr(self.main_window, 'source_directory') or not self.main_window.source_directory:
            QMessageBox.warning(self.main_window, "警告", "请先选择数据源目录")
            return
        
        if not hasattr(self.main_window, 'output_directory') or not self.main_window.output_directory:
            QMessageBox.warning(self.main_window, "警告", "请先选择输出目录")
            return
        
        process_type = getattr(self.main_window, 'process_type', 'excel')
        
        self.main_window.process_btn.setEnabled(False)
        if hasattr(self.main_window, 'classify_btn'):
            self.main_window.classify_btn.setEnabled(False)
        if hasattr(self.main_window, 'alteration_btn'):
            self.main_window.alteration_btn.setEnabled(False)
        if hasattr(self.main_window, 'stats_btn'):
            self.main_window.stats_btn.setEnabled(False)
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
        
        if process_type == 'html':
            self.main_window.process_log.append("开始处理HTML数据...")
        else:
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
        
        lithology_id_start = 1
        if hasattr(self.main_window, 'lithology_id_start_input'):
            try:
                lithology_id_start = int(self.main_window.lithology_id_start_input.text()) or 1
            except ValueError:
                lithology_id_start = 1
        
        from threading import Thread
        self.main_window.process_thread = Thread(
            target=self.main_window.data_processor.process,
            args=(self.main_window.source_directory, self.main_window.output_directory, lithology_id_start),
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
            if hasattr(self.main_window, 'classify_btn'):
                self.main_window.classify_btn.setEnabled(True)
            if hasattr(self.main_window, 'alteration_btn'):
                self.main_window.alteration_btn.setEnabled(True)
            if hasattr(self.main_window, 'stats_btn'):
                self.main_window.stats_btn.setEnabled(True)
            self.main_window.classify_output_file = output_file
            
            with open(output_file, 'r', encoding='utf-8') as f:
                image_data = json.load(f)
            
            desc_file = os.path.join(os.path.dirname(output_file), 'lithology_descriptions.json')
            desc_by_id = {}
            if os.path.exists(desc_file):
                with open(desc_file, 'r', encoding='utf-8') as f:
                    desc_list = json.load(f)
                    for d in desc_list:
                        desc_by_id[d['id']] = d
            
            if desc_by_id:
                for i, desc in desc_by_id.items():
                    if 'id' not in desc:
                        desc['id'] = i
                
                desc_list_sorted = sorted(desc_by_id.values(), key=lambda x: x.get('id', 0))
                
                image_counts = {}
                for item in image_data:
                    desc_id = item.get('lithology_description_id')
                    if desc_id is not None:
                        image_counts[desc_id] = image_counts.get(desc_id, 0) + 1
                
                self.main_window.process_table.setColumnCount(6)
                self.main_window.process_table.setHorizontalHeaderLabels(["项目", "钻孔", "岩性名称", "深度范围(m)", "图片数", "岩性描述"])
                self.main_window.process_table.setColumnWidth(0, 80)
                self.main_window.process_table.setColumnWidth(1, 80)
                self.main_window.process_table.setColumnWidth(2, 100)
                self.main_window.process_table.setColumnWidth(3, 80)
                self.main_window.process_table.setColumnWidth(4, 60)
                self.main_window.process_table.horizontalHeader().setStretchLastSection(True)
                self.main_window.process_table.setColumnWidth(2, 120)
                self.main_window.process_table.setColumnWidth(3, 100)
                self.main_window.process_table.setColumnWidth(4, 60)
                self.main_window.process_table.horizontalHeader().setStretchLastSection(True)
                
                self.main_window.process_table.setRowCount(len(desc_list_sorted))
                
                for i, desc in enumerate(desc_list_sorted):
                    proj = desc.get('project', '')
                    borehole = desc.get('borehole', '')
                    lith_name = desc.get('lithology', '')
                    start = desc.get('start_depth', 0)
                    end = desc.get('end_depth', 0)
                    depth_range = f"{start}-{end}"
                    count = image_counts.get(desc.get('id', i), 0)
                    
                    self.main_window.process_table.setItem(i, 0, QTableWidgetItem(proj))
                    self.main_window.process_table.setItem(i, 1, QTableWidgetItem(borehole))
                    self.main_window.process_table.setItem(i, 2, QTableWidgetItem(lith_name))
                    self.main_window.process_table.setItem(i, 3, QTableWidgetItem(depth_range))
                    self.main_window.process_table.setItem(i, 4, QTableWidgetItem(str(count)))
                    desc_text = desc.get('description', '')
                    if desc_text:
                        desc_text = desc_text.replace('\r\n', ' ').replace('\n', ' ').replace('|', ' ')
                    self.main_window.process_table.setItem(i, 5, QTableWidgetItem(desc_text))
            else:
                lithology_groups = {}
                for item in image_data:
                    proj = item.get('project', '')
                    lith = item.get('lithology', '')
                    key = (proj, lith)
                    
                    if key not in lithology_groups:
                        lithology_groups[key] = {
                            'project': proj,
                            'lithology': lith,
                            'count': 0,
                        }
                    
                    lithology_groups[key]['count'] += 1
                
                self.main_window.process_table.setColumnCount(3)
                self.main_window.process_table.setHorizontalHeaderLabels(["项目", "岩性名称", "图片数"])
                self.main_window.process_table.setColumnWidth(0, 150)
                self.main_window.process_table.setColumnWidth(1, 150)
                self.main_window.process_table.setColumnWidth(2, 80)
                self.main_window.process_table.horizontalHeader().setStretchLastSection(True)
                
                sorted_lith = sorted(lithology_groups.values(), key=lambda x: (x['project'], x['lithology']))
                self.main_window.process_table.setRowCount(len(sorted_lith))
                
                for i, info in enumerate(sorted_lith):
                    self.main_window.process_table.setItem(i, 0, QTableWidgetItem(info['project']))
                    self.main_window.process_table.setItem(i, 1, QTableWidgetItem(info['lithology']))
                    self.main_window.process_table.setItem(i, 2, QTableWidgetItem(str(info['count'])))
            
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
            if hasattr(self.main_window, 'classify_btn'):
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
        if hasattr(self.main_window, 'classify_btn'):
            self.main_window.classify_btn.setEnabled(True)
        self.main_window.process_status_label.setText("处理出错")
        self.main_window.process_status_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #F44336;
            padding: 8px;
            background-color: #FFEBEE;
            border: 1px solid #F44336;
            border-radius: 4px;
        """)
