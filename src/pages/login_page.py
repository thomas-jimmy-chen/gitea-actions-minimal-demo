#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
LoginPage - Login Page Object
Handles all login operations: Cookie login, manual login, CAPTCHA OCR
"""

import time
import base64
from selenium.webdriver.common.by import By
from .base_page import BasePage
from ..core.cookie_manager import CookieManager
from ..utils.captcha_ocr import solve_captcha_with_confidence


class LoginPage(BasePage):
    """Login Page Object"""

    # Element Locators
    USERNAME_INPUT = (By.ID, 'user_name')
    PASSWORD_INPUT = (By.ID, 'password')
    CAPTCHA_IMAGE = (By.XPATH, "//form//img[contains(@src,'captcha')]")
    CAPTCHA_INPUT = (By.NAME, 'captcha_code')
    SUBMIT_BUTTON = (By.ID, 'submit')
    LOGIN_CONTENT = (By.CSS_SELECTOR, 'div.login-content.ng-scope')
    CAPTCHA_ERROR = (By.XPATH, "//*[contains(text(),'驗證碼錯誤')]")
    CAPTCHA_REFRESH = (By.XPATH, "//form//img[contains(@src,'captcha')]/following-sibling::*[contains(@class,'refresh') or contains(@class,'reload') or @title='刷新']")

    # Default OCR Settings
    DEFAULT_MAX_OCR_RETRIES = 3
    DEFAULT_MIN_CONFIDENCE = 'medium'

    def __init__(self, driver, cookie_manager: CookieManager = None):
        """
        Initialize Login Page

        Args:
            driver: WebDriver instance
            cookie_manager: Cookie Manager (optional)
        """
        super().__init__(driver)
        self.cookie_manager = cookie_manager

    def goto(self, url: str):
        """
        Navigate to login page

        Args:
            url: Login page URL
        """
        self.driver.get(url)
        time.sleep(2)

    def is_login_required(self) -> bool:
        """
        Check if login is required

        Returns:
            bool: True if login required, False if already logged in
        """
        return self.is_element_present(self.LOGIN_CONTENT)

    def is_logged_in(self) -> bool:
        """
        Check if already logged in

        Returns:
            bool: True if logged in
        """
        return not self.is_login_required()

    def login_with_cookies(self) -> bool:
        """
        Login using Cookies

        Returns:
            bool: True if login successful
        """
        if self.cookie_manager is None:
            print('[WARN] CookieManager not provided, cannot login with cookies')
            return False

        cookies = self.cookie_manager.load()
        if not cookies:
            print('[INFO] No cookies found')
            return False

        print('[INFO] Attempting login with cookies...')

        # Delete existing cookies and load new ones
        self.driver.delete_all_cookies()
        for cookie in cookies:
            try:
                self.driver.add_cookie(cookie)
            except Exception as e:
                print(f'[WARN] Failed to add cookie: {e}')

        # Refresh page
        self.driver.refresh()
        time.sleep(5)

        # Check login status
        if self.is_logged_in():
            print('[SUCCESS] Logged in via cookies')
            return True
        else:
            print('[INFO] Cookie login failed')
            return False

    def save_captcha_image(self, output_path: str = 'captcha.png') -> bool:
        """
        Save CAPTCHA image

        Args:
            output_path: Image save path

        Returns:
            bool: True if saved successfully
        """
        try:
            img_element = self.find_element(self.CAPTCHA_IMAGE)

            # Use Canvas to capture base64 encoded image
            img_base64 = self.execute_script(
                """
                let e = arguments[0], c = document.createElement('canvas');
                c.width = e.width; c.height = e.height;
                c.getContext('2d').drawImage(e, 0, 0);
                return c.toDataURL('image/png').split(',')[1];
                """,
                img_element
            )

            # Decode and save
            with open(output_path, 'wb') as f:
                f.write(base64.b64decode(img_base64))

            return True

        except Exception as e:
            print(f'[ERROR] Failed to save captcha image: {e}')
            return False

    def refresh_captcha(self) -> bool:
        """
        Refresh CAPTCHA image

        Returns:
            bool: True if refreshed successfully
        """
        try:
            # Method 1: Try clicking refresh icon
            try:
                refresh_btn = self.find_element(self.CAPTCHA_REFRESH)
                refresh_btn.click()
                time.sleep(0.5)
                return True
            except:
                pass

            # Method 2: Click CAPTCHA image
            img_element = self.find_element(self.CAPTCHA_IMAGE)
            img_element.click()
            time.sleep(0.5)
            return True

        except Exception as e:
            print(f'[ERROR] Failed to refresh captcha: {e}')
            return False

    def check_captcha_error(self) -> bool:
        """
        Check if CAPTCHA error message is displayed

        Returns:
            bool: True if error message displayed
        """
        try:
            error_element = self.find_element(self.CAPTCHA_ERROR)
            return error_element.is_displayed()
        except:
            return False

    def clear_and_fill_form(self, username: str, password: str, captcha: str) -> bool:
        """
        Clear and fill login form

        Args:
            username: Username
            password: Password
            captcha: CAPTCHA code

        Returns:
            bool: True if filled successfully
        """
        try:
            # Clear and fill username
            username_input = self.find_element(self.USERNAME_INPUT)
            username_input.clear()
            time.sleep(0.1)
            username_input.send_keys(username)

            # Clear and fill password
            password_input = self.find_element(self.PASSWORD_INPUT)
            password_input.clear()
            time.sleep(0.1)
            password_input.send_keys(password)

            # Clear and fill CAPTCHA
            captcha_input = self.find_element(self.CAPTCHA_INPUT)
            captcha_input.clear()
            time.sleep(0.1)
            captcha_input.send_keys(captcha)

            return True

        except Exception as e:
            print(f'[ERROR] Failed to fill form: {e}')
            return False

    def submit_login(self) -> bool:
        """
        Click login button

        Returns:
            bool: True if clicked successfully
        """
        try:
            self.click(self.SUBMIT_BUTTON)
            time.sleep(2)
            return True
        except Exception as e:
            print(f'[ERROR] Failed to click login: {e}')
            return False

    def login_with_ocr(self, username: str, password: str,
                       max_retries: int = None,
                       min_confidence: str = None) -> bool:
        """
        Login with automatic CAPTCHA OCR recognition

        Args:
            username: Username
            password: Password
            max_retries: Max OCR retry attempts (default: 3)
            min_confidence: Minimum confidence level (default: 'medium')

        Returns:
            bool: True if login successful
        """
        max_retries = max_retries or self.DEFAULT_MAX_OCR_RETRIES
        min_confidence = min_confidence or self.DEFAULT_MIN_CONFIDENCE

        print(f'[INFO] OCR Login (max_retries={max_retries}, min_confidence={min_confidence})')

        for attempt in range(1, max_retries + 1):
            print(f'[OCR] Attempt {attempt}/{max_retries}')

            # 1. Save CAPTCHA image
            if not self.save_captcha_image():
                print('  Failed to save captcha, retrying...')
                self.refresh_captcha()
                continue

            # 2. OCR recognition
            result, confidence = solve_captcha_with_confidence('captcha.png', min_confidence)

            if result is None:
                if confidence:
                    print(f'  OCR failed: invalid format or low confidence ({confidence})')
                else:
                    print('  OCR failed: recognition error')
                self.refresh_captcha()
                continue

            print(f'  OCR result: {result} (confidence: {confidence})')

            # 3. Clear and fill form
            if not self.clear_and_fill_form(username, password, result):
                print('  Failed to fill form')
                continue

            # 4. Submit login
            if not self.submit_login():
                print('  Failed to submit')
                continue

            # 5. Check result
            if self.is_logged_in():
                print(f'[SUCCESS] Login successful (attempt {attempt})')
                # Wait for page to fully load after login
                time.sleep(5)
                return True

            if self.check_captcha_error():
                print('  CAPTCHA error, refreshing...')
                self.refresh_captcha()
                time.sleep(0.5)
            else:
                print('  Login failed (not CAPTCHA error)')
                # Might be wrong credentials, don't continue
                break

        # OCR failed, fallback to manual
        print(f'[INFO] OCR failed after {max_retries} attempts, switching to manual input')
        return self.login_manually_input(username, password)

    def login_manually_input(self, username: str, password: str) -> bool:
        """
        Manual CAPTCHA input login

        Args:
            username: Username
            password: Password

        Returns:
            bool: True if login successful
        """
        print('[INFO] Manual CAPTCHA input mode')

        # Refresh CAPTCHA
        self.refresh_captcha()
        time.sleep(0.5)

        # Save for viewing
        self.save_captcha_image()
        print('[INFO] CAPTCHA saved to captcha.png')

        # Get manual input
        captcha = input('[INPUT] Please enter CAPTCHA code: ')

        # Fill and submit
        if self.clear_and_fill_form(username, password, captcha):
            self.submit_login()
            time.sleep(2)

            if self.is_logged_in():
                print('[SUCCESS] Manual login successful')
                # Wait for page to fully load after login
                time.sleep(5)
                return True

        print('[FAILED] Login failed')
        return False

    def login_manually(self, username: str, password: str, captcha: str = None):
        """
        Manual login (legacy compatibility)

        Args:
            username: Username
            password: Password
            captcha: CAPTCHA code (if None, will use OCR with manual fallback)

        Returns:
            bool: True if login successful
        """
        print('[INFO] Performing login...')

        if captcha is None:
            # Use OCR with manual fallback
            return self.login_with_ocr(username, password)

        # Direct login with provided CAPTCHA
        self.save_captcha_image()
        self.input_text(self.USERNAME_INPUT, username)
        self.input_text(self.PASSWORD_INPUT, password)
        self.input_text(self.CAPTCHA_INPUT, captcha)

        self.click(self.SUBMIT_BUTTON)
        time.sleep(3)

        # Save cookies if successful
        if self.is_logged_in() and self.cookie_manager:
            self.cookie_manager.save(self.driver.get_cookies())
            print('[INFO] Cookies saved')

        return self.is_logged_in()

    def auto_login(self, username: str, password: str, url: str,
                   max_ocr_retries: int = None,
                   min_confidence: str = None) -> bool:
        """
        Automatic login (try cookies first, then OCR, then manual)

        Args:
            username: Username
            password: Password
            url: Login page URL
            max_ocr_retries: Max OCR retry attempts
            min_confidence: Minimum OCR confidence level

        Returns:
            bool: True if login successful
        """
        # Navigate to login page
        self.goto(url)

        # Check if already logged in
        if self.is_logged_in():
            print('[INFO] Already logged in')
            return True

        # Try cookie login
        if self.cookie_manager and self.login_with_cookies():
            return True

        # Cookie login failed, use OCR login
        print('[INFO] Cookie login failed, attempting OCR login')
        success = self.login_with_ocr(
            username, password,
            max_retries=max_ocr_retries,
            min_confidence=min_confidence
        )

        if success:
            # Save cookies for next time
            if self.cookie_manager:
                self.cookie_manager.save(self.driver.get_cookies())
                print('[INFO] Cookies saved')
            print('[SUCCESS] Login succeeded')
        else:
            print('[ERROR] Login failed')

        return success

    def logout(self):
        """Logout (if logout button exists)"""
        # Implement logout logic based on actual page
        pass
