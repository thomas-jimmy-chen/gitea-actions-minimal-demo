#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import base64
import json
import re
from collections import defaultdict
from typing import Dict, List, Any
from datetime import datetime

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
    lines = header_text.split('\r\n')
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            headers[key.strip()] = value.strip()
    return headers

def parse_json_safely(text):
    """Safely parse JSON"""
    try:
        return json.loads(text)
    except:
        return None

def main():
    file_path = r'D:\Dev\eebot\test2'

    print("[*] Starting comprehensive analysis...")

    tree = ET.parse(file_path)
    root = tree.getroot()
    items = root.findall('.//item')

    # Collections for specific APIs
    user_visits_posts = []  # POST /statistics/api/user-visits
    user_visits_metrics = defaultdict(list)  # GET metrics
    online_video_metrics = defaultdict(list)  # GET online-video metrics
    interactions_metrics = defaultdict(list)  # GET interactions metrics
    activity_reads = defaultdict(list)  # GET activity-reads
    online_video_setting = defaultdict(list)  # GET online-video-setting

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

        # Extract request
        req_body = ""
        req_headers = ""
        if request_elem is not None and request_elem.text:
            is_base64 = request_elem.get('base64', 'false').lower() == 'true'
            decoded = decode_base64(request_elem.text) if is_base64 else request_elem.text
            parts = decoded.split('\r\n\r\n', 1)
            if len(parts) == 2:
                req_headers = parts[0]
                req_body = parts[1]

        # Extract response
        resp_body = ""
        resp_headers = ""
        resp_status = status_elem.text if status_elem is not None else ""
        if response_elem is not None and response_elem.text:
            is_base64 = response_elem.get('base64', 'false').lower() == 'true'
            decoded = decode_base64(response_elem.text) if is_base64 else response_elem.text
            parts = decoded.split('\r\n\r\n', 1)
            if len(parts) == 2:
                resp_headers = parts[0]
                resp_body = parts[1]

        req_headers_dict = parse_headers(req_headers)
        resp_headers_dict = parse_headers(resp_headers)

        # Classify requests
        if '/statistics/api/user-visits' in url and method == 'POST':
            req_json = parse_json_safely(req_body)
            resp_json = parse_json_safely(resp_body)
            user_visits_posts.append({
                'index': idx,
                'url': url,
                'method': method,
                'req_headers': req_headers_dict,
                'req_body': req_json,
                'resp_status': resp_status,
                'resp_headers': resp_headers_dict,
                'resp_body': resp_json,
                'raw_req_body': req_body,
                'raw_resp_body': resp_body
            })

        elif '/user-visits/metrics' in url:
            resp_json = parse_json_safely(resp_body)
            user_visits_metrics[url].append({
                'index': idx,
                'method': method,
                'resp_status': resp_status,
                'resp_body': resp_json
            })

        elif '/online-videos/metrics' in url:
            resp_json = parse_json_safely(resp_body)
            online_video_metrics[url].append({
                'index': idx,
                'method': method,
                'resp_status': resp_status,
                'resp_body': resp_json
            })

        elif '/interactions/metrics' in url:
            resp_json = parse_json_safely(resp_body)
            interactions_metrics[url].append({
                'index': idx,
                'method': method,
                'resp_status': resp_status,
                'resp_body': resp_json
            })

        elif 'activity-reads-for-user' in url:
            resp_json = parse_json_safely(resp_body)
            activity_reads[url].append({
                'index': idx,
                'method': method,
                'resp_status': resp_status,
                'resp_body': resp_json
            })

        elif 'online-video-completeness/setting' in url:
            resp_json = parse_json_safely(resp_body)
            online_video_setting[url].append({
                'index': idx,
                'method': method,
                'resp_status': resp_status,
                'resp_body': resp_json
            })

    # Analysis output
    print(f"\n[*] Analysis Complete")
    print(f"[+] POST /statistics/api/user-visits: {len(user_visits_posts)} requests")
    print(f"[+] GET */user-visits/metrics: {len(user_visits_metrics)} unique endpoints with {sum(len(v) for v in user_visits_metrics.values())} total requests")
    print(f"[+] GET */online-videos/metrics: {len(online_video_metrics)} unique endpoints with {sum(len(v) for v in online_video_metrics.values())} total requests")
    print(f"[+] GET */interactions/metrics: {len(interactions_metrics)} unique endpoints with {sum(len(v) for v in interactions_metrics.values())} total requests")
    print(f"[+] GET */activity-reads-for-user: {len(activity_reads)} unique endpoints with {sum(len(v) for v in activity_reads.values())} total requests")
    print(f"[+] GET */online-video-completeness/setting: {len(online_video_setting)} unique endpoints with {sum(len(v) for v in online_video_setting.values())} total requests")

    # Print sample user-visits requests
    print("\n=== Sample POST /statistics/api/user-visits Requests ===")
    for i, req in enumerate(user_visits_posts[:3]):
        print(f"\n--- Request #{i+1} (Index: {req['index']}) ---")
        print(f"Method: {req['method']}")
        print(f"URL: {req['url']}")
        print(f"Response Status: {req['resp_status']}")
        print(f"Request Body Fields:")
        if req['req_body']:
            for key, value in sorted(req['req_body'].items()):
                print(f"  - {key}: {value} ({type(value).__name__})")

    # Extract all unique fields from user-visits requests
    all_req_fields = set()
    all_req_field_types = {}
    for req in user_visits_posts:
        if req['req_body']:
            for key, value in req['req_body'].items():
                all_req_fields.add(key)
                if key not in all_req_field_types:
                    all_req_field_types[key] = type(value).__name__

    print(f"\n=== All Unique Request Fields in POST /statistics/api/user-visits ({len(all_req_fields)} fields) ===")
    for field in sorted(all_req_fields):
        print(f"  - {field}: {all_req_field_types.get(field, 'unknown')}")

    # Save comprehensive data
    output = {
        'summary': {
            'total_items': len(items),
            'user_visits_posts': len(user_visits_posts),
            'user_visits_metrics_endpoints': len(user_visits_metrics),
            'online_video_metrics_endpoints': len(online_video_metrics),
            'interactions_metrics_endpoints': len(interactions_metrics),
            'activity_reads_endpoints': len(activity_reads),
            'online_video_setting_endpoints': len(online_video_setting)
        },
        'user_visits_posts': user_visits_posts[:20],  # Save first 20
        'all_request_fields': {
            'fields': sorted(list(all_req_fields)),
            'types': all_req_field_types
        },
        'user_visits_metrics': {k: v[:2] for k, v in user_visits_metrics.items()},
        'online_video_metrics': {k: v[:2] for k, v in online_video_metrics.items()},
        'interactions_metrics': {k: v[:2] for k, v in interactions_metrics.items()},
        'activity_reads': {k: v[:2] for k, v in activity_reads.items()},
        'online_video_setting': {k: v[:2] for k, v in online_video_setting.items()}
    }

    output_path = r'D:\Dev\eebot\comprehensive_analysis.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n[+] Saved to {output_path}")

    # Save visit duration analysis
    duration_data = []
    for req in user_visits_posts:
        if req['req_body'] and 'visit_duration' in req['req_body']:
            duration_data.append({
                'index': req['index'],
                'visit_duration': req['req_body']['visit_duration'],
                'visit_start_from': req['req_body'].get('visit_start_from'),
                'course_id': req['req_body'].get('course_id'),
                'activity_id': req['req_body'].get('activity_id')
            })

    duration_path = r'D:\Dev\eebot\visit_duration_analysis.json'
    with open(duration_path, 'w', encoding='utf-8') as f:
        json.dump(duration_data, f, ensure_ascii=False, indent=2)
    print(f"[+] Visit duration analysis saved to {duration_path}")

if __name__ == '__main__':
    main()
