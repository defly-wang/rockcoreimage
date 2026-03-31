import os
import re
import shutil
import json
from pathlib import Path
import openpyxl
from PyQt6.QtCore import QObject, pyqtSignal


class DataProcessor(QObject):
    progress_updated = pyqtSignal(int, str)
    processing_finished = pyqtSignal(str, dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.source_dir = ""
        self.output_dir = ""
        
    def process(self, source_dir, output_dir):
        self.source_dir = source_dir
        self.output_dir = output_dir
        
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'images'), exist_ok=True)
        
        project_dirs = [d for d in os.listdir(source_dir) 
                      if os.path.isdir(os.path.join(source_dir, d)) and not d.startswith('.')]
        
        total_projects = len(project_dirs)
        all_data = []
        
        for idx, project in enumerate(sorted(project_dirs)):
            self.progress_updated.emit(
                int(idx / total_projects * 100),
                f"处理项目: {project}"
            )
            
            project_path = os.path.join(source_dir, project)
            
            excel_files = [f for f in os.listdir(project_path) 
                         if f.endswith('.xlsx') and not f.startswith('~') and not f.startswith('.~')]
            
            if not excel_files:
                continue
            
            excel_path = os.path.join(project_path, excel_files[0])
            
            try:
                project_data = self.process_project(project, project_path, excel_path)
                all_data.extend(project_data)
            except Exception as e:
                self.error_occurred.emit(f"处理项目 {project} 时出错: {str(e)}")
        
        output_file = os.path.join(output_dir, 'image_descriptions.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        
        self.progress_updated.emit(100, "处理完成")
        self.processing_finished.emit(output_file, {
            'total_images': len(all_data),
            'total_projects': total_projects
        })
    
    def process_project(self, project_name, project_path, excel_path):
        project_data = []
        
        wb = openpyxl.load_workbook(excel_path, read_only=True)
        
        lithology_data = self.read_lithology_sheet(wb)
        
        image_data = self.read_image_sheet(wb)
        
        wb.close()
        
        borehole_image_index = {}
        
        for img_record in image_data:
            borehole = img_record['borehole']
            img_filename = img_record['filename']
            start_depth = img_record['start_depth']
            end_depth = img_record['end_depth']
            
            lithology = self.match_lithology(lithology_data, borehole, start_depth, end_depth)
            
            source_img_path = self.find_image_file(project_path, borehole, img_filename, borehole_image_index)
            
            if source_img_path:
                new_filename = f"{project_name}_{borehole}_{os.path.basename(source_img_path)}"
                dest_img_path = os.path.join(self.output_dir, 'images', new_filename)
                os.makedirs(os.path.dirname(dest_img_path), exist_ok=True)
                
                try:
                    shutil.copy2(source_img_path, dest_img_path)
                    
                    project_data.append({
                        'project': project_name,
                        'borehole': borehole,
                        'image_file': os.path.basename(source_img_path),
                        'new_filename': new_filename,
                        'start_depth': start_depth,
                        'end_depth': end_depth,
                        'lithology': lithology['rock_name'],
                        'lithology_description': lithology['description'],
                        'source_path': source_img_path
                    })
                except Exception as e:
                    self.error_occurred.emit(f"复制图片失败 {source_img_path}: {str(e)}")
        
        return project_data
    
    def read_lithology_sheet(self, wb):
        data = []
        try:
            ws = wb['岩性描述']
            headers = [cell.value for cell in ws[1]]
            
            borehole_idx = headers.index('钻孔编号') if '钻孔编号' in headers else -1
            start_idx = headers.index('起始深度') if '起始深度' in headers else -1
            end_idx = headers.index('终止深度') if '终止深度' in headers else -1
            rock_idx = headers.index('岩石名称') if '岩石名称' in headers else -1
            desc_idx = headers.index('岩性描述') if '岩性描述' in headers else -1
            
            for row in ws.iter_rows(min_row=2, values_only=True):
                if row[0] is None:
                    continue
                    
                data.append({
                    'borehole': row[borehole_idx] if borehole_idx >= 0 else None,
                    'start_depth': float(row[start_idx]) if start_idx >= 0 and row[start_idx] is not None else 0,
                    'end_depth': float(row[end_idx]) if end_idx >= 0 and row[end_idx] is not None else 0,
                    'rock_name': row[rock_idx] if rock_idx >= 0 else '',
                    'description': row[desc_idx] if desc_idx >= 0 else ''
                })
        except KeyError:
            pass
        
        return data
    
    def read_image_sheet(self, wb):
        data = []
        try:
            ws = wb['岩心影像']
            headers = [cell.value for cell in ws[1]]
            
            borehole_idx = headers.index('钻孔编号') if '钻孔编号' in headers else -1
            start_idx = headers.index('起始深度') if '起始深度' in headers else -1
            end_idx = headers.index('终止深度') if '终止深度' in headers else -1
            path_idx = headers.index('图片路径') if '图片路径' in headers else -1
            
            for row in ws.iter_rows(min_row=2, values_only=True):
                if row[0] is None:
                    continue
                
                path = row[path_idx] if path_idx >= 0 else ''
                filename = self.extract_filename(path)
                
                data.append({
                    'borehole': row[borehole_idx] if borehole_idx >= 0 else None,
                    'start_depth': float(row[start_idx]) if start_idx >= 0 and row[start_idx] is not None else 0,
                    'end_depth': float(row[end_idx]) if end_idx >= 0 and row[end_idx] is not None else 0,
                    'filename': filename,
                    'path': path
                })
        except KeyError:
            pass
        
        return data
    
    def extract_filename(self, path):
        if not path:
            return ''
        
        path = path.replace('\\', '/')
        if '//' in path:
            path = path.split('//', 1)[1]
        
        return os.path.basename(path)
    
    def find_image_file(self, project_path, borehole, filename, image_index_cache):
        borehole_dir = os.path.join(project_path, borehole)
        
        if not os.path.exists(borehole_dir):
            return None
        
        if borehole not in image_index_cache:
            image_index_cache[borehole] = self.build_image_index(borehole_dir)
        
        index = image_index_cache[borehole]
        
        match = re.match(r'(HC\d+)-(\d+)\.(\w+)', filename, re.IGNORECASE)
        if match:
            hc_num = match.group(1).upper()
            suffix = match.group(2)
            ext = match.group(3).lower()
            
            if hc_num in index and suffix in index[hc_num]:
                return index[hc_num][suffix]
        
        for hc, files in index.items():
            for suffix, full_path in files.items():
                if os.path.basename(full_path).upper() == filename.upper():
                    return full_path
        
        return None
    
    def build_image_index(self, borehole_dir):
        index = {}
        
        for f in os.listdir(borehole_dir):
            if not f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                continue
            
            match = re.match(r'(HC\d+)-(\d+)\.(\w+)', f, re.IGNORECASE)
            if match:
                hc_num = match.group(1).upper()
                suffix = match.group(2)
                
                if hc_num not in index:
                    index[hc_num] = {}
                index[hc_num][suffix] = os.path.join(borehole_dir, f)
        
        return index
    
    def match_lithology(self, lithology_data, borehole, start_depth, end_depth):
        for lith in lithology_data:
            if lith['borehole'] != borehole:
                continue
            
            lith_start = lith['start_depth']
            lith_end = lith['end_depth']
            
            if start_depth >= lith_start and end_depth <= lith_end:
                return lith
            
            if start_depth < lith_end and end_depth > lith_start:
                return lith
        
        return {
            'borehole': borehole,
            'rock_name': '',
            'description': '',
            'start_depth': 0,
            'end_depth': 0
        }
