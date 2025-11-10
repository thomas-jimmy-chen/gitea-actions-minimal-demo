#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
LoginPage - 登入頁面物件
處理登入相關的所有操作：Cookie 登入、手動登入、驗證碼處理
"""

import time
import base64
from selenium.webdriver.common.by import By
from .base_page import BasePage
from ..core.cookie_manager import CookieManager


class LoginPage(BasePage):
    """登入頁面物件"""

    # 元素定位器
    USERNAME_INPUT = (By.ID, 'user_name')
    PASSWORD_INPUT = (By.ID, 'password')
    CAPTCHA_IMAGE = (By.XPATH, "//form//img[contains(@src,'captcha')]")
    CAPTCHA_INPUT = (By.NAME, 'captcha_code')
    SUBMIT_BUTTON = (By.ID, 'submit')
    LOGIN_CONTENT = (By.CSS_SELECTOR, 'div.login-content.ng-scope')

    def __init__(self, driver, cookie_manager: CookieManager = None):
        """
        初始化登入頁面

        Args:
            driver: WebDriver 實例
            cookie_manager: Cookie 管理器（可選）
        """
        super().__init__(driver)
        self.cookie_manager = cookie_manager

    def goto(self, url: str):
        """
        前往登入頁面

        Args:
            url: 登入頁面 URL
        """
        self.driver.get(url)
        time.sleep(2)

    def is_login_required(self) -> bool:
        """
        檢查是否需要登入

        Returns:
            bool: True 表示需要登入，False 表示已登入
        """
        return self.is_element_present(self.LOGIN_CONTENT)

    def is_logged_in(self) -> bool:
        """
        檢查是否已登入

        Returns:
            bool: True 表示已登入
        """
        return not self.is_login_required()

    def login_with_cookies(self) -> bool:
        """
        使用 Cookies 登入

        Returns:
            bool: 登入是否成功
        """
        if self.cookie_manager is None:
            print('[WARN] CookieManager not provided, cannot login with cookies')
            return False

        cookies = self.cookie_manager.load()
        if not cookies:
            print('[INFO] No cookies found')
            return False

        print('[INFO] Attempting login with cookies...')

        # 刪除現有 cookies 並載入新的
        self.driver.delete_all_cookies()
        for cookie in cookies:
            try:
                self.driver.add_cookie(cookie)
            except Exception as e:
                print(f'[WARN] Failed to add cookie: {e}')

        # 重新整理頁面
        self.driver.refresh()
        time.sleep(5)

        # 檢查是否登入成功
        if self.is_logged_in():
            print('[SUCCESS] Logged in via cookies')
            return True
        else:
            print('[INFO] Cookie login failed')
            return False

    def save_captcha_image(self, output_path: str = 'captcha.png'):
        """
        儲存驗證碼圖片

        Args:
            output_path: 圖片儲存路徑
        """
        try:
            img_element = self.find_element(self.CAPTCHA_IMAGE)

            # 使用 Canvas 擷取圖片的 base64 編碼
            img_base64 = self.execute_script(
                """
                let e = arguments[0], c = document.createElement('canvas');
                c.width = e.width; c.height = e.height;
                c.getContext('2d').drawImage(e, 0, 0);
                return c.toDataURL('image/png').split(',')[1];
                """,
                img_element
            )

            # 解碼並儲存
            with open(output_path, 'wb') as f:
                f.write(base64.b64decode(img_base64))

            print(f'[INFO] Captcha image saved to {output_path}')

        except Exception as e:
            print(f'[ERROR] Failed to save captcha image: {e}')

    def login_manually(self, username: str, password: str, captcha: str = None):
        """
        手動登入

        Args:
            username: 使用者名稱
            password: 密碼
            captcha: 驗證碼（若為 None，會提示使用者輸入）

        Returns:
            bool: 登入是否成功
        """
        print('[INFO] Performing manual login...')

        # 輸入帳號密碼
        self.input_text(self.USERNAME_INPUT, username)
        self.input_text(self.PASSWORD_INPUT, password)

        # 處理驗證碼
        self.save_captcha_image()

        if captcha is None:
            captcha = input('[INPUT] Please enter captcha code: ')

        self.input_text(self.CAPTCHA_INPUT, captcha)

        # 點擊登入
        self.click(self.SUBMIT_BUTTON)
        time.sleep(3)

        # 儲存 cookies（如果登入成功）
        if self.is_logged_in() and self.cookie_manager:
            self.cookie_manager.save(self.driver.get_cookies())
            print('[INFO] Cookies saved')

        return self.is_logged_in()

    def auto_login(self, username: str, password: str, url: str) -> bool:
        """
        自動登入（先嘗試 cookies，失敗則手動登入）

        Args:
            username: 使用者名稱
            password: 密碼
            url: 登入頁面 URL

        Returns:
            bool: 登入是否成功
        """
        # 前往登入頁
        self.goto(url)

        # 如果已登入，直接返回
        if self.is_logged_in():
            print('[INFO] Already logged in')
            return True

        # 嘗試使用 cookies 登入
        if self.cookie_manager and self.login_with_cookies():
            return True

        # Cookie 登入失敗，進行手動登入
        print('[INFO] Cookie login failed, manual login required')
        success = self.login_manually(username, password)

        if success:
            print('[SUCCESS] Manual login succeeded')
        else:
            print('[ERROR] Login failed')

        return success

    def logout(self):
        """登出（如果有登出按鈕的話）"""
        # 這裡可以根據實際頁面實作登出邏輯
        pass
