#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EEBot 自定義異常類

此模組定義了 EEBot 專案中使用的所有自定義異常。
所有自定義異常都繼承自 EEBotError 基類。

異常層次結構:
    EEBotError (基類)
    ├── ConfigError (配置相關錯誤)
    │   ├── ConfigFileNotFoundError
    │   ├── ConfigValidationError
    │   └── ConfigKeyMissingError
    │
    ├── AuthenticationError (認證相關錯誤)
    │   ├── LoginError
    │   ├── CaptchaError
    │   └── SessionExpiredError
    │
    ├── WebDriverError (WebDriver 相關錯誤)
    │   ├── DriverInitializationError
    │   ├── ElementNotFoundError
    │   └── PageLoadTimeoutError
    │
    ├── ProxyError (Proxy 相關錯誤)
    │   ├── ProxyStartError
    │   ├── ProxyStopError
    │   └── ProxyConnectionError
    │
    ├── ScanError (掃描相關錯誤)
    │   ├── CourseNotFoundError
    │   ├── PayloadNotFoundError
    │   └── ScanTimeoutError
    │
    ├── APIError (API 相關錯誤)
    │   ├── APIRequestError
    │   ├── APIResponseError
    │   └── APITimeoutError
    │
    ├── DataError (數據相關錯誤)
    │   ├── InvalidDataError
    │   ├── DataParseError
    │   └── DataValidationError
    │
    └── ExamError (考試相關錯誤)
        ├── QuestionNotFoundError
        ├── AnswerMatchError
        └── SubmissionError

使用方式:
    from src.exceptions import LoginError, APIError

    try:
        # 執行登入
        ...
    except LoginError as e:
        print(f'登入失敗: {e}')
        # 處理登入錯誤
    except APIError as e:
        print(f'API 錯誤 (狀態碼: {e.status_code}): {e}')
        # 處理 API 錯誤
