#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
API 安全性測試 - 反偵測風險評估
測試 API 直接調用是否會被伺服器偵測/阻擋

創建日期: 2025-12-05
用途: 評估是否可安全使用 API 直接調用模式
"""

import sys
import os
import json
import time
import random
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

# 添加專案根目錄到 Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import requests
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from src.core.config_loader import ConfigLoader


class APISecurityTester:
    """API 安全性測試器 - 評估反偵測風險"""

    def __init__(self):
        """初始化測試器"""
        self.config = None
        self.base_url = None
        self.api_url = None
        self.cookies = None
        self.test_results = []

    def step1_load_config(self):
        """Step 1: 載入配置"""
        print("=" * 60)
        print("[Step 1/6] 載入配置...")
        print("=" * 60)

        config_path = PROJECT_ROOT / 'config' / 'eebot.cfg'
        if not config_path.exists():
            print(f"[ERROR] 配置檔案不存在: {config_path}")
            sys.exit(1)

        try:
            self.config = ConfigLoader(str(config_path))
            self.config.load()

            target_url = self.config.get('target_http')
            parsed = urlparse(target_url)
            self.base_url = f"{parsed.scheme}://{parsed.netloc}"
            self.api_url = f"{self.base_url}/api/my-courses"

            print(f"[SUCCESS] 配置載入成功")
            print(f"[INFO] 基礎 URL: {self.base_url}")
            print(f"[INFO] API URL: {self.api_url}")

        except Exception as e:
            print(f"[ERROR] 配置載入失敗: {e}")
            sys.exit(1)

        print()

    def step2_load_cookies(self):
        """Step 2: 載入 Session Cookie"""
        print("=" * 60)
        print("[Step 2/6] 載入 Session Cookie...")
        print("=" * 60)

        cookie_file = PROJECT_ROOT / 'resource' / 'cookies' / 'cookies.json'

        if not cookie_file.exists():
            print(f"[ERROR] Cookie 檔案不存在: {cookie_file}")
            print("[HINT] 請先執行 test_my_courses_api.py 登入並獲取 Cookie")
            sys.exit(1)

        try:
            with open(cookie_file, 'r', encoding='utf-8-sig') as f:
                cookie_list = json.load(f)

            # 轉換為 requests 格式的 dict
            self.cookies = {c['name']: c['value'] for c in cookie_list}

            print(f"[SUCCESS] 載入 {len(self.cookies)} 個 Cookie")
            print("[DEBUG] Cookie 列表:")
            for name in self.cookies.keys():
                print(f"  - {name}")

        except Exception as e:
            print(f"[ERROR] Cookie 載入失敗: {e}")
            sys.exit(1)

        print()

    def _call_api(self, scenario_name: str, cookies: dict, headers: dict,
                  delay: float = 0) -> dict:
        """
        調用 API 並記錄結果

        Args:
            scenario_name: 測試場景名稱
            cookies: Cookie 字典
            headers: 請求頭字典
            delay: 請求前延遲（秒）

        Returns:
            dict: 測試結果
        """
        if delay > 0:
            time.sleep(delay)

        result = {
            'scenario': scenario_name,
            'success': False,
            'status_code': None,
            'response_time': 0,
            'error': None,
            'blocked': False
        }

        try:
            start_time = time.time()
            response = requests.get(
                self.api_url,
                cookies=cookies,
                headers=headers,
                timeout=30,
                verify=False
            )
            result['response_time'] = time.time() - start_time
            result['status_code'] = response.status_code

            if response.status_code == 200:
                result['success'] = True
                result['data_size'] = len(response.text)
            elif response.status_code in [401, 403]:
                result['blocked'] = True
                result['error'] = f"HTTP {response.status_code}"
            else:
                result['error'] = f"HTTP {response.status_code}"

        except requests.exceptions.SSLError as e:
            result['error'] = f"SSL Error: {str(e)[:100]}"
        except requests.exceptions.Timeout:
            result['error'] = "Timeout"
        except Exception as e:
            result['error'] = str(e)[:100]

        return result

    def step3_scenario1_baseline(self):
        """Scenario 1: 基準測試 - 使用完整 Cookie + Headers"""
        print("=" * 60)
        print("[Step 3/6] Scenario 1: 基準測試")
        print("=" * 60)
        print("[INFO] 使用完整 Cookie 和標準 Headers")
        print("[INFO] 此測試應該成功（驗證環境正常）")
        print()

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': self.base_url,
            'Origin': self.base_url,
        }

        result = self._call_api("Scenario 1: 基準測試", self.cookies, headers)
        self.test_results.append(result)

        self._print_result(result)
        print()

    def step4_scenario2_direct_api(self):
        """Scenario 2: 純 requests 調用 - 模擬 API 直接調用"""
        print("=" * 60)
        print("[Step 4/6] Scenario 2: 純 API 調用（無瀏覽器）")
        print("=" * 60)
        print("[INFO] 使用 Cookie 但簡化 Headers")
        print("[INFO] 模擬非瀏覽器環境的 API 調用")
        print()

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        }

        result = self._call_api("Scenario 2: 純 API 調用", self.cookies, headers)
        self.test_results.append(result)

        self._print_result(result)
        print()

    def step5_scenario3_high_frequency(self):
        """Scenario 3: 高頻請求測試 - 測試頻率限制"""
        print("=" * 60)
        print("[Step 5/6] Scenario 3: 高頻請求測試")
        print("=" * 60)
        print("[INFO] 連續發送 10 次請求，間隔 1 秒")
        print("[INFO] 測試伺服器是否有頻率限制")
        print()

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        }

        success_count = 0
        blocked_count = 0

        for i in range(10):
            print(f"[{i+1}/10] 發送請求...", end=" ")
            result = self._call_api(
                f"Scenario 3: 高頻請求 #{i+1}",
                self.cookies,
                headers,
                delay=1
            )

            if result['success']:
                success_count += 1
                print(f"✓ 成功 ({result['response_time']:.2f}s)")
            elif result['blocked']:
                blocked_count += 1
                print(f"✗ 被阻擋 ({result['error']})")
            else:
                print(f"✗ 失敗 ({result['error']})")

            # 只記錄摘要
            if i == 9:  # 最後一次
                summary_result = {
                    'scenario': 'Scenario 3: 高頻請求測試',
                    'success': success_count == 10,
                    'success_rate': f"{success_count}/10",
                    'blocked_count': blocked_count,
                    'status_code': 200 if success_count > 0 else None
                }
                self.test_results.append(summary_result)

        print()
        print(f"[SUMMARY] 成功: {success_count}/10, 被阻擋: {blocked_count}/10")
        print()

    def step6_scenario4_minimal_headers(self):
        """Scenario 4: 最小化 Headers - 測試必要的 Headers"""
        print("=" * 60)
        print("[Step 6/6] Scenario 4: 最小化 Headers")
        print("=" * 60)
        print("[INFO] 只使用 Cookie，不帶任何 Headers")
        print("[INFO] 測試伺服器是否檢查 Headers")
        print()

        headers = {}  # 完全不帶 Headers

        result = self._call_api("Scenario 4: 最小化 Headers", self.cookies, headers)
        self.test_results.append(result)

        self._print_result(result)
        print()

    def step7_generate_report(self):
        """Step 7: 生成風險評估報告"""
        print("=" * 60)
        print("[Step 7/7] 生成風險評估報告...")
        print("=" * 60)

        # 分析結果
        analysis = self._analyze_results()

        # 生成報告
        report = self._build_report(analysis)

        # 儲存報告
        output_dir = PROJECT_ROOT / 'scripts' / 'api_verification' / 'results'
        output_dir.mkdir(parents=True, exist_ok=True)

        report_file = output_dir / 'security_assessment.md'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"[SUCCESS] 報告已儲存: {report_file}")
        print()

        # 顯示評級
        print("=" * 60)
        print("  風險評估結果")
        print("=" * 60)
        print(f"評級: {analysis['rating']}")
        print(f"建議: {analysis['recommendation']}")
        print("=" * 60)
        print()

    def _print_result(self, result: dict):
        """打印單一測試結果"""
        if result['success']:
            print(f"✓ 成功")
            print(f"  - 狀態碼: {result['status_code']}")
            print(f"  - 回應時間: {result['response_time']:.2f}s")
            if 'data_size' in result:
                print(f"  - 資料大小: {result['data_size']} bytes")
        elif result.get('blocked'):
            print(f"✗ 被阻擋")
            print(f"  - 錯誤: {result['error']}")
        else:
            print(f"✗ 失敗")
            print(f"  - 錯誤: {result['error']}")

    def _analyze_results(self) -> dict:
        """分析測試結果並評級"""
        # 計算成功率
        total_tests = len([r for r in self.test_results if 'success' in r])
        successful_tests = len([r for r in self.test_results if r.get('success')])
        blocked_tests = len([r for r in self.test_results if r.get('blocked')])

        # 評級邏輯
        rating = None
        recommendation = None
        risk_level = None

        # Scenario 1（基準測試）必須成功
        scenario1 = next((r for r in self.test_results if 'Scenario 1' in r['scenario']), None)
        if not scenario1 or not scenario1.get('success'):
            rating = "🔴 紅燈 - 環境異常"
            recommendation = "基準測試失敗，請檢查環境配置"
            risk_level = "HIGH"
        # 如果有任何測試被明確阻擋（401/403）
        elif blocked_tests > 0:
            rating = "🔴 紅燈 - 檢測到反偵測機制"
            recommendation = "伺服器會阻擋非瀏覽器請求，不建議使用 API 直接調用"
            risk_level = "HIGH"
        # 如果成功率 100%
        elif successful_tests == total_tests:
            rating = "🟢 綠燈 - 安全"
            recommendation = "所有測試通過，可安全使用 API 直接調用模式"
            risk_level = "LOW"
        # 如果成功率 >= 75%
        elif successful_tests / total_tests >= 0.75:
            rating = "🟡 黃燈 - 謹慎使用"
            recommendation = "部分測試失敗，建議添加延遲和完整 Headers"
            risk_level = "MEDIUM"
        else:
            rating = "🔴 紅燈 - 高風險"
            recommendation = "多數測試失敗，不建議使用 API 直接調用"
            risk_level = "HIGH"

        return {
            'rating': rating,
            'recommendation': recommendation,
            'risk_level': risk_level,
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'blocked_tests': blocked_tests,
            'success_rate': f"{successful_tests}/{total_tests}"
        }

    def _build_report(self, analysis: dict) -> str:
        """生成 Markdown 報告"""
        report = f"""# API 安全性評估報告
