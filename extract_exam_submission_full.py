#!/usr/bin/env python3
"""
完整提取 test3 中的考試提交資料
包括題目、答案、欄位對應關係
"""

import xml.etree.ElementTree as ET
import base64
import json
from urllib.parse import urlparse
import re

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

def extract_exam_submissions(items):
    """提取所有考試提交請求"""
    submissions = []

    for item in items:
        url_elem = item.find('url')
        if url_elem is None:
            continue

        url = url_elem.text
        path = urlparse(url).path

        # 只處理 /api/exams/{id}/submissions（不包含 /storage）
        if not re.match(r'/api/exams/\d+/submissions$', path):
            continue

        method_elem = item.find('method')
        if method_elem is None or method_elem.text != 'POST':
            continue

        request_elem = item.find('request')
        response_elem = item.find('response')

        if request_elem is None:
            continue

        request_text = decode_base64(request_elem.text)
        response_text = decode_base64(response_elem.text) if response_elem is not None else ""

        # 提取 cookies
        cookies = extract_cookies(request_text)

        # 提取 request body
        request_body = ""
        if '\r\n\r\n' in request_text:
            request_body = request_text.split('\r\n\r\n', 1)[1]

        # 解析 JSON
        try:
            body_json = json.loads(request_body)
        except:
            body_json = None

        # 提取 response
        response_body = ""
        response_status = ""
        if response_text:
            lines = response_text.split('\r\n')
            if lines:
                response_status = lines[0]
            if '\r\n\r\n' in response_text:
                response_body = response_text.split('\r\n\r\n', 1)[1]

        # 提取 exam_id
        match = re.search(r'/api/exams/(\d+)/submissions', path)
        exam_id = match.group(1) if match else None

        submissions.append({
            'exam_id': exam_id,
            'url': url,
            'cookies': cookies,
            'request_body': body_json,
            'response_status': response_status,
            'response_body': response_body[:1000],
        })

    return submissions

def extract_exam_questions(items):
    """提取考試題目（GET /api/courses/{id}/exams）"""
    exam_questions = {}

    for item in items:
        url_elem = item.find('url')
        if url_elem is None:
            continue

        url = url_elem.text
        path = urlparse(url).path

        # 只處理 /api/courses/{id}/exams
        if not re.match(r'/api/courses/\d+/exams$', path):
            continue

        method_elem = item.find('method')
        if method_elem is None or method_elem.text != 'GET':
            continue

        response_elem = item.find('response')
        if response_elem is None:
            continue

        response_text = decode_base64(response_elem.text)

        # 提取 response body
        response_body = ""
        if '\r\n\r\n' in response_text:
            response_body = response_text.split('\r\n\r\n', 1)[1]

        # 解析 JSON
        try:
            body_json = json.loads(response_body)
            if body_json and 'exams' in body_json and body_json['exams']:
                # 提取 course_id
                match = re.search(r'/api/courses/(\d+)/exams', path)
                course_id = match.group(1) if match else None

                exam_questions[course_id] = body_json
        except:
            pass

    return exam_questions

def analyze_submission_structure(submissions):
    """分析提交結構"""
    if not submissions:
        return None

    # 使用第一個提交作為範例
    example = submissions[0]
    body = example.get('request_body')

    if not body:
        return None

    structure = {
        'fields': list(body.keys()),
        'exam_paper_instance_id': {
            'type': type(body.get('exam_paper_instance_id')).__name__,
            'example': body.get('exam_paper_instance_id'),
        },
        'exam_submission_id': {
            'type': type(body.get('exam_submission_id')).__name__,
            'example': body.get('exam_submission_id'),
        },
        'subjects': {
            'is_array': isinstance(body.get('subjects'), list),
            'count': len(body.get('subjects', [])),
        }
    }

    # 分析 subjects 結構
    subjects = body.get('subjects', [])
    if subjects:
        subject_example = subjects[0]
        structure['subjects']['fields'] = list(subject_example.keys())
        structure['subjects']['subject_id_type'] = type(subject_example.get('subject_id')).__name__
        structure['subjects']['answer_option_ids_type'] = type(subject_example.get('answer_option_ids')).__name__
        structure['subjects']['example'] = subject_example

    return structure

def main():
    print("[*] 完整提取 test3 考試提交資料...")

    items = parse_burp_xml('test3')
    print(f"[+] 共找到 {len(items)} 個請求")

    # 提取考試提交
    submissions = extract_exam_submissions(items)
    print(f"[+] 找到 {len(submissions)} 個考試提交（/api/exams/{'{id}'}/submissions）")

    # 提取考試題目
    exam_questions = extract_exam_questions(items)
    print(f"[+] 找到 {len(exam_questions)} 個課程的考試題目")

    # 分析提交結構
    structure = analyze_submission_structure(submissions)

    # 儲存結果
    result = {
        'summary': {
            'total_submissions': len(submissions),
            'exam_ids': sorted(set(s['exam_id'] for s in submissions)),
            'courses_with_exams': sorted(exam_questions.keys()),
        },
        'submission_structure': structure,
        'submissions': submissions,
        'exam_questions': exam_questions,
        'cookies_required': list(submissions[0]['cookies'].keys()) if submissions else [],
    }

    with open('test3_exam_submission_full.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("\n[+] 結果已儲存到 test3_exam_submission_full.json")

    # 顯示結構分析
    print("\n=== 考試提交結構分析 ===")
    if structure:
        print(f"  欄位: {', '.join(structure['fields'])}")
        print(f"  exam_paper_instance_id: {structure['exam_paper_instance_id']['type']} (範例: {structure['exam_paper_instance_id']['example']})")
        print(f"  exam_submission_id: {structure['exam_submission_id']['type']} (範例: {structure['exam_submission_id']['example']})")
        print(f"  subjects: 陣列, 共 {structure['subjects']['count']} 題")
        if 'fields' in structure['subjects']:
            print(f"    - 欄位: {', '.join(structure['subjects']['fields'])}")
            print(f"    - subject_id: {structure['subjects']['subject_id_type']}")
            print(f"    - answer_option_ids: {structure['subjects']['answer_option_ids_type']}")
            print(f"    - 範例: {json.dumps(structure['subjects']['example'], ensure_ascii=False)}")

    # 顯示必要的 Cookies
    print("\n=== 必要的 Cookies ===")
    if submissions:
        cookies = submissions[0]['cookies']
        for key in sorted(cookies.keys()):
            print(f"  {key}")

    # 顯示範例
    if submissions:
        print("\n=== 提交範例 ===")
        example = submissions[0]
        print(f"  Exam ID: {example['exam_id']}")
        print(f"  URL: {example['url']}")
        print(f"  Response Status: {example['response_status']}")
        if example['request_body']:
            body = example['request_body']
            print(f"  題目數量: {len(body.get('subjects', []))}")
            if body.get('subjects'):
                first_subject = body['subjects'][0]
                print(f"  第一題範例: subject_id={first_subject.get('subject_id')}, answer_option_ids={first_subject.get('answer_option_ids')}")

if __name__ == '__main__':
    main()
