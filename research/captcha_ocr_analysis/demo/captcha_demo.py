#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
CAPTCHA OCR 示範程式
====================

功能:
1. 使用 Stealth 模式啟動 ChromeDriver (繞過自動化檢測)
2. 自動辨識驗證碼 (使用 eebot optimized OCR，針對 4 位數字)
3. 自動填入帳號密碼並登入
4. 【渲染前】姓名替換: 陳偉鳴 → 陳〇〇 (使用 Object.defineProperty 攔截)
5. 【渲染前】輸入框背景變淺紅色 (#ffebee)
6. 【渲染前】Focus 時外框變亮紅色 (#f44336) + 光暈效果
7. 【渲染前】username 上方顯示 "***驗證碼自動 OCR 中***"
8. 【渲染前】驗證碼下方顯示 "***驗證碼自動 OCR 中***"
9. 登入成功後等待指定秒數
10. 重複執行指定次數
11. 結束時清理 cookies 與 stealth.min.js

姓名替換位置 (從 Burp Suite 分析):
- window.analyticsData.userName (JavaScript 變數攔截)
- window.CurrentName (JavaScript 變數攔截)
- <root-scope-variable name="currentUserName"> (AngularJS)
- 頁面所有文字節點 (MutationObserver 監聽)

技術實現:
- 使用 Chrome DevTools Protocol (CDP) 的 Page.addScriptToEvaluateOnNewDocument
- 在頁面 DOM 載入前注入 CSS 和 JavaScript
- 使用 Object.defineProperty 攔截 JavaScript 變數賦值
- 使用 MutationObserver 監聽動態載入的內容
- 確保樣式和姓名替換在網頁渲染時就已生效

使用方式:
    conda activate eebot
    python captcha_demo.py

作者: Claude Code (Opus 4.5)
日期: 2025-12-30
"""

import os
import sys
import json
import time
import base64
import shutil
import platform
import subprocess
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 專案根目錄
DEMO_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(DEMO_DIR)))

# 加入專案路徑
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ============================================================
# 常數定義
# ============================================================

# 檔案路徑
CREDENTIALS_FILE = os.path.join(DEMO_DIR, 'credentials.json')
COOKIES_FILE = os.path.join(DEMO_DIR, 'cookies.json')
STEALTH_JS_FILE = os.path.join(DEMO_DIR, 'stealth.min.js')
CAPTCHA_IMAGE_FILE = os.path.join(DEMO_DIR, 'captcha_temp.png')

# ChromeDriver 路徑 (可根據環境調整)
CHROMEDRIVER_PATHS = [
    'C:/tools/chromedriver/chromedriver.exe',  # eebot 預設路徑
    'chromedriver',
    'C:/chromedriver/chromedriver.exe',
    '/usr/local/bin/chromedriver',
]

# 樣式設定
HIGHLIGHT_COLOR = '#ff0000'  # 亮紅色
HIGHLIGHT_BORDER_WIDTH = '2px'

# OCR 提示訊息
OCR_NOTICE_MESSAGE = "***驗證碼自動 OCR 中***"

# 姓名替換設定 (從 Burp Suite 分析得到的位置)
# 規則：保留第一個字，其餘用〇替換
# 例如：陳偉鳴 → 陳〇〇、李四 → 李〇、司馬相如 → 司〇〇〇
ORIGINAL_NAME = "陳偉鳴"  # 從 Burp Suite 分析得到

# 在頁面渲染前注入的 CSS 和 JS
# 這段腳本會在每個頁面載入前執行，實現「渲染前」修改
PRE_RENDER_INJECTION_SCRIPT = """
(function() {
    // ============================================================
    // 姓名替換設定 (從 Burp Suite 分析得到)
    // ============================================================
    var ORIGINAL_NAME = '""" + ORIGINAL_NAME + """';

    // 動態生成替換名稱：保留第一個字，其餘用〇替換
    function maskName(name) {
        if (!name || name.length < 1) return name;
        var firstChar = name.charAt(0);
        var masked = firstChar;
        for (var i = 1; i < name.length; i++) {
            masked += '〇';  // U+3007 國字零
        }
        return masked;
    }

    var REPLACEMENT_NAME = maskName(ORIGINAL_NAME);

    // ============================================================
    // 1. 攔截並修改 JavaScript 全域變數 (渲染前)
    // ============================================================

    // 攔截 window.analyticsData
    var _analyticsData = null;
    Object.defineProperty(window, 'analyticsData', {
        get: function() { return _analyticsData; },
        set: function(val) {
            if (val && val.userName) {
                val.userName = val.userName.replace(ORIGINAL_NAME, REPLACEMENT_NAME);
            }
            if (val && val.orgName) {
                // orgName 不替換，保留原值
            }
            _analyticsData = val;
            console.log('[EEBot] analyticsData.userName 已替換');
        },
        configurable: true
    });

    // 攔截 CurrentName
    var _currentName = '';
    Object.defineProperty(window, 'CurrentName', {
        get: function() { return _currentName; },
        set: function(val) {
            _currentName = val ? val.replace(ORIGINAL_NAME, REPLACEMENT_NAME) : val;
            console.log('[EEBot] CurrentName 已替換');
        },
        configurable: true
    });

    // ============================================================
    // 2. DOM 載入後的處理
    // ============================================================
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', onDOMReady);
    } else {
        onDOMReady();
    }

    function onDOMReady() {
        applyLoginStyles();
        replaceNameInDOM();
    }

    // ============================================================
    // 3. 登入頁面樣式 (淺紅色背景、OCR 提示)
    // ============================================================
    function applyLoginStyles() {
        // 只在登入頁面執行
        if (!window.location.href.includes('/login')) return;

        // 注入 CSS 樣式
        if (!document.getElementById('eebot-pre-render-style')) {
            var style = document.createElement('style');
            style.id = 'eebot-pre-render-style';
            style.textContent = `
                /* 輸入欄位 - 淺紅色背景 */
                #user_name,
                #password,
                input[name="captcha_code"] {
                    background-color: #ffebee !important;
                    border: 2px solid #e57373 !important;
                    transition: all 0.3s ease !important;
                }

                /* Focus 時 - 亮紅色外框 */
                #user_name:focus,
                #password:focus,
                input[name="captcha_code"]:focus {
                    background-color: #ffcdd2 !important;
                    border-color: #f44336 !important;
                    box-shadow: 0 0 8px rgba(244, 67, 54, 0.6) !important;
                    outline: none !important;
                }

                /* OCR 提示文字樣式 */
                .eebot-ocr-notice {
                    text-align: center;
                    color: #d32f2f;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 8px;
                    margin: 5px 0;
                    background: linear-gradient(90deg, transparent, #ffcdd2, transparent);
                    animation: eebot-blink 1.5s ease-in-out infinite;
                }

                @keyframes eebot-blink {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.5; }
                }
            `;
            document.head.appendChild(style);
        }

        // 在 username 上方加入 OCR 提示
        var loginTip = document.querySelector('.login-tip');
        if (loginTip && !document.getElementById('eebot-notice-top')) {
            var noticeTop = document.createElement('div');
            noticeTop.id = 'eebot-notice-top';
            noticeTop.className = 'eebot-ocr-notice';
            noticeTop.textContent = '""" + OCR_NOTICE_MESSAGE + """';
            loginTip.parentNode.insertBefore(noticeTop, loginTip.nextSibling);
        }

        // 在驗證碼區塊下方加入 OCR 提示
        var captchaDiv = document.querySelector('.captcha-verification');
        if (captchaDiv && !document.getElementById('eebot-notice-bottom')) {
            var noticeBottom = document.createElement('div');
            noticeBottom.id = 'eebot-notice-bottom';
            noticeBottom.className = 'eebot-ocr-notice';
            noticeBottom.textContent = '""" + OCR_NOTICE_MESSAGE + """';
            captchaDiv.parentNode.insertBefore(noticeBottom, captchaDiv.nextSibling);
        }

        console.log('[EEBot] 登入頁面樣式已注入');
    }

    // ============================================================
    // 4. 替換 DOM 中的姓名 (所有頁面)
    // ============================================================
    function replaceNameInDOM() {
        if (!ORIGINAL_NAME) return;

        // 替換 AngularJS root-scope-variable
        var rootScopeVars = document.querySelectorAll('root-scope-variable[name="currentUserName"]');
        rootScopeVars.forEach(function(el) {
            if (el.getAttribute('value') === ORIGINAL_NAME) {
                el.setAttribute('value', REPLACEMENT_NAME);
                console.log('[EEBot] root-scope-variable 已替換');
            }
        });

        // 替換頁面中的文字節點
        replaceTextInElement(document.body);

        console.log('[EEBot] DOM 姓名替換完成');
    }

    function replaceTextInElement(element) {
        if (!element) return;

        // 遍歷所有子節點
        var walker = document.createTreeWalker(
            element,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );

        var textNodes = [];
        while (walker.nextNode()) {
            textNodes.push(walker.currentNode);
        }

        textNodes.forEach(function(node) {
            if (node.nodeValue && node.nodeValue.includes(ORIGINAL_NAME)) {
                node.nodeValue = node.nodeValue.replace(new RegExp(ORIGINAL_NAME, 'g'), REPLACEMENT_NAME);
            }
        });
    }

    // ============================================================
    // 5. MutationObserver 監聽動態載入的內容
    // ============================================================
    var observer = new MutationObserver(function(mutations) {
        applyLoginStyles();

        // 對新增的節點進行姓名替換
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === Node.ELEMENT_NODE) {
                    replaceTextInElement(node);
                } else if (node.nodeType === Node.TEXT_NODE) {
                    if (node.nodeValue && node.nodeValue.includes(ORIGINAL_NAME)) {
                        node.nodeValue = node.nodeValue.replace(new RegExp(ORIGINAL_NAME, 'g'), REPLACEMENT_NAME);
                    }
                }
            });
        });
    });

    observer.observe(document.documentElement, {
        childList: true,
        subtree: true
    });

    console.log('[EEBot] 渲染前腳本已載入 - 姓名替換 + 樣式注入');
})();
"""


# ============================================================
# Stealth 提取器
# ============================================================

class StealthExtractor:
    """提取 Stealth JS 腳本"""

    def __init__(self, output_path: str):
        self.output_path = output_path

    def extract(self) -> bool:
        """提取 stealth.min.js"""
        print('[INFO] 正在提取 stealth.min.js...')
        try:
            use_shell = platform.system() == 'Windows'
            result = subprocess.run(
                ['npx', 'extract-stealth-evasions'],
                check=True,
                capture_output=True,
                text=True,
                shell=use_shell,
                timeout=60
            )

            # 移動到指定位置
            if os.path.exists('stealth.min.js'):
                shutil.move('stealth.min.js', self.output_path)
                print('[SUCCESS] stealth.min.js 提取成功')
                return True
            else:
                print('[WARN] stealth.min.js 未生成')
                return False

        except subprocess.TimeoutExpired:
            print('[ERROR] 提取超時')
            return False
        except Exception as e:
            print(f'[ERROR] 提取失敗: {e}')
            return False

    def exists(self) -> bool:
        return os.path.exists(self.output_path)


# ============================================================
# ChromeDriver 管理器
# ============================================================

class DemoDriverManager:
    """示範程式專用的 Driver 管理器"""

    def __init__(self, stealth_js_path: str):
        self.stealth_js_path = stealth_js_path
        self.driver = None

    def _find_chromedriver(self) -> str:
        """尋找 ChromeDriver"""
        for path in CHROMEDRIVER_PATHS:
            if os.path.exists(path) or shutil.which(path):
                return path
        raise FileNotFoundError('找不到 ChromeDriver，請確認已安裝')

    def create_driver(self) -> webdriver.Chrome:
        """建立 Chrome WebDriver"""
        opts = ChromeOptions()

        # 反自動化檢測
        opts.add_experimental_option('excludeSwitches', ['enable-automation'])
        opts.add_experimental_option('useAutomationExtension', False)

        # 偏好設定
        opts.add_experimental_option('prefs', {
            'credentials_enable_service': False,
            'profile.password_manager_enabled': False,
            'intl.accept_languages': 'zh-TW'
        })

        # User Agent
        opts.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        # 建立 Driver
        try:
            chromedriver_path = self._find_chromedriver()
            service = Service(chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=opts)
        except FileNotFoundError:
            # 嘗試不指定路徑
            self.driver = webdriver.Chrome(options=opts)

        self.driver.maximize_window()

        # 注入 Stealth JS
        self._inject_stealth()

        print('[INFO] WebDriver 初始化成功')
        return self.driver

    def _inject_stealth(self):
        """注入 Stealth JS"""
        if not os.path.exists(self.stealth_js_path):
            print('[WARN] stealth.min.js 不存在，跳過注入')
        else:
            try:
                with open(self.stealth_js_path, 'r', encoding='utf-8') as f:
                    js_code = f.read()

                self.driver.execute_cdp_cmd(
                    'Page.addScriptToEvaluateOnNewDocument',
                    {'source': js_code}
                )
                print('[INFO] Stealth 模式已啟用')

            except Exception as e:
                print(f'[WARN] Stealth 注入失敗: {e}')

        # 注入登入頁面樣式修改腳本 (在頁面渲染前執行)
        self._inject_login_style_script()

    def _inject_login_style_script(self):
        """注入登入頁面樣式修改腳本 (渲染前)"""
        try:
            self.driver.execute_cdp_cmd(
                'Page.addScriptToEvaluateOnNewDocument',
                {'source': PRE_RENDER_INJECTION_SCRIPT}
            )
            print('[INFO] 登入頁面樣式腳本已注入 (渲染前生效)')
        except Exception as e:
            print(f'[WARN] 樣式腳本注入失敗: {e}')

    def quit(self):
        """關閉 WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                print('[INFO] WebDriver 已關閉')
            except Exception:
                pass
            finally:
                self.driver = None


