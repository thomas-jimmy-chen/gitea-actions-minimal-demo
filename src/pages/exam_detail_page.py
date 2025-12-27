#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
ExamDetailPage - 考試詳情頁面物件
處理考試頁面的操作：點擊考試、勾選同意、確認答題等
Created: 2025-01-13
"""

import time
from selenium.webdriver.common.by import By
from .base_page import BasePage


class ExamDetailPage(BasePage):
    """考試詳情頁面物件"""

    # 元素定位器
    # 同意考試紀律的 checkbox
    AGREEMENT_CHECKBOX = (By.XPATH, "//input[@type='checkbox' and @name='confirm' and @ng-model='ui.confirmationCheck']")

    # 彈窗內的"繼續答題"按鈕
    POPUP_CONTINUE_BUTTON = (By.XPATH, "//button[@class='button button-green medium' and @ng-click='takeExam(exam.referrer_type)']")

    def click_exam_by_name(self, exam_name: str, delay: float = 10.0):
        """
        根據考試名稱點擊考試（多策略版本）

        Args:
            exam_name: 考試名稱（例如："高齡測驗(100分及格)"）
            delay: 點擊前的延遲時間（秒），預設 10 秒
        """
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        try:
            # 等待指定時間
            time.sleep(delay)

            wait = WebDriverWait(self.driver, 30)
            element = None
            successful_strategy = None

            # 提取考試名稱的關鍵詞（去除常見後綴）
            # 例如："金融友善服務測驗" → "金融友善服務"
            exam_keywords = exam_name.replace('測驗', '').replace('考試', '').strip()

            # 嘗試多種定位策略（從最精確到最寬鬆）
            strategies = [
                # 策略 1: LINK_TEXT（完全匹配）
                (By.LINK_TEXT, exam_name, "LINK_TEXT (完全匹配)"),
                # 策略 2: PARTIAL_LINK_TEXT（部分匹配）
                (By.PARTIAL_LINK_TEXT, exam_name[:20], "PARTIAL_LINK_TEXT (前20字)"),
                # 策略 3: XPath - activity.title（常見考試連結結構）
                (By.XPATH, f"//a[@ng-bind='activity.title' and contains(text(), '{exam_keywords}')]", "XPath (activity.title + 關鍵詞)"),
                # 策略 4: XPath - 包含考試名稱的任何連結
                (By.XPATH, f"//a[contains(text(), '{exam_keywords}') and (contains(text(), '測驗') or contains(text(), '考試'))]", "XPath (關鍵詞 + 測驗/考試)"),
                # 策略 5: XPath - ng-click 包含 changeActivity
                (By.XPATH, f"//a[@ng-click='changeActivity(activity)' and contains(., '{exam_keywords}')]", "XPath (ng-click + 關鍵詞)"),
                # 策略 6: XPath - 寬鬆匹配（只用關鍵詞）
                (By.XPATH, f"//a[contains(text(), '{exam_keywords}')]", "XPath (只用關鍵詞)"),
            ]

            # 嘗試每種策略
            print(f'  → 嘗試多種定位策略查找考試: {exam_name[:30]}...')
            for strategy_by, strategy_value, strategy_name in strategies:
                try:
                    locator = (strategy_by, strategy_value)
                    element = wait.until(EC.presence_of_element_located(locator))
                    if element:
                        successful_strategy = strategy_name
                        print(f'  ✓ 找到考試連結 (策略: {strategy_name})')
                        break
                except Exception:
                    continue

            if not element:
                raise Exception(f"無法使用任何策略找到考試: {exam_name[:30]}...")

            # 滾動到元素位置
            print(f'  → 滾動到考試連結...')
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            time.sleep(1)

            # 等待元素可點擊
            print(f'  → 等待考試連結可點擊...')
            element = wait.until(EC.element_to_be_clickable(locator))

            # 嘗試點擊（優先使用 JavaScript）
            print(f'  → 嘗試點擊...')
            try:
                self.driver.execute_script("arguments[0].click();", element)
                print(f'  ✓ JavaScript 點擊成功')
            except Exception:
                element.click()
                print(f'  ✓ 普通點擊成功')

            print(f'[SUCCESS] Clicked exam: {exam_name[:30]}... (策略: {successful_strategy})')

        except Exception as e:
            print(f'[ERROR] Failed to click exam "{exam_name}": {e}')
            raise

    def click_exam_by_xpath(self, exam_name: str, delay: float = 10.0):
        """
        使用 XPath 根據考試名稱點擊考試（備用方法）

        Args:
            exam_name: 考試名稱
            delay: 點擊前的延遲時間（秒）
        """
        try:
            # 使用 XPath 定位包含特定文本的考試連結
            locator = (By.XPATH, f"//a[@ng-click='changeActivity(activity)']//span[contains(text(), '{exam_name}')]")

            time.sleep(delay)

            # 捲動到元素位置
            self.scroll_to_element(locator)

            # 點擊考試
            self.click(locator)
            print(f'[SUCCESS] Clicked exam via XPath: {exam_name}')

        except Exception as e:
            print(f'[ERROR] Failed to click exam via XPath "{exam_name}": {e}')
            raise

    def click_continue_exam_button(self, delay: float = 10.0):
        """
        點擊"繼續答題"或"開始答題"按鈕（會彈出確認視窗）

        Args:
            delay: 點擊前的延遲時間（秒）
        """
        try:
            time.sleep(delay)

            # 嘗試多種定位策略
            locators = [
                # 策略1: 根據文本內容定位（最可靠）
                (By.XPATH, "//a[contains(@class, 'take-exam') and (contains(., '繼續答題') or contains(., '開始答題'))]"),
                # 策略2: 根據 ng-click 部分匹配
                (By.XPATH, "//a[contains(@ng-click, 'openStartExamConfirmationPopup')]"),
                # 策略3: 根據 span 文字定位（找到 span 再回溯到父元素）
                (By.XPATH, "//span[contains(text(), '繼續答題') or contains(text(), '開始答題')]/parent::a"),
                # 策略4: 使用 exam-button-container 容器內的按鈕
                (By.XPATH, "//div[contains(@class, 'exam-button-container')]//a[contains(@class, 'take-exam')]"),
            ]

            success = False
            for i, locator in enumerate(locators, 1):
                try:
                    print(f'[INFO] Trying locator strategy {i}...')
                    # 捲動到按鈕位置
                    self.scroll_to_element(locator)
                    # 點擊按鈕
                    self.click(locator)
                    print(f'[SUCCESS] Clicked "繼續答題" button (strategy {i})')
                    success = True
                    break
                except Exception as e:
                    print(f'[DEBUG] Strategy {i} failed: {e}')
                    continue

            if not success:
                raise Exception('All locator strategies failed')

        except Exception as e:
            print(f'[ERROR] Failed to click "繼續答題" button: {e}')
            raise

    def check_agreement_checkbox(self, delay: float = 10.0):
        """
        勾選"我已詳閱考試要求並承諾遵守考試紀律" checkbox

        Args:
            delay: 點擊前的延遲時間（秒）
        """
        try:
            time.sleep(delay)

            # 檢查 checkbox 是否已勾選
            element = self.find_element(self.AGREEMENT_CHECKBOX)
            is_checked = element.is_selected()

            if not is_checked:
                # 使用 JavaScript 點擊（避免被其他元素覆蓋）
                self.driver.execute_script("arguments[0].click();", element)
                print('[SUCCESS] Checked agreement checkbox')
            else:
                print('[INFO] Agreement checkbox already checked')

        except Exception as e:
            print(f'[ERROR] Failed to check agreement checkbox: {e}')
            raise

    def click_popup_continue_button(self, delay: float = 10.0):
        """
        點擊彈窗內的"繼續答題"按鈕（確認進入考試）

        Args:
            delay: 點擊前的延遲時間（秒）
        """
        try:
            time.sleep(delay)

            # 嘗試多種定位和點擊策略
            locators = [
                # 策略1: 精確路徑（用戶提供的 XPath - 最可靠）
                (By.XPATH, "//*[@id='start-exam-confirmation-popup']/div/div/div[3]/div/button[1]"),
                # 策略2: 彈窗 ID + 第一個綠色按鈕
                (By.XPATH, "//div[@id='start-exam-confirmation-popup']//button[contains(@class, 'button-green')][1]"),
                # 策略3: 部分匹配（包含 class 和 ng-click）
                (By.XPATH, "//button[contains(@class, 'button-green') and contains(@ng-click, 'takeExam')]"),
                # 策略4: 只根據文本內容定位
                (By.XPATH, "//button[contains(., '繼續答題') or contains(., '開始答題')]"),
                # 策略5: popup-footer 內的第一個綠色按鈕
                (By.XPATH, "//div[contains(@class, 'popup-footer')]//button[contains(@class, 'button-green')][1]"),
            ]

            success = False
            for i, locator in enumerate(locators, 1):
                try:
                    print(f'[INFO] Trying popup button strategy {i}...')

                    # 找到元素
                    element = self.find_element(locator)

                    # 檢查是否 disabled
                    is_disabled = element.get_attribute('disabled')
                    if is_disabled:
                        print(f'[DEBUG] Button is disabled, waiting for it to be enabled...')
                        # 等待按鈕啟用（最多等 5 秒）
                        for _ in range(10):
                            time.sleep(0.5)
                            is_disabled = element.get_attribute('disabled')
                            if not is_disabled:
                                break

                    # 嘗試使用 JavaScript 點擊（避免被遮擋）
                    self.driver.execute_script("arguments[0].click();", element)
                    print(f'[SUCCESS] Clicked popup "繼續答題" button (strategy {i})')
                    success = True
                    break

                except Exception as e:
                    print(f'[DEBUG] Popup button strategy {i} failed: {e}')
                    continue

            if not success:
                raise Exception('All popup button strategies failed')

        except Exception as e:
            print(f'[ERROR] Failed to click popup "繼續答題" button: {e}')
            raise

    def complete_exam_flow(self, exam_name: str, delay: float = 10.0):
        """
        完成整個考試流程（便捷方法）

        Args:
            exam_name: 考試名稱
            delay: 每個步驟的延遲時間（秒）

        流程：
            1. 點擊考試名稱
            2. 點擊"繼續答題"按鈕（彈出確認視窗）
            3. 勾選同意 checkbox
            4. 點擊彈窗內的"繼續答題"按鈕
        """
        try:
            print(f'\n[EXAM FLOW] Starting exam flow for: {exam_name}')

            # 步驟 1: 點擊考試名稱
            print('[EXAM FLOW] Step 1: Clicking exam name...')
            self.click_exam_by_name(exam_name, delay=delay)

            # 步驟 2: 點擊"繼續答題"按鈕
            print('[EXAM FLOW] Step 2: Clicking continue button...')
            self.click_continue_exam_button(delay=delay)

            # 步驟 3: 勾選同意 checkbox
            print('[EXAM FLOW] Step 3: Checking agreement checkbox...')
            self.check_agreement_checkbox(delay=delay)

            # 步驟 4: 點擊彈窗內的"繼續答題"按鈕
            print('[EXAM FLOW] Step 4: Clicking popup continue button...')
            self.click_popup_continue_button(delay=delay)

            print(f'[EXAM FLOW] ✓ Exam flow completed for: {exam_name}')

        except Exception as e:
            print(f'[EXAM FLOW] ✗ Failed to complete exam flow: {e}')
            raise

    def is_on_exam_page(self) -> bool:
        """
        檢查是否在考試頁面

        Returns:
            bool: 是否在考試頁面
        """
        try:
            # 檢查是否存在考試相關的元素
            exam_title = (By.XPATH, "//span[@ng-bind='exam.title']")
            return self.is_element_present(exam_title)
        except:
            return False

    def wait_for_exam_page_load(self, timeout: int = 10) -> bool:
        """
        等待考試頁面載入完成

        Args:
            timeout: 超時時間（秒）

        Returns:
            bool: 是否載入成功
        """
        try:
            exam_title = (By.XPATH, "//span[@ng-bind='exam.title']")
            return self.is_element_visible(exam_title, timeout=timeout)
        except:
            return False