**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**API 端點**: GET /api/my-courses

---

## 執行摘要

| 項目 | 結果 |
|------|------|
| **風險評級** | {analysis['rating']} |
| **風險等級** | {analysis['risk_level']} |
| **測試總數** | {analysis['total_tests']} |
| **成功測試** | {analysis['successful_tests']} |
| **被阻擋測試** | {analysis['blocked_tests']} |
| **成功率** | {analysis['success_rate']} |

---

## 建議

{analysis['recommendation']}

---

## 測試結果明細

"""
        for idx, result in enumerate(self.test_results, 1):
            report += f"\n### {idx}. {result['scenario']}\n\n"

            if result.get('success'):
                report += f"- **結果**: ✅ 成功\n"
                if 'status_code' in result:
                    report += f"- **狀態碼**: {result['status_code']}\n"
                if 'response_time' in result:
                    report += f"- **回應時間**: {result['response_time']:.2f}s\n"
                if 'data_size' in result:
                    report += f"- **資料大小**: {result['data_size']} bytes\n"
            elif result.get('blocked'):
                report += f"- **結果**: ❌ 被阻擋\n"
                report += f"- **錯誤**: {result['error']}\n"
            else:
                report += f"- **結果**: ❌ 失敗\n"
                if 'error' in result:
                    report += f"- **錯誤**: {result['error']}\n"

            if 'success_rate' in result:  # 高頻測試摘要
                report += f"- **成功率**: {result['success_rate']}\n"
                report += f"- **被阻擋次數**: {result['blocked_count']}\n"

            report += "\n"

        # 風險分析
        report += """---