# ============================================================
# CAPTCHA OCR (使用 eebot 的 optimized OCR)
# ============================================================

class CaptchaOCR:
    """CAPTCHA 辨識器 (使用 eebot 的 optimized OCR，針對 4 位數字驗證碼)"""

    def __init__(self):
        # 載入 eebot 的 OCR 模組
        from src.utils.captcha_ocr import solve_captcha_with_confidence
        self.solve_captcha = solve_captcha_with_confidence

    def recognize(self, image_path: str) -> Optional[str]:
        """辨識驗證碼圖片 (4 位數字)"""
        try:
            result, confidence = self.solve_captcha(image_path, min_confidence='low')
            if result:
                print(f'[OCR] 辨識結果: {result} (信心: {confidence})')
                return result
            return None
        except Exception as e:
            print(f'[ERROR] OCR 辨識失敗: {e}')
            return None

    def recognize_bytes(self, image_bytes: bytes) -> Optional[str]:
        """辨識驗證碼 bytes (需先存檔)"""
        temp_path = os.path.join(DEMO_DIR, 'captcha_temp.png')
        try:
            with open(temp_path, 'wb') as f:
                f.write(image_bytes)
            return self.recognize(temp_path)
        except Exception as e:
            print(f'[ERROR] OCR 辨識失敗: {e}')
            return None
        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass


