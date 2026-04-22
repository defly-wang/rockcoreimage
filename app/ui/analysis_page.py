import os
import re
import json
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGroupBox,
    QProgressBar,
    QTextEdit,
    QTableWidget,
    QButtonGroup,
    QTableWidgetItem,
    QMessageBox,
    QFileDialog,
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
        main_window.analysis_log.setStyleSheet(
            "background-color: white; color: #333333; border: 1px solid #E0E0E0; border-radius: 4px;"
        )
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
        """)
        view_classify_btn.clicked.connect(
            main_window.analysis_handler.view_lithology_classification
        )
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
        """)
        view_alteration_btn.clicked.connect(
            main_window.analysis_handler.view_alteration_analysis
        )
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

        action_button_panel = QHBoxLayout()
        action_button_panel.addStretch()

        stats_btn = QPushButton("岩性统计")
        stats_btn.setStyleSheet("""
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
        """)
        stats_btn.clicked.connect(main_window.lithology_handler.show_lithology_stats)
        action_button_panel.addWidget(stats_btn)

        classify_btn = QPushButton("岩性分类")
        classify_btn.setStyleSheet("""
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
        """)
        classify_btn.clicked.connect(
            main_window.analysis_handler.start_lithology_classify
        )
        action_button_panel.addWidget(classify_btn)

        adjust_btn = QPushButton("岩性调整")
        adjust_btn.setStyleSheet("""
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
        """)
        adjust_btn.clicked.connect(
            main_window.lithology_handler.adjust_lithology
        )
        action_button_panel.addWidget(adjust_btn)

        alteration_btn = QPushButton("蚀变分析")
        alteration_btn.setStyleSheet("""
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
        alteration_btn.clicked.connect(
            main_window.analysis_handler.start_alteration_analysis
        )
        action_button_panel.addWidget(alteration_btn)

        detail_btn = QPushButton("深入分析")
        detail_btn.setStyleSheet("""
            QPushButton {
                background-color: #E91E63;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #C2185B;
            }
        """)
        detail_btn.clicked.connect(main_window.analysis_handler.start_detail_analysis)

        ai_btn = QPushButton("AI分析")
        ai_btn.setStyleSheet("""
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
        """)
        ai_btn.clicked.connect(main_window.analysis_handler.start_ai_analysis)
        action_button_panel.addWidget(ai_btn)
        action_button_panel.addWidget(detail_btn)

        right_layout.addLayout(action_button_panel)

        right_panel.setLayout(right_layout)

        main_content.addWidget(right_panel, 1)

        layout.addLayout(main_content)

        page.setLayout(layout)
        return page


class AnalysisHandler:
    def __init__(self, main_window):
        self.main_window = main_window

    def start_lithology_classify(self):
        json_file, _ = QFileDialog.getOpenFileName(
            self.main_window, "选择JSON文件", "", "JSON文件 (*.json)"
        )
        if not json_file:
            return

        import os

        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        project_root = os.path.dirname(app_dir)
        config_file = os.path.join(project_root, "config", "rock_types_flat.json")

        if not os.path.exists(config_file):
            QMessageBox.warning(
                self.main_window, "错误", f"找不到配置文件: {config_file}"
            )
            return

        output_file = json_file.replace(".json", "_classified.json")

        self.main_window.analysis_status_label.setText("正在初始化...")
        self.main_window.analysis_progress.setValue(0)
        self.main_window.analysis_log.clear()
        self.main_window.analysis_log.append("开始岩性分类...")

        from app.modules.data_processor import DataProcessor

        data_processor = DataProcessor()

        data_processor.progress_updated.connect(self.on_classify_progress)
        data_processor.processing_finished.connect(self.on_classify_finished)
        data_processor.error_occurred.connect(self.on_processing_error)

        from threading import Thread

        classify_thread = Thread(
            target=data_processor.classify_lithology,
            args=(json_file, config_file, output_file),
            daemon=True,
        )
        classify_thread.start()

    def on_classify_progress(self, value, message):
        self.main_window.analysis_progress.setValue(value)
        self.main_window.analysis_log.append(message)
        self.main_window.status_bar.showMessage(message)
        self.main_window.analysis_status_label.setText(message)

    def on_classify_finished(self, output_file, stats):
        import json
        import os

        self.main_window.analysis_progress.setValue(100)
        self.main_window.analysis_status_label.setText(
            f"分类完成 - 匹配 {stats.get('matched', 0)}/{stats.get('total', 0)} 条"
        )
        self.main_window.analysis_log.append(f"分类完成!")
        self.main_window.analysis_log.append(f"输出文件: {output_file}")

        try:
            with open(output_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            project_root = os.path.dirname(app_dir)
            config_file = os.path.join(project_root, 'config', 'rock_types_flat.json')
            rock_category_map = {}
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
                for rock in config_data.get('rocks', []):
                    rock_category_map[rock['name']] = rock.get('category', '')
            except Exception:
                pass

            rock_groups = {}
            for item in data:
                rock_name = item.get("rock_name", "") or "未分类"
                lithology = item.get("lithology", "")
                if rock_name not in rock_groups:
                    rock_groups[rock_name] = {"lithologies": set(), "count": 0}
                rock_groups[rock_name]["lithologies"].add(lithology)
                rock_groups[rock_name]["count"] += 1

            category_counts = {'岩浆岩': 0, '沉积岩': 0, '变质岩': 0}
            for rock_name in rock_groups.keys():
                category = rock_category_map.get(rock_name, '')
                if category in category_counts:
                    category_counts[category] += 1

            self.main_window.analysis_table.setColumnCount(4)
            self.main_window.analysis_table.setHorizontalHeaderLabels(
                ["标准岩性", "图片数", "分类数", "对应原始岩性"]
            )
            self.main_window.analysis_table.setColumnWidth(0, 100)
            self.main_window.analysis_table.setColumnWidth(1, 80)
            self.main_window.analysis_table.setColumnWidth(2, 80)
            self.main_window.analysis_table.horizontalHeader().setStretchLastSection(
                True
            )

            sorted_rocks = sorted(
                rock_groups.items(), key=lambda x: x[1]["count"], reverse=True
            )
            self.main_window.analysis_table.setRowCount(len(sorted_rocks))

            for i, (rock_name, info) in enumerate(sorted_rocks):
                self.main_window.analysis_table.setItem(
                    i, 0, QTableWidgetItem(rock_name)
                )
                self.main_window.analysis_table.setItem(
                    i, 1, QTableWidgetItem(str(info["count"]))
                )
                self.main_window.analysis_table.setItem(
                    i, 2, QTableWidgetItem(str(len(info["lithologies"])))
                )
                lithologies_str = ", ".join(sorted(info["lithologies"]))
                self.main_window.analysis_table.setItem(
                    i, 3, QTableWidgetItem(lithologies_str)
                )

            self.main_window.analysis_table.resizeRowsToContents()
            cat_stat = f"岩浆岩{category_counts['岩浆岩']}种/沉积岩{category_counts['沉积岩']}种/变质岩{category_counts['变质岩']}种"
            self.main_window.analysis_log.append(
                f"显示分类结果 - 共 {len(rock_groups)} 种岩性（{cat_stat}）"
            )

        except Exception as e:
            self.main_window.analysis_log.append(f"加载结果失败: {str(e)}")

        self.main_window.status_bar.showMessage("分类完成")

    def on_processing_error(self, error_message):
        QMessageBox.critical(self.main_window, "错误", error_message)
        self.main_window.analysis_status_label.setText(f"错误: {error_message}")

    def start_alteration_analysis(self):
        json_file, _ = QFileDialog.getOpenFileName(
            self.main_window, "选择岩性分类后的JSON文件", "", "JSON文件 (*.json)"
        )
        if not json_file:
            return

        import os

        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        project_root = os.path.dirname(app_dir)
        alteration_config_file = os.path.join(
            project_root, "config", "alteration_types.json"
        )

        if not os.path.exists(alteration_config_file):
            QMessageBox.warning(
                self.main_window,
                "错误",
                f"找不到蚀变配置文件: {alteration_config_file}",
            )
            return

        output_file = json_file.replace(".json", "_alteration.json")

        self.main_window.analysis_status_label.setText("正在蚀变分析...")
        self.main_window.analysis_progress.setValue(0)
        self.main_window.analysis_log.clear()
        self.main_window.analysis_log.append("开始蚀变分析...")

        from app.modules.data_processor import DataProcessor

        data_processor = DataProcessor()

        data_processor.progress_updated.connect(self.on_alteration_progress)
        data_processor.processing_finished.connect(self.on_alteration_finished)
        data_processor.error_occurred.connect(self.on_processing_error)

        from threading import Thread

        alteration_thread = Thread(
            target=data_processor.analyze_alteration,
            args=(json_file, alteration_config_file, output_file),
            daemon=True,
        )
        alteration_thread.start()

    def on_alteration_progress(self, value, message):
        self.main_window.analysis_progress.setValue(value)
        self.main_window.analysis_log.append(message)
        self.main_window.status_bar.showMessage(message)
        self.main_window.analysis_status_label.setText(message)

    def on_alteration_finished(self, output_file, stats):
        import json

        self.main_window.analysis_progress.setValue(100)

        records_with_alt = stats.get("records_with_alteration", 0)
        total_records = stats.get("total_records", 0)

        self.main_window.analysis_status_label.setText(
            f"蚀变分析完成 - {records_with_alt}/{total_records} 条含蚀变"
        )
        self.main_window.analysis_log.append(f"蚀变分析完成!")
        self.main_window.analysis_log.append(f"总记录数: {total_records}")
        self.main_window.analysis_log.append(f"含蚀变记录: {records_with_alt} 条")

        try:
            with open(output_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            records = [
                (
                    item.get("rock_name", "") or "未分类",
                    item.get("lithology", ""),
                    item.get("蚀变类型", ""),
                    item.get("lithology_description", ""),
                )
                for item in data
            ]
            records.sort(key=lambda x: (x[0], x[1]))

            self.main_window.analysis_table.setColumnCount(6)
            self.main_window.analysis_table.setHorizontalHeaderLabels(
                ["标准岩性", "图片数", "分类数", "原始岩性", "蚀变类型", "岩性描述"]
            )
            self.main_window.analysis_table.setColumnWidth(0, 100)
            self.main_window.analysis_table.setColumnWidth(1, 60)
            self.main_window.analysis_table.setColumnWidth(2, 60)
            self.main_window.analysis_table.setColumnWidth(3, 200)
            self.main_window.analysis_table.setColumnWidth(4, 120)
            self.main_window.analysis_table.horizontalHeader().setStretchLastSection(
                True
            )

            rock_groups = {}
            for rock_name, lithology, alteration, description in records:
                if rock_name not in rock_groups:
                    rock_groups[rock_name] = {}
                if lithology not in rock_groups[rock_name]:
                    rock_groups[rock_name][lithology] = {
                        "count": 0,
                        "alterations": set(),
                        "description": description,
                    }
                rock_groups[rock_name][lithology]["count"] += 1
                if alteration:
                    rock_groups[rock_name][lithology]["alterations"].add(alteration)

            rows = []
            for rock_name in sorted(rock_groups.keys()):
                for lithology, info in rock_groups[rock_name].items():
                    alterations_str = (
                        ", ".join(sorted(info["alterations"]))
                        if info["alterations"]
                        else "-"
                    )
                    desc = info["description"] or "-"
                    rows.append(
                        (
                            rock_name,
                            str(info["count"]),
                            "1",
                            lithology,
                            alterations_str,
                            desc,
                        )
                    )

            self.main_window.analysis_table.setRowCount(len(rows))
            for row, (
                rock_name,
                count,
                _,
                lithology,
                alteration,
                description,
            ) in enumerate(rows):
                self.main_window.analysis_table.setItem(
                    row, 0, QTableWidgetItem(rock_name)
                )
                self.main_window.analysis_table.setItem(row, 1, QTableWidgetItem(count))
                self.main_window.analysis_table.setItem(row, 2, QTableWidgetItem("1"))
                self.main_window.analysis_table.setItem(
                    row, 3, QTableWidgetItem(lithology)
                )
                self.main_window.analysis_table.setItem(
                    row, 4, QTableWidgetItem(alteration)
                )
                self.main_window.analysis_table.setItem(
                    row, 5, QTableWidgetItem(description)
                )

            self.main_window.analysis_table.resizeRowsToContents()
            self.main_window.analysis_log.append(f"显示蚀变分析结果")

        except Exception as e:
            self.main_window.analysis_log.append(f"加载结果失败: {str(e)}")

        self.main_window.status_bar.showMessage("蚀变分析完成")

    def show_process_stats(self):
        json_file, _ = QFileDialog.getOpenFileName(
            self.main_window, "选择处理结果文件", "", "JSON文件 (*.json)"
        )
        if not json_file:
            return

        import json

        try:
            with open(json_file, "r", encoding="utf-8") as f:
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
            lith = item.get("lithology", "")
            proj = item.get("project", "")
            start_depth = item.get("start_depth", 0)
            end_depth = item.get("end_depth", 0)
            if lith:
                if proj not in proj_order:
                    proj_order[proj] = len(proj_order)
                key = (lith, proj)
                if key not in lithology_stats:
                    lithology_stats[key] = {
                        "lithology": lith,
                        "project": proj,
                        "count": 0,
                        "description": item.get("lithology_description", ""),
                        "start_depth": start_depth,
                        "end_depth": end_depth,
                    }
                    lith_order[key] = len(lith_order)
                else:
                    if start_depth < lithology_stats[key]["start_depth"]:
                        lithology_stats[key]["start_depth"] = start_depth
                    if end_depth > lithology_stats[key]["end_depth"]:
                        lithology_stats[key]["end_depth"] = end_depth
                lithology_stats[key]["count"] += 1

        for key in lithology_stats:
            lithology_stats[key]["order"] = lith_order[key]
            lithology_stats[key]["proj_order"] = proj_order[key[1]]

        self.main_window.analysis_table.setColumnCount(6)
        self.main_window.analysis_table.setHorizontalHeaderLabels(
            ["项目", "岩性名称", "起始深度(m)", "结束深度(m)", "图片数", "岩性描述"]
        )
        self.main_window.analysis_table.setColumnWidth(0, 100)
        self.main_window.analysis_table.setColumnWidth(1, 100)
        self.main_window.analysis_table.setColumnWidth(2, 80)
        self.main_window.analysis_table.setColumnWidth(3, 80)
        self.main_window.analysis_table.setColumnWidth(4, 60)
        self.main_window.analysis_table.horizontalHeader().setStretchLastSection(True)

        sorted_lith = sorted(
            lithology_stats.values(),
            key=lambda x: (x.get("proj_order", 0), x.get("order", 0)),
        )
        self.main_window.analysis_table.setRowCount(len(sorted_lith))

        for i, info in enumerate(sorted_lith):
            self.main_window.analysis_table.setItem(
                i, 0, QTableWidgetItem(info["project"])
            )
            self.main_window.analysis_table.setItem(
                i, 1, QTableWidgetItem(info["lithology"])
            )
            self.main_window.analysis_table.setItem(
                i, 2, QTableWidgetItem(str(info.get("start_depth", 0)))
            )
            self.main_window.analysis_table.setItem(
                i, 3, QTableWidgetItem(str(info.get("end_depth", 0)))
            )
            self.main_window.analysis_table.setItem(
                i, 4, QTableWidgetItem(str(info["count"]))
            )
            desc = info["description"]
            self.main_window.analysis_table.setItem(
                i, 5, QTableWidgetItem(desc.replace("\n", " ") if desc else "")
            )

        self.main_window.analysis_table.resizeRowsToContents()
        self.main_window.analysis_log.append(
            f"已加载 {len(data)} 条记录，按项目/岩性统计共 {len(sorted_lith)} 项"
        )

    def start_detail_analysis(self):
        from PyQt6.QtWidgets import QFileDialog

        dir_path = QFileDialog.getExistingDirectory(
            self.main_window, "选择处理结果目录"
        )
        if not dir_path:
            return

        lithology_file = os.path.join(dir_path, "lithology_descriptions.json")

        if not os.path.exists(lithology_file):
            QMessageBox.warning(
                self.main_window, "错误", "找不到lithology_descriptions.json文件"
            )
            return

        try:
            with open(lithology_file, "r", encoding="utf-8") as f:
                lithology_data = json.load(f)
        except Exception as e:
            QMessageBox.warning(self.main_window, "错误", f"无法读取文件: {str(e)}")
            return

        self.main_window.analysis_status_label.setText("正在深入分析...")
        self.main_window.analysis_progress.setValue(0)
        self.main_window.analysis_log.clear()
        self.main_window.analysis_log.append(f"开始深入分析: {lithology_file}")

        max_id = max((lith.get("id", 0) for lith in lithology_data), default=0)

        new_records = []

        depth_pattern = re.compile(r"(\d+\.?\d*)\s*[-–—至]\s*(\d+\.?\d*)\s*m")
        lith_keywords = [
            "钾化花岗岩",
            "黄铁绢英岩化花岗岩",
            "黄铁绢英岩化碎裂岩",
            "黄铁绢英岩化花岗质碎裂岩",
            "闪长岩",
            "石英闪长岩",
            "辉长岩",
            "玄武岩",
            "安山岩",
            "流纹岩",
            "片麻岩",
            "片岩",
            "千枚岩",
            "板岩",
            "大理岩",
            "石英岩",
            "砂岩",
            "页岩",
            "灰岩",
            "白云岩",
            "粘土岩",
            "泥岩",
            "砾岩",
            "角砾岩",
            "凝灰岩",
            "断层泥",
            "碎裂岩",
            "糜棱岩",
            "斜长角闪石",
            "黑云变粒岩",
            "黑云角闪片岩",
            "含磁铁黑云角闪片岩",
            "磁铁角闪石英岩",
            "含海绿石石英砂岩",
            "二长花岗岩",
        ]

        for idx, lith in enumerate(lithology_data):
            if idx % 100 == 0:
                self.main_window.analysis_progress.setValue(
                    int(idx * 100 / len(lithology_data))
                )

            original_id = lith.get("id", 0)
            original_lith = lith.get("lithology", "")
            project = lith.get("project", "")
            borehole = lith.get("borehole", "")
            start_depth = lith.get("start_depth", 0)
            end_depth = lith.get("end_depth", 0)
            desc = lith.get("description", "")

            if not desc:
                new_records.append(
                    {
                        "id": max_id + len(new_records) + 1,
                        "project": project,
                        "borehole": borehole,
                        "lithology": original_lith,
                        "start_depth": start_depth,
                        "end_depth": end_depth,
                        "description": desc,
                        "original_lithology": original_lith,
                        "original_id": original_id,
                    }
                )
                continue

            temp_desc = desc.replace("|", "。").replace("\\n", "。")
            segments = [
                s.strip() for s in re.split(r"[。；\n]", temp_desc) if s.strip()
            ]

            if not segments:
                new_records.append(
                    {
                        "id": max_id + len(new_records) + 1,
                        "project": project,
                        "borehole": borehole,
                        "lithology": original_lith,
                        "start_depth": start_depth,
                        "end_depth": end_depth,
                        "description": desc,
                        "original_lithology": original_lith,
                        "original_id": original_id,
                    }
                )
                continue

            found_segments = []
            for seg in segments:
                matches = list(depth_pattern.finditer(seg))
                if matches:
                    for m in matches:
                        ds = float(m.group(1))
                        de = float(m.group(2))
                        if ds >= start_depth and de <= end_depth and ds < de:
                            seg_text = (
                                seg[m.end() :].strip() if m.end() < len(seg) else seg
                            )
                            new_lith = original_lith
                            for kw in lith_keywords:
                                if kw in seg:
                                    new_lith = kw
                                    break
                            found_segments.append(
                                {
                                    "start": ds,
                                    "end": de,
                                    "text": seg_text if seg_text else seg,
                                    "lithology": new_lith,
                                }
                            )

            if found_segments:
                for seg in found_segments:
                    new_records.append(
                        {
                            "id": max_id + len(new_records) + 1,
                            "project": project,
                            "borehole": borehole,
                            "lithology": seg["lithology"],
                            "start_depth": seg["start"],
                            "end_depth": seg["end"],
                            "description": seg["text"],
                            "original_lithology": original_lith,
                            "original_id": original_id,
                        }
                    )
            else:
                new_records.append(
                    {
                        "id": max_id + len(new_records) + 1,
                        "project": project,
                        "borehole": borehole,
                        "lithology": original_lith,
                        "start_depth": start_depth,
                        "end_depth": end_depth,
                        "description": desc,
                        "original_lithology": original_lith,
                        "original_id": original_id,
                    }
                )

        output_file = os.path.join(dir_path, "lithology_detail.json")

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(new_records, f, ensure_ascii=False, indent=2)

            self.main_window.analysis_progress.setValue(100)
            self.main_window.analysis_status_label.setText(
                f"深入分析完成 - 共 {len(new_records)} 条记录"
            )
            self.main_window.analysis_log.append(f"深入分析完成!")
            self.main_window.analysis_log.append(f"原记录: {len(lithology_data)} 条")
            self.main_window.analysis_log.append(f"分析后: {len(new_records)} 条")
            self.main_window.analysis_log.append(f"输出文件: {output_file}")

            self.main_window.analysis_table.setColumnCount(8)
            self.main_window.analysis_table.setHorizontalHeaderLabels(
                [
                    "ID",
                    "项目",
                    "钻孔",
                    "岩性名称",
                    "开始深度",
                    "结束深度",
                    "原岩性",
                    "描述",
                ]
            )
            self.main_window.analysis_table.setColumnWidth(0, 40)
            self.main_window.analysis_table.setColumnWidth(1, 80)
            self.main_window.analysis_table.setColumnWidth(2, 80)
            self.main_window.analysis_table.setColumnWidth(3, 100)
            self.main_window.analysis_table.setColumnWidth(4, 80)
            self.main_window.analysis_table.setColumnWidth(5, 80)
            self.main_window.analysis_table.setColumnWidth(6, 100)
            self.main_window.analysis_table.horizontalHeader().setStretchLastSection(
                True
            )

            self.main_window.analysis_table.setRowCount(len(new_records))

            for i, rec in enumerate(new_records):
                self.main_window.analysis_table.setItem(
                    i, 0, QTableWidgetItem(str(rec.get("id", "")))
                )
                self.main_window.analysis_table.setItem(
                    i, 1, QTableWidgetItem(rec.get("project", ""))
                )
                self.main_window.analysis_table.setItem(
                    i, 2, QTableWidgetItem(rec.get("borehole", ""))
                )
                self.main_window.analysis_table.setItem(
                    i, 3, QTableWidgetItem(rec.get("lithology", ""))
                )
                self.main_window.analysis_table.setItem(
                    i, 4, QTableWidgetItem(str(rec.get("start_depth", 0)))
                )
                self.main_window.analysis_table.setItem(
                    i, 5, QTableWidgetItem(str(rec.get("end_depth", 0)))
                )
                self.main_window.analysis_table.setItem(
                    i, 6, QTableWidgetItem(rec.get("original_lithology", ""))
                )
                self.main_window.analysis_table.setItem(
                    i,
                    7,
                    QTableWidgetItem(
                        rec.get("description", "")[:50]
                        if rec.get("description", "")
                        else ""
                    ),
                )

            self.main_window.analysis_table.resizeRowsToContents()
            self.main_window.status_bar.showMessage("深入分析完成")

        except Exception as e:
            QMessageBox.critical(self.main_window, "错误", f"保存文件失败: {str(e)}")
            self.main_window.analysis_status_label.setText(f"错误: {str(e)}")

        return

    def start_ai_analysis(self):
        from PyQt6.QtWidgets import QFileDialog, QInputDialog

        dir_path = QFileDialog.getExistingDirectory(
            self.main_window, "选择处理结果目录"
        )
        if not dir_path:
            return

        lithology_file = os.path.join(dir_path, "lithology_descriptions.json")

        if not os.path.exists(lithology_file):
            QMessageBox.warning(
                self.main_window, "错误", "找不到lithology_descriptions.json文件"
            )
            return

        api_key, ok = QInputDialog.getText(
            self.main_window,
            "硅基流动 API",
            "请输入硅基流动 API Key:",
        )
        if not ok or not api_key:
            return

        try:
            with open(lithology_file, "r", encoding="utf-8") as f:
                lithology_data = json.load(f)
        except Exception as e:
            QMessageBox.warning(self.main_window, "错误", f"无法读取文件: {str(e)}")
            return

        self.main_window.analysis_status_label.setText("正在AI分析...")
        self.main_window.analysis_progress.setValue(0)
        self.main_window.analysis_log.clear()
        self.main_window.analysis_log.append(f"开始AI分析: {lithology_file}")

        try:
            import requests
            import datetime
        except ImportError:
            QMessageBox.warning(
                self.main_window, "错误", "请安装requests库: pip install requests"
            )
            return

        max_id = max((lith.get("id", 0) for lith in lithology_data), default=0)
        new_records = []
        total_calls = len(lithology_data)
        success_count = 0

        for idx, lith in enumerate(lithology_data):
            self.main_window.analysis_progress.setValue(int(idx * 100 / total_calls))

            original_id = lith.get("id", 0)
            original_lith = lith.get("lithology", "")
            project = lith.get("project", "")
            borehole = lith.get("borehole", "")
            start_depth = lith.get("start_depth", 0)
            end_depth = lith.get("end_depth", 0)
            desc = lith.get("description", "")

            user_content = f"""分析以下岩性信息，根据岩性描述中内中包含的各个深度中的描述内容，提取各个深度的岩性，如果岩性与原始岩性不同,返回该层数据,并返回该层的描述。返回各种岩性JSON数据，格式：{{"lithology": "岩性名称", "start_depth": 起始深度, "end_depth": 结束深度, "description": "岩性描述"}}
原岩性名称: {original_lith}
起始深度: {start_depth} m
结束深度: {end_depth} m 
岩性描述： {desc}"""

            ok1 = (
                QMessageBox.question(
                    self.main_window,
                    "继续分析吗？",
                    "是否继续分析下一条记录？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                == QMessageBox.StandardButton.Yes
            )

            if not ok1:
                continue

            self.main_window.analysis_log.append(
                f"[API调用 {idx + 1}/{total_calls}] {project} {borehole} {start_depth}-{end_depth}m [请求中...]"
            )

            try:
                start_time = datetime.datetime.now()

                response = requests.post(
                    "https://api.siliconflow.cn/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "Pro/zai-org/GLM-5.1",
                        "messages": [
                            {
                                "role": "system",
                                "content": "你是岩矿分析专家，负责分析岩性描述并提取岩性信息。",
                            },
                            {"role": "user", "content": user_content},
                        ],
                        "max_tokens": 5000,
                        "response_format": {"type": "json_object"},
                    },
                    timeout=600,
                )

                end_time = datetime.datetime.now()
                duration = (end_time - start_time).total_seconds()

                if response.status_code == 200:
                    self.main_window.analysis_log.append(
                        f"[成功] {project} {borehole} {start_depth}-{end_depth}m [耗时: {duration:.2f}s]"
                    )
                    success_count += 1
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]

                    self.main_window.analysis_log.append(user_content)
                    self.main_window.analysis_log.append(f"[返回] {content}")

                    try:
                        ai_result = json.loads(content)
                        if isinstance(ai_result, list):
                            for item in ai_result:
                                new_records.append(
                                    {
                                        "id": max_id + len(new_records) + 1,
                                        "project": project,
                                        "borehole": borehole,
                                        "lithology": item.get(
                                            "lithology", original_lith
                                        ),
                                        "start_depth": item.get(
                                            "start_depth", start_depth
                                        ),
                                        "end_depth": item.get("end_depth", end_depth),
                                        "description": item.get("description", desc),
                                        "original_lithology": original_lith,
                                        "original_id": original_id,
                                    }
                                )
                            continue
                        elif "result" in ai_result and isinstance(
                            ai_result["result"], list
                        ):
                            for item in ai_result["result"]:
                                new_records.append(
                                    {
                                        "id": max_id + len(new_records) + 1,
                                        "project": project,
                                        "borehole": borehole,
                                        "lithology": item.get(
                                            "lithology", original_lith
                                        ),
                                        "start_depth": item.get(
                                            "start_depth", start_depth
                                        ),
                                        "end_depth": item.get("end_depth", end_depth),
                                        "description": item.get("description", desc),
                                        "original_lithology": original_lith,
                                        "original_id": original_id,
                                    }
                                )
                            continue
                        else:
                            new_lith = ai_result.get("lithology", original_lith)
                            new_start = ai_result.get("start_depth", start_depth)
                            new_end = ai_result.get("end_depth", end_depth)
                            new_desc = ai_result.get("description", desc)
                    except json.JSONDecodeError:
                        new_lith = original_lith
                        new_start = start_depth
                        new_end = end_depth
                        new_desc = desc
                        self.main_window.analysis_log.append(
                            f"[警告] JSON解析失败，使用原始描述"
                        )
                else:
                    self.main_window.analysis_log.append(
                        f"[失败] {project} {borehole} {start_depth}-{end_depth}m [状态码: {response.status_code}]"
                    )
                    new_lith = original_lith
                    new_start = start_depth
                    new_end = end_depth
                    new_desc = desc
            except requests.exceptions.Timeout:
                self.main_window.analysis_log.append(
                    f"[超时] {project} {borehole} {start_depth}-{end_depth}m [请求超时]"
                )
                new_lith = original_lith
                new_start = start_depth
                new_end = end_depth
                new_desc = desc
            except Exception as e:
                self.main_window.analysis_log.append(
                    f"[错误] {project} {borehole} {start_depth}-{end_depth}m [{str(e)}]"
                )
                new_lith = original_lith
                new_start = start_depth
                new_end = end_depth
                new_desc = desc

            new_records.append(
                {
                    "id": max_id + len(new_records) + 1,
                    "project": project,
                    "borehole": borehole,
                    "lithology": new_lith,
                    "start_depth": new_start,
                    "end_depth": new_end,
                    "description": new_desc,
                    "original_lithology": original_lith,
                    "original_id": original_id,
                }
            )

        output_file = os.path.join(dir_path, "lithology_ai.json")

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(new_records, f, ensure_ascii=False, indent=2)

            self.main_window.analysis_progress.setValue(100)
            self.main_window.analysis_status_label.setText(
                f"AI分析完成 - 共 {len(new_records)} 条记录"
            )
            self.main_window.analysis_log.append(
                f"[完成] 原记录: {total_calls} 条, 成功: {success_count} 条, 失败: {total_calls - success_count} 条"
            )
            self.main_window.analysis_log.append(f"[输出] {output_file}")

            self.main_window.analysis_table.setColumnCount(8)
            self.main_window.analysis_table.setHorizontalHeaderLabels(
                [
                    "ID",
                    "项目",
                    "钻孔",
                    "岩性名称",
                    "开始深度",
                    "结束深度",
                    "原岩性",
                    "描述",
                ]
            )
            self.main_window.analysis_table.setColumnWidth(0, 40)
            self.main_window.analysis_table.setColumnWidth(1, 80)
            self.main_window.analysis_table.setColumnWidth(2, 80)
            self.main_window.analysis_table.setColumnWidth(3, 100)
            self.main_window.analysis_table.setColumnWidth(4, 80)
            self.main_window.analysis_table.setColumnWidth(5, 80)
            self.main_window.analysis_table.setColumnWidth(6, 100)
            self.main_window.analysis_table.horizontalHeader().setStretchLastSection(
                True
            )

            self.main_window.analysis_table.setRowCount(len(new_records))

            for i, rec in enumerate(new_records):
                self.main_window.analysis_table.setItem(
                    i, 0, QTableWidgetItem(str(rec.get("id", "")))
                )
                self.main_window.analysis_table.setItem(
                    i, 1, QTableWidgetItem(rec.get("project", ""))
                )
                self.main_window.analysis_table.setItem(
                    i, 2, QTableWidgetItem(rec.get("borehole", ""))
                )
                self.main_window.analysis_table.setItem(
                    i, 3, QTableWidgetItem(rec.get("lithology", ""))
                )
                self.main_window.analysis_table.setItem(
                    i, 4, QTableWidgetItem(str(rec.get("start_depth", 0)))
                )
                self.main_window.analysis_table.setItem(
                    i, 5, QTableWidgetItem(str(rec.get("end_depth", 0)))
                )
                self.main_window.analysis_table.setItem(
                    i, 6, QTableWidgetItem(rec.get("original_lithology", ""))
                )
                self.main_window.analysis_table.setItem(
                    i,
                    7,
                    QTableWidgetItem(
                        rec.get("description", "")[:50]
                        if rec.get("description", "")
                        else ""
                    ),
                )

            self.main_window.analysis_table.resizeRowsToContents()
            self.main_window.status_bar.showMessage("AI分析完成")

        except Exception as e:
            QMessageBox.critical(self.main_window, "错误", f"保存文件失败: {str(e)}")
            self.main_window.analysis_status_label.setText(f"错误: {str(e)}")

    def view_lithology_classification(self):
        json_file, _ = QFileDialog.getOpenFileName(
            self.main_window, "选择岩性分类后的JSON文件", "", "JSON文件 (*.json)"
        )
        if not json_file:
            return

        import json
        import os

        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            QMessageBox.warning(self.main_window, "错误", f"无法读取文件: {str(e)}")
            return

        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        project_root = os.path.dirname(app_dir)
        config_file = os.path.join(project_root, 'config', 'rock_types_flat.json')
        rock_category_map = {}
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config_data = json.load(f)
            for rock in config_data.get('rocks', []):
                rock_category_map[rock['name']] = rock.get('category', '')
        except Exception:
            pass

        self.main_window.analysis_log.clear()
        self.main_window.analysis_log.append(f"已加载岩性分类结果: {json_file}")
        self.main_window.analysis_log.append(f"总记录数: {len(data)}")

        rock_groups = {}
        for item in data:
            rock_name = item.get("rock_name", "") or "未分类"
            lithology = item.get("lithology", "")
            if rock_name not in rock_groups:
                rock_groups[rock_name] = {"lithologies": set(), "count": 0}
            rock_groups[rock_name]["lithologies"].add(lithology)
            rock_groups[rock_name]["count"] += 1

        category_counts = {'岩浆岩': 0, '沉积岩': 0, '变质岩': 0}
        for rock_name in rock_groups.keys():
            category = rock_category_map.get(rock_name, '')
            if category in category_counts:
                category_counts[category] += 1

        self.main_window.analysis_table.setColumnCount(4)
        self.main_window.analysis_table.setHorizontalHeaderLabels(
            ["标准岩性", "图片数", "分类数", "对应原始岩性"]
        )
        self.main_window.analysis_table.setColumnWidth(0, 100)
        self.main_window.analysis_table.setColumnWidth(1, 80)
        self.main_window.analysis_table.setColumnWidth(2, 80)
        self.main_window.analysis_table.horizontalHeader().setStretchLastSection(True)

        sorted_rocks = sorted(
            rock_groups.items(), key=lambda x: x[1]["count"], reverse=True
        )
        self.main_window.analysis_table.setRowCount(len(sorted_rocks))

        for row, (rock_name, info) in enumerate(sorted_rocks):
            lithologies_str = ", ".join(sorted(info["lithologies"]))
            self.main_window.analysis_table.setItem(row, 0, QTableWidgetItem(rock_name))
            self.main_window.analysis_table.setItem(
                row, 1, QTableWidgetItem(str(info["count"]))
            )
            self.main_window.analysis_table.setItem(
                row, 2, QTableWidgetItem(str(len(info["lithologies"])))
            )

        self.main_window.analysis_table.resizeRowsToContents()
        cat_stat = f"岩浆岩{category_counts['岩浆岩']}种/沉积岩{category_counts['沉积岩']}种/变质岩{category_counts['变质岩']}种"
        self.main_window.analysis_status_label.setText(
            f"显示岩性分类 - 共 {len(rock_groups)} 种岩性（{cat_stat}）"
        )
        self.main_window.analysis_table.setColumnWidth(0, 100)
        self.main_window.analysis_table.setColumnWidth(1, 80)
        self.main_window.analysis_table.setColumnWidth(2, 80)
        self.main_window.analysis_table.horizontalHeader().setStretchLastSection(True)

        sorted_rocks = sorted(
            rock_groups.items(), key=lambda x: x[1]["count"], reverse=True
        )
        self.main_window.analysis_table.setRowCount(len(sorted_rocks))

        for row, (rock_name, info) in enumerate(sorted_rocks):
            lithologies_str = ", ".join(sorted(info["lithologies"]))
            self.main_window.analysis_table.setItem(row, 0, QTableWidgetItem(rock_name))
            self.main_window.analysis_table.setItem(
                row, 1, QTableWidgetItem(str(info["count"]))
            )
            self.main_window.analysis_table.setItem(
                row, 2, QTableWidgetItem(str(len(info["lithologies"])))
            )
            self.main_window.analysis_table.setItem(
                row, 3, QTableWidgetItem(lithologies_str)
            )

        self.main_window.analysis_table.resizeRowsToContents()
        self.main_window.analysis_status_label.setText(
            f"显示岩性分类 - 共 {len(rock_groups)} 种岩性"
        )
        self.main_window.status_bar.showMessage("已加载岩性分类结果")

    def view_alteration_analysis(self):
        json_file, _ = QFileDialog.getOpenFileName(
            self.main_window, "选择蚀变分析后的JSON文件", "", "JSON文件 (*.json)"
        )
        if not json_file:
            return

        import json

        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            QMessageBox.warning(self.main_window, "错误", f"无法读取文件: {str(e)}")
            return

        records_with_alt = sum(1 for item in data if item.get("蚀变类型", ""))

        self.main_window.analysis_log.clear()
        self.main_window.analysis_log.append(f"已加载蚀变分析结果: {json_file}")
        self.main_window.analysis_log.append(f"总记录数: {len(data)}")
        self.main_window.analysis_log.append(f"含蚀变记录: {records_with_alt} 条")

        records = [
            (
                item.get("岩性名称", "") or "未分类",
                item.get("lithology", ""),
                item.get("蚀变类型", ""),
                item.get("lithology_description", ""),
            )
            for item in data
        ]
        records.sort(key=lambda x: (x[0], x[1]))

        self.main_window.analysis_table.setColumnCount(6)
        self.main_window.analysis_table.setHorizontalHeaderLabels(
            ["标准岩性", "图片数", "分类数", "原始岩性", "蚀变类型", "岩性描述"]
        )
        self.main_window.analysis_table.setColumnWidth(0, 100)
        self.main_window.analysis_table.setColumnWidth(1, 60)
        self.main_window.analysis_table.setColumnWidth(2, 60)
        self.main_window.analysis_table.setColumnWidth(3, 200)
        self.main_window.analysis_table.setColumnWidth(4, 120)
        self.main_window.analysis_table.horizontalHeader().setStretchLastSection(True)

        rock_groups = {}
        for rock_name, lithology, alteration, description in records:
            if rock_name not in rock_groups:
                rock_groups[rock_name] = {}
            if lithology not in rock_groups[rock_name]:
                rock_groups[rock_name][lithology] = {
                    "count": 0,
                    "alterations": set(),
                    "description": description,
                }
            rock_groups[rock_name][lithology]["count"] += 1
            if alteration:
                rock_groups[rock_name][lithology]["alterations"].add(alteration)

        rows = []
        for rock_name in sorted(rock_groups.keys()):
            for lithology, info in rock_groups[rock_name].items():
                alterations_str = (
                    ", ".join(sorted(info["alterations"]))
                    if info["alterations"]
                    else "-"
                )
                desc = info["description"] or "-"
                rows.append(
                    (
                        rock_name,
                        str(info["count"]),
                        "1",
                        lithology,
                        alterations_str,
                        desc,
                    )
                )

        self.main_window.analysis_table.setRowCount(len(rows))
        for row, (rock_name, count, _, lithology, alteration, description) in enumerate(
            rows
        ):
            self.main_window.analysis_table.setItem(row, 0, QTableWidgetItem(rock_name))
            self.main_window.analysis_table.setItem(row, 1, QTableWidgetItem(count))
            self.main_window.analysis_table.setItem(row, 2, QTableWidgetItem("1"))
            self.main_window.analysis_table.setItem(row, 3, QTableWidgetItem(lithology))
            self.main_window.analysis_table.setItem(
                row, 4, QTableWidgetItem(alteration)
            )
            self.main_window.analysis_table.setItem(
                row, 5, QTableWidgetItem(description)
            )

        self.main_window.analysis_table.resizeRowsToContents()
        self.main_window.analysis_log.append(f"显示蚀变分析结果")
        self.main_window.analysis_status_label.setText(
            f"显示蚀变分析 - {records_with_alt}/{len(data)} 条含蚀变"
        )
        self.main_window.status_bar.showMessage("已加载蚀变分析结果")

        self.main_window.analysis_table.resizeRowsToContents()
        self.main_window.analysis_status_label.setText(
            f"显示蚀变分析 - {records_with_alt}/{len(data)} 条含蚀变"
        )
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

            headers = [
                self.main_window.analysis_table.horizontalHeaderItem(i).text()
                for i in range(self.main_window.analysis_table.columnCount())
            ]

            df = pd.DataFrame(rows, columns=headers)
            df.to_excel(file_path, index=False)

            QMessageBox.information(self.main_window, "完成", f"已导出到: {file_path}")
            self.main_window.analysis_log.append(f"已导出到: {file_path}")

        except Exception as e:
            QMessageBox.critical(self.main_window, "错误", f"导出失败: {str(e)}")
