#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
CourseListPage - 課程列表頁面物件
處理課程列表相關的操作：選擇課程、返回等
"""

import time
from selenium.webdriver.common.by import By
from .base_page import BasePage


class CourseListPage(BasePage):
    """課程列表頁面物件"""

    # 元素定位器
    MY_COURSES_LINK = (By.LINK_TEXT, "我的課程")
    GO_BACK_LINK = (By.XPATH, "//a[@class='go-back-link' and span[text()='返回']]")

    def goto_my_courses(self):
        """前往我的課程列表"""
        try:
            self.click(self.MY_COURSES_LINK)
            time.sleep(2)
            print('[INFO] Navigated to "我的課程"')
        except Exception as e:
            print(f'[ERROR] Failed to navigate to "我的課程": {e}')
            raise

    def select_course_by_name(self, course_name: str, delay: float = 7.0):
        """
        根據課程名稱選擇課程

        Args:
            course_name: 課程名稱（完整的連結文字）
            delay: 點擊前的延遲時間（秒）
        """
        try:
            locator = (By.LINK_TEXT, course_name)

            # 等待一段時間（確保頁面穩定）
            time.sleep(delay)

            # 點擊課程
            self.click(locator)
            print(f'[SUCCESS] Selected course: {course_name}')

        except Exception as e:
            print(f'[ERROR] Failed to select course "{course_name}": {e}')
            raise

    def select_course_by_partial_name(self, partial_name: str, delay: float = 7.0):
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
            print(f'[SUCCESS] Selected course containing: {partial_name}')

        except Exception as e:
            print(f'[ERROR] Failed to select course containing "{partial_name}": {e}')
            raise

    def go_back_to_course_list(self):
        """返回課程列表"""
        try:
            self.click(self.GO_BACK_LINK)
            time.sleep(1)
            print('[SUCCESS] Returned to course list')
        except Exception as e:
            print(f'[ERROR] Failed to return to course list: {e}')
            raise

    def get_all_course_names(self) -> list:
        """
        取得所有課程名稱

        Returns:
            list: 課程名稱列表
        """
        try:
            # 找到所有課程連結（這裡需要根據實際頁面結構調整）
            course_links = self.find_elements((By.XPATH, "//a[contains(@class, 'course-link')]"))
            course_names = [link.text for link in course_links if link.text]
            return course_names
        except Exception as e:
            print(f'[ERROR] Failed to get course names: {e}')
            return []

    def is_on_course_list_page(self) -> bool:
        """
        檢查是否在課程列表頁面

        Returns:
            bool: 是否在課程列表頁面
        """
        return self.is_element_present(self.MY_COURSES_LINK) or \
               self.is_element_present(self.GO_BACK_LINK)
