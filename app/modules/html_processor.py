import os
import re
import shutil
import json


class HtmlProcessor:
    def __init__(self):
        self.source_dir = ""
        self.output_dir = ""
    
    def process_html_files(self, project_name, borehole_dir, white_light_html, histogram_html):
        project_data = []
        
        image_info = self.parse_white_light_html(white_light_html)
        
        lithology_info = self.parse_histogram_html(histogram_html)
        
        lithology_map = {}
        for lith in lithology_info:
            key = (lith['start_depth'], lith['end_depth'])
            lithology_map[key] = lith
        
        for img in image_info:
            full_path = img['path']
            full_path = full_path.replace('\\', '/')
            if '//' in full_path:
                full_path = full_path.split('//', 1)[1]
            
            filename = os.path.basename(full_path)
            start_depth = img['start_depth']
            end_depth = img['end_depth']
            
            matched_lith = None
            for (s, e), lith in lithology_map.items():
                if start_depth >= s and end_depth <= e:
                    matched_lith = lith
                    break
                if start_depth < e and end_depth > s:
                    matched_lith = lith
                    break
            
            lithology = matched_lith['rock_name'] if matched_lith else ''
            lithology_description = matched_lith['description'] if matched_lith else ''
            
            source_img_path = self.find_image_in_tongci(borehole_dir, filename)
            
            if source_img_path:
                new_filename = f"{project_name}_{os.path.basename(source_img_path)}"
                dest_img_path = os.path.join(self.output_dir, 'images', new_filename)
                os.makedirs(os.path.dirname(dest_img_path), exist_ok=True)
                
                try:
                    shutil.copy2(source_img_path, dest_img_path)
                    
                    project_data.append({
                        'project': project_name,
                        'borehole': project_name,
                        'image_file': os.path.basename(source_img_path),
                        'new_filename': new_filename,
                        'start_depth': start_depth,
                        'end_depth': end_depth,
                        'lithology': lithology,
                        'lithology_description': lithology_description,
                        'source_path': source_img_path
                    })
                except Exception as e:
                    print(f"复制图片失败 {source_img_path}: {str(e)}")
        
        return project_data, lithology_info
    
    def parse_white_light_html(self, html_file):
        if not os.path.exists(html_file):
            return []
        
        info_js = os.path.join(os.path.dirname(html_file), '白光平扫相册_files', 'Info.js')
        if not os.path.exists(info_js):
            return []
        
        with open(info_js, 'r', encoding='utf-8') as f:
            content = f.read()
        
        result = []
        
        match = re.search(r'var\s+imgjson\s*=\s*(\[.*?\]);', content, re.DOTALL)
        if not match:
            return []
        
        json_str = match.group(1)
        
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            return []
        
        if not data or len(data) == 0:
            return []
        
        for item in data[0]:
            img_path = item.get('Txlj', '')
            if not img_path:
                continue
            
            try:
                start = float(item.get('QSSD', 0) or 0)
                end = float(item.get('ZZSD', 0) or 0)
            except (ValueError, TypeError):
                start = 0
                end = 0
            
            result.append({
                'start_depth': start,
                'end_depth': end,
                'path': img_path
            })
        
        return result
    
    def parse_histogram_html(self, html_file):
        sys_js_path = os.path.join(os.path.dirname(html_file), '综合柱状图_files', 'SysHistogramInfo.js')
        if not os.path.exists(sys_js_path):
            return []
        
        with open(sys_js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        match = re.search(r'var\s+json\s*=\s*(\[.*?\]);', content, re.DOTALL)
        if not match:
            return []
        
        json_str = match.group(1)
        json_str = json_str.replace('\\', '\\\\')
        
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            return []
        
        if len(data) < 2:
            return []
        
        lithology_batch = data[1]
        
        result = []
        for item in lithology_batch:
            if item.get('Type') != '岩心描述':
                continue
                
            qsjs = item.get('QSJD', 0)
            zzjs = item.get('ZZJD', 0)
            rock_name = item.get('YSMC', '')
            description = item.get('MS', '')
            
            if description:
                description = description.replace('||', '')
                description = description.replace('\\n', '\n')
                description = description.replace('\\r', '\r')
                description = description.replace('\\t', '\t')
                description = description.strip()
            
            result.append({
                'start_depth': float(qsjs) if qsjs else 0,
                'end_depth': float(zzjs) if zzjs else 0,
                'rock_name': rock_name,
                'description': description
            })
        
        return result
    
    def find_image_in_tongci(self, borehole_dir, filename):
        if not borehole_dir or not os.path.exists(borehole_dir):
            return None
        
        def extract_number(d):
            match = re.match(r'第(\d+)筒次', d)
            return int(match.group(1)) if match else 0
        
        tongci_dirs = [d for d in os.listdir(borehole_dir) 
                      if d.endswith('筒次') and os.path.isdir(os.path.join(borehole_dir, d))]
        
        for tongci in sorted(tongci_dirs, key=extract_number):
            tongci_path = os.path.join(borehole_dir, tongci)
            original_img_dir = os.path.join(tongci_path, '原始图像')
            
            if not os.path.exists(original_img_dir):
                continue
            
            for root, dirs, files in os.walk(original_img_dir):
                for f in files:
                    if f.lower() == filename.lower():
                        return os.path.join(root, f)
        
        return None
