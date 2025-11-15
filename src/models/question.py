# Question and Option Data Models
# Created: 2025-11-15
#
# 題目與選項的資料結構定義

from typing import List, Optional
from dataclasses import dataclass


@dataclass
class Option:
    """選項資料模型"""
    content: str           # 選項內容（HTML）
    content_text: str      # 選項內容（純文字）
    is_answer: bool        # 是否為正確答案
    sort: int              # 排序
    option_id: Optional[int] = None  # 選項ID（來自題庫）

    def __repr__(self):
        answer_mark = "✓" if self.is_answer else " "
        return f"[{answer_mark}] {self.content_text[:50]}"


@dataclass
class Question:
    """題目資料模型"""
    description: str           # 題目內容（HTML）
    description_text: str      # 題目內容（純文字）
    question_type: str         # 題型：single_selection / multiple_selection
    options: List[Option]      # 選項列表
    difficulty_level: Optional[str] = None  # 難度
    question_id: Optional[int] = None       # 題目ID（來自題庫）
    category: Optional[str] = None          # 分類
    answer_explanation: Optional[str] = None  # 答案說明

    def get_correct_options(self) -> List[Option]:
        """取得正確選項"""
        return [opt for opt in self.options if opt.is_answer]

    def get_correct_indices(self) -> List[int]:
        """取得正確選項的索引"""
        return [i for i, opt in enumerate(self.options) if opt.is_answer]

    def __repr__(self):
        type_display = "單選" if self.question_type == "single_selection" else "複選"
        return f"[{type_display}] {self.description_text[:60]}... ({len(self.options)}個選項)"