# ============================================================
# 登入頁面處理
# ============================================================

class LoginHandler:
    """登入頁面處理器"""

    # 元素定位器 (elearn.post.gov.tw - 郵政 e 大學)
    # 參考 eebot src/pages/login_page.py 已驗證可用的選擇器
    USERNAME_SELECTORS = [
        (By.ID, 'user_name'),
        (By.NAME, 'user_name'),
        (By.CSS_SELECTOR, 'input[type="text"]'),
    ]
    PASSWORD_SELECTORS = [
        (By.ID, 'password'),
        (By.NAME, 'password'),
        (By.CSS_SELECTOR, 'input[type="password"]'),
    ]
    CAPTCHA_IMAGE_SELECTORS = [
        (By.XPATH, "//form//img[contains(@src,'captcha')]"),  # eebot 使用的選擇器
        (By.XPATH, "//img[contains(@src,'captcha')]"),
        (By.CSS_SELECTOR, 'img.captcha'),
    ]
    CAPTCHA_INPUT_SELECTORS = [
        (By.NAME, 'captcha_code'),
        (By.ID, 'captcha_code'),
        (By.CSS_SELECTOR, 'input[placeholder*="驗證碼"]'),
    ]
    SUBMIT_SELECTORS = [
        (By.ID, 'submit'),
        (By.CSS_SELECTOR, 'button[type="submit"]'),
        (By.XPATH, "//button[contains(text(),'登入')]"),
    ]

    def __init__(self, driver):
        self.driver = driver
        self.ocr = CaptchaOCR()

    def _find_element(self, selectors: list, timeout: int = 10):
        """嘗試多個選擇器尋找元素"""
        for by, value in selectors:
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((by, value))
                )
                return element
            except TimeoutException:
                continue
        return None

    def _highlight_element(self, element, color: str = HIGHLIGHT_COLOR):
        """將元素邊框設為亮紅色"""
        if element:
            try:
                self.driver.execute_script(
                    f"arguments[0].style.border = '{HIGHLIGHT_BORDER_WIDTH} solid {color}';",
                    element
                )
            except Exception:
                pass

    def goto(self, url: str):
        """導航到登入頁面"""
        print(f'[INFO] 正在前往: {url}')
        self.driver.get(url)
        time.sleep(3)

    def fill_credentials(self, username: str, password: str) -> bool:
        """填入帳號密碼 (使用 JavaScript 直接設值，避免顯示明文)"""
        print('[INFO] 正在填入帳號密碼...')

        # 尋找並填入帳號 (使用 JavaScript 設值)
        username_input = self._find_element(self.USERNAME_SELECTORS)
        if not username_input:
            print('[ERROR] 找不到帳號輸入框')
            return False

        # 用 JavaScript 直接設值，不會逐字顯示
        # 同時觸發 input 事件讓框架 (Angular/React) 能偵測到變化
        self.driver.execute_script("""
            var el = arguments[0];
            var value = arguments[1];
            el.value = value;
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
        """, username_input, username)
        self._highlight_element(username_input)
        print(f'[INFO] 帳號已填入: {"*" * len(username)}')

        # 尋找並填入密碼 (密碼欄位本身就是隱藏的)
        password_input = self._find_element(self.PASSWORD_SELECTORS)
        if not password_input:
            print('[ERROR] 找不到密碼輸入框')
            return False

        password_input.clear()
        password_input.send_keys(password)
        self._highlight_element(password_input)
        print('[INFO] 密碼已填入: ***')

        return True

    def get_captcha_image(self) -> Optional[bytes]:
        """取得驗證碼圖片 bytes"""
        captcha_img = self._find_element(self.CAPTCHA_IMAGE_SELECTORS, timeout=5)
        if not captcha_img:
            print('[WARN] 找不到驗證碼圖片')
            return None

        try:
            # 使用 Canvas 擷取圖片
            img_base64 = self.driver.execute_script("""
                let e = arguments[0], c = document.createElement('canvas');
                c.width = e.naturalWidth || e.width;
                c.height = e.naturalHeight || e.height;
                c.getContext('2d').drawImage(e, 0, 0);
                return c.toDataURL('image/png').split(',')[1];
            """, captcha_img)

            return base64.b64decode(img_base64)

        except Exception as e:
            print(f'[ERROR] 擷取驗證碼圖片失敗: {e}')
            return None

    def fill_captcha(self, captcha_code: str) -> bool:
        """填入驗證碼"""
        captcha_input = self._find_element(self.CAPTCHA_INPUT_SELECTORS, timeout=5)
        if not captcha_input:
            print('[WARN] 找不到驗證碼輸入框')
            return False

        captcha_input.clear()
        captcha_input.send_keys(captcha_code)
        self._highlight_element(captcha_input)
        print(f'[INFO] 驗證碼已填入: {captcha_code}')
        return True

    def submit(self) -> bool:
        """點擊登入按鈕"""
        submit_btn = self._find_element(self.SUBMIT_SELECTORS)
        if not submit_btn:
            print('[ERROR] 找不到登入按鈕')
            return False

        submit_btn.click()
        print('[INFO] 已點擊登入按鈕')
        return True

    def _mask_real_name(self):
        """遮蔽頁面上的真實姓名 (只顯示第一個字 + ○○)"""
        try:
            # 郵政 e 大學專用：精確遮蔽姓名，避免影響選單
            self.driver.execute_script("""
                function maskName(text) {
                    if (!text || text.length < 2) return text;
                    return text.charAt(0) + '○○';
                }

                // 排除清單：這些是選單項目或標籤，不應該遮蔽
                var menuKeywords = ['首頁', '課程', '學程', '考試', '公告', '設置', '管理',
                                    '資源', '題庫', '應用', '學習', '履歷', '進度', '完成',
                                    '學員', '教師', '管理', '待辦', '最近', '最新', '總數',
                                    '事項', '造訪', '訊息', '中心', '帳戶', '個人'];

                function isMenuText(text) {
                    return menuKeywords.some(function(kw) {
                        return text.indexOf(kw) !== -1 || kw.indexOf(text) !== -1;
                    });
                }

                // 方法1: 頭像下方的姓名
                // 郵政 e 大學: 頭像在 .user-avatar 或 img 內，姓名在附近的文字節點
                var avatarContainers = document.querySelectorAll('[class*="user"], [class*="profile"], [class*="avatar"]');
                avatarContainers.forEach(function(container) {
                    // 找容器內的圖片（頭像）
                    var hasAvatar = container.querySelector('img') ||
                                   container.querySelector('[class*="avatar"]') ||
                                   container.querySelector('svg');
                    if (!hasAvatar) return;

                    // 找容器內的文字，排除選單
                    var textElements = container.querySelectorAll('span, div, p');
                    textElements.forEach(function(el) {
                        // 跳過有子元素的（可能是容器）
                        if (el.children.length > 0) return;
                        // 跳過選單連結
                        if (el.closest('a[href], nav, [role="menu"]')) return;

                        var text = el.textContent.trim();
                        if (text.length >= 2 && text.length <= 4 &&
                            /^[\u4e00-\u9fa5]+$/.test(text) && !isMenuText(text)) {
                            el.textContent = maskName(text);
                        }
                    });
                });

                // 方法2: 右上角的用戶名 (header 區域的中文姓名)
                var headerArea = document.querySelector('header, .header, [class*="top-bar"], [class*="navbar"]');
                if (headerArea) {
                    var spans = headerArea.querySelectorAll('span, a');
                    spans.forEach(function(el) {
                        var text = el.textContent.trim();
                        if (text.length >= 2 && text.length <= 4 &&
                            /^[\u4e00-\u9fa5]+$/.test(text) && !isMenuText(text)) {
                            // 只處理看起來像姓名的（不是選單）
                            if (!el.href && !el.closest('nav')) {
                                el.childNodes.forEach(function(node) {
                                    if (node.nodeType === 3) { // Text node
                                        var nodeText = node.textContent.trim();
                                        if (nodeText.length >= 2 && nodeText.length <= 4 &&
                                            /^[\u4e00-\u9fa5]+$/.test(nodeText) && !isMenuText(nodeText)) {
                                            node.textContent = maskName(nodeText);
                                        }
                                    }
                                });
                            }
                        }
                    });
                }
            """)
            print('[INFO] 已遮蔽頁面上的真實姓名')
        except Exception as e:
            print(f'[WARN] 遮蔽姓名時發生錯誤: {e}')

    def is_login_success(self) -> bool:
        """檢查是否登入成功"""
        time.sleep(3)

        try:
            # 檢查 URL 是否改變
            current_url = self.driver.current_url
            print(f'[DEBUG] 當前 URL: {current_url}')

            if 'login' not in current_url.lower():
                # 登入成功，遮蔽真實姓名後再截圖
                self._mask_real_name()

                # 截圖以便診斷
                screenshot_path = os.path.join(DEMO_DIR, 'login_result.png')
                try:
                    self.driver.save_screenshot(screenshot_path)
                    print(f'[DEBUG] 截圖已儲存: {screenshot_path}')
                except Exception as e:
                    print(f'[DEBUG] 截圖失敗: {e}')

                return True

            # 檢查頁面是否有錯誤訊息
            try:
                page_source = self.driver.page_source
                if '驗證碼錯誤' in page_source:
                    print('[DEBUG] 頁面包含驗證碼錯誤訊息')
                    return False
            except Exception:
                pass

            # 截圖 (登入失敗時)
            screenshot_path = os.path.join(DEMO_DIR, 'login_result.png')
            try:
                self.driver.save_screenshot(screenshot_path)
                print(f'[DEBUG] 截圖已儲存: {screenshot_path}')
            except Exception:
                pass

            # 檢查是否還有登入表單 (使用 CSS 選擇器更快)
            try:
                login_content = self.driver.find_element(By.CSS_SELECTOR, 'div.login-content')
                return False  # 還在登入頁面
            except NoSuchElementException:
                return True  # 已離開登入頁面

        except Exception as e:
            print(f'[ERROR] 檢查登入狀態時發生錯誤: {e}')
            # 如果會話失效，假設登入成功 (頁面已跳轉)
            return True

    def auto_login(self, username: str, password: str, max_retries: int = 3) -> bool:
        """自動登入 (含驗證碼辨識)"""
        for attempt in range(1, max_retries + 1):
            print(f'\n[INFO] === 登入嘗試 {attempt}/{max_retries} ===')

            # 填入帳號密碼
            if not self.fill_credentials(username, password):
                continue

            # 取得並辨識驗證碼
            captcha_bytes = self.get_captcha_image()
            if captcha_bytes:
                captcha_code = self.ocr.recognize_bytes(captcha_bytes)
                if captcha_code:
                    self.fill_captcha(captcha_code)
                else:
                    print('[WARN] 驗證碼辨識失敗')
                    continue
            else:
                print('[INFO] 此頁面可能無驗證碼')

            # 提交
            time.sleep(1)
            if not self.submit():
                continue

            # 檢查結果
            time.sleep(3)
            if self.is_login_success():
                print('[SUCCESS] 登入成功！')
                return True
            else:
                print('[WARN] 登入失敗，可能是驗證碼錯誤')
                # 重新整理頁面
                self.driver.refresh()
                time.sleep(2)

        print('[ERROR] 已達最大重試次數')
        return False


