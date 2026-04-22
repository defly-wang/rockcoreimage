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
        self.lithology_id_start = 1
        self.excel_processor = ExcelProcessor()
        self.html_processor = HtmlProcessor()
    
    def process(self, source_dir, output_dir, lithology_id_start=1):
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.lithology_id_start = lithology_id_start
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
        all_lithology_data = excel_lithology_data + html_lithology_data
        for idx, lith in enumerate(all_lithology_data):
            descriptions.append({
                'id': self.lithology_id_start + idx,
                'project': lith.get('project', ''),
                'borehole': lith.get('borehole', ''),
                'lithology': lith.get('rock_name', ''),
                'start_depth': lith.get('start_depth', 0),
                'end_depth': lith.get('end_depth', 0),
                'description': lith.get('description', '')
            })
        
        desc_lookup = {(d.get('project', ''), d.get('borehole', ''), d.get('start_depth', 0), d.get('end_depth', 0)): self.lithology_id_start + idx 
                      for idx, d in enumerate(all_lithology_data)}
        
        for item in all_data:
            project = item.get('project', '')
            borehole = item.get('borehole', '')
            start_depth = item.get('start_depth', 0)
            end_depth = item.get('end_depth', 0)
            
            desc_id = None
            for (proj, bore, ds, de), lith_id in desc_lookup.items():
                if proj == project and bore == borehole:
                    if start_depth >= ds and end_depth <= de:
                        desc_id = lith_id
                        break
                    if start_depth < de and end_depth > ds:
                        desc_id = lith_id
                        break
            
            item['lithology_description_id'] = desc_id
            item.pop('lithology_description', None)
        
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
    
    def classify_lithology(self, json_file, config_file, output_file):
        import json
        
        self.progress_updated.emit(0, "正在加载配置文件...")
        
        if not os.path.exists(config_file):
            self.error_occurred.emit(f"找不到配置文件: {config_file}")
            return
        
        if not os.path.exists(json_file):
            self.error_occurred.emit(f"找不到JSON文件: {json_file}")
            return
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                rock_types = json.load(f)
        except Exception as e:
            self.error_occurred.emit(f"读取配置文件失败: {str(e)}")
            return
        
        rocks = set()
        for rock in rock_types.get('rocks', []):
            rocks.add(rock['name'])
            rocks.update(rock.get('aliases', []))
        rocks = sorted(rocks, key=lambda x: -len(x))
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            self.error_occurred.emit(f"读取JSON文件失败: {str(e)}")
            return
        
        total = len(data)
        self.progress_updated.emit(10, f"共 {total} 条记录待分类")
        
        def extract_last_keyword(lithology):
            lithology = lithology.strip()
            for rock in rocks:
                if lithology.endswith(rock):
                    return rock
            return ''
        
        mapping = {}
        unmatched = {}
        
        for idx, item in enumerate(data):
            lithology = item.get('lithology', '')
            keyword = extract_last_keyword(lithology)
            item['岩性名称'] = keyword
            
            progress = int(10 + (idx + 1) / total * 80)
            if idx % max(1, total // 10) == 0:
                self.progress_updated.emit(progress, f"正在分类 [{idx+1}/{total}]: {lithology}")
            
            if keyword:
                if keyword not in mapping:
                    mapping[keyword] = {'lithologies': set(), 'count': 0}
                mapping[keyword]['lithologies'].add(lithology)
                mapping[keyword]['count'] += 1
            else:
                if lithology not in unmatched:
                    unmatched[lithology] = 0
                unmatched[lithology] += 1
        
        self.progress_updated.emit(95, "正在保存结果...")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        matched = sum(v['count'] for v in mapping.values())
        
        stats = {
            'total': total,
            'matched': matched,
            'types': len(mapping),
            'mapping': mapping,
            'unmatched': unmatched
        }
        
        self.progress_updated.emit(100, "分类完成")
        self.processing_finished.emit(output_file, stats)
