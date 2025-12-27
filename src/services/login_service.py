# -*- coding: utf-8 -*-
"""
LoginService - 統一的登入服務

提供帶重試機制的登入功能，消除 menu.py 中重複的登入邏輯。

Usage:
    from src.services.login_service import LoginService

    login_service = LoginService(login_page, config)
    success = login_service.login_with_retry(
        on_success=lambda: print('登入成功'),
        on_retry=lambda attempt, max_retries: print(f'重試 {attempt}/{max_retries}'),
        on_failure=lambda: print('登入失敗')
    )
"""

import time
import logging
from typing import Callable, Optional, Any
from dataclasses import dataclass

from src.constants import MAX_LOGIN_RETRIES, LOGIN_RETRY_DELAY

logger = logging.getLogger(__name__)


@dataclass
class LoginResult:
    """登入結果資料類"""
    success: bool
    attempts: int
    error_message: Optional[str] = None


class LoginService:
    """
    統一的登入服務，提供帶重試機制的登入功能。

    此服務封裝了登入重試邏輯，支援回調函數自定義各階段的行為，
    使得調用方可以靈活處理登入成功、重試、失敗等情況。

    Attributes:
        login_page: LoginPage 實例，用於執行實際的登入操作
        config: 配置物件，包含 user_name, password, target_http 等設定
        max_retries: 最大重試次數，預設為 MAX_LOGIN_RETRIES (3)
        retry_delay: 重試間隔秒數，預設為 LOGIN_RETRY_DELAY (5)
    """

    def __init__(
        self,
        login_page: Any,
        config: Any,
        max_retries: int = None,
        retry_delay: float = None
    ):
        """
        初始化 LoginService。

        Args:
            login_page: LoginPage 實例
            config: 配置物件（需有 get() 方法或對應屬性）
            max_retries: 最大重試次數（可選，預設使用常量）
            retry_delay: 重試間隔秒數（可選，預設使用常量）
        """
        self.login_page = login_page
        self.config = config
        self.max_retries = max_retries if max_retries is not None else MAX_LOGIN_RETRIES
        self.retry_delay = retry_delay if retry_delay is not None else LOGIN_RETRY_DELAY

    def _get_config_value(self, key: str) -> Optional[str]:
        """從配置中取得值，支援 get() 方法或直接屬性存取。"""
        if hasattr(self.config, 'get') and callable(self.config.get):
            return self.config.get(key)
        return getattr(self.config, key, None)

    def login_with_retry(
        self,
        on_success: Optional[Callable[[], None]] = None,
        on_retry: Optional[Callable[[int, int], None]] = None,
        on_failure: Optional[Callable[[], None]] = None,
        refresh_on_retry: bool = True
    ) -> LoginResult:
        """
        執行帶重試機制的登入。

        此方法會嘗試登入最多 max_retries 次，每次失敗後可選擇是否
        刷新頁面以獲取新的驗證碼。

        Args:
            on_success: 登入成功時的回調函數
            on_retry: 重試時的回調函數，接收 (當前嘗試次數, 最大重試次數)
            on_failure: 所有嘗試失敗後的回調函數
            refresh_on_retry: 重試前是否刷新頁面（預設 True）

        Returns:
            LoginResult: 包含登入結果的資料類

        Example:
            result = login_service.login_with_retry(
                on_success=lambda: print('  ✓ 登入成功'),
                on_retry=lambda a, m: print(f'  ⚠️ 重試中... ({a}/{m})'),
                on_failure=lambda: print('  ✗ 登入失敗')
            )

            if result.success:
                # 繼續執行後續操作
                ...
        """
        username = self._get_config_value('user_name')
        password = self._get_config_value('password')
        target_url = self._get_config_value('target_http')

        if not all([username, password, target_url]):
            error_msg = "缺少必要的登入配置 (user_name, password, target_http)"
            logger.error(error_msg)
            return LoginResult(success=False, attempts=0, error_message=error_msg)

        login_success = False
        last_error = None

        for attempt in range(self.max_retries):
            try:
                login_success = self.login_page.auto_login(
                    username=username,
                    password=password,
                    url=target_url
                )

                if login_success:
                    logger.info("登入成功 (嘗試次數: %d)", attempt + 1)
                    if on_success:
                        on_success()
                    return LoginResult(success=True, attempts=attempt + 1)

                # 登入失敗但非異常
                if attempt < self.max_retries - 1:
                    logger.warning("登入失敗，準備重試 (%d/%d)", attempt + 1, self.max_retries)
                    if on_retry:
                        on_retry(attempt + 1, self.max_retries)

                    if refresh_on_retry:
                        # 刷新頁面以獲取新的驗證碼
                        self.login_page.goto(target_url)

                    if self.retry_delay > 0:
                        time.sleep(self.retry_delay)

            except Exception as e:
                last_error = str(e)
                logger.error("登入過程發生錯誤: %s", last_error)

                if attempt < self.max_retries - 1:
                    if on_retry:
                        on_retry(attempt + 1, self.max_retries)

                    if refresh_on_retry:
                        try:
                            self.login_page.goto(target_url)
                        except Exception:
                            pass

                    if self.retry_delay > 0:
                        time.sleep(self.retry_delay)

        # 所有嘗試都失敗
        logger.error("登入失敗，已達最大重試次數 (%d)", self.max_retries)
        if on_failure:
            on_failure()

        return LoginResult(
            success=False,
            attempts=self.max_retries,
            error_message=last_error or "已達最大重試次數"
        )

    def login_simple(self) -> bool:
        """
        簡化的登入方法（無回調）。

        Returns:
            bool: 登入是否成功

        Example:
            if login_service.login_simple():
                print('登入成功')
            else:
                print('登入失敗')
        """
        result = self.login_with_retry()
        return result.success

    def login_with_default_messages(self) -> LoginResult:
        """
        使用預設訊息的登入方法。

        自動印出標準化的成功/重試/失敗訊息。

        Returns:
            LoginResult: 登入結果
        """
        return self.login_with_retry(
            on_success=lambda: print('  ✓ 登入成功'),
            on_retry=lambda a, m: print(f'  ⚠️  登入失敗，重試中... ({a}/{m})'),
            on_failure=lambda: print('  ✗ 登入失敗，已達最大重試次數')
        )
