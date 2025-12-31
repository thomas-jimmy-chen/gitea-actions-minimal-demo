#!/usr/bin/env python3
"""
Burp Suite API 流程分析器
分析整串 Burp Suite 記錄，自動識別 API 調用流程與依賴關係
"""

import base64
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import re

class BurpFlowAnalyzer:
    def __init__(self, xml_file):
        self.xml_file = xml_file
        self.requests = []

    def parse_burp_xml(self):
        """解析 Burp Suite XML 檔案"""
        tree = ET.parse(self.xml_file)
        root = tree.getroot()

        for item in root.findall('item'):
            try:
                # 基本資訊
                time_str = item.find('time').text
                url = item.find('url').text
                method = item.find('method').text
                status = item.find('status').text

                # 解碼 request
                request_elem = item.find('request')
                if request_elem.get('base64') == 'true':
                    request_data = base64.b64decode(request_elem.text).decode('utf-8', errors='ignore')
                else:
                    request_data = request_elem.text

                # 解碼 response
                response_elem = item.find('response')
                if response_elem.get('base64') == 'true':
                    response_data = base64.b64decode(response_elem.text).decode('utf-8', errors='ignore')
                else:
                    response_data = response_elem.text

                # 提取請求體（如果有）
                request_body = self.extract_request_body(request_data)

                # 提取響應體
                response_body = self.extract_response_body(response_data)

                # 儲存請求資訊
                self.requests.append({
                    'time': time_str,
                    'url': url,
                    'method': method,
                    'status': status,
                    'request_headers': request_data.split('\n\n')[0] if '\n\n' in request_data else request_data,
                    'request_body': request_body,
                    'response_body': response_body,
                    'parsed_url': urlparse(url)
                })
            except Exception as e:
                print(f"[WARN] 解析項目時出錯: {e}")
                continue

    def extract_request_body(self, request_data):
        """提取請求體"""
        if '\n\n' in request_data:
            parts = request_data.split('\n\n', 1)
            if len(parts) > 1:
                body = parts[1].strip()
                if body:
                    try:
                        return json.loads(body)
                    except:
                        return body
        return None

    def extract_response_body(self, response_data):
        """提取響應體（JSON）"""
        # 找到 JSON 開始的位置
        json_start = -1
        for i, char in enumerate(response_data):
            if char in ['{', '[']:
                json_start = i
                break

        if json_start >= 0:
            try:
                json_str = response_data[json_start:].strip()
                return json.loads(json_str)
            except:
                pass

        return None

    def analyze_flow(self):
        """分析 API 流程"""
        print("="*100)
        print("Burp Suite API 流程分析")
        print("="*100)
        print(f"\n[檔案] {self.xml_file}")
        print(f"[請求總數] {len(self.requests)}")

        # 過濾出 API 請求
        api_requests = [r for r in self.requests if '/api/' in r['url']]
        print(f"[API 請求數] {len(api_requests)}")

        print("\n" + "="*100)
        print("API 調用流程（按時間順序）")
        print("="*100)

        # 用於追蹤 ID 傳遞
        id_tracker = {}

        for idx, req in enumerate(api_requests, 1):
            parsed = req['parsed_url']
            path = parsed.path
            query = parse_qs(parsed.query)

            print(f"\n[{idx}] {req['time']}")
            print(f"    {req['method']} {path}")
            print(f"    Status: {req['status']}")

            # 分析請求參數
            if query:
                print(f"    Query: {query}")

            # 分析請求體
            if req['request_body']:
                print(f"    Request Body:")
                if isinstance(req['request_body'], dict):
                    self.print_json_summary(req['request_body'], indent=6)
                    # 追蹤請求中使用的 ID
                    self.track_ids_in_request(req['request_body'], id_tracker, 'request')
                else:
                    print(f"      {str(req['request_body'])[:200]}")

            # 分析響應體
            if req['response_body']:
                print(f"    Response Body:")
                if isinstance(req['response_body'], dict):
                    self.print_json_summary(req['response_body'], indent=6)
                    # 追蹤響應中返回的 ID
                    self.track_ids_in_response(req['response_body'], id_tracker, path)
                else:
                    print(f"      {str(req['response_body'])[:200]}")

            print(f"    {'-'*94}")

        # 分析 ID 流動
        print("\n" + "="*100)
        print("ID 流動追蹤")
        print("="*100)

        if id_tracker:
            for key, value in id_tracker.items():
                print(f"\n[{key}]")
                print(f"  來源: {value.get('source', 'unknown')}")
                print(f"  值: {value.get('value', 'N/A')}")
                if 'used_in' in value:
                    print(f"  被使用於: {', '.join(value['used_in'])}")
        else:
            print("未檢測到明顯的 ID 傳遞")

        # 生成流程總結
        print("\n" + "="*100)
        print("API 調用流程總結")
        print("="*100)

        self.generate_flow_summary(api_requests)

        # 保存完整分析結果
        self.save_analysis(api_requests, id_tracker)

    def print_json_summary(self, data, indent=0, max_depth=3, current_depth=0):
        """打印 JSON 摘要（限制深度避免過長）"""
        prefix = " " * indent

        if current_depth >= max_depth:
            print(f"{prefix}... (更多資料)")
            return

        if isinstance(data, dict):
            for key, value in list(data.items())[:10]:  # 最多顯示 10 個鍵
                if isinstance(value, (dict, list)):
                    print(f"{prefix}{key}: {type(value).__name__} (長度: {len(value)})")
                    if len(value) > 0 and current_depth < max_depth - 1:
                        if isinstance(value, dict):
                            first_key = list(value.keys())[0]
                            print(f"{prefix}  例如 {first_key}: {value[first_key]}")
                        elif isinstance(value, list) and len(value) > 0:
                            print(f"{prefix}  第一項: {value[0]}")
                else:
                    print(f"{prefix}{key}: {value}")
        elif isinstance(data, list):
            print(f"{prefix}陣列長度: {len(data)}")
            if len(data) > 0:
                print(f"{prefix}第一項:")
                self.print_json_summary(data[0], indent + 2, max_depth, current_depth + 1)

    def track_ids_in_request(self, data, tracker, context):
        """追蹤請求中的 ID"""
        if isinstance(data, dict):
            for key, value in data.items():
                if 'id' in key.lower() and isinstance(value, (int, str)):
                    id_key = f"{key}={value}"
                    if id_key in tracker:
                        if 'used_in' not in tracker[id_key]:
                            tracker[id_key]['used_in'] = []
                        tracker[id_key]['used_in'].append(context)

    def track_ids_in_response(self, data, tracker, source):
        """追蹤響應中的 ID"""
        if isinstance(data, dict):
            for key, value in data.items():
                if 'id' in key.lower() and isinstance(value, (int, str)):
                    id_key = f"{key}={value}"
                    if id_key not in tracker:
                        tracker[id_key] = {
                            'source': source,
                            'value': value
                        }

    def generate_flow_summary(self, api_requests):
        """生成流程總結"""
        # 按 API 路徑分組
        api_groups = {}
        for req in api_requests:
            path_pattern = self.extract_path_pattern(req['parsed_url'].path)
            if path_pattern not in api_groups:
                api_groups[path_pattern] = []
            api_groups[path_pattern].append(req)

        print("\n[API 端點統計]")
        for pattern, requests in api_groups.items():
            methods = set(r['method'] for r in requests)
            print(f"  {pattern}")
            print(f"    調用次數: {len(requests)}")
            print(f"    HTTP 方法: {', '.join(methods)}")

        # 生成流程圖（文字版）
        print("\n[API 調用順序]")
        for idx, req in enumerate(api_requests, 1):
            path = self.extract_path_pattern(req['parsed_url'].path)
            print(f"  {idx}. {req['method']} {path}")
            if idx < len(api_requests):
                print(f"     ↓")

    def extract_path_pattern(self, path):
        """提取路徑模式（將數字 ID 替換為 {id}）"""
        # 替換數字為 {id}
        pattern = re.sub(r'/\d+', '/{id}', path)
        return pattern

    def save_analysis(self, api_requests, id_tracker):
        """保存分析結果到 JSON"""
        output_file = self.xml_file.replace('.txt', '_flow_analysis.json')

        analysis = {
            'total_requests': len(api_requests),
            'api_calls': [
                {
                    'time': req['time'],
                    'method': req['method'],
                    'url': req['url'],
                    'path': req['parsed_url'].path,
                    'status': req['status'],
                    'request_body': req['request_body'],
                    'response_body': req['response_body']
                }
                for req in api_requests
            ],
            'id_tracker': id_tracker
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)

        print(f"\n[OK] 完整分析已保存至: {output_file}")

def main():
    import sys

    if len(sys.argv) < 2:
        print("使用方式: python analyze_burp_flow.py <burp_suite_file.txt>")
        print("\n範例:")
        print("  python analyze_burp_flow.py api_my-courses.txt")
        print("  python analyze_burp_flow.py complete_exam_flow.txt")
        sys.exit(1)

    xml_file = sys.argv[1]

    analyzer = BurpFlowAnalyzer(xml_file)
    analyzer.parse_burp_xml()
    analyzer.analyze_flow()

if __name__ == '__main__':
    main()
