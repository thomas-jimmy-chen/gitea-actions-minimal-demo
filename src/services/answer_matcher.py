# Answer Matcher Engine
# Created: 2025-11-15
#
# 答案匹配引擎 - 負責匹配考試題目與題庫答案

import re
from typing import List, Optional, Tuple
from difflib import SequenceMatcher
from ..models.question import Question, Option


class AnswerMatcher:
    """答案匹配引擎"""

    def __init__(self, confidence_threshold: float = 0.85):
        """
        初始化匹配引擎

        Args:
            confidence_threshold: 匹配信心門檻（0.0 ~ 1.0），預設 0.85
        """
        self.confidence_threshold = confidence_threshold

    def normalize_text(self, text: str) -> str:
        """
        標準化文字

        處理步驟：
        1. 移除所有 HTML 標籤
        2. 移除所有空白字元
        3. 全形標點轉半形
        4. 轉小寫

        Args:
            text: 原始文字

        Returns:
            標準化後的文字
        """
        if not text:
            return ""

        # 1. 移除 HTML 標籤
        text = re.sub(r'<[^>]+>', '', text)

        # 2. 移除所有空白字元（包括空格、換行、tab）
        text = re.sub(r'\s+', '', text)

        # 3. 全形標點符號轉半形
        replacements = {
            '？': '?',
            '。': '.',
            '，': ',',
            '；': ';',
            '：': ':',
            '！': '!',
            '（': '(',
            '）': ')',
            '「': '"',
            '」': '"',
            '『': "'",
            '』': "'",
            '【': '[',
            '】': ']',
        }
        for full, half in replacements.items():
            text = text.replace(full, half)

        # 4. 轉小寫（僅對英文字母）
        text = text.lower()

        return text

    def find_best_match(
        self,
        web_question_text: str,
        question_bank: List[Question]
    ) -> Optional[Tuple[Question, float]]:
        """
        尋找最佳匹配的題目

        使用多層級匹配策略：
        1. 精確匹配（最快）
        2. 包含匹配（處理編號前綴）
        3. 相似度匹配（模糊匹配）

        Args:
            web_question_text: 網頁上的題目文字
            question_bank: 題庫列表

        Returns:
            (匹配的題目, 信心分數)，若無匹配則返回 None
        """
        if not web_question_text or not question_bank:
            return None

        web_norm = self.normalize_text(web_question_text)
        best_match = None
        best_score = 0.0

        for db_question in question_bank:
            db_norm = self.normalize_text(db_question.description_text)

            # 策略 1: 精確匹配
            if web_norm == db_norm:
                return (db_question, 1.0)

            # 策略 2: 包含匹配（處理題號前綴，例如 "1. 題目" vs "題目"）
            if web_norm in db_norm or db_norm in web_norm:
                score = 0.95  # 包含匹配給 95% 信心
                if score > best_score:
                    best_match = db_question
                    best_score = score

            # 策略 3: 相似度匹配
            similarity = SequenceMatcher(None, web_norm, db_norm).ratio()
            if similarity > best_score:
                best_match = db_question
                best_score = similarity

        # 檢查是否達到信心門檻
        if best_match and best_score >= self.confidence_threshold:
            return (best_match, best_score)

        return None

    def match_correct_options(
        self,
        web_options: List[str],
        db_question: Question
    ) -> List[int]:
        """
        匹配正確選項的索引

        Args:
            web_options: 網頁上的選項文字列表
            db_question: 題庫中匹配到的題目

        Returns:
            正確選項的索引列表（0-based）
        """
        correct_indices = []
        db_options = db_question.options

        # 取得題庫中的正確答案
        for db_opt in db_options:
            if not db_opt.is_answer:
                continue

            db_opt_norm = self.normalize_text(db_opt.content_text)

            # 在網頁選項中尋找匹配
            for idx, web_opt_text in enumerate(web_options):
                web_opt_norm = self.normalize_text(web_opt_text)

                # 精確匹配或包含匹配
                if db_opt_norm == web_opt_norm or db_opt_norm in web_opt_norm or web_opt_norm in db_opt_norm:
                    if idx not in correct_indices:
                        correct_indices.append(idx)
                    break

        return sorted(correct_indices)

    def validate_match(
        self,
        web_question_text: str,
        web_options: List[str],
        db_question: Question,
        correct_indices: List[int]
    ) -> bool:
        """
        驗證匹配結果的合理性

        檢查項目：
        1. 題型是否一致（單選/複選）
        2. 選項數量是否接近
        3. 正確答案數量是否符合題型

        Args:
            web_question_text: 網頁題目文字
            web_options: 網頁選項列表
            db_question: 匹配到的題庫題目
            correct_indices: 匹配到的正確選項索引

        Returns:
            驗證是否通過
        """
        # 檢查 1: 選項數量是否接近（允許 ±1 的差異）
        web_opt_count = len(web_options)
        db_opt_count = len(db_question.options)
        if abs(web_opt_count - db_opt_count) > 1:
            print(f"[警告] 選項數量差異過大: 網頁 {web_opt_count} vs 題庫 {db_opt_count}")
            return False

        # 檢查 2: 正確答案數量是否符合題型
        if db_question.question_type == "single_selection":
            if len(correct_indices) != 1:
                print(f"[警告] 單選題應有1個正確答案，實際: {len(correct_indices)}")
                return False
        elif db_question.question_type == "multiple_selection":
            if len(correct_indices) < 1:
                print(f"[警告] 複選題至少1個正確答案，實際: {len(correct_indices)}")
                return False

        # 檢查 3: 索引是否在有效範圍內
        for idx in correct_indices:
            if idx < 0 or idx >= web_opt_count:
                print(f"[錯誤] 選項索引超出範圍: {idx}")
                return False

        return True

    def get_match_info(
        self,
        web_question_text: str,
        db_question: Question,
        confidence: float
    ) -> str:
        """
        取得匹配資訊（用於日誌輸出）

        Args:
            web_question_text: 網頁題目
            db_question: 匹配到的題庫題目
            confidence: 匹配信心分數

        Returns:
            格式化的匹配資訊
        """
        info = []
        info.append(f"網頁題目: {web_question_text[:60]}...")
        info.append(f"題庫題目: {db_question.description_text[:60]}...")
        info.append(f"匹配信心: {confidence:.2%}")
        info.append(f"題型: {db_question.question_type}")
        info.append(f"分類: {db_question.category}")
        return "\n".join(info)
