#!/usr/bin/env python3
"""
test3 Exam API 分析腳本
專門分析考試相關的 API 請求，包括：
1. Cookies 欄位對應
2. 考試提交機制
3. 題目與答案結構
4. 是否能用 JSON 產生應答
"""

import xml.etree.ElementTree as ET
import base64
import json
from collections import defaultdict
from urllib.parse import urlparse, parse_qs
import re

def parse_burp_xml(filename):
    """解析 Burp Suite XML 檔案"""
    tree = ET.parse(filename)
    root = tree.getroot()
    return root.findall('item')

def decode_base64(data):
    """解碼 base64 資料"""
    if not data:
        return ""
    try:
        return base64.b64decode(data).decode('utf-8', errors='ignore')
    except:
        return ""

def extract_cookies(request_text):
    """提取 cookies 資訊"""
    cookies = {}
    for line in request_text.split('\n'):
        if line.startswith('Cookie:'):
            cookie_str = line[7:].strip()
            for cookie in cookie_str.split('; '):
                if '=' in cookie:
                    key, value = cookie.split('=', 1)
                    cookies[key] = value
    return cookies

def analyze_exam_apis(items):
    """分析考試相關的 API"""
    exam_apis = {
        'exams': [],           # GET /api/courses/{id}/exams
        'submitted_exams': [], # GET /api/courses/{id}/submitted-exams
        'exam_scores': [],     # GET /api/courses/{id}/exam-scores
        'submit_exam': [],     # POST 提交考試答案
    }

    cookies_summary = defaultdict(set)

    for item in items:
        url_elem = item.find('url')
        if url_elem is None:
            continue

        url = url_elem.text
        path = urlparse(url).path

        # 檢查是否為考試相關 API
        is_exam_api = False
        api_type = None

        if '/exams' in path and '/submitted-exams' not in path and '/exam-scores' not in path:
            is_exam_api = True
            api_type = 'exams'
        elif '/submitted-exams' in path:
            is_exam_api = True
            api_type = 'submitted_exams'
        elif '/exam-scores' in path:
            is_exam_api = True
            api_type = 'exam_scores'
        elif 'submit' in path.lower() and 'exam' in path.lower():
            is_exam_api = True
            api_type = 'submit_exam'

        if not is_exam_api:
            continue

        # 解析請求
        request_elem = item.find('request')
        response_elem = item.find('response')

        if request_elem is None:
            continue

        request_text = decode_base64(request_elem.text)
        response_text = decode_base64(response_elem.text) if response_elem is not None else ""

        # 提取 HTTP 方法
        method = item.find('method').text if item.find('method') is not None else "UNKNOWN"

        # 提取 cookies
        cookies = extract_cookies(request_text)
        for key in cookies.keys():
            cookies_summary[key].add(api_type)

        # 提取 request body
        request_body = ""
        if '\r\n\r\n' in request_text:
            request_body = request_text.split('\r\n\r\n', 1)[1]

        # 提取 response body
        response_body = ""
        response_status = ""
        if response_text:
            lines = response_text.split('\r\n')
            if lines:
                response_status = lines[0]
            if '\r\n\r\n' in response_text:
                response_body = response_text.split('\r\n\r\n', 1)[1]

        # 儲存資料
        api_data = {
            'url': url,
            'method': method,
            'cookies': cookies,
            'request_body': request_body[:1000],  # 限制長度
            'response_status': response_status,
            'response_body': response_body[:2000],  # 限制長度
        }

        exam_apis[api_type].append(api_data)

    return exam_apis, cookies_summary

