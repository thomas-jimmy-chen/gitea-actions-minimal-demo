#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import base64
import json
import re
from collections import defaultdict
from typing import Dict, List, Any

def decode_base64(text):
    """Decode base64 text"""
    if not text:
        return ""
    try:
        return base64.b64decode(text).decode('utf-8', errors='ignore')
    except:
        return ""

def extract_api_path(url):
    """Extract API path from URL"""
    try:
        # Remove protocol and host
        match = re.search(r'https?://[^/]+(/[^?]*)', url)
        if match:
            return match.group(1)
        return url
    except:
        return url

def parse_headers(header_text):
    """Parse HTTP headers into dict"""
    if not header_text:
        return {}
    headers = {}
    lines = header_text.split('\n')
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            headers[key.strip()] = value.strip()
    return headers

def main():
    file_path = r'D:\Dev\eebot\test2'

    print("[*] Parsing Burp Suite XML file...")

    # Register namespaces
    for prefix, uri in [("burp", "http://portswigger.net/burp")]:
        ET.register_namespace(prefix, uri)

    tree = ET.parse(file_path)
    root = tree.getroot()

    items = root.findall('.//item')
    print(f"[+] Found {len(items)} items")

    api_stats = defaultdict(list)
    user_visits_reqs = []
    statistics_reqs = []
    activity_reqs = []

    for idx, item in enumerate(items):
        url_elem = item.find('url')
        method_elem = item.find('method')
        request_elem = item.find('request')
        response_elem = item.find('response')
        status_elem = item.find('status')

        if url_elem is None or url_elem.text is None:
            continue

        url = url_elem.text
        method = method_elem.text if method_elem is not None else 'N/A'
        api_path = extract_api_path(url)

        # Get request body
        req_body = ""
        req_headers = ""
        if request_elem is not None and request_elem.text:
            is_base64 = request_elem.get('base64', 'false').lower() == 'true'
            if is_base64:
                req_body = decode_base64(request_elem.text)
            else:
                req_body = request_elem.text

        # Parse request to separate headers and body
        if req_body:
            parts = req_body.split('\r\n\r\n', 1)
            if len(parts) == 2:
                req_headers = parts[0]
                req_body = parts[1]

        # Get response
        resp_body = ""
        resp_headers = ""
        resp_status = status_elem.text if status_elem is not None else ""
        if response_elem is not None and response_elem.text:
            is_base64 = response_elem.get('base64', 'false').lower() == 'true'
            if is_base64:
                resp_body = decode_base64(response_elem.text)
            else:
                resp_body = response_elem.text

        # Parse response to separate headers and body
        if resp_body:
            parts = resp_body.split('\r\n\r\n', 1)
            if len(parts) == 2:
                resp_headers = parts[0]
                resp_body = parts[1]

        # Record API
        api_stats[api_path].append({
            'index': idx,
            'method': method,
            'url': url,
            'req_headers': req_headers,
            'req_body': req_body,
            'resp_status': resp_status,
            'resp_headers': resp_headers,
            'resp_body': resp_body
        })

        # Collect specific APIs
        if 'user-visits' in api_path:
            user_visits_reqs.append({
                'index': idx,
                'method': method,
                'url': url
            })

        if '/statistics/' in api_path:
            statistics_reqs.append({
                'index': idx,
                'method': method,
                'url': url
            })

        if 'activity-reads' in api_path or 'online-video' in api_path:
            activity_reqs.append({
                'index': idx,
                'method': method,
                'url': url
            })

    print(f"\n[+] Statistics APIs found: {len(statistics_reqs)}")
    print(f"[+] user-visits APIs found: {len(user_visits_reqs)}")
    print(f"[+] activity APIs found: {len(activity_reqs)}")

    # Print top APIs
    print("\n=== Top 30 APIs ===")
    sorted_apis = sorted(api_stats.items(), key=lambda x: len(x[1]), reverse=True)
    for api, reqs in sorted_apis[:30]:
        print(f"  {api}: {len(reqs)} requests")

    # Save user-visits details
    print("\n=== Analyzing user-visits requests ===")
    if user_visits_reqs:
        # Get first few user-visits requests with full details
        user_visits_full = []
        for req_info in user_visits_reqs[:5]:
            idx = req_info['index']
            full_data = api_stats[extract_api_path(req_info['url'])][0]  # Get full data
            # Find correct entry
            for entry in api_stats[extract_api_path(req_info['url'])]:
                if entry['index'] == idx:
                    full_data = entry
                    break
            user_visits_full.append(full_data)

        print(f"\nFirst user-visits request:")
        if user_visits_full:
            first = user_visits_full[0]
            print(f"  Method: {first['method']}")
            print(f"  URL: {first['url']}")
            print(f"  Request Body (first 500 chars):")
            print(f"    {first['req_body'][:500]}")
            print(f"  Response Status: {first['resp_status']}")
            print(f"  Response Body (first 500 chars):")
            print(f"    {first['resp_body'][:500]}")

    # Save all API paths
    output = {
        'total_items': len(items),
        'api_count': len(api_stats),
        'user_visits_count': len(user_visits_reqs),
        'statistics_count': len(statistics_reqs),
        'activity_count': len(activity_reqs),
        'api_paths': {path: len(reqs) for path, reqs in api_stats.items()}
    }

    output_path = r'D:\Dev\eebot\api_overview.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n[+] Overview saved to {output_path}")

    # Save detailed data for user-visits
    if user_visits_reqs:
        user_visits_full_data = []
        for req_info in user_visits_reqs[:10]:  # First 10
            path = extract_api_path(req_info['url'])
            idx = req_info['index']
            for entry in api_stats[path]:
                if entry['index'] == idx:
                    user_visits_full_data.append(entry)
                    break

        details_path = r'D:\Dev\eebot\user_visits_detailed.json'
        with open(details_path, 'w', encoding='utf-8') as f:
            json.dump(user_visits_full_data, f, ensure_ascii=False, indent=2)
        print(f"[+] user-visits details saved to {details_path}")

if __name__ == '__main__':
    main()
