# -*- coding: utf-8 -*-
"""
BaseOrchestrator - 業務流程編排基類

提供模板方法模式的抽象基類，統一編排複雜的多步驟業務流程。

設計模式:
    - Template Method: execute() 定義骨架，子類實現 _do_execute()
    - Hook Methods: _before_execute() 和 _after_execute() 提供擴展點

使用方式:
    class MyOrchestrator(BaseOrchestrator):
        def _do_execute(self, **kwargs):
            # 實現具體業務邏輯
            return OrchestratorResult(success=True, data={'key': 'value'})

    orchestrator = MyOrchestrator(config, "我的編排器")
    result = orchestrator.execute(param1=value1)
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List
from enum import Enum

from src.utils.execution_wrapper import ExecutionWrapper
from src.config.feature_flags import feature_enabled

logger = logging.getLogger(__name__)


class OrchestratorPhase(Enum):
    """Orchestrator 執行階段"""
    INITIALIZING = "initializing"
    BEFORE_EXECUTE = "before_execute"
    EXECUTING = "executing"
    AFTER_EXECUTE = "after_execute"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class OrchestratorResult:
    """
    Orchestrator 執行結果

    Attributes:
        success: 是否成功
        data: 執行結果數據
        error: 錯誤信息（如果有）
        phase: 最終階段
        metrics: 執行指標（時間、計數等）
    """
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    phase: OrchestratorPhase = OrchestratorPhase.COMPLETED
    metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            'success': self.success,
            'data': self.data,
            'error': self.error,
            'phase': self.phase.value,
            'metrics': self.metrics
        }


class BaseOrchestrator(ABC):
    """
    業務流程編排基類

    使用模板方法模式，提供統一的執行框架。子類只需實現 _do_execute() 方法。

    Attributes:
        config: 配置對象
        name: Orchestrator 名稱
        wrapper: ExecutionWrapper 實例（執行時創建）

    Template Method Pattern:
        execute()
        ├── _before_execute()  # Hook: 執行前準備
        ├── _do_execute()      # Abstract: 核心邏輯（子類必須實現）
        └── _after_execute()   # Hook: 執行後清理

    Example:
        class CourseOrchestrator(BaseOrchestrator):
            def _do_execute(self, course_id: int, **kwargs):
                # 處理課程...
                return OrchestratorResult(
                    success=True,
                    data={'course_id': course_id, 'completed': True}
                )

        orchestrator = CourseOrchestrator(config, "課程處理")
        result = orchestrator.execute(course_id=123)
    """

    def __init__(
        self,
        config: Any,
        name: str,
        enable_tracking: bool = True,
        enable_screenshot: bool = True
    ):
        """
        初始化 Orchestrator

        Args:
            config: 配置對象
            name: Orchestrator 名稱（用於日誌和報告）
            enable_tracking: 是否啟用時間追蹤
            enable_screenshot: 是否啟用截圖
        """
        self.config = config
        self.name = name
        self.enable_tracking = enable_tracking
        self.enable_screenshot = enable_screenshot

        # 執行時狀態
        self.wrapper: Optional[ExecutionWrapper] = None
        self._current_phase = OrchestratorPhase.INITIALIZING
        self._execution_context: Dict[str, Any] = {}

        logger.debug("Orchestrator '%s' 已初始化", self.name)

    @property
    def current_phase(self) -> OrchestratorPhase:
        """取得當前執行階段"""
        return self._current_phase

    def execute(self, **kwargs) -> OrchestratorResult:
        """
        執行業務流程（模板方法）

        此方法定義了執行的骨架：
        1. 創建 ExecutionWrapper
        2. 調用 _before_execute() 準備工作
        3. 調用 _do_execute() 核心邏輯
        4. 調用 _after_execute() 清理工作
        5. 處理異常和返回結果

        Args:
            **kwargs: 傳遞給 _do_execute() 的參數

        Returns:
            OrchestratorResult: 執行結果
        """
        result = OrchestratorResult(success=False, phase=OrchestratorPhase.FAILED)

        try:
            with ExecutionWrapper(
                self.config,
                self.name,
                enable_tracking=self.enable_tracking,
                enable_screenshot=self.enable_screenshot
            ) as wrapper:
                self.wrapper = wrapper
                self._execution_context = kwargs.copy()

                # Phase 1: Before Execute
                self._current_phase = OrchestratorPhase.BEFORE_EXECUTE
                wrapper.start_phase("準備階段")
                self._before_execute(**kwargs)
                wrapper.end_phase("準備階段")

                # Phase 2: Execute
                self._current_phase = OrchestratorPhase.EXECUTING
                wrapper.start_phase("執行階段")
                result = self._do_execute(**kwargs)
                wrapper.end_phase("執行階段")

                # Phase 3: After Execute
                self._current_phase = OrchestratorPhase.AFTER_EXECUTE
                wrapper.start_phase("清理階段")
                self._after_execute(result, **kwargs)
                wrapper.end_phase("清理階段")

                # 標記完成
                self._current_phase = OrchestratorPhase.COMPLETED
                result.phase = OrchestratorPhase.COMPLETED

                # 收集執行指標
                if wrapper.is_tracking_enabled():
                    result.metrics = wrapper.get_stats()

        except Exception as e:
            self._current_phase = OrchestratorPhase.FAILED
            logger.exception("Orchestrator '%s' 執行失敗", self.name)
            result = OrchestratorResult(
                success=False,
                error=str(e),
                phase=OrchestratorPhase.FAILED
            )

            # 嘗試執行錯誤處理
            try:
                self._on_error(e, **kwargs)
            except Exception as cleanup_error:
                logger.warning("錯誤處理失敗: %s", cleanup_error)

        finally:
            self.wrapper = None

        return result

    def _before_execute(self, **kwargs) -> None:
        """
        執行前的準備工作（Hook 方法）

        子類可以覆寫此方法來添加準備邏輯。
        默認實現只記錄日誌。

        Args:
            **kwargs: execute() 傳入的參數
        """
        logger.info("開始執行 '%s'", self.name)

    @abstractmethod
    def _do_execute(self, **kwargs) -> OrchestratorResult:
        """
        核心執行邏輯（抽象方法）

        子類必須實現此方法來定義具體的業務邏輯。

        Args:
            **kwargs: execute() 傳入的參數

        Returns:
            OrchestratorResult: 執行結果
        """
        pass

    def _after_execute(self, result: OrchestratorResult, **kwargs) -> None:
        """
        執行後的清理工作（Hook 方法）

        子類可以覆寫此方法來添加清理邏輯。
        默認實現只記錄日誌。

        Args:
            result: 執行結果
            **kwargs: execute() 傳入的參數
        """
        if result.success:
            logger.info("'%s' 執行成功", self.name)
        else:
            logger.warning("'%s' 執行失敗: %s", self.name, result.error)

    def _on_error(self, error: Exception, **kwargs) -> None:
        """
        錯誤處理（Hook 方法）

        當執行過程中發生異常時調用。子類可以覆寫此方法來添加錯誤恢復邏輯。

        Args:
            error: 發生的異常
            **kwargs: execute() 傳入的參數
        """
        logger.error("'%s' 發生錯誤: %s", self.name, error)

    # ===== 便捷方法（供子類使用）=====

    def start_phase(self, phase_name: str) -> None:
        """開始一個執行階段"""
        if self.wrapper:
            self.wrapper.start_phase(phase_name)

    def end_phase(self, phase_name: str = None) -> None:
        """結束一個執行階段"""
        if self.wrapper:
            self.wrapper.end_phase(phase_name)

    def start_item(
        self,
        item_name: str,
        program_name: str = '',
        item_type: str = 'course'
    ) -> None:
        """開始處理一個項目（課程或考試）"""
        if self.wrapper:
            self.wrapper.start_item(item_name, program_name, item_type)

    def end_item(self, item_name: str = None) -> None:
        """結束處理一個項目"""
        if self.wrapper:
            self.wrapper.end_item(item_name)

    def record_delay(self, delay_seconds: float, description: str = '') -> None:
        """記錄延遲時間"""
        if self.wrapper:
            self.wrapper.record_delay(delay_seconds, description)

    def take_screenshot(
        self,
        driver: Any,
        item_name: str,
        sequence: int = 1
    ) -> Optional[str]:
        """截取網頁"""
        if self.wrapper:
            return self.wrapper.take_screenshot(driver, item_name, sequence)
        return None

    def get_context(self, key: str, default: Any = None) -> Any:
        """取得執行上下文中的值"""
        return self._execution_context.get(key, default)

    def set_context(self, key: str, value: Any) -> None:
        """設置執行上下文中的值"""
        self._execution_context[key] = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', phase={self._current_phase.value})"
