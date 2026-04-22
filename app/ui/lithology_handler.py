import os
import json
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
        import os
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            QMessageBox.warning(self.main_window, "错误", f"无法读取文件: {str(e)}")
            return
        
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        project_root = os.path.dirname(app_dir)
        config_file = os.path.join(project_root, 'config', 'rock_types_flat.json')
        
        rock_category_map = {}
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            for rock in config_data.get('rocks', []):
                rock_category_map[rock['name']] = rock.get('category', '')
        except Exception:
            pass
        
        self.main_window.process_log.clear()
        self.main_window.process_log.append(f"已加载岩性分类结果: {json_file}")
        self.main_window.process_log.append(f"总记录数: {len(data)}")
        
        rock_groups = {}
        for item in data:
            rock_name = item.get('rock_name', '') or '未分类'
            lithology = item.get('lithology', '')
            if rock_name not in rock_groups:
                rock_groups[rock_name] = {'lithologies': set(), 'count': 0}
            rock_groups[rock_name]['lithologies'].add(lithology)
            rock_groups[rock_name]['count'] += 1
        
        category_counts = {'岩浆岩': 0, '沉积岩': 0, '变质岩': 0}
        for rock_name in rock_groups.keys():
            category = rock_category_map.get(rock_name, '')
            if category in category_counts:
                category_counts[category] += 1
        
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
        
        cat_stat = f"岩浆岩{category_counts['岩浆岩']}种/沉积岩{category_counts['沉积岩']}种/变质岩{category_counts['变质岩']}种"
        self.main_window.process_status_label.setText(f"显示岩性分类 - 共 {len(rock_groups)} 种岩性（{cat_stat}）")
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
    
    def show_lithology_stats(self):
        from PyQt6.QtWidgets import QFileDialog
        dir_path = QFileDialog.getExistingDirectory(
            self.main_window, "选择处理结果目录"
        )
        if not dir_path:
            return
        
        lithology_file = os.path.join(dir_path, 'lithology_descriptions.json')
        image_file = os.path.join(dir_path, 'image_descriptions.json')
        
        if not os.path.exists(lithology_file):
            QMessageBox.warning(self.main_window, "错误", "找不到lithology_descriptions.json文件")
            return
        if not os.path.exists(image_file):
            QMessageBox.warning(self.main_window, "错误", "找不到image_descriptions.json文件")
            return
        
        try:
            with open(lithology_file, 'r', encoding='utf-8') as f:
                lithology_data = json.load(f)
            with open(image_file, 'r', encoding='utf-8') as f:
                image_data = json.load(f)
        except Exception as e:
            QMessageBox.warning(self.main_window, "错误", f"无法读取文件: {str(e)}")
            return
        
        image_counts = {}
        for item in image_data:
            desc_id = item.get('lithology_description_id')
            if desc_id is not None:
                image_counts[desc_id] = image_counts.get(desc_id, 0) + 1
        
        self.main_window.analysis_table.setColumnCount(7)
        self.main_window.analysis_table.setHorizontalHeaderLabels(["项目", "钻孔", "岩性名称", "开始深度", "结束深度", "图片数量", "岩性描述"])
        self.main_window.analysis_table.setColumnWidth(0, 80)
        self.main_window.analysis_table.setColumnWidth(1, 80)
        self.main_window.analysis_table.setColumnWidth(2, 100)
        self.main_window.analysis_table.setColumnWidth(3, 80)
        self.main_window.analysis_table.setColumnWidth(4, 80)
        self.main_window.analysis_table.setColumnWidth(5, 80)
        self.main_window.analysis_table.horizontalHeader().setStretchLastSection(True)
        
        lithology_data_sorted = sorted(lithology_data, key=lambda x: x.get('id', 0))
        self.main_window.analysis_table.setRowCount(len(lithology_data_sorted))
        
        for i, lith in enumerate(lithology_data_sorted):
            proj = lith.get('project', '')
            borehole = lith.get('borehole', '')
            lith_name = lith.get('lithology', '')
            start = lith.get('start_depth', 0)
            end = lith.get('end_depth', 0)
            desc = lith.get('description', '')
            count = image_counts.get(lith.get('id', i), 0)
            
            self.main_window.analysis_table.setItem(i, 0, QTableWidgetItem(proj))
            self.main_window.analysis_table.setItem(i, 1, QTableWidgetItem(borehole))
            self.main_window.analysis_table.setItem(i, 2, QTableWidgetItem(lith_name))
            self.main_window.analysis_table.setItem(i, 3, QTableWidgetItem(str(start)))
            self.main_window.analysis_table.setItem(i, 4, QTableWidgetItem(str(end)))
            self.main_window.analysis_table.setItem(i, 5, QTableWidgetItem(str(count)))
            self.main_window.analysis_table.setItem(i, 6, QTableWidgetItem(desc.replace('\r\n', ' ').replace('\n', ' ') if desc else ''))
        
        self.main_window.analysis_table.resizeRowsToContents()
        
        total_images = sum(image_counts.values())
        self.main_window.analysis_log.clear()
        self.main_window.analysis_log.append(f"已加载岩性统计: {dir_path}")
        self.main_window.analysis_log.append(f"共 {len(lithology_data)} 条岩性记录, {total_images} 张图片")
        
        self.main_window.analysis_status_label.setText(f"岩性统计 - {len(lithology_data)} 条记录")
        self.main_window.analysis_status_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #2196F3;
            padding: 8px;
            background-color: #E3F2FD;
            border: 1px solid #2196F3;
            border-radius: 4px;
        """)

    def adjust_lithology(self):
        from PyQt6.QtWidgets import QFileDialog
        dir_path = QFileDialog.getExistingDirectory(
            self.main_window, "选择目录", ""
        )
        if not dir_path:
            return
        
        diff_file = os.path.join(dir_path, 'lithology_descriptions_diff.json')
        image_file = os.path.join(dir_path, 'image_descriptions.json')
        
        if not os.path.exists(diff_file):
            QMessageBox.warning(self.main_window, "错误", f"找不到 {diff_file}")
            return
        
        if not os.path.exists(image_file):
            QMessageBox.warning(self.main_window, "错误", f"找不到 {image_file}")
            return
        
        output_file = os.path.join(dir_path, 'image_descriptions_adjusted.json')
        
        try:
            with open(diff_file, 'r', encoding='utf-8') as f:
                diff_data = json.load(f)
            
            with open(image_file, 'r', encoding='utf-8') as f:
                image_data = json.load(f)
            
            from collections import defaultdict
            lithology_by_project = defaultdict(list)
            for item in diff_data:
                key = (item['project'], item['borehole'])
                lithology_by_project[key].append({
                    'start': item['start_depth'],
                    'end': item['end_depth'],
                    'lithology': item['lithology'],
                    'description': item.get('description', ''),
                    'description_id': item['id']
                })
            
            def calculate_overlap(img_start, img_end, lith_start, lith_end):
                overlap_start = max(img_start, lith_start)
                overlap_end = min(img_end, lith_end)
                if overlap_start >= overlap_end:
                    return 0
                overlap_depth = overlap_end - overlap_start
                img_depth = img_end - img_start
                if img_depth <= 0:
                    return 0
                return overlap_depth / img_depth
            
            update_count = 0
            not_found_count = 0
            
            for img in image_data:
                project = img['project']
                borehole = img['borehole']
                img_start = img['start_depth']
                img_end = img['end_depth']
                
                key = (project, borehole)
                if key not in lithology_by_project:
                    not_found_count += 1
                    continue
                
                best_match = None
                best_overlap = 0
                
                for lith in lithology_by_project[key]:
                    overlap = calculate_overlap(img_start, img_end, lith['start'], lith['end'])
                    if overlap > best_overlap and overlap >= 0.6:
                        best_overlap = overlap
                        best_match = lith
                
                if best_match:
                    img['lithology'] = best_match['lithology']
                    img['lithology_description_id'] = best_match['description_id']
                    update_count += 1
                else:
                    not_found_count += 1
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(image_data, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(
                self.main_window, "完成",
                f"岩性调整完成!\n\n更新: {update_count} 条\n未匹配: {not_found_count} 条\n\n输出文件: {output_file}"
            )
            
            self.main_window.analysis_log.append(f"岩性调整完成: 更新 {update_count} 条, 输出 {output_file}")
            
        except Exception as e:
            QMessageBox.critical(self.main_window, "错误", f"处理失败: {str(e)}")
