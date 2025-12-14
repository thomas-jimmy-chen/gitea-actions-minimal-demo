#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速獲取學習履歷統計 - 從 my-courses API 計算
"""

import requests
import json
from pathlib import Path


def get_learning_stats(session_cookie):
    """
    從 /api/my-courses 獲取並計算學習統計

    返回:
    {
        'progress': 100.0,          # 學習進度 (%)
        'completed': 8,             # 完成課程數
        'total': 8,                 # 課程總數
        'in_progress': 0            # 進行中課程數
    }
    """

    url = "https://elearn.post.gov.tw/api/my-courses"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
    }
    cookies = {'aenrich_session': session_cookie}

    response = requests.get(url, headers=headers, cookies=cookies, timeout=10)

    if response.status_code == 200:
        data = response.json()
        courses = data.get('courses', [])

        total = len(courses)
        completed = len([c for c in courses if c.get('is_graduated') == True])
        in_progress = total - completed
        progress = (completed / total * 100) if total > 0 else 0

        return {
            'success': True,
            'progress': progress,
            'completed': completed,
            'total': total,
            'in_progress': in_progress,
            'courses': courses
        }
    else:
        return {
            'success': False,
            'error': f'HTTP {response.status_code}'
        }


def main():
    # 從 cookies.json 讀取
    cookies_path = Path("resource/cookies/cookies.json")

    if cookies_path.exists():
        with open(cookies_path, 'r') as f:
            cookies = json.load(f)
            for cookie in cookies:
                if cookie.get('name') == 'aenrich_session':
                    session_cookie = cookie.get('value')
                    break
    else:
        session_cookie = input("請輸入 session cookie: ").strip()

    # 獲取統計
    stats = get_learning_stats(session_cookie)

    if stats['success']:
        print("=" * 60)
        print("📊 學習履歷統計")
        print("=" * 60)
        print(f"學習進度: {stats['progress']:.1f}%")
        print(f"完成課程: {stats['completed']}")
        print(f"課程總數: {stats['total']}")
        print(f"進行中: {stats['in_progress']}")
        print("=" * 60)
    else:
        print(f"❌ 錯誤: {stats['error']}")


if __name__ == "__main__":
    main()
