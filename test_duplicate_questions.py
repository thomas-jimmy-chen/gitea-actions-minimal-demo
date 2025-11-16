#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
單元測試: 驗證重複題目的選項比對邏輯

測試場景: 題庫中有兩個題目文字相似但選項不同的題目
- ID: 191 - 題目: "下列敘述何者正確" (無問號)
- ID: 187 - 題目: "下列敘述何者正確?" (有問號)

目標: 驗證新邏輯能否根據選項內容正確區分這兩個題目
"""

import json
import sys
import os
from pathlib import Path

# 設定控制台編碼為 UTF-8（Windows）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 加入專案路徑
sys.path.insert(0, str(Path(__file__).parent))

from src.services.answer_matcher import AnswerMatcher
from src.models.question import Question, Option
from bs4 import BeautifulSoup


class MockConfig:
    """模擬配置物件（測試用）"""
    def get(self, key, default=None):
        return default

    def get_bool(self, key, default=False):
        return default


class SimplifiedQuestionBank:
    """簡化的題庫載入器（測試用）"""

    def __init__(self):
        self.questions = []

    def load_from_file(self, file_path):
        """從檔案載入題庫"""
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)

            # 解析分頁結構
            for page in data:
                if 'subjects' in page:
                    for subject in page['subjects']:
                        question = self._parse_question(subject)
                        if question:
                            self.questions.append(question)

            return len(self.questions)

        except Exception as e:
            print(f"[錯誤] 載入題庫失敗: {str(e)}")
            return 0

    def _parse_question(self, subject_data):
        """解析題目"""
        try:
            description_html = subject_data.get('description', '')
            description_text = self._clean_html(description_html)
            question_type = subject_data.get('type', 'single_selection')
            question_id = subject_data.get('id')

            # 解析選項
            options = []
            for opt_data in subject_data.get('options', []):
                option = Option(
                    content=opt_data.get('content', ''),
                    content_text=self._clean_html(opt_data.get('content', '')),
                    is_answer=opt_data.get('is_answer', False),
                    sort=opt_data.get('sort', 0),
                    option_id=opt_data.get('id')
                )
                options.append(option)

            # 建立 Question
            question = Question(
                description=description_html,
                description_text=description_text,
                question_type=question_type,
                options=options,
                question_id=question_id,
                category="test"
            )

            return question

        except Exception as e:
            print(f"[錯誤] 解析題目失敗: {str(e)}")
            return None

    @staticmethod
    def _clean_html(html_text):
        """清理 HTML"""
        if not html_text:
            return ""
        try:
            soup = BeautifulSoup(html_text, 'html.parser')
            text = soup.get_text()
            text = ' '.join(text.split())
            return text.strip()
        except Exception:
            import re
            text = re.sub(r'<[^>]+>', '', html_text)
            text = ' '.join(text.split())
            return text.strip()


class DuplicateQuestionTester:
    """重複題目測試器"""

    def __init__(self):
        self.question_bank = SimplifiedQuestionBank()
        self.answer_matcher = AnswerMatcher(confidence_threshold=0.85)

        # 測試結果統計
        self.results = {
            'test_count': 0,
            'passed': 0,
            'failed': 0
        }

    def load_test_data(self):
        """載入測試題庫"""
        print("=" * 80)
        print("🔍 步驟 1: 載入題庫")
        print("=" * 80)

        # 載入壽險業務員題庫
        file_path = "郵政E大學114年題庫/壽險業務員在職訓練（30題）.json"
        print(f"📂 題庫檔案: {file_path}")

        question_count = self.question_bank.load_from_file(file_path)

        print(f"✅ 成功載入 {question_count} 題\n")
        return question_count > 0

    def find_duplicate_questions(self):
        """找出測試用的重複題目"""
        print("=" * 80)
        print("🔍 步驟 2: 定位重複題目")
        print("=" * 80)

        question_191 = None
        question_187 = None

        for q in self.question_bank.questions:
            if q.question_id == 191:
                question_191 = q
            elif q.question_id == 187:
                question_187 = q

        if question_191:
            print(f"\n✅ 找到題目 ID: 191")
            print(f"   題目文字: {question_191.description_text}")
            print(f"   選項數量: {len(question_191.options)}")
            print(f"   正確答案: {[i for i, opt in enumerate(question_191.options) if opt.is_answer]}")

        if question_187:
            print(f"\n✅ 找到題目 ID: 187")
            print(f"   題目文字: {question_187.description_text}")
            print(f"   選項數量: {len(question_187.options)}")
            print(f"   正確答案: {[i for i, opt in enumerate(question_187.options) if opt.is_answer]}")

        if not question_191 or not question_187:
            print("\n❌ 錯誤: 未找到測試題目")
            return None, None

        print("\n" + "=" * 80)
        return question_191, question_187

    def test_scenario_1_match_191(self, q191, q187):
        """
        測試場景 1: 網頁題目匹配 ID:191 (無問號版本)
        """
        print("\n" + "=" * 80)
        print("📝 測試場景 1: 網頁題目應匹配 ID:191")
        print("=" * 80)

        # 模擬網頁題目和選項（來自 ID:191）
        web_question = q191.description_text
        web_options = [opt.content_text for opt in q191.options]

        print(f"\n🌐 模擬網頁題目:")
        print(f"   題目: {web_question}")
        print(f"   選項數: {len(web_options)}")
        for i, opt in enumerate(web_options):
            print(f"   {chr(65+i)}. {opt[:50]}...")

        # 測試 1: 不傳選項（舊邏輯）
        print(f"\n--- 測試 1.1: 不傳選項（模擬舊邏輯） ---")
        result_without_options = self.answer_matcher.find_best_match(
            web_question,
            self.question_bank.questions,
            web_options=None  # 不傳選項
        )

        if result_without_options:
            matched_q, confidence = result_without_options
            print(f"✅ 匹配結果: ID {matched_q.question_id}")
            print(f"   信心度: {confidence:.2%}")
            if matched_q.question_id == 191:
                print(f"   ✅ 正確: 匹配到 ID:191")
            else:
                print(f"   ⚠️  可能不正確: 匹配到 ID:{matched_q.question_id}")
        else:
            print(f"❌ 無匹配結果")

        # 測試 2: 傳入選項（新邏輯）
        print(f"\n--- 測試 1.2: 傳入選項（新邏輯） ---")
        result_with_options = self.answer_matcher.find_best_match(
            web_question,
            self.question_bank.questions,
            web_options=web_options  # 傳入選項
        )

        if result_with_options:
            matched_q, confidence = result_with_options
            print(f"✅ 匹配結果: ID {matched_q.question_id}")
            print(f"   信心度: {confidence:.2%}")

            # 驗證結果
            self.results['test_count'] += 1
            if matched_q.question_id == 191:
                print(f"   ✅ 正確: 匹配到 ID:191")
                self.results['passed'] += 1
            else:
                print(f"   ❌ 錯誤: 應匹配 ID:191，實際匹配 ID:{matched_q.question_id}")
                self.results['failed'] += 1
        else:
            print(f"❌ 無匹配結果")
            self.results['test_count'] += 1
            self.results['failed'] += 1

    def test_scenario_2_match_187(self, q191, q187):
        """
        測試場景 2: 網頁題目匹配 ID:187 (有問號版本)
        """
        print("\n" + "=" * 80)
        print("📝 測試場景 2: 網頁題目應匹配 ID:187")
        print("=" * 80)

        # 模擬網頁題目和選項（來自 ID:187）
        web_question = q187.description_text
        web_options = [opt.content_text for opt in q187.options]

        print(f"\n🌐 模擬網頁題目:")
        print(f"   題目: {web_question}")
        print(f"   選項數: {len(web_options)}")
        for i, opt in enumerate(web_options):
            print(f"   {chr(65+i)}. {opt[:50]}...")

        # 測試 1: 不傳選項（舊邏輯）
        print(f"\n--- 測試 2.1: 不傳選項（模擬舊邏輯） ---")
        result_without_options = self.answer_matcher.find_best_match(
            web_question,
            self.question_bank.questions,
            web_options=None  # 不傳選項
        )

        if result_without_options:
            matched_q, confidence = result_without_options
            print(f"✅ 匹配結果: ID {matched_q.question_id}")
            print(f"   信心度: {confidence:.2%}")
            if matched_q.question_id == 187:
                print(f"   ✅ 正確: 匹配到 ID:187")
            else:
                print(f"   ⚠️  可能不正確: 匹配到 ID:{matched_q.question_id}")
        else:
            print(f"❌ 無匹配結果")

        # 測試 2: 傳入選項（新邏輯）
        print(f"\n--- 測試 2.2: 傳入選項（新邏輯） ---")
        result_with_options = self.answer_matcher.find_best_match(
            web_question,
            self.question_bank.questions,
            web_options=web_options  # 傳入選項
        )

        if result_with_options:
            matched_q, confidence = result_with_options
            print(f"✅ 匹配結果: ID {matched_q.question_id}")
            print(f"   信心度: {confidence:.2%}")

            # 驗證結果
            self.results['test_count'] += 1
            if matched_q.question_id == 187:
                print(f"   ✅ 正確: 匹配到 ID:187")
                self.results['passed'] += 1
            else:
                print(f"   ❌ 錯誤: 應匹配 ID:187，實際匹配 ID:{matched_q.question_id}")
                self.results['failed'] += 1
        else:
            print(f"❌ 無匹配結果")
            self.results['test_count'] += 1
            self.results['failed'] += 1

    def test_detailed_scoring(self, q191, q187):
        """
        詳細評分測試: 顯示匹配過程的詳細分數
        """
        print("\n" + "=" * 80)
        print("📊 詳細評分分析")
        print("=" * 80)

        # 模擬網頁題目來自 ID:187（有問號）
        web_question = q187.description_text
        web_options = [opt.content_text for opt in q187.options]

        print(f"\n🌐 測試題目: {web_question}")
        print(f"🌐 測試選項數: {len(web_options)}")

        # 手動計算兩個候選題目的分數
        print(f"\n--- 候選題目 1: ID:191 ---")
        q191_norm = self.answer_matcher.normalize_text(q191.description_text)
        web_norm = self.answer_matcher.normalize_text(web_question)

        from difflib import SequenceMatcher
        q191_question_sim = SequenceMatcher(None, web_norm, q191_norm).ratio()
        q191_option_sim = self.answer_matcher._calculate_option_similarity(
            web_options, q191.options
        )
        q191_combined = q191_question_sim * 0.4 + q191_option_sim * 0.6

        print(f"   題目相似度: {q191_question_sim:.2%}")
        print(f"   選項相似度: {q191_option_sim:.2%}")
        print(f"   綜合評分: {q191_combined:.2%} (題目40% + 選項60%)")

        print(f"\n--- 候選題目 2: ID:187 ---")
        q187_norm = self.answer_matcher.normalize_text(q187.description_text)
        q187_question_sim = SequenceMatcher(None, web_norm, q187_norm).ratio()
        q187_option_sim = self.answer_matcher._calculate_option_similarity(
            web_options, q187.options
        )
        q187_combined = q187_question_sim * 0.4 + q187_option_sim * 0.6

        print(f"   題目相似度: {q187_question_sim:.2%}")
        print(f"   選項相似度: {q187_option_sim:.2%}")
        print(f"   綜合評分: {q187_combined:.2%} (題目40% + 選項60%)")

        print(f"\n📊 評分對比:")
        print(f"   ID:191 綜合分: {q191_combined:.2%}")
        print(f"   ID:187 綜合分: {q187_combined:.2%}")

        if q187_combined > q191_combined:
            print(f"   ✅ 正確: ID:187 分數更高，應被選中")
        else:
            print(f"   ❌ 錯誤: ID:191 分數更高")

    def print_summary(self):
        """輸出測試總結"""
        print("\n" + "=" * 80)
        print("📊 測試總結")
        print("=" * 80)

        print(f"\n總測試數: {self.results['test_count']}")
        print(f"✅ 通過: {self.results['passed']}")
        print(f"❌ 失敗: {self.results['failed']}")

        if self.results['test_count'] > 0:
            pass_rate = self.results['passed'] / self.results['test_count'] * 100
            print(f"\n通過率: {pass_rate:.1f}%")

            if self.results['failed'] == 0:
                print("\n🎉 所有測試通過！選項比對邏輯運作正常！")
            else:
                print(f"\n⚠️  有 {self.results['failed']} 個測試失敗，請檢查邏輯")

        print("=" * 80 + "\n")

    def run_all_tests(self):
        """執行所有測試"""
        print("\n" + "=" * 80)
        print("🧪 重複題目選項比對邏輯測試")
        print("=" * 80)
        print("測試目標: 驗證新邏輯能否正確區分相似題目")
        print("=" * 80 + "\n")

        # 1. 載入題庫
        if not self.load_test_data():
            print("❌ 題庫載入失敗，測試終止")
            return

        # 2. 找出測試題目
        q191, q187 = self.find_duplicate_questions()
        if not q191 or not q187:
            print("❌ 未找到測試題目，測試終止")
            return

        # 3. 執行測試場景
        self.test_scenario_1_match_191(q191, q187)
        self.test_scenario_2_match_187(q191, q187)
        self.test_detailed_scoring(q191, q187)

        # 4. 輸出總結
        self.print_summary()


def main():
    """主程式入口"""
    tester = DuplicateQuestionTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
