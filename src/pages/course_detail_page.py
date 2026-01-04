#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
CourseDetailPage - 課程詳情頁面物件
處理課程詳情頁的操作：選擇特定課程、返回課程計畫等
"""

import time
from selenium.webdriver.common.by import By
from .base_page import BasePage


class CourseDetailPage(BasePage):
    """課程詳情頁面物件"""

    # 頁面載入指標（空白頁檢測用）
    PAGE_LOAD_INDICATOR = [
        ".clickable-area",                   # 課程學習區
        ".activity-content-box",             # 活動內容區
        "[ng-bind='activity.title']",        # 活動標題
    ]

    # 動態元素定位器模板
    BACK_TO_COURSE_XPATH_TEMPLATE = "//a[@ng-click='goBackCourse({course_id})']"
    CLICKABLE_AREA = (By.XPATH, "//div[@class='clickable-area']")

    def select_lesson_by_name(self, lesson_name: str, delay: float = 7.0):
        """
        選擇特定課程

        Args:
            lesson_name: 課程名稱（完整的連結文字）
            delay: 點擊前的延遲時間（秒）
        """
        try:
            locator = (By.LINK_TEXT, lesson_name)

            # 等待一段時間
            time.sleep(delay)

            # 點擊課程
            self.click(locator)
            print(f'[SUCCESS] Selected lesson: {lesson_name}')

        except Exception as e:
            print(f'[ERROR] Failed to select lesson "{lesson_name}": {e}')
            raise

    def select_lesson_by_partial_name(self, partial_name: str, delay: float = 7.0):
        """
        根據部分課程名稱選擇課程

        Args:
            partial_name: 課程名稱的部分文字
            delay: 點擊前的延遲時間（秒）
        """
        try:
            locator = (By.PARTIAL_LINK_TEXT, partial_name)

            time.sleep(delay)

            self.click(locator)
            print(f'[SUCCESS] Selected lesson containing: {partial_name}')

        except Exception as e:
            print(f'[ERROR] Failed to select lesson containing "{partial_name}": {e}')
            raise

    def click_clickable_area(self):
        """點擊課程學習頁的 clickable-area"""
        try:
            self.click(self.CLICKABLE_AREA)
            print('[SUCCESS] Clicked clickable-area')
        except Exception as e:
            print(f'[ERROR] Failed to click clickable-area: {e}')
            raise

    def go_back_to_course(self, course_id: int):
        """
        返回課程計畫頁面（使用 ng-click）

        Args:
            course_id: 課程 ID
        """
        try:
            xpath = self.BACK_TO_COURSE_XPATH_TEMPLATE.format(course_id=course_id)
            locator = (By.XPATH, xpath)

            self.click(locator)
            time.sleep(1)
            print(f'[SUCCESS] Returned to course {course_id}')

        except Exception as e:
            print(f'[ERROR] Failed to return to course {course_id}: {e}')
            raise

    def extract_pass_requirement(self, module_id: str) -> dict:
        """
        提取指定 module 的通過條件

        Args:
            module_id: Module ID (例如: "1491")

        Returns:
            dict: {
                'text': str,  # 原始文字 (例如: "通過條件為累積觀看時長100分鐘以上且教材狀態為已完成")
                'required_minutes': int or None,  # 提取的分鐘數
                'required_score': int or None  # 提取的測驗成績
            }
        """
        import re

        result = {
            'text': None,
            'required_minutes': None,
            'required_score': None
        }

        try:
            # XPath: //*[@id="module-{module_id}"]/div[1]/div[1]/span
            xpath = f'//*[@id="module-{module_id}"]/div[1]/div[1]/span'
            element = self.driver.find_element(By.XPATH, xpath)
            text = element.text.strip()

            if text:
                result['text'] = text

                # 提取觀看時長 (例如: "觀看時長100分鐘")
                duration_match = re.search(r'觀看時長(\d+)分鐘', text)
                if duration_match:
                    result['required_minutes'] = int(duration_match.group(1))

                # 提取測驗成績 (例如: "測驗成績達60分")
                score_match = re.search(r'測驗成績達(\d+)分', text)
                if score_match:
                    result['required_score'] = int(score_match.group(1))

                print(f'[INFO] 提取通過條件: {text}')
                if result['required_minutes']:
                    print(f'       → 需要時長: {result["required_minutes"]} 分鐘')
                if result['required_score']:
                    print(f'       → 需要成績: {result["required_score"]} 分')

        except Exception as e:
            print(f'[WARNING] 無法提取 module {module_id} 的通過條件: {e}')

        return result

    def get_first_module_id(self) -> str:
        """
        獲取頁面中第一個 module 的 ID

        Returns:
            str: Module ID (例如: "1491")，失敗則返回 None
        """
        try:
            # 查找第一個 module 元素
            module_elem = self.driver.find_element(By.XPATH, '//div[starts-with(@id, "module-")]')
            module_id = module_elem.get_attribute('id').replace('module-', '')
            print(f'[INFO] 找到第一個 module ID: {module_id}')
            return module_id
        except Exception as e:
            print(f'[WARNING] 無法找到 module ID: {e}')
            return None

    def extract_current_read_time(self) -> dict:
        """
        從頁面提取已閱讀時數（多策略版本）

        Returns:
            dict: {
                'text': str,          # 原始文字 (例如: "已閱讀時數 6729 分鐘")
                'minutes': int or None,    # 提取的分鐘數
                'hours': float or None     # 換算成小時
            }
        """
        import re
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        result = {
            'text': None,
            'minutes': None,
            'hours': None
        }

        # 多種定位策略（從最具體到最寬鬆）
        strategies = [
            # 策略 1: 原始 XPath
            ("原始 XPath", '/html/body/div[2]/div[5]/div/div/div[2]/div[2]/div[2]/div[4]/div/div[2]/div'),
            # 策略 2: 包含「已閱讀時數」的元素
            ("包含已閱讀時數", "//*[contains(text(), '已閱讀時數')]"),
            # 策略 3: 包含「分鐘」的元素
            ("包含分鐘", "//*[contains(text(), '分鐘') and contains(text(), '閱讀')]"),
            # 策略 4: 課程資訊區域中的時數
            ("課程資訊區域", "//div[contains(@class, 'course-info')]//div[contains(text(), '分鐘')]"),
            # 策略 5: 任何包含「XX 分鐘」格式的元素
            ("任意分鐘格式", "//div[contains(text(), ' 分鐘')]"),
            # 策略 6: 更寬鬆的搜索
            ("寬鬆搜索", "//span[contains(text(), '分鐘')] | //div[contains(text(), '分鐘')]"),
        ]

        for strategy_name, xpath in strategies:
            try:
                # 使用短暫等待
                wait = WebDriverWait(self.driver, 3)
                element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                text = element.text.strip()

                if text:
                    result['text'] = text

                    # 提取分鐘數 (例如: "已閱讀時數 6729 分鐘")
                    minutes_match = re.search(r'(\d+)\s*分鐘', text)
                    if minutes_match:
                        minutes = int(minutes_match.group(1))
                        result['minutes'] = minutes
                        result['hours'] = round(minutes / 60, 2)
                        print(f'[INFO] 已閱讀時數: {minutes} 分鐘 ({result["hours"]} 小時) (策略: {strategy_name})')
                        return result
                    else:
                        print(f'[INFO] 找到元素但無法提取分鐘數: {text[:50]}... (策略: {strategy_name})')

            except Exception:
                continue  # 嘗試下一個策略

        # 所有策略都失敗
        print(f'[WARNING] 無法提取已閱讀時數（所有策略都失敗）')

        return result

    def go_back_with_text(self, link_text: str = "返回課程"):
        """
        使用連結文字返回（通用方法）

        Args:
            link_text: 返回連結的文字
        """
        try:
            locator = (By.XPATH, f"//a[span[text()='{link_text}']]")
            self.click(locator)
            time.sleep(1)
            print(f'[SUCCESS] Clicked back link: {link_text}')
        except Exception as e:
            print(f'[ERROR] Failed to click back link "{link_text}": {e}')
            raise

    def get_all_lesson_names(self) -> list:
        """
        取得所有課程名稱

        Returns:
            list: 課程名稱列表
        """
        try:
            # 找到所有課程連結（根據實際頁面結構調整）
            lesson_links = self.find_elements((By.XPATH, "//a[contains(@href, 'lesson') or contains(@href, 'course')]"))
            lesson_names = [link.text for link in lesson_links if link.text]
            return lesson_names
        except Exception as e:
            print(f'[ERROR] Failed to get lesson names: {e}')
            return []

    def wait_for_lesson_page_load(self, timeout: int = 10) -> bool:
        """
        等待課程頁面載入完成

        Args:
            timeout: 超時時間

        Returns:
            bool: 是否載入成功
        """
        try:
            # 等待 clickable-area 出現（表示課程頁面已載入）
            self.is_element_visible(self.CLICKABLE_AREA, timeout=timeout)
            return True
        except:
            return False
