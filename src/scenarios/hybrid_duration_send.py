# -*- coding: utf-8 -*-
"""
混合式時長發送場景

流程：
1. 第一次掃描：記錄所有主課程的當前已閱讀時數
2. 瀏覽器停止在 "我的課程" 頁面
3. 等待用戶加入排程
4. API 發送時長（針對已排程課程）
5. 第二次掃描：重新記錄時數
6. 計算並顯示時長增加差異

Created: 2025-12-16
"""

import time
import json
from typing import Dict, List, Optional
from pathlib import Path

from ..core.config_loader import ConfigLoader
from ..core.driver_manager import DriverManager
from ..pages.login_page import LoginPage
from ..pages.course_list_page import CourseListPage
from ..api.visit_duration_api import VisitDurationAPI


class HybridDurationSendScenario:
    """混合式時長發送場景"""

    def __init__(self, config: ConfigLoader):
        """初始化場景"""
        self.config = config
        # 初始化 DriverManager（禁用 stealth，加快啟動速度）
        self.driver_manager = DriverManager(config, stealth_enabled=False)

        # 時數記錄
        self.course_durations_before = {}  # 第一次掃描結果
        self.course_durations_after = {}   # 第二次掃描結果

        # 用戶資訊
        self.user_info = None
        self.session_cookie = None

    def execute(self):
        """執行混合式時長發送流程"""
        try:
            print('\n' + '='*60)
            print('【混合式時長發送】')
            print('='*60)

            # === 步驟 1: 登入 ===
            print('\n[步驟 1/6] 登入系統...')
            driver = self._login()

            # === 步驟 2: 第一次掃描（記錄當前時數）===
            print('\n[步驟 2/6] 第一次掃描 - 記錄所有課程的當前時數...')
            self.course_durations_before = self._scan_course_durations(driver)
            self._display_scan_results(self.course_durations_before, "第一次掃描結果")

            # === 步驟 3: 提取用戶資訊（準備 API 發送）===
            print('\n[步驟 3/6] 提取用戶資訊（準備 API 發送）...')
            self._extract_user_info(driver)

            # === 步驟 4: 等待用戶加入排程 ===
            print('\n[步驟 4/6] 瀏覽器已停止在 "我的課程" 頁面')
            print('━'*60)
            print('⏸️  請在另一個終端執行：')
            print('   python menu.py')
            print('   選擇課程加入排程，然後選擇 "s. 儲存排程"')
            print('━'*60)
            input('✅ 排程完成後，按 Enter 繼續...')

            # === 步驟 5: 讀取排程並發送時長 ===
            print('\n[步驟 5/6] 讀取排程並發送時長...')
            scheduled_courses = self._load_schedule()
            if not scheduled_courses:
                print('⚠️  排程為空，跳過時長發送')
            else:
                self._send_durations_for_scheduled(scheduled_courses)

            # === 步驟 6: 第二次掃描（驗證時長增加）===
            print('\n[步驟 6/6] 第二次掃描 - 驗證時長是否增加...')
            self.course_durations_after = self._scan_course_durations(driver)
            self._display_scan_results(self.course_durations_after, "第二次掃描結果")

            # === 計算並顯示差異 ===
            self._display_duration_diff()

            print('\n' + '='*60)
            print('✅ 混合式時長發送完成！')
            print('='*60)

        except Exception as e:
            print(f'\n❌ 執行失敗: {e}')
            import traceback
            traceback.print_exc()

        finally:
            # 不關閉瀏覽器，保持在 "我的課程" 頁面
            print('\n💡 提示：瀏覽器保持開啟，可手動檢查結果')
            input('按 Enter 關閉瀏覽器...')
            self.driver_manager.quit()

    def _login(self):
        """登入系統"""
        max_retries = 3

        for attempt in range(1, max_retries + 1):
            try:
                print(f'  嘗試登入 ({attempt}/{max_retries})...')

                # 創建 driver（不使用 proxy，因為我們只需要從頁面讀取時數）
                driver = self.driver_manager.create_driver(use_proxy=False)
                login_page = LoginPage(driver)

                # 使用 auto_login（先嘗試 Cookie，失敗則手動登入）
                username = self.config.get('user_name')
                password = self.config.get('password')
                target_url = self.config.get('target_http')

                success = login_page.auto_login(
                    username=username,
                    password=password,
                    url=target_url
                )

                if success:
                    print('  ✅ 登入成功')
                    time.sleep(3)
                    return driver
                else:
                    print('  ✗ 登入失敗')
                    if attempt < max_retries:
                        print('  ⚠️  準備重試...')
                        driver.quit()
                        time.sleep(3)
                    else:
                        driver.quit()
                        raise Exception('登入失敗，已達最大重試次數')

            except Exception as e:
                if attempt < max_retries:
                    print(f'  ⚠️  發生錯誤: {e}')
                    print('  準備重試...')
                    time.sleep(3)
                else:
                    raise Exception(f'登入失敗: {e}')

    def _scan_course_durations(self, driver) -> Dict[str, Dict]:
        """
        掃描所有課程的已閱讀時數

        返回格式:
        {
            "課程計畫名稱": {
                "program_id": "465",
                "program_name": "課程計畫名稱",
                "duration_minutes": 120,  # 已閱讀分鐘數
                "status": "修習中",
                "modules": [...]
            }
        }
        """
        course_list_page = CourseListPage(driver)

        # 前往 "我的課程" 頁面
        print('  📍 前往我的課程...')
        course_list_page.goto_my_courses()

        # ⭐ 關鍵：等待頁面載入完成（參考 menu.py 第 318 行）
        print('  ⏳ 等待頁面載入（10秒）...')
        time.sleep(10)

        # 掃描所有 "修習中" 的課程計畫
        print('  🔍 正在掃描課程計畫...')
        programs = course_list_page.get_in_progress_programs()

        if not programs:
            print('  ⚠️  未找到任何 "修習中" 的課程計畫')
            return {}

        print(f'  ✅ 找到 {len(programs)} 個課程計畫')

        durations = {}

        for i, program in enumerate(programs, 1):
            program_name = program['name']  # ← 修正：使用 'name' 而不是 'program_name'
            print(f'\n  [{i}/{len(programs)}] 掃描課程計畫: {program_name}')

            try:
                # 進入課程計畫詳情頁（使用 select_course_by_name）
                course_list_page.select_course_by_name(program_name, delay=5.0)

                # 提取已閱讀時數（從頁面提取）
                duration_info = self._extract_duration_from_page(driver, program_name)

                durations[program_name] = {
                    'program_name': program_name,
                    'duration_minutes': duration_info.get('duration_minutes', 0),
                    'status': '修習中',
                    'scan_time': time.strftime('%Y-%m-%d %H:%M:%S')
                }

                print(f'      已閱讀時數: {duration_info.get("duration_minutes", 0)} 分鐘')

                # 返回 "我的課程" 頁面（參考 menu.py 第 1161 行 - 使用 back() 而不是 get()）
                print(f'      返回我的課程...')
                driver.back()
                time.sleep(2)

            except Exception as e:
                print(f'      ⚠️  掃描失敗: {e}')
                # 嘗試返回 "我的課程"（使用 back()）
                try:
                    driver.back()
                    time.sleep(2)
                except:
                    pass
                continue

        return durations

    def _extract_duration_from_page(self, driver, program_name: str) -> Dict:
        """
        從課程計畫詳情頁提取已閱讀時數

        提取策略：
        1. 尋找包含 "累積觀看時長" 的文字
        2. 解析分鐘數
        """
        from selenium.webdriver.common.by import By

        try:
            # 策略 1: 尋找包含 "累積觀看時長" 的元素
            page_text = driver.find_element(By.TAG_NAME, 'body').text

            # 使用正則表達式提取時數
            import re

            # 範例文字: "累積觀看時長 120 分鐘"
            match = re.search(r'累積觀看時長[：:\s]*(\d+)\s*分鐘', page_text)
            if match:
                duration_minutes = int(match.group(1))
                return {'duration_minutes': duration_minutes}

            # 範例文字: "已觀看 120 分鐘"
            match = re.search(r'已觀看[：:\s]*(\d+)\s*分鐘', page_text)
            if match:
                duration_minutes = int(match.group(1))
                return {'duration_minutes': duration_minutes}

            # 如果都沒找到，返回 0
            print(f'      ⚠️  未找到時數資訊，預設為 0 分鐘')
            return {'duration_minutes': 0}

        except Exception as e:
            print(f'      ⚠️  提取時數失敗: {e}')
            return {'duration_minutes': 0}

    def _extract_user_info(self, driver):
        """提取用戶資訊（準備 API 發送）"""
        try:
            # 提取 Session Cookie
            print('  🍪 提取 Session Cookie...')
            cookies = driver.get_cookies()
            self.session_cookie = {}
            for cookie in cookies:
                if cookie['name'] == 'session':
                    self.session_cookie['session'] = cookie['value']
                    break

            if not self.session_cookie:
                print('  ⚠️  未找到 Session Cookie')

            # 提取用戶資訊
            print('  📋 提取用戶資訊...')
            self.user_info = VisitDurationAPI.extract_user_info_from_cookies(driver)

            # 備用方案 1: 從 API 獲取
            if not self.user_info:
                print('  ⚠️  從頁面提取失敗，嘗試從 API 獲取...')
                from urllib.parse import urlparse
                target_url = self.config.get('target_http')
                parsed = urlparse(target_url)
                base_url = f"{parsed.scheme}://{parsed.netloc}"

                self.user_info = VisitDurationAPI.get_user_info_from_api(base_url, self.session_cookie)

            # 備用方案 2: 使用最小化用戶資訊
            if not self.user_info:
                print('  ⚠️  從 API 獲取失敗，使用最小化用戶資訊...')
                user_name = self.config.get('user_name', '')
                if user_name:
                    self.user_info = {
                        'user_id': '0',  # 佔位符
                        'user_no': user_name,
                        'user_name': user_name,
                        'org_id': '1',
                        'org_name': '郵政ｅ大學',
                        'dep_id': '0',
                        'dep_name': '未知部門',
                        'dep_code': '0000000000'
                    }
                    print(f'  ⚠️  使用最小化用戶資訊: {user_name}')
                    print('  ⚠️  某些欄位使用佔位符，可能影響統計數據準確性')

            # 顯示結果
            if self.user_info and self.session_cookie:
                print(f'  ✅ 用戶: {self.user_info.get("user_name")} (編號: {self.user_info.get("user_no")})')
            else:
                print('  ❌ 用戶資訊或 Cookie 提取失敗')

        except Exception as e:
            print(f'  ⚠️  提取失敗: {e}')

    def _load_schedule(self) -> List[Dict]:
        """載入排程檔案"""
        schedule_path = Path('data/schedule.json')

        if not schedule_path.exists():
            print('  ⚠️  排程檔案不存在')
            return []

        try:
            with open(schedule_path, 'r', encoding='utf-8-sig') as f:
                scheduled = json.load(f)

            # 過濾出課程（非考試）
            courses = [item for item in scheduled if item.get('course_type') != 'exam']

            print(f'  ✅ 載入排程: {len(courses)} 個課程')
            return courses

        except Exception as e:
            print(f'  ⚠️  載入排程失敗: {e}')
            return []

    def _send_durations_for_scheduled(self, scheduled_courses: List[Dict]):
        """為已排程的課程發送時長"""
        if not self.user_info or not self.session_cookie:
            print('  ⚠️  缺少用戶資訊或 Cookie，無法發送時長')
            return

        # 初始化 API 客戶端
        api_client = VisitDurationAPI(
            base_url=self.config.get('target_http'),
            session_cookie=self.session_cookie,
            user_info=self.user_info
        )

        # 讀取時長增加配置
        duration_increase = self.config.get_int('visit_duration_increase', 9000)

        print(f'\n  📤 開始發送時長（增加 {duration_increase} 秒 = {duration_increase//60} 分鐘）...')
        print('  ' + '━'*58)

        success_count = 0
        failed_count = 0

        for i, course in enumerate(scheduled_courses, 1):
            program_name = course.get('program_name')
            lesson_name = course.get('lesson_name')
            course_id = course.get('course_id')

            print(f'\n  [{i}/{len(scheduled_courses)}] {program_name} - {lesson_name}')

            try:
                # 發送時長
                result = api_client.send_visit_duration(
                    visit_duration=duration_increase,
                    course_id=str(course_id),
                    course_name=f"{program_name} - {lesson_name}"
                )

                if result:
                    print(f'      ✅ 發送成功 (+{duration_increase//60} 分鐘)')
                    success_count += 1
                else:
                    print(f'      ❌ 發送失敗')
                    failed_count += 1

                # 延遲（避免請求過快）
                time.sleep(2)

            except Exception as e:
                print(f'      ❌ 發送失敗: {e}')
                failed_count += 1

        print('\n  ' + '━'*58)
        print(f'  📊 發送結果: ✅ 成功 {success_count} 個, ❌ 失敗 {failed_count} 個')

    def _display_scan_results(self, durations: Dict, title: str):
        """顯示掃描結果"""
        print(f'\n  📋 {title}')
        print('  ' + '━'*58)

        if not durations:
            print('  （無資料）')
            return

        for program_name, info in durations.items():
            duration = info.get('duration_minutes', 0)
            scan_time = info.get('scan_time', 'N/A')
            print(f'  • {program_name}')
            print(f'      時數: {duration} 分鐘 | 掃描時間: {scan_time}')

        print('  ' + '━'*58)

    def _display_duration_diff(self):
        """計算並顯示時長差異"""
        print('\n📊 時長變化分析')
        print('='*60)

        if not self.course_durations_before or not self.course_durations_after:
            print('⚠️  缺少掃描資料，無法計算差異')
            return

        # 計算差異
        for program_name in self.course_durations_before.keys():
            before = self.course_durations_before[program_name].get('duration_minutes', 0)
            after = self.course_durations_after.get(program_name, {}).get('duration_minutes', 0)
            diff = after - before

            status_icon = '✅' if diff > 0 else '⚠️'

            print(f'\n{status_icon} {program_name}')
            print(f'   掃描前: {before} 分鐘')
            print(f'   掃描後: {after} 分鐘')
            print(f'   增加量: {diff} 分鐘 ({diff*60} 秒)')

        print('\n' + '='*60)
