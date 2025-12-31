#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
Burp Suite POST /statistics/api/user-visits 請求分析工具
"""

import base64
import json
import xml.etree.ElementTree as ET

def decode_request(base64_text):
    """解碼 base64 請求"""
    decoded = base64.b64decode(base64_text).decode('utf-8', errors='ignore')
    return decoded

def extract_json_payload(request_text):
    """從 HTTP 請求中提取 JSON payload"""
    # 分離 headers 和 body
    parts = request_text.split('\r\n\r\n', 1)
    if len(parts) == 2:
        return parts[1].strip()
    return None

def analyze_burp_file(filepath):
    """分析 Burp Suite XML 檔案"""
    tree = ET.parse(filepath)
    root = tree.getroot()

    print("=" * 80)
    print("Burp Suite POST /statistics/api/user-visits 請求分析")
    print("=" * 80)
    print()

    requests_data = []

    for idx, item in enumerate(root.findall('item'), 1):
        time = item.find('time').text
        request_base64 = item.find('request').text

        # 解碼請求
        request_text = decode_request(request_base64)
        json_text = extract_json_payload(request_text)

        if json_text:
            try:
                payload = json.loads(json_text)
                requests_data.append({
                    'index': idx,
                    'time': time,
                    'payload': payload
                })

                print(f"【請求 #{idx}】")
                print(f"時間: {time}")
                print(f"JSON Payload:")
                print(json.dumps(payload, indent=2, ensure_ascii=False))
                print()

            except json.JSONDecodeError as e:
                print(f"[WARNING] 請求 #{idx} JSON 解析失敗: {e}")

    # 統計分析
    print("=" * 80)
    print("統計分析")
    print("=" * 80)
    print()

    # 欄位統計
    all_fields = set()
    field_frequency = {}

    for req in requests_data:
        for field in req['payload'].keys():
            all_fields.add(field)
            field_frequency[field] = field_frequency.get(field, 0) + 1

    print(f"總請求數: {len(requests_data)}")
    print(f"不同欄位數: {len(all_fields)}")
    print()

    print("欄位出現頻率:")
    for field, count in sorted(field_frequency.items(), key=lambda x: -x[1]):
        percentage = (count / len(requests_data)) * 100
        print(f"  {field:20s}: {count}/{len(requests_data)} ({percentage:.1f}%)")
    print()

    # 時長分析
    durations = [req['payload'].get('visit_duration', 0) for req in requests_data]
    print("時長統計:")
    print(f"  最小值: {min(durations)} 秒")
    print(f"  最大值: {max(durations)} 秒")
    print(f"  平均值: {sum(durations) / len(durations):.2f} 秒")
    print(f"  所有時長: {durations}")
    print()

    # 課程相關請求分析
    course_requests = [req for req in requests_data if 'course_id' in req['payload']]
    print(f"包含 course_id 的請求: {len(course_requests)}/{len(requests_data)}")

    if course_requests:
        print("\n課程相關請求詳情:")
        for req in course_requests:
            payload = req['payload']
            print(f"  請求 #{req['index']}:")
            print(f"    course_id: {payload.get('course_id')}")
            print(f"    course_code: {payload.get('course_code')}")
            print(f"    course_name: {payload.get('course_name', 'N/A')[:50]}...")
            print(f"    visit_duration: {payload.get('visit_duration')} 秒")
            print()

    # 分析 org_id 類型
    print("org_id 類型分析:")
    for req in requests_data[:3]:
        org_id = req['payload'].get('org_id')
        print(f"  請求 #{req['index']}: org_id = {repr(org_id)} (type: {type(org_id).__name__})")
    print()

    # 分析 Content-Type
    print("從第一個請求提取 Headers:")
    first_request = decode_request(root.find('item').find('request').text)
    headers_section = first_request.split('\r\n\r\n')[0]
    for line in headers_section.split('\r\n'):
        if 'Content-Type' in line or 'Referer' in line or 'Origin' in line:
            print(f"  {line}")
    print()

    return requests_data

def generate_recommendations(requests_data):
    """生成改進建議"""
    print("=" * 80)
    print("改進建議 - 如何應用於 menu.py Stage 6")
    print("=" * 80)
    print()

    print("【發現 1】Content-Type 使用")
    print("  真實請求: text/plain;charset=UTF-8")
    print("  當前代碼: application/json")
    print("  建議: 修改 visit_duration_api.py 的 headers")
    print()

    print("【發現 2】org_id 類型不一致")
    print("  真實請求: 有時是字串 '1'，有時是數字 1")
    print("  建議: 統一使用字串 '1' 或數字 1，觀察哪種更穩定")
    print()

    print("【發現 3】時長發送模式")
    durations = [req['payload'].get('visit_duration', 0) for req in requests_data]
    print(f"  觀察到的時長: {durations}")
    print("  分析: 包含大時長 (892秒) 和小時長 (6秒、0秒、13秒)")
    print("  建議: 當前分批發送策略（每批 ≤60分鐘）符合實際模式")
    print()

    print("【發現 4】Referer 頭不同場景")
    print("  無課程: /user/index 或 /user/courses")
    print("  有課程: /course/{course_id}/content")
    print("  建議: 根據是否有 course_id 動態設置 Referer")
    print()

    print("【發現 5】必需欄位清單")
    all_fields = set()
    for req in requests_data:
        all_fields.update(req['payload'].keys())

    # 計算出現在所有請求中的欄位
    required_fields = set(requests_data[0]['payload'].keys())
    for req in requests_data[1:]:
        required_fields &= set(req['payload'].keys())

    print(f"  必需欄位 (出現在所有請求): {sorted(required_fields)}")
    print(f"  可選欄位: {sorted(all_fields - required_fields)}")
    print()

    print("【發現 6】課程欄位組合")
    course_req = next((req for req in requests_data if 'course_id' in req['payload']), None)
    if course_req:
        course_fields = [f for f in course_req['payload'].keys() if 'course' in f or 'master' in f]
        print(f"  課程相關欄位: {course_fields}")
        print("  建議: 發送課程時長時，必須包含這些欄位")
    print()

if __name__ == '__main__':
    # 分析 Burp Suite 檔案
    filepath = 'POST_statistics_api_user-visits.txt'
    requests_data = analyze_burp_file(filepath)

    # 生成建議
    generate_recommendations(requests_data)

    print("\n" + "=" * 80)
    print("分析完成！")
    print("=" * 80)
