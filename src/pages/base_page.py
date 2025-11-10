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


class BasePage:
    """所有頁面物件的基類"""

    # 預設等待時間
    DEFAULT_TIMEOUT = 40
    DEFAULT_POLL_FREQUENCY = 0.5

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
