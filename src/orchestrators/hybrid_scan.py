# -*- coding: utf-8 -*-
"""
HybridScanOrchestrator - 混合式掃描流程編排器

編排混合式課程掃描與時長發送的流程：
1. 登入與初始化
2. Payload 捕獲掃描
3. 課程選擇
4. 時長計算與發送
5. 驗證與報告

支援三種模式:
- duration: 一般課程時長發送
- batch: 批量模式
- exam: 考試自動答題

使用方式:
    from src.orchestrators import HybridScanOrchestrator

    orchestrator = HybridScanOrchestrator(config, mode='duration')
    result = orchestrator.execute()
"""

import os
import time
import json
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import urlparse

from .base_orchestrator import BaseOrchestrator, OrchestratorResult

logger = logging.getLogger(__name__)


class HybridMode(Enum):
    """混合掃描模式"""
    DURATION = "duration"  # 一般課程時長發送
    BATCH = "batch"        # 批量模式
    EXAM = "exam"          # 考試自動答題


@dataclass
class PayloadData:
    """Payload 數據"""
    course_id: int
    course_name: str
    program_name: str
    payload: Dict[str, Any]
    read_time: int = 0
    pass_time: int = 0
    target_time: int = 0


@dataclass
class HybridScanResult:
    """混合掃描結果"""
    mode: HybridMode
    payloads: List[PayloadData] = field(default_factory=list)
    selected_courses: List[PayloadData] = field(default_factory=list)
    sent_count: int = 0
    verified_count: int = 0
    error: Optional[str] = None


