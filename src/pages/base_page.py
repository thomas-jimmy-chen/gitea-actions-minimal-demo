#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
BasePage - 頁面物件基類
提供所有頁面物件的通用方法與功能
"""

import time
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    TimeoutException,
    NoSuchElementException
)


class PageLoadError(Exception):
    """頁面載入錯誤的自訂異常"""

    def __init__(self, message: str, error_type: str = None, status_code: int = None):
        super().__init__(message)
        self.error_type = error_type  # 'server_error', 'blank_page', 'client_error'
        self.status_code = status_code


class BasePage:
    """所有頁面物件的基類"""

    # 預設等待時間
    DEFAULT_TIMEOUT = 40
    DEFAULT_POLL_FREQUENCY = 0.5

    # 子類別覆寫此屬性，定義該頁面的關鍵元素選擇器
    # 可以是單一選擇器字串，或多個選擇器的列表（任一存在即可）
    PAGE_LOAD_INDICATOR = None

    # 空白頁檢測的最小內容長度閾值
    MIN_CONTENT_LENGTH = 100

    # 重刷設定
    MAX_RELOAD_RETRIES = 3
    RELOAD_DELAYS = [2, 4, 6]  # Exponential backoff (秒)

    def __init__(self, driver: webdriver.Chrome, timeout: int = None):
        """
        初始化頁面物件

        Args:
            driver: Selenium WebDriver 實例
            timeout: 等待超時時間（秒），預設為 40 秒
        """
        self.driver = driver
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.wait = WebDriverWait(
            driver,
            self.timeout,
            poll_frequency=self.DEFAULT_POLL_FREQUENCY
        )

    def find_element(self, locator: tuple) -> WebElement:
        """
        尋找元素（帶等待）

        Args:
            locator: 元素定位器 (By.XXX, "value")

        Returns:
            WebElement: 找到的元素

        Raises:
            TimeoutException: 當元素在超時時間內未找到
        """
        try:
            return self.wait.until(EC.presence_of_element_located(locator))
        except TimeoutException:
            print(f'[ERROR] Element not found: {locator}')
            raise

    def find_elements(self, locator: tuple) -> list:
        """
        尋找多個元素

        Args:
            locator: 元素定位器

        Returns:
            list: 元素列表
        """
        return self.driver.find_elements(*locator)

    def click(self, locator: tuple, use_js: bool = False, timeout: int = None):
        """
        點擊元素（處理攔截異常）

        Args:
            locator: 元素定位器
            use_js: 是否使用 JavaScript 點擊
            timeout: 自訂超時時間

        Raises:
            TimeoutException: 當元素不可點擊
        """
        wait = WebDriverWait(self.driver, timeout or self.timeout, self.DEFAULT_POLL_FREQUENCY)

        try:
            element = wait.until(EC.element_to_be_clickable(locator))

            if use_js:
                self.driver.execute_script("arguments[0].click();", element)
            else:
                element.click()

        except ElementClickInterceptedException:
            # 如果普通點擊被攔截，改用 JS 點擊
            element = self.find_element(locator)
            self.driver.execute_script("arguments[0].click();", element)

        except TimeoutException:
            print(f'[ERROR] Element not clickable: {locator}')
            raise

    def input_text(self, locator: tuple, text: str, clear_first: bool = True):
        """
        輸入文字

        Args:
            locator: 元素定位器
            text: 要輸入的文字
            clear_first: 是否先清除原有內容
        """
        element = self.find_element(locator)

        if clear_first:
            element.clear()

        element.send_keys(text)

    def get_text(self, locator: tuple) -> str:
        """
        取得元素文字

        Args:
            locator: 元素定位器

        Returns:
            str: 元素文字內容
        """
        element = self.find_element(locator)
        return element.text

    def get_attribute(self, locator: tuple, attribute: str) -> str:
        """
        取得元素屬性

        Args:
            locator: 元素定位器
            attribute: 屬性名稱

        Returns:
            str: 屬性值
        """
        element = self.find_element(locator)
        return element.get_attribute(attribute)

    def is_element_present(self, locator: tuple) -> bool:
        """
        檢查元素是否存在

        Args:
            locator: 元素定位器

        Returns:
            bool: 元素是否存在
        """
        try:
            self.driver.find_element(*locator)
            return True
        except NoSuchElementException:
            return False

    def is_element_visible(self, locator: tuple, timeout: int = 5) -> bool:
        """
        檢查元素是否可見

        Args:
            locator: 元素定位器
            timeout: 等待超時時間

        Returns:
            bool: 元素是否可見
        """
        try:
            wait = WebDriverWait(self.driver, timeout, self.DEFAULT_POLL_FREQUENCY)
            wait.until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False

    def scroll_to_element(self, locator: tuple, block: str = 'center'):
        """
        捲動到元素位置

        Args:
            locator: 元素定位器
            block: 對齊方式 ('start', 'center', 'end', 'nearest')
        """
        element = self.find_element(locator)
        self.driver.execute_script(
            f"arguments[0].scrollIntoView({{block: '{block}', behavior: 'smooth'}});",
            element
        )

    def wait_for_url_contains(self, url_part: str, timeout: int = None) -> bool:
        """
        等待 URL 包含特定字串

        Args:
            url_part: URL 片段
            timeout: 超時時間

        Returns:
            bool: 是否在超時時間內 URL 包含該字串
        """
        try:
            wait = WebDriverWait(self.driver, timeout or self.timeout)
            wait.until(EC.url_contains(url_part))
            return True
        except TimeoutException:
            return False

    def execute_script(self, script: str, *args):
        """
        執行 JavaScript

        Args:
            script: JavaScript 程式碼
            *args: 傳遞給 JS 的參數

        Returns:
            JavaScript 執行結果
        """
        return self.driver.execute_script(script, *args)

    def sleep(self, seconds: float):
        """
        暫停執行

        Args:
            seconds: 暫停秒數
        """
        time.sleep(seconds)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(timeout={self.timeout})"

    # ========== 頁面載入檢測方法 ==========

    def detect_server_error(self) -> dict:
        """
        檢測伺服器錯誤 (50X/40X)

        Returns:
            dict: {
                'has_error': bool,
                'status_code': int or None,
                'error_type': str or None,  # 'server_error' or 'client_error'
                'message': str or None
            }
        """
        result = {
            'has_error': False,
            'status_code': None,
            'error_type': None,
            'message': None
        }

        try:
            # 取得頁面文字內容
            body_text = self.driver.execute_script(
                "return document.body ? document.body.innerText : '';"
            ) or ""
            page_title = self.driver.title or ""

            # 伺服器錯誤模式 (50X)
            server_error_patterns = {
                500: ["500", "Internal Server Error", "內部伺服器錯誤"],
                502: ["502", "Bad Gateway", "錯誤的閘道"],
                503: ["503", "Service Unavailable", "服務暫時無法使用"],
                504: ["504", "Gateway Timeout", "閘道逾時"],
            }

            # 客戶端錯誤模式 (40X) - 這類不應重刷
            client_error_patterns = {
                400: ["400", "Bad Request"],
                401: ["401", "Unauthorized", "未授權"],
                403: ["403", "Forbidden", "禁止存取"],
                404: ["404", "Not Found", "找不到頁面", "頁面不存在"],
            }

            # 伺服器特徵 (nginx, apache 錯誤頁)
            server_signatures = [
                "nginx",
                "Apache",
                "The server encountered an error",
                "請稍後再試",
                "系統維護中",
            ]

            combined_text = f"{page_title} {body_text}".lower()

            # 檢查 50X 錯誤
            for code, patterns in server_error_patterns.items():
                for pattern in patterns:
                    if pattern.lower() in combined_text:
                        result['has_error'] = True
                        result['status_code'] = code
                        result['error_type'] = 'server_error'
                        result['message'] = f"偵測到伺服器錯誤 {code}"
                        return result

            # 檢查 40X 錯誤
            for code, patterns in client_error_patterns.items():
                for pattern in patterns:
                    if pattern.lower() in combined_text:
                        result['has_error'] = True
                        result['status_code'] = code
                        result['error_type'] = 'client_error'
                        result['message'] = f"偵測到客戶端錯誤 {code}"
                        return result

            # 檢查伺服器錯誤特徵
            for signature in server_signatures:
                if signature.lower() in combined_text:
                    # 需要額外確認是否為錯誤頁面（避免誤判）
                    if len(body_text) < 500:  # 錯誤頁面通常很短
                        result['has_error'] = True
                        result['error_type'] = 'server_error'
                        result['message'] = f"偵測到伺服器錯誤頁面特徵: {signature}"
                        return result

        except Exception as e:
            print(f"[WARN] 檢測伺服器錯誤時發生異常: {e}")

        return result

    def check_page_blank(self) -> dict:
        """
        檢測頁面是否空白（組合策略 D）

        Returns:
            dict: {
                'is_blank': bool,
                'checks': {
                    'body_visible': bool,
                    'has_content': bool,
                    'indicator_found': bool or None
                },
                'message': str or None
            }
        """
        result = {
            'is_blank': False,
            'checks': {
                'body_visible': True,
                'has_content': True,
                'indicator_found': None
            },
            'message': None
        }

        try:
            # 檢查 A: body 可見性
            body_visible = self.driver.execute_script("""
                var body = document.body;
                if (!body) return false;
                var style = window.getComputedStyle(body);
                return style.display !== 'none' && style.visibility !== 'hidden';
            """)
            result['checks']['body_visible'] = bool(body_visible)

            # 檢查 B: 內容長度
            content_length = self.driver.execute_script(
                "return document.body ? document.body.innerText.trim().length : 0;"
            ) or 0
            result['checks']['has_content'] = content_length >= self.MIN_CONTENT_LENGTH

            # 檢查 C: 關鍵元素存在（如果有定義）
            if self.PAGE_LOAD_INDICATOR:
                indicators = self.PAGE_LOAD_INDICATOR
                if isinstance(indicators, str):
                    indicators = [indicators]

                indicator_found = False
                for selector in indicators:
                    try:
                        element = self.driver.find_element("css selector", selector)
                        if element:
                            indicator_found = True
                            break
                    except NoSuchElementException:
                        continue

                result['checks']['indicator_found'] = indicator_found

            # 判斷是否空白
            # 規則: body 不可見 OR 內容太少 OR (有定義指標但找不到)
            if not result['checks']['body_visible']:
                result['is_blank'] = True
                result['message'] = "頁面 body 不可見 (display: none)"
            elif not result['checks']['has_content']:
                result['is_blank'] = True
                result['message'] = f"頁面內容過少 (長度: {content_length})"
            elif result['checks']['indicator_found'] is False:
                result['is_blank'] = True
                result['message'] = f"找不到關鍵元素: {self.PAGE_LOAD_INDICATOR}"

        except Exception as e:
            print(f"[WARN] 檢測空白頁時發生異常: {e}")
            result['is_blank'] = True
            result['message'] = f"檢測異常: {e}"

        return result

    def ensure_page_loaded(self, max_retries: int = None) -> bool:
        """
        確保頁面載入完成，空白或錯誤時自動重刷

        Args:
            max_retries: 最大重刷次數，預設為 MAX_RELOAD_RETRIES (3)

        Returns:
            bool: 頁面是否成功載入

        Raises:
            PageLoadError: 當無法恢復的錯誤發生時（如 40X 錯誤）
        """
        max_retries = max_retries or self.MAX_RELOAD_RETRIES
        current_url = self.driver.current_url

        for attempt in range(max_retries + 1):
            # 第一次是初始檢測，之後才是重刷
            if attempt > 0:
                delay = self.RELOAD_DELAYS[min(attempt - 1, len(self.RELOAD_DELAYS) - 1)]
                print(f"[INFO] 第 {attempt} 次重刷，等待 {delay} 秒...")
                time.sleep(delay)
                self.driver.refresh()
                time.sleep(2)  # 等待頁面基本載入

            # 步驟 1: 檢測伺服器錯誤
            server_check = self.detect_server_error()
            if server_check['has_error']:
                if server_check['error_type'] == 'client_error':
                    # 40X 錯誤不重刷，直接報錯
                    raise PageLoadError(
                        server_check['message'],
                        error_type='client_error',
                        status_code=server_check['status_code']
                    )
                elif server_check['error_type'] == 'server_error':
                    # 50X 錯誤，繼續嘗試重刷
                    print(f"[WARN] {server_check['message']}，嘗試重刷...")
                    continue

            # 步驟 2: 檢測空白頁
            blank_check = self.check_page_blank()
            if blank_check['is_blank']:
                print(f"[WARN] 空白頁: {blank_check['message']}，嘗試重刷...")
                continue

            # 頁面正常載入
            print(f"[INFO] 頁面載入成功: {current_url}")
            return True

        # 所有重刷嘗試都失敗
        raise PageLoadError(
            f"頁面載入失敗，已重刷 {max_retries} 次: {current_url}",
            error_type='blank_page'
        )

    def navigate_to(self, url: str, ensure_loaded: bool = True) -> bool:
        """
        導航到指定 URL，並確保頁面載入完成

        Args:
            url: 目標 URL
            ensure_loaded: 是否自動檢測並重刷空白頁

        Returns:
            bool: 導航是否成功

        Raises:
            PageLoadError: 當頁面載入失敗時
        """
        self.driver.get(url)

        if ensure_loaded:
            return self.ensure_page_loaded()

        return True
