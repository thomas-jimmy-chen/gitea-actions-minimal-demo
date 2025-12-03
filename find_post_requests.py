#!/usr/bin/env python3
"""
搜尋 test3 中的所有 POST 請求
特別關注可能與考試提交相關的請求
"""

import xml.etree.ElementTree as ET
import base64
import json
from urllib.parse import urlparse

def parse_burp_xml(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    return root.findall('item')

def decode_base64(data):
    if not data:
        return ""
    try:
        return base64.b64decode(data).decode('utf-8', errors='ignore')
    except:
        return ""

def analyze_post_requests(items):
    """分析所有 POST 請求"""
    post_requests = []

    for item in items:
        method_elem = item.find('method')
        if method_elem is None or method_elem.text != 'POST':
            continue

        url_elem = item.find('url')
        if url_elem is None:
            continue

        url = url_elem.text
        path = urlparse(url).path

        request_elem = item.find('request')
        response_elem = item.find('response')

        if request_elem is None:
            continue

        request_text = decode_base64(request_elem.text)
        response_text = decode_base64(response_elem.text) if response_elem is not None else ""

        # 提取 request body
        request_body = ""
        if '\r\n\r\n' in request_text:
            request_body = request_text.split('\r\n\r\n', 1)[1]

        # 提取 response status
        response_status = ""
        if response_text:
            lines = response_text.split('\r\n')
            if lines:
                response_status = lines[0]

        post_requests.append({
            'url': url,
            'path': path,
            'request_body_length': len(request_body),
            'request_body_preview': request_body[:500],
            'response_status': response_status,
        })

    return post_requests

def main():
    print("[*] 搜尋 test3 中的所有 POST 請求...")

    items = parse_burp_xml('test3')
    print(f"[+] 共找到 {len(items)} 個請求")

    post_requests = analyze_post_requests(items)
    print(f"[+] 找到 {len(post_requests)} 個 POST 請求")

    # 按 path 分組
    path_groups = {}
    for req in post_requests:
        path = req['path']
        if path not in path_groups:
            path_groups[path] = []
        path_groups[path].append(req)

    print("\n=== POST 請求統計（按 path） ===")
    for path, reqs in sorted(path_groups.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {path}: {len(reqs)} 次")

    # 儲存結果
    result = {
        'total_post_requests': len(post_requests),
        'unique_paths': len(path_groups),
        'path_groups': {k: len(v) for k, v in path_groups.items()},
        'post_requests': post_requests,
    }

    with open('test3_post_requests.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("\n[+] 結果已儲存到 test3_post_requests.json")

    # 顯示可能與考試相關的 POST 請求
    print("\n=== 可能與考試相關的 POST 請求 ===")
    exam_related_keywords = ['exam', 'test', 'answer', 'submit', 'question', 'score']
    found_exam_related = False

    for path in sorted(path_groups.keys()):
        if any(keyword in path.lower() for keyword in exam_related_keywords):
            found_exam_related = True
            print(f"\n  路徑: {path}")
            print(f"  次數: {len(path_groups[path])}")
            # 顯示第一個範例
            example = path_groups[path][0]
            if example['request_body_preview']:
                print(f"  Request Body (前200字): {example['request_body_preview'][:200]}")
            print(f"  Response Status: {example['response_status']}")

    if not found_exam_related:
        print("  未找到明顯的考試相關 POST 請求")
        print("\n  所有 POST 請求路徑:")
        for path in sorted(path_groups.keys())[:20]:  # 只顯示前20個
            print(f"    {path}")

if __name__ == '__main__':
    main()
