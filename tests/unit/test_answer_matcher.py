# -*- coding: utf-8 -*-
"""
Tests for AnswerMatcher - 答案匹配引擎測試

測試覆蓋：
- 文字標準化 (normalize_text)
- 最佳匹配查找 (find_best_match)
- 選項相似度計算
- 正確選項匹配 (match_correct_options)
- 匹配驗證 (validate_match)
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.services.answer_matcher import AnswerMatcher
from src.models.question import Question, Option


class TestNormalizeText:
    """測試文字標準化功能"""

    def setup_method(self):
        """每個測試前初始化"""
        self.matcher = AnswerMatcher()

    def test_normalize_empty_string(self):
        """測試空字串"""
        assert self.matcher.normalize_text("") == ""
        assert self.matcher.normalize_text(None) == ""

    def test_normalize_removes_html_tags(self):
        """測試移除 HTML 標籤"""
        html = "<p>這是<strong>測試</strong>文字</p>"
        result = self.matcher.normalize_text(html)
        assert "<" not in result
        assert ">" not in result
        assert "這是測試文字" in result

    def test_normalize_removes_whitespace(self):
        """測試移除空白字元"""
        text = "這是  測試   文字"
        result = self.matcher.normalize_text(text)
        assert " " not in result

    def test_normalize_fullwidth_to_halfwidth(self):
        """測試全形標點轉半形"""
        text = "這是？測試。"
        result = self.matcher.normalize_text(text)
        assert "？" not in result
        assert "。" not in result
        assert "?" in result
        assert "." in result

    def test_normalize_lowercase(self):
        """測試英文轉小寫"""
        text = "ABC Test XYZ"
        result = self.matcher.normalize_text(text)
        assert "ABC" not in result
        assert "abc" in result.lower()


class TestFindBestMatch:
    """測試最佳匹配查找功能"""

    def setup_method(self):
        """每個測試前初始化"""
        self.matcher = AnswerMatcher(confidence_threshold=0.85)
        self.question_bank = self._create_question_bank()

    def _create_question_bank(self):
        """建立測試用題庫"""
        questions = []

        # 題目 1
        q1 = Question(
            description="<p>資通安全的三大要素不包含下列何者？</p>",
            description_text="資通安全的三大要素不包含下列何者？",
            question_type="single_selection",
            options=[
                Option("機密性", "機密性", False, 0),
                Option("完整性", "完整性", False, 1),
                Option("可用性", "可用性", False, 2),
                Option("便利性", "便利性", True, 3),
            ],
            category="資通安全"
        )
        questions.append(q1)

        # 題目 2
        q2 = Question(
            description="<p>下列何者為密碼設定的良好習慣？</p>",
            description_text="下列何者為密碼設定的良好習慣？",
            question_type="multiple_selection",
            options=[
                Option("定期更換密碼", "定期更換密碼", True, 0),
                Option("使用生日作為密碼", "使用生日作為密碼", False, 1),
                Option("使用複雜字元組合", "使用複雜字元組合", True, 2),
            ],
            category="資通安全"
        )
        questions.append(q2)

        return questions

    def test_find_exact_match(self):
        """測試精確匹配"""
        web_question = "資通安全的三大要素不包含下列何者？"
        result = self.matcher.find_best_match(web_question, self.question_bank)

        assert result is not None
        question, confidence = result
        assert confidence >= 0.95
        assert "便利性" in [opt.content_text for opt in question.get_correct_options()]

    def test_find_match_with_html(self):
        """測試帶 HTML 的題目匹配"""
        web_question = "<p>資通安全的三大要素不包含下列何者？</p>"
        result = self.matcher.find_best_match(web_question, self.question_bank)

        assert result is not None
        question, confidence = result
        assert confidence >= 0.85

    def test_no_match_for_unrelated_question(self):
        """測試不相關題目不匹配"""
        web_question = "這是一個完全不相關的題目，在題庫中找不到"
        result = self.matcher.find_best_match(web_question, self.question_bank)

        assert result is None

    def test_empty_inputs(self):
        """測試空輸入"""
        assert self.matcher.find_best_match("", self.question_bank) is None
        assert self.matcher.find_best_match("測試", []) is None


class TestMatchCorrectOptions:
    """測試正確選項匹配功能"""

    def setup_method(self):
        """每個測試前初始化"""
        self.matcher = AnswerMatcher()

    def test_match_single_correct_option(self):
        """測試單選題正確選項匹配"""
        db_question = Question(
            description="測試題目",
            description_text="測試題目",
            question_type="single_selection",
            options=[
                Option("選項A", "選項A", False, 0),
                Option("選項B", "選項B", True, 1),
                Option("選項C", "選項C", False, 2),
            ]
        )
        web_options = ["選項A", "選項B", "選項C"]

        result = self.matcher.match_correct_options(web_options, db_question)

        assert result == [1]  # 選項B 是正確答案，索引為 1

    def test_match_multiple_correct_options(self):
        """測試複選題正確選項匹配"""
        db_question = Question(
            description="測試題目",
            description_text="測試題目",
            question_type="multiple_selection",
            options=[
                Option("選項A", "選項A", True, 0),
                Option("選項B", "選項B", False, 1),
                Option("選項C", "選項C", True, 2),
            ]
        )
        web_options = ["選項A", "選項B", "選項C"]

        result = self.matcher.match_correct_options(web_options, db_question)

        assert sorted(result) == [0, 2]  # 選項A 和 C 是正確答案


class TestValidateMatch:
    """測試匹配驗證功能"""

    def setup_method(self):
        """每個測試前初始化"""
        self.matcher = AnswerMatcher()

    def test_validate_valid_single_selection(self):
        """測試有效的單選題驗證"""
        db_question = Question(
            description="測試題目",
            description_text="測試題目",
            question_type="single_selection",
            options=[
                Option("A", "A", False, 0),
                Option("B", "B", True, 1),
                Option("C", "C", False, 2),
                Option("D", "D", False, 3),
            ]
        )
        web_options = ["A", "B", "C", "D"]
        correct_indices = [1]

        result = self.matcher.validate_match(
            "測試題目", web_options, db_question, correct_indices
        )

        assert result is True

    def test_validate_invalid_single_selection_multiple_answers(self):
        """測試單選題有多個答案（無效）"""
        db_question = Question(
            description="測試題目",
            description_text="測試題目",
            question_type="single_selection",
            options=[
                Option("A", "A", True, 0),
                Option("B", "B", True, 1),
            ]
        )
        web_options = ["A", "B"]
        correct_indices = [0, 1]  # 兩個答案對單選題無效

        result = self.matcher.validate_match(
            "測試題目", web_options, db_question, correct_indices
        )

        assert result is False

    def test_validate_option_count_mismatch(self):
        """測試選項數量差異過大"""
        db_question = Question(
            description="測試題目",
            description_text="測試題目",
            question_type="single_selection",
            options=[
                Option("A", "A", True, 0),
                Option("B", "B", False, 1),
            ]
        )
        web_options = ["A", "B", "C", "D", "E"]  # 5個選項，題庫只有2個
        correct_indices = [0]

        result = self.matcher.validate_match(
            "測試題目", web_options, db_question, correct_indices
        )

        assert result is False

    def test_validate_index_out_of_range(self):
        """測試索引超出範圍"""
        db_question = Question(
            description="測試題目",
            description_text="測試題目",
            question_type="single_selection",
            options=[
                Option("A", "A", True, 0),
                Option("B", "B", False, 1),
            ]
        )
        web_options = ["A", "B"]
        correct_indices = [5]  # 索引超出範圍

        result = self.matcher.validate_match(
            "測試題目", web_options, db_question, correct_indices
        )

        assert result is False


class TestConfidenceThreshold:
    """測試信心門檻功能"""

    def test_custom_threshold(self):
        """測試自定義信心門檻"""
        matcher = AnswerMatcher(confidence_threshold=0.95)
        assert matcher.confidence_threshold == 0.95

    def test_default_threshold(self):
        """測試預設信心門檻"""
        matcher = AnswerMatcher()
        assert matcher.confidence_threshold == 0.85
