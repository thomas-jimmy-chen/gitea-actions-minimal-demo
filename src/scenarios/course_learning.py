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


class CourseLearningScenario:
    """課程學習場景 - 編排多個頁面物件完成業務流程"""

    def __init__(self, config: ConfigLoader, keep_browser_on_error: bool = False):
        """
        初始化場景

        Args:
            config: 配置載入器
            keep_browser_on_error: 發生錯誤時是否保持瀏覽器開啟（預設為 False）
        """
        self.config = config
        self.keep_browser_on_error = keep_browser_on_error

        # 初始化核心元件
        self.driver_manager = DriverManager(config)
        self.cookie_manager = CookieManager(config.get('cookies_file'))

        # 建立 Driver
        driver = self.driver_manager.create_driver()

        # 初始化頁面物件
        self.login_page = LoginPage(driver, self.cookie_manager)
        self.course_list = CourseListPage(driver)
        self.course_detail = CourseDetailPage(driver)

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

            # 1. 自動登入
            print('\n[Step 1] Logging in...')
            self.login_page.auto_login(
                username=self.config.get('user_name'),
                password=self.config.get('password'),
                url=self.config.get('target_http')
            )

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
        處理單一課程

        Args:
            course: 課程資料字典
                {
                    "program_name": str,
                    "lesson_name": str,
                    "course_id": int,
                    "delay": float (optional)
                }
        """
        program_name = course.get('program_name')
        lesson_name = course.get('lesson_name')
        course_id = course.get('course_id')
        delay = course.get('delay', 7.0)

        print(f'  Program: {program_name}')
        print(f'  Lesson: {lesson_name}')
        print(f'  Course ID: {course_id}')

        try:
            # 選擇課程計畫
            self.course_list.select_course_by_name(program_name, delay=delay)

            # 選擇課程
            self.course_detail.select_lesson_by_name(lesson_name, delay=delay)

            # 返回課程計畫
            self.course_detail.go_back_to_course(course_id)

            # 返回課程列表
            self.course_list.go_back_to_course_list()

            print(f'  ✓ Course processed successfully')

        except Exception as e:
            print(f'  ✗ Failed to process course: {e}')
            # 可以選擇繼續或中斷
            # raise

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
