# -*- coding: utf-8 -*-
"""
HybridScanOrchestrator - 混合式掃描流程編排器

編排混合式課程掃描與時長發送的流程。

支援模式:
- DURATION (h1): 一般課程時長發送
    - 使用兩階段掃描（DOM + mitmproxy）
    - 只處理一般課程

- BATCH (h2): 批量模式（課程 + 考試）
    - 使用兩階段掃描（DOM + mitmproxy）
    - 處理一般課程和考試
    - 課程使用 requests.post，考試使用 mitmproxy

- EXAM (h3): 考試自動答題
    - 只使用 DOM 提取（無 mitmproxy）
    - 只處理考試

使用方式:
    from src.orchestrators import HybridScanOrchestrator, HybridMode

    orchestrator = HybridScanOrchestrator(config, mode=HybridMode.DURATION)
    result = orchestrator.execute()
"""

import time
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

from .base_orchestrator import BaseOrchestrator, OrchestratorResult

logger = logging.getLogger(__name__)


class HybridMode(Enum):
    """混合掃描模式"""
    DURATION = "duration"  # h1: 一般課程時長發送
    BATCH = "batch"        # h2: 批量模式（課程 + 考試）
    EXAM = "exam"          # h3: 考試自動答題


@dataclass
class HybridScanResult:
    """混合掃描結果"""
    mode: HybridMode
    programs_scanned: int = 0
    general_courses_found: int = 0
    exams_found: int = 0
    payloads_captured: int = 0
    courses_selected: int = 0
    courses_processed: int = 0
    exams_processed: int = 0
    success_count: int = 0
    failed_count: int = 0
    total_increase_minutes: int = 0
    error: Optional[str] = None