## 風險分析

"""
        if analysis['risk_level'] == 'LOW':
            report += """### 🟢 綠燈 - 低風險

伺服器對 API 調用**沒有明顯的反偵測機制**：

- ✅ 接受簡化的 Headers
- ✅ 無頻率限制
- ✅ 無瀏覽器指紋檢測

**建議行動**:
- 可安全使用 API 直接調用模式
- 建議保留基本的 User-Agent 和 Accept Headers
- 可實作批次處理以提升效率

"""
        elif analysis['risk_level'] == 'MEDIUM':
            report += """### 🟡 黃燈 - 中風險

伺服器對 API 調用**有部分檢測機制**：

- ⚠️ 部分測試失敗
- ⚠️ 可能需要特定 Headers
- ⚠️ 建議謹慎使用

**建議行動**:
- 使用完整的 Headers（模擬真實瀏覽器）
- 添加請求延遲（建議 2-5 秒）
- 實作錯誤重試機制
- 監控 API 回應，如有異常立即停止

**緩解措施**:
```python
headers = {
    'User-Agent': 'Mozilla/5.0...',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-TW,zh;q=0.9',
    'Referer': base_url,
    'Origin': base_url,
}

# 添加隨機延遲
time.sleep(random.uniform(2, 5))
```

"""
        else:  # HIGH
            report += """### 🔴 紅燈 - 高風險

