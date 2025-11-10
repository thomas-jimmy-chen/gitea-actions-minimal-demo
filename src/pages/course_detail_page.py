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

            # 捲動到元素位置
            self.scroll_to_element(locator)
            print(f'[INFO] Scrolled to lesson: {lesson_name}')

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

            self.scroll_to_element(locator)
            print(f'[INFO] Scrolled to lesson containing: {partial_name}')

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