def analyze_exam_structure(exam_apis):
    """分析考試結構（題目、選項、答案）"""
    exam_structure = {
        'questions_format': None,
        'answer_format': None,
        'submission_format': None,
    }

    # 分析 GET /exams 的回應（取得考試題目）
    if exam_apis['exams']:
        for api in exam_apis['exams']:
            body = api['response_body']
            if body and len(body) > 10:
                try:
                    data = json.loads(body)
                    exam_structure['questions_format'] = {
                        'sample': json.dumps(data, ensure_ascii=False, indent=2)[:1000],
                        'has_questions': 'questions' in str(data).lower(),
                        'has_subjects': 'subjects' in str(data).lower(),
                        'has_options': 'options' in str(data).lower(),
                    }
                    break
                except:
                    pass

    # 分析 GET /submitted-exams（已提交的答案）
    if exam_apis['submitted_exams']:
        for api in exam_apis['submitted_exams']:
            body = api['response_body']
            if body and len(body) > 10:
                try:
                    data = json.loads(body)
                    exam_structure['answer_format'] = {
                        'sample': json.dumps(data, ensure_ascii=False, indent=2)[:1000],
                        'has_answers': 'answer' in str(data).lower(),
                        'has_selections': 'select' in str(data).lower(),
                    }
                    break
                except:
                    pass

    # 分析 POST submit（提交答案的格式）
    if exam_apis['submit_exam']:
        for api in exam_apis['submit_exam']:
            body = api['request_body']
            if body and len(body) > 10:
                try:
                    data = json.loads(body)
                    exam_structure['submission_format'] = {
                        'sample': json.dumps(data, ensure_ascii=False, indent=2)[:1000],
                    }
                    break
                except:
                    pass

    return exam_structure

def main():
    print("[*] 分析 test3 中的考試相關 API...")

    items = parse_burp_xml('test3')
    print(f"[+] 共找到 {len(items)} 個請求")

    # 分析考試 API
    exam_apis, cookies_summary = analyze_exam_apis(items)

    print("\n=== 考試 API 統計 ===")
    print(f"  GET /exams: {len(exam_apis['exams'])} 次")
    print(f"  GET /submitted-exams: {len(exam_apis['submitted_exams'])} 次")
    print(f"  GET /exam-scores: {len(exam_apis['exam_scores'])} 次")
    print(f"  POST submit: {len(exam_apis['submit_exam'])} 次")

    # 分析考試結構
    exam_structure = analyze_exam_structure(exam_apis)

    # 儲存結果
    result = {
        'summary': {
            'total_items': len(items),
            'exam_apis_count': sum(len(v) for v in exam_apis.values()),
            'api_breakdown': {k: len(v) for k, v in exam_apis.items()},
        },
        'cookies': {k: list(v) for k, v in cookies_summary.items()},
        'exam_apis': exam_apis,
        'exam_structure': exam_structure,
    }

    with open('test3_exam_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("\n[+] 分析完成，結果已儲存到 test3_exam_analysis.json")

    # 顯示 Cookies 摘要
    print("\n=== Cookies 摘要 ===")
    for cookie_name, api_types in sorted(cookies_summary.items()):
        print(f"  {cookie_name}: 用於 {', '.join(sorted(api_types))}")

    # 顯示考試結構
    print("\n=== 考試結構分析 ===")
    if exam_structure['questions_format']:
        print("  [題目格式]")
        print(f"    - 包含 questions: {exam_structure['questions_format']['has_questions']}")
        print(f"    - 包含 subjects: {exam_structure['questions_format']['has_subjects']}")
        print(f"    - 包含 options: {exam_structure['questions_format']['has_options']}")

    if exam_structure['answer_format']:
        print("  [答案格式]")
        print(f"    - 包含 answer: {exam_structure['answer_format']['has_answers']}")
        print(f"    - 包含 select: {exam_structure['answer_format']['has_selections']}")

    if exam_structure['submission_format']:
        print("  [提交格式] 已找到")

    # 顯示範例
    if exam_apis['exams']:
        print("\n=== 範例：GET /exams ===")
        example = exam_apis['exams'][0]
        print(f"  URL: {example['url']}")
        print(f"  Method: {example['method']}")
        print(f"  Response Status: {example['response_status']}")
        print(f"  Cookies: {list(example['cookies'].keys())}")
        if example['response_body']:
            print(f"  Response Body (前200字): {example['response_body'][:200]}")

if __name__ == '__main__':
    main()
