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
        根據課程名稱選擇課程（增強版：多重策略 + 重試機制）

        Args:
            course_name: 課程名稱（完整的連結文字）
            delay: 點擊後的延遲時間（秒），等待頁面載入完成
        """
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import (
            TimeoutException,
            ElementClickInterceptedException,
            StaleElementReferenceException
        )

        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                print(f'[嘗試 {attempt + 1}/{max_retries}] 等待課程元素載入: {course_name[:50]}...')

                wait = WebDriverWait(self.driver, 30)
                element = None
                successful_strategy = None

                # 嘗試多種定位策略
                strategies = [
                    # 策略 1: LINK_TEXT（精確匹配）
                    (By.LINK_TEXT, course_name, "LINK_TEXT"),
                    # 策略 2: PARTIAL_LINK_TEXT（部分匹配）
                    (By.PARTIAL_LINK_TEXT, course_name[:30], "PARTIAL_LINK_TEXT"),
                    # 策略 3: XPath（ng-bind 屬性）
                    (By.XPATH, f"//a[@ng-bind='course.display_name' and contains(text(), '{course_name[:20]}')]", "XPath (ng-bind)"),
                    # 策略 4: XPath（通用連結包含文字）
                    (By.XPATH, f"//a[contains(text(), '{course_name[:20]}')]", "XPath (contains)"),
                ]

                # 步驟 1: 嘗試不同策略找到元素
                print(f'  → 嘗試多種定位策略...')
                for strategy_by, strategy_value, strategy_name in strategies:
                    try:
                        locator = (strategy_by, strategy_value)
                        element = wait.until(EC.presence_of_element_located(locator))
                        if element:
                            successful_strategy = strategy_name
                            print(f'  ✓ 元素已找到 (策略: {strategy_name})')
                            break
                    except TimeoutException:
                        continue

                if not element:
                    raise TimeoutException(f"無法使用任何策略找到元素: {course_name[:50]}...")

                # 步驟 2: 滾動到元素位置
                print(f'  → 滾動到元素位置...')
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                time.sleep(1)  # 等待滾動完成

                # 步驟 3: 等待元素可點擊（clickable）
                print(f'  → 等待元素可點擊...')
                element = wait.until(EC.element_to_be_clickable(locator))
                print(f'  ✓ 元素可點擊')

                # 步驟 4: 嘗試點擊（先用 JavaScript，更可靠）
                print(f'  → 嘗試點擊...')
                try:
                    # 先嘗試 JavaScript 點擊（繞過遮擋問題）
                    self.driver.execute_script("arguments[0].click();", element)
                    print(f'  ✓ JavaScript 點擊成功')
                except Exception as js_error:
                    print(f'  ⚠️  JavaScript 點擊失敗: {js_error}')
                    # 如果 JS 點擊失敗，嘗試普通點擊
                    element.click()
                    print(f'  ✓ 普通點擊成功')

                print(f'[SUCCESS] Selected course: {course_name[:50]}...')

                # 等待頁面載入完成
                time.sleep(delay)
                return  # 成功，退出函數

            except (TimeoutException, ElementClickInterceptedException, StaleElementReferenceException) as e:
                print(f'  ✗ 第 {attempt + 1} 次嘗試失敗: {type(e).__name__}')

                if attempt < max_retries - 1:
                    print(f'  → 等待 {retry_delay} 秒後重試...')
                    time.sleep(retry_delay)
                else:
                    # 最後一次嘗試失敗，拋出異常
                    print(f'[ERROR] 已達最大重試次數，無法選擇課程: {course_name[:50]}...')
                    raise

            except Exception as e:
                print(f'[ERROR] 未預期的錯誤: {e}')
                raise

    def select_course_by_partial_name(self, partial_name: str, delay: float = 7.0):
        """
        根據部分課程名稱選擇課程

        Args:
            partial_name: 課程名稱的部分文字
            delay: 點擊後的延遲時間（秒），等待頁面載入完成
        """
        try:
            locator = (By.PARTIAL_LINK_TEXT, partial_name)

            # 點擊課程
            self.click(locator)
            print(f'[SUCCESS] Selected course containing: {partial_name}')

            # 等待頁面載入完成
            time.sleep(delay)

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

    # ==================== 智能推薦功能 (2025-11-16) ====================

    def get_in_progress_programs(self) -> list:
        """
        獲取「修習中」的課程計畫列表

        Returns:
            list: [
                {
                    "name": "課程計畫名稱",
                    "element": WebElement
                },
                ...
            ]
        """
        try:
            print('[掃描] 正在獲取「修習中」的課程計畫...')

            # 策略 1: 直接定位到課程容器，然後找出「修習中」的課程
            # 根據用戶提供的路徑: /html/body/div[2]/div[5]/div/div/div[2]/div/div[1]/div[2]
            courses_container_xpath = "/html/body/div[2]/div[5]/div/div/div[2]/div/div[1]/div[2]"

            try:
                courses_container = self.driver.find_element(By.XPATH, courses_container_xpath)
                print('[DEBUG] 成功找到課程容器')
            except Exception as e:
                print(f'[WARNING] 無法找到指定的課程容器: {e}')
                print('[DEBUG] 嘗試使用更寬鬆的選擇器...')
                courses_container = None

            programs = []

            if courses_container:
                # 根據 HTML 結構：
                # - 「修習中」在 div[1] 裡
                # - 課程在 div[2] 裡（兄弟元素）
                # 策略：找到所有課程連結，然後檢查它們所在的課程卡片（更上層的 div）

                # 找出所有課程連結
                all_course_links = courses_container.find_elements(
                    By.XPATH, ".//a[@ng-bind='course.display_name']"
                )
                print(f'[DEBUG] 容器內有 {len(all_course_links)} 個課程連結')

                for i, course_link in enumerate(all_course_links, 1):
                    try:
                        # 向上找到課程卡片的最外層 div（可能需要往上找多層）
                        # 先嘗試不同層級的父容器
                        found = False

                        for ancestor_level in range(2, 8):  # 嘗試找 2-7 層的父元素
                            try:
                                course_card = course_link.find_element(
                                    By.XPATH, f"./ancestor::div[{ancestor_level}]"
                                )
                                card_text = course_card.text

                                # 檢查這個 div 是否包含「修習中」
                                if '修習中' in card_text:
                                    name = course_link.text.strip()

                                    if name and len(name) > 3:
                                        programs.append({
                                            "name": name,
                                            "element": course_link
                                        })
                                        print(f'[DEBUG] 找到課程 [{i}]: {name[:60]} (層級: {ancestor_level})')
                                        found = True
                                        break
                            except:
                                continue

                        if not found:
                            # 如果所有層級都找不到「修習中」，可能這個課程不是修習中的
                            pass

                    except Exception as e:
                        print(f'[DEBUG] 處理第 {i} 個課程時發生錯誤: {e}')
                        continue

            # 策略 2: 如果策略 1 沒有結果，使用全局搜尋「修習中」
            if not programs:
                print('[DEBUG] 策略 1 無結果，使用策略 2（全局搜尋）...')

                in_progress_spans = self.find_elements(
                    (By.XPATH, "//span[contains(text(), '修習中')]")
                )
                print(f'[DEBUG] 找到 {len(in_progress_spans)} 個「修習中」標籤')

                for span in in_progress_spans:
                    try:
                        # 向上找到最近的課程容器（通常是幾層 div 之上）
                        parent = span.find_element(By.XPATH, "./ancestor::div[3]")

                        # 在父容器中找課程名稱
                        try:
                            program_link = parent.find_element(By.XPATH, ".//a[@ng-click]")
                            name = program_link.text.strip()
                            element = program_link
                        except:
                            # 如果找不到連結，取父容器的第一行文字
                            text_lines = parent.text.split('\n')
                            name = None
                            for line in text_lines:
                                line = line.strip()
                                if line and '修習中' not in line and len(line) > 5:
                                    name = line
                                    break
                            element = parent

                        if name and '修習中' not in name:
                            # 檢查是否已經加入（避免重複）
                            if not any(p['name'] == name for p in programs):
                                programs.append({
                                    "name": name,
                                    "element": element
                                })
                                print(f'[DEBUG] 找到課程: {name[:60]}')

                    except Exception as e:
                        continue

            print(f'[成功] 找到 {len(programs)} 個課程計畫')
            return programs

        except Exception as e:
            print(f'[錯誤] 獲取課程計畫失敗: {e}')
            import traceback
            traceback.print_exc()
            return []

    def get_program_courses_and_exams(self, program_name: str) -> dict:
        """
        獲取課程計畫內的所有課程和考試

        Args:
            program_name: 課程計畫名稱

        Returns:
            dict: {
                "courses": [{"name": "課程名稱", "type": "course"}, ...],
                "exams": [{"name": "考試名稱", "type": "exam"}, ...]
            }
        """
        try:
            print(f'[掃描] 正在分析課程計畫: {program_name[:30]}...')

            # 點擊進入課程計畫（內部已包含延遲等待頁面載入）
            self.select_course_by_name(program_name, delay=5.0)

            # 根據實際 HTML 結構：
            # <a class="title ng-binding ng-scope" ng-bind="activity.title" ...>課程名稱</a>

            # 提取所有活動 (課程 + 考試)
            activity_elements = self.find_elements(
                (By.XPATH, "//a[@ng-bind='activity.title']")
            )

            print(f'[DEBUG] 找到 {len(activity_elements)} 個活動')

            courses = []
            exams = []
            seen_names = set()  # 追蹤已見過的課程/考試名稱，防止重複

            for elem in activity_elements:
                try:
                    name = elem.text.strip()
                    if not name:
                        continue

                    # 去重：如果已經見過這個名稱，跳過
                    if name in seen_names:
                        print(f'[DEBUG] 跳過重複項目: {name[:50]}')
                        continue

                    seen_names.add(name)

                    # 根據名稱判斷是課程還是考試
                    if '測驗' in name or '考試' in name:
                        exams.append({
                            "name": name,
                            "type": "exam"
                        })
                        print(f'[DEBUG] 找到考試: {name[:50]}')
                    else:
                        courses.append({
                            "name": name,
                            "type": "course"
                        })
                        print(f'[DEBUG] 找到課程: {name[:50]}')

                except Exception as e:
                    print(f'[DEBUG] 處理活動時發生錯誤: {e}')
                    continue

            print(f'  ✅ 找到 {len(courses)} 個課程, {len(exams)} 個考試')

            # 注意：不在這裡返回！讓調用者決定何時返回
            # 這樣才能在獲取子課程後，繼續點擊進入子課程獲取章節

            return {
                "courses": courses,
                "exams": exams
            }

        except Exception as e:
            print(f'[錯誤] 獲取課程詳情失敗: {e}')
            import traceback
            traceback.print_exc()
            # 注意：出錯時返回 error 標記，讓調用者知道掃描失敗
            return {
                "courses": [],
                "exams": [],
                "error": True,
                "error_message": str(e)
            }

    def get_course_chapters(self, course_name: str) -> list:
        """
        獲取課程內的章節列表（孫課程）

        Args:
            course_name: 子課程名稱

        Returns:
            list: [{"name": "章節名稱", "type": "chapter"}, ...]
        """
        try:
            print(f'[掃描] 正在進入子課程: {course_name[:40]}...')

            # 點擊進入子課程
            self.select_course_by_name(course_name, delay=3.0)

            # 等待頁面載入
            time.sleep(2)

            # 嘗試多種可能的章節定位方式
            chapters = []
            seen_names = set()

            # 方式 1: 查找課程內容列表（常見於 SCORM 課程）
            # 可能的選擇器：
            # - <a class="title">章節名稱</a>
            # - <div class="chapter-title">章節名稱</div>
            # - <li class="content-item">章節名稱</li>

            # 嘗試多個選擇器
            selectors = [
                (By.XPATH, "//div[@class='content-list']//a[@class='title']"),
                (By.XPATH, "//li[contains(@class,'content-item')]//a"),
                (By.XPATH, "//div[contains(@class,'chapter')]//a"),
                (By.XPATH, "//ul[contains(@class,'list')]//a[@ng-bind]"),
                (By.XPATH, "//div[@class='activity-list']//a[@class='title']"),
            ]

            for selector in selectors:
                try:
                    chapter_elements = self.find_elements(selector)
                    if chapter_elements:
                        print(f'[DEBUG] 使用選擇器找到 {len(chapter_elements)} 個元素: {selector[1]}')
                        for elem in chapter_elements:
                            try:
                                name = elem.text.strip()
                                if name and name not in seen_names and len(name) > 2:
                                    seen_names.add(name)
                                    chapters.append({
                                        "name": name,
                                        "type": "chapter"
                                    })
                                    print(f'[DEBUG] 找到章節: {name[:50]}')
                            except Exception:
                                continue

                        # 如果找到章節就停止嘗試其他選擇器
                        if chapters:
                            break
                except Exception:
                    continue

            print(f'  ✅ 找到 {len(chapters)} 個章節')

            # 返回上一頁
            self.driver.back()
            time.sleep(2)

            return chapters

        except Exception as e:
            print(f'[錯誤] 獲取章節失敗: {e}')
            # 嘗試返回
            try:
                self.driver.back()
                time.sleep(2)
            except Exception:
                pass
            return []
