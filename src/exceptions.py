#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EEBot 自定義異常類

此模組定義了 EEBot 專案中使用的所有自定義異常。
所有自定義異常都繼承自 EEBotError 基類。

異常層次結構:
    EEBotError (基類)
    └── APIError (API 相關錯誤)
        ├── APIRequestError
        ├── APIResponseError
        └── APITimeoutError

使用方式:
    from src.exceptions import EEBotError, APIRequestError

    try:
        # 業務邏輯
        ...
    except APIRequestError as e:
        handle_error(e, driver=driver, context="API 操作", is_known=True)
    except EEBotError as e:
        handle_error(e, driver=driver, context="業務操作", is_known=True)
    except Exception as e:
        handle_error(e, driver=driver, context="未知操作", is_known=False)

錯誤處理:
    所有錯誤（已知和未預期）都應使用 src.utils.error_handler.handle_error() 處理，
    該函數會自動生成錯誤 Log 和截圖。

Note:
    如需新增異常類型，請繼承 EEBotError 或 APIError，
    並在 __all__ 中導出。
"""

from typing import Optional


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
# 導出
# =============================================================================

__all__ = [
    # 基礎異常
    'EEBotError',

    # API 異常
    'APIError',
    'APIRequestError',
    'APIResponseError',
    'APITimeoutError',
]
