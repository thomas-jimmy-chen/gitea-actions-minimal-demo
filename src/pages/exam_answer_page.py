# Exam Answer Page
# Created: 2025-11-15
#
# 考卷區答題頁面 - 處理考試答題的所有操作

import time
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from .base_page import BasePage


class ExamAnswerPage(BasePage):
    """考卷區答題頁面"""

    # 定位器
    SUBJECT_LIST = (By.CLASS_NAME, "subject")
    SUBJECT_DESCRIPTION = (By.CLASS_NAME, "subject-description")
    OPTION_LIST = (By.CLASS_NAME, "option")
    OPTION_CONTENT = (By.CLASS_NAME, "option-content")
    RADIO_INPUT = (By.CSS_SELECTOR, "input[type='radio']")
    CHECKBOX_INPUT = (By.CSS_SELECTOR, "input[type='checkbox']")
    # 交卷按鈕（考卷內）
    SUBMIT_BUTTON = (By.XPATH, "/html/body/div[3]/div[4]/div[3]/div[9]/div/div/div[3]/div/div[3]/a")
    # 確認按鈕（浮動視窗）
    CONFIRM_BUTTON = (By.XPATH, "//*[@id='submit-exam-confirmation-popup']/div/div[3]/div/button[1]")

    def __init__(self, driver):
        """初始化考卷頁面"""
        super().__init__(driver)
        self.screenshot_dir = "screenshots/unmatched"
        self._ensure_screenshot_dir()

    def _ensure_screenshot_dir(self):
        """確保截圖目錄存在"""
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)
            print(f"[建立] 截圖目錄: {self.screenshot_dir}")

    def detect_questions(self) -> List[WebElement]:
        """
        偵測所有考題

        Returns:
            考題元素列表
        """
        try:
            # 等待題目載入
            time.sleep(2)
            questions = self.driver.find_elements(*self.SUBJECT_LIST)
            print(f"\n[偵測] 共 {len(questions)} 題")
            return questions
        except Exception as e:
            print(f"[錯誤] 偵測考題失敗: {str(e)}")
            return []

    def detect_question_type(self, question_elem: WebElement) -> str:
        """
        偵測題型（單選/複選）

        Args:
            question_elem: 題目元素

        Returns:
            "single_selection" 或 "multiple_selection"
        """
        try:
            # 檢查是否有 radio 或 checkbox
            radios = question_elem.find_elements(*self.RADIO_INPUT)
            checkboxes = question_elem.find_elements(*self.CHECKBOX_INPUT)

            if radios:
                return "single_selection"
            elif checkboxes:
                return "multiple_selection"
            else:
                return "unknown"
        except Exception as e:
            print(f"[錯誤] 偵測題型失敗: {str(e)}")
            return "unknown"

    def extract_question_text(self, question_elem: WebElement) -> str:
        """
        提取題目文字（保留 HTML 以便後續清理）

        Args:
            question_elem: 題目元素

        Returns:
            題目文字
        """
        try:
            desc_elem = question_elem.find_element(*self.SUBJECT_DESCRIPTION)
            # 取得 innerHTML（含HTML標籤）
            html_text = desc_elem.get_attribute("innerHTML")
            # 也取得純文字版本
            text_content = desc_elem.text
            return text_content.strip() if text_content else html_text
        except Exception as e:
            print(f"[錯誤] 提取題目文字失敗: {str(e)}")
            return ""

    def extract_options(self, question_elem: WebElement) -> List[Dict]:
        """
        提取所有選項

        Args:
            question_elem: 題目元素

        Returns:
            選項資訊列表，格式: [{'element': WebElement, 'text': str, 'input': WebElement}, ...]
        """
        try:
            option_elems = question_elem.find_elements(*self.OPTION_LIST)
            options = []

            for opt_elem in option_elems:
                try:
                    # 提取選項文字
                    content_elem = opt_elem.find_element(*self.OPTION_CONTENT)
                    option_text = content_elem.text.strip()

                    # 找到對應的 input 元素（radio 或 checkbox）
                    try:
                        input_elem = opt_elem.find_element(*self.RADIO_INPUT)
                    except NoSuchElementException:
                        input_elem = opt_elem.find_element(*self.CHECKBOX_INPUT)

                    options.append({
                        'element': opt_elem,
                        'text': option_text,
                        'input': input_elem
                    })
                except Exception as e:
                    print(f"[警告] 提取選項失敗: {str(e)}")
                    continue

            return options
        except Exception as e:
            print(f"[錯誤] 提取選項列表失敗: {str(e)}")
            return []

    def click_option(self, option_input: WebElement, delay: float = 0.5):
        """
        點擊選項（使用 JavaScript 確保點擊成功）

        Args:
            option_input: 選項的 input 元素
            delay: 點擊後延遲時間
        """
        try:
            # 使用 JavaScript 點擊以避免被遮擋
            self.driver.execute_script("arguments[0].click();", option_input)
            time.sleep(delay)
        except Exception as e:
            print(f"[錯誤] 點擊選項失敗: {str(e)}")

    def auto_answer_question(
        self,
        question_elem: WebElement,
        question_type: str,
        correct_indices: List[int],
        question_number: int
    ):
        """
        自動作答單一題目

        Args:
            question_elem: 題目元素
            question_type: 題型
            correct_indices: 正確選項索引列表
            question_number: 題號（用於顯示）
        """
        try:
            options = self.extract_options(question_elem)

            if not options:
                print(f"  [錯誤] 第 {question_number} 題: 無法提取選項")
                return

            if not correct_indices:
                print(f"  [跳過] 第 {question_number} 題: 無正確答案資訊")
                return

            # 根據題型點擊選項
            if question_type == "single_selection":
                # 單選題：點擊第一個正確答案
                idx = correct_indices[0]
                if idx < len(options):
                    self.click_option(options[idx]['input'])
                    print(f"  ✓ 第 {question_number} 題: 已選擇選項 {idx + 1}")
                else:
                    print(f"  [錯誤] 第 {question_number} 題: 選項索引超出範圍 ({idx})")

            elif question_type == "multiple_selection":
                # 複選題：點擊所有正確答案
                selected = []
                for idx in correct_indices:
                    if idx < len(options):
                        self.click_option(options[idx]['input'])
                        selected.append(idx + 1)
                    else:
                        print(f"  [錯誤] 第 {question_number} 題: 選項索引超出範圍 ({idx})")

                if selected:
                    print(f"  ✓ 第 {question_number} 題: 已選擇選項 {selected}")

        except Exception as e:
            print(f"  [錯誤] 第 {question_number} 題: 自動作答失敗 - {str(e)}")

    def take_screenshot_for_unmatched(
        self,
        question_elem: WebElement,
        question_number: int,
        question_text: str
    ) -> str:
        """
        為無法匹配的題目截圖

        Args:
            question_elem: 題目元素
            question_number: 題號
            question_text: 題目文字

        Returns:
            截圖檔案路徑
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"question_{question_number}_{timestamp}.png"
            filepath = os.path.join(self.screenshot_dir, filename)

            # 捲動到題目位置
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", question_elem)
            time.sleep(0.5)

            # 截圖整個瀏覽器視窗
            self.driver.save_screenshot(filepath)

            # 記錄題目資訊到文字檔
            info_file = filepath.replace('.png', '.txt')
            with open(info_file, 'w', encoding='utf-8') as f:
                f.write(f"題號: {question_number}\n")
                f.write(f"時間: {timestamp}\n")
                f.write(f"題目: {question_text}\n")

            print(f"  [截圖] 已儲存: {filepath}")
            return filepath

        except Exception as e:
            print(f"  [錯誤] 截圖失敗: {str(e)}")
            return ""

    def count_answered_questions(self) -> Tuple[int, int]:
        """
        計算已作答和未作答的題數

        Returns:
            (已作答數, 總題數)
        """
        try:
            questions = self.detect_questions()
            total = len(questions)
            answered = 0

            for q_elem in questions:
                # 檢查是否有被選中的選項
                checked_inputs = q_elem.find_elements(By.CSS_SELECTOR, "input:checked")
                if checked_inputs:
                    answered += 1

            return (answered, total)
        except Exception as e:
            print(f"[錯誤] 統計答題數失敗: {str(e)}")
            return (0, 0)

    def show_answer_summary(self):
        """顯示答題統計摘要"""
        answered, total = self.count_answered_questions()
        unanswered = total - answered

        print(f"\n{'='*60}")
        print(f"📊 答題完成統計")
        print(f"{'='*60}")
        print(f"  總題數: {total}")
        print(f"  已作答: {answered} 題")
        print(f"  未作答: {unanswered} 題")
        print(f"{'='*60}\n")

    def submit_exam_with_confirmation(self, auto_submit: bool = False) -> bool:
        """
        提交考卷（含使用者確認）

        Args:
            auto_submit: 是否自動提交（不詢問使用者）

        Returns:
            是否成功提交
        """
        try:
            # 顯示答題統計
            self.show_answer_summary()

            # 使用者確認（除非設定自動提交）
            if not auto_submit:
                user_input = input("是否確認交卷？(y/n): ").lower().strip()
                if user_input != 'y':
                    print("[取消] 使用者取消交卷")
                    return False

            # 點擊交卷按鈕（使用 JavaScript 避免被遮擋）
            print("[執行] 點擊交卷按鈕...")
            submit_btn = self.find_element(self.SUBMIT_BUTTON)
            self.driver.execute_script("arguments[0].click();", submit_btn)
            time.sleep(3)  # 等待浮動視窗出現

            # 確認浮動視窗（使用 JavaScript）
            print("[執行] 確認浮動視窗...")
            confirm_btn = self.find_element(self.CONFIRM_BUTTON)
            self.driver.execute_script("arguments[0].click();", confirm_btn)
            time.sleep(3)  # 等待提交完成

            print("[完成] ✓ 考卷已提交")
            return True

        except Exception as e:
            print(f"[錯誤] 提交考卷失敗: {str(e)}")
            return False

    def display_score_if_available(self, delay: float = 3.0):
        """
        顯示考試分數（如果有的話）

        Args:
            delay: 等待分數顯示的時間
        """
        try:
            time.sleep(delay)

            # 嘗試尋找分數元素（實際的定位器需要根據網站調整）
            # 這裡提供幾種常見的分數顯示方式
            score_locators = [
                (By.XPATH, "//*[contains(text(), '分數') or contains(text(), '成績')]"),
                (By.CLASS_NAME, "score"),
                (By.CLASS_NAME, "exam-result"),
            ]

            for locator in score_locators:
                try:
                    score_elem = self.driver.find_element(*locator)
                    score_text = score_elem.text
                    print(f"\n{'='*60}")
                    print(f"📝 考試結果")
                    print(f"{'='*60}")
                    print(f"  {score_text}")
                    print(f"{'='*60}\n")
                    return
                except NoSuchElementException:
                    continue

            print("[提示] 無法自動偵測分數，請手動確認考試結果")

        except Exception as e:
            print(f"[錯誤] 顯示分數失敗: {str(e)}")