伺服器對 API 調用**有強反偵測機制**：

- ❌ 多數測試失敗或被阻擋
- ❌ 可能有頻率限制
- ❌ 可能檢查瀏覽器指紋

**建議行動**:
- **不建議使用 API 直接調用模式**
- 改用混合模式：Selenium + MitmProxy 被動攔截
- 保持現有的 Web Scan 方式

**替代方案**:
1. **方案 A**: 完全使用 Selenium（現狀）
2. **方案 B**: Selenium + MitmProxy 混合模式
   - 使用 Selenium 模擬真實瀏覽器行為
   - 使用 MitmProxy 被動攔截 API 回應
   - 從攔截的 JSON 中提取額外欄位

"""

        report += """---

## 測試環境

- **Python**: 3.x
- **測試工具**: requests
- **SSL 驗證**: 已禁用（測試環境）
- **Cookie 來源**: Selenium 登入後提取

---

**報告結束**
"""
        return report

    def run(self):
        """執行完整測試流程"""
        print("""
============================================================
  API 安全性測試 - 反偵測風險評估
============================================================
  測試目的: 評估是否可安全使用 API 直接調用模式
  測試場景: 5 種不同的 API 調用方式
  評估標準: 🟢 綠燈 / 🟡 黃燈 / 🔴 紅燈
============================================================
""")

        input("按 Enter 鍵開始測試...")
        print()

        self.step1_load_config()
        self.step2_load_cookies()
        self.step3_scenario1_baseline()
        self.step4_scenario2_direct_api()
        self.step5_scenario3_high_frequency()
        self.step6_scenario4_minimal_headers()
        self.step7_generate_report()

        print("""
============================================================
  測試完成！
============================================================
  請查看: scripts/api_verification/results/security_assessment.md
============================================================
""")


if __name__ == '__main__':
    tester = APISecurityTester()
    tester.run()