"""


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
        """
        初始化異常

        Args:
            message: 錯誤訊息
            **details: 額外的錯誤詳情（鍵值對）
        """
        super().__init__(message)
        self.message = message
        self.details = details

    def __str__(self) -> str:
        """返回錯誤訊息的字符串表示"""
        if self.details:
            details_str = ', '.join(f'{k}={v}' for k, v in self.details.items())
            return f'{self.message} ({details_str})'
        return self.message

    def to_dict(self) -> dict:
        """
        將異常轉換為字典

        Returns:
            包含錯誤信息的字典
        """
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'details': self.details
        }


# =============================================================================
# 配置相關異常
# =============================================================================

class ConfigError(EEBotError):
    """配置相關錯誤的基類"""
    pass


class ConfigFileNotFoundError(ConfigError):
    """
    配置文件未找到錯誤

    當無法找到指定的配置文件時拋出。

    Attributes:
        config_path (str): 配置文件路徑
    """

    def __init__(self, config_path: str):
        """
        Args:
            config_path: 配置文件路徑
        """
        super().__init__(
            f'配置文件不存在: {config_path}',
            config_path=config_path
        )
        self.config_path = config_path


class ConfigValidationError(ConfigError):
    """
    配置驗證錯誤

    當配置文件內容不符合要求時拋出。

    Attributes:
        validation_errors (list): 驗證錯誤列表
    """

    def __init__(self, validation_errors: list):
        """
        Args:
            validation_errors: 驗證錯誤列表
        """
        errors_str = ', '.join(validation_errors)
        super().__init__(
            f'配置驗證失敗: {errors_str}',
            validation_errors=validation_errors
        )
        self.validation_errors = validation_errors


class ConfigKeyMissingError(ConfigError):
    """
    配置鍵缺失錯誤

    當必需的配置鍵不存在時拋出。

    Attributes:
        missing_keys (list): 缺失的配置鍵列表
    """

    def __init__(self, missing_keys: list):
        """
        Args:
            missing_keys: 缺失的配置鍵列表
        """
        keys_str = ', '.join(missing_keys)
        super().__init__(
            f'缺少必需的配置項: {keys_str}',
            missing_keys=missing_keys
        )
        self.missing_keys = missing_keys


# =============================================================================
# 認證相關異常
# =============================================================================

class AuthenticationError(EEBotError):
    """認證相關錯誤的基類"""
    pass


class LoginError(AuthenticationError):
    """
    登入失敗錯誤

    當用戶登入失敗時拋出。

    Attributes:
        username (str): 用戶名
        reason (str): 失敗原因
        retry_count (int): 已重試次數
    """

    def __init__(self, username: str = None, reason: str = None, retry_count: int = 0):
        """
        Args:
            username: 用戶名
            reason: 失敗原因
            retry_count: 已重試次數
        """
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


class CaptchaError(AuthenticationError):
    """
    驗證碼錯誤

    當驗證碼識別或輸入失敗時拋出。

    Attributes:
        captcha_image_path (str): 驗證碼圖片路徑
        retry_count (int): 已重試次數
    """

    def __init__(self, message: str = '驗證碼錯誤',
                 captcha_image_path: str = None,
                 retry_count: int = 0):
        """
        Args:
            message: 錯誤訊息
            captcha_image_path: 驗證碼圖片路徑
            retry_count: 已重試次數
        """
        super().__init__(
            message,
            captcha_image_path=captcha_image_path,
            retry_count=retry_count
        )
        self.captcha_image_path = captcha_image_path
        self.retry_count = retry_count


class SessionExpiredError(AuthenticationError):
    """
    Session 過期錯誤

    當用戶 Session 過期需要重新登入時拋出。
    """

    def __init__(self):
        super().__init__('Session 已過期，請重新登入')


# =============================================================================
# WebDriver 相關異常
# =============================================================================

class WebDriverError(EEBotError):
    """WebDriver 相關錯誤的基類"""
    pass


class DriverInitializationError(WebDriverError):
    """
    WebDriver 初始化錯誤

    當 WebDriver 初始化失敗時拋出。

    Attributes:
        driver_type (str): 驅動類型（如 'chrome'）
        reason (str): 失敗原因
    """

    def __init__(self, driver_type: str = 'chrome', reason: str = None):
        """
        Args:
            driver_type: 驅動類型
            reason: 失敗原因
        """
        message = f'{driver_type} WebDriver 初始化失敗'
        if reason:
            message += f': {reason}'

        super().__init__(
            message,
            driver_type=driver_type,
            reason=reason
        )
        self.driver_type = driver_type
        self.reason = reason


class ElementNotFoundError(WebDriverError):
    """
    元素未找到錯誤

    當無法找到指定的頁面元素時拋出。

    Attributes:
        locator (tuple): 元素定位器 (By.*, 'selector')
        timeout (int): 等待超時時間
    """

    def __init__(self, locator: tuple, timeout: int = None):
        """
        Args:
            locator: 元素定位器
            timeout: 等待超時時間
        """
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


class PageLoadTimeoutError(WebDriverError):
    """
    頁面加載超時錯誤

    當頁面加載超時時拋出。

    Attributes:
        url (str): 頁面 URL
        timeout (int): 超時時間
    """

    def __init__(self, url: str = None, timeout: int = None):
        """
        Args:
            url: 頁面 URL
            timeout: 超時時間
        """
        message = '頁面加載超時'
        if url:
            message += f': {url}'

        super().__init__(
            message,
            url=url,
            timeout=timeout
        )
        self.url = url
        self.timeout = timeout


# =============================================================================
# Proxy 相關異常
# =============================================================================

class ProxyError(EEBotError):
    """Proxy 相關錯誤的基類"""
    pass


class ProxyStartError(ProxyError):
    """
    Proxy 啟動失敗錯誤

    當 MitmProxy 啟動失敗時拋出。

    Attributes:
        port (int): Proxy 端口
        reason (str): 失敗原因
    """

    def __init__(self, port: int = None, reason: str = None):
        """
        Args:
            port: Proxy 端口
            reason: 失敗原因
        """
        message = 'MitmProxy 啟動失敗'
        if reason:
            message += f': {reason}'

        super().__init__(
            message,
            port=port,
            reason=reason
        )
        self.port = port
        self.reason = reason


class ProxyStopError(ProxyError):
    """
    Proxy 停止失敗錯誤

    當 MitmProxy 停止失敗時拋出。
    """

    def __init__(self, reason: str = None):
        """
        Args:
            reason: 失敗原因
        """
        message = 'MitmProxy 停止失敗'
        if reason:
            message += f': {reason}'

        super().__init__(message, reason=reason)
        self.reason = reason


class ProxyConnectionError(ProxyError):
    """
    Proxy 連接錯誤

    當無法連接到 Proxy 時拋出。

    Attributes:
        proxy_url (str): Proxy URL
    """

    def __init__(self, proxy_url: str):
        """
        Args:
            proxy_url: Proxy URL
        """
        super().__init__(
            f'無法連接到 Proxy: {proxy_url}',
            proxy_url=proxy_url
        )
        self.proxy_url = proxy_url


# =============================================================================
# 掃描相關異常
# =============================================================================

class ScanError(EEBotError):
    """掃描相關錯誤的基類"""
    pass


class CourseNotFoundError(ScanError):
    """
    課程未找到錯誤

    當無法找到指定的課程時拋出。

    Attributes:
        course_name (str): 課程名稱
        course_id (int): 課程 ID
    """

    def __init__(self, course_name: str = None, course_id: int = None):
        """
        Args:
            course_name: 課程名稱
            course_id: 課程 ID
        """
        if course_name:
            message = f'找不到課程: {course_name}'
        elif course_id:
            message = f'找不到課程 (ID: {course_id})'
        else:
            message = '找不到課程'

        super().__init__(
            message,
            course_name=course_name,
            course_id=course_id
        )
        self.course_name = course_name
        self.course_id = course_id


class PayloadNotFoundError(ScanError):
    """
    Payload 未捕獲錯誤

    當無法捕獲到預期的 Payload 時拋出。

    Attributes:
        course_id (int): 課程 ID
        timeout (int): 等待超時時間
    """

    def __init__(self, course_id: int = None, timeout: int = None):
        """
        Args:
            course_id: 課程 ID
            timeout: 等待超時時間
        """
        message = '未捕獲到 Payload'
        if course_id:
            message += f' (課程 ID: {course_id})'

        super().__init__(
            message,
            course_id=course_id,
            timeout=timeout
        )
        self.course_id = course_id
        self.timeout = timeout


class ScanTimeoutError(ScanError):
    """
    掃描超時錯誤

    當掃描操作超時時拋出。

    Attributes:
        operation (str): 操作名稱
        timeout (int): 超時時間
    """

    def __init__(self, operation: str = '掃描', timeout: int = None):
        """
        Args:
            operation: 操作名稱
            timeout: 超時時間
        """
        message = f'{operation}操作超時'
        if timeout:
            message += f' ({timeout}秒)'

        super().__init__(
            message,
            operation=operation,
            timeout=timeout
        )
        self.operation = operation
        self.timeout = timeout


# =============================================================================
# API 相關異常
# =============================================================================

class APIError(EEBotError):
    """
    API 相關錯誤的基類

    Attributes:
        status_code (int): HTTP 狀態碼
        response_text (str): 響應文本
    """

    def __init__(self, message: str, status_code: int = None, response_text: str = None):
        """
        Args:
            message: 錯誤訊息
            status_code: HTTP 狀態碼
            response_text: 響應文本
        """
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

    當 API 請求失敗時拋出。

    Attributes:
        url (str): API URL
        method (str): HTTP 方法
    """

    def __init__(self, message: str = 'API 請求失敗',
                 url: str = None,
                 method: str = None,
                 status_code: int = None,
                 response_text: str = None):
        """
        Args:
            message: 錯誤訊息
            url: API URL
            method: HTTP 方法
            status_code: HTTP 狀態碼
            response_text: 響應文本
        """
        if url:
            message += f' ({method or "GET"} {url})'

        super().__init__(message, status_code, response_text)
        self.url = url
        self.method = method


