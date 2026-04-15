import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QGroupBox, QProgressBar, QTextEdit, QTableWidget, QButtonGroup,
    QTableWidgetItem, QMessageBox, QFileDialog
)
from PyQt6.QtWidgets import QHeaderView


class AnalysisPage:
    @staticmethod
    def create(main_window):
        page = QWidget()
        layout = QVBoxLayout()
        
        main_content = QHBoxLayout()
        
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        main_window.analysis_status_label = QLabel("等待开始...")
        main_window.analysis_status_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #1E3A5F;
            padding: 8px;
            background-color: white;
            border: 1px solid #E0E0E0;
            border-radius: 4px;
        """)
        right_layout.addWidget(main_window.analysis_status_label)
        
        main_window.analysis_progress = QProgressBar()
        main_window.analysis_progress.setTextVisible(True)
        main_window.analysis_progress.setFormat("%p%")
        right_layout.addWidget(main_window.analysis_progress)
        
        main_window.analysis_log = QTextEdit()
        main_window.analysis_log.setReadOnly(True)
        main_window.analysis_log.setStyleSheet("background-color: white; color: #333333; border: 1px solid #E0E0E0; border-radius: 4px;")
        right_layout.addWidget(QLabel("处理日志:"))
        right_layout.addWidget(main_window.analysis_log)
        
        view_button_panel = QHBoxLayout()
        
        view_button_panel.addStretch()
        
        view_classify_btn = QPushButton("显示岩性分类")
        view_classify_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """)
        view_classify_btn.clicked.connect(main_window.analysis_handler.view_lithology_classification)
        view_button_panel.addWidget(view_classify_btn)
        
        view_alteration_btn = QPushButton("显示蚀变分析")
        view_alteration_btn.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """)
        view_alteration_btn.clicked.connect(main_window.analysis_handler.view_lithology_classification)
        view_button_panel.addWidget(view_alteration_btn)
        
        export_btn = QPushButton("导出Excel")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """)
        export_btn.clicked.connect(main_window.analysis_handler.export_to_excel)
        view_button_panel.addWidget(export_btn)
        
        right_layout.addLayout(view_button_panel)
        
        main_window.analysis_table = QTableWidget()
        main_window.analysis_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #E0E0E0;
                background-color: white;
                color: #333333;
            }
            QTableWidget::item {
                padding: 5px;
                color: #333333;
            }
            QHeaderView::section {
                background-color: #1E3A5F;
                color: white;
                padding: 5px;
                font-weight: bold;
            }
        """)
        main_window.analysis_table.setColumnCount(4)
        main_window.analysis_table.setWordWrap(True)
        main_window.analysis_table.setColumnWidth(0, 120)
        main_window.analysis_table.setColumnWidth(1, 80)
        main_window.analysis_table.horizontalHeader().setStretchLastSection(True)
        main_window.analysis_table.resizeRowsToContents()
        
        right_layout.addWidget(QLabel("统计表格:"))
        right_layout.addWidget(main_window.analysis_table, 1)
        
        stats_button_panel = QHBoxLayout()
        stats_button_panel.addStretch()
        
        stats_btn = QPushButton("岩性统计")
        stats_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        stats_btn.clicked.connect(main_window.analysis_handler.show_process_stats)
        stats_button_panel.addWidget(stats_btn)
        
        right_layout.addLayout(stats_button_panel)
        
        right_panel.setLayout(right_layout)
        
        main_content.addWidget(right_panel, 1)
        
        layout.addLayout(main_content)
        
        page.setLayout(layout)
        return page


class AnalysisHandler:
    def __init__(self, main_window):
        self.main_window = main_window
    
    def show_process_stats(self):
        json_file, _ = QFileDialog.getOpenFileName(
            self.main_window, "选择处理结果文件", "", "JSON文件 (*.json)"
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
        
        self.main_window.analysis_log.clear()
        self.main_window.analysis_log.append(f"正在加载: {json_file}")
        
        lithology_stats = {}
        lith_order = {}
        proj_order = {}
        for idx, item in enumerate(data):
            lith = item.get('lithology', '')
            proj = item.get('project', '')
            if lith:
                if proj not in proj_order:
                    proj_order[proj] = len(proj_order)
                key = (lith, proj)
                if key not in lithology_stats:
                    lithology_stats[key] = {'lithology': lith, 'project': proj, 'count': 0, 'description': item.get('lithology_description', '')}
                    lith_order[key] = len(lith_order)
                lithology_stats[key]['count'] += 1
        
        for key in lithology_stats:
            lithology_stats[key]['order'] = lith_order[key]
            lithology_stats[key]['proj_order'] = proj_order[key[1]]
        
        self.main_window.analysis_table.setColumnCount(4)
        self.main_window.analysis_table.setHorizontalHeaderLabels(["项目", "岩性名称", "图片数", "岩性描述"])
        self.main_window.analysis_table.setColumnWidth(0, 120)
        self.main_window.analysis_table.setColumnWidth(1, 120)
        self.main_window.analysis_table.setColumnWidth(2, 80)
        self.main_window.analysis_table.horizontalHeader().setStretchLastSection(True)
        
        sorted_lith = sorted(lithology_stats.values(), key=lambda x: (x.get('proj_order', 0), x.get('order', 0)))
        self.main_window.analysis_table.setRowCount(len(sorted_lith))
        
        for i, info in enumerate(sorted_lith):
            self.main_window.analysis_table.setItem(i, 0, QTableWidgetItem(info['project']))
            self.main_window.analysis_table.setItem(i, 1, QTableWidgetItem(info['lithology']))
            self.main_window.analysis_table.setItem(i, 2, QTableWidgetItem(str(info['count'])))
            desc = info['description']
            self.main_window.analysis_table.setItem(i, 3, QTableWidgetItem(desc.replace('\n', ' ') if desc else ''))
        
        self.main_window.analysis_table.resizeRowsToContents()
        self.main_window.analysis_log.append(f"已加载 {len(data)} 条记录，按项目/岩性统计共 {len(sorted_lith)} 项")
    
    def view_lithology_classification(self):
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
        
        self.main_window.analysis_log.clear()
        self.main_window.analysis_log.append(f"已加载岩性分类结果: {json_file}")
        self.main_window.analysis_log.append(f"总记录数: {len(data)}")
        
        rock_groups = {}
        for item in data:
            rock_name = item.get('岩性名称', '') or '未分类'
            lithology = item.get('lithology', '')
            if rock_name not in rock_groups:
                rock_groups[rock_name] = {'lithologies': set(), 'count': 0}
            rock_groups[rock_name]['lithologies'].add(lithology)
            rock_groups[rock_name]['count'] += 1
        
        self.main_window.analysis_table.setColumnCount(4)
        self.main_window.analysis_table.setHorizontalHeaderLabels(["标准岩性", "图片数", "分类数", "对应原始岩性"])
        self.main_window.analysis_table.setColumnWidth(0, 100)
        self.main_window.analysis_table.setColumnWidth(1, 80)
        self.main_window.analysis_table.setColumnWidth(2, 80)
        self.main_window.analysis_table.horizontalHeader().setStretchLastSection(True)
        
        sorted_rocks = sorted(rock_groups.items(), key=lambda x: x[1]['count'], reverse=True)
        self.main_window.analysis_table.setRowCount(len(sorted_rocks))
        
        for i, (rock_name, info) in enumerate(sorted_rocks):
            self.main_window.analysis_table.setItem(i, 0, QTableWidgetItem(rock_name))
            self.main_window.analysis_table.setItem(i, 1, QTableWidgetItem(str(info['count'])))
            self.main_window.analysis_table.setItem(i, 2, QTableWidgetItem(str(len(info['lithologies']))))
            lithologies_str = ", ".join(sorted(info['lithologies'])[:5])
            if len(info['lithologies']) > 5:
                lithologies_str += f" 等{len(info['lithologies'])}种"
            self.main_window.analysis_table.setItem(i, 3, QTableWidgetItem(lithologies_str))
        
        self.main_window.analysis_table.resizeRowsToContents()
        self.main_window.analysis_status_label.setText(f"显示岩性分类 - 共 {len(rock_groups)} 种岩性")
        self.main_window.status_bar.showMessage(f"已加载岩性分类结果")
    
    def load_alteration_results(self):
        json_file, _ = QFileDialog.getOpenFileName(
            self.main_window, "选择蚀变分析后的JSON文件", "", "JSON文件 (*.json)"
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
        
        records_with_alt = sum(1 for item in data if item.get('蚀变类型', ''))
        
        self.main_window.analysis_log.clear()
        self.main_window.analysis_log.append(f"已加载蚀变分析结果: {json_file}")
        self.main_window.analysis_log.append(f"总记录数: {len(data)}")
        self.main_window.analysis_log.append(f"含蚀变记录: {records_with_alt} 条")
        
        alteration_groups = {}
        for item in data:
            rock_name = item.get('岩性名称', '') or '未分类'
            alteration = item.get('蚀变类型', '')
            if alteration:
                if rock_name not in alteration_groups:
                    alteration_groups[rock_name] = {'alterations': set(), 'count': 0}
                alteration_groups[rock_name]['alterations'].add(alteration)
                alteration_groups[rock_name]['count'] += 1
        
        self.main_window.analysis_table.setColumnCount(3)
        self.main_window.analysis_table.setHorizontalHeaderLabels(["岩性", "蚀变类型数", "含蚀变条数"])
        self.main_window.analysis_table.setColumnWidth(0, 150)
        self.main_window.analysis_table.setColumnWidth(1, 100)
        self.main_window.analysis_table.horizontalHeader().setStretchLastSection(True)
        
        sorted_alterations = sorted(alteration_groups.items(), key=lambda x: x[1]['count'], reverse=True)
        self.main_window.analysis_table.setRowCount(len(sorted_alterations))
        
        for i, (rock_name, info) in enumerate(sorted_alterations):
            self.main_window.analysis_table.setItem(i, 0, QTableWidgetItem(rock_name))
            self.main_window.analysis_table.setItem(i, 1, QTableWidgetItem(str(len(info['alterations']))))
            self.main_window.analysis_table.setItem(i, 2, QTableWidgetItem(str(info['count'])))
        
        self.main_window.analysis_table.resizeRowsToContents()
        self.main_window.analysis_status_label.setText(f"显示蚀变分析 - {records_with_alt}/{len(data)} 条含蚀变")
        self.main_window.status_bar.showMessage("已加载蚀变分析结果")
    
    def export_to_excel(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self.main_window, "保存Excel文件", "", "Excel文件 (*.xlsx)"
        )
        if not file_path:
            return
        
        try:
            import pandas as pd
            
            rows = []
            for row in range(self.main_window.analysis_table.rowCount()):
                row_data = []
                for col in range(self.main_window.analysis_table.columnCount()):
                    item = self.main_window.analysis_table.item(row, col)
                    row_data.append(item.text() if item else "")
                rows.append(row_data)
            
            if not rows:
                QMessageBox.warning(self.main_window, "警告", "没有可导出的数据")
                return
            
            headers = [self.main_window.analysis_table.horizontalHeaderItem(i).text() 
                     for i in range(self.main_window.analysis_table.columnCount())]
            
            df = pd.DataFrame(rows, columns=headers)
            df.to_excel(file_path, index=False)
            
            QMessageBox.information(self.main_window, "完成", f"已导出到: {file_path}")
            self.main_window.analysis_log.append(f"已导出到: {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self.main_window, "错误", f"导出失败: {str(e)}")