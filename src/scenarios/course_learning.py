#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
CourseLearningScenario - 課程學習場景
編排多個頁面物件完成課程學習的業務流程
"""

from typing import List, Dict
from selenium.webdriver.support.ui import WebDriverWait
from ..core.config_loader import ConfigLoader
from ..core.driver_manager import DriverManager
from ..core.cookie_manager import CookieManager
from ..pages.login_page import LoginPage
from ..pages.course_list_page import CourseListPage
from ..pages.course_detail_page import CourseDetailPage
from ..utils.screenshot_utils import ScreenshotManager
import time


class CourseLearningScenario:
    """課程學習場景 - 編排多個頁面物件完成業務流程"""

    def __init__(self, config: ConfigLoader, keep_browser_on_error: bool = False, time_tracker=None, visit_duration_increase: int = None):
        """
        初始化場景

        Args:
            config: 配置載入器
            keep_browser_on_error: 發生錯誤時是否保持瀏覽器開啟（預設為 False）
            time_tracker: 時間追蹤器（可選）
            visit_duration_increase: 訪問時長增加值（秒），從 main.py 傳入
        """
        self.config = config
        self.keep_browser_on_error = keep_browser_on_error
        self.time_tracker = time_tracker

        # 載入時間與截圖配置
        self.timing_config = config.load_timing_config()

        # 儲存蟲洞功能配置（訪問時長增加值）
        self.visit_duration_increase = visit_duration_increase

        # 初始化核心元件
        self.driver_manager = DriverManager(config)
        self.cookie_manager = CookieManager(config.get('cookies_file'))

        # 建立 Driver
        driver = self.driver_manager.create_driver()

        # 初始化頁面物件
        self.login_page = LoginPage(driver, self.cookie_manager)
        self.course_list = CourseListPage(driver)
        self.course_detail = CourseDetailPage(driver)

        # 初始化截圖管理器
        self.screenshot_manager = ScreenshotManager(config, self.timing_config)

    def execute(self, courses: List[Dict[str, any]]):
        """
        執行課程學習流程

        Args:
            courses: 課程資料列表，格式：
                [
                    {
                        "program_name": "課程計畫名稱",
                        "lesson_name": "課程名稱",
                        "course_id": 369,
                        "delay": 7.0
                    },
                    ...
                ]
        """
        success = False  # 追蹤執行是否成功

        try:
            print('=' * 60)
            print('Course Learning Scenario Started')
            print('=' * 60)

            # 1. 自動登入（最多重試 3 次）
            print('\n[Step 1] Logging in...')
            max_retries = 3
            login_success = False

            for attempt in range(max_retries):
                login_success = self.login_page.auto_login(
                    username=self.config.get('user_name'),
                    password=self.config.get('password'),
                    url=self.config.get('target_http')
                )

                if login_success:
                    print('[SUCCESS] Login successful\n')
                    break
                else:
                    if attempt < max_retries - 1:
                        print(f'[WARN] Login failed, retrying... ({attempt + 1}/{max_retries})\n')
                        # 刷新頁面以獲取新的驗證碼
                        self.login_page.goto(self.config.get('target_http'))
                    else:
                        print('[ERROR] Login failed after maximum retries\n')
                        raise Exception('Login failed after maximum retries')

            if not login_success:
                raise Exception('Login failed')

            # 2. 前往我的課程
            print('\n[Step 2] Navigating to my courses...')
            self.course_list.goto_my_courses()

            # 3. 依序處理每個課程
            print(f'\n[Step 3] Processing {len(courses)} courses...')
            for i, course in enumerate(courses, 1):
                print(f'\n--- Processing Course {i}/{len(courses)} ---')
                self._process_course(course)

            # 標記為成功
            success = True

            # 4. 完成所有課程
            print('\n[Step 4] All courses processed successfully!')
            print('Waiting 10 seconds before closing browser...')

            # 最後一個課程執行完成後，暫停10秒
            import time
            for remaining in range(10, 0, -1):
                print(f'  Closing in {remaining} seconds...', end='\r')
                time.sleep(1)
            print('\n')  # 換行

            print('Closing browser and cleaning up...')

            print('\n' + '=' * 60)
            print('Course Learning Scenario Completed')
            print('=' * 60)

        except KeyboardInterrupt:
            print('\n[INFO] User interrupted, closing...')
        except Exception as e:
            print(f'\n[ERROR] Scenario execution failed: {e}')
            import traceback
            traceback.print_exc()

            # 根據設定決定是否保持瀏覽器開啟
            if self.keep_browser_on_error:
                print('\n[INFO] Keeping browser open for debugging... Press Ctrl+C to exit')
                self._wait_for_manual_close()
            else:
                print('\n[INFO] Closing browser due to error...')
        finally:
            print('[INFO] Closing browser...')
            self.driver_manager.quit()
            print('[INFO] Browser closed')

    def _process_course(self, course: Dict[str, any]):
        """
        處理單一課程（整合截圖功能）

        Args:
            course: 課程資料字典
                {
                    "program_name": str,
                    "lesson_name": str,
                    "course_id": int,
                    "enable_screenshot": bool (optional, default: False)
                }
        """
        program_name = course.get('program_name')
        lesson_name = course.get('lesson_name')
        course_id = course.get('course_id')
        enable_screenshot = course.get('enable_screenshot', False)

        # 取得延遲時間（從 timing.json）
        delay_stage2 = self.timing_config.get('delays', {}).get('stage_2_program_detail', 11.0)
        delay_stage3 = self.timing_config.get('delays', {}).get('stage_3_lesson_detail', 7.0)
        delay_stage1 = self.timing_config.get('delays', {}).get('stage_1_course_list', 3.0)

        print(f'\n{"=" * 80}')
        print(f'課程: {lesson_name}')
        print(f'計畫: {program_name}')
        print(f'截圖: {"啟用" if enable_screenshot else "停用"}')
        print(f'{"=" * 80}\n')

        # 開始追蹤課程時間
        if self.time_tracker:
            self.time_tracker.start_course(lesson_name, program_name)

        try:
            # Step 1: 選擇課程計畫（進入第二階）
            print(f'[Step 1] 選擇課程計畫: {program_name}')
            self.course_list.select_course_by_name(program_name, delay=delay_stage2)
            print(f'  ✓ 已進入第二階，等待 {delay_stage2} 秒...\n')

            # 記錄延遲時間
            if self.time_tracker:
                self.time_tracker.record_delay(delay_stage2, '課程計畫頁面載入等待')

            # 📸 第一次截圖（第二階 - 進入時）
            if enable_screenshot:
                print(f'[截圖 1/2] 第二階 - 進入時')
                self.screenshot_manager.take_screenshot(
                    self.driver_manager.get_driver(),
                    lesson_name,
                    sequence=1
                )
                print()

            # 顯示蟲洞功能狀態（第二階 - 進入時）
            if self.config.get_bool('modify_visits'):
                minutes = self.visit_duration_increase // 60
                print(f'⏰ 蟲洞: 已開啟，時間推至 {minutes} 分鐘\n')

            # Step 2: 選擇課程單元（進入第三階）
            print(f'[Step 2] 選擇課程單元: {lesson_name}')
            self.course_detail.select_lesson_by_name(lesson_name, delay=delay_stage3)

            # 顯示蟲洞功能狀態（進入第三階）
            if self.config.get_bool('modify_visits'):
                minutes = self.visit_duration_increase // 60
                print(f'⏰ 蟲洞: 已開啟，時間推至 {minutes} 分鐘')

            print(f'  ✓ 已進入第三階，等待 {delay_stage3} 秒...\n')

            # 記錄延遲時間
            if self.time_tracker:
                self.time_tracker.record_delay(delay_stage3, '課程單元頁面載入等待')

            # Step 3: 返回課程計畫（返回第二階）
            print(f'[Step 3] 返回課程計畫 (course_id: {course_id})')
            self.course_detail.go_back_to_course(course_id)

            # 顯示蟲洞功能狀態（返回第二階）
            if self.config.get_bool('modify_visits'):
                minutes = self.visit_duration_increase // 60
                print(f'⏰ 蟲洞: 已開啟，時間推至 {minutes} 分鐘')

            print(f'  ✓ 已返回第二階，等待 {delay_stage2} 秒...\n')
            time.sleep(delay_stage2)

            # 記錄延遲時間
            if self.time_tracker:
                self.time_tracker.record_delay(delay_stage2, '返回課程計畫等待')

            # 📸 第二次截圖（第二階 - 返回時）
            if enable_screenshot:
                print(f'[截圖 2/2] 第二階 - 返回時')
                self.screenshot_manager.take_screenshot(
                    self.driver_manager.get_driver(),
                    lesson_name,
                    sequence=2
                )
                print()

            # Step 4: 返回課程列表（返回第一階）
            print(f'[Step 4] 返回課程列表')
            self.course_list.go_back_to_course_list()
            time.sleep(delay_stage1)
            print(f'  ✓ 已返回第一階\n')

            # 記錄延遲時間
            if self.time_tracker:
                self.time_tracker.record_delay(delay_stage1, '返回課程列表等待')

            print(f'[SUCCESS] 課程完成: {lesson_name}\n')

            # 結束追蹤課程時間
            if self.time_tracker:
                self.time_tracker.end_course()

        except Exception as e:
            print(f'[ERROR] 處理課程失敗: {lesson_name}')
            print(f'錯誤訊息: {str(e)}\n')
            raise

    def _wait_for_manual_close(self):
        """等待手動關閉瀏覽器"""
        try:
            driver = self.driver_manager.get_driver()
            WebDriverWait(driver, 99999).until(lambda d: False)
        except:
            pass

    def execute_single_course(self, program_name: str, lesson_name: str, course_id: int, delay: float = 7.0):
        """
        執行單一課程（便捷方法）

        Args:
            program_name: 課程計畫名稱
            lesson_name: 課程名稱
            course_id: 課程 ID
            delay: 延遲時間
        """
        course = {
            'program_name': program_name,
            'lesson_name': lesson_name,
            'course_id': course_id,
            'delay': delay
        }

        self.execute([course])

    def __repr__(self) -> str:
        return f"CourseLearningScenario(config={self.config.config_file})"
