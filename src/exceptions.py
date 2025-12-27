#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EEBot 自定義異常類

此模組定義了 EEBot 專案中使用的所有自定義異常。
所有自定義異常都繼承自 EEBotError 基類。

異常層次結構:
    EEBotError (基類)
    ├── ConfigError (配置相關錯誤)
    ├── LoginError (登入相關錯誤)
    ├── ElementNotFoundError (元素未找到錯誤)
    ├── ProxyStartError (Proxy 啟動錯誤)
    ├── ScanError (掃描相關錯誤)
    └── APIError (API 相關錯誤)
        ├── APIRequestError
        ├── APIResponseError
        └── APITimeoutError

使用方式:
    from src.exceptions import LoginError, APIError

    try:
        # 執行登入
        ...
    except LoginError as e:
        print(f'登入失敗: {e}')
    except APIError as e:
        print(f'API 錯誤 (狀態碼: {e.status_code}): {e}')
"""

from typing import Optional, Any


# =============================================================================
# 基礎異常
# =============================================================================

class EEBotError(Exception):
    """
    EEBot 基礎異常

    所有 EEBot 自定義異常的基類。

    Attributes:
        message (str): 錯誤訊息
        details (dict): 額外的錯誤詳情
    """

    def __init__(self, message: str, **details):
        super().__init__(message)
        self.message = message
        self.details = details

    def __str__(self) -> str:
        if self.details:
            details_str = ', '.join(f'{k}={v}' for k, v in self.details.items())
            return f'{self.message} ({details_str})'
        return self.message

    def to_dict(self) -> dict:
        """將異常轉換為字典"""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'details': self.details
        }


# =============================================================================
# 配置異常
# =============================================================================

class ConfigError(EEBotError):
    """配置相關錯誤"""
    pass


# =============================================================================
# 認證/登入異常
# =============================================================================

class LoginError(EEBotError):
    """
    登入失敗錯誤

    Attributes:
        username (str): 用戶名
        reason (str): 失敗原因
        retry_count (int): 已重試次數
    """

    def __init__(
        self,
        username: Optional[str] = None,
        reason: Optional[str] = None,
        retry_count: int = 0
    ):
        message = '登入失敗'
        if reason:
            message += f': {reason}'

        super().__init__(
            message,
            username=username,
            reason=reason,
            retry_count=retry_count
        )
        self.username = username
        self.reason = reason
        self.retry_count = retry_count


# =============================================================================
# WebDriver 異常
# =============================================================================

class ElementNotFoundError(EEBotError):
    """
    元素未找到錯誤

    Attributes:
        locator: 元素定位器
        timeout (int): 等待超時時間
    """

    def __init__(self, locator: Any, timeout: Optional[int] = None):
        message = f'找不到元素: {locator}'
        if timeout:
            message += f' (超時: {timeout}秒)'

        super().__init__(
            message,
            locator=str(locator),
            timeout=timeout
        )
        self.locator = locator
        self.timeout = timeout


# =============================================================================
# Proxy 異常
# =============================================================================

class ProxyStartError(EEBotError):
    """
    Proxy 啟動失敗錯誤

    Attributes:
        port (int): Proxy 端口
        reason (str): 失敗原因
    """

    def __init__(
        self,
        port: Optional[int] = None,
        reason: Optional[str] = None
    ):
        message = 'MitmProxy 啟動失敗'
        if reason:
            message += f': {reason}'

        super().__init__(message, port=port, reason=reason)
        self.port = port
        self.reason = reason


# =============================================================================
# 掃描異常
# =============================================================================

class ScanError(EEBotError):
    """掃描相關錯誤"""
    pass


# =============================================================================
# API 異常
# =============================================================================

class APIError(EEBotError):
    """
    API 相關錯誤的基類

    Attributes:
        status_code (int): HTTP 狀態碼
        response_text (str): 響應文本
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_text: Optional[str] = None
    ):
        super().__init__(
            message,
            status_code=status_code,
            response_text=response_text
        )
        self.status_code = status_code
        self.response_text = response_text


class APIRequestError(APIError):
    """
    API 請求錯誤

    Attributes:
        url (str): API URL
        method (str): HTTP 方法
    """

    def __init__(
        self,
        message: str = 'API 請求失敗',
        url: Optional[str] = None,
        method: Optional[str] = None,
        status_code: Optional[int] = None,
        response_text: Optional[str] = None
    ):
        if url:
            message += f' ({method or "GET"} {url})'

        super().__init__(message, status_code, response_text)
        self.url = url
        self.method = method


class APIResponseError(APIError):
    """API 響應錯誤 - 響應格式錯誤或內容無效"""

    def __init__(
        self,
        message: str = 'API 響應格式錯誤',
        status_code: Optional[int] = None,
        response_text: Optional[str] = None
    ):
        super().__init__(message, status_code, response_text)


class APITimeoutError(APIError):
    """
    API 超時錯誤

    Attributes:
        url (str): API URL
        timeout (int): 超時時間
    """

    def __init__(
        self,
        url: Optional[str] = None,
        timeout: Optional[int] = None
    ):
        message = 'API 請求超時'
        if url:
            message += f': {url}'

        super().__init__(message)
        self.url = url
        self.timeout = timeout


# =============================================================================
# 異常工具函數
# =============================================================================

def handle_exception(exception: Exception, log_func=None) -> dict:
    """
    統一處理異常

    Args:
        exception: 異常對象
        log_func: 日誌函數（可選）

    Returns:
        異常信息字典
    """
    if isinstance(exception, EEBotError):
        error_info = exception.to_dict()
    else:
        error_info = {
            'error_type': exception.__class__.__name__,
            'message': str(exception),
            'details': {}
        }

    if log_func:
        log_func(f"[{error_info['error_type']}] {error_info['message']}")

    return error_info


# =============================================================================
# 導出
# =============================================================================

__all__ = [
    # 基礎異常
    'EEBotError',

    # 配置異常
    'ConfigError',

    # 認證異常
    'LoginError',

    # WebDriver 異常
    'ElementNotFoundError',

    # Proxy 異常
    'ProxyStartError',

    # 掃描異常
    'ScanError',

    # API 異常
    'APIError',
    'APIRequestError',
    'APIResponseError',
    'APITimeoutError',

    # 工具函數
    'handle_exception',
]
