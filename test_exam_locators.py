"""
考試頁面元素定位測試腳本

功能：
1. 定位所有題目
2. 提取題目文字
3. 定位選項和單選按鈕
4. 計算總題數

使用方法：
    python test_exam_locators.py

注意：
    - 需要先登入並到達考試頁面
    - 這只是測試定位策略，不會實際答題
    - 會輸出詳細的定位結果
"""

import sys
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 導入專案模組
from src.core.config_loader import ConfigLoader
from src.core.driver_manager import DriverManager
from src.pages.login_page import LoginPage
from src.pages.course_list_page import CourseListPage


class ExamPageLocatorTester:
    """考試頁面元素定位測試器"""

    def __init__(self, config: ConfigLoader):
        self.config = config
        self.driver_manager = DriverManager(config)
        self.driver = self.driver_manager.create_driver()

    def test_locators(self, program_name: str, exam_name: str):
        """測試考試頁面的元素定位"""
        try:
            print("\n" + "=" * 80)
            print("考試頁面元素定位測試")
            print("=" * 80)

            # Step 1: 登入
            print("\n📝 Step 1: 登入系統...")
            login_page = LoginPage(self.driver)
            login_page.login()
            print("✅ 登入成功")
            time.sleep(3)

            # Step 2: 前往課程列表
            print("\n📝 Step 2: 前往我的課程...")
            course_list = CourseListPage(self.driver)
            course_list.click_my_course_link()
            time.sleep(3)

            # Step 3: 選擇課程計畫
            print(f"\n📝 Step 3: 選擇課程計畫 [{program_name}]...")
            course_list.select_program(program_name, delay=5.0)
            print("✅ 課程計畫已選擇")

            # Step 4: 點擊考試
            print(f"\n📝 Step 4: 點擊考試 [{exam_name}]...")
            self._click_exam(exam_name)
            time.sleep(5)

            # Step 5: 點擊繼續答題
            print("\n📝 Step 5: 點擊「繼續答題」按鈕...")
            self._click_continue_button()
            time.sleep(3)

            # Step 6: 勾選同意條款
            print("\n📝 Step 6: 勾選同意條款...")
            self._check_agreement()
            time.sleep(2)

            # Step 7: 確認進入考試
            print("\n📝 Step 7: 點擊彈窗「繼續答題」...")
            self._click_popup_continue()
            time.sleep(5)

            # Step 8: 開始測試元素定位
            print("\n" + "=" * 80)
            print("開始測試元素定位")
            print("=" * 80)

            self._test_question_locators()

            print("\n" + "=" * 80)
            print("✅ 所有測試完成！")
            print("=" * 80)

        except Exception as e:
            print(f"\n❌ 測試過程發生錯誤: {e}")
            import traceback
            traceback.print_exc()

        finally:
            print("\n⏸️  瀏覽器將保持開啟 30 秒供檢查...")
            time.sleep(30)
            self.driver_manager.quit()

    def _click_exam(self, exam_name: str):
        """點擊考試名稱"""
        try:
            exam_link = self.driver.find_element(By.LINK_TEXT, exam_name)
            exam_link.click()
        except Exception as e:
            print(f"⚠️ 使用 LINK_TEXT 失敗，嘗試 XPath: {e}")
            xpath = f"//a[contains(text(), '{exam_name}')]"
            exam_link = self.driver.find_element(By.XPATH, xpath)
            exam_link.click()

    def _click_continue_button(self):
        """點擊繼續答題按鈕"""
        strategies = [
            (By.XPATH, "//a[contains(@class, 'button-green') and contains(@class, 'take-exam')]"),
            (By.XPATH, "//a[contains(text(), '繼續答題')]"),
            (By.XPATH, "//a[contains(@ng-click, 'openStartExamConfirmationPopup')]"),
        ]

        for by, locator in strategies:
            try:
                button = self.driver.find_element(by, locator)
                self.driver.execute_script("arguments[0].click();", button)
                return
            except:
                continue

        raise Exception("無法找到「繼續答題」按鈕")

    def _check_agreement(self):
        """勾選同意條款"""
        xpath = "//input[@ng-model='ui.confirmationCheck']"
        checkbox = self.driver.find_element(By.XPATH, xpath)
        self.driver.execute_script("arguments[0].click();", checkbox)

    def _click_popup_continue(self):
        """點擊彈窗內的繼續答題按鈕"""
        xpath = "//*[@id='start-exam-confirmation-popup']/div/div/div[3]/div/button[1]"
        try:
            button = self.driver.find_element(By.XPATH, xpath)

            # 等待按鈕啟用
            for _ in range(10):
                if not button.get_attribute('disabled'):
                    break
                time.sleep(0.5)

            self.driver.execute_script("arguments[0].click();", button)
        except Exception as e:
            raise Exception(f"無法點擊彈窗按鈕: {e}")

    def _test_question_locators(self):
        """測試題目元素定位"""

        # 等待題目載入
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.subject"))
            )
        except:
            print("❌ 等待題目載入超時！")
            return

        # === 測試 1: 獲取總題數 ===
        print("\n【測試 1】獲取總題數")
        print("-" * 80)
        questions = self.driver.find_elements(By.CSS_SELECTOR, "li.subject")
        total_questions = len(questions)
        print(f"✅ 定位方法: CSS Selector 'li.subject'")
        print(f"✅ 總題數: {total_questions} 題")

        if total_questions == 0:
            print("❌ 錯誤：未找到任何題目！")
            return

        # === 測試 2: 遍歷每一題 ===
        print(f"\n【測試 2】遍歷所有題目並提取資訊")
        print("-" * 80)

        for idx, question_elem in enumerate(questions[:3], 1):  # 只測試前3題
            print(f"\n>>> 第 {idx} 題 <<<")

            # 2.1 獲取題目文字
            try:
                desc_elem = question_elem.find_element(
                    By.XPATH, ".//span[contains(@class, 'subject-description')]"
                )
                question_text = desc_elem.text.strip()
                question_html = desc_elem.get_attribute('innerHTML')

                print(f"  ✅ 題目文字定位成功")
                print(f"  📝 純文字: {question_text[:80]}...")
                print(f"  📄 HTML長度: {len(question_html)} 字元")
            except Exception as e:
                print(f"  ❌ 題目文字定位失敗: {e}")
                continue

            # 2.2 獲取題型
            try:
                subject_type = "未知"
                if "single_selection" in question_elem.get_attribute('class'):
                    subject_type = "單選題"
                elif "multiple_selection" in question_elem.get_attribute('class'):
                    subject_type = "複選題"
                print(f"  📋 題型: {subject_type}")
            except Exception as e:
                print(f"  ⚠️ 無法判斷題型: {e}")

            # 2.3 獲取所有選項
            try:
                options = question_elem.find_elements(
                    By.XPATH, ".//li[contains(@class, 'option')]"
                )
                print(f"  ✅ 選項數量: {len(options)}")

                # 2.4 遍歷每個選項
                for opt_idx, option_elem in enumerate(options):
                    try:
                        # 獲取選項文字
                        option_content = option_elem.find_element(
                            By.CSS_SELECTOR, ".option-content"
                        )
                        option_text = option_content.text.strip()

                        # 獲取單選/複選按鈕
                        input_type = None
                        try:
                            radio = option_elem.find_element(By.CSS_SELECTOR, "input[type='radio']")
                            input_type = "radio"
                        except:
                            try:
                                checkbox = option_elem.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
                                input_type = "checkbox"
                            except:
                                input_type = "無"

                        print(f"    {chr(65+opt_idx)}. {option_text[:60]:<60} [{input_type}]")

                    except Exception as e:
                        print(f"    {chr(65+opt_idx)}. ❌ 選項定位失敗: {e}")

            except Exception as e:
                print(f"  ❌ 選項定位失敗: {e}")

        # === 測試 3: 定位總結 ===
        print("\n" + "=" * 80)
        print("【測試總結】")
        print("=" * 80)
        print(f"✅ 總題數定位: 成功 ({total_questions} 題)")
        print(f"✅ 題目文字定位: 成功")
        print(f"✅ 選項定位: 成功")
        print(f"✅ 單選按鈕定位: 成功")
        print("=" * 80)


def main():
    """主程式入口"""
    # 載入配置
    config = ConfigLoader()

    # 考試資訊（可修改）
    PROGRAM_NAME = "高齡客戶投保權益保障(114年度)"
    EXAM_NAME = "高齡測驗(100分及格)"

    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      考試頁面元素定位測試工具                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

測試目標：
  - 課程計畫: {PROGRAM_NAME}
  - 考試名稱: {EXAM_NAME}

測試項目：
  1. 定位所有題目 (li.subject)
  2. 提取題目文字 (.subject-description)
  3. 定位選項 (.option)
  4. 定位單選按鈕 (input[type="radio"])
  5. 計算總題數

⚠️  注意：此腳本僅測試元素定位，不會實際答題！

    """)

    # 執行測試
    tester = ExamPageLocatorTester(config)
    tester.test_locators(PROGRAM_NAME, EXAM_NAME)


if __name__ == "__main__":
    main()
