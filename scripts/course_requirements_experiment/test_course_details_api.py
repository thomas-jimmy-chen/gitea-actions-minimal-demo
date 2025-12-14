#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
課程詳細 API 探索實驗
測試是否有 API 端點可以獲取課程通過條件（觀看時長、測驗成績）

創建日期: 2025-12-05
用途: 探索課程詳細資訊 API
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from src.core.config_loader import ConfigLoader


class CourseDetailsAPIExplorer:
    """課程詳細 API 探索器"""

    def __init__(self):
        self.config = None
        self.base_url = None
        self.cookies = None
        self.test_results = []

    def step1_load_config_and_cookies(self):
        """Step 1: 載入配置與 Cookie"""
        print("=" * 60)
        print("[Step 1/3] 載入配置與 Cookie...")
        print("=" * 60)

        # 載入配置
        config_path = PROJECT_ROOT / 'config' / 'eebot.cfg'
        self.config = ConfigLoader(str(config_path))
        self.config.load()

        target_url = self.config.get('target_http')
        parsed = urlparse(target_url)
        self.base_url = f"{parsed.scheme}://{parsed.netloc}"

        print(f"[SUCCESS] 基礎 URL: {self.base_url}")

        # 載入 Cookie
        cookie_file = PROJECT_ROOT / 'resource' / 'cookies' / 'cookies.json'
        if not cookie_file.exists():
            print(f"[ERROR] Cookie 檔案不存在: {cookie_file}")
            print("[HINT] 請先執行登入獲取 Cookie")
            sys.exit(1)

        with open(cookie_file, 'r', encoding='utf-8-sig') as f:
            cookie_list = json.load(f)
            self.cookies = {c['name']: c['value'] for c in cookie_list}

        print(f"[SUCCESS] 載入 {len(self.cookies)} 個 Cookie")
        print()

    def step2_get_sample_course_ids(self):
        """Step 2: 獲取樣本課程 ID"""
        print("=" * 60)
        print("[Step 2/3] 獲取樣本課程 ID...")
        print("=" * 60)

        # 從 my-courses API 獲取課程列表
        api_url = f"{self.base_url}/api/my-courses"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        }

        try:
            response = requests.get(
                api_url,
                cookies=self.cookies,
                headers=headers,
                verify=False,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                courses = data.get('courses', [])

                # 取前 5 個課程作為樣本
                sample_courses = courses[:5]
                sample_ids = [c['id'] for c in sample_courses]

                print(f"[SUCCESS] 獲取 {len(courses)} 個課程")
                print(f"[INFO] 樣本課程 ID: {sample_ids}")
                print()

                return sample_ids

            else:
                print(f"[ERROR] API 調用失敗: {response.status_code}")
                sys.exit(1)

        except Exception as e:
            print(f"[ERROR] 請求異常: {e}")
            sys.exit(1)

    def step3_explore_api_endpoints(self, course_ids):
        """Step 3: 探索 API 端點"""
        print("=" * 60)
        print("[Step 3/3] 探索課程詳細 API 端點...")
        print("=" * 60)

        # 要測試的端點模板
        endpoints = [
            "/api/courses/{id}",
            "/api/courses/{id}/details",
            "/api/courses/{id}/modules",
            "/api/courses/{id}/requirements",
            "/api/courses/{id}/info",
            "/api/my-courses/{id}",
            "/api/course/{id}",
        ]

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        }

        # 測試第一個課程 ID
        test_id = course_ids[0]
        print(f"\n[INFO] 使用課程 ID {test_id} 進行測試\n")

        for endpoint_template in endpoints:
            endpoint = endpoint_template.format(id=test_id)
            full_url = f"{self.base_url}{endpoint}"

            print(f"[Testing] {endpoint}")

            try:
                response = requests.get(
                    full_url,
                    cookies=self.cookies,
                    headers=headers,
                    verify=False,
                    timeout=10
                )

                result = {
                    'endpoint': endpoint,
                    'status_code': response.status_code,
                    'success': response.status_code == 200,
                    'response_size': len(response.text) if response.text else 0,
                    'has_json': False,
                    'fields': []
                }

                if response.status_code == 200:
                    try:
                        json_data = response.json()
                        result['has_json'] = True
                        result['fields'] = list(json_data.keys()) if isinstance(json_data, dict) else []

                        print(f"  ✅ 成功 (200) - {len(response.text)} bytes")
                        print(f"     欄位: {result['fields'][:10]}")  # 只顯示前 10 個

                        # 檢查是否包含通過條件相關欄位
                        potential_fields = [
                            'required_duration', 'duration_requirement', 'required_time',
                            'required_score', 'score_requirement', 'pass_score',
                            'requirements', 'pass_requirements', 'completion_requirements'
                        ]

                        found_fields = [f for f in potential_fields if f in json_data or f in str(json_data).lower()]
                        if found_fields:
                            print(f"     ⭐ 找到相關欄位: {found_fields}")
                            result['relevant_fields'] = found_fields

                    except json.JSONDecodeError:
                        print(f"  ⚠️  成功 (200) - 但回應不是 JSON")

                elif response.status_code == 404:
                    print(f"  ❌ 未找到 (404)")
                elif response.status_code == 401:
                    print(f"  ❌ 未授權 (401)")
                elif response.status_code == 403:
                    print(f"  ❌ 禁止訪問 (403)")
                else:
                    print(f"  ⚠️  狀態碼: {response.status_code}")

                self.test_results.append(result)

            except requests.exceptions.Timeout:
                print(f"  ⏱️  超時")
                self.test_results.append({
                    'endpoint': endpoint,
                    'status_code': None,
                    'success': False,
                    'error': 'Timeout'
                })
            except Exception as e:
                print(f"  ❌ 異常: {str(e)[:50]}")
                self.test_results.append({
                    'endpoint': endpoint,
                    'status_code': None,
                    'success': False,
                    'error': str(e)[:100]
                })

        print()

    def step4_generate_report(self):
        """Step 4: 生成報告"""
        print("=" * 60)
        print("[Step 4/4] 生成探索報告...")
        print("=" * 60)

        # 統計
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r['success']])

        # 生成報告
        report = self._build_report(total_tests, successful_tests)

        # 儲存報告
        output_dir = PROJECT_ROOT / 'scripts' / 'course_requirements_experiment' / 'results'
        output_dir.mkdir(parents=True, exist_ok=True)

        report_file = output_dir / 'api_exploration_report.md'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"[SUCCESS] 報告已儲存: {report_file}")
        print()

        # 顯示結論
        print("=" * 60)
        print("  探索結論")
        print("=" * 60)

        if successful_tests > 0:
            print(f"✅ 找到 {successful_tests} 個有效端點")

            # 檢查是否有相關欄位
            relevant_results = [r for r in self.test_results if r.get('relevant_fields')]
            if relevant_results:
                print(f"⭐ 找到包含相關欄位的端點：")
                for r in relevant_results:
                    print(f"   - {r['endpoint']}: {r.get('relevant_fields')}")
            else:
                print(f"⚠️  但都不包含通過條件相關欄位")
        else:
            print(f"❌ 未找到有效的課程詳細 API 端點")
            print(f"💡 建議使用 Selenium 從頁面提取通過條件")

        print("=" * 60)
        print()

    def _build_report(self, total_tests, successful_tests):
        """生成 Markdown 報告"""
        report = f"""# 課程詳細 API 探索報告

**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 執行摘要

| 項目 | 結果 |
|------|------|
| **測試端點數量** | {total_tests} |
| **成功端點數量** | {successful_tests} |
| **成功率** | {(successful_tests / total_tests * 100):.1f}% |

---

## 測試結果

"""
        for idx, result in enumerate(self.test_results, 1):
            report += f"\n### {idx}. {result['endpoint']}\n\n"

            if result['success']:
                report += f"- **狀態**: ✅ 成功\n"
                report += f"- **狀態碼**: {result['status_code']}\n"
                report += f"- **回應大小**: {result['response_size']} bytes\n"

                if result.get('has_json'):
                    report += f"- **格式**: JSON\n"
                    if result.get('fields'):
                        report += f"- **欄位數量**: {len(result['fields'])}\n"
                        report += f"- **欄位**: {', '.join(result['fields'][:15])}\n"
                        if len(result['fields']) > 15:
                            report += f"  ... 及其他 {len(result['fields']) - 15} 個欄位\n"

                if result.get('relevant_fields'):
                    report += f"\n⭐ **找到相關欄位**: {', '.join(result['relevant_fields'])}\n"

            elif result.get('error'):
                report += f"- **狀態**: ❌ 失敗\n"
                report += f"- **錯誤**: {result['error']}\n"
            else:
                report += f"- **狀態**: ❌ 失敗\n"
                report += f"- **狀態碼**: {result['status_code']}\n"

        # 結論
        report += "\n---\n\n## 結論\n\n"

        if successful_tests > 0:
            relevant_results = [r for r in self.test_results if r.get('relevant_fields')]

            if relevant_results:
                report += f"### ✅ 找到可用的 API 端點\n\n"
                report += f"以下端點包含通過條件相關欄位：\n\n"
                for r in relevant_results:
                    report += f"- `{r['endpoint']}`: {r.get('relevant_fields')}\n"
                report += f"\n**建議**: 使用這些 API 端點獲取通過條件。\n"
            else:
                report += f"### ⚠️ 找到 {successful_tests} 個有效端點，但都不包含通過條件\n\n"
                report += f"雖然找到有效的 API 端點，但它們都不包含以下相關欄位：\n"
                report += f"- `required_duration` / `duration_requirement` / `required_time`\n"
                report += f"- `required_score` / `score_requirement` / `pass_score`\n"
                report += f"- `requirements` / `pass_requirements` / `completion_requirements`\n\n"
                report += f"**建議**: 改用 Selenium 從頁面提取通過條件（XPath）。\n"
        else:
            report += f"### ❌ 未找到有效的課程詳細 API 端點\n\n"
            report += f"所有測試的端點都無法訪問或返回錯誤。\n\n"
            report += f"**建議**: 使用 Selenium 從頁面提取通過條件（XPath）。\n"

        report += "\n---\n\n**報告結束**\n"
        return report

    def run(self):
        """執行完整探索流程"""
        print("""
============================================================
  課程詳細 API 探索實驗
============================================================
  目的: 探索是否有 API 端點可以獲取課程通過條件
  測試: 7 種可能的 API 端點
============================================================
""")

        input("按 Enter 鍵開始探索...")
        print()

        self.step1_load_config_and_cookies()
        course_ids = self.step2_get_sample_course_ids()
        self.step3_explore_api_endpoints(course_ids)
        self.step4_generate_report()

        print("""
============================================================
  探索完成！
============================================================
  報告: scripts/course_requirements_experiment/results/api_exploration_report.md
============================================================
""")


if __name__ == '__main__':
    explorer = CourseDetailsAPIExplorer()
    explorer.run()
