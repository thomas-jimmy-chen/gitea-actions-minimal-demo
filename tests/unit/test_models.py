# -*- coding: utf-8 -*-
"""
Tests for Question and Option Models - 題目與選項資料模型測試

測試覆蓋：
- Option dataclass
- Question dataclass
- get_correct_options
- get_correct_indices
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.models.question import Question, Option


class TestOption:
    """測試 Option 資料模型"""

    def test_option_creation(self):
        """測試選項建立"""
        option = Option(
            content="<p>選項A</p>",
            content_text="選項A",
            is_answer=True,
            sort=0,
            option_id=1001
        )

        assert option.content == "<p>選項A</p>"
        assert option.content_text == "選項A"
        assert option.is_answer is True
        assert option.sort == 0
        assert option.option_id == 1001

    def test_option_default_id(self):
        """測試選項預設 ID"""
        option = Option(
            content="選項",
            content_text="選項",
            is_answer=False,
            sort=0
        )

        assert option.option_id is None

    def test_option_repr_correct(self):
        """測試正確選項的字串表示"""
        option = Option(
            content="正確答案",
            content_text="正確答案",
            is_answer=True,
            sort=0
        )

        result = repr(option)
        assert "✓" in result
        assert "正確答案" in result

    def test_option_repr_incorrect(self):
        """測試錯誤選項的字串表示"""
        option = Option(
            content="錯誤答案",
            content_text="錯誤答案",
            is_answer=False,
            sort=0
        )

        result = repr(option)
        assert "✓" not in result


class TestQuestion:
    """測試 Question 資料模型"""

    def test_question_creation(self):
        """測試題目建立"""
        options = [
            Option("A", "A", False, 0),
            Option("B", "B", True, 1),
            Option("C", "C", False, 2),
        ]

        question = Question(
            description="<p>這是題目？</p>",
            description_text="這是題目？",
            question_type="single_selection",
            options=options,
            difficulty_level="easy",
            question_id=100,
            category="測試分類"
        )

        assert question.description == "<p>這是題目？</p>"
        assert question.description_text == "這是題目？"
        assert question.question_type == "single_selection"
        assert len(question.options) == 3
        assert question.difficulty_level == "easy"
        assert question.question_id == 100
        assert question.category == "測試分類"

    def test_question_default_values(self):
        """測試題目預設值"""
        question = Question(
            description="題目",
            description_text="題目",
            question_type="single_selection",
            options=[]
        )

        assert question.difficulty_level is None
        assert question.question_id is None
        assert question.category is None
        assert question.answer_explanation is None

    def test_get_correct_options_single(self):
        """測試取得單選題正確選項"""
        options = [
            Option("A", "A", False, 0),
            Option("B", "B", True, 1),
            Option("C", "C", False, 2),
        ]

        question = Question(
            description="題目",
            description_text="題目",
            question_type="single_selection",
            options=options
        )

        correct = question.get_correct_options()

        assert len(correct) == 1
        assert correct[0].content_text == "B"

    def test_get_correct_options_multiple(self):
        """測試取得複選題正確選項"""
        options = [
            Option("A", "A", True, 0),
            Option("B", "B", False, 1),
            Option("C", "C", True, 2),
            Option("D", "D", False, 3),
        ]

        question = Question(
            description="題目",
            description_text="題目",
            question_type="multiple_selection",
            options=options
        )

        correct = question.get_correct_options()

        assert len(correct) == 2
        assert correct[0].content_text == "A"
        assert correct[1].content_text == "C"

    def test_get_correct_options_none(self):
        """測試沒有正確選項"""
        options = [
            Option("A", "A", False, 0),
            Option("B", "B", False, 1),
        ]

        question = Question(
            description="題目",
            description_text="題目",
            question_type="single_selection",
            options=options
        )

        correct = question.get_correct_options()

        assert len(correct) == 0

    def test_get_correct_indices_single(self):
        """測試取得單選題正確選項索引"""
        options = [
            Option("A", "A", False, 0),
            Option("B", "B", True, 1),
            Option("C", "C", False, 2),
        ]

        question = Question(
            description="題目",
            description_text="題目",
            question_type="single_selection",
            options=options
        )

        indices = question.get_correct_indices()

        assert indices == [1]

    def test_get_correct_indices_multiple(self):
        """測試取得複選題正確選項索引"""
        options = [
            Option("A", "A", True, 0),
            Option("B", "B", False, 1),
            Option("C", "C", True, 2),
            Option("D", "D", True, 3),
        ]

        question = Question(
            description="題目",
            description_text="題目",
            question_type="multiple_selection",
            options=options
        )

        indices = question.get_correct_indices()

        assert indices == [0, 2, 3]

    def test_question_repr_single_selection(self):
        """測試單選題字串表示"""
        options = [Option("A", "A", True, 0)]

        question = Question(
            description="這是一個很長的題目，需要被截斷顯示",
            description_text="這是一個很長的題目，需要被截斷顯示",
            question_type="single_selection",
            options=options
        )

        result = repr(question)

        assert "[單選]" in result
        assert "1個選項" in result

    def test_question_repr_multiple_selection(self):
        """測試複選題字串表示"""
        options = [
            Option("A", "A", True, 0),
            Option("B", "B", True, 1),
        ]

        question = Question(
            description="題目",
            description_text="題目",
            question_type="multiple_selection",
            options=options
        )

        result = repr(question)

        assert "[複選]" in result
        assert "2個選項" in result
