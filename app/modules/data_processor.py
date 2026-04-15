import os
import json
from PyQt6.QtCore import QObject, pyqtSignal

from app.modules.excel_processor import ExcelProcessor
from app.modules.html_processor import HtmlProcessor


class DataProcessor(QObject):
    progress_updated = pyqtSignal(int, str)
    processing_finished = pyqtSignal(str, dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.source_dir = ""
        self.output_dir = ""
        self.excel_processor = ExcelProcessor()
        self.html_processor = HtmlProcessor()
    
    def process(self, source_dir, output_dir):
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.excel_processor.source_dir = source_dir
        self.excel_processor.output_dir = output_dir
        self.html_processor.output_dir = output_dir
        
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'images'), exist_ok=True)
        
        self.progress_updated.emit(0, "正在扫描项目目录...")
        
        project_dirs = [d for d in os.listdir(source_dir) 
                      if os.path.isdir(os.path.join(source_dir, d)) and not d.startswith('.')]
        
        total_projects = len(project_dirs)
        if total_projects == 0:
            self.progress_updated.emit(100, "未找到项目")
            self.processing_finished.emit("", {'total_images': 0, 'total_projects': 0})
            return
        
        self.progress_updated.emit(5, f"共发现 {total_projects} 个项目")
        
        all_data = []
        excel_lithology_data = []
        html_lithology_data = []
        
        for idx, project in enumerate(sorted(project_dirs)):
            progress_base = int(10 + (idx / total_projects) * 80)
            self.progress_updated.emit(
                progress_base,
                f"处理项目 [{idx+1}/{total_projects}]: {project}"
            )
            
            project_path = os.path.join(source_dir, project)
            
            self.progress_updated.emit(
                progress_base,
                f"正在读取项目 {project} 的Excel文件..."
            )
            
            excel_files = [f for f in os.listdir(project_path) 
                         if f.endswith('.xlsx') and not f.startswith('~') and not f.startswith('.~')]
            
            if excel_files:
                excel_path = os.path.join(project_path, excel_files[0])
                try:
                    self.progress_updated.emit(
                        progress_base + 2,
                        f"正在解析 {excel_files[0]}..."
                    )
                    project_data, lithology_data = self.excel_processor.process_project(project, project_path, excel_path)
                    all_data.extend(project_data)
                    
                    for lith in lithology_data:
                        lith['project'] = project
                        excel_lithology_data.append(lith)
                    
                    self.progress_updated.emit(
                        progress_base + 5,
                        f"项目 {project} 处理完成，获取 {len(project_data)} 条记录"
                    )
                except Exception as e:
                    self.error_occurred.emit(f"处理项目 {project} 时出错: {str(e)}")
            else:
                offline_dir = os.path.join(project_path, '离线成果展示')
                borehole_dir = project_path
                
                found = False
                for d in os.listdir(project_path):
                    d_path = os.path.join(project_path, d)
                    if os.path.isdir(d_path) and d.endswith('筒次'):
                        borehole_dir = project_path
                        found = True
                        break
                    if os.path.isdir(d_path):
                        for sub_d in os.listdir(d_path):
                            if sub_d.endswith('筒次'):
                                borehole_dir = d_path
                                found = True
                                break
                    if found:
                        break
                
                if os.path.exists(offline_dir):
                    white_light_html = os.path.join(offline_dir, '白光平扫相册.html')
                    histogram_html = os.path.join(offline_dir, '综合柱状图.html')
                    
                    if os.path.exists(white_light_html) and os.path.exists(histogram_html):
                        try:
                            self.progress_updated.emit(progress_base + 2, f"正在解析 {project} 的HTML文件...")
                            project_data, lithology_info = self.html_processor.process_html_files(project, borehole_dir, white_light_html, histogram_html)
                            all_data.extend(project_data)
                            for lith in lithology_info:
                                lith['project'] = project
                                lith['borehole'] = project
                                html_lithology_data.append(lith)
                            self.progress_updated.emit(
                                progress_base + 5,
                                f"项目 {project} 处理完成，获取 {len(project_data)} 条记录"
                            )
                        except Exception as e:
                            self.error_occurred.emit(f"处理项目 {project} 时出错: {str(e)}")
                    else:
                        self.progress_updated.emit(progress_base, f"项目 {project} 缺少HTML文件，跳过")
                else:
                    self.progress_updated.emit(progress_base, f"项目 {project} 无Excel和HTML文件，跳过")
        
        self.progress_updated.emit(95, "正在保存数据文件...")
        
        descriptions = []
        if excel_lithology_data:
            for idx, lith in enumerate(excel_lithology_data):
                descriptions.append({
                    'id': idx,
                    'project': lith.get('project', ''),
                    'borehole': lith.get('borehole', ''),
                    'lithology': lith.get('rock_name', ''),
                    'start_depth': lith.get('start_depth', 0),
                    'end_depth': lith.get('end_depth', 0),
                    'description': lith.get('description', '')
                })
        
        desc_lookup = {(d.get('project', ''), d.get('borehole', ''), d.get('start_depth', 0), d.get('end_depth', 0)): idx 
                      for idx, d in enumerate(excel_lithology_data)}
        
        for item in all_data:
            project = item.get('project', '')
            borehole = item.get('borehole', '')
            start_depth = item.get('start_depth', 0)
            end_depth = item.get('end_depth', 0)
            
            desc_id = None
            for (proj, bore, ds, de), lid in desc_lookup.items():
                if proj == project and bore == borehole:
                    if start_depth >= ds and end_depth <= de:
                        desc_id = lid
                        break
                    if start_depth < de and end_depth > ds:
                        desc_id = lid
                        break
            
            item['lithology_description_id'] = desc_id
            item.pop('lithology_description', None)
        
        if html_lithology_data:
            base_id = len(descriptions)
            for idx, lith in enumerate(html_lithology_data):
                descriptions.append({
                    'id': base_id + idx,
                    'project': lith.get('project', ''),
                    'borehole': lith.get('borehole', ''),
                    'lithology': lith.get('rock_name', ''),
                    'start_depth': lith.get('start_depth', 0),
                    'end_depth': lith.get('end_depth', 0),
                    'description': lith.get('description', '')
                })
        
        lithology_stats = {}
        for item in all_data:
            lith = item.get('lithology', '')
            proj = item.get('project', '')
            if lith:
                key = (lith, proj)
                if key not in lithology_stats:
                    lithology_stats[key] = {'lithology': lith, 'project': proj, 'count': 0}
                lithology_stats[key]['count'] += 1
        
        output_file = os.path.join(output_dir, 'image_descriptions.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        
        descriptions_file = os.path.join(output_dir, 'lithology_descriptions.json')
        with open(descriptions_file, 'w', encoding='utf-8') as f:
            json.dump(descriptions, f, ensure_ascii=False, indent=2)
        
        self.progress_updated.emit(100, "处理完成")
        self.processing_finished.emit(output_file, {
            'total_images': len(all_data),
            'total_projects': total_projects,
            'lithology_stats': lithology_stats,
            'descriptions_file': descriptions_file
        })