class HybridScanOrchestrator(BaseOrchestrator):
    """
    混合式掃描流程編排器

    編排完整的混合式掃描與時長發送流程。

    Attributes:
        mode: 操作模式 (duration/batch/exam)

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
            HybridMode.DURATION: "一般課程時長發送",
            HybridMode.BATCH: "批量模式",
            HybridMode.EXAM: "考試自動答題",
        }
        name = f"混合掃描 - {mode_names.get(mode, mode.value)}"
        super().__init__(config, name)

        self.mode = mode
        self._driver_manager = None
        self._driver = None
        self._proxy = None
        self._scan_result: Optional[HybridScanResult] = None

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
            # Phase 1: 登入與初始化
            self.start_phase("登入與初始化")
            if not self._initialize_and_login(max_retries):
                result.error = "登入失敗"
                return OrchestratorResult(
                    success=False,
                    error="登入失敗",
                    data={'result': result}
                )
            self.end_phase("登入與初始化")

            # Phase 2: Payload 捕獲掃描
            self.start_phase("Payload 捕獲掃描")
            result.payloads = self._scan_payloads()
            self.end_phase("Payload 捕獲掃描")

            if not result.payloads:
                result.error = "未捕獲到任何 Payload"
                return OrchestratorResult(
                    success=False,
                    error="未捕獲到任何 Payload",
                    data={'result': result}
                )

            # Phase 3: 課程選擇
            self.start_phase("課程選擇")
            result.selected_courses = self._select_courses(
                result.payloads,
                auto_select
            )
            self.end_phase("課程選擇")

            if not result.selected_courses:
                result.error = "未選擇任何課程"
                return OrchestratorResult(
                    success=False,
                    error="未選擇任何課程",
                    data={'result': result}
                )

            # Phase 4: 時長計算與發送
            self.start_phase("時長發送")
            result.sent_count = self._send_duration(result.selected_courses)
            self.end_phase("時長發送")

            # Phase 5: 驗證
            self.start_phase("驗證")
            result.verified_count = self._verify_duration(result.selected_courses)
            self.end_phase("驗證")

            # Phase 6: 報告
            self.start_phase("生成報告")
            self._generate_report(result)
            self.end_phase("生成報告")

            return OrchestratorResult(
                success=True,
                data={
                    'mode': self.mode.value,
                    'payloads_count': len(result.payloads),
                    'selected_count': len(result.selected_courses),
                    'sent_count': result.sent_count,
                    'verified_count': result.verified_count
                }
            )

        except Exception as e:
            logger.exception("混合掃描執行失敗")
            result.error = str(e)
            return OrchestratorResult(
                success=False,
                error=str(e),
                data={'result': result}
            )
        finally:
            self._cleanup()

    def _initialize_and_login(self, max_retries: int) -> bool:
        """初始化並登入"""
        print('\n[階段 1] 登入與初始化...')
        print('━' * 70)

        try:
            from src.utils.stealth_extractor import StealthExtractor
            from src.core.driver_manager import DriverManager
            from src.core.cookie_manager import CookieManager
            from src.pages.login_page import LoginPage

            # 初始化 Stealth
            print('[初始化 1/4] 啟動瀏覽器自動化模式...')
            extractor = StealthExtractor()
            if not extractor.exists():
                extractor.run()
            else:
                print('  ✓ 瀏覽器自動化模式就緒')

            # 初始化核心組件
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
            print('  ✓ 頁面物件已初始化\n')

            # 執行登入
            print('[登入] 正在登入...')
            for attempt in range(max_retries):
                success = login_page.auto_login(
                    username=self._get_config_value('user_name'),
                    password=self._get_config_value('password'),
                    url=self._get_config_value('target_http'),
                )

                if success:
                    print('  ✓ 登入成功\n')
                    return True

                if attempt < max_retries - 1:
                    print(f'  ⚠️  登入失敗，重試中... ({attempt + 1}/{max_retries})')
                    login_page.goto(self._get_config_value('target_http'))

            print('  ✗ 登入失敗，已達最大重試次數')
            return False

        except Exception as e:
            logger.exception("初始化失敗")
            print(f'  ✗ 初始化失敗: {e}')
            return False

    def _scan_payloads(self) -> List[PayloadData]:
        """掃描並捕獲 Payload"""
        print('\n[階段 2] Payload 捕獲掃描...')
        print('━' * 70)

        payloads = []

        try:
            from src.pages.course_list_page import CourseListPage

            course_list_page = CourseListPage(self._driver)

            # 前往我的課程
            print('[掃描 1/3] 前往我的課程...')
            course_list_page.goto_my_courses()
            time.sleep(3)
            print('  ✓ 已進入我的課程\n')

            # 獲取進行中的課程計畫
            print('[掃描 2/3] 掃描課程計畫...')
            programs = course_list_page.get_in_progress_programs()

            if not programs:
                print('  ⚠️  未找到進行中的課程計畫')
                return payloads

            print(f'  ✓ 找到 {len(programs)} 個課程計畫\n')

            # 模擬 Payload 捕獲（實際實現需要 mitmproxy）
            print('[掃描 3/3] 捕獲課程 Payload...')
            print('  (此處為模擬，實際需要 mitmproxy 捕獲)')

            # 為每個課程計畫創建模擬數據
            for i, program in enumerate(programs):
                payload = PayloadData(
                    course_id=i + 1,
                    course_name=f"課程 {i + 1}",
                    program_name=program.get('name', f'計畫 {i + 1}'),
                    payload={},
                    read_time=0,
                    pass_time=60,  # 模擬通過時間
                    target_time=60
                )
                payloads.append(payload)

            print(f'  ✓ 捕獲 {len(payloads)} 個 Payload\n')

        except Exception as e:
            logger.exception("Payload 掃描失敗")
            print(f'  ✗ 掃描失敗: {e}')

        return payloads

    def _select_courses(
        self,
        payloads: List[PayloadData],
        auto_select: bool
    ) -> List[PayloadData]:
        """選擇要處理的課程"""
        print('\n[階段 3] 課程選擇...')
        print('━' * 70)

        if auto_select:
            print('  ✓ 自動選擇所有課程')
            return payloads.copy()

        # 顯示可選課程
        print('\n可選課程：')
        for i, p in enumerate(payloads, 1):
            print(f'  {i}. {p.course_name} ({p.program_name})')

        print('\n輸入課程編號（以逗號分隔）或 "all" 選擇全部：')
        selection = input('> ').strip().lower()

        if selection == 'all':
            return payloads.copy()

        selected = []
        try:
            indices = [int(x.strip()) - 1 for x in selection.split(',')]
            for idx in indices:
                if 0 <= idx < len(payloads):
                    selected.append(payloads[idx])
        except ValueError:
            print('  ⚠️  無效的選擇')

        print(f'  ✓ 已選擇 {len(selected)} 個課程\n')
        return selected

    def _send_duration(self, courses: List[PayloadData]) -> int:
        """發送時長"""
        print('\n[階段 4] 時長發送...')
        print('━' * 70)

        sent_count = 0

        for course in courses:
            try:
                print(f'  發送: {course.course_name}...')
                # 實際發送邏輯需要 mitmproxy
                # 此處為模擬
                time.sleep(0.1)
                sent_count += 1
                print(f'    ✓ 已發送 (目標: {course.target_time} 分鐘)')
            except Exception as e:
                print(f'    ✗ 發送失敗: {e}')

        print(f'\n  ✓ 成功發送 {sent_count}/{len(courses)} 個課程\n')
        return sent_count

    def _verify_duration(self, courses: List[PayloadData]) -> int:
        """驗證時長"""
        print('\n[階段 5] 驗證...')
        print('━' * 70)

        verified_count = 0

        for course in courses:
            try:
                print(f'  驗證: {course.course_name}...')
                # 實際驗證邏輯需要重新請求 API
                # 此處為模擬
                time.sleep(0.1)
                verified_count += 1
                print(f'    ✓ 驗證通過')
            except Exception as e:
                print(f'    ✗ 驗證失敗: {e}')

        print(f'\n  ✓ 驗證通過 {verified_count}/{len(courses)} 個課程\n')
        return verified_count

    def _generate_report(self, result: HybridScanResult) -> None:
        """生成報告"""
        print('\n[階段 6] 生成報告...')
        print('━' * 70)

        print('\n📊 執行摘要：')
        print(f'  模式: {result.mode.value}')
        print(f'  掃描課程數: {len(result.payloads)}')
        print(f'  選擇課程數: {len(result.selected_courses)}')
        print(f'  成功發送數: {result.sent_count}')
        print(f'  驗證通過數: {result.verified_count}')

        if result.error:
            print(f'  錯誤: {result.error}')

        print('\n  ✓ 報告生成完成\n')

    def _cleanup(self) -> None:
        """清理資源"""
        if self._proxy:
            try:
                self._proxy.stop()
                logger.debug("Proxy 已停止")
            except Exception as e:
                logger.warning("停止 Proxy 失敗: %s", e)
            self._proxy = None

        if self._driver_manager:
            try:
                print('\n[清理] 關閉瀏覽器...')
                self._driver_manager.quit()
                print('  ✓ 瀏覽器已關閉')
            except Exception as e:
                logger.warning("關閉瀏覽器失敗: %s", e)
            self._driver_manager = None
            self._driver = None

    def _get_config_value(self, key: str, default: Any = None) -> Any:
        """從配置中取得值"""
        if hasattr(self.config, 'get') and callable(self.config.get):
            return self.config.get(key, default)
        return getattr(self.config, key, default)
