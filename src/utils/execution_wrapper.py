#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
ExecutionWrapper - 標準化執行包裝器
統一管理時間追蹤和截圖功能，使所有功能選項都能一致地使用這些功能

Created: 2025-12-21
Author: Claude Code (Sonnet 4.5) with wizard03
"""

from typing import Dict, Optional, TYPE_CHECKING
from .time_tracker import TimeTracker

if TYPE_CHECKING:
    # 僅用於類型檢查，不會在運行時導入
    from .screenshot_utils import ScreenshotManager


class ExecutionWrapper:
    """
    標準化執行包裝器 - 統一管理時間追蹤和截圖功能

    使用範例:
        with ExecutionWrapper(config, "功能名稱") as wrapper:
            wrapper.start_phase("初始化")
            # ... 執行功能代碼 ...
            wrapper.end_phase("初始化")

            wrapper.start_item("課程1", item_type="course")
            # ... 處理課程 ...
            wrapper.take_screenshot(driver, "課程1", sequence=1)
            wrapper.record_delay(10.0, "等待頁面載入")
            wrapper.end_item()
    """

    def __init__(
        self,
        config,
        function_name: str,
        enable_tracking: bool = True,
        enable_screenshot: bool = True
    ):
        """
        初始化執行包裝器

        Args:
            config: ConfigLoader 實例
            function_name: 功能名稱（用於報告）
            enable_tracking: 是否啟用時間追蹤（預設 True）
            enable_screenshot: 是否啟用截圖（預設 True）
        """
        self.config = config
        self.function_name = function_name
        self.enable_tracking = enable_tracking
        self.enable_screenshot = enable_screenshot

        # 初始化時間追蹤器
        if enable_tracking:
            self.time_tracker = TimeTracker()
        else:
            self.time_tracker = None

        # 初始化截圖管理器（延遲導入）
        if enable_screenshot:
            try:
                timing_config = config.load_timing_config()
                # 檢查配置中是否啟用截圖
                screenshot_config = timing_config.get('screenshot', {})
                if screenshot_config.get('enabled', False):
                    # 延遲導入 ScreenshotManager（避免在不需要時導入 PIL）
                    from .screenshot_utils import ScreenshotManager
                    self.screenshot_manager = ScreenshotManager(config, timing_config)
                else:
                    self.screenshot_manager = None
                    print(f'[執行包裝器] 截圖功能在配置中已禁用')
            except Exception as e:
                print(f'[執行包裝器] 初始化截圖管理器失敗: {e}')
                self.screenshot_manager = None
        else:
            self.screenshot_manager = None

    # ===== 上下文管理器 =====

    def __enter__(self):
        """進入上下文管理器"""
        if self.time_tracker:
            self.time_tracker.start_program()
            print(f'\n{"=" * 80}')
            print(f'[執行包裝器] {self.function_name} - 開始執行')
            print(f'{"=" * 80}\n')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文管理器"""
        if self.time_tracker:
            self.time_tracker.end_program()
            print(f'\n{"=" * 80}')
            print(f'[執行包裝器] {self.function_name} - 執行結束')
            print(f'{"=" * 80}\n')

            # 自動生成報告
            report_dir = f'reports/{self.function_name.replace(" ", "_").replace("/", "_")}'
            try:
                self.time_tracker.print_report(save_to_file=True, report_dir=report_dir)
            except Exception as e:
                print(f'[執行包裝器] 生成報告失敗: {e}')
                # 即使生成報告失敗，也嘗試打印控制台輸出
                try:
                    self.time_tracker.print_report(save_to_file=False)
                except:
                    pass

        # 不抑制異常
        return False

    # ===== 階段管理 =====

    def start_phase(self, phase_name: str):
        """
        開始階段

        Args:
            phase_name: 階段名稱（如："初始化"、"處理課程"）
        """
        if self.time_tracker:
            self.time_tracker.start_phase(phase_name)

    def end_phase(self, phase_name: str = None):
        """
        結束階段

        Args:
            phase_name: 階段名稱（可選，預設結束當前階段）
        """
        if self.time_tracker:
            if phase_name:
                self.time_tracker.end_phase(phase_name)
            elif self.time_tracker.current_phase:
                self.time_tracker.end_phase(self.time_tracker.current_phase)

    # ===== 項目管理（課程/考試） =====

    def start_item(
        self,
        item_name: str,
        program_name: str = '',
        item_type: str = 'course'
    ):
        """
        開始處理項目（課程或考試）

        Args:
            item_name: 項目名稱
            program_name: 課程計畫名稱（可選）
            item_type: 項目類型 ('course' 或 'exam')
        """
        if self.time_tracker:
            if item_type == 'exam':
                self.time_tracker.start_exam(item_name, program_name)
            else:
                self.time_tracker.start_course(item_name, program_name)

    def end_item(self, item_name: str = None):
        """
        結束處理項目

        Args:
            item_name: 項目名稱（可選，預設結束當前項目）
        """
        if self.time_tracker:
            # 根據當前項目類型決定調用哪個方法
            if self.time_tracker.current_exam:
                self.time_tracker.end_exam(item_name)
            elif self.time_tracker.current_course:
                self.time_tracker.end_course(item_name)

    # ===== 延遲記錄 =====

    def record_delay(self, delay_seconds: float, description: str = ''):
        """
        記錄延遲時間

        Args:
            delay_seconds: 延遲秒數
            description: 延遲描述（可選）
        """
        if self.time_tracker:
            self.time_tracker.record_delay(delay_seconds, description)

    # ===== 截圖管理 =====

    def take_screenshot(
        self,
        driver,
        item_name: str,
        sequence: int = 1
    ) -> Optional[str]:
        """
        截取網頁

        Args:
            driver: Selenium WebDriver
            item_name: 項目名稱（用於檔名）
            sequence: 序號（用於區分同一項目的多張截圖）

        Returns:
            str: 截圖檔案路徑，若未啟用則返回 None
        """
        if self.screenshot_manager:
            try:
                return self.screenshot_manager.take_screenshot(driver, item_name, sequence)
            except Exception as e:
                print(f'[執行包裝器] 截圖失敗: {e}')
                return None
        return None

    # ===== 使用者輸入等待 =====

    def start_user_wait(self, description: str = '等待使用者輸入'):
        """
        開始記錄使用者輸入等待時間

        Args:
            description: 等待描述
        """
        if self.time_tracker:
            self.time_tracker.start_user_wait(description)

    def end_user_wait(self):
        """結束記錄使用者輸入等待時間"""
        if self.time_tracker:
            self.time_tracker.end_user_wait()

    # ===== 工具方法 =====

    def get_stats(self) -> Dict:
        """
        取得統計數據

        Returns:
            Dict: 按課程計畫分組的統計數據
        """
        if self.time_tracker:
            return self.time_tracker.get_program_stats()
        return {}

    def is_tracking_enabled(self) -> bool:
        """
        檢查是否啟用時間追蹤

        Returns:
            bool: True 如果啟用，False 如果未啟用
        """
        return self.time_tracker is not None

    def is_screenshot_enabled(self) -> bool:
        """
        檢查是否啟用截圖

        Returns:
            bool: True 如果啟用，False 如果未啟用
        """
        return self.screenshot_manager is not None

    def get_time_tracker(self) -> Optional[TimeTracker]:
        """
        取得時間追蹤器實例（用於高級使用）

        Returns:
            Optional[TimeTracker]: TimeTracker 實例，若未啟用則返回 None
        """
        return self.time_tracker

    def get_screenshot_manager(self) -> Optional['ScreenshotManager']:
        """
        取得截圖管理器實例（用於高級使用）

        Returns:
            Optional[ScreenshotManager]: ScreenshotManager 實例，若未啟用則返回 None
        """
        return self.screenshot_manager

    # ===== 便捷方法 =====

    def print_status(self):
        """打印當前狀態"""
        print(f'\n[執行包裝器狀態]')
        print(f'  功能名稱: {self.function_name}')
        print(f'  時間追蹤: {"啟用" if self.is_tracking_enabled() else "禁用"}')
        print(f'  截圖功能: {"啟用" if self.is_screenshot_enabled() else "禁用"}')

        if self.time_tracker:
            if self.time_tracker.current_phase:
                print(f'  當前階段: {self.time_tracker.current_phase}')
            if self.time_tracker.current_course:
                print(f'  當前課程: {self.time_tracker.current_course}')
            if self.time_tracker.current_exam:
                print(f'  當前考試: {self.time_tracker.current_exam}')

    def __repr__(self) -> str:
        """字串表示"""
        tracking = "enabled" if self.is_tracking_enabled() else "disabled"
        screenshot = "enabled" if self.is_screenshot_enabled() else "disabled"
        return (f"ExecutionWrapper(function='{self.function_name}', "
                f"tracking={tracking}, screenshot={screenshot})")
