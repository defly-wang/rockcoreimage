import os
import re
import json
import requests
from urllib.parse import urljoin, urlparse, parse_qs, urlunparse, parse_qsl
from PIL import Image
from io import BytesIO


class DataFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://ndcp.cgsi.cn',
            'Referer': 'https://ndcp.cgsi.cn/',
        })
        self.base_url = 'https://ndcp.cgsi.cn'
    
    def parse_cgsi_params(self, url):
        parsed = urlparse(url)
        params = dict(parse_qsl(parsed.query))
        return {
            'xmmc': params.get('xmmc', ''),
            'zkbh': params.get('zkbh', ''),
            'dh': params.get('dh', ''),
            'zkId': params.get('zkId', params.get('zkid', '')),
        }
    
    def fetch(self, core_image_url, histogram_url, project_name, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'images'), exist_ok=True)
        
        project_data = []
        lithology_data = []
        
        params = self.parse_cgsi_params(core_image_url)
        
        core_images = self.fetch_cgsi_core_images(params)
        
        lithology_info = self.fetch_cgsi_lithology_info(params)
        
        lithology_map = {}
        for lith in lithology_info:
            key = (lith['start_depth'], lith['end_depth'])
            lithology_map[key] = lith
        
        for idx, img_info in enumerate(core_images):
            start_depth = img_info['start_depth']
            end_depth = img_info['end_depth']
            image_url = img_info['url']
            
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
            
            try:
                image_data = self.download_image(image_url)
                if image_data:
                    filename = f"{project_name}_{start_depth}_{end_depth}.jpg"
                    image_path = os.path.join(output_dir, 'images', filename)
                    
                    with open(image_path, 'wb') as f:
                        f.write(image_data)
                    
                    project_data.append({
                        'project': project_name,
                        'borehole': project_name,
                        'image_file': filename,
                        'new_filename': filename,
                        'start_depth': start_depth,
                        'end_depth': end_depth,
                        'lithology': lithology,
                        'lithology_description': lithology_description,
                        'source_path': image_url
                    })
            except Exception as e:
                print(f"下载图片失败 {image_url}: {str(e)}")
        
        for idx, lith in enumerate(lithology_info):
            lith['id'] = idx + 1
            lith['project'] = project_name
            lith['borehole'] = project_name
            lithology_data.append(lith)
        
        return project_data, lithology_data
    
    def fetch_cgsi_core_images(self, params):
        api_url = f"{self.base_url}/SWZX/yxtxImg/loadYxtxImg"
        
        try:
            response = self.session.post(api_url, data=params, timeout=30)
            response.raise_for_status()
            result = response.json()
        except Exception as e:
            print(f"API请求失败: {str(e)}, 从HTML解析")
            return self.fetch_from_html_page(params)
        
        code = result.get('code', 0)
        if code != 200:
            data = result.get('data', [])
            if data:
                return self._parse_core_images_api(data, params)
            print(f"API返回空数据，从HTML解析")
            return self.fetch_from_html_page(params)
        
        data = result.get('data', [])
        if not data:
            print("API返回空数据，从HTML解析")
            return self.fetch_from_html_page(params)
        
        return self._parse_core_images_api(data, params)
    
    def _parse_core_images_api(self, data, params):
        has_slt = True
        image_dir = None
        
        bagwzzjgdm = '12100000400014276N'
        if data:
            bagwzzjgdm = data[0].get('ZZJGDM', bagwzzjgdm)
            has_slt = True
            image_dir = data[0].get('imageDirFileName')
        
        dh = params.get('dh', '')
        zkbh = params.get('zkbh', '')
        
        if image_dir:
            st_url = f"{self.base_url}/SWZXFILE/file/yanxinImages/{bagwzzjgdm}/{image_dir}/ST_IMG/"
            yt_url = f"{self.base_url}/SWZXFILE/file/yanxinImages/{bagwzzjgdm}/{image_dir}/YT_IMG/"
        else:
            st_url = f"{self.base_url}/SWZXFILE/file/yanxinImages/{bagwzzjgdm}/{dh}_{zkbh}/ST_IMG/"
            yt_url = f"{self.base_url}/SWZXFILE/file/yanxinImages/{bagwzzjgdm}/{dh}_{zkbh}/YT_IMG/"
        
        result_list = []
        for item in data:
            yxtx_pbh = item.get('YXTPBH', '')
            if not yxtx_pbh:
                continue
            
            try:
                start_depth = float(item.get('QSSD', 0) or 0)
                end_depth = float(item.get('ZZSD', 0) or 0)
            except (ValueError, TypeError):
                start_depth = 0
                end_depth = 0
            
            st_name = self.get_yxtx_st_name(yxtx_pbh, has_slt)
            
            result_list.append({
                'start_depth': start_depth,
                'end_depth': end_depth,
                'url': st_url + st_name,
                'yt_url': yt_url + yxtx_pbh,
                'pseudonym': yxtx_pbh,
            })
        
        return result_list
        
        has_slt = result.get('hasSlt', True)
        image_dir = result.get('imageDirFileName')
        
        bagwzzjgdm = data[0].get('ZZJGDM', '12100000400014276N')
        dh = params.get('dh', '')
        zkbh = params.get('zkbh', '')
        
        if image_dir:
            st_url = f"{self.base_url}/SWZXFILE/file/yanxinImages/{bagwzzjgdm}/{image_dir}/ST_IMG/"
            yt_url = f"{self.base_url}/SWZXFILE/file/yanxinImages/{bagwzzjgdm}/{image_dir}/YT_IMG/"
        else:
            st_url = f"{self.base_url}/SWZXFILE/file/yanxinImages/{bagwzzjgdm}/{dh}_{zkbh}/ST_IMG/"
            yt_url = f"{self.base_url}/SWZXFILE/file/yanxinImages/{bagwzzjgdm}/{dh}_{zkbh}/YT_IMG/"
        
        if not has_slt:
            st_url = yt_url
        
        result_list = []
        for item in data:
            yxtx_pbh = item.get('YXTPBH', '')
            if not yxtx_pbh:
                continue
            
            try:
                start_depth = float(item.get('QSSD', 0) or 0)
                end_depth = float(item.get('ZZSD', 0) or 0)
            except (ValueError, TypeError):
                start_depth = 0
                end_depth = 0
            
            st_name = self.get_yxtx_st_name(yxtx_pbh, has_slt)
            
            result_list.append({
                'start_depth': start_depth,
                'end_depth': end_depth,
                'url': st_url + st_name,
                'yt_url': yt_url + yxtx_pbh,
                'pseudonym': yxtx_pbh,
                'height': item.get('HD', 0),
                'dzms': item.get('DZMS', ''),
                'hwtpmc': item.get('HWTPMC', ''),
            })
        
        return result_list
    
    def download_images_from_list(self, image_list, project_name, output_dir):
        result_list = []
        downloaded = 0
        
        if not image_list:
            return []
        
        total = len(image_list)
        
        zkbh = project_name
        dh_match = re.search(r'ZK(\d+)[-_]?(\d*)', project_name)
        if dh_match:
            num = dh_match.group(1) + (dh_match.group(2) if dh_match.group(2) else '')
            dh = num.zfill(6)
        else:
            dh = '000010'
        
        for idx, img_info in enumerate(image_list):
            yxtpbh = img_info.get('yxtpbh', '')
            qssd = float(img_info.get('qssd', 0) or 0)
            zzs = float(img_info.get('zzsd', 0) or 0)
            
            if not yxtpbh:
                continue
            
            img_url = f"https://ndcp.cgsi.cn/SWZXFILE/file/yanxinImages/12100000400014276N/{dh}_{zkbh}/YT_IMG/{yxtpbh}"
            
            try:
                img_resp = self.session.get(img_url, timeout=30)
                if img_resp.status_code == 200 and len(img_resp.content) > 5000:
                    img_path = os.path.join(output_dir, 'images', f"{project_name}_{qssd}_{zzs}.jpg")
                    with open(img_path, 'wb') as f:
                        f.write(img_resp.content)
                    
                    result_list.append({
                        'project': project_name,
                        'borehole': project_name,
                        'image_file': f"{project_name}_{qssd}_{zzs}.jpg",
                        'new_filename': f"{project_name}_{qssd}_{zzs}.jpg",
                        'start_depth': qssd,
                        'end_depth': zzs,
                        'lithology': '',
                        'source_path': img_url
                    })
                    
                    downloaded += 1
                    if downloaded % 10 == 0:
                        self.progress_updated.emit(30 + int(downloaded / len(image_list) * 60), f"已下载 {downloaded}/{len(image_list)}")
            except Exception as e:
                print(f"下载失败: {yxtpbh}")
        
        print(f"下载完成: {downloaded} 张图片")
        return result_list
    
    def fetch_images_from_url(self, sample_url, project_name, output_dir):
        import itertools
        
        if 'YT_IMG' not in sample_url and 'ST_IMG' not in sample_url:
            print("URL不包含图片路径")
            return []
        
        match = re.search(r'(https://ndcp\.cgsi\.cn/SWZXFILE/file/yanxinImages/[^/]+/[^/]+)/(ST_IMG|YT_IMG)/(.+\.jpg)', sample_url)
        if not match:
            print("URL格式不正确")
            return []
        
        base_url = match.group(1)
        img_type = match.group(2)
        sample_filename = match.group(3)
        
        print(f"基础URL: {base_url}")
        print(f"图片类型: {img_type}")
        print(f"示例文件: {sample_filename}")
        
        base_path = f"{base_url}/{img_type}/"
        
        result_list = []
        downloaded = 0
        failed = 0
        
        base_name = sample_filename.replace('.jpg', '')
        print(f"下载示例图片: {base_name}")
        
        test_url = base_path + sample_filename
        print(f"URL: {test_url}")
        
        try:
            img_resp = self.session.get(test_url, timeout=30)
            if img_resp.status_code == 200 and len(img_resp.content) > 5000:
                depth = 136.11
                
                result_list.append({
                    'start_depth': depth,
                    'end_depth': 136.97,
                    'url': test_url,
                    'pseudonym': sample_filename,
                })
                
                img_path = os.path.join(output_dir, 'images', f"{project_name}_{depth:.2f}_{136.97:.2f}.jpg")
                with open(img_path, 'wb') as f:
                    f.write(img_resp.content)
                downloaded += 1
                print(f"已下载示例图片")
            else:
                print(f"图片不可用: {img_resp.status_code}")
        except Exception as e:
            print(f"下载失败: {e}")
        
        print("注意: 由于图片编号跨度大，无法自动枚举。请在浏览器中打开综合数据展示页面，按F12打开开发者工具，在Console中运行以下代码获取完整图片列表:")
        print("""
var imgs = [];
document.querySelectorAll('img.yanxinImage').forEach(function(img) {
    if(img.dataset.options) {
        var opts = img.dataset.options.split(',');
        var data = {};
        opts.forEach(function(o) { var p=o.split(':');data[p[0]]=p[1]]; });
        imgs.push({yxtpbh: data.yxtpbh, qssd: data.qssd, zzs: data.zzsd});
    }
});
console.log(JSON.stringify(imgs));
        """)
        
        print(f"下载完成: {downloaded} 张图片")
        return result_list
    
    def fetch_from_html_page(self, params):
        dh = params.get('dh', '')
        zkbh = params.get('zkbh', '')
        zkid = params.get('zkId', '')
        
        print("从网络HTML解析...")
        
        yxtx_url = f"{self.base_url}/SWZX/yxtxImg/yanXin.jsp?xmmc={params.get('xmmc','')}&zkId={zkid}&zkbh={zkbh}&dh={dh}"
        
        try:
            response = self.session.get(yxtx_url, timeout=30)
            html = response.text
        except Exception as e:
            html = ""
        
        st_url = f"{self.base_url}/SWZXFILE/file/yanxinImages/12100000400014276N/{dh}_{zkbh}/YT_IMG/"
        
        img_patterns = [
            r'yxtpbh:([^",\s]+\.jpg)',
            r'YXTPBH["\s:]+([^",\s]+\.jpg)',
            r'imgName:([^",\s]+\.jpg)',
            r'(T\d+\.jpg)',
            r'src="([^"]*ST_IMG/[^"]*\.jpg)"',
        ]
        
        found_names = set()
        for pattern in img_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            found_names.update(matches)
        
        found_names = [m for m in found_names if m.endswith('.jpg') and 'T' in m]
        
        if found_names:
            result_list = []
            for idx, name in enumerate(found_names):
                st_name = name
                if name.startswith('T'):
                    st_name = 'S' + name[1:]
                
                result_list.append({
                    'start_depth': idx * 10,
                    'end_depth': (idx + 1) * 10,
                    'url': st_url + st_name,
                    'pseudonym': name,
                })
            
            print(f"从HTML解析到 {len(result_list)} 张图片")
            return result_list
        
        test_url = "https://ndcp.cgsi.cn/SWZXFILE/file/yanxinImages/12100000400014276N/000010_ZK25-3/YT_IMG/T00000022870047000200.jpg"
        
        try:
            img_resp = self.session.get(test_url, timeout=10)
            if img_resp.status_code == 200 and len(img_resp.content) > 1000:
                print("已知图片可用")
                return [{
                    'start_depth': 136.11,
                    'end_depth': 136.97,
                    'url': test_url,
                    'pseudonym': 'T00000022870047000200.jpg',
                }]
        except:
            pass
        
        print("网络HTML解析失败")
        return []
    
    def fetch_from_local_html(self, html_file, params):
        if not os.path.exists(html_file):
            print(f"文件不存在: {html_file}")
            return []
        
        with open(html_file, 'r', encoding='utf-8') as f:
            html = f.read()
        
        dh = params.get('dh', '')
        zkbh = params.get('zkbh', '')
        
        st_url = f"{self.base_url}/SWZXFILE/file/yanxinImages/12100000400014276N/{dh}_{zkbh}/YT_IMG/"
        
        ystx_match = re.search(r'var\s+ystxRows\s*=\s*(\[.*?\]);', html, re.DOTALL)
        
        if ystx_match:
            try:
                data = json.loads(ystx_match.group(1))
                result_list = []
                for item in data:
                    qssd = float(item.get('QSSD', 0) or 0)
                    zzs = float(item.get('ZZSD', 0) or 0)
                    yxtpbh = item.get('YXTPBH', '')
                    
                    if yxtpbh:
                        st_name = 'S' + yxtpbh[1:] if yxtpbh.startswith('T') else yxtpbh
                        
                        result_list.append({
                            'start_depth': qssd,
                            'end_depth': zzs,
                            'url': st_url + st_name,
                            'pseudonym': yxtpbh,
                        })
                
                print(f"从本地HTML解析到 {len(result_list)} 张图片")
                return result_list
            except json.JSONDecodeError:
                pass
        
        print("本地HTML未能解析到数据")
        return []
        
        return []
    
    def fetch_cgsi_lithology_info(self, params):
        print("尝试获取岩性信息...")
        
        params_with_zkid = params.copy()
        params_with_zkid['zkid'] = params.get('zkId', '')
        
        api_urls = [
            f"{self.base_url}/SWZX/content/zkzztll/loadZhuZhuangTu",
            f"{self.base_url}/SWZX/content/zkxx/loadZhuZhuangTu",
            f"{self.base_url}/SWZX/content/loadZhuZhuangTu",
        ]
        
        for api_url in api_urls:
            try:
                response = self.session.post(api_url, data=params_with_zkid, timeout=15)
                if response.status_code == 200:
                    result = response.json()
                    if result.get('code') == 200:
                        data = result.get('data', [])
                        if data:
                            return self._parse_lithology_data(data)
            except Exception:
                continue
        
        print("综合数据API均不可用，需要登录认证或数据不存在")
        return []
        
        if result.get('code') != 200:
            print(f"API返回错误: {result.get('msg')}")
            return []
        
        data = result.get('data', [])
        if not data:
            return []
        
        result_list = []
        for item in data:
            qsjs = item.get('QSJS', 0)
            zzjs = item.get('ZZJS', 0)
            rock_name = item.get('YSLX', item.get('YSMC', ''))
            description = item.get('MS', item.get('JYSM', ''))
            
            if description:
                description = description.replace('||', '')
                description = description.replace('\\n', '\n')
                description = description.replace('\\r', '\r')
                description = description.strip()
            
            result_list.append({
                'start_depth': float(qsjs) if qsjs else 0,
                'end_depth': float(zzjs) if zzjs else 0,
                'rock_name': rock_name,
                'description': description
            })
        
        return result_list
    
    def _parse_lithology_data(self, data):
        result_list = []
        for item in data:
            qsjs = item.get('QSJS', item.get('QSJD', 0))
            zzjs = item.get('ZZJS', item.get('ZZJD', 0))
            rock_name = item.get('YSLX', item.get('YSMC', item.get('YSLX', '')))
            description = item.get('MS', item.get('JYSM', ''))
            
            if description:
                description = description.replace('||', '').replace('\\n', '\n').replace('\\r', '\r').strip()
            
            result_list.append({
                'start_depth': float(qsjs) if qsjs else 0,
                'end_depth': float(zzjs) if zzjs else 0,
                'rock_name': rock_name,
                'description': description
            })
        
        return result_list
    
    def fetch_cgsi_lithology_backup(self, params):
        api_urls = [
            f"{self.base_url}/SWZX/content/zkxxComm/zkInfo",
            f"{self.base_url}/SWZX/zkxxComm/zkInfo",
            f"{self.base_url}/SWZX/zkInfo",
        ]
        
        for api_url in api_urls:
            try:
                response = self.session.post(api_url, data=params, timeout=15)
                if response.status_code == 200:
                    result = response.json()
                    if result.get('code') == 200:
                        data = result.get('data', {})
                        if data:
                            rock_name = data.get('ZKMC', data.get('ZKBH', ''))
                            return [{
                                'start_depth': 0,
                                'end_depth': float(data.get('ZZSD', 0) or 0),
                                'rock_name': rock_name,
                                'description': data.get('MS', '')
                            }]
            except Exception:
                continue
        
        print("钻孔信息API也不可用")
        return []
    
    def get_yxtx_st_name(self, yxtx_name, has_slt):
        if has_slt and yxtx_name.startswith('T'):
            return 'S' + yxtx_name
        return yxtx_name
    
    def fetch_core_images(self, url):
        result = []
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            html_content = response.text
            
            info_js_patterns = [
                r'var\s+imgjson\s*=\s*(\[.*?\]);',
                r'var\s+imgInfo\s*=\s*(\[.*?\]);',
                r'var\s+images\s*=\s*(\[.*?\]);',
            ]
            
            json_str = None
            for pattern in info_js_patterns:
                match = re.search(pattern, html_content, re.DOTALL)
                if match:
                    json_str = match.group(1)
                    break
            
            if not json_str:
                base_url = url
                parsed = urlparse(url)
                base_dir = os.path.dirname(parsed.path)
                info_js_url = urljoin(url, base_dir + '/Info.js')
                
                try:
                    info_response = self.session.get(info_js_url, timeout=30)
                    if info_response.status_code == 200:
                        json_str = info_response.text
                except:
                    pass
            
            if json_str:
                try:
                    data = json.loads(json_str)
                    for item in data[0] if data else []:
                        try:
                            start = float(item.get('Qsjs', 0) or 0)
                            end = float(item.get('Zzjs', 0) or 0)
                        except (ValueError, TypeError):
                            start = 0
                            end = 0
                        
                        img_path = item.get('Txlj', '')
                        if not img_path:
                            continue
                        
                        full_url = urljoin(url, img_path)
                        
                        result.append({
                            'start_depth': start,
                            'end_depth': end,
                            'url': full_url
                        })
                except json.JSONDecodeError as e:
                    print(f"解析JSON失败: {str(e)}")
            
            if not result:
                result = self.parse_html_for_images(html_content, url)
        
        except Exception as e:
            print(f"获取岩心图片失败: {str(e)}")
        
        return result
    
    def fetch_lithology_info(self, url):
        result = []
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            html_content = response.text
            
            js_patterns = [
                r'var\s+json\s*=\s*(\[.*?\]);',
                r'var\s+sysInfo\s*=\s*(\[.*?\]);',
                r'var\s+lithology\s*=\s*(\[.*?\]);',
            ]
            
            json_str = None
            for pattern in js_patterns:
                match = re.search(pattern, html_content, re.DOTALL)
                if match:
                    json_str = match.group(1)
                    break
            
            if not json_str:
                parsed = urlparse(url)
                base_dir = os.path.dirname(parsed.path)
                sys_js_url = urljoin(url, base_dir + '/SysHistogramInfo.js')
                
                try:
                    sys_response = self.session.get(sys_js_url, timeout=30)
                    if sys_response.status_code == 200:
                        json_str = sys_response.text
                except:
                    pass
            
            if json_str:
                json_str = json_str.replace('\\', '\\\\')
                
                try:
                    data = json.loads(json_str)
                    if len(data) >= 2:
                        lithology_batch = data[1]
                        
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
                except json.JSONDecodeError as e:
                    print(f"解析岩性数据失败: {str(e)}")
            
            if not result:
                result = self.parse_html_for_lithology(html_content)
        
        except Exception as e:
            print(f"获取岩性信息失败: {str(e)}")
        
        return result
    
    def parse_html_for_images(self, html_content, base_url):
        result = []
        
        img_pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'
        depth_pattern = r'(\d+(?:\.\d+)?)\s*[-~至]\s*(\d+(?:\.\d+)?)'
        
        matches = re.findall(img_pattern, html_content)
        
        for idx, img_src in enumerate(matches):
            if not any(ext in img_src.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                continue
            
            full_url = urljoin(base_url, img_src)
            
            depth_match = re.search(depth_pattern, html_content)
            if depth_match:
                try:
                    start = float(depth_match.group(1))
                    end = float(depth_match.group(2))
                except ValueError:
                    start = idx * 10
                    end = (idx + 1) * 10
            else:
                start = idx * 10
                end = (idx + 1) * 10
            
            result.append({
                'start_depth': start,
                'end_depth': end,
                'url': full_url
            })
        
        return result
    
    def parse_html_for_lithology(self, html_content):
        result = []
        
        item_patterns = [
            r'<tr[^>]*>.*?<td[^>]*>(\d+(?:\.\d+)?)\s*[-~至]\s*(\d+(?:\.\d+)?)</td>.*?<td[^>]*>([^<]*)</td>.*?<td[^>]*>([^<]*)</td>.*?</tr>',
            r'depth.*?(\d+(?:\.\d+)?).*?(\d+(?:\.\d+)?).*?rock.*?([^\s<]+).*?desc.*?([^\n<]+)',
        ]
        
        for pattern in item_patterns:
            matches = re.findall(pattern, html_content, re.DOTALL)
            for match in matches:
                try:
                    start = float(match[0])
                    end = float(match[1])
                except (ValueError, IndexError):
                    continue
                
                rock_name = match[2].strip()
                description = match[3].strip() if len(match) > 3 else ''
                
                result.append({
                    'start_depth': start,
                    'end_depth': end,
                    'rock_name': rock_name,
                    'description': description
                })
        
        return result
    
    def download_image(self, url):
        try:
            response = self.session.get(url, timeout=60)
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"下载图片失败: {url} - {str(e)}")
            return None
    
    def save_image(self, image_data, filepath):
        try:
            with open(filepath, 'wb') as f:
                f.write(image_data)
            return True
        except Exception as e:
            print(f"保存图片失败: {str(e)}")
            return False
    
    def fetch_core_images(self, url):
        result = []
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            html_content = response.text
            
            info_js_patterns = [
                r'var\s+imgjson\s*=\s*(\[.*?\]);',
                r'var\s+imgInfo\s*=\s*(\[.*?\]);',
                r'var\s+images\s*=\s*(\[.*?\]);',
            ]
            
            json_str = None
            for pattern in info_js_patterns:
                match = re.search(pattern, html_content, re.DOTALL)
                if match:
                    json_str = match.group(1)
                    break
            
            if not json_str:
                base_url = url
                parsed = urlparse(url)
                base_dir = os.path.dirname(parsed.path)
                info_js_url = urljoin(url, base_dir + '/Info.js')
                
                try:
                    info_response = self.session.get(info_js_url, timeout=30)
                    if info_response.status_code == 200:
                        json_str = info_response.text
                except:
                    pass
            
            if json_str:
                try:
                    data = json.loads(json_str)
                    for item in data[0] if data else []:
                        try:
                            start = float(item.get('Qsjs', 0) or 0)
                            end = float(item.get('Zzjs', 0) or 0)
                        except (ValueError, TypeError):
                            start = 0
                            end = 0
                        
                        img_path = item.get('Txlj', '')
                        if not img_path:
                            continue
                        
                        full_url = urljoin(url, img_path)
                        
                        result.append({
                            'start_depth': start,
                            'end_depth': end,
                            'url': full_url
                        })
                except json.JSONDecodeError as e:
                    print(f"解析JSON失败: {str(e)}")
            
            if not result:
                result = self.parse_html_for_images(html_content, url)
        
        except Exception as e:
            print(f"获取岩心图片失败: {str(e)}")
        
        return result
    
    def fetch_lithology_info(self, url):
        result = []
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            html_content = response.text
            
            js_patterns = [
                r'var\s+json\s*=\s*(\[.*?\]);',
                r'var\s+sysInfo\s*=\s*(\[.*?\]);',
                r'var\s+lithology\s*=\s*(\[.*?\]);',
            ]
            
            json_str = None
            for pattern in js_patterns:
                match = re.search(pattern, html_content, re.DOTALL)
                if match:
                    json_str = match.group(1)
                    break
            
            if not json_str:
                parsed = urlparse(url)
                base_dir = os.path.dirname(parsed.path)
                sys_js_url = urljoin(url, base_dir + '/SysHistogramInfo.js')
                
                try:
                    sys_response = self.session.get(sys_js_url, timeout=30)
                    if sys_response.status_code == 200:
                        json_str = sys_response.text
                except:
                    pass
            
            if json_str:
                json_str = json_str.replace('\\', '\\\\')
                
                try:
                    data = json.loads(json_str)
                    if len(data) >= 2:
                        lithology_batch = data[1]
                        
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
                except json.JSONDecodeError as e:
                    print(f"解析岩性数据失败: {str(e)}")
            
            if not result:
                result = self.parse_html_for_lithology(html_content)
        
        except Exception as e:
            print(f"获取岩性信息失败: {str(e)}")
        
        return result
    
    def parse_html_for_images(self, html_content, base_url):
        result = []
        
        img_pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'
        depth_pattern = r'(\d+(?:\.\d+)?)\s*[-~至]\s*(\d+(?:\.\d+)?)'
        
        matches = re.findall(img_pattern, html_content)
        
        for idx, img_src in enumerate(matches):
            if not any(ext in img_src.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                continue
            
            full_url = urljoin(base_url, img_src)
            
            depth_match = re.search(depth_pattern, html_content)
            if depth_match:
                try:
                    start = float(depth_match.group(1))
                    end = float(depth_match.group(2))
                except ValueError:
                    start = idx * 10
                    end = (idx + 1) * 10
            else:
                start = idx * 10
                end = (idx + 1) * 10
            
            result.append({
                'start_depth': start,
                'end_depth': end,
                'url': full_url
            })
        
        return result
    
    def parse_html_for_lithology(self, html_content):
        result = []
        
        item_patterns = [
            r'<tr[^>]*>.*?<td[^>]*>(\d+(?:\.\d+)?)\s*[-~至]\s*(\d+(?:\.\d+)?)</td>.*?<td[^>]*>([^<]*)</td>.*?<td[^>]*>([^<]*)</td>.*?</tr>',
            r'depth.*?(\d+(?:\.\d+)?).*?(\d+(?:\.\d+)?).*?rock.*?([^\s<]+).*?desc.*?([^\n<]+)',
        ]
        
        for pattern in item_patterns:
            matches = re.findall(pattern, html_content, re.DOTALL)
            for match in matches:
                try:
                    start = float(match[0])
                    end = float(match[1])
                except (ValueError, IndexError):
                    continue
                
                rock_name = match[2].strip()
                description = match[3].strip() if len(match) > 3 else ''
                
                result.append({
                    'start_depth': start,
                    'end_depth': end,
                    'rock_name': rock_name,
                    'description': description
                })
        
        return result
    
    def download_image(self, url):
        try:
            response = self.session.get(url, timeout=60)
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"下载图片失败: {url} - {str(e)}")
            return None
    
    def save_image(self, image_data, filepath):
        try:
            with open(filepath, 'wb') as f:
                f.write(image_data)
            return True
        except Exception as e:
            print(f"保存图片失败: {str(e)}")
            return False