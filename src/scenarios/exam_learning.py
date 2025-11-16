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
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from ..core.config_loader import ConfigLoader
from ..core.driver_manager import DriverManager
from ..core.cookie_manager import CookieManager
from ..pages.login_page import LoginPage
from ..pages.course_list_page import CourseListPage
from ..pages.exam_detail_page import ExamDetailPage
from ..pages.exam_answer_page import ExamAnswerPage
from ..services.question_bank import QuestionBankService
from ..services.answer_matcher import AnswerMatcher


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
        self.exam_answer_page = ExamAnswerPage(driver)

        # 初始化自動答題相關服務（如果需要的話會用到）
        self.question_bank = None
        self.answer_matcher = None

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

            # ========== 檢查是否需要自動答題 ==========
            enable_auto_answer = exam.get('enable_auto_answer', False)

            if enable_auto_answer and self._is_in_exam_answer_page():
                print('\n' + '=' * 80)
                print('  【自動答題模式啟動】')
                print('=' * 80)
                print(f'  📝 偵測到該考試啟用自動答題功能')
                print(f'  🎯 開始自動答題流程...\n')

                # 執行自動答題
                self._auto_answer_current_exam(exam)

                print('\n' + '=' * 80)
                print('  【自動答題完成】')
                print('=' * 80)
            else:
                if not enable_auto_answer:
                    print('\n  ℹ️  該考試未啟用自動答題，保持手動模式')
                elif not self._is_in_exam_answer_page():
                    print('\n  ⚠️  未偵測到考卷區頁面，跳過自動答題')

                # 等待用戶手動操作
                print('\n  ⏸️  請手動完成考試')
                input('  完成後按 Enter 繼續...')
            # ========== 自動答題檢查結束 ==========

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

    def _is_in_exam_answer_page(self) -> bool:
        """
        檢測是否已進入考卷區頁面

        Returns:
            bool: 如果在考卷區返回 True，否則返回 False
        """
        try:
            driver = self.driver_manager.get_driver()

            # 等待考卷頁面載入，使用短超時避免長時間等待
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.subject"))
            )

            # 檢查是否有題目元素
            questions = driver.find_elements(By.CSS_SELECTOR, "li.subject")
            if len(questions) > 0:
                print(f'  ✅ 偵測到考卷區頁面（共 {len(questions)} 題）')
                return True
            else:
                print('  ⚠️  未偵測到題目元素')
                return False

        except Exception as e:
            print(f'  ⚠️  考卷區檢測失敗: {e}')
            return False

    def _auto_answer_current_exam(self, exam: Dict[str, any]):
        """
        執行自動答題邏輯（針對當前考試）

        Args:
            exam: 考試資料字典
        """
        import time

        try:
            # 1. 為每個考試載入對應的題庫
            # 修復：每次都重新載入，避免不同考試使用錯誤的題庫
            print('  📚 正在載入題庫...')

            # 創建新的題庫服務實例
            self.question_bank = QuestionBankService(self.config)

            # 載入題庫（根據 program_name 或使用總題庫）
            program_name = exam.get('program_name')
            question_count = self.question_bank.load_question_bank(program_name)

            if question_count > 0:
                print(f'  ✅ 題庫已載入（共 {question_count} 題）')
                print(f'  📋 課程名稱: {program_name}')
            else:
                print(f'  ❌ 題庫載入失敗')
                return

            # 2. 初始化答案匹配器（如果尚未初始化）
            if self.answer_matcher is None:
                confidence_threshold = float(self.config.get('answer_confidence_threshold', 0.85))
                self.answer_matcher = AnswerMatcher(confidence_threshold=confidence_threshold)
                print(f'  ✅ 答案匹配器已初始化（信心門檻: {confidence_threshold}）')

            # 3. 獲取所有題目
            print('\n  🔍 開始分析考試題目...')
            all_questions = self.exam_answer_page.detect_questions()
            total_questions = len(all_questions)
            print(f'  📊 偵測到 {total_questions} 題')

            if total_questions == 0:
                print('  ❌ 未找到任何題目，無法自動答題')
                return

            # 4. 逐題作答
            matched_count = 0
            answered_count = 0
            unmatched_questions = []

            for idx, question_elem in enumerate(all_questions, 1):
                print(f'\n  --- 第 {idx}/{total_questions} 題 ---')

                try:
                    # 4.1 獲取題目文字
                    question_text = self.exam_answer_page.extract_question_text(question_elem)
                    print(f'  📝 題目: {question_text[:50]}...' if len(question_text) > 50 else f'  📝 題目: {question_text}')

                    # 4.2 獲取選項（提前獲取，用於匹配）
                    options = self.exam_answer_page.extract_options(question_elem)
                    option_texts = [opt['text'] for opt in options]

                    # 4.3 查詢題庫（傳入選項用於精確匹配）
                    match_result = self.answer_matcher.find_best_match(
                        question_text,
                        self.question_bank.questions,
                        option_texts  # 傳入選項文字列表
                    )

                    if match_result is None:
                        print(f'  ⚠️  無法匹配題目')
                        unmatched_questions.append({'index': idx, 'text': question_text})

                        # 截圖保存
                        if self.config.get_bool('screenshot_on_mismatch', True):
                            self._save_unmatched_screenshot(idx, question_text)

                        # 根據配置決定是否跳過
                        if self.config.get_bool('skip_unmatched_questions', True):
                            print(f'  ⏭️   跳過該題')
                            continue
                        else:
                            print(f'  ❌ 停止自動答題（設定不允許跳過）')
                            break

                    # 解包 tuple: (Question对象, 信心分数)
                    db_question, confidence = match_result
                    matched_count += 1
                    print(f'  ✅ 匹配成功（信心: {confidence:.2%}）')

                    # 從 Question 對象中獲取正確答案索引
                    correct_option_indices = db_question.get_correct_indices()

                    print(f'  🎯 正確答案索引: {correct_option_indices}')

                    # 點擊正確選項
                    for correct_idx in correct_option_indices:
                        if correct_idx < len(options):
                            # options 返回的格式是 [{'element': ..., 'text': ..., 'input': ...}, ...]
                            self.exam_answer_page.click_option(options[correct_idx]['input'])
                            answered_count += 1
                            print(f'  ✓ 已選擇選項 {chr(65 + correct_idx)}')
                        else:
                            print(f'  ⚠️  選項索引 {correct_idx} 超出範圍（選項數: {len(options)}）')

                    time.sleep(0.5)  # 短暫延遲避免過快操作

                except Exception as e:
                    print(f'  ❌ 處理第 {idx} 題時發生錯誤: {e}')
                    import traceback
                    traceback.print_exc()
                    continue

            # 5. 顯示統計結果
            print('\n' + '=' * 80)
            print('  【答題統計】')
            print('=' * 80)
            print(f'  總題數: {total_questions}')
            print(f'  匹配成功: {matched_count}')
            print(f'  無法匹配: {len(unmatched_questions)}')
            print(f'  已作答: {answered_count}')

            # 計算匹配成功率
            match_rate = (matched_count / total_questions * 100) if total_questions > 0 else 0
            print(f'  匹配成功率: {match_rate:.1f}%')
            print('=' * 80)

            # 6. 判斷是否自動交卷
            auto_submit = self.config.get_bool('auto_submit_exam', False)

            # 新邏輯: 如果匹配成功率達到 100%，自動交卷
            if match_rate == 100.0:
                print('\n  🎉 匹配成功率達到 100%！自動交卷中...')
                print('  ⏱️  等待 3 秒後自動提交...')
                time.sleep(3)
                # 自動交卷並確認
                success = self.exam_answer_page.submit_exam_with_confirmation(auto_submit=True)
                if success:
                    print('  ✅ 考試已成功提交！')
                else:
                    print('  ⚠️  交卷過程可能有問題，請手動確認')
            elif not auto_submit:
                print('\n  ⏸️  自動答題完成，請確認答案')
                print(f'  📊 匹配成功率: {match_rate:.1f}% (未達 100%，需手動確認)')
                # 使用 ExamAnswerPage 的提交方法（內建確認機制）
                self.exam_answer_page.submit_exam_with_confirmation(auto_submit=False)
            else:
                print('\n  📤 自動提交模式啟用，正在提交考試...')
                time.sleep(2)
                # 使用 ExamAnswerPage 的提交方法（自動確認）
                self.exam_answer_page.submit_exam_with_confirmation(auto_submit=True)

        except Exception as e:
            print(f'\n  ❌ 自動答題過程發生錯誤: {e}')
            import traceback
            traceback.print_exc()

    def _save_unmatched_screenshot(self, question_index: int, question_text: str):
        """
        儲存無法匹配題目的截圖

        Args:
            question_index: 題目索引
            question_text: 題目文字
        """
        import os
        from datetime import datetime

        try:
            driver = self.driver_manager.get_driver()
            screenshot_dir = self.config.get('screenshot_dir', 'screenshots/unmatched')

            if not os.path.exists(screenshot_dir):
                os.makedirs(screenshot_dir)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_file = os.path.join(screenshot_dir, f'unmatched_q{question_index}_{timestamp}.png')
            text_file = os.path.join(screenshot_dir, f'unmatched_q{question_index}_{timestamp}.txt')

            # 保存截圖
            driver.save_screenshot(screenshot_file)

            # 保存題目文字
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(f'題號: {question_index}\n')
                f.write(f'時間: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
                f.write(f'題目內容:\n{question_text}\n')

            print(f'  📸 已保存截圖: {screenshot_file}')

        except Exception as e:
            print(f'  ⚠️  截圖保存失敗: {e}')

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
