#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
ExamLearningScenario - 考試學習場景
編排多個頁面物件完成考試流程的業務流程
Created: 2025-01-13
Based on: CourseLearningScenario
"""

from typing import List, Dict
from selenium.webdriver.support.ui import WebDriverWait
from ..core.config_loader import ConfigLoader
from ..core.driver_manager import DriverManager
from ..core.cookie_manager import CookieManager
from ..pages.login_page import LoginPage
from ..pages.course_list_page import CourseListPage
from ..pages.exam_detail_page import ExamDetailPage


class ExamLearningScenario:
    """考試學習場景 - 編排多個頁面物件完成考試流程"""

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
        self.exam_detail = ExamDetailPage(driver)

    def execute(self, exams: List[Dict[str, any]]):
        """
        執行考試流程

        Args:
            exams: 考試資料列表，格式：
                [
                    {
                        "program_name": "課程計畫名稱",
                        "exam_name": "考試名稱",
                        "course_type": "exam",
                        "delay": 10.0
                    },
                    ...
                ]
        """
        success = False  # 追蹤執行是否成功

        try:
            print('=' * 60)
            print('Exam Learning Scenario Started')
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

            # 3. 依序處理每個考試
            print(f'\n[Step 3] Processing {len(exams)} exams...')
            for i, exam in enumerate(exams, 1):
                print(f'\n--- Processing Exam {i}/{len(exams)} ---')
                self._process_exam(exam)

            # 標記為成功
            success = True

            # 4. 完成所有考試
            print('\n[Step 4] All exams processed successfully!')
            print('Waiting 10 seconds before closing browser...')

            # 最後一個考試執行完成後，暫停10秒
            import time
            for remaining in range(10, 0, -1):
                print(f'  Closing in {remaining} seconds...', end='\r')
                time.sleep(1)
            print('\n')  # 換行

            print('Closing browser and cleaning up...')

            print('\n' + '=' * 60)
            print('Exam Learning Scenario Completed')
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

    def _process_exam(self, exam: Dict[str, any]):
        """
        處理單一考試

        Args:
            exam: 考試資料字典
                {
                    "program_name": str,       # 課程計畫名稱
                    "exam_name": str,          # 考試名稱
                    "course_type": "exam",     # 類型標記
                    "delay": float (optional)  # 延遲時間
                }
        """
        program_name = exam.get('program_name')
        exam_name = exam.get('exam_name')
        delay = exam.get('delay', 10.0)

        print(f'  Program: {program_name}')
        print(f'  Exam: {exam_name}')
        print(f'  Type: exam')
        print(f'  Delay: {delay}s')

        try:
            # 步驟 1: 選擇課程計畫
            print('  [1/5] Selecting course program...')
            self.course_list.select_course_by_name(program_name, delay=delay)

            # 步驟 2-5: 完成考試流程
            print('  [2/5] Clicking exam name...')
            print('  [3/5] Clicking continue button...')
            print('  [4/5] Checking agreement checkbox...')
            print('  [5/5] Clicking popup continue button...')

            # 使用 ExamDetailPage 的便捷方法完成整個考試流程
            self.exam_detail.complete_exam_flow(exam_name, delay=delay)

            # 返回課程列表
            print('  [Done] Returning to course list...')
            self.course_list.go_back_to_course_list()

            print(f'  ✓ Exam processed successfully')

        except Exception as e:
            print(f'  ✗ Failed to process exam: {e}')
            # 可以選擇繼續或中斷
            # raise

    def _wait_for_manual_close(self):
        """等待手動關閉瀏覽器"""
        try:
            driver = self.driver_manager.get_driver()
            WebDriverWait(driver, 99999).until(lambda d: False)
        except:
            pass

    def execute_single_exam(self, program_name: str, exam_name: str, delay: float = 10.0):
        """
        執行單一考試（便捷方法）

        Args:
            program_name: 課程計畫名稱
            exam_name: 考試名稱
            delay: 延遲時間
        """
        exam = {
            'program_name': program_name,
            'exam_name': exam_name,
            'course_type': 'exam',
            'delay': delay
        }

        self.execute([exam])

    def __repr__(self) -> str:
        return f"ExamLearningScenario(config={self.config.config_file})"
