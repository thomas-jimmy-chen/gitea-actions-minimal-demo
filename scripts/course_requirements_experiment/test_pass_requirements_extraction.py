#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
通過條件提取測試
測試從頁面提取課程通過條件（觀看時長、測驗成績）的可靠性

創建日期: 2025-12-05
用途: 驗證 XPath 提取通過條件
"""

import sys
import re
import json
import time
from pathlib import Path
from datetime import datetime
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from src.core.config_loader import ConfigLoader
from src.core.driver_manager import DriverManager
from src.core.cookie_manager import CookieManager
from src.pages.login_page import LoginPage
from src.pages.course_list_page import CourseListPage


class PassRequirementsExtractor:
    """通過條件提取測試器"""

    def __init__(self):
        self.config = None
        self.driver_manager = None
        self.driver = None
        self.course_list_page = None
        self.extraction_results = []

    def step1_setup(self):
        """Step 1: 初始化配置"""
        print("=" * 60)
        print("[Step 1/4] 初始化配置...")
        print("=" * 60)

        config_path = PROJECT_ROOT / 'config' / 'eebot.cfg'
        self.config = ConfigLoader(str(config_path))
        self.config.load()

        print("[SUCCESS] 配置載入成功")
        print()

    def step2_login(self):
        """Step 2: 登入並前往課程列表頁"""
        print("=" * 60)
        print("[Step 2/4] 登入並前往課程列表頁...")
        print("=" * 60)

        # 初始化 DriverManager
        self.driver_manager = DriverManager(self.config)
        self.driver = self.driver_manager.create_driver(use_proxy=False)
        print("[SUCCESS] 瀏覽器啟動成功")

        # 初始化 CookieManager、LoginPage 和 CourseListPage
        cookie_manager = CookieManager()
        login_page = LoginPage(self.driver, cookie_manager)
        self.course_list_page = CourseListPage(self.driver)

        # 登入
        print("[INFO] 開始登入...")
        login_success = login_page.auto_login(
            username=self.config.get('user_name'),
            password=self.config.get('password'),
            url=self.config.get('target_http')
        )

        if not login_success:
            print("[ERROR] 登入失敗")
            self.driver_manager.quit()
            sys.exit(1)

        print("[SUCCESS] 登入成功")

        # 前往課程列表頁
        print("[INFO] 前往課程列表頁...")
        self.course_list_page.goto_my_courses()
        time.sleep(3)  # 等待頁面完全載入

        # 滾動頁面確保所有課程都載入
        print("[INFO] 滾動頁面載入所有課程...")
        for _ in range(3):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)

        print("[SUCCESS] 已進入課程列表頁")
        print()

    def step3_extract_requirements(self):
        """Step 3: 提取所有課程的通過條件"""
        print("=" * 60)
        print("[Step 3/4] 提取通過條件...")
        print("=" * 60)

        # 先從 API 獲取課程計畫列表
        import requests
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # 從瀏覽器獲取 Cookie
        cookies_list = self.driver.get_cookies()
        cookies_dict = {c['name']: c['value'] for c in cookies_list}

        # 調用 API 獲取課程計畫列表
        base_url = self.config.get('target_http').replace('/login', '')
        api_url = f"{base_url}/api/my-courses"

        response = requests.get(
            api_url,
            cookies=cookies_dict,
            verify=False,
            timeout=30
        )

        if response.status_code != 200:
            print(f"[ERROR] 無法獲取課程列表: {response.status_code}")
            return

        programs = response.json().get('courses', [])
        print(f"[INFO] 找到 {len(programs)} 個課程計畫")
        print()

        # 逐個進入課程計畫並提取通過條件
        success_count = 0
        fail_count = 0
        empty_count = 0
        total_modules = 0

        for idx, program in enumerate(programs, 1):
            program_id = program['id']
            program_name = program['name']

            print(f"[{idx}/{len(programs)}] 課程計畫 {program_id}: {program_name[:50]}...")

            # 更準確的定位方式 - 使用精確的 XPath
            # 先嘗試找到對應的課程卡片
            try:
                # 使用精確的 LINK_TEXT
                xpath = f'//a[text()="{program_name}"]'
                program_links = self.driver.find_elements(By.XPATH, xpath)

                if len(program_links) > 1:
                    print(f"  ⚠️  找到 {len(program_links)} 個匹配的連結，使用第一個")

                if not program_links:
                    print(f"  ❌ 找不到課程連結")
                    fail_count += 1
                    continue

                program_link = program_links[0]

                # 滾動到元素位置
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", program_link)
                time.sleep(0.5)

                # 嘗試點擊
                try:
                    program_link.click()
                except Exception:
                    # 如果普通點擊失敗，使用 JS 點擊
                    print(f"  ⚠️  普通點擊失敗，改用 JS 點擊")
                    self.driver.execute_script("arguments[0].click();", program_link)

                time.sleep(3)
                print(f"  ✅ 已進入課程計畫: {program_name[:50]}")

            except Exception as click_error:
                print(f"  ❌ 點擊失敗: {str(click_error)[:80]}")
                fail_count += 1
                continue

            # 找到所有 module 元素
            try:
                module_elements = self.driver.find_elements(By.XPATH, '//*[starts-with(@id, "module-")]')
                print(f"  找到 {len(module_elements)} 個課程單元")
                total_modules += len(module_elements)

                # 提取每個 module 的通過條件
                for module_elem in module_elements:
                    try:
                        module_id = module_elem.get_attribute('id').replace('module-', '')

                        # 查找通過條件元素
                        xpath = f'//*[@id="module-{module_id}"]/div[1]/div[1]/span'
                        req_element = self.driver.find_element(By.XPATH, xpath)
                        text = req_element.text.strip()

                        if not text:
                            empty_count += 1
                            result = {
                                'program_id': program_id,
                                'program_name': program_name,
                                'module_id': module_id,
                                'success': True,
                                'text': None,
                                'duration_minutes': None,
                                'exam_score': None
                            }
                        else:
                            # 解析文字
                            duration_minutes = None
                            exam_score = None

                            # 提取觀看時長
                            duration_match = re.search(r'觀看時長(\d+)分鐘', text)
                            if duration_match:
                                duration_minutes = int(duration_match.group(1))

                            # 提取測驗成績
                            score_match = re.search(r'測驗成績達(\d+)分', text)
                            if score_match:
                                exam_score = int(score_match.group(1))

                            print(f"    ✅ Module {module_id}: \"{text}\"")

                            success_count += 1

                            result = {
                                'program_id': program_id,
                                'program_name': program_name,
                                'module_id': module_id,
                                'success': True,
                                'text': text,
                                'duration_minutes': duration_minutes,
                                'exam_score': exam_score
                            }

                        self.extraction_results.append(result)

                    except NoSuchElementException:
                        fail_count += 1
                        self.extraction_results.append({
                            'program_id': program_id,
                            'program_name': program_name,
                            'module_id': module_id,
                            'success': False,
                            'error': 'Requirement element not found'
                        })
                    except Exception as e:
                        fail_count += 1
                        self.extraction_results.append({
                            'program_id': program_id,
                            'program_name': program_name,
                            'module_id': module_id,
                            'success': False,
                            'error': str(e)[:100]
                        })

                # 返回課程列表頁
                self.driver.back()
                time.sleep(2)

            except Exception as e:
                print(f"  ❌ 提取過程異常: {str(e)[:80]}")
                # 嘗試返回課程列表頁
                try:
                    self.driver.back()
                    time.sleep(2)
                except Exception:
                    pass

        print()
        print("=" * 60)
        print(f"  提取統計")
        print("=" * 60)
        print(f"課程計畫數: {len(programs)}")
        print(f"課程單元數: {total_modules}")
        print(f"成功提取: {success_count}")
        print(f"文字為空: {empty_count}")
        print(f"提取失敗: {fail_count}")
        if total_modules > 0:
            print(f"成功率: {(success_count / total_modules * 100):.1f}%")
        print("=" * 60)
        print()

    def step4_generate_report(self):
        """Step 4: 生成報告並關閉瀏覽器"""
        print("=" * 60)
        print("[Step 4/4] 生成報告...")
        print("=" * 60)

        # 關閉瀏覽器
        if self.driver_manager:
            self.driver_manager.quit()
            print("[INFO] 瀏覽器已關閉")

        # 分析結果
        successful_results = [r for r in self.extraction_results if r.get('success')]
        failed_results = [r for r in self.extraction_results if not r.get('success')]

        # 統計文字格式
        text_patterns = []
        duration_values = []
        score_values = []

        for r in successful_results:
            if r.get('text'):
                text_patterns.append(r['text'])
            if r.get('duration_minutes'):
                duration_values.append(r['duration_minutes'])
            if r.get('exam_score'):
                score_values.append(r['exam_score'])

        # 生成報告
        report = self._build_report(text_patterns, duration_values, score_values)

        # 儲存報告
        output_dir = PROJECT_ROOT / 'scripts' / 'course_requirements_experiment' / 'results'
        output_dir.mkdir(parents=True, exist_ok=True)

        report_file = output_dir / 'extraction_test_report.md'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        # 儲存原始資料
        json_file = output_dir / 'extraction_raw_data.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.extraction_results, f, indent=2, ensure_ascii=False)

        print(f"[SUCCESS] 報告已儲存:")
        print(f"  - {report_file}")
        print(f"  - {json_file}")
        print()

    def _build_report(self, text_patterns, duration_values, score_values):
        """生成 Markdown 報告"""
        total = len(self.extraction_results)
        successful = len([r for r in self.extraction_results if r.get('success')])
        has_text = len([r for r in self.extraction_results if r.get('text')])
        success_rate = (successful / total * 100) if total > 0 else 0

        report = f"""# 通過條件提取測試報告

