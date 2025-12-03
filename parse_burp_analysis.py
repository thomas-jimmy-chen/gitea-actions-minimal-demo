#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析 Burp Suite XML 匯出檔案 - EEBot 平台 API 端點分析
"""

import xml.etree.ElementTree as ET
import base64
import json
from urllib.parse import unquote, parse_qs
from io import StringIO

def decode_base64(data):
    """解碼 base64"""
    try:
        return base64.b64decode(data).decode('utf-8', errors='replace')
    except Exception as e:
        print(f"解碼失敗: {e}")
        return data

def extract_headers(raw_http):
    """從原始 HTTP 請求提取 headers"""
    lines = raw_http.split('\n')
    headers = {}

    # 跳過第一行（請求行）
    for line in lines[1:]:
        if ':' in line and line.strip():
            key, value = line.split(':', 1)
            headers[key.strip()] = value.strip()
        elif not line.strip():
            break

    return headers

def extract_body(raw_http):
    """從原始 HTTP 請求/回應提取 body"""
    # 處理 \r\n\r\n 的情況
    if '\r\n\r\n' in raw_http:
        parts = raw_http.split('\r\n\r\n', 1)
    elif '\n\n' in raw_http:
        parts = raw_http.split('\n\n', 1)
    else:
        return ''

    if len(parts) > 1:
        return parts[1]
    return ''

def parse_form_data(body):
    """解析 URL encoded 表單資料"""
    try:
        pairs = parse_qs(body, keep_blank_values=True)
        # 轉換為單一值字典（而不是列表）
        return {k: v[0] if v else '' for k, v in pairs.items()}
    except:
        return {}

def main():
    xml_file = 'D:\\Dev\\eebot\\test1'

    try:
        tree = ET.parse(xml_file)
    except ET.ParseError as e:
        print(f"XML 解析錯誤: {e}")
        return

    root = tree.getroot()

    print("=" * 120)
    print("BURP SUITE XML 詳細分析報告 - EEBot 平台 API 端點")
    print("=" * 120)

    target_paths = {
        '/login?no_cas=&next=': 'POST登入請求',
        '/api/my-courses': '我的課程 API',
        '/api/exam-center/my-exams': '考試中心 API',
        '/api/curriculums': '課程計畫 API'
    }

    items = root.findall('item')

    for idx, item in enumerate(items):
        path_elem = item.find('path')
        method_elem = item.find('method')
        url_elem = item.find('url')
        status_elem = item.find('status')

        if path_elem is not None:
            path = path_elem.text
            method = method_elem.text if method_elem is not None else ''
            url = url_elem.text if url_elem is not None else ''
            status = status_elem.text if status_elem is not None else ''

            # 檢查是否是目標路徑
            matched_target = None
            for target_path, target_name in target_paths.items():
                if target_path in path:
                    matched_target = target_name
                    break

            if matched_target:
                print(f"\n{'='*120}")
                print(f"API 端點 #{idx+1}: {matched_target}")
                print(f"{'='*120}\n")
                print(f"URL: {url}")
                print(f"方法: {method}")
                print(f"回應狀態: {status}\n")

                # 解析 Request
                request_elem = item.find('request')
                if request_elem is not None:
                    is_base64 = request_elem.get('base64', 'false') == 'true'
                    request_data = request_elem.text

                    if is_base64:
                        request_data = decode_base64(request_data)

                    print("REQUEST 詳情")
                    print("-" * 120)

                    headers = extract_headers(request_data)
                    print("\n【Request Headers】")
                    for key, value in sorted(headers.items()):
                        if key.lower() == 'cookie':
                            # Cookie 單獨顯示
                            print(f"  {key}:")
                            for cookie_part in value.split(';'):
                                if cookie_part.strip():
                                    print(f"    - {cookie_part.strip()}")
                        else:
                            print(f"  {key}: {value}")

                    body = extract_body(request_data)
                    if body.strip():
                        print("\n【Request Body】")
                        # 檢查是否是 URL encoded 表單
                        if 'application/x-www-form-urlencoded' in headers.get('Content-Type', ''):
                            form_data = parse_form_data(body)
                            print("  (URL Encoded Form Data)")
                            for key, value in form_data.items():
                                # 嘗試解碼 base64 值
                                try:
                                    if len(value) > 20 and all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=' for c in value):
                                        decoded = decode_base64(value)
                                        print(f"  {key}: [base64] {decoded[:50]}")
                                    else:
                                        print(f"  {key}: {value}")
                                except:
                                    print(f"  {key}: {value}")
                        elif 'application/json' in headers.get('Content-Type', ''):
                            try:
                                body_json = json.loads(body)
                                print(json.dumps(body_json, indent=4, ensure_ascii=False))
                            except:
                                print(body[:500])
                        else:
                            print(body[:500])

                # 解析 Response
                response_elem = item.find('response')
                if response_elem is not None:
                    is_base64 = response_elem.get('base64', 'false') == 'true'
                    response_data = response_elem.text

                    if is_base64:
                        response_data = decode_base64(response_data)

                    print("\n\nRESPONSE 詳情")
                    print("-" * 120)

                    resp_headers = extract_headers(response_data)
                    print("\n【Response Headers】")
                    for key, value in sorted(resp_headers.items()):
                        if key.lower() == 'set-cookie':
                            print(f"  {key}: {value}")
                        else:
                            print(f"  {key}: {value}")

                    resp_body = extract_body(response_data)
                    if resp_body.strip():
                        print("\n【Response Body (前 20 個欄位)】")

                        # 嘗試解析 JSON
                        try:
                            resp_json = json.loads(resp_body)
                            if isinstance(resp_json, dict):
                                print("  Type: Object/Dictionary")
                                for i, (key, value) in enumerate(resp_json.items()):
                                    if i < 20:
                                        val_str = str(value)
                                        if len(val_str) > 80:
                                            val_str = val_str[:77] + "..."
                                        print(f"  {key}: {val_str}")
                                    else:
                                        print(f"  ... (還有 {len(resp_json) - 20} 個欄位)")
                                        break
                            elif isinstance(resp_json, list):
                                print(f"  Type: Array (長度: {len(resp_json)})")
                                for i, item_data in enumerate(resp_json[:5]):
                                    print(f"  [{i}]: {str(item_data)[:100]}")
                                if len(resp_json) > 5:
                                    print(f"  ... (還有 {len(resp_json) - 5} 個項目)")
                        except json.JSONDecodeError:
                            # 不是 JSON，顯示前 500 字
                            print("  (非 JSON 內容)")
                            print(resp_body[:500])

                print()

if __name__ == '__main__':
    main()
