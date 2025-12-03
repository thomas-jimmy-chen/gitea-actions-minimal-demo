#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import base64
import json
import re
from collections import defaultdict
from typing import Dict, List, Any
import os

def decode_content(content_str):
    """Decode base64 content"""
    if not content_str:
        return ""
    try:
        decoded = base64.b64decode(content_str).decode('utf-8', errors='ignore')
        return decoded
    except Exception as e:
        return f"[Decode Error]"

def extract_api_path(url):
    """Extract API path from URL"""
    try:
        # 提取 /path 部分
        match = re.search(r'://[^/]+(/[^?]*)', url)
        if match:
            return match.group(1)
        return url
    except:
        return url

def main():
    file_path = r'D:\Dev\eebot\test2'

    print("[*] Parsing Burp Suite XML file...")

    # 使用 iterparse 以處理大檔案
    api_stats = defaultdict(int)
    user_visits_reqs = []
    statistics_reqs = []
    activity_reqs = []

    try:
        context = ET.iterparse(file_path, events=('end',))
        item_count = 0

        for event, elem in context:
            if elem.tag != 'item':
                continue

            item_count += 1

            request_elem = elem.find('request')
            if request_elem is None:
                continue

            url_elem = request_elem.find('url')
            method_elem = request_elem.find('method')
            if url_elem is None or url_elem.text is None:
                continue

            url = url_elem.text
            method = method_elem.text if method_elem is not None else 'N/A'
            api_path = extract_api_path(url)

            # 統計 API
            api_stats[api_path] += 1

            # 收集感興趣的 API
            if 'user-visits' in url and '/statistics/' in url:
                user_visits_reqs.append({
                    'index': item_count - 1,
                    'url': url,
                    'method': method
                })

            if '/statistics/' in url:
                statistics_reqs.append({
                    'index': item_count - 1,
                    'url': url,
                    'method': method
                })

            if 'activity-reads' in url or 'online-video' in url:
                activity_reqs.append({
                    'index': item_count - 1,
                    'url': url,
                    'method': method
                })

            # 清理記憶體
            elem.clear()

        print(f"[+] Total requests processed: {item_count}")
        print(f"[+] user-visits requests: {len(user_visits_reqs)}")
        print(f"[+] statistics requests: {len(statistics_reqs)}")
        print(f"[+] activity requests: {len(activity_reqs)}")

        print("\n=== API Statistics (Top 30) ===")
        sorted_apis = sorted(api_stats.items(), key=lambda x: x[1], reverse=True)
        for api, count in sorted_apis[:30]:
            if count > 1:
                print(f"  {api}: {count}")

        # 保存結果
        result = {
            'total_items': item_count,
            'api_statistics': dict(api_stats),
            'user_visits_requests': user_visits_reqs,
            'statistics_requests': statistics_reqs,
            'activity_requests': activity_reqs
        }

        output_path = r'D:\Dev\eebot\burp_analysis_summary.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n[+] Summary saved to {output_path}")

    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == '__main__':
    main()
