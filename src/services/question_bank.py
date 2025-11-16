# Question Bank Service
# Created: 2025-11-15
#
# 題庫載入與查詢服務

import json
import os
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from ..models.question import Question, Option


class QuestionBankService:
    """題庫服務 - 負責載入和查詢題庫資料"""

    # 題庫檔案對應表（基於 program_name）
    QUESTION_BANK_MAPPING = {
        "高齡客戶投保權益保障(114年度)": "高齡投保（10題）.json",
        "資通安全學程課程(114年度)": "資通安全（30題）.json",
        "資通安全測驗(114年度)": "資通安全（30題）.json",
        "壽險業務員在職訓練學程課程及測驗(114年度)": "壽險業務員在職訓練（30題）.json",
        "金融服務業公平待客原則＆洗錢防制及打擊資恐教育訓練(114年度)": "銀行業金融友善服務（21題）.json",
        "預防執行職務遭受不法侵害(員工)(114年度)": "窗口線上測驗（390題）.json",
        "環境教育學程課程(綠色金融)(114年度)": "窗口線上測驗（390題）.json",
        # 可根據需要繼續添加
    }

    def __init__(self, config):
        """
        初始化題庫服務

        Args:
            config: ConfigLoader 實例
        """
        self.config = config
        self.question_bank_mode = config.get('question_bank_mode', 'total_bank')
        self.question_bank_path = config.get('question_bank_path', '郵政E大學114年題庫/總題庫.json')
        self.questions: List[Question] = []
        self.raw_data: Dict = {}

    def load_question_bank(self, program_name: Optional[str] = None) -> int:
        """
        載入題庫

        Args:
            program_name: 課程計畫名稱（用於選擇對應題庫）

        Returns:
            載入的題目數量
        """
        if self.question_bank_mode == 'total_bank':
            # 使用總題庫
            return self._load_total_bank()
        elif self.question_bank_mode == 'file_mapping':
            # 根據 program_name 選擇對應的題庫檔案
            return self._load_specific_bank(program_name)
        else:
            print(f"[錯誤] 未知的題庫模式: {self.question_bank_mode}")
            return 0

    def _load_total_bank(self) -> int:
        """載入總題庫（包含所有題目）"""
        try:
            file_path = self.question_bank_path
            print(f"[載入] 題庫檔案: {file_path}")

            if not os.path.exists(file_path):
                print(f"[錯誤] 題庫檔案不存在: {file_path}")
                return 0

            with open(file_path, 'r', encoding='utf-8-sig') as f:
                self.raw_data = json.load(f)

            # 解析所有分類的題目
            total_count = 0
            for category_name, category_data in self.raw_data.items():
                if isinstance(category_data, list):
                    # 處理分頁結構
                    for page_data in category_data:
                        if 'subjects' in page_data:
                            for subject in page_data['subjects']:
                                question = self._parse_question(subject, category_name)
                                if question:
                                    self.questions.append(question)
                                    total_count += 1

            print(f"[成功] 載入題庫: {total_count} 題")
            return total_count

        except Exception as e:
            print(f"[錯誤] 載入題庫失敗: {str(e)}")
            return 0

    def _load_specific_bank(self, program_name: str) -> int:
        """載入特定主題的題庫"""
        try:
            # 從對應表找到題庫檔案
            bank_file = self.QUESTION_BANK_MAPPING.get(program_name)
            if not bank_file:
                print(f"[警告] 未找到對應題庫: {program_name}，將使用總題庫")
                return self._load_total_bank()

            file_path = os.path.join("郵政E大學114年題庫", bank_file)
            print(f"[載入] 題庫檔案: {file_path}")

            if not os.path.exists(file_path):
                print(f"[錯誤] 題庫檔案不存在: {file_path}")
                return 0

            with open(file_path, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)

            # 解析題目（處理分頁結構）
            total_count = 0

            # 檢查是否為分頁結構
            if isinstance(data, list) and len(data) > 0:
                # 如果第一個元素有 'subjects' 字段，說明是分頁結構
                if isinstance(data[0], dict) and 'subjects' in data[0]:
                    # 分頁結構：[{"subjects": [...]}]
                    for page in data:
                        if 'subjects' in page:
                            for subject in page['subjects']:
                                question = self._parse_question(subject, program_name)
                                if question:
                                    self.questions.append(question)
                                    total_count += 1
                else:
                    # 直接題目數組：[{題目1}, {題目2}, ...]
                    for subject in data:
                        question = self._parse_question(subject, program_name)
                        if question:
                            self.questions.append(question)
                            total_count += 1

            print(f"[成功] 載入題庫: {total_count} 題")
            return total_count

        except Exception as e:
            print(f"[錯誤] 載入題庫失敗: {str(e)}")
            return 0

    def _parse_question(self, subject_data: Dict, category: str) -> Optional[Question]:
        """
        解析單一題目資料

        Args:
            subject_data: 題目原始資料
            category: 分類名稱

        Returns:
            Question 實例，若解析失敗則返回 None
        """
        try:
            # 提取題目資訊
            description_html = subject_data.get('description', '')
            description_text = self._clean_html(description_html)
            question_type = subject_data.get('type', 'single_selection')
            difficulty_level = subject_data.get('difficulty_level')
            question_id = subject_data.get('id')
            answer_explanation = subject_data.get('answer_explanation', '')

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

            # 建立 Question 實例
            question = Question(
                description=description_html,
                description_text=description_text,
                question_type=question_type,
                options=options,
                difficulty_level=difficulty_level,
                question_id=question_id,
                category=category,
                answer_explanation=answer_explanation
            )

            return question

        except Exception as e:
            print(f"[錯誤] 解析題目失敗: {str(e)}")
            return None

    @staticmethod
    def _clean_html(html_text: str) -> str:
        """
        清理 HTML 標籤，提取純文字

        Args:
            html_text: HTML 文字

        Returns:
            純文字
        """
        if not html_text:
            return ""

        try:
            soup = BeautifulSoup(html_text, 'html.parser')
            text = soup.get_text()
            # 移除多餘的空白
            text = ' '.join(text.split())
            return text.strip()
        except Exception:
            # 如果 BeautifulSoup 解析失敗，使用簡單的正則替換
            import re
            text = re.sub(r'<[^>]+>', '', html_text)
            text = ' '.join(text.split())
            return text.strip()

    def get_all_questions(self) -> List[Question]:
        """取得所有題目"""
        return self.questions

    def find_question_by_text(self, question_text: str) -> Optional[Question]:
        """
        根據題目文字尋找題目（精確匹配）

        Args:
            question_text: 題目文字

        Returns:
            找到的 Question，若無則返回 None
        """
        for question in self.questions:
            if question.description_text == question_text:
                return question
        return None

    def get_question_count(self) -> int:
        """取得題目總數"""
        return len(self.questions)
