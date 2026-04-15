import os
import json


class AlterationAnalyzer:
    def __init__(self):
        pass
    
    def analyze_alteration(self, json_file, alteration_config_file, output_file):
        with open(alteration_config_file, 'r', encoding='utf-8') as f:
            alteration_config = json.load(f)
        
        alterations = alteration_config.get('alterations', [])
        
        alteration_keywords = {}
        for alt in alterations:
            alt_name = alt['name']
            keywords = [alt_name]
            keywords.extend(alt.get('aliases', []))
            alteration_keywords[alt_name] = {
                'keywords': set(keywords),
                'category': alt.get('category', ''),
                'importance': alt.get('importance', False)
            }
        
        alteration_keywords = dict(sorted(alteration_keywords.items(), key=lambda x: -len(x[1]['keywords'])))
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        total = len(data)
        
        def detect_alterations(lithology):
            if not lithology:
                return []
            detected = []
            lithology_lower = lithology.lower()
            for alt_name, alt_info in alteration_keywords.items():
                for keyword in alt_info['keywords']:
                    if keyword and keyword.lower() in lithology_lower:
                        detected.append(alt_name)
                        break
            return detected
        
        alteration_stats = {}
        total_alterations = 0
        
        for idx, item in enumerate(data):
            lithology = item.get('lithology', '')
            
            detected = detect_alterations(lithology)
            item['蚀变类型'] = ", ".join(detected) if detected else ""
            
            for alt_name in detected:
                if alt_name not in alteration_stats:
                    alteration_stats[alt_name] = {
                        'category': alteration_keywords[alt_name]['category'],
                        'importance': alteration_keywords[alt_name]['importance'],
                        'count': 0
                    }
                alteration_stats[alt_name]['count'] += 1
                total_alterations += 1
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        importance_stats = {
            'important': {},
            'other': {}
        }
        category_stats = {}
        
        for alt_name, info in alteration_stats.items():
            target = importance_stats['important'] if info['importance'] else importance_stats['other']
            target[alt_name] = info['count']
            
            if info['category'] not in category_stats:
                category_stats[info['category']] = 0
            category_stats[info['category']] += info['count']
        
        stats = {
            'total_records': total,
            'records_with_alteration': sum(1 for item in data if item.get('蚀变类型')),
            'total_alterations': total_alterations,
            'alteration_types': len(alteration_stats),
            'important_alterations': importance_stats['important'],
            'other_alterations': importance_stats['other'],
            'category_stats': category_stats
        }
        
        return output_file, stats
    
    def generate_lithology_descriptions(self, image_json_file, output_file):
        with open(image_json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        desc_key_map = {}
        desc_records = {}
        
        for item in data:
            project = item.get('project', '')
            borehole = item.get('borehole', '')
            lithology = item.get('lithology', '')
            start_depth = item.get('start_depth', 0)
            end_depth = item.get('end_depth', 0)
            description = item.get('lithology_description', '')
            
            key = (project, borehole, lithology)
            
            if key not in desc_key_map:
                desc_id = len(desc_key_map)
                desc_key_map[key] = desc_id
                desc_records[desc_id] = {
                    'id': desc_id,
                    'project': project,
                    'borehole': borehole,
                    'lithology': lithology,
                    'segments': []
                }
            
            existing = desc_records[desc_key_map[key]]
            if not any(s['start'] == start_depth and s['end'] == end_depth for s in existing['segments']):
                existing['segments'].append({
                    'start': start_depth,
                    'end': end_depth,
                    'description': description
                })
        
        descriptions = []
        for desc_id in sorted(desc_records.keys()):
            rec = desc_records[desc_id]
            rec['segments'].sort(key=lambda x: x['start'])
            
            min_start = min(s['start'] for s in rec['segments'])
            max_end = max(s['end'] for s in rec['segments'])
            
            merged_desc = '；'.join([s['description'] for s in rec['segments'] if s['description']])
            
            descriptions.append({
                'id': rec['id'],
                'project': rec['project'],
                'borehole': rec['borehole'],
                'lithology': rec['lithology'],
                'start_depth': min_start,
                'end_depth': max_end,
                'description': merged_desc
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(descriptions, f, ensure_ascii=False, indent=2)
        
        stats = {
            'total_records': len(data),
            'unique_descriptions': len(descriptions)
        }
        
        return output_file, stats
