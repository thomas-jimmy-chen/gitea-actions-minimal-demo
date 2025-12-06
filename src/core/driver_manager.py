#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
DriverManager - WebDriver 管理器
負責 WebDriver 的初始化、配置與生命週期管理
"""

import os
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from .config_loader import ConfigLoader


class DriverManager:
    """管理 WebDriver 生命週期與配置"""

    def __init__(self, config: ConfigLoader, stealth_enabled: bool = True):
        """
        初始化 Driver 管理器

        Args:
            config: 配置載入器
            stealth_enabled: 是否啟用 Stealth 模式
        """
        self.config = config
        self.driver = None
        self.stealth_enabled = stealth_enabled

    def create_driver(self, use_proxy: bool = True) -> webdriver.Chrome:
        """
        建立並配置 WebDriver

        Args:
            use_proxy: 是否使用 proxy（預設 True）

        Returns:
            webdriver.Chrome: 配置好的 Chrome WebDriver

        Raises:
            Exception: 當 WebDriver 初始化失敗時
        """
        try:
            opts = self._get_chrome_options(use_proxy=use_proxy)
            service = Service(self.config.get('execute_file'))
            self.driver = webdriver.Chrome(service=service, options=opts)
            self.driver.maximize_window()

            if self.stealth_enabled:
                self._inject_stealth()

            print('[INFO] WebDriver initialized successfully')
            return self.driver

        except Exception as e:
            print(f'[ERROR] Failed to initialize WebDriver: {e}')
            raise

    def _get_chrome_options(self, use_proxy: bool = True) -> ChromeOptions:
        """
        配置 Chrome 選項

        Args:
            use_proxy: 是否使用 proxy（預設 True）

        Returns:
            ChromeOptions: Chrome 瀏覽器選項
        """
        opts = ChromeOptions()

        # Proxy 設定（可選）
        if use_proxy:
            proxy_host = self.config.get('listen_host', '127.0.0.1')
            proxy_port = self.config.get('listen_port', '8080')
            opts.add_argument(f"--proxy-server={proxy_host}:{proxy_port}")
            opts.add_argument("--ignore-certificate-errors")

        # 靜默模式：抑制 Chrome 日誌輸出
        silent_mode = self.config.get_bool('silent_mitm', False)
        if silent_mode:
            opts.add_argument('--log-level=3')  # 只顯示 FATAL 錯誤
            opts.add_argument('--disable-logging')  # 禁用日誌
            opts.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
        else:
            # 反自動化檢測設定（非靜默模式）
            opts.add_experimental_option('excludeSwitches', ['enable-automation'])

        # 反自動化檢測設定
        opts.add_experimental_option('useAutomationExtension', False)

        # 偏好設定
        opts.add_experimental_option('prefs', {
            'credentials_enable_service': False,
            'profile.password_manager_enabled': False,
            'intl.accept_languages': 'zh-TW'
        })

        # User Agent
        opts.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')

        return opts

    def _inject_stealth(self):
        """
        注入 Stealth JS 腳本以繞過自動化檢測

        如果 stealth.min.js 不存在，會嘗試重新提取
        """
        js_path = os.path.join("resource", "plugins", "stealth.min.js")

        # 如果檔案不存在，嘗試重新提取
        if not os.path.exists(js_path):
            print('[WARN] stealth mode file not found, attempting to extract...')
            try:
                os.makedirs("resource/plugins", exist_ok=True)

                # Windows 相容性修復：使用 shell=True
                # 在 Windows 下，subprocess 需要通過 shell 來找到 npx.cmd
                import platform
                use_shell = platform.system() == 'Windows'

                subprocess.run(
                    ['npx', 'extract-stealth-evasions', '-o', js_path],
                    check=True,
                    capture_output=True,
                    shell=use_shell,  # Windows 下使用 shell
                    timeout=60
                )
                print('[INFO] stealth mode file extracted successfully')
            except subprocess.TimeoutExpired:
                print('[WARN] stealth mode file extraction timed out')
                return
            except Exception as e:
                print(f'[WARN] Failed to extract stealth mode file: {e}')
                return

        # 注入 JS 腳本
        try:
            with open(js_path, 'r', encoding='utf-8') as f:
                js_code = f.read()

            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': js_code})
            print('[INFO] Stealth mode enabled')

        except FileNotFoundError:
            print('[WARN] stealth mode file missing, stealth mode disabled')
        except Exception as e:
            print(f'[ERROR] Failed to inject stealth script: {e}')

    def quit(self):
        """關閉 WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                print('[INFO] WebDriver closed')
            except Exception as e:
                print(f'[WARN] Error while closing WebDriver: {e}')
            finally:
                self.driver = None

    def get_driver(self) -> webdriver.Chrome:
        """
        取得 WebDriver 實例

        Returns:
            webdriver.Chrome: WebDriver 實例

        Raises:
            RuntimeError: 當 Driver 尚未建立時
        """
        if self.driver is None:
            raise RuntimeError("Driver not initialized. Call create_driver() first.")
        return self.driver

    def __enter__(self):
        """Context manager 進入"""
        self.create_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 退出"""
        self.quit()

    def __repr__(self) -> str:
        return f"DriverManager(stealth={self.stealth_enabled}, driver={'active' if self.driver else 'inactive'})"