# ============================================================
# Cookie 管理
# ============================================================

class CookieHandler:
    """Cookie 處理器"""

    def __init__(self, driver, cookie_file: str):
        self.driver = driver
        self.cookie_file = cookie_file

    def save(self):
        """儲存 Cookies"""
        try:
            cookies = self.driver.get_cookies()
            with open(self.cookie_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            print(f'[INFO] Cookies 已儲存: {self.cookie_file}')
        except Exception as e:
            print(f'[WARN] 儲存 Cookies 失敗: {e}')

    def load(self) -> bool:
        """載入 Cookies"""
        if not os.path.exists(self.cookie_file):
            return False

        try:
            with open(self.cookie_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)

            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except Exception:
                    pass

            print('[INFO] Cookies 已載入')
            return True
        except Exception as e:
            print(f'[WARN] 載入 Cookies 失敗: {e}')
            return False

    def clear_file(self):
        """刪除 Cookie 檔案"""
        if os.path.exists(self.cookie_file):
            os.remove(self.cookie_file)
            print(f'[INFO] Cookie 檔案已刪除: {self.cookie_file}')


# ============================================================
# 主程式
# ============================================================

def load_credentials() -> dict:
    """載入登入憑證"""
    if not os.path.exists(CREDENTIALS_FILE):
        print(f'[ERROR] 找不到憑證檔案: {CREDENTIALS_FILE}')
        print('[INFO] 請建立 credentials.json 並填入帳號密碼')
        sys.exit(1)

    with open(CREDENTIALS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def cleanup():
    """清理暫存檔案"""
    print('\n[INFO] 正在清理暫存檔案...')

    files_to_delete = [
        COOKIES_FILE,
        STEALTH_JS_FILE,
        CAPTCHA_IMAGE_FILE,
    ]

    for filepath in files_to_delete:
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f'[INFO] 已刪除: {os.path.basename(filepath)}')
            except Exception as e:
                print(f'[WARN] 刪除失敗 {filepath}: {e}')

    print('[INFO] 清理完成')


def run_single_cycle(credentials: dict, cycle_num: int) -> bool:
    """執行單次登入流程 (無論成功或失敗都會關閉 ChromeDriver)"""
    print('\n' + '=' * 60)
    print(f'  第 {cycle_num} 次執行')
    print('=' * 60)

    driver_manager = None
    success = False

    try:
        # 1. 提取 Stealth JS (如果不存在)
        stealth_extractor = StealthExtractor(STEALTH_JS_FILE)
        if not stealth_extractor.exists():
            stealth_extractor.extract()

        # 2. 建立 WebDriver
        driver_manager = DemoDriverManager(STEALTH_JS_FILE)
        driver = driver_manager.create_driver()

        # 3. 建立處理器
        login_handler = LoginHandler(driver)
        cookie_handler = CookieHandler(driver, COOKIES_FILE)

        # 4. 前往登入頁面
        login_handler.goto(credentials['url'])

        # 5. 自動登入
        success = login_handler.auto_login(
            username=credentials['username'],
            password=credentials['password'],
            max_retries=3
        )

        if success:
            # 6. 儲存 Cookies
            cookie_handler.save()

            # 7. 等待指定秒數
            wait_time = credentials.get('wait_after_login', 5)
            print(f'[INFO] 登入成功，等待 {wait_time} 秒...')
            time.sleep(wait_time)

    except Exception as e:
        print(f'[ERROR] 執行發生錯誤: {e}')
        success = False

    finally:
        # 無論成功或失敗，一定要關閉 WebDriver
        print(f'[INFO] 正在關閉 ChromeDriver (第 {cycle_num} 次)...')
        if driver_manager:
            try:
                driver_manager.quit()
                print(f'[INFO] ChromeDriver 已關閉 (第 {cycle_num} 次)')
            except Exception as e:
                print(f'[WARN] 關閉 ChromeDriver 時發生錯誤: {e}')

    return success


def main():
    """主程式"""
    print('=' * 60)
    print('  CAPTCHA OCR 示範程式')
    print('  使用 eebot optimized OCR + Stealth ChromeDriver')
    print('=' * 60)

    # 載入憑證
    credentials = load_credentials()
    repeat_count = credentials.get('repeat_count', 5)

    print(f'\n[INFO] 登入網址: {credentials["url"]}')
    print(f'[INFO] 帳號: {"*" * len(credentials["username"])}')
    print(f'[INFO] 重複次數: {repeat_count}')

    # 執行多次
    success_count = 0
    for i in range(1, repeat_count + 1):
        if run_single_cycle(credentials, i):
            success_count += 1

        # 每次執行間隔
        if i < repeat_count:
            print('\n[INFO] 等待 3 秒後進行下一次...')
            time.sleep(3)

    # 結果統計
    print('\n' + '=' * 60)
    print('  執行結果')
    print('=' * 60)
    print(f'成功: {success_count}/{repeat_count}')
    print(f'失敗: {repeat_count - success_count}/{repeat_count}')

    # 清理
    cleanup()

    print('\n[INFO] 示範程式結束')


if __name__ == '__main__':
    main()
