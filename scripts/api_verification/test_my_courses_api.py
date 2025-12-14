#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 結構驗證腳本 - GET /api/my-courses

目的:
1. 使用專案現有登入模組（完全一致的安全性）
2. 自動載入 stealth.min.js 反偵測腳本
3. 獲取 Session Cookie
4. 調用 API 並分析結構

安全保證:
- ✅ 使用 SteathExtractor 載入 stealth.min.js
- ✅ 使用 ConfigLoader 讀取 eebot.cfg
- ✅ 使用 DriverManager 管理 WebDriver
- ✅ 使用 LoginPage 執行登入流程
- ✅ 使用 CookieManager 管理 Cookie

創建日期: 2025-12-05
作者: wizard03 (with Claude Code CLI)
"""

import os
import sys
import json
import time
import requests
from pathlib import Path
from datetime import datetime

# 添加專案根目錄到 Python 路徑
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 導入專案現有模組（完全使用專案核心功能）
from src.core.config_loader import ConfigLoader
from src.core.driver_manager import DriverManager
from src.core.cookie_manager import CookieManager
from src.pages.login_page import LoginPage
from src.utils.stealth_extractor import StealthExtractor

# 結果輸出目錄
RESULTS_DIR = Path(__file__).parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)


class ApiStructureValidator:
    """API 結構驗證器"""

    def __init__(self):
        """初始化驗證器"""
        self.config = None
        self.driver_manager = None
        self.driver = None
        self.target_url = None
        self.session_cookie = None
        self.api_response = None

    def step1_extract_stealth(self):
        """
        Step 1: 提取 stealth.min.js（與 main.py 完全一致）

        使用專案的 StealthExtractor 模組
        """
        print("=" * 60)
        print("[Step 1/6] 提取 stealth.min.js 反偵測腳本...")
        print("=" * 60)

        # 使用與 main.py 相同的方式
        extractor = StealthExtractor()

        if extractor.exists():
            print(f"[INFO] stealth.min.js 已存在: {extractor.output_path}")
            print("[INFO] 跳過提取步驟")
        else:
            print("[INFO] stealth.min.js 不存在，開始提取...")
            try:
                success = extractor.run()
                if success:
                    print(f"[SUCCESS] stealth.min.js 提取成功: {extractor.output_path}")
                else:
                    print("[WARNING] stealth.min.js 提取失敗，但繼續執行")
                    print("[WARNING] 可能影響反偵測效果")
            except Exception as e:
                print(f"[ERROR] stealth.min.js 提取異常: {e}")
                print("[WARNING] 繼續執行，但可能影響反偵測效果")

        print()

    def step2_load_config(self):
        """
        Step 2: 載入配置（與 main.py 完全一致）

        使用專案的 ConfigLoader 模組
        """
        print("=" * 60)
        print("[Step 2/6] 載入專案配置 (eebot.cfg)...")
        print("=" * 60)

        config_path = PROJECT_ROOT / 'config' / 'eebot.cfg'

        if not config_path.exists():
            print(f"[ERROR] 配置檔案不存在: {config_path}")
            print("[HINT] 請確認 config/eebot.cfg 存在且配置正確")
            sys.exit(1)

        try:
            # 使用與 main.py 完全一致的方式
            self.config = ConfigLoader(str(config_path))
            self.config.load()  # 必須先 load()

            # 使用 get() 方法取得配置
            self.target_url = self.config.get('target_http')

            if not self.target_url:
                print("[ERROR] 配置中未找到 target_http")
                sys.exit(1)

            print(f"[SUCCESS] 配置載入成功")
            print(f"[INFO] 目標網站: {self.target_url}")
        except Exception as e:
            print(f"[ERROR] 配置載入失敗: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

        print()

    def step3_login_with_selenium(self):
        """
        Step 3: 使用 Selenium 登入（與 CourseLearningScenario 完全一致）

        使用專案的 DriverManager、CookieManager 和 LoginPage 模組
        支援自動 Cookie 登入與手動驗證碼登入
        """
        print("=" * 60)
        print("[Step 3/6] 使用 Selenium 登入...")
        print("=" * 60)

        print("[INFO] 正在啟動瀏覽器...")
        print("[INFO] 使用專案的 DriverManager（與 main.py 一致）")

        try:
            # 1. 初始化 CookieManager（使用默認路徑，不需要 driver）
            cookie_manager = CookieManager()
            print(f"[INFO] CookieManager 初始化完成: {cookie_manager.cookie_path}")

            # 2. 創建 WebDriver（無 Proxy 模式）
            self.driver_manager = DriverManager(self.config)
            self.driver = self.driver_manager.create_driver(use_proxy=False)
            print("[SUCCESS] 瀏覽器啟動成功（直連模式，無 Proxy）")

            # 3. 初始化 LoginPage（傳入 cookie_manager）
            login_page = LoginPage(self.driver, cookie_manager)
            print("[INFO] LoginPage 初始化完成")

            # 4. 使用 auto_login 自動處理登入流程
            # 此方法會自動：
            #   - 前往登入頁面
            #   - 嘗試使用 Cookie 登入
            #   - Cookie 失敗則提示手動輸入驗證碼
            #   - 登入成功後自動儲存 Cookie
            print("\n[INFO] 開始登入流程...")
            print("[INFO] 將自動嘗試 Cookie 登入，失敗則需手動輸入驗證碼")
            print()

            login_success = login_page.auto_login(
                username=self.config.get('user_name'),
                password=self.config.get('password'),
                url=self.config.get('target_http')
            )

            if not login_success:
                print("\n[ERROR] 登入失敗")
                self.driver_manager.quit()
                sys.exit(1)

            print("\n[SUCCESS] 登入成功！")

        except Exception as e:
            print(f"[ERROR] 登入失敗: {e}")
            if self.driver_manager:
                self.driver_manager.quit()
            sys.exit(1)

        print()

    def step4_extract_session_cookie(self):
        """
        Step 4: 提取 Session Cookie
        """
        print("=" * 60)
        print("[Step 4/6] 提取 Session Cookie...")
        print("=" * 60)

        try:
            cookies = self.driver.get_cookies()
            print(f"[INFO] 總共有 {len(cookies)} 個 Cookie")

            # 顯示所有 Cookie 名稱（用於調試）
            print("[DEBUG] Cookie 列表:")
            for cookie in cookies:
                print(f"  - {cookie['name']}")

            # 根據 Burp Suite 分析，Session Cookie 格式為 V2-*
            for cookie in cookies:
                if cookie['name'].startswith('V2-'):
                    self.session_cookie = {cookie['name']: cookie['value']}
                    print(f"[SUCCESS] 找到 Session Cookie: {cookie['name']}")
                    print(f"[INFO] Cookie 值: {cookie['value'][:20]}...")
                    break

            if not self.session_cookie:
                print("[WARNING] 未找到 V2-* 格式的 Session Cookie")
                print("[INFO] 嘗試使用所有 Cookie")
                self.session_cookie = {c['name']: c['value'] for c in cookies}

        except Exception as e:
            print(f"[ERROR] 提取 Cookie 失敗: {e}")
            sys.exit(1)

        print()

    def step5_call_api(self):
        """
        Step 5: 調用 GET /api/my-courses API
        """
        print("=" * 60)
        print("[Step 5/6] 調用 GET /api/my-courses API...")
        print("=" * 60)

        # 修正 API URL：移除 /login 路徑，只保留基礎 URL
        from urllib.parse import urlparse
        parsed = urlparse(self.target_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        api_url = f"{base_url}/api/my-courses"

        print(f"[INFO] 基礎 URL: {base_url}")
        print(f"[INFO] API URL: {api_url}")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': base_url,
            'Origin': base_url,
        }

        try:
            print("[INFO] 發送 API 請求...")
            # 添加 verify=False 跳過 SSL 證書驗證（測試環境）
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            response = requests.get(
                api_url,
                cookies=self.session_cookie,
                headers=headers,
                timeout=30,
                verify=False  # 跳過 SSL 證書驗證
            )

            print(f"[INFO] 狀態碼: {response.status_code}")

            if response.status_code == 200:
                print("[SUCCESS] API 調用成功！")
                self.api_response = response.json()
                print(f"[INFO] 回應大小: {len(response.text)} bytes")
            elif response.status_code == 401:
                print("[ERROR] 未授權（401）- Session Cookie 可能已過期")
                sys.exit(1)
            elif response.status_code == 403:
                print("[ERROR] 禁止訪問（403）- 可能被伺服器阻擋")
                sys.exit(1)
            else:
                print(f"[ERROR] API 調用失敗: {response.status_code}")
                print(f"[ERROR] 回應內容: {response.text[:500]}")
                sys.exit(1)

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] API 請求異常: {e}")
            sys.exit(1)

        print()

    def step6_analyze_and_save(self):
        """
        Step 6: 分析並儲存結果
        """
        print("=" * 60)
        print("[Step 6/6] 分析 API 結構並儲存結果...")
        print("=" * 60)

        # 儲存原始回應
        response_file = RESULTS_DIR / 'api_response.json'
        with open(response_file, 'w', encoding='utf-8') as f:
            json.dump(self.api_response, f, ensure_ascii=False, indent=2)
        print(f"[SUCCESS] 原始回應已儲存: {response_file}")

        # 分析結構
        print("\n[INFO] 分析 API 結構...")
        analysis = self._analyze_structure()

        # 儲存分析報告
        report_file = RESULTS_DIR / 'api_structure_analysis.md'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(analysis)
        print(f"[SUCCESS] 結構分析報告已儲存: {report_file}")

        print()

    def _analyze_structure(self):
        """
        分析 API 回應結構

        Returns:
            str: Markdown 格式的分析報告
        """
        report = ["# API 結構分析報告\n"]
        report.append(f"**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append(f"**API 端點**: GET /api/my-courses\n")
        report.append("---\n\n")

        # 頂層鍵值
        report.append("## 頂層結構\n\n")
        top_keys = list(self.api_response.keys())
        report.append(f"頂層鍵值: `{', '.join(top_keys)}`\n\n")

        # 檢查是否有課程列表
        courses_found = False

        if 'courses' in self.api_response:
            courses_found = True
            courses = self.api_response['courses']
            report.append(f"## 課程列表 (courses)\n\n")
            report.append(f"**課程數量**: {len(courses)}\n\n")

            if len(courses) > 0:
                report.append("### 第一個課程範例\n\n")
                report.append("```json\n")
                report.append(json.dumps(courses[0], ensure_ascii=False, indent=2))
                report.append("\n```\n\n")

                report.append("### 課程物件欄位清單\n\n")
                report.append("| 欄位名稱 | 類型 | 範例值 |\n")
                report.append("|---------|------|--------|\n")
                for key, value in courses[0].items():
                    value_type = type(value).__name__
                    sample = str(value)[:50] if value else 'null'
                    report.append(f"| `{key}` | {value_type} | {sample} |\n")
                report.append("\n")

        # 檢查是否有階層結構（programs）
        if 'programs' in self.api_response:
            programs = self.api_response['programs']
            report.append(f"## 主課程列表 (programs)\n\n")
            report.append(f"**主課程數量**: {len(programs)}\n\n")
            report.append("**發現階層結構！**\n\n")

            if len(programs) > 0:
                report.append("### 第一個主課程範例\n\n")
                report.append("```json\n")
                report.append(json.dumps(programs[0], ensure_ascii=False, indent=2))
                report.append("\n```\n\n")

        # 判斷情境
        report.append("## 結構分析結論\n\n")

        if 'programs' in self.api_response:
            report.append("**情境判斷**: 情境 A - 有明確的階層結構\n\n")
            report.append("- ✅ API 包含 `programs` 和 `lessons` 階層\n")
            report.append("- ✅ 可直接對應 Web Scan 的主課程/子課程\n")
            report.append("- ✅ 建議採用**直接對應策略**\n\n")
        elif courses_found and any('master_course_id' in c for c in self.api_response.get('courses', [])):
            report.append("**情境判斷**: 情境 B - 扁平結構 + master_course_id\n\n")
            report.append("- ⚠️ API 僅有 `courses` 扁平列表\n")
            report.append("- ✅ 包含 `master_course_id` 欄位\n")
            report.append("- ✅ 可透過 `master_course_id` 重建階層\n")
            report.append("- ✅ 建議採用**推斷階層策略**\n\n")
        elif courses_found:
            report.append("**情境判斷**: 情境 C - 扁平結構，無階層資訊\n\n")
            report.append("- ⚠️ API 僅有 `courses` 扁平列表\n")
            report.append("- ❌ 無 `master_course_id` 或階層資訊\n")
            report.append("- ⚠️ 只能部分整合\n")
            report.append("- ⚠️ 建議採用**部分整合策略**\n\n")
        else:
            report.append("**情境判斷**: 未知結構\n\n")
            report.append("- ❌ 未找到課程列表\n")
            report.append("- ❌ API 結構不符合預期\n")
            report.append("- ⚠️ 需要進一步分析\n\n")

        return ''.join(report)

    def cleanup(self):
        """清理資源"""
        print("=" * 60)
        print("[Cleanup] 清理資源...")
        print("=" * 60)

        if self.driver_manager:
            self.driver_manager.quit()
            print("[INFO] 瀏覽器已關閉")

        print()

    def run(self):
        """執行完整流程"""
        try:
            self.step1_extract_stealth()
            self.step2_load_config()
            self.step3_login_with_selenium()
            self.step4_extract_session_cookie()
            self.step5_call_api()
            self.step6_analyze_and_save()

            print("=" * 60)
            print("✅ API 結構驗證完成！")
            print("=" * 60)
            print(f"\n📁 結果檔案:")
            print(f"   - {RESULTS_DIR / 'api_response.json'}")
            print(f"   - {RESULTS_DIR / 'api_structure_analysis.md'}")
            print(f"\n📖 下一步:")
            print(f"   1. 查看 api_structure_analysis.md 了解 API 結構")
            print(f"   2. 執行反偵測風險評估: python scripts/api_verification/test_api_security.py")
            print()

        except KeyboardInterrupt:
            print("\n\n[INFO] 使用者中斷執行")
        except Exception as e:
            print(f"\n[ERROR] 執行失敗: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  API 結構驗證 - GET /api/my-courses")
    print("=" * 60)
    print("⚠️  重要提醒:")
    print("  - 本腳本完全使用專案現有模組")
    print("  - 會自動載入 stealth.min.js")
    print("  - 需要手動輸入驗證碼")
    print("  - 請確保 eebot.cfg 配置正確")
    print("=" * 60)
    print()

    input("按 Enter 鍵開始執行...")

    validator = ApiStructureValidator()
    validator.run()
