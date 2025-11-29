#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
Eebot 互動式選單 - 課程排程管理
允許使用者選擇課程並加入排程

Author: wizard03
Date: 2025/11/10
Version: 2.0.1
"""

import json
import os
import sys

# 設定 Windows 命令行編碼
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class CourseScheduler:
    """課程排程管理器"""

    def __init__(self):
        self.courses_file = 'data/courses.json'
        self.schedule_file = 'data/schedule.json'
        self.all_courses = []
        self.scheduled_courses = []

    def load_courses(self):
        """載入所有可用課程"""
        try:
            with open(self.courses_file, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
                self.all_courses = data.get('courses', [])
            print(f'✓ 已載入 {len(self.all_courses)} 個課程')
            return True
        except FileNotFoundError:
            print(f'✗ 找不到課程資料檔: {self.courses_file}')
            return False
        except json.JSONDecodeError as e:
            print(f'✗ 課程資料格式錯誤: {e}')
            return False

    def load_schedule(self):
        """載入已排程的課程"""
        if not os.path.exists(self.schedule_file):
            self.scheduled_courses = []
            return

        try:
            with open(self.schedule_file, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
                self.scheduled_courses = data.get('courses', [])
        except:
            self.scheduled_courses = []

    def save_schedule(self):
        """儲存排程到檔案"""
        schedule_data = {
            'description': '已排程的課程列表',
            'version': '1.0',
            'courses': self.scheduled_courses
        }

        try:
            with open(self.schedule_file, 'w', encoding='utf-8') as f:
                json.dump(schedule_data, f, ensure_ascii=False, indent=2)
            print(f'\n✓ 排程已儲存至 {self.schedule_file}')
            print(f'✓ 共 {len(self.scheduled_courses)} 個課程已加入排程')
            return True
        except Exception as e:
            print(f'\n✗ 儲存排程失敗: {e}')
            return False

    def display_menu(self):
        """顯示主選單"""
        print('\n' + '=' * 70)
        print('  Eebot 課程排程管理系統')
        print('=' * 70)
        print('\n可用課程列表：\n')

        for i, course in enumerate(self.all_courses, 1):
            # 判斷是考試還是課程
            course_type = course.get('course_type', 'course')

            print(f'  [{i}] {course["program_name"]}')

            if course_type == 'exam':
                # 考試類型
                auto_answer = '自動答題' if course.get('enable_auto_answer', False) else '手動作答'
                print(f'      └─ {course["exam_name"]} [考試 - {auto_answer}]')
            else:
                # 課程類型
                screenshot = '啟用截圖' if course.get('enable_screenshot', False) else '停用截圖'
                print(f'      └─ {course["lesson_name"]} [{screenshot}]')
                print(f'         (課程ID: {course["course_id"]})')
            print()

        print('-' * 70)
        print('操作說明：')
        print('  • 輸入數字 (1-{}) 選擇課程加入排程'.format(len(self.all_courses)))
        print('  • 輸入 v - 查看目前排程')
        print('  • 輸入 c - 清除排程')
        print('  • 輸入 i - 一鍵自動執行 (掃描所有修習中課程並自動執行) ⭐')
        print('  • 輸入 s - 儲存排程')
        print('  • 輸入 r - 執行排程')
        print('  • 輸入 q - 離開')
        print('=' * 70)

    def display_schedule(self):
        """顯示當前排程"""
        print('\n' + '=' * 70)
        print('  目前排程')
        print('=' * 70)

        if not self.scheduled_courses:
            print('  (排程為空)')
        else:
            for i, course in enumerate(self.scheduled_courses, 1):
                course_type = course.get('course_type', 'course')

                print(f'  [{i}] {course["program_name"]}')

                if course_type == 'exam':
                    # 考試類型
                    print(f'      └─ {course["exam_name"]} [考試]')
                else:
                    # 課程類型
                    print(f'      └─ {course["lesson_name"]}')
                print()

        print(f'總計: {len(self.scheduled_courses)} 個課程')
        print('=' * 70)

    def add_course_to_schedule(self, course_index):
        """將課程加入排程"""
        if 1 <= course_index <= len(self.all_courses):
            course = self.all_courses[course_index - 1]
            self.scheduled_courses.append(course)

            # 根據類型顯示不同訊息
            course_type = course.get('course_type', 'course')
            if course_type == 'exam':
                print(f'\n✓ 已加入排程: {course["program_name"]} - {course["exam_name"]} [考試]')
            else:
                print(f'\n✓ 已加入排程: {course["program_name"]} - {course["lesson_name"]}')
            return True
        else:
            print(f'\n✗ 無效的課程編號: {course_index}')
            return False

    def clear_schedule(self):
        """清除所有排程"""
        self.scheduled_courses = []
        print('\n✓ 排程已清除')

    def handle_intelligent_recommendation(self):
        """智能推薦 - 一鍵自動執行所有修習中課程"""

        # ===== 顯示警告提示 =====
        print('\n' + '=' * 70)
        print('  ⚠️  智能推薦 - 一鍵自動執行')
        print('=' * 70)
        print()
        print('本選項會自動登入(有驗證碼時，必須人工輸入)，')
        print('一直到所有課程完成。')
        print()
        print('執行流程：')
        print('  1. 自動清除 cookies 與排程')
        print('  2. 自動掃描所有「修習中」課程')
        print('  3. 自動加入排程並執行')
        print('  4. 執行完成後自動清除 cookies 與排程')
        print('=' * 70)

        confirm = input('\n確定要執行嗎？(y/n): ').strip().lower()
        if confirm != 'y':
            print('\n✓ 已取消')
            input('\n按 Enter 返回主選單...')
            return

        # ===== 步驟 1: 執行前清理 =====
        print('\n[步驟 1/5] 執行前清理...')

        # 清除內部排程
        self.scheduled_courses = []
        print('  ✓ 已清除內部排程')

        # 清除排程檔案
        if os.path.exists(self.schedule_file):
            try:
                os.remove(self.schedule_file)
                print(f'  ✓ 已刪除排程檔案')
            except OSError as e:
                print(f'  ✗ 刪除排程檔案失敗: {e}')

        # 清除 cookies 和相關檔案
        temp_files = [
            'cookies.json',
            'resource/cookies/cookies.json',
            'stealth.min.js',
            'resource/plugins/stealth.min.js'
        ]

        for file_path in temp_files:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    # 將技術性檔名轉為使用者友善的顯示名稱
                    display_name = file_path.replace('stealth.min.js', 'stealth mode file')
                    print(f'  ✓ 已刪除: {display_name}')
                except OSError as e:
                    display_name = file_path.replace('stealth.min.js', 'stealth mode file')
                    print(f'  ✗ 刪除失敗 {display_name}: {e}')

        print('  ✓ 執行前清理完成\n')

        # ===== 步驟 2-4: 掃描課程 =====
        driver_manager = None

        try:
            from src.core.config_loader import ConfigLoader
            from src.core.driver_manager import DriverManager
            from src.core.cookie_manager import CookieManager
            from src.pages.login_page import LoginPage
            from src.pages.course_list_page import CourseListPage
            from src.utils.stealth_extractor import StealthExtractor

            print('[步驟 2/5] 正在啟動瀏覽器...')
            print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')

            # 1. 載入配置
            print('[初始化 1/5] 載入配置...')
            config = ConfigLoader('config/eebot.cfg')
            config.load()
            print('  ✓ 配置已載入')

            # 2. 啟動瀏覽器自動化模式（提取 Stealth JS）
            print('[初始化 2/5] 啟動瀏覽器自動化模式...')
            extractor = StealthExtractor()
            if not extractor.exists():
                extractor.run()
            else:
                print('  ✓ 瀏覽器自動化模式就緒，跳過初始化')

            # 3. 初始化核心元件（不使用 proxy）
            print('[初始化 3/5] 初始化核心元件...')
            driver_manager = DriverManager(config)
            cookie_manager = CookieManager(config.get('cookies_file'))
            print('  ✓ 核心元件已初始化')

            # 4. 建立 Driver（停用 proxy）
            print('[初始化 4/5] 啟動瀏覽器...')
            driver = driver_manager.create_driver(use_proxy=False)
            print('  ✓ 瀏覽器已啟動')

            # 5. 初始化頁面物件
            print('[初始化 5/5] 初始化頁面物件...')
            login_page = LoginPage(driver, cookie_manager)
            course_list_page = CourseListPage(driver)
            print('  ✓ 頁面物件已初始化\n')

            # ===== 參考 CourseLearningScenario.execute() 的登入流程 =====

            print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
            print('【智能推薦】開始執行')
            print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')

            # Step 1: 自動登入（完全參考 CourseLearningScenario）
            print('[Step 1] 正在登入...')

            # 嘗試登入，最多重試 3 次
            max_retries = 3
            login_success = False

            for attempt in range(max_retries):
                login_success = login_page.auto_login(
                    username=config.get('user_name'),
                    password=config.get('password'),
                    url=config.get('target_http')
                )

                if login_success:
                    print('  ✓ 登入成功\n')
                    break
                else:
                    if attempt < max_retries - 1:
                        print(f'  ⚠️  登入失敗，重試中... ({attempt + 1}/{max_retries})\n')
                        # 刷新頁面以獲取新的驗證碼
                        login_page.goto(config.get('target_http'))
                    else:
                        print('  ✗ 登入失敗，已達最大重試次數\n')

            # 如果登入失敗，終止流程
            if not login_success:
                print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
                print('【智能推薦】登入失敗，流程終止')
                print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')
                input('\n按 Enter 返回主選單...')
                return

            # Step 2: 前往我的課程
            print('[Step 2] 前往我的課程...')
            course_list_page.goto_my_courses()
            print('  ✓ 已進入我的課程\n')

            # ===== 接上掃描步驟 =====

            # Step 3: 等待頁面載入完成（課程數據需要時間渲染）
            print('[Step 3] 等待頁面載入...')
            import time
            time.sleep(10)
            print('  ✓ 頁面已載入\n')

            # Step 4: 掃描課程計畫
            print('[Step 4] 掃描「修習中」的課程計畫...')
            programs = course_list_page.get_in_progress_programs()

            if not programs:
                print('  ⚠️  未找到任何「修習中」的課程計畫')
                input('\n按 Enter 返回主選單...')
                return

            print(f'  ✓ 找到 {len(programs)} 個課程計畫\n')

            # Step 4: 分析課程詳情
            print('[Step 4] 正在分析課程詳情...\n')
            available_courses = []
            for i, program in enumerate(programs, 1):
                program_name = program['name']
                print(f'  [{i}/{len(programs)}] {program_name[:50]}...')

                details = course_list_page.get_program_courses_and_exams(program_name)
                available_courses.append({
                    "program_name": program_name,
                    "courses": details.get('courses', []),
                    "exams": details.get('exams', [])
                })

            print('\n  ✓ 分析完成！\n')

            # Step 6: 比對配置
            print('[Step 6] 比對已配置的課程...')

            # 載入 courses.json
            try:
                import json
                from difflib import SequenceMatcher

                with open('data/courses.json', 'r', encoding='utf-8-sig') as f:
                    config_data = json.load(f)
                    config_courses = config_data.get('courses', [])
            except Exception as e:
                print(f'  ✗ 載入配置失敗: {e}')
                input('\n按 Enter 返回主選單...')
                return

            # 簡化的匹配邏輯（直接在這裡實作，不使用 CourseRecommender）
            def normalize_text(text):
                """正規化文字"""
                if not text:
                    return ""
                return ''.join(text.split()).lower()

            def match_course(web_name, courses_list):
                """匹配課程"""
                web_norm = normalize_text(web_name)
                for course in courses_list:
                    config_name = course.get('lesson_name') or course.get('exam_name')
                    if not config_name:
                        continue
                    config_norm = normalize_text(config_name)
                    # 精確匹配
                    if web_norm == config_norm:
                        return course
                    # 包含匹配
                    if web_norm in config_norm or config_norm in web_norm:
                        return course
                    # 模糊匹配 (90%)
                    similarity = SequenceMatcher(None, web_norm, config_norm).ratio()
                    if similarity >= 0.90:
                        return course
                return None

            recommendations = []
            for program in available_courses:
                program_name = program['program_name']
                # 比對一般課程
                for course in program.get('courses', []):
                    matched_config = match_course(course['name'], config_courses)
                    if matched_config:
                        recommendations.append({
                            "program_name": program_name,
                            "item_name": course['name'],
                            "type": "course",
                            "matched": True,
                            "config": matched_config
                        })
                # 比對考試
                for exam in program.get('exams', []):
                    matched_config = match_course(exam['name'], config_courses)
                    if matched_config:
                        recommendations.append({
                            "program_name": program_name,
                            "item_name": exam['name'],
                            "type": "exam",
                            "matched": True,
                            "auto_answer": matched_config.get('enable_auto_answer', False),
                            "config": matched_config
                        })

            if not recommendations:
                print('  ⚠️  未找到可推薦的課程')
                print('\n提示: 請先在 courses.json 中配置您想要上的課程')
                input('\n按 Enter 返回主選單...')
                return

            print(f'  ✓ 找到 {len(recommendations)} 個已配置的課程\n')

            # Step 7: 顯示推薦結果
            print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
            print('【課程推薦】本服務推薦可以上的課程如下：')
            print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')

            for i, item in enumerate(recommendations, 1):
                item_type = "考試" if item['type'] == "exam" else "課程"
                print(f"{i}. [{item_type}] {item['item_name']}")
                print(f"   📚 所屬計畫: {item['program_name']}")
                print(f"   ✅ 已配置")

                item_config = item.get('config', {})

                # 顯示課程特性
                if item['type'] == 'exam':
                    if item.get('auto_answer'):
                        print(f"   🤖 自動答題: 啟用")
                    else:
                        print(f"   📝 手動作答")
                else:
                    # 一般課程 - 顯示截圖狀態
                    if item_config.get('enable_screenshot', False):
                        print(f"   📸 截圖: 啟用")
                    else:
                        print(f"   📸 截圖: 停用")

                print()

            print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
            print(f'總計: {len(recommendations)} 個課程可以立即執行')
            print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')

            # Step 8: 自動全部加入排程（不再詢問）
            print('[步驟 3/5] 正在加入排程...\n')

            added_count = 0
            skipped_count = 0

            for item in recommendations:
                config = item['config']

                # 檢查是否已經存在於排程中（去重）
                is_duplicate = False
                for existing in self.scheduled_courses:
                    # 判斷重複的邏輯
                    if config.get('course_type') == 'exam':
                        # 考試：比對 program_name + exam_name
                        if (existing.get('program_name') == config.get('program_name') and
                            existing.get('exam_name') == config.get('exam_name') and
                            existing.get('course_type') == 'exam'):
                            is_duplicate = True
                            break
                    else:
                        # 一般課程：比對 program_name + lesson_name + course_id
                        if (existing.get('program_name') == config.get('program_name') and
                            existing.get('lesson_name') == config.get('lesson_name') and
                            existing.get('course_id') == config.get('course_id')):
                            is_duplicate = True
                            break

                if is_duplicate:
                    skipped_count += 1
                    print(f'  ⚠️  跳過重複項目: {item["item_name"][:40]}...')
                else:
                    self.scheduled_courses.append(config)
                    added_count += 1

            print(f'\n✓ 已將 {added_count} 個推薦課程加入排程')
            if skipped_count > 0:
                print(f'  ⚠️  跳過 {skipped_count} 個重複項目\n')
            else:
                print()

        except ImportError as e:
            print(f'\n✗ 無法載入推薦服務: {e}')
            print('  請確保已正確安裝所有依賴')
            input('\n按 Enter 返回主選單...')
            return
        except Exception as e:
            print(f'\n✗ 智能推薦執行失敗: {e}')
            import traceback
            traceback.print_exc()
            input('\n按 Enter 返回主選單...')
            return
        finally:
            # 關閉瀏覽器（參考 CourseLearningScenario 的清理流程）
            if driver_manager:
                print('\n[步驟 4/5] 關閉瀏覽器...')
                driver_manager.quit()
                print('  ✓ 瀏覽器已關閉')

        # ===== 步驟 5: 自動執行排程 =====
        if not self.scheduled_courses:
            print('\n⚠️  未找到可執行的課程')
            input('\n按 Enter 返回主選單...')
            return

        print('\n[步驟 5/5] 正在執行排程...')
        print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')

        # 儲存排程
        self.save_schedule()

        # 執行 main.py
        print('\n啟動 main.py...\n')
        print('=' * 70)
        os.system('python main.py')
        print('=' * 70)

        # ===== 執行後清理 =====
        print('\n[執行完成] 正在清理...')

        # 清除內部排程
        self.scheduled_courses = []
        print('  ✓ 已清除內部排程')

        # 清除排程檔案
        if os.path.exists(self.schedule_file):
            try:
                os.remove(self.schedule_file)
                print(f'  ✓ 已刪除排程檔案')
            except OSError as e:
                print(f'  ✗ 刪除排程檔案失敗: {e}')

        # 清除 cookies 和相關檔案
        temp_files = [
            'cookies.json',
            'resource/cookies/cookies.json',
            'stealth.min.js',
            'resource/plugins/stealth.min.js'
        ]

        for file_path in temp_files:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    # 將技術性檔名轉為使用者友善的顯示名稱
                    display_name = file_path.replace('stealth.min.js', 'stealth mode file')
                    print(f'  ✓ 已刪除: {display_name}')
                except OSError as e:
                    display_name = file_path.replace('stealth.min.js', 'stealth mode file')
                    print(f'  ✗ 刪除失敗 {display_name}: {e}')

        print('\n✓ 所有任務已完成！')
        input('\n按 Enter 返回主選單...')

    def run_schedule(self):
        """執行排程（啟動 main.py）"""
        if not self.scheduled_courses:
            print('\n✗ 排程為空，無法執行！')
            print('  請先選擇課程並儲存排程。')
            return

        print('\n' + '=' * 70)
        print('  準備執行排程')
        print('=' * 70)
        self.display_schedule()

        confirm = input('\n確定要執行排程嗎？(y/n): ').strip().lower()
        if confirm == 'y':
            print('\n啟動 main.py...\n')
            os.system('python main.py')
        else:
            print('\n✗ 已取消執行')

    def run(self):
        """執行互動式選單"""
        # 載入課程資料
        if not self.load_courses():
            return

        # 載入已存在的排程
        self.load_schedule()

        print('\n歡迎使用 Eebot 課程排程管理系統！')

        while True:
            self.display_menu()

            # 顯示當前排程摘要
            if self.scheduled_courses:
                print(f'\n當前排程: {len(self.scheduled_courses)} 個課程')

            choice = input('\n請輸入選項: ').strip().lower()

            # 處理數字輸入（選擇課程）
            if choice.isdigit():
                self.add_course_to_schedule(int(choice))

            # 查看排程
            elif choice == 'v':
                self.display_schedule()

            # 清除排程
            elif choice == 'c':
                confirm = input('\n確定要清除所有排程嗎？(y/n): ').strip().lower()
                if confirm == 'y':
                    self.clear_schedule()

            # 智能推薦
            elif choice == 'i':
                self.handle_intelligent_recommendation()

            # 儲存排程
            elif choice == 's':
                if not self.scheduled_courses:
                    print('\n✗ 排程為空，無需儲存')
                else:
                    self.save_schedule()

            # 執行排程
            elif choice == 'r':
                self.run_schedule()

            # 離開
            elif choice == 'q':
                # 檢查是否有未儲存的排程
                if self.scheduled_courses:
                    # 檢查是否與已儲存的不同
                    try:
                        with open(self.schedule_file, 'r', encoding='utf-8-sig') as f:
                            saved_data = json.load(f)
                            saved_courses = saved_data.get('courses', [])
                            if saved_courses != self.scheduled_courses:
                                save = input('\n排程尚未儲存，是否儲存？(y/n): ').strip().lower()
                                if save == 'y':
                                    self.save_schedule()
                    except:
                        save = input('\n排程尚未儲存，是否儲存？(y/n): ').strip().lower()
                        if save == 'y':
                            self.save_schedule()

                print('\n再見！')
                break

            else:
                print('\n✗ 無效的選項，請重新輸入')

            # 暫停讓使用者看到訊息
            input('\n按 Enter 繼續...')


def main():
    """主程式入口"""
    scheduler = CourseScheduler()
    scheduler.run()


if __name__ == '__main__':
    main()
