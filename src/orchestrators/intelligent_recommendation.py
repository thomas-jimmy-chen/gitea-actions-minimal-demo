# -*- coding: utf-8 -*-
"""
IntelligentRecommendationOrchestrator - 智能推薦流程編排器

編排智能推薦的完整流程：
1. 執行前清理
2. 瀏覽器操作與掃描
3. 課程匹配與推薦
4. 加入排程
5. 執行排程
6. 執行後清理

使用方式:
    from src.orchestrators import IntelligentRecommendationOrchestrator

    orchestrator = IntelligentRecommendationOrchestrator(config)
    result = orchestrator.execute(
        scheduler=scheduler,
        auto_execute=True
    )
"""

import os
import time
import json
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from urllib.parse import urlparse

from .base_orchestrator import BaseOrchestrator, OrchestratorResult

logger = logging.getLogger(__name__)


@dataclass
class ScanResult:
    """掃描結果"""
    programs: List[Dict[str, Any]] = field(default_factory=list)
    available_courses: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None


class IntelligentRecommendationOrchestrator(BaseOrchestrator):
    """
    智能推薦流程編排器

    編排完整的智能推薦流程，包括：
    - 清理舊的排程和 cookies
    - 啟動瀏覽器並登入
    - 掃描修習中的課程
    - 匹配已配置的課程
    - 加入排程並執行

    Attributes:
        temp_files: 需要清理的臨時檔案列表
        courses_config_path: 課程配置檔案路徑

    Example:
        orchestrator = IntelligentRecommendationOrchestrator(config)
        result = orchestrator.execute(
            scheduler=my_scheduler,
            auto_execute=True,
            max_retries=3
        )
    """

    # 需要清理的臨時檔案
    TEMP_FILES = [
        'cookies.json',
        'resource/cookies/cookies.json',
        'stealth.min.js',
        'resource/plugins/stealth.min.js',
    ]

    def __init__(
        self,
        config: Any,
        courses_config_path: str = 'data/courses.json',
        schedule_file: str = 'data/schedule.json'
    ):
        """
        初始化智能推薦編排器

        Args:
            config: 配置對象
            courses_config_path: 課程配置檔案路徑
            schedule_file: 排程檔案路徑
        """
        super().__init__(config, "智能推薦")
        self.courses_config_path = courses_config_path
        self.schedule_file = schedule_file

        # 內部狀態
        self._driver_manager = None
        self._driver = None
        self._scan_result: Optional[ScanResult] = None

    def _do_execute(
        self,
        scheduler: Any = None,
        auto_execute: bool = True,
        max_retries: int = 3,
        **kwargs
    ) -> OrchestratorResult:
        """
        執行智能推薦流程

        Args:
            scheduler: CourseScheduler 實例（用於管理排程）
            auto_execute: 是否自動執行排程
            max_retries: 登入最大重試次數

        Returns:
            OrchestratorResult: 執行結果
        """
        try:
            # Phase 1: 執行前清理
            self.start_phase("執行前清理")
            self._cleanup_before_execution(scheduler)
            self.end_phase("執行前清理")

            # Phase 2: 瀏覽器操作與掃描
            self.start_phase("瀏覽器操作與掃描")
            scan_result = self._browser_scan_phase(max_retries)
            self.end_phase("瀏覽器操作與掃描")

            if scan_result.error:
                return OrchestratorResult(
                    success=False,
                    error=scan_result.error,
                    data={'scan_result': scan_result}
                )

            # Phase 3: 加入排程
            self.start_phase("加入排程")
            added_count = self._add_to_schedule(
                scheduler,
                scan_result.recommendations
            )
            self.end_phase("加入排程")

            # Phase 4: 執行排程
            if auto_execute and added_count > 0:
                self.start_phase("執行排程")
                self._execute_schedule(scheduler)
                self.end_phase("執行排程")

            # Phase 5: 執行後清理
            self.start_phase("執行後清理")
            self._cleanup_after_execution(scheduler)
            self.end_phase("執行後清理")

            return OrchestratorResult(
                success=True,
                data={
                    'programs_count': len(scan_result.programs),
                    'recommendations_count': len(scan_result.recommendations),
                    'added_count': added_count,
                    'auto_executed': auto_execute and added_count > 0
                }
            )

        except Exception as e:
            logger.exception("智能推薦執行失敗")
            return OrchestratorResult(
                success=False,
                error=str(e)
            )
        finally:
            self._cleanup_driver()

    def _cleanup_before_execution(self, scheduler: Any) -> None:
        """執行前清理"""
        print('\n[步驟 1/5] 執行前清理...')

        # 清除內部排程
        if scheduler:
            scheduler.scheduled_courses = []
            print('  ✓ 已清除內部排程')

        # 清除排程檔案
        if os.path.exists(self.schedule_file):
            try:
                os.remove(self.schedule_file)
                print('  ✓ 已刪除排程檔案')
            except OSError as e:
                print(f'  ✗ 刪除排程檔案失敗: {e}')

        # 清除臨時檔案
        self._cleanup_temp_files()
        print('  ✓ 執行前清理完成\n')

    def _cleanup_temp_files(self) -> None:
        """清理臨時檔案"""
        for file_path in self.TEMP_FILES:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    display_name = file_path.replace(
                        'stealth.min.js', 'stealth mode file'
                    )
                    print(f'  ✓ 已刪除: {display_name}')
                except OSError as e:
                    display_name = file_path.replace(
                        'stealth.min.js', 'stealth mode file'
                    )
                    print(f'  ✗ 刪除失敗 {display_name}: {e}')

    def _browser_scan_phase(self, max_retries: int) -> ScanResult:
        """瀏覽器掃描階段"""
        result = ScanResult()

        try:
            # 延遲導入
            from src.core.cookie_manager import CookieManager
            from src.core.driver_manager import DriverManager
            from src.pages.course_list_page import CourseListPage
            from src.pages.login_page import LoginPage
            from src.utils.stealth_extractor import StealthExtractor

            print('[步驟 2/5] 正在啟動瀏覽器...')
            print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')

            # 初始化 Stealth
            print('[初始化 1/4] 啟動瀏覽器自動化模式...')
            extractor = StealthExtractor()
            if not extractor.exists():
                extractor.run()
            else:
                print('  ✓ 瀏覽器自動化模式就緒')

            # 初始化核心元件
            print('[初始化 2/4] 初始化核心元件...')
            self._driver_manager = DriverManager(self.config)
            cookie_manager = CookieManager(self._get_config_value('cookies_file'))
            print('  ✓ 核心元件已初始化')

            # 建立 Driver
            print('[初始化 3/4] 啟動瀏覽器...')
            self._driver = self._driver_manager.create_driver(use_proxy=False)
            print('  ✓ 瀏覽器已啟動')

            # 初始化頁面物件
            print('[初始化 4/4] 初始化頁面物件...')
            login_page = LoginPage(self._driver, cookie_manager)
            course_list_page = CourseListPage(self._driver)
            print('  ✓ 頁面物件已初始化\n')

            # 登入
            print('[Step 1] 正在登入...')
            login_success = self._perform_login(login_page, max_retries)

            if not login_success:
                result.error = "登入失敗"
                return result

            print('  ✓ 登入成功\n')

            # 前往我的課程
            print('[Step 2] 前往我的課程...')
            course_list_page.goto_my_courses()
            print('  ✓ 已進入我的課程\n')

            # 等待頁面載入
            print('[Step 3] 等待頁面載入...')
            time.sleep(10)
            print('  ✓ 頁面已載入\n')

            # 掃描課程計畫
            print('[Step 4] 掃描「修習中」的課程計畫...')
            result.programs = course_list_page.get_in_progress_programs()

            if not result.programs:
                result.error = "未找到任何「修習中」的課程計畫"
                return result

            print(f'  ✓ 找到 {len(result.programs)} 個課程計畫\n')

            # 分析課程詳情
            print('[Step 5] 正在分析課程詳情...\n')
            result.available_courses = self._scan_program_details(
                course_list_page,
                result.programs
            )
            print('\n  ✓ 分析完成！\n')

            # 比對配置
            print('[Step 6] 比對已配置的課程...')
            result.recommendations = self._match_with_config(
                result.available_courses
            )

            if not result.recommendations:
                result.error = "未找到可推薦的課程"
                return result

            print(f'  ✓ 找到 {len(result.recommendations)} 個已配置的課程\n')

            # 顯示推薦結果
            self._display_recommendations(result.recommendations)

        except ImportError as e:
            result.error = f"無法載入推薦服務: {e}"
        except Exception as e:
            logger.exception("瀏覽器掃描失敗")
            result.error = str(e)

        return result

    def _perform_login(self, login_page: Any, max_retries: int) -> bool:
        """執行登入"""
        for attempt in range(max_retries):
            login_success = login_page.auto_login(
                username=self._get_config_value('user_name'),
                password=self._get_config_value('password'),
                url=self._get_config_value('target_http'),
            )

            if login_success:
                return True

            if attempt < max_retries - 1:
                print(f'  ⚠️  登入失敗，重試中... ({attempt + 1}/{max_retries})\n')
                login_page.goto(self._get_config_value('target_http'))
            else:
                print('  ✗ 登入失敗，已達最大重試次數\n')

        return False

    def _scan_program_details(
        self,
        course_list_page: Any,
        programs: List[Dict]
    ) -> List[Dict]:
        """掃描課程詳情"""
        available_courses = []

        target_url = self._get_config_value('target_http')
        parsed = urlparse(target_url)
        base_url = f'{parsed.scheme}://{parsed.netloc}'

        for i, program in enumerate(programs, 1):
            program_name = program['name']
            print(f'  [{i}/{len(programs)}] {program_name[:50]}...')

            # 記錄課程處理
            self.start_item(program_name, item_type='course')

            details = course_list_page.get_program_courses_and_exams(program_name)

            if details.get('error', False):
                print(f'  ✗ 掃描失敗: {details.get("error_message", "未知錯誤")}')
                available_courses.append({
                    'program_name': program_name,
                    'courses': [],
                    'exams': [],
                })
            else:
                available_courses.append({
                    'program_name': program_name,
                    'courses': details.get('courses', []),
                    'exams': details.get('exams', []),
                })

            self.end_item(program_name)

            # 返回課程列表
            if i < len(programs):
                self._navigate_back_to_course_list(
                    course_list_page,
                    base_url
                )

        return available_courses

    def _navigate_back_to_course_list(
        self,
        course_list_page: Any,
        base_url: str
    ) -> None:
        """返回課程列表"""
        print('  → 返回課程列表...')
        try:
            course_list_page.go_back_to_course_list()
        except Exception as e1:
            print(f'  [WARNING] 返回按鈕失敗，嘗試直接導航: {e1}')
            try:
                self._driver.get(f'{base_url}/user/courses')
                time.sleep(2)
                print('  ✓ 已導航到課程列表')
            except Exception as e2:
                print(f'  [ERROR] 導航失敗: {e2}')

    def _match_with_config(
        self,
        available_courses: List[Dict]
    ) -> List[Dict]:
        """比對已配置的課程"""
        try:
            with open(self.courses_config_path, 'r', encoding='utf-8-sig') as f:
                config_data = json.load(f)
                config_courses = config_data.get('courses', [])
        except Exception as e:
            logger.error("載入配置失敗: %s", e)
            return []

        recommendations = []

        for program in available_courses:
            program_name = program['program_name']

            # 比對一般課程
            for course in program.get('courses', []):
                matched = self._match_course(course['name'], config_courses)
                if matched:
                    recommendations.append({
                        'program_name': program_name,
                        'item_name': course['name'],
                        'type': 'course',
                        'matched': True,
                        'config': matched,
                    })

            # 比對考試
            for exam in program.get('exams', []):
                matched = self._match_course(exam['name'], config_courses)
                if matched:
                    recommendations.append({
                        'program_name': program_name,
                        'item_name': exam['name'],
                        'type': 'exam',
                        'matched': True,
                        'auto_answer': matched.get('enable_auto_answer', False),
                        'config': matched,
                    })

        return recommendations

    @staticmethod
    def _normalize_text(text: str) -> str:
        """正規化文字"""
        if not text:
            return ''
        return ''.join(text.split()).lower()

    def _match_course(
        self,
        web_name: str,
        courses_list: List[Dict]
    ) -> Optional[Dict]:
        """匹配課程"""
        web_norm = self._normalize_text(web_name)

        for course in courses_list:
            config_name = course.get('lesson_name') or course.get('exam_name')
            if not config_name:
                continue

            config_norm = self._normalize_text(config_name)

            # 精確匹配
            if web_norm == config_norm:
                return course

            # 包含匹配
            if web_norm in config_norm or config_norm in web_norm:
                return course

            # 模糊匹配 (90%)
            similarity = SequenceMatcher(None, web_norm, config_norm).ratio()
            if similarity >= 0.90:
                return course

        return None

    def _display_recommendations(self, recommendations: List[Dict]) -> None:
        """顯示推薦結果"""
        print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
        print('【課程推薦】本服務推薦可以上的課程如下：')
        print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')

        for i, item in enumerate(recommendations, 1):
            item_type = '考試' if item['type'] == 'exam' else '課程'
            print(f"{i}. [{item_type}] {item['item_name']}")
            print(f"   所屬計畫: {item['program_name']}")
            print(f'   已配置')

            if item['type'] == 'exam':
                if item.get('auto_answer'):
                    print('   自動答題: 啟用')
                else:
                    print('   手動作答')
            print()

        print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
        print(f'總計: {len(recommendations)} 個課程可以立即執行')
        print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')

    def _add_to_schedule(
        self,
        scheduler: Any,
        recommendations: List[Dict]
    ) -> int:
        """加入排程"""
        if not scheduler:
            logger.warning("未提供 scheduler，跳過加入排程")
            return 0

        print('[步驟 3/5] 正在加入排程...\n')

        added_count = 0
        skipped_count = 0

        for item in recommendations:
            config_item = item['config']

            # 檢查是否重複
            is_duplicate = self._is_duplicate(scheduler, config_item)

            if is_duplicate:
                skipped_count += 1
                print(f'  ⚠️  跳過重複項目: {item["item_name"][:40]}...')
            else:
                scheduler.scheduled_courses.append(config_item)
                added_count += 1

        print(f'\n✓ 已將 {added_count} 個推薦課程加入排程')
        if skipped_count > 0:
            print(f'  ⚠️  跳過 {skipped_count} 個重複項目\n')

        return added_count

    @staticmethod
    def _is_duplicate(scheduler: Any, config_item: Dict) -> bool:
        """檢查是否重複"""
        for existing in scheduler.scheduled_courses:
            if config_item.get('course_type') == 'exam':
                if (existing.get('program_name') == config_item.get('program_name')
                    and existing.get('exam_name') == config_item.get('exam_name')
                    and existing.get('course_type') == 'exam'):
                    return True
            else:
                if (existing.get('program_name') == config_item.get('program_name')
                    and existing.get('lesson_name') == config_item.get('lesson_name')
                    and existing.get('course_id') == config_item.get('course_id')):
                    return True
        return False

    def _execute_schedule(self, scheduler: Any) -> None:
        """執行排程"""
        if not scheduler or not scheduler.scheduled_courses:
            print('\n⚠️  未找到可執行的課程')
            return

        print('\n[步驟 5/5] 正在執行排程...')
        print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')

        # 儲存排程
        scheduler.save_schedule()

        # 執行 main.py
        print('\n啟動 main.py...\n')
        print('=' * 70)
        os.system('python main.py')
        print('=' * 70)

    def _cleanup_after_execution(self, scheduler: Any) -> None:
        """執行後清理"""
        print('\n[執行完成] 正在清理...')

        # 清除內部排程
        if scheduler:
            scheduler.scheduled_courses = []
            print('  ✓ 已清除內部排程')

        # 清除排程檔案
        if os.path.exists(self.schedule_file):
            try:
                os.remove(self.schedule_file)
                print('  ✓ 已刪除排程檔案')
            except OSError as e:
                print(f'  ✗ 刪除排程檔案失敗: {e}')

        # 清除臨時檔案
        self._cleanup_temp_files()
        print('\n✓ 所有任務已完成！')

    def _cleanup_driver(self) -> None:
        """清理 driver"""
        if self._driver_manager:
            try:
                print('\n[清理] 關閉瀏覽器...')
                self._driver_manager.quit()
                print('  ✓ 瀏覽器已關閉')
            except Exception as e:
                logger.warning("關閉瀏覽器失敗: %s", e)
            finally:
                self._driver_manager = None
                self._driver = None

    def _get_config_value(self, key: str, default: Any = None) -> Any:
        """從配置中取得值"""
        if hasattr(self.config, 'get') and callable(self.config.get):
            return self.config.get(key, default)
        return getattr(self.config, key, default)