class APIResponseError(APIError):
    """
    API 響應錯誤

    當 API 響應格式錯誤或內容無效時拋出。
    """

    def __init__(self, message: str = 'API 響應格式錯誤',
                 status_code: int = None,
                 response_text: str = None):
        super().__init__(message, status_code, response_text)


class APITimeoutError(APIError):
    """
    API 超時錯誤

    當 API 請求超時時拋出。

    Attributes:
        url (str): API URL
        timeout (int): 超時時間
    """

    def __init__(self, url: str = None, timeout: int = None):
        """
        Args:
            url: API URL
            timeout: 超時時間
        """
        message = 'API 請求超時'
        if url:
            message += f': {url}'

        super().__init__(message)
        self.url = url
        self.timeout = timeout


# =============================================================================
# 數據相關異常
# =============================================================================

class DataError(EEBotError):
    """數據相關錯誤的基類"""
    pass


class InvalidDataError(DataError):
    """
    無效數據錯誤

    當數據格式或內容無效時拋出。

    Attributes:
        data_type (str): 數據類型
        expected (str): 預期格式
        actual (str): 實際格式
    """

    def __init__(self, message: str = '無效的數據',
                 data_type: str = None,
                 expected: str = None,
                 actual: str = None):
        """
        Args:
            message: 錯誤訊息
            data_type: 數據類型
            expected: 預期格式
            actual: 實際格式
        """
        super().__init__(
            message,
            data_type=data_type,
            expected=expected,
            actual=actual
        )
        self.data_type = data_type
        self.expected = expected
        self.actual = actual


