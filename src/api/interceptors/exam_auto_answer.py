#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
ExamAutoAnswerInterceptor - 考試自動答題攔截器
攔截考試 API 請求，自動匹配題庫並注入正確答案
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from mitmproxy import http


class ExamAutoAnswerInterceptor:
    """
    考試自動答題攔截器

    工作流程:
    1. 攔截 GET /api/exams/{id}/distribute - 提取考題並匹配題庫
    2. 攔截 POST /api/exams/{id}/submissions - 注入正確答案

    優勢:
    - 跳過 Selenium 逐題點擊 (節省 50-100 秒)
    - 保留 Web 流程的真實性 (進入考試頁面獲取 exam_paper_instance_id)
    - 4.5x 速度提升 (180秒 → 40秒)
    """

    def __init__(self, question_bank_service, answer_matcher, enable: bool = True):
        """
        初始化攔截器

        Args:
            question_bank_service: QuestionBankService 實例
            answer_matcher: AnswerMatcher 實例
            enable: 是否啟用攔截器
        """
        self.question_bank_service = question_bank_service
        self.answer_matcher = answer_matcher
        self.enable = enable

        # 存儲考試資料 {exam_id: exam_data}
        self.exam_data_store: Dict[str, Dict] = {}

        # 統計資訊
        self.stats = {
            'intercepted_distributes': 0,
            'intercepted_submissions': 0,
            'total_questions': 0,
            'matched_questions': 0,
            'unmatched_questions': 0
        }

        print(f"[ExamAutoAnswer] 攔截器已初始化 (enable={self.enable})")

    def response(self, flow: http.HTTPFlow):
        """
        攔截 HTTP 響應

        處理 GET /api/exams/{id}/distribute 的響應

        Args:
            flow: mitmproxy 的 HTTP 流物件
        """
        # 攔截 GET /api/exams/{id}/distribute
        if '/api/exams/' in flow.request.url and '/distribute' in flow.request.url:
            if flow.request.method == 'GET':
                if not self.enable:
                    return
                print(f"[ExamAutoAnswer] 攔截到 distribute 響應")
                self._handle_distribute_response(flow)

    def request(self, flow: http.HTTPFlow):
        """
        攔截 HTTP 請求

        處理 POST /api/exams/{id}/submissions 的請求

        Args:
            flow: mitmproxy 的 HTTP 流物件
        """
        # 攔截 POST /api/exams/{id}/submissions
        if '/api/exams/' in flow.request.url and '/submissions' in flow.request.url:
            if flow.request.method == 'POST':
                if not self.enable:
                    return
                print(f"[ExamAutoAnswer] 攔截到 submissions 請求")
                self._handle_submission_request(flow)

    def _handle_distribute_response(self, flow: http.HTTPFlow):
        """
        處理 distribute API 的響應

        從響應中提取考題，匹配題庫，並存儲結果

        Args:
            flow: mitmproxy 的 HTTP 流物件
        """
        try:
            # 解析響應 JSON
            response_text = flow.response.get_text(strict=False)
            if not response_text:
                return

            response_data = json.loads(response_text)

            # 提取 exam_id
            exam_id = self._extract_exam_id(flow.request.url)
            if not exam_id:
                print("[ExamInterceptor] 無法提取 exam_id")
                return

            # 提取考題列表
            subjects = response_data.get('subjects', [])
            if not subjects:
                print(f"[ExamInterceptor] 考試 {exam_id} 無題目")
                return

            print(f"\n[ExamInterceptor] 攔截到考試 {exam_id} (共 {len(subjects)} 題)")
            self.stats['intercepted_distributes'] += 1
            self.stats['total_questions'] += len(subjects)

            # 匹配題庫
            matched_answers = self._match_questions(subjects)

            # 存儲匹配結果（包含 submission 需要的所有欄位）
            self.exam_data_store[exam_id] = {
                'exam_paper_instance_id': response_data.get('exam_paper_instance_id'),
                'exam_submission_id': response_data.get('exam_submission_id'),
                'subjects': subjects,
                'matched_answers': matched_answers,
                'original_response': response_data
            }

            print(f"[ExamInterceptor] 匹配完成: {len(matched_answers)}/{len(subjects)} 題")
            print(f"[ExamInterceptor] 匹配率: {len(matched_answers)/len(subjects)*100:.1f}%\n")

        except json.JSONDecodeError as e:
            print(f"[ExamInterceptor] JSON 解析錯誤: {e}")
        except Exception as e:
            print(f"[ExamInterceptor] distribute 處理失敗: {e}")

    def _handle_submission_request(self, flow: http.HTTPFlow):
        """
        處理 submission API 的請求

        修改請求 payload，注入正確答案

        Args:
            flow: mitmproxy 的 HTTP 流物件
        """
        try:
            # 提取 exam_id
            exam_id = self._extract_exam_id(flow.request.url)
            if not exam_id:
                print("[ExamInterceptor] submission: 無法提取 exam_id")
                return

            # 檢查是否有匹配資料
            if exam_id not in self.exam_data_store:
                print(f"[ExamInterceptor] submission: 找不到考試 {exam_id} 的匹配資料")
                return

            exam_data = self.exam_data_store[exam_id]
            matched_answers = exam_data['matched_answers']

            if not matched_answers:
                print(f"[ExamInterceptor] submission: 考試 {exam_id} 無匹配答案")
                return

            # 解析請求 payload
            payload = json.loads(flow.request.get_text(strict=False) or "{}")

            # 修改 subjects
            if 'subjects' in payload:
                print(f"\n[ExamInterceptor] 正在注入答案到考試 {exam_id}...")
                modified_count = self._inject_answers(payload['subjects'], matched_answers, payload)

                # 更新請求內容
                flow.request.set_text(json.dumps(payload))

                self.stats['intercepted_submissions'] += 1
                print(f"[ExamInterceptor] 已注入 {modified_count} 題答案")
                print(f"[ExamInterceptor] submission 攔截完成\n")

        except json.JSONDecodeError as e:
            print(f"[ExamInterceptor] submission JSON 解析錯誤: {e}")
        except Exception as e:
            print(f"[ExamInterceptor] submission 處理失敗: {e}")

    def _extract_exam_id(self, url: str) -> Optional[str]:
        """
        從 URL 提取 exam_id

        例如: /api/exams/48/distribute → "48"

        Args:
            url: API URL

        Returns:
            exam_id 或 None
        """
        match = re.search(r'/api/exams/(\d+)/', url)
        if match:
            return match.group(1)
        return None

    def _match_questions(self, subjects: List[Dict]) -> Dict[str, Dict]:
        """
        匹配考題與題庫

        Args:
            subjects: API 返回的題目列表

        Returns:
            {subject_id: {
                'correct_option_ids': [id1, id2, ...],
                'confidence': 0.95,
                'db_question': Question實例
            }}
        """
        matched_answers = {}
        question_bank = self.question_bank_service.get_all_questions()

        if not question_bank:
            print("[ExamInterceptor] 題庫為空，無法匹配")
            return matched_answers

        for subject in subjects:
            subject_id = str(subject.get('id'))
            description = subject.get('description', '')
            options = subject.get('options', [])
            updated_at = subject.get('updated_at', '')  # 提取 updated_at

            # 清理 HTML
            question_text = self._clean_html(description)

            # 提取選項文字
            option_texts = [self._clean_html(opt.get('content', '')) for opt in options]

            # 匹配題庫
            match_result = self.answer_matcher.find_best_match(
                question_text,
                question_bank,
                option_texts
            )

            if match_result:
                db_question, confidence = match_result

                # 匹配正確選項
                correct_indices = self.answer_matcher.match_correct_options(option_texts, db_question)

                if correct_indices:
                    # 將索引轉換為 option_id
                    correct_option_ids = [options[idx]['id'] for idx in correct_indices]

                    matched_answers[subject_id] = {
                        'correct_option_ids': correct_option_ids,
                        'subject_updated_at': updated_at,  # 存儲 updated_at
                        'confidence': confidence,
                        'db_question': db_question
                    }

                    self.stats['matched_questions'] += 1
                    print(f"  ✓ 題目 {subject_id}: 匹配成功 ({confidence:.2%})")
                else:
                    self.stats['unmatched_questions'] += 1
                    print(f"  ✗ 題目 {subject_id}: 無法匹配選項")
            else:
                self.stats['unmatched_questions'] += 1
                print(f"  ✗ 題目 {subject_id}: 無法匹配")

        return matched_answers

    def _inject_answers(self, subjects: List[Dict], matched_answers: Dict[str, Dict], payload: Dict) -> int:
        """
        注入正確答案到 submission payload

        Args:
            subjects: submission 的 subjects 列表
            matched_answers: 匹配的答案字典
            payload: 完整的 submission payload（用於更新 progress）

        Returns:
            注入的題目數量
        """
        modified_count = 0
        total_subjects = len(subjects)

        for subject in subjects:
            subject_id = str(subject.get('subject_id'))

            if subject_id in matched_answers:
                match_data = matched_answers[subject_id]
                correct_option_ids = match_data['correct_option_ids']

                # ✅ 修正：使用 answer_option_ids（而非 selected_option_ids）
                subject['answer_option_ids'] = correct_option_ids

                # ✅ 確保包含 subject_updated_at（如果原本沒有）
                if 'subject_updated_at' not in subject and 'subject_updated_at' in match_data:
                    subject['subject_updated_at'] = match_data['subject_updated_at']

                modified_count += 1
                print(f"  ✓ 注入題目 {subject_id}: {correct_option_ids}")

        # ✅ 更新 progress 欄位
        if 'progress' in payload:
            payload['progress']['answered_num'] = modified_count
            payload['progress']['total_subjects'] = total_subjects
            print(f"  ✓ 更新 progress: {modified_count}/{total_subjects} 題")

        return modified_count

    def _clean_html(self, html_text: str) -> str:
        """
        清理 HTML 標籤

        Args:
            html_text: HTML 文字

        Returns:
            純文字
        """
        if not html_text:
            return ""

        # 移除 <p> 標籤
        text = re.sub(r'<p>|</p>', '', html_text)
        # 移除所有 HTML 標籤
        text = re.sub(r'<[^>]+>', '', html_text)
        # 移除多餘空白
        text = ' '.join(text.split())
        return text.strip()

    def get_stats(self) -> Dict:
        """取得統計資訊"""
        return self.stats.copy()

    def reset_stats(self):
        """重置統計資訊"""
        self.stats = {
            'intercepted_distributes': 0,
            'intercepted_submissions': 0,
            'total_questions': 0,
            'matched_questions': 0,
            'unmatched_questions': 0
        }

    def clear_exam_data(self):
        """清除考試資料"""
        self.exam_data_store.clear()

    def __repr__(self) -> str:
        status = 'enabled' if self.enable else 'disabled'
        return f"ExamAutoAnswerInterceptor(status={status}, exams={len(self.exam_data_store)})"
