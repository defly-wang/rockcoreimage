import os
import json
import re
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem, QLabel, QFileDialog, QHBoxLayout


class DataProcessHandler:
    def __init__(self, main_window):
        self.main_window = main_window
    
    def start_data_processing(self):
        process_type = getattr(self.main_window, 'process_type', 'excel')
        
        if process_type == 'web':
            self.start_local_fetching()
            return
        
        if not hasattr(self.main_window, 'source_directory') or not self.main_window.source_directory:
            QMessageBox.warning(self.main_window, "警告", "请先选择数据源目录")
            return
        
        if not hasattr(self.main_window, 'output_directory') or not self.main_window.output_directory:
            QMessageBox.warning(self.main_window, "警告", "请先选择输出目录")
            return
        
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
    
    def start_web_fetching(self):
        from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QCheckBox, QPushButton
        
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("实物中心数据 - 全国数字岩心平台")
        dialog.setModal(True)
        dialog.setFixedSize(550, 280)
        
        layout = QFormLayout()
        
        info_label = QLabel("请选择数据来源:")
        info_label.setStyleSheet("font-weight: bold; color: #1E3A5F;")
        layout.addRow("", info_label)
        
        use_json_check = QCheckBox("从JSON文件导入图片列表")
        use_json_check.setChecked(True)
        layout.addRow("", use_json_check)
        
        project_name_input = QLineEdit()
        project_name_input.setPlaceholderText("项目名称，如 ZK13-4-2")
        layout.addRow("项目名称:", project_name_input)
        
        json_file_input = QLineEdit()
        json_file_input.setPlaceholderText("JSON文件路径")
        
        def select_json_file():
            file_path, _ = QFileDialog.getOpenFileName(
                self.main_window, "选择JSON文件", "", "JSON Files (*.json)"
            )
            if file_path:
                json_file_input.setText(file_path)
        
        json_btn = QPushButton("浏览...")
        json_btn.clicked.connect(select_json_file)
        
        json_layout = QHBoxLayout()
        json_layout.addWidget(json_file_input, 1)
        json_layout.addWidget(json_btn)
        layout.addRow("图片列表文件:", json_layout)
        
        help_label = QLabel("在浏览器打开综合数据展示页面，按F12，在Console中运行：\nvar d=[];document.querySelectorAll('img.yanxinImage').forEach(i=>{if(i.dataset.options){var o={},s=i.dataset.options.split(',');s.forEach(x=>{var p=x.split(':');o[p[0]]=p[1]});d.push({yxtpbh:o.yxtpbh,qssd:o.qssd,zzsd:o.zzsd})}});console.log(JSON.stringify(d));")
        help_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addRow("帮助:", help_label)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow("", buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        project_name = project_name_input.text().strip()
        json_file = json_file_input.text().strip()
        output_dir = self.main_window.output_directory if hasattr(self.main_window, 'output_directory') and self.main_window.output_directory else ""
        
        if not project_name or not json_file or not output_dir:
            QMessageBox.warning(self.main_window, "警告", "请选择JSON文件和输出目录")
            return
        
        if not os.path.exists(json_file):
            QMessageBox.warning(self.main_window, "警告", "JSON文件不存在")
            return
        
        self.main_window.process_btn.setEnabled(False)
        if hasattr(self.main_window, 'classify_btn'):
            self.main_window.classify_btn.setEnabled(False)
        if hasattr(self.main_window, 'alteration_btn'):
            self.main_window.alteration_btn.setEnabled(False)
        if hasattr(self.main_window, 'stats_btn'):
            self.main_window.stats_btn.setEnabled(False)
        
        self.main_window.process_status_label.setText("正在从互联网抓取数据...")
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
        self.main_window.process_log.append("开始从互联网抓取数据...")
        
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
            target=self.main_window.data_processor.fetch_from_json,
            args=(json_file, project_name, output_dir, lithology_id_start),
            daemon=True
        )
        self.main_window.process_thread.start()
    
    def start_local_fetching(self):
        """从本地综合数据展示.htm文件处理数据"""
        from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QPushButton
        
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("实物中心本地数据处理")
        dialog.setModal(True)
        dialog.setFixedSize(550, 250)
        
        layout = QFormLayout()
        
        info_label = QLabel("选择包含综合数据展示.htm的目录")
        info_label.setStyleSheet("font-weight: bold; color: #1E3A5F;")
        layout.addRow("", info_label)
        
        source_input = QLineEdit()
        source_input.setPlaceholderText("综合数据展示.htm文件路径")
        
        def select_source():
            file_path, _ = QFileDialog.getOpenFileName(
                self.main_window, "选择综合数据展示.htm", "",
                "HTML Files (*.htm *.html)"
            )
            if file_path:
                source_input.setText(file_path)
        
        source_btn = QPushButton("浏览...")
        source_btn.clicked.connect(select_source)
        
        source_layout = QHBoxLayout()
        source_layout.addWidget(source_input, 1)
        source_layout.addWidget(source_btn)
        layout.addRow("数据文件:", source_layout)
        
        output_input = QLineEdit()
        output_input.setPlaceholderText("输出目录")
        
        def select_output():
            folder = QFileDialog.getExistingDirectory(self.main_window, "选择输出目录")
            if folder:
                output_input.setText(folder)
        
        output_btn = QPushButton("浏览...")
        output_btn.clicked.connect(select_output)
        
        output_layout = QHBoxLayout()
        output_layout.addWidget(output_input, 1)
        output_layout.addWidget(output_btn)
        layout.addRow("输出目录:", output_layout)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow("", buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        html_file = source_input.text().strip()
        output_dir = output_input.text().strip()
        
        if not html_file:
            QMessageBox.warning(self.main_window, "警告", "请选择综合数据展示.htm文件")
            return
        
        if not output_dir:
            QMessageBox.warning(self.main_window, "警告", "请选择输出目录")
            return
        
        if not os.path.exists(html_file):
            QMessageBox.warning(self.main_window, "警告", "文件不存在")
            return
        
        self.process_local_data(html_file, output_dir)
    
    def process_local_data(self, html_file, output_dir):
        """处理本地HTML文件"""
        self.main_window.process_btn.setEnabled(False)
        
        self.main_window.process_status_label.setText("正在处理本地数据...")
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
        self.main_window.process_log.append("开始处理本地数据...")
        self.main_window.process_log.append(f"HTML文件: {html_file}")
        
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'images'), exist_ok=True)
        
        try:
            with open(html_file, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            self.main_window.process_log.append("正在解析图片数据...")
            self.main_window.process_progress.setValue(20)
            
            images = []
            img_pattern = re.compile(r'class="yanxinImage ([^"]+)"[^>]*data-options="qssd:([0-9.]+),zzsd:([0-9.]+),yxtpbh:([^"]+)"')
            for m in img_pattern.finditer(content):
                images.append({
                    'imgName': m.group(1).strip(),
                    'qssd': float(m.group(2)),
                    'zzsd': float(m.group(3)),
                    'yxtpbh': m.group(4).strip()
                })
            
            self.main_window.process_log.append(f"找到 {len(images)} 张图片")
            self.main_window.process_progress.setValue(40)
            
            self.main_window.process_log.append("正在解析岩性数据...")
            
            fch_matches = re.findall(r'class="field-fch move-field(\d+)" title="([^"]+)"', content)
            hd_matches = re.findall(r'class="field-hd move-field(\d+)" title="([^"]+)"', content)
            ysmc_matches = re.findall(r'class="field-ysmc move-field(\d+)" title="([^"]+)"', content)
            dzms_matches = re.findall(r'class="field-dzms move-field(\d+)" title="([^"]+)"', content)
            
            self.main_window.process_log.append(f"找到 {len(ysmc_matches)} 层岩性数据")
            self.main_window.process_progress.setValue(60)
            
            lithology_data = []
            start_depth = 0.0
            for i, (idx, ysmc) in enumerate(ysmc_matches):
                hd = 0.0
                if i < len(hd_matches):
                    try:
                        hd = float(hd_matches[i][1])
                    except:
                        pass
                
                if hd > 0:
                    end_depth = start_depth + hd
                    dzms = dzms_matches[i][1] if i < len(dzms_matches) else ''
                    
                    lithology_data.append({
                        '分层号': i + 1,
                        '起始孔深(m)': round(start_depth, 2),
                        '终止孔深(m)': round(end_depth, 2),
                        '厚度(m)': hd,
                        '岩石名称': ysmc,
                        '地质描述': dzms
                    })
                    start_depth = end_depth
            
            lithology_file = os.path.join(output_dir, 'lithology_descriptions.json')
            with open(lithology_file, 'w', encoding='utf-8') as f:
                json.dump(lithology_data, f, ensure_ascii=False, indent=2)
            
            self.main_window.process_log.append(f"已保存岩性数据到: {lithology_file}")
            self.main_window.process_progress.setValue(80)
            
            image_descriptions = []
            for img in images:
                qssd = img['qssd']
                zzsd = img['zzsd']
                
                matched_lith = None
                for lith in lithology_data:
                    if qssd >= lith['起始孔深(m)'] and zzsd <= lith['终止孔深(m)']:
                        matched_lith = lith
                        break
                    if qssd < lith['终止孔深(m)'] and zzsd > lith['起始孔深(m)']:
                        matched_lith = lith
                        break
                
                image_descriptions.append({
                    'image_file': img['yxtpbh'],
                    'qssd': qssd,
                    'zzsd': zzsd,
                    '岩石名称': matched_lith['岩石名称'] if matched_lith else '',
                    '地质描述': matched_lith['地质描述'] if matched_lith else ''
                })
            
            image_file = os.path.join(output_dir, 'image_descriptions.json')
            with open(image_file, 'w', encoding='utf-8') as f:
                json.dump(image_descriptions, f, ensure_ascii=False, indent=2)
            
            self.main_window.process_log.append(f"已保存图片数据到: {image_file}")
            self.main_window.process_progress.setValue(100)
            
            self.main_window.process_status_label.setText("处理完成！")
            self.main_window.process_status_label.setStyleSheet("""
                font-size: 14px;
                font-weight: bold;
                color: #4CAF50;
                padding: 8px;
                background-color: #E8F5E9;
                border: 1px solid #4CAF50;
                border-radius: 4px;
            """)
            
            self.main_window.process_log.append("=" * 50)
            self.main_window.process_log.append(f"处理完成！")
            self.main_window.process_log.append(f"图片数量: {len(images)}")
            self.main_window.process_log.append(f"岩性层数: {len(lithology_data)}")
            self.main_window.process_log.append(f"岩性数据: {lithology_file}")
            self.main_window.process_log.append(f"图片数据: {image_file}")
            
        except Exception as e:
            self.main_window.process_status_label.setText(f"处理失败: {str(e)}")
            self.main_window.process_status_label.setStyleSheet("""
                font-size: 14px;
                font-weight: bold;
                color: #F44336;
                padding: 8px;
                background-color: #FFEBEE;
                border: 1px solid #F44336;
                border-radius: 4px;
            """)
            self.main_window.process_log.append(f"错误: {str(e)}")
        
        finally:
            self.main_window.process_btn.setEnabled(True)
