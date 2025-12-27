#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API 掃描服務

此模組提供 API 掃描功能，用於從 e-Learning API 獲取課程列表和相關信息。

主要功能:
- 從 Selenium WebDriver 提取 Session Cookie
- 調用 /api/my-courses 獲取課程列表
- 調用 /api/courses/{course_id}/activities 獲取課程活動
- 統一的錯誤處理和重試機制

使用方式:
    from src.services.api_scanner import APIScanner

    # 創建掃描器
    scanner = APIScanner(base_url='https://example.com')

    # 從 WebDriver 提取 Cookie 並掃描
    courses = scanner.scan_my_courses_from_driver(driver)

    # 或直接使用 Session Cookie
    courses = scanner.scan_my_courses(session_cookies)
"""

from typing import Dict, List, Optional
import requests
from urllib.parse import urlparse
from selenium.webdriver.remote.webdriver import WebDriver

from src.constants import (
    API_MY_COURSES,
    API_COURSE_ACTIVITIES,
    HTTP_TIMEOUT,
    is_http_success,
)
from src.exceptions import (
    APIRequestError,
    APIResponseError,
    APITimeoutError,
)


class APIScanner:
    """
    API 掃描器

    提供統一的 API 掃描接口，消除代碼重複。

    Attributes:
        base_url (str): API 基礎 URL
        headers (dict): 默認 HTTP 請求頭
        timeout (int): 請求超時時間
    """

    def __init__(self, base_url: str, timeout: int = HTTP_TIMEOUT):
        """
        初始化 API 掃描器

        Args:
            base_url: API 基礎 URL (例如: 'https://elearn.post.gov.tw')
            timeout: 請求超時時間（秒）
        """
        self.base_url = base_url
        self.timeout = timeout

        # 默認請求頭
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-TW,zh;q=0.9',
            'Referer': base_url,
        }

        # 禁用 SSL 警告
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    @staticmethod
    def extract_cookies_from_driver(driver: WebDriver) -> Dict[str, str]:
        """
        從 Selenium WebDriver 提取 Session Cookie

        Args:
            driver: Selenium WebDriver 實例

        Returns:
            Session Cookie 字典 {name: value, ...}

        Examples:
            >>> driver = webdriver.Chrome()
            >>> cookies = APIScanner.extract_cookies_from_driver(driver)
            >>> print(cookies)
            {'session_id': 'abc123', 'user_token': 'xyz789'}
        """
        selenium_cookies = driver.get_cookies()
        session_cookie = {cookie['name']: cookie['value']
                          for cookie in selenium_cookies}
        return session_cookie

    def scan_my_courses(
        self,
        session_cookies: Dict[str, str]
    ) -> List[dict]:
        """
        調用 /api/my-courses API 獲取課程列表

        Args:
            session_cookies: Session Cookie 字典

        Returns:
            課程列表，每個課程包含 id, name 等欄位

        Raises:
            APIRequestError: API 請求失敗
            APIResponseError: API 響應格式錯誤
            APITimeoutError: 請求超時

        Examples:
            >>> scanner = APIScanner('https://example.com')
            >>> cookies = {'session_id': 'abc123'}
            >>> courses = scanner.scan_my_courses(cookies)
            >>> print(len(courses))
            7
        """
        api_url = f"{self.base_url}{API_MY_COURSES}"

        try:
            response = requests.get(
                api_url,
                cookies=session_cookies,
                headers=self.headers,
                verify=False,
                timeout=self.timeout
            )

            # 檢查 HTTP 狀態碼
            if not is_http_success(response.status_code):
                raise APIRequestError(
                    message=f'API 請求失敗',
                    url=api_url,
                    method='GET',
                    status_code=response.status_code,
                    response_text=response.text[:200] if response.text else None
                )

            # 解析 JSON 響應
            try:
                data = response.json()
            except ValueError as e:
                raise APIResponseError(
                    message=f'API 響應不是有效的 JSON',
                    status_code=response.status_code,
                    response_text=response.text[:200]
                )

            # 提取課程列表
            courses = data.get('courses', [])

            if not isinstance(courses, list):
                raise APIResponseError(
                    message='API 響應格式錯誤: courses 不是列表',
                    status_code=response.status_code
                )

            return courses

        except requests.Timeout:
            raise APITimeoutError(
                url=api_url,
                timeout=self.timeout
            )

        except requests.RequestException as e:
            raise APIRequestError(
                message=f'API 請求異常: {str(e)}',
                url=api_url,
                method='GET'
            )

    def scan_my_courses_from_driver(
        self,
        driver: WebDriver
    ) -> List[dict]:
        """
        從 WebDriver 提取 Cookie 並掃描課程

        這是一個便捷方法，組合了 Cookie 提取和課程掃描。

        Args:
            driver: Selenium WebDriver 實例

        Returns:
            課程列表

        Raises:
            APIRequestError: API 請求失敗
            APIResponseError: API 響應格式錯誤
            APITimeoutError: 請求超時

        Examples:
            >>> scanner = APIScanner('https://example.com')
            >>> driver = webdriver.Chrome()
            >>> # ... 登入後 ...
            >>> courses = scanner.scan_my_courses_from_driver(driver)
        """
        session_cookies = self.extract_cookies_from_driver(driver)
        return self.scan_my_courses(session_cookies)

    def scan_course_activities(
        self,
        course_id: int,
        session_cookies: Dict[str, str]
    ) -> List[dict]:
        """
        獲取課程的所有學習活動（子課程）

        Args:
            course_id: 課程 ID
            session_cookies: Session Cookie 字典

        Returns:
            活動列表，每個活動包含 id, name, type 等欄位

        Raises:
            APIRequestError: API 請求失敗
            APIResponseError: API 響應格式錯誤
            APITimeoutError: 請求超時

        Examples:
            >>> scanner = APIScanner('https://example.com')
            >>> activities = scanner.scan_course_activities(465, cookies)
            >>> print(activities[0]['name'])
            '第一單元'
        """
        api_url = f"{self.base_url}{API_COURSE_ACTIVITIES.format(course_id=course_id)}"

        try:
            response = requests.get(
                api_url,
                cookies=session_cookies,
                headers=self.headers,
                verify=False,
                timeout=self.timeout
            )

            # 檢查 HTTP 狀態碼
            if not is_http_success(response.status_code):
                raise APIRequestError(
                    message=f'API 請求失敗',
                    url=api_url,
                    method='GET',
                    status_code=response.status_code,
                    response_text=response.text[:200] if response.text else None
                )

            # 解析 JSON 響應
            try:
                data = response.json()
            except ValueError:
                raise APIResponseError(
                    message=f'API 響應不是有效的 JSON',
                    status_code=response.status_code,
                    response_text=response.text[:200]
                )

            # 提取活動列表
            activities = data.get('activities', [])

            if not isinstance(activities, list):
                raise APIResponseError(
                    message='API 響應格式錯誤: activities 不是列表',
                    status_code=response.status_code
                )

            return activities

        except requests.Timeout:
            raise APITimeoutError(
                url=api_url,
                timeout=self.timeout
            )

        except requests.RequestException as e:
            raise APIRequestError(
                message=f'API 請求異常: {str(e)}',
                url=api_url,
                method='GET'
            )

    def get_course_by_id(
        self,
        course_id: int,
        courses: List[dict]
    ) -> Optional[dict]:
        """
        根據課程 ID 查找課程

        Args:
            course_id: 課程 ID
            courses: 課程列表

        Returns:
            找到的課程字典，未找到則返回 None

        Examples:
            >>> courses = [{'id': 465, 'name': '課程A'}, {'id': 452, 'name': '課程B'}]
            >>> course = scanner.get_course_by_id(465, courses)
            >>> print(course['name'])
            '課程A'
        """
        for course in courses:
            cid = course.get('id') or course.get('course_id')
            if cid == course_id:
                return course
        return None

    def get_course_by_name(
        self,
        course_name: str,
        courses: List[dict]
    ) -> Optional[dict]:
        """
        根據課程名稱查找課程

        Args:
            course_name: 課程名稱
            courses: 課程列表

        Returns:
            找到的課程字典，未找到則返回 None

        Examples:
            >>> courses = [{'id': 465, 'name': '課程A'}, {'id': 452, 'name': '課程B'}]
            >>> course = scanner.get_course_by_name('課程A', courses)
            >>> print(course['id'])
            465
        """
        for course in courses:
            cname = course.get('name', '')
            if cname == course_name:
                return course
        return None

    def match_course_id_by_name(
        self,
        program_name: str,
        api_courses: List[dict]
    ) -> Optional[int]:
        """
        根據課程名稱匹配 API 課程 ID

        使用三種匹配策略：
        1. 完全匹配: api_name == program_name
        2. 子集匹配: api_name in program_name
        3. 超集匹配: program_name in api_name

        Args:
            program_name: 課程計畫名稱（來自 Web）
            api_courses: API 課程列表

        Returns:
            匹配的課程 ID，未找到則返回 None

        Examples:
            >>> courses = [
            ...     {'id': 465, 'name': '性別平等工作法'},
            ...     {'id': 452, 'name': '高齡客戶投保'}
            ... ]
            >>> course_id = scanner.match_course_id_by_name('性別平等工作法', courses)
            >>> print(course_id)
            465
        """
        for api_course in api_courses:
            api_name = api_course.get('name', '')

            # 三種匹配策略
            if (api_name == program_name or          # 完全匹配
                api_name in program_name or           # API 名稱是 Web 名稱的子集
                program_name in api_name):            # Web 名稱是 API 名稱的子集
                return api_course.get('id') or api_course.get('course_id')

        return None

    def print_courses_summary(self, courses: List[dict]) -> None:
        """
        打印課程列表摘要

        Args:
            courses: 課程列表

        Examples:
            >>> scanner.print_courses_summary(courses)
            ✓ 獲取成功，共 7 門課程
            [1] 課程A (ID: 465)
            [2] 課程B (ID: 452)
            ...
        """
        print(f'✓ 獲取成功，共 {len(courses)} 門課程')

        for i, course in enumerate(courses, 1):
            course_id = course.get('id') or course.get('course_id')
            course_name = course.get('name', '未命名課程')
            print(f'[{i}] {course_name} (ID: {course_id})')


# =============================================================================
# 便捷函數
# =============================================================================

def create_scanner_from_config(config) -> APIScanner:
    """
    從配置創建 API 掃描器

    Args:
        config: 配置對象，需要包含 'target_http' 鍵

    Returns:
        配置好的 APIScanner 實例

    Examples:
        >>> config = ConfigLoader('config/eebot.cfg')
        >>> config.load()
        >>> scanner = create_scanner_from_config(config)
    """
    target_url = config.get('target_http')
    parsed = urlparse(target_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    return APIScanner(base_url)


def scan_courses_simple(driver: WebDriver, base_url: str) -> List[dict]:
    """
    簡化的課程掃描（單行調用）

    Args:
        driver: Selenium WebDriver 實例
        base_url: API 基礎 URL

    Returns:
        課程列表

    Examples:
        >>> from src.services.api_scanner import scan_courses_simple
        >>> courses = scan_courses_simple(driver, 'https://example.com')
    """
    scanner = APIScanner(base_url)
    return scanner.scan_my_courses_from_driver(driver)


# =============================================================================
# 版本信息
# =============================================================================

__version__ = '1.0.0'
__author__ = 'EEBot Development Team'
__all__ = [
    'APIScanner',
    'create_scanner_from_config',
    'scan_courses_simple',
]
