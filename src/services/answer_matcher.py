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
        question_bank: List[Question],
        web_options: Optional[List[str]] = None
    ) -> Optional[Tuple[Question, float]]:
        """
        尋找最佳匹配的題目（含選項比對）

        使用多層級匹配策略：
        1. 題目文字匹配（精確/包含/相似度）
        2. 選項內容匹配（若提供 web_options）
        3. 綜合評分（題目40% + 選項60%）

        Args:
            web_question_text: 網頁上的題目文字
            question_bank: 題庫列表
            web_options: 網頁上的選項文字列表（可選）

        Returns:
            (匹配的題目, 信心分數)，若無匹配則返回 None
        """
        if not web_question_text or not question_bank:
            return None

        web_norm = self.normalize_text(web_question_text)

        # 階段 1: 收集所有題目文字達到門檻的候選題目
        candidates = []

        for db_question in question_bank:
            db_norm = self.normalize_text(db_question.description_text)

            # 計算題目相似度
            if web_norm == db_norm:
                question_similarity = 1.0
            elif web_norm in db_norm or db_norm in web_norm:
                question_similarity = 0.95
            else:
                question_similarity = SequenceMatcher(None, web_norm, db_norm).ratio()

            # 只保留達到門檻的題目
            if question_similarity >= self.confidence_threshold:
                candidates.append((db_question, question_similarity))

        if not candidates:
            return None

        # 階段 2: 如果只有一個候選，直接返回
        if len(candidates) == 1:
            return candidates[0]

        # 階段 3: 有多個候選題目
        if web_options is None or len(web_options) == 0:
            # 沒有提供選項資訊，返回題目相似度最高的
            return max(candidates, key=lambda x: x[1])

        # 階段 4: 有多個候選且提供選項，計算綜合評分
        best_match = None
        best_combined_score = 0.0

        for db_question, question_sim in candidates:
            # 計算選項相似度
            option_sim = self._calculate_option_similarity(web_options, db_question.options)

            # 綜合評分 = 題目相似度 * 0.4 + 選項相似度 * 0.6
            # （選項權重更高，因為題目相同時選項是關鍵）
            combined_score = question_sim * 0.4 + option_sim * 0.6

            if combined_score > best_combined_score:
                best_combined_score = combined_score
                best_match = db_question

        # 檢查綜合分數是否達到門檻
        if best_match and best_combined_score >= self.confidence_threshold:
            return (best_match, best_combined_score)

        return None

    def _calculate_option_similarity(
        self,
        web_options: List[str],
        db_options: List[Option]
    ) -> float:
        """
        計算選項相似度

        比對網頁選項與題庫選項的匹配程度

        Args:
            web_options: 網頁上的選項文字列表
            db_options: 題庫中的選項列表

        Returns:
            選項相似度分數 (0.0 ~ 1.0)
        """
        if not web_options or not db_options:
            return 0.0

        # 標準化所有選項
        web_opts_norm = [self.normalize_text(opt) for opt in web_options]
        db_opts_norm = [self.normalize_text(opt.content_text) for opt in db_options]

        total_similarity = 0.0
        matched_count = 0

        # 計算每個網頁選項與題庫選項的最佳匹配
        for web_opt in web_opts_norm:
            best_sim = 0.0

            for db_opt in db_opts_norm:
                # 精確匹配
                if web_opt == db_opt:
                    sim = 1.0
                # 包含匹配
                elif web_opt in db_opt or db_opt in web_opt:
                    sim = 0.9
                # 相似度匹配
                else:
                    sim = SequenceMatcher(None, web_opt, db_opt).ratio()

                if sim > best_sim:
                    best_sim = sim

            total_similarity += best_sim

            # 如果匹配度 >= 80%，視為匹配成功
            if best_sim >= 0.8:
                matched_count += 1

        # 計算平均相似度
        avg_similarity = total_similarity / len(web_options) if web_options else 0.0

        # 返回平均相似度
        return avg_similarity

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
