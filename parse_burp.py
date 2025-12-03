#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import base64
import json
import re
from collections import defaultdict
from typing import Dict, List, Tuple, Any
import sys

def decode_content(content_str):
    """Decode base64 content"""
    try:
        if not content_str:
            return ""
        decoded = base64.b64decode(content_str).decode('utf-8', errors='ignore')
        return decoded
    except Exception as e:
        return f"[Decode Error: {str(e)}]"

def parse_xml_safely(file_path, max_items=None):
    """Parse XML file with error handling"""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        items = root.findall('.//item')
        if max_items:
            items = items[:max_items]

        return items
    except Exception as e:
        print(f"Error parsing XML: {e}", file=sys.stderr)
        return []

def extract_request_info(request_elem):
    """Extract request information"""
    try:
        method = request_elem.find('method')
        url = request_elem.find('url')
        headers = request_elem.find('headers')
        body = request_elem.find('body')

        return {
            'method': method.text if method is not None else '',
            'url': url.text if url is not None else '',
            'headers': decode_content(headers.text) if headers is not None and headers.text else '',
            'body': decode_content(body.text) if body is not None and body.text else ''
        }
    except Exception as e:
        return None

def extract_response_info(response_elem):
    """Extract response information"""
    try:
        status = response_elem.find('status')
        headers = response_elem.find('headers')
        body = response_elem.find('body')

        return {
            'status': status.text if status is not None else '',
            'headers': decode_content(headers.text) if headers is not None and headers.text else '',
            'body': decode_content(body.text) if body is not None and body.text else ''
        }
    except Exception as e:
        return None

def parse_json_safely(text):
    """Safely parse JSON"""
    try:
        return json.loads(text)
    except:
        return None

def main():
    file_path = r'D:\Dev\eebot\test2'

    print("[*] 開始解析 Burp Suite XML 檔案...", file=sys.stderr)
    items = parse_xml_safely(file_path)
    print(f"[*] 找到 {len(items)} 個請求", file=sys.stderr)

    # 統計 API 端點
    api_stats = defaultdict(list)
    user_visits_requests = []

    for idx, item in enumerate(items):
        request_elem = item.find('request')
        response_elem = item.find('response')

        if request_elem is None:
            continue

        request = extract_request_info(request_elem)
        response = extract_response_info(response_elem) if response_elem is not None else None

        if not request or not request['url']:
            continue

        # 提取 API 路徑
        url = request['url']
        path_match = re.search(r'(https?://[^/]+)?(/[^?]*)', url)
        if path_match:
            api_path = path_match.group(2)
        else:
            api_path = url

        # 記錄所有請求
        api_stats[api_path].append({
            'index': idx,
            'url': url,
            'method': request['method'],
            'request': request,
            'response': response
        })

        # 特別收集 user-visits API
        if 'user-visits' in url:
            user_visits_requests.append({
                'index': idx,
                'url': url,
                'method': request['method'],
                'request': request,
                'response': response
            })

    print(f"[*] 找到 {len(user_visits_requests)} 個 user-visits 請求", file=sys.stderr)

    # 保存 user-visits 的詳細信息
    output_file = r'D:\Dev\eebot\user_visits_analysis.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, req in enumerate(user_visits_requests[:10]):  # 先保存前 10 個
            print(f"\n=== User-Visits Request #{i+1} (Index: {req['index']}) ===", file=sys.stderr)
            print(f"Method: {req['method']}", file=sys.stderr)
            print(f"URL: {req['url']}", file=sys.stderr)
            print(f"\nRequest Body:", file=sys.stderr)
            req_body = parse_json_safely(req['request']['body'])
            if req_body:
                print(json.dumps(req_body, indent=2, ensure_ascii=False), file=sys.stderr)
            else:
                print(req['request']['body'][:500], file=sys.stderr)

            if req['response']:
                print(f"\nResponse Status: {req['response']['status']}", file=sys.stderr)
                print(f"Response Body:", file=sys.stderr)
                resp_body = parse_json_safely(req['response']['body'])
                if resp_body:
                    print(json.dumps(resp_body, indent=2, ensure_ascii=False), file=sys.stderr)
                else:
                    print(req['response']['body'][:500], file=sys.stderr)

    # 保存 API 統計
    print("\n\n=== API 統計 ===", file=sys.stderr)
    for api_path in sorted(api_stats.keys()):
        count = len(api_stats[api_path])
        if count > 5:  # 只顯示出現超過 5 次的 API
            print(f"{api_path}: {count} 次", file=sys.stderr)

    # 保存所有數據為 JSON
    export_data = {
        'total_requests': len(items),
        'user_visits_count': len(user_visits_requests),
        'api_statistics': {k: len(v) for k, v in api_stats.items()},
        'user_visits_requests': user_visits_requests[:20]  # 前 20 個用於分析
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)

    print(f"\n[+] 已保存分析結果到 {output_file}", file=sys.stderr)

if __name__ == '__main__':
    main()
