import os
import re
import json


class LithologyClassifier:
    def __init__(self):
        pass
    
    def classify_lithology(self, json_file, config_file, output_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            rock_types = json.load(f)
        
        rocks = set()
        for rock in rock_types['rocks']:
            rocks.add(rock['name'])
            rocks.update(rock.get('aliases', []))
        rocks = sorted(rocks, key=lambda x: -len(x))
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        total = len(data)
        
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
            
            if keyword:
                if keyword not in mapping:
                    mapping[keyword] = {'lithologies': set(), 'count': 0}
                mapping[keyword]['lithologies'].add(lithology)
                mapping[keyword]['count'] += 1
            else:
                if lithology not in unmatched:
                    unmatched[lithology] = 0
                unmatched[lithology] += 1
        
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
        
        return output_file, stats
    
    def load_rock_types(self):
        config_files = [
            'config/rock_types.json',
            'config/rock_types_comprehensive.json',
            'config/rock_types_flat.json'
        ]
        
        rocks = set()
        for config_file in config_files:
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                if 'rocks' in config:
                    for rock in config['rocks']:
                        rocks.add(rock['name'])
                        rocks.update(rock.get('aliases', []))
                elif 'categories' in config:
                    for category, cat_info in config['categories'].items():
                        for rock_list in [cat_info.get('important', []), cat_info.get('general', [])]:
                            rocks.update(rock_list)
            except:
                pass
        
        return sorted(rocks, key=lambda x: -len(x))
    
    def analyze_lithology_from_description(self, current_lithology, description, start_depth, end_depth, rocks):
        if not description:
            return current_lithology
        
        rock_minerals = ['钾长石', '斜长石', '石英', '黑云母', '白云母', '绿泥石', '绢云母', '黄铁矿', '黄铜矿', '榍石', '钛铁矿', '石榴子石']
        
        exclude_terms = ['分界线', '接触带', '界面', '断层泥', '糜棱岩', '角砾']

        def check_lithology(lithology):
            if lithology in rock_minerals:
                return None
            if any(term in lithology for term in exclude_terms):
                return None
            for rock in rocks:
                if lithology == rock:
                    return rock
            if '岩' in lithology:
                return lithology
            return None

        depth_pattern = r'(\d+\.?\d*)[m米]?[-–—](\d+\.?\d*)[m米]?\s*([\u4e00-\u9fa5]+岩)'
        match = re.search(depth_pattern, description)
        if match:
            lithology = match.group(3).strip()
            result = check_lithology(lithology)
            if result:
                try:
                    desc_start = float(match.group(1))
                    desc_end = float(match.group(2))
                    overlap_start = max(start_depth, desc_start)
                    overlap_end = min(end_depth, desc_end)
                    overlap = max(0, overlap_end - overlap_start)
                    img_range = end_depth - start_depth
                    if img_range > 0 and overlap / img_range >= 0.6:
                        return result
                except:
                    pass
        
        for pattern in [
            r'(\d+\.?\d*)[m米]?[-–—](\d+\.?\d*)[m米]?[\u4e00-\u9fa5]*([\u4e00-\u9fa5]+)粒([\u4e00-\u9fa5]+岩)',
            r'(\d+\.?\d*)[m米]?[-–—](\d+\.?\d*)[m米]?[\u4e00-\u9fa5]*色([\u4e00-\u9fa5]+岩)',
        ]:
            match = re.search(pattern, description)
            if match:
                lithology = match.groups()[-1].strip()
                result = check_lithology(lithology)
                if result:
                    try:
                        desc_start = float(match.group(1))
                        desc_end = float(match.group(2))
                        overlap_start = max(start_depth, desc_start)
                        overlap_end = min(end_depth, desc_end)
                        overlap = max(0, overlap_end - overlap_start)
                        img_range = end_depth - start_depth
                        if img_range > 0 and overlap / img_range >= 0.6:
                            return result
                    except:
                        pass
        
        return current_lithology