class DataParseError(DataError):
    """
    數據解析錯誤

    當無法解析數據時拋出（如 JSON 解析失敗）。

    Attributes:
        data_format (str): 數據格式（如 'json', 'xml'）
        parse_error (str): 解析錯誤訊息
    """

    def __init__(self, data_format: str = None, parse_error: str = None):
        """
        Args:
            data_format: 數據格式
            parse_error: 解析錯誤訊息
        """
        message = f'數據解析失敗'
        if data_format:
            message += f' (格式: {data_format})'

        super().__init__(
            message,
            data_format=data_format,
            parse_error=parse_error
        )
        self.data_format = data_format
        self.parse_error = parse_error


class DataValidationError(DataError):
    """
    數據驗證錯誤

    當數據不符合驗證規則時拋出。

    Attributes:
        field (str): 字段名稱
        value (any): 字段值
        validation_rule (str): 驗證規則
    """

    def __init__(self, field: str = None, value=None, validation_rule: str = None):
        """
        Args:
            field: 字段名稱
            value: 字段值
            validation_rule: 驗證規則
        """
        message = '數據驗證失敗'
        if field:
            message += f': 字段 "{field}"'
        if validation_rule:
            message += f' ({validation_rule})'

        super().__init__(
            message,
            field=field,
            value=str(value) if value is not None else None,
            validation_rule=validation_rule
        )
        self.field = field
        self.value = value
        self.validation_rule = validation_rule


# =============================================================================
# 考試相關異常
# =============================================================================

class ExamError(EEBotError):
    """考試相關錯誤的基類"""
    pass


class QuestionNotFoundError(ExamError):
    """
    題目未找到錯誤

    當在題庫中找不到匹配的題目時拋出。

    Attributes:
        question_text (str): 題目文字
    """

    def __init__(self, question_text: str = None):
        """
        Args:
            question_text: 題目文字
        """
        message = '題庫中找不到匹配的題目'
        if question_text:
            preview = question_text[:50] + '...' if len(question_text) > 50 else question_text
            message += f': "{preview}"'

        super().__init__(
            message,
            question_text=question_text
        )
        self.question_text = question_text


class AnswerMatchError(ExamError):
    """
    答案匹配錯誤

    當無法匹配正確答案時拋出。

    Attributes:
        question_text (str): 題目文字
        options (list): 選項列表
        threshold (float): 匹配閾值
    """

    def __init__(self, question_text: str = None, options: list = None, threshold: float = None):
        """
        Args:
            question_text: 題目文字
            options: 選項列表
            threshold: 匹配閾值
        """
        message = '無法匹配正確答案'

        super().__init__(
            message,
            question_text=question_text,
            options=options,
            threshold=threshold
        )
        self.question_text = question_text
        self.options = options
        self.threshold = threshold


class SubmissionError(ExamError):
    """
    提交錯誤

    當考試提交失敗時拋出。

    Attributes:
        exam_id (int): 考試 ID
        reason (str): 失敗原因
    """

    def __init__(self, exam_id: int = None, reason: str = None):
        """
        Args:
            exam_id: 考試 ID
            reason: 失敗原因
        """
        message = '考試提交失敗'
        if reason:
            message += f': {reason}'

        super().__init__(
            message,
            exam_id=exam_id,
            reason=reason
        )
        self.exam_id = exam_id
        self.reason = reason


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
# 版本信息
# =============================================================================

__version__ = '1.0.0'
__author__ = 'EEBot Development Team'
__all__ = [
    # 基礎異常
    'EEBotError',

    # 配置異常
    'ConfigError', 'ConfigFileNotFoundError', 'ConfigValidationError',
    'ConfigKeyMissingError',

    # 認證異常
    'AuthenticationError', 'LoginError', 'CaptchaError', 'SessionExpiredError',

    # WebDriver 異常
    'WebDriverError', 'DriverInitializationError', 'ElementNotFoundError',
    'PageLoadTimeoutError',

    # Proxy 異常
    'ProxyError', 'ProxyStartError', 'ProxyStopError', 'ProxyConnectionError',

    # 掃描異常
    'ScanError', 'CourseNotFoundError', 'PayloadNotFoundError', 'ScanTimeoutError',

    # API 異常
    'APIError', 'APIRequestError', 'APIResponseError', 'APITimeoutError',

    # 數據異常
    'DataError', 'InvalidDataError', 'DataParseError', 'DataValidationError',

    # 考試異常
    'ExamError', 'QuestionNotFoundError', 'AnswerMatchError', 'SubmissionError',

    # 工具函數
    'handle_exception',
]