class HybridScanOrchestrator(BaseOrchestrator):
    """
    混合式掃描流程編排器

    使用服務層實現真實業務邏輯。支持三種模式：

    - h1 (DURATION): 一般課程時長發送
        流程: 登入 → DOM+Payload 掃描 → 選擇 → 提取條件 → 發送時長

    - h2 (BATCH): 批量模式
        流程: 登入 → DOM+Payload 掃描 → 選擇 → 課程發送 + 考試處理

    - h3 (EXAM): 考試自動答題
        流程: 登入 → DOM 掃描（只取考試） → 選擇 → 考試處理

    Example:
        orchestrator = HybridScanOrchestrator(
            config,
            mode=HybridMode.DURATION
        )
        result = orchestrator.execute(auto_select=False)
    """

    def __init__(
        self,
        config: Any,
        mode: HybridMode = HybridMode.DURATION
    ):
        """
        初始化混合掃描編排器

        Args:
            config: 配置對象
            mode: 操作模式
        """
        mode_names = {
            HybridMode.DURATION: "一般課程時長發送 (h1)",
            HybridMode.BATCH: "批量模式 (h2)",
            HybridMode.EXAM: "考試自動答題 (h3)",
        }
        name = f"混合掃描 - {mode_names.get(mode, mode.value)}"
        super().__init__(config, name)

        self.mode = mode

        # 服務實例（延遲初始化）
        self._session_manager = None
        self._structure_service = None
        self._payload_service = None
        self._pass_req_service = None
        self._duration_service = None

        # 運行時狀態
        self._driver_manager = None
        self._cookie_manager = None

    def _do_execute(
        self,
        auto_select: bool = False,
        max_retries: int = 3,
        **kwargs
    ) -> OrchestratorResult:
        """
        執行混合掃描流程

        Args:
            auto_select: 是否自動選擇所有課程
            max_retries: 登入最大重試次數

        Returns:
            OrchestratorResult: 執行結果
        """
        result = HybridScanResult(mode=self.mode)

        try:
            # 初始化服務
            self._initialize_services()

            # Phase 1: 登入與初始化
            self.start_phase("登入與初始化")
            if not self._phase1_initialize_and_login(max_retries):
                result.error = "登入失敗"
                return self._create_result(False, result, "登入失敗")
            self.end_phase("登入與初始化")

            # 獲取課程計畫
            programs = self._get_programs()
            if not programs:
                result.error = "未找到課程"
                return self._create_result(False, result, "未找到課程")
            result.programs_scanned = len(programs)

            # 根據模式執行不同流程
            if self.mode == HybridMode.EXAM:
                return self._execute_exam_mode(result, programs, auto_select)
            elif self.mode == HybridMode.BATCH:
                return self._execute_batch_mode(result, programs, auto_select)
            else:  # DURATION
                return self._execute_duration_mode(result, programs, auto_select)

        except Exception as e:
            logger.exception("混合掃描執行失敗")
            result.error = str(e)
            return self._create_result(False, result, str(e))

        finally:
            self._cleanup()

    def _execute_duration_mode(
        self,
        result: HybridScanResult,
        programs: List[Dict[str, Any]],
        auto_select: bool
    ) -> OrchestratorResult:
        """
        執行 h1 模式：一般課程時長發送

        流程:
        1. 兩階段掃描（DOM + mitmproxy）
        2. 課程選擇（只顯示一般課程）
        3. 提取通過條件
        4. 發送時長
        """
        # Phase 2: 兩階段掃描（排除考試）
        self.start_phase("Payload 捕獲掃描（兩階段）")
        capture_result = self._payload_service.capture_payloads(
            session_manager=self._session_manager,
            programs=programs,
            exclude_exams=True  # h1 不需要考試
        )
        self.end_phase("Payload 捕獲掃描（兩階段）")

        if not capture_result.success:
            result.error = capture_result.error or "掃描失敗"
            return self._create_result(False, result, result.error)

        result.general_courses_found = len(capture_result.general_courses)
        result.payloads_captured = len(capture_result.payloads)

        if not capture_result.payloads:
            result.error = "未捕獲到 Payload"
            return self._create_result(False, result, result.error)

        # 構建課程數據
        courses_data = self._build_courses_data(capture_result.payloads)

        # Phase 3: 課程選擇
        self.start_phase("課程選擇")
        selected_courses = self._phase3_select_courses(courses_data, auto_select)
        self.end_phase("課程選擇")

        if not selected_courses:
            result.error = "未選擇任何課程"
            return self._create_result(False, result, "未選擇任何課程")

        result.courses_selected = len(selected_courses)

        # Phase 4: 提取通過條件
        self.start_phase("提取通過條件與計算目標時長")
        extraction_result = self._pass_req_service.extract_requirements(
            session_manager=self._session_manager,
            selected_courses=selected_courses
        )
        self.end_phase("提取通過條件與計算目標時長")

        if not extraction_result.success or not extraction_result.courses_to_process:
            result.error = extraction_result.error or "無需發送時長的課程"
            return self._create_result(False, result, result.error)

        # Phase 5: 發送時長
        self.start_phase("使用 Mitmproxy 發送目標時長")
        interceptor = self._payload_service.get_interceptor()
        send_result = self._duration_service.send_duration(
            session_manager=self._session_manager,
            interceptor=interceptor,
            courses_to_process=extraction_result.courses_to_process,
            durations_before=extraction_result.durations_before
        )
        self.end_phase("使用 Mitmproxy 發送目標時長")

        # 追蹤已處理的課程（事後記錄）
        for item in send_result.results:
            self.start_item(item.program_name, '', 'course')
            self.end_item(item.program_name)

        result.courses_processed = len(send_result.results)
        result.success_count = send_result.success_count
        result.failed_count = send_result.failed_count
        result.total_increase_minutes = send_result.total_increase

        # Phase 6: 生成報告
        self.start_phase("生成報告")
        self._duration_service.generate_report(send_result)
        self.end_phase("生成報告")

        return self._create_result(True, result)

    def _execute_batch_mode(
        self,
        result: HybridScanResult,
        programs: List[Dict[str, Any]],
        auto_select: bool
    ) -> OrchestratorResult:
        """
        執行 h2 模式：批量模式（課程 + 考試）

        關鍵設計（參照 Legacy menu.py:1917-2900）：
        - 一個 mitmproxy，兩個 interceptor
        - PayloadCaptureInterceptor（先啟用，後禁用）
        - ExamAutoAnswerInterceptor（先禁用，後啟用）
        - 全程不重啟 proxy

        流程:
        1. 快速掃描（無 proxy）- 收集課程結構和考試列表
        2. 啟動 mitmproxy（雙 interceptor）
        3. Payload 捕獲（有 proxy）
        4. 課程選擇
        5. 處理課程（無 proxy，requests.post）
        6. 處理考試（有 proxy，exam interceptor）
        7. 停止 mitmproxy
        """
        import re
        from pathlib import Path
        from urllib.parse import urlparse

        from src.core.proxy_manager import ProxyManager
        from src.api.interceptors.payload_capture import PayloadCaptureInterceptor
        from src.api.interceptors.exam_auto_answer import ExamAutoAnswerInterceptor
        from src.services.question_bank import QuestionBankService
        from src.services.answer_matcher import AnswerMatcher
        from src.pages.course_detail_page import CourseDetailPage
        from src.pages.exam_detail_page import ExamDetailPage
        from src.pages.exam_answer_page import ExamAnswerPage
        from src.utils.scroll_utils import scroll_to_bottom_multi_strategy

        proxy = None
        payload_interceptor = None
        exam_interceptor = None
        question_bank_service = None

        try:
            # ================================================================
            # Phase 2A: 快速掃描（無 proxy）- 收集課程結構和考試列表
            # ================================================================
            self.start_phase("快速掃描課程結構")
            print('\n[階段 2A] 快速掃描課程結構（無 proxy）...')
            print('━' * 70)

            driver = self._session_manager.driver
            target_url = self._get_config_value('target_http')
            parsed = urlparse(target_url)
            base_url = f'{parsed.scheme}://{parsed.netloc}'

            from src.pages.course_list_page import CourseListPage
            course_list_page = CourseListPage(driver)

            course_structure = []  # 需要 payload 的課程
            all_exam_courses = []  # 所有考試

            for i, program in enumerate(programs, 1):
                program_name = program.get('name', f'課程 {i}')
                print(f'\n  [{i}/{len(programs)}] {program_name[:50]}...')

                try:
                    details = course_list_page.get_program_courses_and_exams(program_name)
                    courses = details.get('courses', [])
                    exams = details.get('exams', [])

                    # 從 URL 提取課程 ID
                    current_url = driver.current_url
                    course_id_match = re.search(r'/course/(\d+)', current_url)
                    course_id = course_id_match.group(1) if course_id_match else None

                    print(f'      ✓ 課程: {len(courses)} 個, 考試: {len(exams)} 個')

                    # 記錄需要 payload 的課程
                    if courses:
                        first_course = courses[0]
                        course_detail_page = CourseDetailPage(driver)
                        module_id = course_detail_page.get_first_module_id()
                        required_minutes = 0
                        if module_id:
                            pass_req = course_detail_page.extract_pass_requirement(module_id)
                            required_minutes = pass_req.get('required_minutes', 0) or 0

                        course_structure.append({
                            "program_name": program_name,
                            "first_course_name": first_course['name'],
                            "api_course_id": course_id,
                            "required_minutes": required_minutes
                        })

                    # 收集考試
                    for exam in exams:
                        all_exam_courses.append({
                            "program_name": program_name,
                            "exam_name": exam['name'],
                            "api_course_id": course_id,
                            "item_type": "exam"
                        })

                    # 返回課程列表
                    if i < len(programs):
                        try:
                            course_list_page.go_back_to_course_list()
                            self._sleep_with_record(2, '返回課程列表')
                        except Exception:
                            driver.get(f'{base_url}/user/courses')
                            self._sleep_with_record(3, '返回課程列表(fallback)')

                except Exception as e:
                    print(f'      ✗ 掃描失敗: {e}')
                    if i < len(programs):
                        driver.get(f'{base_url}/user/courses')
                        self._sleep_with_record(3, '錯誤恢復：返回課程列表')

            print(f'\n✓ 快速掃描完成')
            print(f'  - 需要 payload 的課程: {len(course_structure)} 個')
            print(f'  - 考試: {len(all_exam_courses)} 個')
            self.end_phase("快速掃描課程結構")

            result.exams_found = len(all_exam_courses)

            # ================================================================
            # Phase 2B: 啟動 mitmproxy（雙 interceptor）
            # ================================================================
            all_general_courses = []

            # 如果有課程或考試，需要啟動 mitmproxy
            if course_structure or all_exam_courses:
                self.start_phase("初始化 Mitmproxy")
                print('\n[階段 2B] 啟動 mitmproxy（雙 interceptor）...')
                print('━' * 70)

                # 初始化題庫服務（考試需要）
                question_bank_service = QuestionBankService(self.config)
                answer_matcher = AnswerMatcher(confidence_threshold=0.85)

                # 創建兩個 interceptor
                payload_interceptor = PayloadCaptureInterceptor()
                exam_interceptor = ExamAutoAnswerInterceptor(
                    question_bank_service=question_bank_service,
                    answer_matcher=answer_matcher,
                    enable=False  # 先禁用，Phase 6 再啟用
                )

                # 一個 mitmproxy，兩個 interceptor
                proxy = ProxyManager(self.config, interceptors=[payload_interceptor, exam_interceptor])
                proxy.start()
                print('  ✓ Mitmproxy 已啟動（端口 8080）')
                print('  ℹ️  Payload 捕獲：啟用')
                print('  ℹ️  考試答題：禁用（稍後啟用）')

                self.end_phase("初始化 Mitmproxy")

            # 如果有課程，進行 Payload 捕獲
            if course_structure:
                self.start_phase("Payload 捕獲")
                print('\n[Payload 捕獲] 訪問課程...')

                # 重啟瀏覽器（使用 proxy）
                print('\n[重啟瀏覽器] 使用 proxy...')
                self._session_manager.close()
                driver = self._driver_manager.create_driver(use_proxy=True)

                # 重新登入（使用統一方法）
                self._relogin_browser(driver, use_proxy=True)

                # 訪問課程以捕獲 Payload
                for i, course_info in enumerate(course_structure, 1):
                    program_name = course_info['program_name']
                    first_course_name = course_info['first_course_name']
                    course_id = course_info['api_course_id']

                    print(f'\n  [{i}/{len(course_structure)}] {program_name[:40]}...')

                    try:
                        course_url = f"{target_url}/course/{course_id}/content#/"
                        driver.get(course_url)
                        self._sleep_with_record(5, '等待課程頁面載入')

                        course_detail_page = CourseDetailPage(driver)
                        course_detail_page.select_lesson_by_name(first_course_name, delay=3.0)
                        self._sleep_with_record(3, '等待觸發 payload')
                        print(f'      ✓ 已觸發 payload')

                    except Exception as e:
                        print(f'      ✗ 無法訪問: {e}')

                # 禁用 Payload 捕獲（保持 mitmproxy 運行）
                print('\n[禁用 Payload 捕獲]')
                captured_payloads = payload_interceptor.get_captured_payloads()
                payload_interceptor.disable_capture()
                print(f'  ✓ 已捕獲 {len(captured_payloads)} 個 payload')
                print(f'  ℹ️  Mitmproxy 保持運行')

                # 構建課程數據
                course_structure_map = {
                    info['api_course_id']: info
                    for info in course_structure if info.get('api_course_id')
                }

                for course_code, payload in captured_payloads.items():
                    main_course_id = str(payload.get('course_id', ''))
                    course_name = payload.get('course_name', '未知')
                    structure_info = course_structure_map.get(main_course_id, {})

                    all_general_courses.append({
                        "api_course_id": main_course_id or str(course_code),
                        "program_name": course_name,
                        "course_name": course_name,
                        "course_code": payload.get('course_code', 'N/A'),
                        "required_minutes": structure_info.get('required_minutes', 0),
                        "payload": payload.copy(),
                        "item_type": "course"
                    })

                self.end_phase("Payload 捕獲")

            result.general_courses_found = len(all_general_courses)
            result.payloads_captured = len(all_general_courses)

            # ================================================================
            # Phase 3: 課程選擇
            # ================================================================
            all_items = all_general_courses + all_exam_courses

            if not all_items:
                result.error = "未找到任何課程或考試"
                return self._create_result(False, result, result.error)

            print(f'\n✓ 掃描完成')
            print(f'  - 一般課程: {len(all_general_courses)} 個')
            print(f'  - 考試: {len(all_exam_courses)} 個')

            self.start_phase("課程與考試選擇")
            selected_items = self._phase3_select_courses(all_items, auto_select)
            self.end_phase("課程與考試選擇")

            if not selected_items:
                result.error = "未選擇任何項目"
                return self._create_result(False, result, "未選擇任何項目")

            result.courses_selected = len(selected_items)

            selected_courses = [i for i in selected_items if i.get('item_type') == 'course']
            selected_exams = [i for i in selected_items if i.get('item_type') == 'exam']

            print(f'\n已選擇: {len(selected_courses)} 個課程, {len(selected_exams)} 個考試')

            # ================================================================
            # Phase 5: 處理課程（無 proxy，requests.post）
            # ================================================================
            if selected_courses:
                self.start_phase("處理一般課程")
                print('\n[階段 5] 處理一般課程（無 proxy）...')
                print('━' * 70)

                # 重啟瀏覽器（無 proxy）
                driver.quit()
                driver = self._driver_manager.create_driver(use_proxy=False)

                # 重新登入（使用統一方法）
                self._relogin_browser(driver, use_proxy=False)

                # 發送 Payload
                course_result = self._process_courses_internal(selected_courses, driver)
                result.courses_processed = course_result.get('processed', 0)
                result.success_count = course_result.get('success', 0)
                result.failed_count = course_result.get('failed', 0)

                self.end_phase("處理一般課程")

            # ================================================================
            # Phase 6: 處理考試（有 proxy，exam interceptor）
            # ================================================================
            if selected_exams:
                self.start_phase("處理考試")
                print('\n[階段 6] 處理考試（使用 proxy）...')
                print('━' * 70)

                # 重啟瀏覽器（使用 proxy）
                try:
                    driver.quit()
                except Exception:
                    pass

                driver = self._driver_manager.create_driver(use_proxy=True)

                # 重新登入（使用統一方法）
                self._relogin_browser(driver, use_proxy=True)

                # 啟用考試攔截器
                if exam_interceptor:
                    exam_interceptor.enable = True
                    print('  ✓ 考試答題攔截器已啟用')

                # 處理考試
                exam_result = self._process_exams_internal(
                    selected_exams, driver, exam_interceptor,
                    question_bank_service, base_url, target_url
                )
                result.exams_processed = exam_result.get('processed', 0)

                # 禁用考試攔截器
                if exam_interceptor:
                    exam_interceptor.enable = False

                self.end_phase("處理考試")

            return self._create_result(True, result)

        except Exception as e:
            logger.exception("h2 批量模式執行失敗")
            result.error = str(e)
            return self._create_result(False, result, str(e))

        finally:
            # 最後才停止 mitmproxy
            if proxy:
                try:
                    proxy.stop()
                    print('\n  ✓ Mitmproxy 已停止')
                except Exception:
                    pass

    def _process_courses(
        self,
        selected_courses: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """
        處理一般課程（發送 payload）

        使用 requests.post 發送修改後的 payload，
        參照 Legacy menu.py Stage 5 的邏輯。

        Args:
            selected_courses: 已選擇的課程列表

        Returns:
            Dict: {'processed': int, 'success': int, 'failed': int}
        """
        import requests

        print(f'\n[處理課程] 發送 {len(selected_courses)} 個課程的 Payload...')

        # 獲取配置（確保轉換為整數）
        duration_increase = int(self._get_config_value('visit_duration_increase', 6000))
        target_http = self._get_config_value('target_http')
        api_url = f"{target_http}/statistics/api/user-visits"

        print(f'  配置: 增加 {duration_increase} 秒 ({duration_increase//60} 分鐘)')

        # 獲取認證信息（從瀏覽器）
        driver = self._session_manager.driver
        cookies_dict = {
            cookie['name']: cookie['value']
            for cookie in driver.get_cookies()
        }
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': driver.execute_script("return navigator.userAgent"),
            'Referer': f'{target_http}/learning/my-courses'
        }

        success_count = 0
        failed_count = 0

        for i, course in enumerate(selected_courses, 1):
            program_name = course.get('name', course.get('program_name', f'課程 {i}'))
            course_code = course.get('course_code', 'N/A')

            # 開始追蹤課程
            self.start_item(program_name, '', 'course')

            print(f'\n  [{i}/{len(selected_courses)}] {program_name[:50]}...')

            # 使用已捕獲的 payload
            payload = course.get('payload')
            if not payload:
                print(f'      ✗ 無 payload，跳過')
                failed_count += 1
                self.end_item(program_name)
                continue

            # 修改 visit_duration
            modified_payload = payload.copy()
            original_duration = modified_payload.get('visit_duration', 0)
            modified_payload['visit_duration'] = original_duration + duration_increase

            print(f'      發送時長: {modified_payload["visit_duration"]} 秒 (+{duration_increase})')

            try:
                response = requests.post(
                    api_url,
                    json=modified_payload,
                    cookies=cookies_dict,
                    headers=headers,
                    timeout=10,
                    verify=False
                )

                if response.status_code in (200, 204):
                    print(f'      ✓ 發送成功 (HTTP {response.status_code})')
                    success_count += 1
                else:
                    print(f'      ✗ 發送失敗 (HTTP {response.status_code})')
                    failed_count += 1

            except Exception as e:
                print(f'      ✗ 發送失敗: {e}')
                failed_count += 1

            # 結束追蹤課程
            self.end_item(program_name)

            self._sleep_with_record(1, '請求間隔')

        print(f'\n  ✓ 課程處理完成: {success_count} 成功, {failed_count} 失敗')

        return {
            'processed': len(selected_courses),
            'success': success_count,
            'failed': failed_count
        }

    def _process_exams(
        self,
        selected_exams: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """
        處理考試（自動答題）

        在 h2 批量模式中直接處理考試，流程：
        1. 停止當前的 payload capture proxy
        2. 初始化考試服務（題庫、攔截器）
        3. 啟動新的 mitmproxy（考試攔截器）
        4. 重啟瀏覽器（使用 proxy）
        5. 重新登入
        6. 處理每個考試
        7. 生成報告

        Args:
            selected_exams: 已選擇的考試列表

        Returns:
            Dict: {'processed': int, 'success': int, 'failed': int}
        """
        from pathlib import Path
        from urllib.parse import urlparse

        from src.services.question_bank import QuestionBankService
        from src.services.answer_matcher import AnswerMatcher
        from src.api.interceptors.exam_auto_answer import ExamAutoAnswerInterceptor
        from src.core.proxy_manager import ProxyManager
        from src.pages.exam_detail_page import ExamDetailPage
        from src.pages.exam_answer_page import ExamAnswerPage
        from src.utils.scroll_utils import scroll_to_bottom_multi_strategy

        result_stats = {'processed': 0, 'success': 0, 'failed': 0}
        proxy = None
        driver = None
        exam_screenshots = {}

        print(f'\n[處理考試] 共選擇 {len(selected_exams)} 個考試')
        print('━' * 50)

        try:
            # Step 1: 停止當前的 payload capture proxy
            print('\n[考試準備 1/3] 停止 Payload 捕獲代理...')
            if self._payload_service:
                self._payload_service.stop_proxy()
            print('  ✓ 已停止')

            # Step 2: 初始化考試服務
            print('\n[考試準備 2/3] 初始化考試服務...')
            question_bank_service = QuestionBankService(self.config)
            answer_matcher = AnswerMatcher(confidence_threshold=0.85)
            interceptor = ExamAutoAnswerInterceptor(
                question_bank_service=question_bank_service,
                answer_matcher=answer_matcher,
                enable=True
            )
            print('  ✓ 題庫服務已初始化')
            print('  ✓ ExamAutoAnswerInterceptor 已初始化')

            # Step 3: 啟動新的 mitmproxy
            print('\n[考試準備 3/3] 啟動考試攔截代理...')
            proxy = ProxyManager(self.config, interceptors=[interceptor])
            proxy.start()
            print('  ✓ Mitmproxy 已啟動（考試自動答題模式）')

            # Step 4: 重啟瀏覽器（使用 proxy）
            print('\n[瀏覽器] 重新啟動瀏覽器（使用 proxy）...')
            if self._session_manager:
                self._session_manager.close()

            driver = self._driver_manager.create_driver(use_proxy=True)

            # Step 5: 重新登入（使用統一方法）
            self._relogin_browser(driver, use_proxy=True)

            # 提取 base_url
            target_url = self._get_config_value('target_http')
            parsed = urlparse(target_url)
            base_url = f'{parsed.scheme}://{parsed.netloc}'

            # 準備截圖目錄
            screenshot_dir = Path('reports/exam_screenshots')
            screenshot_dir.mkdir(parents=True, exist_ok=True)

            # Step 6: 處理每個考試
            print('\n[處理考試] 開始自動答題...')

            exam_detail_page = ExamDetailPage(driver)
            exam_answer_page = ExamAnswerPage(driver)

            for i, exam in enumerate(selected_exams, 1):
                exam_id = exam.get('api_course_id')
                program_name = exam.get('program_name', f'考試 {i}')
                exam_name = exam.get('exam_name', exam.get('name', '未知考試'))

                # 開始追蹤考試
                self.start_item(exam_name, program_name, 'exam')

                print(f'\n  [{i}/{len(selected_exams)}] {program_name[:50]}')
                print(f'      考試名稱: {exam_name}')

                # 動態載入題庫
                print(f'      → 載入題庫: {program_name[:40]}...')
                question_count = question_bank_service.load_question_bank(program_name)
                if question_count > 0:
                    print(f'         ✓ 題庫已載入: {question_count} 題')
                else:
                    print(f'         ⚠️  題庫載入失敗或為空')

                # 前往課程頁面
                exam_url = f"{target_url}/course/{exam_id}/content#/"
                print(f'      → 前往課程頁面...')
                driver.get(exam_url)
                self._sleep_with_record(5, '等待課程頁面載入')

                before_path = screenshot_dir / f'exam_{exam_id}_before.png'
                after_path = screenshot_dir / f'exam_{exam_id}_after.png'

                try:
                    # 點擊考試名稱
                    print('         [1/4] 點擊考試名稱...')
                    exam_detail_page.click_exam_by_name(exam_name, delay=3.0)

                    # 等待進入考試頁面
                    print('         → 等待進入考試頁面...')
                    for _ in range(15):
                        self._sleep_with_record(1, '等待進入考試頁面')
                        if 'learning-activity/full-screen#/exam/' in driver.current_url:
                            print(f'         ✓ 已進入考試頁面')
                            break
                    else:
                        print(f'         ⚠️  等待超時')

                    # Before 截圖
                    print('         [2/4] Before 截圖...')
                    scroll_to_bottom_multi_strategy(driver, max_scrolls=10, wait_time=2.0)
                    self._sleep_with_record(6, '滾動後等待載入')
                    scroll_to_bottom_multi_strategy(driver, max_scrolls=3, wait_time=1.5)
                    driver.save_screenshot(str(before_path))
                    print(f'               ✓ Before: {before_path}')

                    # 開始答題
                    print('         [3/4] 開始答題...')
                    exam_detail_page.click_continue_exam_button(delay=3.0)
                    exam_detail_page.check_agreement_checkbox(delay=3.0)
                    exam_detail_page.click_popup_continue_button(delay=3.0)
                    self._sleep_with_record(5, '等待答題頁面載入')

                    # 提交考卷
                    print('         [4/4] 自動提交考卷...')
                    print('               （Mitmproxy 將攔截並注入答案）')
                    success = exam_answer_page.submit_exam_with_confirmation(auto_submit=True)

                    if success:
                        print('               ✓ 考試已完成')
                        result_stats['success'] += 1
                    else:
                        print('               ✗ 提交失敗')
                        result_stats['failed'] += 1

                    # After 截圖
                    self._sleep_with_record(5, 'After 截圖前等待')
                    print('      → After 截圖...')
                    scroll_to_bottom_multi_strategy(driver, max_scrolls=5, wait_time=1.5)
                    driver.save_screenshot(str(after_path))
                    print(f'         ✓ After: {after_path}')

                except Exception as e:
                    print(f'         ✗ 自動化流程失敗: {e}')
                    logger.exception("考試處理失敗: %s", exam_name)
                    result_stats['failed'] += 1

                    # 錯誤截圖
                    error_path = screenshot_dir / f'exam_{exam_id}_error.png'
                    driver.save_screenshot(str(error_path))
                    after_path = error_path

                exam_screenshots[exam_id] = {
                    'before': str(before_path),
                    'after': str(after_path)
                }
                result_stats['processed'] += 1

                # 結束追蹤考試
                self.end_item(exam_name)

                # 返回課程列表
                if i < len(selected_exams):
                    print('      → 返回課程列表...')
                    driver.get(f'{base_url}/user/courses')
                    self._sleep_with_record(3, '返回課程列表')

            # Step 7: 顯示報告
            print(f'\n✓ 考試處理完成')
            print('━' * 50)

            if hasattr(interceptor, 'get_stats'):
                stats = interceptor.get_stats()
                print('\n【攔截統計】')
                print(f'  總攔截次數 (distribute): {stats.get("intercepted_distributes", 0)}')
                print(f'  總攔截次數 (submission): {stats.get("intercepted_submissions", 0)}')
                print(f'  成功匹配: {stats.get("matched_questions", 0)}')
                print(f'  匹配失敗: {stats.get("unmatched_questions", 0)}')

            print('\n【考試處理詳情】')
            for i, exam in enumerate(selected_exams, 1):
                exam_id = exam.get('api_course_id')
                exam_name = exam.get('exam_name', exam.get('name', '未知考試'))
                print(f'  [{i}] {exam_name}')
                if exam_id in exam_screenshots:
                    print(f'      截圖: {exam_screenshots[exam_id]["after"]}')

            print(f'\n  處理: {result_stats["processed"]} 個')
            print(f'  成功: {result_stats["success"]} 個')
            print(f'  失敗: {result_stats["failed"]} 個')

        except Exception as e:
            logger.exception("h2 考試處理失敗")
            print(f'\n  ✗ 考試處理失敗: {e}')
            result_stats['failed'] = len(selected_exams)

        finally:
            # 清理資源
            if proxy:
                try:
                    proxy.stop()
                except Exception:
                    pass
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass

        return result_stats

    def _execute_exam_mode(
        self,
        result: HybridScanResult,
        programs: List[Dict[str, Any]],
        auto_select: bool
    ) -> OrchestratorResult:
        """
        執行 h3 模式：考試自動答題

        流程:
        1. DOM 提取（只取考試，不需要 mitmproxy 掃描）
        2. 考試選擇
        3. 考試處理
        """
        # Phase 2: DOM 結構提取（只取考試）
        self.start_phase("DOM 結構提取（考試）")
        structure_result = self._structure_service.extract_exams_only(
            self._session_manager.driver,
            programs
        )
        self.end_phase("DOM 結構提取（考試）")

        if not structure_result.success:
            result.error = structure_result.error or "掃描失敗"
            return self._create_result(False, result, result.error)

        result.exams_found = len(structure_result.exam_courses)

        if not structure_result.exam_courses:
            result.error = "未找到任何考試"
            return self._create_result(False, result, result.error)

        # 構建考試數據
        exams_data = []
        for exam in structure_result.exam_courses:
            exams_data.append({
                'name': exam.get('name', '未知考試'),
                'exam_name': exam.get('name', '未知考試'),
                'program_name': exam.get('program_name', ''),
                'api_course_id': exam.get('api_course_id'),
                'item_type': 'exam'
            })

        # Phase 3: 考試選擇
        self.start_phase("考試選擇")
        selected_exams = self._phase3_select_courses(exams_data, auto_select)
        self.end_phase("考試選擇")

        if not selected_exams:
            result.error = "未選擇任何考試"
            return self._create_result(False, result, "未選擇任何考試")

        result.courses_selected = len(selected_exams)

        # Phase 4-6: 載入題庫、處理考試、生成報告
        exam_result = self._process_exams_h3(selected_exams, result)
        return exam_result

    def _initialize_services(self) -> None:
        """初始化服務層"""
        from src.utils.stealth_extractor import StealthExtractor
        from src.core.driver_manager import DriverManager
        from src.core.cookie_manager import CookieManager
        from src.services.hybrid import (
            BrowserSessionManager,
            CourseStructureService,
            PayloadCaptureService,
            PassRequirementService,
            DurationSendService
        )

        print('\n[初始化] 準備服務...')

        # Stealth 模式
        extractor = StealthExtractor()
        if not extractor.exists():
            extractor.run()
        else:
            print('  ✓ 瀏覽器自動化模式就緒')

        # 核心組件
        self._driver_manager = DriverManager(self.config)
        self._cookie_manager = CookieManager(self._get_config_value('cookies_file'))

        # 服務層
        self._session_manager = BrowserSessionManager(
            self.config,
            self._driver_manager,
            self._cookie_manager
        )

        # CourseStructureService（DOM 提取）
        self._structure_service = CourseStructureService(self.config)

        # PayloadCaptureService（兩階段掃描，注入 structure_service）
        self._payload_service = PayloadCaptureService(
            self.config,
            structure_service=self._structure_service
        )

        self._pass_req_service = PassRequirementService(self.config)
        self._duration_service = DurationSendService(self.config)

        print('  ✓ 服務已初始化')

    def _phase1_initialize_and_login(
        self,
        max_retries: int,
        use_legacy_login: bool = False
    ) -> bool:
        """
        階段 1: 登入與初始化

        Args:
            max_retries: 最大重試次數
            use_legacy_login: 是否使用舊登入邏輯（BSM.login）
                - False: 使用 _login_with_retry (LoginService，有頁面刷新)
                - True: 使用 BSM.login (直接重試，無頁面刷新)

        Returns:
            bool: 是否成功
        """
        print('\n[階段 1] 登入與初始化...')
        print('━' * 70)

        # 啟動瀏覽器
        if not self._session_manager.start_session(use_proxy=False):
            return False

        # 登入（使用統一登入機制）
        if use_legacy_login:
            # 舊邏輯：BSM.login（無頁面刷新）
            if not self._session_manager.login(max_retries):
                return False
        else:
            # 新邏輯：_login_with_retry（有頁面刷新，與 IR 一致）
            from src.pages.login_page import LoginPage
            login_page = LoginPage(
                self._session_manager.driver,
                self._cookie_manager
            )
            if not self._login_with_retry(
                login_page,
                max_retries=max_retries,
                use_legacy=False,  # 使用 LoginService
                refresh_on_retry=True,  # 重試時刷新頁面（新驗證碼）
                retry_delay=2.0
            ):
                return False

            # 更新 BSM 狀態（保持一致性）
            self._session_manager._state.is_logged_in = True

        # 前往我的課程
        return self._session_manager.goto_my_courses()

    def _relogin_browser(
        self,
        driver: Any,
        use_proxy: bool = False,
        custom_url: Optional[str] = None,
        use_legacy: bool = True
    ) -> bool:
        """
        統一的重新登入方法

        在瀏覽器重啟後重新登入。使用 BaseOrchestrator 的登入機制。

        Args:
            driver: WebDriver 實例
            use_proxy: 是否使用 proxy（用於顯示訊息）
            custom_url: 自定義 URL（如果與 target_http 不同）
            use_legacy: 是否使用舊邏輯（True=單次嘗試，False=LoginService）

        Returns:
            bool: 是否成功登入
        """
        from src.pages.login_page import LoginPage

        login_page = LoginPage(driver, self._cookie_manager)

        # 使用父類的統一登入方法
        success = self._login_with_retry(
            login_page,
            max_retries=3,
            use_legacy=use_legacy,
            refresh_on_retry=True,
            retry_delay=2.0,
            silent=True  # 自己控制訊息
        )

        # 顯示適當的訊息
        proxy_msg = "使用 proxy" if use_proxy else "無 proxy"
        if success:
            print(f'  ✓ 已重新登入（{proxy_msg}）')
        else:
            print(f'  ⚠️ 重新登入失敗（{proxy_msg}）')

        return success

    def _get_programs(self) -> List[Dict[str, Any]]:
        """獲取課程計畫列表"""
        from src.pages.course_list_page import CourseListPage

        course_list_page = CourseListPage(self._session_manager.driver)
        programs = course_list_page.get_in_progress_programs()

        if not programs:
            print('  ⚠️  未找到任何「修習中」的課程')
        else:
            print(f'  ✓ 找到 {len(programs)} 個課程計畫')

        return programs

    def _build_courses_data(self, payloads) -> List[Dict[str, Any]]:
        """構建課程數據結構"""
        courses_data = []

        for captured in payloads:
            course_data = {
                "api_course_id": captured.course_id,
                "program_name": captured.program_name,
                "course_code": captured.course_code,
                "course_name": captured.course_name,
                "required_minutes": 100,  # 預設值，後續會更新
                "payload": captured.payload,
                "item_type": captured.item_type
            }
            courses_data.append(course_data)

        return courses_data

    def _phase3_select_courses(
        self,
        courses_data: List[Dict[str, Any]],
        auto_select: bool
    ) -> List[Dict[str, Any]]:
        """階段 3: 課程選擇"""
        print('\n[階段 3] 課程選擇...')
        print('━' * 70)

        if auto_select:
            print(f'  ✓ 自動選擇所有 {len(courses_data)} 個項目')
            return courses_data.copy()

        from src.utils.course_selection_menu import CourseSelectionMenu

        selection_menu = CourseSelectionMenu(courses_data)
        selected = selection_menu.run()

        if selected:
            print(f'\n✓ 已選擇 {len(selected)} 個項目')
        else:
            print('\n[已取消] 用戶取消選擇')

        return selected or []

    def _create_result(
        self,
        success: bool,
        scan_result: HybridScanResult,
        error: Optional[str] = None
    ) -> OrchestratorResult:
        """創建 OrchestratorResult"""
        return OrchestratorResult(
            success=success,
            error=error,
            data={
                'mode': self.mode.value,
                'programs_scanned': scan_result.programs_scanned,
                'general_courses_found': scan_result.general_courses_found,
                'exams_found': scan_result.exams_found,
                'payloads_captured': scan_result.payloads_captured,
                'courses_selected': scan_result.courses_selected,
                'courses_processed': scan_result.courses_processed,
                'exams_processed': scan_result.exams_processed,
                'success_count': scan_result.success_count,
                'failed_count': scan_result.failed_count,
                'total_increase_minutes': scan_result.total_increase_minutes,
            }
        )

    def _process_exams_h3(
        self,
        selected_exams: List[Dict[str, Any]],
        result: HybridScanResult
    ) -> OrchestratorResult:
        """
        處理 h3 考試自動答題

        完整流程（參照 Legacy menu.py:2914-3412）：
        1. Phase 4: 載入題庫並初始化攔截器
        2. Phase 5: 啟動 mitmproxy，重啟瀏覽器，處理考試
        3. Phase 6: 生成報告

        Args:
            selected_exams: 選中的考試列表
            result: 掃描結果對象

        Returns:
            OrchestratorResult: 執行結果
        """
        from pathlib import Path
        from urllib.parse import urlparse

        from src.services.question_bank import QuestionBankService
        from src.services.answer_matcher import AnswerMatcher
        from src.api.interceptors.exam_auto_answer import ExamAutoAnswerInterceptor
        from src.core.proxy_manager import ProxyManager
        from src.pages.exam_detail_page import ExamDetailPage
        from src.pages.exam_answer_page import ExamAnswerPage
        from src.utils.scroll_utils import scroll_to_bottom_multi_strategy

        proxy = None
        driver = None
        exam_screenshots = {}

        try:
            # ================================================================
            # Phase 4: 載入題庫並初始化攔截器
            # ================================================================
            self.start_phase("載入題庫")
            print('\n[階段 4/6] 載入題庫並初始化攔截器...')
            print('━' * 70)

            # 初始化題庫服務（不立即加載，將在處理每個考試時動態加載）
            question_bank_service = QuestionBankService(self.config)
            answer_matcher = AnswerMatcher(confidence_threshold=0.85)

            print('  ✓ 題庫服務已初始化')
            print('  ✓ 答案匹配器已初始化（信心閾值: 0.85）')
            print('  ℹ️  題庫將在處理每個考試時動態加載')

            # 初始化攔截器
            interceptor = ExamAutoAnswerInterceptor(
                question_bank_service=question_bank_service,
                answer_matcher=answer_matcher,
                enable=True
            )

            print('  ✓ ExamAutoAnswerInterceptor 已初始化')

            self.end_phase("載入題庫")

            # ================================================================
            # Phase 5: 啟動 mitmproxy 並處理考試
            # ================================================================
            self.start_phase("處理考試")
            print('\n[階段 5/6] 啟動 mitmproxy 並處理考試...')
            print('━' * 70)

            # 啟動 mitmproxy
            proxy = ProxyManager(self.config, interceptors=[interceptor])
            proxy.start()
            print('  ✓ Mitmproxy 已啟動（考試自動答題模式）')

            # 關閉當前瀏覽器（無 proxy）
            print('\n[準備處理] 重新啟動瀏覽器（使用 proxy）...')
            if self._session_manager:
                self._session_manager.close()

            # 重新啟動瀏覽器（使用 proxy）
            driver = self._driver_manager.create_driver(use_proxy=True)

            # 重新登入（使用統一方法）
            self._relogin_browser(driver, use_proxy=True)

            # 提取 base_url
            target_url = self._get_config_value('target_http')
            parsed = urlparse(target_url)
            base_url = f'{parsed.scheme}://{parsed.netloc}'

            # 準備截圖目錄
            screenshot_dir = Path('reports/exam_screenshots')
            screenshot_dir.mkdir(parents=True, exist_ok=True)

            # 處理每個選中的考試
            print('\n[處理考試] 開始處理選中的考試...')

            exam_detail_page = ExamDetailPage(driver)
            exam_answer_page = ExamAnswerPage(driver)

            for i, exam in enumerate(selected_exams, 1):
                exam_id = exam.get('api_course_id')
                program_name = exam.get('program_name', f'考試 {i}')
                exam_name = exam.get('exam_name', '未知考試')

                # 開始追蹤考試
                self.start_item(exam_name, program_name, 'exam')

                print(f'\n  [{i}/{len(selected_exams)}] {program_name[:50]}')
                print(f'      考試名稱: {exam_name}')

                # ✅ 動態切換題庫：為當前考試加載對應的題庫
                print(f'      → 載入題庫: {program_name[:40]}...')
                question_count = question_bank_service.load_question_bank(program_name)
                if question_count > 0:
                    print(f'         ✓ 題庫已載入: {question_count} 題')
                else:
                    print(f'         ⚠️  題庫載入失敗或為空')

                # 前往課程頁面
                exam_url = f"{target_url}/course/{exam_id}/content#/"
                print(f'      → 前往課程頁面...')
                driver.get(exam_url)
                self._sleep_with_record(5, '等待課程頁面載入')

                before_path = screenshot_dir / f'exam_{exam_id}_before.png'
                after_path = screenshot_dir / f'exam_{exam_id}_after.png'

                try:
                    # 步驟 1: 點擊考試名稱（進入測驗區）
                    print('         [1/4] 點擊考試名稱...')
                    exam_detail_page.click_exam_by_name(exam_name, delay=3.0)

                    # 等待進入考試頁面
                    print('         → 等待進入考試頁面...')
                    max_wait = 15
                    for wait_sec in range(max_wait):
                        self._sleep_with_record(1, '等待進入考試頁面')
                        current_url = driver.current_url
                        if 'learning-activity/full-screen#/exam/' in current_url:
                            print(f'         ✓ 已進入考試頁面')
                            break
                    else:
                        print(f'         ⚠️  等待超時，當前 URL: {current_url[:70]}...')

                    # Before 截圖（在測驗區，開始答題前）
                    print('         [2/4] Before 截圖（開始答題前）...')

                    # 使用多策略滾動函數載入所有 Lazy-load 內容
                    print('               → 多策略滾動載入頁面內容...')
                    scroll_count = scroll_to_bottom_multi_strategy(
                        driver, max_scrolls=10, wait_time=2.0
                    )
                    print(f'               → 完成 {scroll_count} 次滾動迭代')

                    # 額外等待確保元素完全載入
                    self._sleep_with_record(6, '滾動後等待載入')

                    # 最後再執行一次多策略滾動確認
                    scroll_to_bottom_multi_strategy(driver, max_scrolls=3, wait_time=1.5)

                    # 截圖
                    driver.save_screenshot(str(before_path))
                    print(f'               ✓ Before: {before_path}')

                    # 步驟 3: 點擊"繼續答題"按鈕並勾選同意
                    print('         [3/4] 開始答題...')
                    exam_detail_page.click_continue_exam_button(delay=3.0)
                    exam_detail_page.check_agreement_checkbox(delay=3.0)
                    exam_detail_page.click_popup_continue_button(delay=3.0)
                    self._sleep_with_record(5, '等待答題頁面載入')

                    # 步驟 4: 自動提交考卷（Mitmproxy 會攔截並注入答案）
                    print('         [4/4] 自動提交考卷...')
                    print('               （Mitmproxy 將攔截並注入答案）')
                    success = exam_answer_page.submit_exam_with_confirmation(
                        auto_submit=True
                    )

                    if success:
                        print('               ✓ 考試已完成')
                        result.success_count += 1
                    else:
                        print('               ✗ 提交失敗')
                        result.failed_count += 1

                    # 等待結果顯示
                    self._sleep_with_record(5, '等待結果顯示')

                    # After 截圖（提交後）
                    print('      → After 截圖（提交後）...')
                    self._sleep_with_record(2, 'After 截圖前等待')
                    scroll_to_bottom_multi_strategy(driver, max_scrolls=5, wait_time=1.5)
                    driver.save_screenshot(str(after_path))
                    print(f'         ✓ After: {after_path}')

                except Exception as e:
                    print(f'         ✗ 自動化流程失敗: {e}')
                    logger.exception("考試處理失敗: %s", exam_name)
                    result.failed_count += 1

                    # 錯誤截圖
                    error_path = screenshot_dir / f'exam_{exam_id}_error.png'
                    driver.save_screenshot(str(error_path))
                    print(f'         ✓ Error: {error_path}')
                    after_path = error_path

                exam_screenshots[exam_id] = {
                    'before': str(before_path),
                    'after': str(after_path)
                }

                result.exams_processed += 1

                # 結束追蹤考試
                self.end_item(exam_name)

                # 返回課程列表（準備處理下一個考試）
                if i < len(selected_exams):
                    print('      → 返回課程列表...')
                    driver.get(f'{base_url}/user/courses')
                    self._sleep_with_record(3, '返回課程列表')

            print(f'\n✓ 已處理 {len(selected_exams)} 個考試')

            # 停止 mitmproxy
            proxy.stop()
            proxy = None

            self.end_phase("處理考試")

            # ================================================================
            # Phase 6: 顯示攔截統計報告
            # ================================================================
            self.start_phase("生成報告")
            print('\n[階段 6/6] 生成攔截統計報告...')
            print('━' * 70)

            print('\n' + '=' * 70)
            print('  考試自動答題報告')
            print('=' * 70)

            # 獲取攔截器統計
            if hasattr(interceptor, 'get_stats'):
                stats = interceptor.get_stats()
                print('\n【攔截統計】')
                print(f'  總攔截次數 (distribute): {stats.get("intercepted_distributes", 0)}')
                print(f'  總攔截次數 (submission): {stats.get("intercepted_submissions", 0)}')
                print(f'  總題目數: {stats.get("total_questions", 0)}')
                print(f'  成功匹配: {stats.get("matched_questions", 0)}')
                print(f'  匹配失敗: {stats.get("unmatched_questions", 0)}')

            # 顯示每個考試的詳細信息
            print('\n【考試處理詳情】')

            for i, exam in enumerate(selected_exams, 1):
                exam_id = exam.get('api_course_id')
                program_name = exam.get('program_name', f'考試 {i}')

                print(f'\n  [{i}] {program_name[:55]}')
                print(f'      狀態: ✓ 已處理')

                if exam_id in exam_screenshots:
                    screenshots = exam_screenshots[exam_id]
                    print(f'      截圖 (before): {screenshots["before"]}')
                    print(f'      截圖 (after):  {screenshots["after"]}')

            print('\n' + '=' * 70)
            print(f'考試自動答題完成！')
            print(f'  - 處理考試: {result.exams_processed} 個')
            print(f'  - 成功: {result.success_count} 個')
            print(f'  - 失敗: {result.failed_count} 個')
            print(f'  - 截圖保存: reports/exam_screenshots/')
            print('=' * 70)

            self.end_phase("生成報告")

            return self._create_result(True, result)

        except Exception as e:
            logger.exception("h3 考試處理失敗")
            result.error = str(e)
            return self._create_result(False, result, str(e))

        finally:
            # 清理資源
            if proxy:
                try:
                    proxy.stop()
                except Exception:
                    pass
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass

    def _process_courses_internal(
        self,
        selected_courses: List[Dict[str, Any]],
        driver: Any
    ) -> Dict[str, int]:
        """
        處理一般課程（內部版本，接受 driver 參數）

        用於 h2 批量模式，使用指定的 driver 發送 Payload。
        參照 Legacy menu.py Stage 5 的邏輯。

        Args:
            selected_courses: 已選擇的課程列表
            driver: WebDriver 實例

        Returns:
            Dict: {'processed': int, 'success': int, 'failed': int}
        """
        import requests

        print(f'\n[處理課程] 發送 {len(selected_courses)} 個課程的 Payload...')

        # 獲取配置（確保轉換為整數）
        duration_increase = int(self._get_config_value('visit_duration_increase', 6000))
        target_http = self._get_config_value('target_http')
        api_url = f"{target_http}/statistics/api/user-visits"

        print(f'  配置: 增加 {duration_increase} 秒 ({duration_increase//60} 分鐘)')

        # 獲取認證信息（從瀏覽器）
        cookies_dict = {
            cookie['name']: cookie['value']
            for cookie in driver.get_cookies()
        }
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': driver.execute_script("return navigator.userAgent"),
            'Referer': f'{target_http}/learning/my-courses'
        }

        success_count = 0
        failed_count = 0

        for i, course in enumerate(selected_courses, 1):
            program_name = course.get('name', course.get('program_name', f'課程 {i}'))
            course_code = course.get('course_code', 'N/A')

            # 開始追蹤課程
            self.start_item(program_name, '', 'course')

            print(f'\n  [{i}/{len(selected_courses)}] {program_name[:50]}...')

            # 使用已捕獲的 payload
            payload = course.get('payload')
            if not payload:
                print(f'      ✗ 無 payload，跳過')
                failed_count += 1
                self.end_item(program_name)
                continue

            # 修改 visit_duration
            modified_payload = payload.copy()
            original_duration = modified_payload.get('visit_duration', 0)
            modified_payload['visit_duration'] = original_duration + duration_increase

            print(f'      發送時長: {modified_payload["visit_duration"]} 秒 (+{duration_increase})')

            try:
                response = requests.post(
                    api_url,
                    json=modified_payload,
                    cookies=cookies_dict,
                    headers=headers,
                    timeout=10,
                    verify=False
                )

                if response.status_code in (200, 204):
                    print(f'      ✓ 發送成功 (HTTP {response.status_code})')
                    success_count += 1
                else:
                    print(f'      ✗ 發送失敗 (HTTP {response.status_code})')
                    failed_count += 1

            except Exception as e:
                print(f'      ✗ 發送失敗: {e}')
                failed_count += 1

            # 結束追蹤課程
            self.end_item(program_name)

            self._sleep_with_record(1, '請求間隔')

        print(f'\n  ✓ 課程處理完成: {success_count} 成功, {failed_count} 失敗')

        return {
            'processed': len(selected_courses),
            'success': success_count,
            'failed': failed_count
        }

    def _process_exams_internal(
        self,
        selected_exams: List[Dict[str, Any]],
        driver: Any,
        exam_interceptor: Any,
        question_bank_service: Any,
        base_url: str,
        target_url: str
    ) -> Dict[str, int]:
        """
        處理考試（內部版本，接受已啟動的 driver 和 interceptor）

        用於 h2 批量模式，使用指定的 driver 和 interceptor 處理考試。
        不重啟 mitmproxy（已在外部啟動）。
        參照 Legacy menu.py Stage 6 的邏輯。

        Args:
            selected_exams: 已選擇的考試列表
            driver: WebDriver 實例（已配置 proxy）
            exam_interceptor: ExamAutoAnswerInterceptor 實例（已啟用）
            question_bank_service: QuestionBankService 實例
            base_url: 基礎 URL（例如 https://example.com）
            target_url: 目標 URL（例如 https://example.com/learning）

        Returns:
            Dict: {'processed': int, 'success': int, 'failed': int}
        """
        from pathlib import Path
        from src.pages.exam_detail_page import ExamDetailPage
        from src.pages.exam_answer_page import ExamAnswerPage
        from src.utils.scroll_utils import scroll_to_bottom_multi_strategy

        result_stats = {'processed': 0, 'success': 0, 'failed': 0}
        exam_screenshots = {}

        print(f'\n[處理考試] 共選擇 {len(selected_exams)} 個考試')
        print('━' * 50)

        # 準備截圖目錄
        screenshot_dir = Path('reports/exam_screenshots')
        screenshot_dir.mkdir(parents=True, exist_ok=True)

        exam_detail_page = ExamDetailPage(driver)
        exam_answer_page = ExamAnswerPage(driver)

        for i, exam in enumerate(selected_exams, 1):
            exam_id = exam.get('api_course_id')
            program_name = exam.get('program_name', f'考試 {i}')
            exam_name = exam.get('exam_name', exam.get('name', '未知考試'))

            # 開始追蹤考試
            self.start_item(exam_name, program_name, 'exam')

            print(f'\n  [{i}/{len(selected_exams)}] {program_name[:50]}')
            print(f'      考試名稱: {exam_name}')

            # 動態載入題庫
            print(f'      → 載入題庫: {program_name[:40]}...')
            question_count = question_bank_service.load_question_bank(program_name)
            if question_count > 0:
                print(f'         ✓ 題庫已載入: {question_count} 題')
            else:
                print(f'         ⚠️  題庫載入失敗或為空')

            # 前往課程頁面
            exam_url = f"{target_url}/course/{exam_id}/content#/"
            print(f'      → 前往課程頁面...')
            driver.get(exam_url)
            self._sleep_with_record(5, '等待課程頁面載入')

            before_path = screenshot_dir / f'exam_{exam_id}_before.png'
            after_path = screenshot_dir / f'exam_{exam_id}_after.png'

            try:
                # 點擊考試名稱
                print('         [1/4] 點擊考試名稱...')
                exam_detail_page.click_exam_by_name(exam_name, delay=3.0)

                # 等待進入考試頁面
                print('         → 等待進入考試頁面...')
                for _ in range(15):
                    self._sleep_with_record(1, '等待考試頁面跳轉')
                    if 'learning-activity/full-screen#/exam/' in driver.current_url:
                        print(f'         ✓ 已進入考試頁面')
                        break
                else:
                    print(f'         ⚠️  等待超時')

                # Before 截圖
                print('         [2/4] Before 截圖...')
                scroll_to_bottom_multi_strategy(driver, max_scrolls=10, wait_time=2.0)
                self._sleep_with_record(6, '滾動後等待載入')
                scroll_to_bottom_multi_strategy(driver, max_scrolls=3, wait_time=1.5)
                driver.save_screenshot(str(before_path))
                print(f'               ✓ Before: {before_path}')

                # 開始答題
                print('         [3/4] 開始答題...')
                exam_detail_page.click_continue_exam_button(delay=3.0)
                exam_detail_page.check_agreement_checkbox(delay=3.0)
                exam_detail_page.click_popup_continue_button(delay=3.0)
                self._sleep_with_record(5, '等待答題頁面載入')

                # 提交考卷
                print('         [4/4] 自動提交考卷...')
                print('               （Mitmproxy 將攔截並注入答案）')
                success = exam_answer_page.submit_exam_with_confirmation(auto_submit=True)

                if success:
                    print('               ✓ 考試已完成')
                    result_stats['success'] += 1
                else:
                    print('               ✗ 提交失敗')
                    result_stats['failed'] += 1

                # After 截圖
                self._sleep_with_record(5, 'After 截圖前等待')
                print('      → After 截圖...')
                scroll_to_bottom_multi_strategy(driver, max_scrolls=5, wait_time=1.5)
                driver.save_screenshot(str(after_path))
                print(f'         ✓ After: {after_path}')

            except Exception as e:
                print(f'         ✗ 自動化流程失敗: {e}')
                logger.exception("考試處理失敗: %s", exam_name)
                result_stats['failed'] += 1

                # 錯誤截圖
                error_path = screenshot_dir / f'exam_{exam_id}_error.png'
                driver.save_screenshot(str(error_path))
                after_path = error_path

            exam_screenshots[exam_id] = {
                'before': str(before_path),
                'after': str(after_path)
            }
            result_stats['processed'] += 1

            # 結束追蹤考試
            self.end_item(exam_name)

            # 返回課程列表
            if i < len(selected_exams):
                print('      → 返回課程列表...')
                driver.get(f'{base_url}/user/courses')
                self._sleep_with_record(3, '返回課程列表')

        # 顯示報告
        print(f'\n✓ 考試處理完成')
        print('━' * 50)

        if hasattr(exam_interceptor, 'get_stats'):
            stats = exam_interceptor.get_stats()
            print('\n【攔截統計】')
            print(f'  總攔截次數 (distribute): {stats.get("intercepted_distributes", 0)}')
            print(f'  總攔截次數 (submission): {stats.get("intercepted_submissions", 0)}')
            print(f'  成功匹配: {stats.get("matched_questions", 0)}')
            print(f'  匹配失敗: {stats.get("unmatched_questions", 0)}')

        print('\n【考試處理詳情】')
        for i, exam in enumerate(selected_exams, 1):
            exam_id = exam.get('api_course_id')
            exam_name = exam.get('exam_name', exam.get('name', '未知考試'))
            print(f'  [{i}] {exam_name}')
            if exam_id in exam_screenshots:
                print(f'      截圖: {exam_screenshots[exam_id]["after"]}')

        print(f'\n  處理: {result_stats["processed"]} 個')
        print(f'  成功: {result_stats["success"]} 個')
        print(f'  失敗: {result_stats["failed"]} 個')

        return result_stats

    def _cleanup(self) -> None:
        """清理資源"""
        print('\n[清理] 釋放資源...')

        # 先關閉瀏覽器（減少對 proxy 的連接）
        if self._session_manager:
            try:
                self._session_manager.close()
                print('  ✓ 瀏覽器已關閉')
            except Exception as e:
                logger.warning("關閉瀏覽器失敗: %s", e)

        # 停止 proxy（內部會等待端口釋放）
        if self._payload_service:
            try:
                self._payload_service.stop_proxy()
            except Exception as e:
                logger.warning("停止 proxy 失敗: %s", e)

        print('  ✓ 資源已釋放')

    def _get_config_value(self, key: str, default: Any = None) -> Any:
        """從配置中取得值"""
        if hasattr(self.config, 'get') and callable(self.config.get):
            return self.config.get(key, default)
        return getattr(self.config, key, default)