**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**XPath**: `//*[@id="module-{{course_id}}"]/div[1]/div[1]/span`

---

## 執行摘要

| 項目 | 結果 |
|------|------|
| **測試課程數** | {total} |
| **成功提取數** | {successful} |
| **包含文字** | {has_text} |
| **成功率** | {success_rate:.1f}% |

---

## 文字格式分析

### 獨特文字格式 ({len(set(text_patterns))} 種)

"""
        # 統計文字格式
        pattern_counter = Counter(text_patterns)
        for pattern, count in pattern_counter.most_common(10):
            report += f"- `{pattern}` - 出現 {count} 次\n"

        if len(pattern_counter) > 10:
            report += f"\n... 及其他 {len(pattern_counter) - 10} 種格式\n"

        report += f"\n---\n\n## 數值統計\n\n"

        # 觀看時長統計
        if duration_values:
            report += f"### 觀看時長要求\n\n"
            report += f"- **樣本數**: {len(duration_values)}\n"
            report += f"- **最小值**: {min(duration_values)} 分鐘\n"
            report += f"- **最大值**: {max(duration_values)} 分鐘\n"
            report += f"- **平均值**: {sum(duration_values) / len(duration_values):.1f} 分鐘\n\n"

            duration_counter = Counter(duration_values)
            report += f"**分佈**:\n"
            for duration, count in duration_counter.most_common(5):
                report += f"- {duration} 分鐘: {count} 個課程\n"
        else:
            report += f"### 觀看時長要求\n\n無資料\n\n"

        # 測驗成績統計
        if score_values:
            report += f"\n### 測驗成績要求\n\n"
            report += f"- **樣本數**: {len(score_values)}\n"
            report += f"- **最小值**: {min(score_values)} 分\n"
            report += f"- **最大值**: {max(score_values)} 分\n"
            report += f"- **平均值**: {sum(score_values) / len(score_values):.1f} 分\n\n"

            score_counter = Counter(score_values)
            report += f"**分佈**:\n"
            for score, count in score_counter.most_common(5):
                report += f"- {score} 分: {count} 個課程\n"
        else:
            report += f"\n### 測驗成績要求\n\n無資料\n\n"

        report += f"\n---\n\n## 提取失敗案例\n\n"

        failed_results = [r for r in self.extraction_results if not r.get('success')]
        if failed_results:
            report += f"共 {len(failed_results)} 個失敗案例：\n\n"
            for r in failed_results[:10]:
                report += f"- 課程計畫 {r['program_id']} / Module {r.get('module_id', 'N/A')}: {r['program_name'][:50]}\n"
                report += f"  - 錯誤: {r.get('error', 'Unknown')}\n"

            if len(failed_results) > 10:
                report += f"\n... 及其他 {len(failed_results) - 10} 個失敗案例\n"
        else:
            report += f"無失敗案例 ✅\n"

        report += f"\n---\n\n## 結論\n\n"

        if success_rate >= 80:
            report += f"### ✅ XPath 提取方式可靠\n\n"
            report += f"成功率達 {success_rate:.1f}%，可以安全使用 XPath 提取通過條件。\n\n"
            report += f"**建議**:\n"
            report += f"- 採用方案 A（混合掃描）\n"
            report += f"- 使用 Selenium 批次提取通過條件\n"
            report += f"- 加入錯誤處理機制處理少數失敗案例\n"
        elif success_rate >= 50:
            report += f"### ⚠️ XPath 提取方式部分可靠\n\n"
            report += f"成功率 {success_rate:.1f}%，有一定比例的失敗案例。\n\n"
            report += f"**建議**:\n"
            report += f"- 謹慎使用 XPath 提取\n"
            report += f"- 需要充分的錯誤處理\n"
            report += f"- 考慮提供手動輸入選項\n"
        else:
            report += f"### ❌ XPath 提取方式不可靠\n\n"
            report += f"成功率僅 {success_rate:.1f}%，不建議使用。\n\n"
            report += f"**建議**:\n"
            report += f"- 探索其他方式獲取通過條件\n"
            report += f"- 或使用固定值/配置\n"

        report += "\n---\n\n**報告結束**\n"
        return report

    def run(self):
        """執行完整測試流程"""
        print("""
============================================================
  通過條件提取測試
============================================================
  目的: 驗證 XPath 提取通過條件的可靠性
  方法: 登入 → 前往課程列表 → 批次提取 → 分析
============================================================
""")

        input("按 Enter 鍵開始測試...")
        print()

        try:
            self.step1_setup()
            self.step2_login()
            self.step3_extract_requirements()
            self.step4_generate_report()

            print("""
============================================================
  測試完成！
============================================================
  報告: scripts/course_requirements_experiment/results/extraction_test_report.md
============================================================
""")

        except KeyboardInterrupt:
            print("\n[INFO] 使用者中斷")
            if self.driver_manager:
                self.driver_manager.quit()
        except Exception as e:
            print(f"\n[ERROR] 測試異常: {e}")
            import traceback
            traceback.print_exc()
            if self.driver_manager:
                self.driver_manager.quit()


if __name__ == '__main__':
    extractor = PassRequirementsExtractor()
    extractor.run()
