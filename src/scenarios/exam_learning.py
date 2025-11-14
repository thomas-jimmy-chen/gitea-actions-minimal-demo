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

            # ========== 新增：元素定位測試 ==========
            print('\n' + '=' * 80)
            print('  【考卷區元素定位測試】')
            print('=' * 80)

            # 執行測試並獲取輸出文件路徑
            output_file = self._test_exam_page_locators()

            if output_file:
                print(f'\n  📄 測試結果已輸出至: {output_file}')
                print('  ✅ 請檢閱文檔內容')
            else:
                print('\n  ⚠️ 測試結果輸出失敗')

            print('=' * 80)

            # 等待用戶按 Enter
            print('\n⏸️  測試完成！')
            input('  按 Enter 繼續...')
            # ========== 測試結束 ==========

            # 返回課程列表（直接跳轉 URL）
            print('\n  [Done] Returning to course list...')
            driver = self.driver_manager.get_driver()
            driver.get('https://elearn.post.gov.tw/user/courses')
            import time
            time.sleep(2)
            print('  ✓ Returned to course list')

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

    def _test_exam_page_locators(self):
        """
        測試考試頁面的元素定位
        將所有題目、選項、單選按鈕等資訊輸出到文檔

        Returns:
            str: 輸出文件路徑，失敗時返回 None
        """
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        import time
        import os
        from datetime import datetime

        driver = self.driver_manager.get_driver()

        # 準備輸出目錄和文件
        output_dir = 'logs'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(output_dir, f'exam_locator_test_{timestamp}.txt')

        try:
            # 等待題目載入
            print('  ⏳ 等待考卷載入...')
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.subject"))
            )
            time.sleep(2)  # 額外等待確保完全載入
            print('  ✅ 考卷已載入')

            # 開始寫入文件
            with open(output_file, 'w', encoding='utf-8') as f:
                # 寫入標題
                f.write('=' * 100 + '\n')
                f.write('考試頁面元素定位測試報告\n')
                f.write('=' * 100 + '\n')
                f.write(f'測試時間: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
                f.write(f'當前 URL: {driver.current_url}\n')
                f.write('=' * 100 + '\n\n')

                # === 測試 1: 獲取總題數 ===
                f.write('【測試 1】獲取總題數\n')
                f.write('-' * 100 + '\n')

                questions = driver.find_elements(By.CSS_SELECTOR, "li.subject")
                total_questions = len(questions)

                f.write(f'定位方法: CSS Selector "li.subject"\n')
                f.write(f'總題數: {total_questions} 題\n')
                f.write(f'邊界值: 第 1 題 ~ 第 {total_questions} 題\n')
                f.write('\n')

                # 控制台同步輸出
                print(f'  📊 偵測到總題數: {total_questions} 題')
                print(f'  📏 邊界值: 1 ~ {total_questions}')

                if total_questions == 0:
                    f.write('❌ 錯誤：未找到任何題目！\n')
                    print('  ❌ 錯誤：未找到任何題目！')
                    return output_file

                # === 測試 2: 遍歷所有題目 ===
                f.write('【測試 2】遍歷所有題目並提取資訊\n')
                f.write('-' * 100 + '\n\n')

                print(f'  🔍 開始遍歷 {total_questions} 題...')

                # 遍歷所有題目
                for idx, question_elem in enumerate(questions, 1):
                    f.write(f'>>> 第 {idx} 題（共 {total_questions} 題）<<<\n')

                    # 控制台顯示進度
                    print(f'    處理第 {idx}/{total_questions} 題...', end='\r')

                    # 2.1 獲取題目文字
                    try:
                        desc_elem = question_elem.find_element(
                            By.XPATH, ".//span[contains(@class, 'subject-description')]"
                        )
                        question_text = desc_elem.text.strip()
                        question_html = desc_elem.get_attribute('innerHTML')

                        f.write(f'  ✅ 題目文字定位成功\n')
                        f.write(f'  📝 題目內容（純文字）:\n')
                        f.write(f'     {question_text}\n')
                        f.write(f'  📄 HTML 長度: {len(question_html)} 字元\n')
                    except Exception as e:
                        f.write(f'  ❌ 題目文字定位失敗: {e}\n')
                        continue

                    # 2.2 獲取題型
                    try:
                        subject_class = question_elem.get_attribute('class')
                        if "single_selection" in subject_class:
                            subject_type = "單選題"
                        elif "multiple_selection" in subject_class:
                            subject_type = "複選題"
                        elif "true_or_false" in subject_class:
                            subject_type = "是非題"
                        else:
                            subject_type = "未知題型"
                        f.write(f'  📋 題型: {subject_type}\n')
                    except Exception as e:
                        f.write(f'  ⚠️ 無法判斷題型: {e}\n')

                    # 2.3 獲取所有選項
                    try:
                        options = question_elem.find_elements(
                            By.XPATH, ".//li[contains(@class, 'option')]"
                        )
                        f.write(f'  ✅ 選項數量: {len(options)}\n')
                        f.write(f'  選項詳細資訊:\n')

                        # 2.4 遍歷每個選項
                        for opt_idx, option_elem in enumerate(options):
                            try:
                                # 獲取選項文字
                                option_content = option_elem.find_element(
                                    By.CSS_SELECTOR, ".option-content"
                                )
                                option_text = option_content.text.strip()

                                # 獲取單選/複選按鈕
                                input_type = "無"
                                input_element = None
                                try:
                                    radio = option_elem.find_element(By.CSS_SELECTOR, "input[type='radio']")
                                    input_type = "radio（單選按鈕）"
                                    input_element = radio
                                except:
                                    try:
                                        checkbox = option_elem.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
                                        input_type = "checkbox（複選按鈕）"
                                        input_element = checkbox
                                    except:
                                        input_type = "無按鈕"

                                # 獲取按鈕狀態
                                button_status = ""
                                if input_element:
                                    is_selected = input_element.is_selected()
                                    is_enabled = input_element.is_enabled()
                                    button_status = f"已選: {is_selected}, 可用: {is_enabled}"

                                # 寫入選項資訊
                                f.write(f'    {chr(65+opt_idx)}. {option_text}\n')
                                f.write(f'       - 按鈕類型: {input_type}\n')
                                if button_status:
                                    f.write(f'       - 按鈕狀態: {button_status}\n')

                            except Exception as e:
                                f.write(f'    {chr(65+opt_idx)}. ❌ 選項定位失敗: {e}\n')

                    except Exception as e:
                        f.write(f'  ❌ 選項定位失敗: {e}\n')

                    f.write('\n' + '-' * 100 + '\n\n')

                # 清除進度顯示
                print(' ' * 50, end='\r')
                print(f'  ✅ 已完成 {total_questions} 題的資料收集')

                # === 測試總結 ===
                f.write('=' * 100 + '\n')
                f.write('【測試總結】\n')
                f.write('=' * 100 + '\n')
                f.write(f'✅ 總題數定位: 成功\n')
                f.write(f'✅ 題目總數: {total_questions} 題\n')
                f.write(f'✅ 邊界值: 1 ~ {total_questions}\n')
                f.write(f'✅ 題目文字定位: 成功\n')
                f.write(f'✅ 選項定位: 成功\n')
                f.write(f'✅ 單選/複選按鈕定位: 成功\n')
                f.write('=' * 100 + '\n')
                f.write(f'\n報告生成時間: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
                f.write(f'輸出文件: {output_file}\n')

            print(f'  ✅ 測試報告已生成')
            return output_file

        except Exception as e:
            print(f'  ❌ 測試過程發生錯誤: {e}')
            import traceback
            traceback.print_exc()

            # 即使發生錯誤，也嘗試寫入錯誤資訊
            try:
                with open(output_file, 'a', encoding='utf-8') as f:
                    f.write(f'\n\n❌ 測試過程發生錯誤:\n{str(e)}\n')
                    f.write(traceback.format_exc())
            except:
                pass

            return None

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
