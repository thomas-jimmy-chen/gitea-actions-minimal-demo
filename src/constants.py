#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EEBot 常量定義

此模組包含所有在專案中使用的常量，包括：
- HTTP 相關常量
- 時長相關常量
- 延遲相關常量
- 重試相關常量
- 文件路徑常量
- API 端點常量
- 狀態碼常量

使用方式:
    from src.constants import (
        HTTP_SUCCESS_MIN,
        DEFAULT_PAGE_LOAD_DELAY,
        MAX_LOGIN_RETRIES
    )
"""

# =============================================================================
# HTTP 相關常量
# =============================================================================

# HTTP 狀態碼範圍
HTTP_SUCCESS_MIN = 200  # HTTP 成功狀態碼最小值 (包含)
HTTP_SUCCESS_MAX = 300  # HTTP 成功狀態碼最大值 (不包含)

# 常見 HTTP 狀態碼
HTTP_OK = 200  # 請求成功，有響應內容
HTTP_CREATED = 201  # 資源已創建
HTTP_NO_CONTENT = 204  # 請求成功，無響應內容
HTTP_BAD_REQUEST = 400  # 錯誤的請求
HTTP_UNAUTHORIZED = 401  # 未授權
HTTP_FORBIDDEN = 403  # 禁止訪問
HTTP_NOT_FOUND = 404  # 資源未找到
HTTP_INTERNAL_ERROR = 500  # 服務器內部錯誤

# HTTP 請求相關
HTTP_TIMEOUT = 30  # HTTP 請求超時時間（秒）
HTTP_MAX_REDIRECTS = 5  # 最大重定向次數


# =============================================================================
# 時長相關常量
# =============================================================================

# 時長計算
BUFFER_SECONDS = 10  # 發送時長的緩衝時間（秒），確保超過最低要求
MINIMUM_DURATION_SECONDS = 60  # 最小學習時長（秒）
SECONDS_PER_MINUTE = 60  # 每分鐘的秒數

# 時長顯示
HOURS_PER_DAY = 24  # 每天的小時數（用於時長換算）
MINUTES_PER_HOUR = 60  # 每小時的分鐘數


# =============================================================================
# 延遲相關常量（Selenium 操作）
# =============================================================================

# 頁面加載延遲
DEFAULT_PAGE_LOAD_DELAY = 7  # 默認頁面加載等待時間（秒）
SHORT_PAGE_LOAD_DELAY = 2  # 短頁面加載等待時間（秒）
LONG_PAGE_LOAD_DELAY = 10  # 長頁面加載等待時間（秒）

# 操作延遲
LESSON_SELECT_DELAY = 2.0  # 選擇課程的延遲時間（秒）
CLICK_DELAY = 1.0  # 點擊操作的延遲時間（秒）
INPUT_DELAY = 0.5  # 輸入操作的延遲時間（秒）

# API 請求延遲
API_REQUEST_DELAY = 1  # API 請求間隔時間（秒），避免請求過快
API_BATCH_DELAY = 0.5  # 批量 API 請求間隔時間（秒）

# 重試延遲
RETRY_DELAY = 5  # 一般重試等待時間（秒）
PORT_RELEASE_DELAY = 5  # 等待端口釋放的時間（秒）

# Payload 捕獲延遲
PAYLOAD_CAPTURE_WAIT = 3  # 等待 Payload 捕獲的時間（秒）
PAYLOAD_CAPTURE_LONG_WAIT = 5  # 長時間等待 Payload 捕獲（秒）


# =============================================================================
# 重試相關常量
# =============================================================================

# 登入重試
MAX_LOGIN_RETRIES = 3  # 最大登入重試次數
LOGIN_RETRY_DELAY = 5  # 登入重試等待時間（秒）

# 操作重試
MAX_OPERATION_RETRIES = 3  # 最大操作重試次數
OPERATION_RETRY_DELAY = 2  # 操作重試等待時間（秒）

# API 重試
MAX_API_RETRIES = 3  # 最大 API 請求重試次數
API_RETRY_DELAY = 3  # API 重試等待時間（秒）


# =============================================================================
# 文件路徑常量
# =============================================================================

# 配置文件
DEFAULT_CONFIG_PATH = 'config/eebot.cfg'  # 默認配置文件路徑

# Cookie 文件
DEFAULT_COOKIES_PATH = 'resource/cookies/cookies.json'  # 默認 Cookie 文件路徑

# 題庫文件
QUESTION_BANK_PATH = 'resource/question_bank.json'  # 題庫文件路徑

# Stealth JS
STEALTH_JS_PATH = 'resource/plugins/stealth.min.js'  # Stealth JS 文件路徑

# 日誌文件
DEFAULT_LOG_PATH = 'logs/eebot.log'  # 默認日誌文件路徑

# 結果文件
BATCH_RESULT_DIR = '.'  # 批量結果文件目錄
BATCH_RESULT_PREFIX = 'batch_result_'  # 批量結果文件前綴
QUICK_COMPLETE_PREFIX = 'quick_complete_result_'  # 快速完成結果前綴
HYBRID_SCAN_PREFIX = 'hybrid_scan_result_'  # 混合掃描結果前綴


# =============================================================================
# API 端點常量
# =============================================================================

# 基礎路徑
API_BASE_PATH = '/api'  # API 基礎路徑

# 課程相關 API
API_MY_COURSES = '/api/my-courses'  # 我的課程列表
API_COURSE_DETAIL = '/api/courses/{course_id}'  # 課程詳情
API_COURSE_ACTIVITIES = '/api/courses/{course_id}/activities'  # 課程活動列表

# 學習相關 API
API_USER_VISITS = '/api/user-visits'  # 用戶訪問記錄（時長發送）
API_LEARNING_STATS = '/api/learning-stats'  # 學習統計

# 考試相關 API
API_EXAMS = '/api/exams'  # 考試列表
API_EXAM_DETAIL = '/api/exams/{exam_id}'  # 考試詳情
API_EXAM_DISTRIBUTE = '/api/exams/{exam_id}/distribute'  # 考試分發
API_EXAM_SUBMISSION = '/api/exams/{exam_id}/submissions'  # 考試提交

# 公告相關 API
API_ANNOUNCEMENTS = '/api/announcements'  # 公告列表


# =============================================================================
# Proxy 相關常量
# =============================================================================

# MitmProxy 設置
DEFAULT_PROXY_HOST = 'localhost'  # 默認 Proxy 主機
DEFAULT_PROXY_PORT = 8899  # 默認 Proxy 端口
PROXY_PROTOCOL = 'http'  # Proxy 協議

# Proxy URL 格式
PROXY_URL_FORMAT = '{protocol}://{host}:{port}'  # Proxy URL 格式


# =============================================================================
# WebDriver 相關常量
# =============================================================================

# 瀏覽器選項
BROWSER_HEADLESS = False  # 是否使用無頭模式
BROWSER_WINDOW_WIDTH = 1920  # 瀏覽器視窗寬度
BROWSER_WINDOW_HEIGHT = 1080  # 瀏覽器視窗高度

# 等待超時
DEFAULT_WAIT_TIMEOUT = 10  # 默認等待超時時間（秒）
LONG_WAIT_TIMEOUT = 30  # 長等待超時時間（秒）
SHORT_WAIT_TIMEOUT = 5  # 短等待超時時間（秒）


# =============================================================================
# 狀態常量
# =============================================================================

# 課程狀態
STATUS_NOT_STARTED = 'not_started'  # 未開始
STATUS_IN_PROGRESS = 'in_progress'  # 進行中
STATUS_COMPLETED = 'completed'  # 已完成
STATUS_PASSED = 'passed'  # 已通過
STATUS_FAILED = 'failed'  # 失敗

# 執行狀態
EXEC_STATUS_SUCCESS = 'success'  # 執行成功
EXEC_STATUS_FAILED = 'failed'  # 執行失敗
EXEC_STATUS_PENDING = 'pending'  # 等待中
EXEC_STATUS_SKIPPED = 'skipped'  # 已跳過


# =============================================================================
# 驗證碼相關常量
# =============================================================================

# 驗證碼設置
CAPTCHA_MAX_RETRIES = 3  # 驗證碼最大重試次數
CAPTCHA_RETRY_DELAY = 2  # 驗證碼重試延遲（秒）
CAPTCHA_IMAGE_PATH = 'captcha.png'  # 驗證碼圖片路徑


# =============================================================================
# 日誌相關常量
# =============================================================================

# 日誌級別
LOG_LEVEL_DEBUG = 'DEBUG'  # 調試級別
LOG_LEVEL_INFO = 'INFO'  # 信息級別
LOG_LEVEL_WARNING = 'WARNING'  # 警告級別
LOG_LEVEL_ERROR = 'ERROR'  # 錯誤級別
LOG_LEVEL_CRITICAL = 'CRITICAL'  # 嚴重級別

# 日誌格式
LOG_FORMAT = '[%(asctime)s] %(levelname)s [%(name)s] %(message)s'  # 日誌格式
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'  # 日期格式


# =============================================================================
# 數據格式常量
# =============================================================================

# 時間格式
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'  # 日期時間格式
DATE_FORMAT = '%Y-%m-%d'  # 日期格式
TIME_FORMAT = '%H:%M:%S'  # 時間格式

# 文件名時間格式
FILENAME_DATETIME_FORMAT = '%Y%m%d_%H%M%S'  # 文件名日期時間格式


# =============================================================================
# 答題相關常量
# =============================================================================

# 題型
QUESTION_TYPE_SINGLE = 'single'  # 單選題
QUESTION_TYPE_MULTIPLE = 'multiple'  # 多選題
QUESTION_TYPE_TRUE_FALSE = 'true_false'  # 是非題

# 答案匹配閾值
ANSWER_MATCH_THRESHOLD = 0.8  # 答案相似度匹配閾值（0-1）


# =============================================================================
# 系統相關常量
# =============================================================================

# 編碼
DEFAULT_ENCODING = 'utf-8'  # 默認編碼

# 換行符
NEWLINE = '\n'  # 換行符

# 分隔符
SEPARATOR = '-' * 70  # 分隔符（70個連字符）


# =============================================================================
# 輔助函數
# =============================================================================

def is_http_success(status_code: int) -> bool:
    """
    檢查 HTTP 狀態碼是否表示成功

    Args:
        status_code: HTTP 狀態碼

    Returns:
        True 如果狀態碼在 2xx 範圍內，否則 False

    Examples:
        >>> is_http_success(200)
        True
        >>> is_http_success(204)
        True
        >>> is_http_success(404)
        False
    """
    return HTTP_SUCCESS_MIN <= status_code < HTTP_SUCCESS_MAX


def get_proxy_url(host: str = DEFAULT_PROXY_HOST,
                  port: int = DEFAULT_PROXY_PORT,
                  protocol: str = PROXY_PROTOCOL) -> str:
    """
    獲取 Proxy URL

    Args:
        host: Proxy 主機
        port: Proxy 端口
        protocol: Proxy 協議

    Returns:
        完整的 Proxy URL

    Examples:
        >>> get_proxy_url()
        'http://localhost:8899'
        >>> get_proxy_url('127.0.0.1', 9090)
        'http://127.0.0.1:9090'
    """
    return PROXY_URL_FORMAT.format(
        protocol=protocol,
        host=host,
        port=port
    )


def seconds_to_minutes(seconds: int) -> float:
    """
    將秒數轉換為分鐘數

    Args:
        seconds: 秒數

    Returns:
        分鐘數（保留兩位小數）

    Examples:
        >>> seconds_to_minutes(120)
        2.0
        >>> seconds_to_minutes(90)
        1.5
    """
    return round(seconds / SECONDS_PER_MINUTE, 2)


def minutes_to_seconds(minutes: float) -> int:
    """
    將分鐘數轉換為秒數

    Args:
        minutes: 分鐘數

    Returns:
        秒數（向上取整）

    Examples:
        >>> minutes_to_seconds(2.5)
        150
        >>> minutes_to_seconds(1.0)
        60
    """
    import math
    return math.ceil(minutes * SECONDS_PER_MINUTE)


def get_result_filename(prefix: str = BATCH_RESULT_PREFIX) -> str:
    """
    生成結果文件名（含時間戳）

    Args:
        prefix: 文件名前綴

    Returns:
        完整的結果文件名

    Examples:
        >>> get_result_filename('test_')
        'test_20251218_142530.json'
    """
    from datetime import datetime
    timestamp = datetime.now().strftime(FILENAME_DATETIME_FORMAT)
    return f'{prefix}{timestamp}.json'


# =============================================================================
# 版本信息
# =============================================================================

__version__ = '1.0.0'
__author__ = 'EEBot Development Team'
__all__ = [
    # HTTP 常量
    'HTTP_SUCCESS_MIN', 'HTTP_SUCCESS_MAX',
    'HTTP_OK', 'HTTP_CREATED', 'HTTP_NO_CONTENT',
    'HTTP_BAD_REQUEST', 'HTTP_UNAUTHORIZED', 'HTTP_FORBIDDEN',
    'HTTP_NOT_FOUND', 'HTTP_INTERNAL_ERROR',
    'HTTP_TIMEOUT', 'HTTP_MAX_REDIRECTS',

    # 時長常量
    'BUFFER_SECONDS', 'MINIMUM_DURATION_SECONDS', 'SECONDS_PER_MINUTE',
    'HOURS_PER_DAY', 'MINUTES_PER_HOUR',

    # 延遲常量
    'DEFAULT_PAGE_LOAD_DELAY', 'SHORT_PAGE_LOAD_DELAY', 'LONG_PAGE_LOAD_DELAY',
    'LESSON_SELECT_DELAY', 'CLICK_DELAY', 'INPUT_DELAY',
    'API_REQUEST_DELAY', 'API_BATCH_DELAY',
    'RETRY_DELAY', 'PORT_RELEASE_DELAY',
    'PAYLOAD_CAPTURE_WAIT', 'PAYLOAD_CAPTURE_LONG_WAIT',

    # 重試常量
    'MAX_LOGIN_RETRIES', 'LOGIN_RETRY_DELAY',
    'MAX_OPERATION_RETRIES', 'OPERATION_RETRY_DELAY',
    'MAX_API_RETRIES', 'API_RETRY_DELAY',

    # 文件路徑
    'DEFAULT_CONFIG_PATH', 'DEFAULT_COOKIES_PATH', 'QUESTION_BANK_PATH',
    'STEALTH_JS_PATH', 'DEFAULT_LOG_PATH',
    'BATCH_RESULT_DIR', 'BATCH_RESULT_PREFIX',
    'QUICK_COMPLETE_PREFIX', 'HYBRID_SCAN_PREFIX',

    # API 端點
    'API_BASE_PATH', 'API_MY_COURSES', 'API_COURSE_DETAIL',
    'API_COURSE_ACTIVITIES', 'API_USER_VISITS', 'API_LEARNING_STATS',
    'API_EXAMS', 'API_EXAM_DETAIL', 'API_EXAM_DISTRIBUTE',
    'API_EXAM_SUBMISSION', 'API_ANNOUNCEMENTS',

    # Proxy 常量
    'DEFAULT_PROXY_HOST', 'DEFAULT_PROXY_PORT', 'PROXY_PROTOCOL',
    'PROXY_URL_FORMAT',

    # WebDriver 常量
    'BROWSER_HEADLESS', 'BROWSER_WINDOW_WIDTH', 'BROWSER_WINDOW_HEIGHT',
    'DEFAULT_WAIT_TIMEOUT', 'LONG_WAIT_TIMEOUT', 'SHORT_WAIT_TIMEOUT',

    # 狀態常量
    'STATUS_NOT_STARTED', 'STATUS_IN_PROGRESS', 'STATUS_COMPLETED',
    'STATUS_PASSED', 'STATUS_FAILED',
    'EXEC_STATUS_SUCCESS', 'EXEC_STATUS_FAILED',
    'EXEC_STATUS_PENDING', 'EXEC_STATUS_SKIPPED',

    # 驗證碼常量
    'CAPTCHA_MAX_RETRIES', 'CAPTCHA_RETRY_DELAY', 'CAPTCHA_IMAGE_PATH',

    # 日誌常量
    'LOG_LEVEL_DEBUG', 'LOG_LEVEL_INFO', 'LOG_LEVEL_WARNING',
    'LOG_LEVEL_ERROR', 'LOG_LEVEL_CRITICAL',
    'LOG_FORMAT', 'LOG_DATE_FORMAT',

    # 數據格式
    'DATETIME_FORMAT', 'DATE_FORMAT', 'TIME_FORMAT',
    'FILENAME_DATETIME_FORMAT',

    # 答題常量
    'QUESTION_TYPE_SINGLE', 'QUESTION_TYPE_MULTIPLE', 'QUESTION_TYPE_TRUE_FALSE',
    'ANSWER_MATCH_THRESHOLD',

    # 系統常量
    'DEFAULT_ENCODING', 'NEWLINE', 'SEPARATOR',

    # 輔助函數
    'is_http_success', 'get_proxy_url',
    'seconds_to_minutes', 'minutes_to_seconds',
    'get_result_filename',
]
