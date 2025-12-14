#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
測試學習履歷統計 API
目標: 找出首頁「學習進度 100%、完成課程 8、課程總數 8」的資料來源
"""

import requests
import json
from pathlib import Path
import sys

# 添加專案根目錄到 path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.config_loader import ConfigLoader


def test_statistics_apis(session_cookie):
    """測試可能的統計 API 端點"""

    base_url = "https://elearn.post.gov.tw"

    # 可能的統計 API 端點列表
    endpoints = [
        "/api/user/statistics",
        "/api/dashboard/summary",
        "/api/learning/progress",
        "/api/my-learning-stats",
        "/api/user/progress",
        "/api/student/statistics",
        "/api/my-dashboard",
        "/api/learning-record",
        "/api/user/learning-history",
        "/api/courses/statistics",
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Referer': 'https://elearn.post.gov.tw/'
    }

    cookies = {'aenrich_session': session_cookie}

    results = []

    print("=" * 80)
    print("測試學習履歷統計 API")
    print("=" * 80)
    print()

    for endpoint in endpoints:
        url = base_url + endpoint
        print(f"測試: {endpoint}")

        try:
            response = requests.get(
                url,
                headers=headers,
                cookies=cookies,
                timeout=10
            )

            result = {
                'endpoint': endpoint,
                'status_code': response.status_code,
                'success': response.status_code == 200
            }

            if response.status_code == 200:
                try:
                    data = response.json()
                    result['has_data'] = True
                    result['data'] = data
                    print(f"  ✅ 成功 (200) - 有資料!")
                    print(f"  資料預覽: {json.dumps(data, ensure_ascii=False)[:200]}...")
                except:
                    result['has_data'] = False
                    result['response_text'] = response.text[:200]
                    print(f"  ✅ 成功 (200) - 但非 JSON 格式")
            else:
                result['has_data'] = False
                print(f"  ❌ 失敗 ({response.status_code})")

            results.append(result)

        except requests.exceptions.Timeout:
            print(f"  ⏰ 超時")
            results.append({
                'endpoint': endpoint,
                'status_code': 'timeout',
                'success': False
            })
        except Exception as e:
            print(f"  ❌ 錯誤: {str(e)}")
            results.append({
                'endpoint': endpoint,
                'status_code': 'error',
                'success': False,
                'error': str(e)
            })

        print()

    return results


def calculate_from_my_courses(session_cookie):
    """從 my-courses API 計算統計資料"""

    print("=" * 80)
    print("從 /api/my-courses 計算統計資料")
    print("=" * 80)
    print()

    url = "https://elearn.post.gov.tw/api/my-courses"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Referer': 'https://elearn.post.gov.tw/'
    }
    cookies = {'aenrich_session': session_cookie}

    try:
        response = requests.get(url, headers=headers, cookies=cookies, timeout=10)

        if response.status_code == 200:
            data = response.json()
            courses = data.get('courses', [])

            # 計算統計
            total_courses = len(courses)
            completed_courses = len([c for c in courses if c.get('is_graduated') == True])
            in_progress_courses = len([c for c in courses if c.get('is_graduated') == False])
            progress = (completed_courses / total_courses * 100) if total_courses > 0 else 0

            print(f"📊 學習履歷統計:")
            print(f"  學習進度: {progress:.1f}%")
            print(f"  完成課程: {completed_courses}")
            print(f"  進行中課程: {in_progress_courses}")
            print(f"  課程總數: {total_courses}")
            print()

            # 詳細列表
            print("📚 課程明細:")
            for course in courses:
                status = "✅ 已完成" if course.get('is_graduated') else "🔄 進行中"
                print(f"  {status} - {course.get('name')}")

            return {
                'success': True,
                'total': total_courses,
                'completed': completed_courses,
                'in_progress': in_progress_courses,
                'progress': progress,
                'courses': courses
            }
        else:
            print(f"❌ API 調用失敗: {response.status_code}")
            return {'success': False, 'error': f'HTTP {response.status_code}'}

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")
        return {'success': False, 'error': str(e)}


def main():
    """主程式"""

    # 載入配置
    config = ConfigLoader("config/eebot.cfg")
    config.load()

    # 提示用戶輸入 session cookie
    print("=" * 80)
    print("學習履歷統計 API 測試工具")
    print("=" * 80)
    print()
    print("請提供 session cookie (aenrich_session):")
    print("  方法 1: 從瀏覽器開發者工具複製")
    print("  方法 2: 使用已登入的 cookies.json")
    print()

    # 嘗試從 cookies.json 讀取
    cookies_path = Path("resource/cookies/cookies.json")
    if cookies_path.exists():
        try:
            with open(cookies_path, 'r') as f:
                cookies = json.load(f)
                for cookie in cookies:
                    if cookie.get('name') == 'aenrich_session':
                        session_cookie = cookie.get('value')
                        print(f"✅ 從 {cookies_path} 載入 session cookie")
                        break
                else:
                    session_cookie = input("請輸入 session cookie: ").strip()
        except:
            session_cookie = input("請輸入 session cookie: ").strip()
    else:
        session_cookie = input("請輸入 session cookie: ").strip()

    print()

    # 測試 1: 從 my-courses 計算
    calc_result = calculate_from_my_courses(session_cookie)
    print()

    # 測試 2: 尋找專門的統計 API
    print("=" * 80)
    print("尋找專門的統計 API 端點")
    print("=" * 80)
    print()

    api_results = test_statistics_apis(session_cookie)

    # 儲存結果
    output = {
        'calculated_from_my_courses': calc_result,
        'api_test_results': api_results,
        'successful_endpoints': [r for r in api_results if r.get('success')]
    }

    output_path = Path("learning_stats_api_test_result.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("=" * 80)
    print("測試完成")
    print("=" * 80)
    print()
    print(f"結果已儲存至: {output_path}")
    print()

    # 總結
    successful = [r for r in api_results if r.get('success')]
    if successful:
        print(f"✅ 找到 {len(successful)} 個有效的統計 API:")
        for r in successful:
            print(f"  - {r['endpoint']}")
    else:
        print("❌ 未找到專門的統計 API")
        print("✅ 建議使用 /api/my-courses 計算統計資料")


if __name__ == "__main__":
    main()
