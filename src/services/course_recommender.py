# Course Recommender Service
# Created: 2025-11-16
#
# 智能課程推薦服務 - 掃描「修習中」課程並比對已配置的課程

import json
import os
import time
import atexit
from typing import List, Dict, Optional
from difflib import SequenceMatcher
from ..core.config_loader import ConfigLoader
from ..core.driver_manager import DriverManager
from ..pages.login_page import LoginPage
from ..pages.course_list_page import CourseListPage


class CourseRecommender:
    """智能課程推薦服務"""

    # 臨時檔案路徑（程式結束時自動刪除）
    TEMP_RECOMMENDATIONS_FILE = "data/temp_recommendations.json"

    def __init__(self, config: ConfigLoader, driver_manager: DriverManager, cookie_manager=None):
        """
        初始化推薦服務

        Args:
            config: 配置載入器
            driver_manager: WebDriver 管理器
            cookie_manager: Cookie 管理器（可選）
        """
        self.config = config
        self.driver_manager = driver_manager
        self.driver = driver_manager.get_driver()
        self.cookie_manager = cookie_manager
        self.login_page = LoginPage(self.driver, cookie_manager)
        self.course_list_page = CourseListPage(self.driver)

        # 註冊程式結束時的清理函數
        atexit.register(self._cleanup_temp_files)

    def _cleanup_temp_files(self):
        """清理臨時檔案（程式結束時自動執行）"""
        if os.path.exists(self.TEMP_RECOMMENDATIONS_FILE):
            try:
                os.remove(self.TEMP_RECOMMENDATIONS_FILE)
                print(f'[清理] 已刪除臨時檔案: {self.TEMP_RECOMMENDATIONS_FILE}')
            except Exception as e:
                print(f'[警告] 無法刪除臨時檔案: {e}')

    def scan_available_courses(self) -> List[Dict]:
        """
        掃描「修習中」的所有課程計畫和子課程

        Returns:
            [
                {
                    "program_name": "課程計畫名稱",
                    "courses": [{"name": "課程名稱", "type": "course"}, ...],
                    "exams": [{"name": "考試名稱", "type": "exam"}, ...]
                }
            ]
        """
        try:
            print('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
            print('【智能推薦】正在分析您的可用課程...')
            print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')

            # 使用 auto_login 進行登入（參考課程學習場景的登入流程）
            print('[Step 1] 正在登入...')
            username = self.config.get('user_name')
            password = self.config.get('password')
            url = self.config.get('target_http')

            if not username or not password:
                print('[錯誤] 未配置登入資訊')
                return []

            self.login_page.auto_login(username, password, url)
            print('✅ 已登入')

            # 前往我的課程
            self.course_list_page.goto_my_courses()
            print('✅ 正在掃描「修習中」的課程...')

            # 獲取所有課程計畫
            programs = self.course_list_page.get_in_progress_programs()

            if not programs:
                print('[警告] 未找到任何「修習中」的課程計畫')
                return []

            print(f'  - 找到 {len(programs)} 個課程計畫')
            print('✅ 正在分析課程詳情...\n')

            # 掃描每個課程計畫的詳情
            available_courses = []
            for i, program in enumerate(programs, 1):
                program_name = program['name']
                print(f'  [{i}/{len(programs)}] {program_name[:50]}...')

                # 獲取課程和考試
                details = self.course_list_page.get_program_courses_and_exams(program_name)

                available_courses.append({
                    "program_name": program_name,
                    "courses": details.get('courses', []),
                    "exams": details.get('exams', [])
                })

            print('\n✅ 分析完成！\n')
            return available_courses

        except Exception as e:
            print(f'[錯誤] 掃描課程失敗: {e}')
            return []

    def load_config_courses(self) -> List[Dict]:
        """
        載入 courses.json 配置

        Returns:
            配置的課程列表
        """
        try:
            courses_file = "data/courses.json"
            if not os.path.exists(courses_file):
                print(f'[錯誤] 課程配置檔不存在: {courses_file}')
                return []

            with open(courses_file, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
                return data.get('courses', [])

        except Exception as e:
            print(f'[錯誤] 載入課程配置失敗: {e}')
            return []

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        正規化文字（去除空白、換行、特殊字元）

        Args:
            text: 原始文字

        Returns:
            正規化後的文字
        """
        if not text:
            return ""
        # 去除所有空白字元並轉換為小寫
        return ''.join(text.split()).lower()

    def match_course(self, web_name: str, config_courses: List[Dict]) -> Optional[Dict]:
        """
        比對課程名稱

        Args:
            web_name: 網頁上的課程名稱
            config_courses: 配置的課程列表

        Returns:
            匹配的配置，若無則返回 None
        """
        web_norm = self.normalize_text(web_name)

        for course in config_courses:
            # 獲取配置中的課程名稱（可能是 lesson_name 或 exam_name）
            config_name = course.get('lesson_name') or course.get('exam_name')
            if not config_name:
                continue

            config_norm = self.normalize_text(config_name)

            # 策略 1: 精確匹配
            if web_norm == config_norm:
                return course

            # 策略 2: 包含匹配
            if web_norm in config_norm or config_norm in web_norm:
                return course

            # 策略 3: 模糊匹配（相似度 >= 90%）
            similarity = SequenceMatcher(None, web_norm, config_norm).ratio()
            if similarity >= 0.90:
                return course

        return None

    def match_with_config(self, available_courses: List[Dict]) -> List[Dict]:
        """
        比對可用課程與配置

        Args:
            available_courses: 掃描得到的可用課程

        Returns:
            匹配的課程列表（僅包含已配置的課程）
        """
        config_courses = self.load_config_courses()
        if not config_courses:
            return []

        matched_courses = []

        for program in available_courses:
            program_name = program['program_name']

            # 比對一般課程
            for course in program.get('courses', []):
                matched_config = self.match_course(course['name'], config_courses)
                if matched_config:
                    matched_courses.append({
                        "program_name": program_name,
                        "item_name": course['name'],
                        "type": "course",
                        "matched": True,
                        "config": matched_config
                    })

            # 比對考試
            for exam in program.get('exams', []):
                matched_config = self.match_course(exam['name'], config_courses)
                if matched_config:
                    matched_courses.append({
                        "program_name": program_name,
                        "item_name": exam['name'],
                        "type": "exam",
                        "matched": True,
                        "auto_answer": matched_config.get('enable_auto_answer', False),
                        "config": matched_config
                    })

        return matched_courses

    def save_recommendations(self, recommendations: List[Dict]):
        """
        儲存推薦結果到臨時檔案

        Args:
            recommendations: 推薦清單
        """
        try:
            # 確保 data 目錄存在
            os.makedirs(os.path.dirname(self.TEMP_RECOMMENDATIONS_FILE), exist_ok=True)

            with open(self.TEMP_RECOMMENDATIONS_FILE, 'w', encoding='utf-8') as f:
                json.dump(recommendations, f, ensure_ascii=False, indent=2)

            print(f'[儲存] 推薦結果已儲存到 {self.TEMP_RECOMMENDATIONS_FILE}')

        except Exception as e:
            print(f'[錯誤] 儲存推薦結果失敗: {e}')

    def generate_recommendation(self) -> List[Dict]:
        """
        執行完整推薦流程

        Returns:
            推薦的課程列表
        """
        # 1. 掃描可用課程
        available_courses = self.scan_available_courses()

        if not available_courses:
            return []

        # 2. 比對配置
        recommendations = self.match_with_config(available_courses)

        # 3. 儲存結果
        if recommendations:
            self.save_recommendations(recommendations)

        return recommendations

    def print_recommendation(self, recommendations: List[Dict]):
        """
        格式化輸出推薦清單

        Args:
            recommendations: 推薦清單
        """
        if not recommendations:
            print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
            print('【推薦結果】未找到可推薦的課程')
            print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
            print('\n提示: 請先在 courses.json 中配置您想要上的課程')
            return

        print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
        print('【課程推薦】本服務推薦可以上的課程如下：')
        print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')

        for i, item in enumerate(recommendations, 1):
            item_type = "考試" if item['type'] == "exam" else "課程"
            print(f"{i}. [{item_type}] {item['item_name']}")
            print(f"   📚 所屬計畫: {item['program_name']}")
            print(f"   ✅ 已配置")

            config = item.get('config', {})
            delay = config.get('delay', 7.0)
            print(f"   ⏱️  延遲時間: {delay} 秒")

            if item['type'] == 'exam' and item.get('auto_answer'):
                # 找出題庫檔案
                from .question_bank import QuestionBankService
                program_name = item['program_name']
                bank_file = QuestionBankService.QUESTION_BANK_MAPPING.get(program_name)
                if bank_file:
                    print(f"   🤖 自動答題: 啟用")
                    print(f"   📖 題庫: {bank_file}")
                else:
                    print(f"   🤖 自動答題: 啟用 (題庫未映射)")

            print()

        print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
        print(f'總計: {len(recommendations)} 個課程可以立即執行')
        print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')
