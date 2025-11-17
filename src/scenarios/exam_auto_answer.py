# Exam Auto Answer Scenario
# Created: 2025-11-15
#
# 考試自動答題場景 - 整合題庫、匹配引擎和答題頁面

import time
from typing import Dict, List, Optional
from ..core.config_loader import ConfigLoader
from ..core.driver_manager import DriverManager
from ..pages.login_page import LoginPage
from ..pages.course_list_page import CourseListPage
from ..pages.exam_detail_page import ExamDetailPage
from ..pages.exam_answer_page import ExamAnswerPage
from ..services.question_bank import QuestionBankService
from ..services.answer_matcher import AnswerMatcher


class ExamAutoAnswerScenario:
    """考試自動答題場景"""

    def __init__(self, config: ConfigLoader):
        """
        初始化自動答題場景

        Args:
            config: ConfigLoader 實例
        """
        self.config = config
        self.driver_manager = DriverManager(config)
        driver = self.driver_manager.create_driver()

        # 初始化頁面物件
        self.login_page = LoginPage(driver)
        self.course_list_page = CourseListPage(driver)
        self.exam_detail_page = ExamDetailPage(driver)
        self.exam_answer_page = ExamAnswerPage(driver)

        # 初始化服務
        self.question_bank_service = QuestionBankService(config)
        confidence_threshold = float(config.get('answer_confidence_threshold', 0.85))
        self.answer_matcher = AnswerMatcher(confidence_threshold=confidence_threshold)

        # 配置選項
        self.enable_auto_answer = config.get_bool('enable_auto_answer', False)
        self.auto_submit_exam = config.get_bool('auto_submit_exam', False)
        self.screenshot_on_mismatch = config.get_bool('screenshot_on_mismatch', True)
        self.skip_unmatched_questions = config.get_bool('skip_unmatched_questions', True)

        # 統計資訊
        self.stats = {
            'total_questions': 0,
            'matched_questions': 0,
            'unmatched_questions': 0,
            'answered_questions': 0
        }

    def execute(self, exams: List[Dict]):
        """
        執行考試自動答題流程

        Args:
            exams: 考試列表
        """
        if not exams:
            print("[提示] 沒有排程的考試")
            return

        try:
            print(f"\n{'='*60}")
            print(f"🤖 開始執行自動答題場景")
            print(f"{'='*60}")
            print(f"考試數量: {len(exams)}")
            print(f"自動答題: {'啟用' if self.enable_auto_answer else '停用'}")
            print(f"自動交卷: {'啟用' if self.auto_submit_exam else '停用'}")
            print(f"{'='*60}\n")

            # 登入
            self._login()

            # 處理每個考試
            for idx, exam in enumerate(exams, 1):
                print(f"\n{'='*60}")
                print(f"📝 處理考試 {idx}/{len(exams)}")
                print(f"{'='*60}")
                self._process_exam(exam)
                print(f"{'='*60}\n")

                # 考試之間的間隔
                if idx < len(exams):
                    time.sleep(3)

            # 顯示總體統計
            self._show_final_stats()

        except Exception as e:
            print(f"\n[錯誤] 執行失敗: {str(e)}")
            import traceback
            traceback.print_exc()

        finally:
            # 清理
            print("\n[清理] 關閉瀏覽器...")
            self.driver_manager.quit()

    def _login(self):
        """執行登入"""
        print("[Step 1] 登入系統...")
        target_url = self.config.get('target_http')
        self.login_page.driver.get(target_url)
        time.sleep(2)

        if self.login_page.login():
            print("[成功] ✓ 登入完成")
        else:
            raise Exception("登入失敗")

    def _process_exam(self, exam: Dict):
        """
        處理單一考試

        Args:
            exam: 考試資訊
        """
        program_name = exam.get('program_name')
        exam_name = exam.get('exam_name')
        delay = exam.get('delay', 10.0)

        print(f"計畫名稱: {program_name}")
        print(f"考試名稱: {exam_name}")
        print(f"延遲時間: {delay}秒\n")

        # Step 1: 載入題庫
        if self.enable_auto_answer:
            print("[Step 1] 載入題庫...")
            question_count = self.question_bank_service.load_question_bank(program_name)
            if question_count == 0:
                print("[警告] 題庫載入失敗，將無法自動答題")
                self.enable_auto_answer = False
            else:
                print(f"[成功] ✓ 題庫載入完成: {question_count} 題\n")

        # Step 2: 進入考試
        print("[Step 2] 進入考試...")
        self.course_list_page.select_course_by_name(program_name, delay=delay)

        # Step 3: 點擊考試名稱
        print("[Step 3] 點擊考試...")
        self.exam_detail_page.click_exam_by_name(exam_name, delay=delay)
        time.sleep(2)

        # Step 4: 進入考卷區（處理確認流程）
        print("[Step 4] 處理考試確認流程...")
        try:
            self.exam_detail_page.complete_exam_flow(delay=delay)
            print("[成功] ✓ 已進入考卷區\n")
        except Exception as e:
            print(f"[警告] 確認流程可能失敗: {str(e)}")
            print("[繼續] 嘗試繼續執行...\n")

        # 等待考卷頁面載入
        time.sleep(3)

        # Step 5: 自動答題
        if self.enable_auto_answer:
            print("[Step 5] 開始自動答題...")
            self._auto_answer_all_questions()
        else:
            print("[Step 5] 自動答題已停用，跳過")

        # Step 6: 交卷
        print("\n[Step 6] 準備交卷...")
        if self.exam_answer_page.submit_exam_with_confirmation(auto_submit=self.auto_submit_exam):
            # 等待結果頁面
            time.sleep(3)
            # 顯示分數
            self.exam_answer_page.display_score_if_available()
        else:
            print("[提示] 未提交考卷")

    def _auto_answer_all_questions(self):
        """自動答題所有題目"""
        # 偵測所有題目
        questions = self.exam_answer_page.detect_questions()
        if not questions:
            print("[錯誤] 無法偵測到題目")
            return

        total = len(questions)
        self.stats['total_questions'] = total

        print(f"開始處理 {total} 題...\n")

        # 取得題庫
        question_bank = self.question_bank_service.get_all_questions()

        # 逐題處理
        for idx, q_elem in enumerate(questions, 1):
            print(f"--- 第 {idx}/{total} 題 ---")

            # 提取題目資訊
            question_text = self.exam_answer_page.extract_question_text(q_elem)
            question_type = self.exam_answer_page.detect_question_type(q_elem)
            options = self.exam_answer_page.extract_options(q_elem)

            if not question_text:
                print(f"  [錯誤] 無法提取題目文字")
                self.stats['unmatched_questions'] += 1
                continue

            print(f"  題目: {question_text[:60]}...")
            print(f"  題型: {'單選' if question_type == 'single_selection' else '複選'}")
            print(f"  選項數: {len(options)}")

            # 提取選項文字
            web_option_texts = [opt['text'] for opt in options]

            # 匹配題庫（傳入選項用於精確匹配）
            match_result = self.answer_matcher.find_best_match(
                question_text,
                question_bank,
                web_option_texts  # 傳入選項文字列表
            )

            if not match_result:
                # 無法匹配
                print(f"  [無法匹配] 信心分數過低")
                self.stats['unmatched_questions'] += 1

                # 截圖
                if self.screenshot_on_mismatch:
                    self.exam_answer_page.take_screenshot_for_unmatched(q_elem, idx, question_text)

                # 是否跳過
                if self.skip_unmatched_questions:
                    print(f"  [跳過] 此題將不作答\n")
                    continue
                else:
                    print(f"  [停止] 停止自動答題（skip_unmatched_questions=n）")
                    break

            else:
                # 成功匹配
                db_question, confidence = match_result
                print(f"  [匹配成功] 信心: {confidence:.2%}")
                self.stats['matched_questions'] += 1

                # 匹配選項
                web_option_texts = [opt['text'] for opt in options]
                correct_indices = self.answer_matcher.match_correct_options(web_option_texts, db_question)

                if not correct_indices:
                    print(f"  [錯誤] 無法匹配正確選項")
                    self.stats['unmatched_questions'] += 1
                    continue

                # 驗證匹配結果
                if not self.answer_matcher.validate_match(question_text, web_option_texts, db_question, correct_indices):
                    print(f"  [警告] 匹配驗證失敗，跳過此題")
                    self.stats['unmatched_questions'] += 1
                    continue

                # 自動作答
                self.exam_answer_page.auto_answer_question(q_elem, question_type, correct_indices, idx)
                self.stats['answered_questions'] += 1

            print()  # 換行

        # 顯示統計
        print(f"\n{'='*60}")
        print(f"自動答題完成")
        print(f"{'='*60}")
        print(f"  總題數: {self.stats['total_questions']}")
        print(f"  匹配成功: {self.stats['matched_questions']} 題")
        print(f"  無法匹配: {self.stats['unmatched_questions']} 題")
        print(f"  已作答: {self.stats['answered_questions']} 題")
        print(f"{'='*60}\n")

    def _show_final_stats(self):
        """顯示最終統計"""
        print(f"\n{'='*60}")
        print(f"✅ 所有考試處理完成")
        print(f"{'='*60}")
        print(f"  總題數: {self.stats['total_questions']}")
        print(f"  匹配成功率: {self.stats['matched_questions']/max(1, self.stats['total_questions'])*100:.1f}%")
        print(f"  作答率: {self.stats['answered_questions']/max(1, self.stats['total_questions'])*100:.1f}%")
        print(f"{'='*60}\n")
