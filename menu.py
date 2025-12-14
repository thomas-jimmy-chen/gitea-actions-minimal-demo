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
        print('  • 輸入 h - 混合掃描 (API + Web 混合掃描課程結構) ⭐')
        print('  • 輸入 w - 快速查詢學習統計 (< 3 秒，無需瀏覽器) ⚡ NEW')
        print('  • 輸入 t - 測試學習履歷統計 API (研究用) 🔬')
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

    def get_course_activities(self, course_id, session_cookie, base_url):
        """
        獲取課程的所有學習活動（子課程）

        Args:
            course_id: 課程 ID
            session_cookie: Session cookie 字典
            base_url: 基礎 URL (e.g., 'https://elearn.post.gov.tw')

        Returns:
            activities: 活動列表，如果失敗返回空列表
        """
        import requests
        import urllib3

        # 禁用 SSL 警告
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        api_url = f"{base_url}/api/courses/{course_id}/activities"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-TW,zh;q=0.9',
            'Referer': f'{base_url}/course/{course_id}/learning-activity/full-screen',
            'Origin': base_url,
        }

        try:
            response = requests.get(
                api_url,
                cookies=session_cookie,
                headers=headers,
                verify=False,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('activities', [])
            else:
                print(f'    ✗ 獲取活動失敗 (狀態碼: {response.status_code})')
                return []

        except Exception as e:
            print(f'    ✗ 獲取活動異常: {e}')
            return []

    def extract_scorm_chapters(self, activity):
        """
        從 activity 的 SCORM manifest 中提取章節列表（孫課程）

        Args:
            activity: API 返回的單個 activity 物件

        Returns:
            chapters: 章節列表，每個元素包含 identifier, title, href
        """
        chapters = []

        try:
            # 導航到 SCORM manifest 的 items
            uploads = activity.get('uploads', [])
            if not uploads:
                return chapters

            # 獲取第一個 upload 的 SCORM 資料
            first_upload = uploads[0]
            scorm_data = first_upload.get('scorm', {})

            if not scorm_data:
                return chapters

            data = scorm_data.get('data', {})
            manifest = data.get('manifest', {})
            organizations = manifest.get('organizations', {})
            organization = organizations.get('organization', {})
            items = organization.get('item', [])

            # 提取每個 item（章節）
            for item in items:
                if isinstance(item, dict):
                    chapter = {
                        'identifier': item.get('identifier', ''),
                        'title': item.get('title', ''),
                        'identifierref': item.get('identifierref', ''),
                        'isvisible': item.get('isvisible', 'true')
                    }
                    chapters.append(chapter)

        except (KeyError, IndexError, AttributeError, TypeError) as e:
            # SCORM 結構可能不同或不存在，靜默失敗
            pass

        return chapters

    def match_chapters(self, api_chapters, web_items, threshold=0.5):
        """
        匹配 API 章節與 Web 掃描項目（孫課程匹配）

        Args:
            api_chapters: API 提取的章節列表
            web_items: Web 掃描的課程/考試項目列表
            threshold: 相似度閾值（預設 0.5，因為章節名稱通常較短）

        Returns:
            matches: 匹配結果列表
        """
        from difflib import SequenceMatcher

        matches = []

        for api_chapter in api_chapters:
            chapter_title = api_chapter.get('title', '')
            chapter_id = api_chapter.get('identifier', '')

            best_match = None
            best_confidence = 0.0

            # 與每個 Web 項目比對
            for web_item in web_items:
                # 確保 web_item 是字典且 item_name 是字串
                if not isinstance(web_item, dict):
                    continue

                web_name = web_item.get('item_name', '')

                # 確保 web_name 是字串
                if not isinstance(web_name, str):
                    continue

                # 計算相似度
                similarity = SequenceMatcher(
                    None,
                    chapter_title.lower(),
                    web_name.lower()
                ).ratio()

                if similarity > best_confidence:
                    best_confidence = similarity
                    best_match = web_item

            # 如果達到閾值，記錄匹配
            if best_match and best_confidence >= threshold:
                matches.append({
                    'api_chapter': {
                        'identifier': chapter_id,
                        'title': chapter_title,
                        'identifierref': api_chapter.get('identifierref', '')
                    },
                    'web_item': {
                        'item_name': best_match.get('item_name'),
                        'item_type': best_match.get('item_type')
                    },
                    'confidence': round(best_confidence, 4)
                })
            else:
                # 無法匹配的章節也記錄（web_item 為 None）
                matches.append({
                    'api_chapter': {
                        'identifier': chapter_id,
                        'title': chapter_title,
                        'identifierref': api_chapter.get('identifierref', '')
                    },
                    'web_item': None,
                    'confidence': 0.0
                })

        return matches

    def match_activities(self, api_activities, web_items, threshold=0.6):
        """
        匹配 API 活動與 Web 掃描項目

        Args:
            api_activities: API 返回的活動列表
            web_items: Web 掃描的課程/考試項目列表（僅包含 item_name）
            threshold: 相似度閾值（預設 0.6）

        Returns:
            matches: 匹配結果列表
        """
        from difflib import SequenceMatcher

        matches = []

        for api_activity in api_activities:
            api_title = api_activity.get('title', '')
            activity_id = api_activity.get('id')
            activity_type = api_activity.get('type', 'scorm')
            activity_sort = api_activity.get('sort', 0)
            completion_criterion = api_activity.get('completion_criterion', '')

            best_match = None
            best_confidence = 0.0

            # 與每個 Web 項目比對
            for web_item in web_items:
                # 確保 web_item 是字典且 item_name 是字串
                if not isinstance(web_item, dict):
                    continue

                web_name = web_item.get('item_name', '')

                # 確保 web_name 是字串
                if not isinstance(web_name, str):
                    continue

                # 計算相似度
                similarity = SequenceMatcher(
                    None,
                    api_title.lower(),
                    web_name.lower()
                ).ratio()

                if similarity > best_confidence:
                    best_confidence = similarity
                    best_match = web_item

            # 如果達到閾值，記錄匹配
            if best_match and best_confidence >= threshold:
                matches.append({
                    'api_activity': {
                        'id': activity_id,
                        'title': api_title,
                        'type': activity_type,
                        'sort': activity_sort,
                        'completion_criterion': completion_criterion
                    },
                    'web_item': {
                        'item_name': best_match.get('item_name'),
                        'item_type': best_match.get('item_type')
                    },
                    'confidence': round(best_confidence, 4)
                })
            else:
                # 無法匹配的活動也記錄（web_item 為 None）
                matches.append({
                    'api_activity': {
                        'id': activity_id,
                        'title': api_title,
                        'type': activity_type,
                        'sort': activity_sort,
                        'completion_criterion': completion_criterion
                    },
                    'web_item': None,
                    'confidence': 0.0
                })

        return matches

    def hybrid_scan(self):
        """混合掃描 v2.0 - 以 Web 為主，完整 API 匹配（主、子、孫課程）"""
        import requests
        import json
        from datetime import datetime
        from difflib import SequenceMatcher

        print('\n' + '=' * 70)
        print('  混合掃描 v2.0 - 完整課程結構匹配分析')
        print('=' * 70)
        print('\n此功能將：')
        print('  1. 初始化瀏覽器並登入系統')
        print('  2. Web 掃描：獲取完整課程結構（主、子、孫課程）')
        print('  3. API 掃描：獲取課程列表與詳細資料')
        print('  4. 智能匹配：建立 Web ↔ API 對應關係')
        print('  5. 輸出詳細匹配報告與統計數據')

        # ============================================================
        # 階段 1: 初始化與登入
        # ============================================================
        print('\n' + '-' * 70)
        print('[階段 1/4] 初始化與登入')
        print('-' * 70)

        driver = None
        max_retries = 3

        for attempt in range(max_retries):
            try:
                # 導入所需模組
                from src.utils.stealth_extractor import StealthExtractor
                from src.core.config_loader import ConfigLoader
                from src.core.driver_manager import DriverManager
                from src.core.cookie_manager import CookieManager
                from src.pages.login_page import LoginPage
                from src.pages.course_list_page import CourseListPage

                # 載入配置
                print('\n[初始化 1/3] 載入配置...')
                config = ConfigLoader('config/eebot.cfg')
                config.load()
                print('  ✓ 配置已載入')

                # 啟動瀏覽器
                print('[初始化 2/3] 啟動瀏覽器...')
                extractor = StealthExtractor()
                if not extractor.exists():
                    extractor.run()

                # 初始化核心元件
                driver_manager = DriverManager(config)
                cookie_manager = CookieManager()
                driver = driver_manager.create_driver(use_proxy=False)

                # 初始化頁面物件
                print('[初始化 3/3] 初始化頁面物件...')
                login_page = LoginPage(driver, cookie_manager)
                print('  ✓ 頁面物件已初始化')

                # 登入
                print(f'\n正在登入... (第 {attempt + 1}/{max_retries} 次)')
                login_success = login_page.auto_login(
                    username=config.get('user_name'),
                    password=config.get('password'),
                    url=config.get('target_http')
                )

                if login_success:
                    print('✓ 登入成功！')
                    break
                else:
                    print(f'✗ 登入失敗 (第 {attempt + 1}/{max_retries} 次)')
                    if attempt < max_retries - 1:
                        print('  等待 3 秒後重試...')
                        import time
                        time.sleep(3)
                        if driver:
                            driver.quit()
                            driver = None
                    else:
                        print('\n✗ 已達最大重試次數')
                        if driver:
                            driver.quit()
                        input('\n按 Enter 返回主選單...')
                        return

            except Exception as e:
                print(f'✗ 初始化失敗: {e}')
                if driver:
                    driver.quit()
                    driver = None
                if attempt < max_retries - 1:
                    print(f'  等待 3 秒後重試...')
                    import time
                    time.sleep(3)
                else:
                    print('\n✗ 已達最大重試次數')
                    input('\n按 Enter 返回主選單...')
                    return

        # ============================================================
        # 階段 2: Web 掃描 - 獲取完整課程結構（主、子、孫）
        # ============================================================
        print('\n' + '-' * 70)
        print('[階段 2/5] Web 掃描 - 獲取完整課程結構')
        print('-' * 70)

        web_programs = []  # 主課程列表

        try:
            course_list_page = CourseListPage(driver)

            # 前往我的課程
            print('\n進入「我的課程」...')
            course_list_page.goto_my_courses()
            import time
            time.sleep(2)

            # 獲取主課程列表
            print('正在獲取主課程列表...')
            programs = course_list_page.get_in_progress_programs()
            print(f'✓ 找到 {len(programs)} 個修習中的主課程')

            # 遍歷每個主課程
            for i, program in enumerate(programs, 1):
                program_name = program['name']
                print(f'\n[{i}/{len(programs)}] 掃描主課程: {program_name[:50]}...')

                program_data = {
                    'name': program_name,
                    'subcourses': [],  # 子課程列表
                    'exams': []        # 測驗列表
                }

                # 獲取子課程和測驗
                details = course_list_page.get_program_courses_and_exams(program_name)

                if details.get('error', False):
                    print(f'  ✗ 掃描失敗: {details.get("error_message", "未知錯誤")}')
                    program_data['error'] = True
                    web_programs.append(program_data)
                    continue

                courses = details.get('courses', [])
                exams = details.get('exams', [])
                print(f'  → 找到 {len(courses)} 個子課程, {len(exams)} 個測驗')

                # 處理子課程
                for j, course in enumerate(courses, 1):
                    if isinstance(course, dict):
                        course_name = course.get('name') or course.get('title') or str(course)
                    else:
                        course_name = str(course) if course else ''

                    print(f'    [{j}] {course_name[:40]}...')

                    subcourse_data = {
                        'name': course_name,
                        'chapters': []  # 章節列表（孫課程）
                    }

                    # 獲取孫課程（章節）
                    try:
                        print(f'        → 獲取章節...')
                        chapters = course_list_page.get_course_chapters(course_name)
                        subcourse_data['chapters'] = chapters
                        print(f'        ✓ 找到 {len(chapters)} 個章節')

                        # 顯示前 3 個章節
                        for k, chapter in enumerate(chapters[:3], 1):
                            chapter_name = chapter.get('name', '')
                            print(f'          └─ [{k}] {chapter_name[:35]}...')

                        if len(chapters) > 3:
                            print(f'          └─ ... 還有 {len(chapters) - 3} 個章節')

                    except Exception as e:
                        print(f'        ✗ 獲取章節失敗: {str(e)[:50]}')
                        subcourse_data['error'] = str(e)

                    program_data['subcourses'].append(subcourse_data)

                # 處理測驗
                for exam in exams:
                    if isinstance(exam, dict):
                        exam_name = exam.get('name') or exam.get('title') or str(exam)
                    else:
                        exam_name = str(exam) if exam else ''

                    program_data['exams'].append({'name': exam_name})

                # 返回主課程列表
                driver.back()
                time.sleep(2)

                web_programs.append(program_data)

            print(f'\n✓ Web 掃描完成')
            print(f'  → 主課程總數: {len(web_programs)}')
            total_subcourses = sum(len(p['subcourses']) for p in web_programs)
            total_chapters = sum(len(sc['chapters']) for p in web_programs for sc in p['subcourses'])
            print(f'  → 子課程總數: {total_subcourses}')
            print(f'  → 孫課程總數: {total_chapters}')

        except Exception as e:
            print(f'✗ Web 掃描失敗: {e}')
            import traceback
            traceback.print_exc()
            if driver:
                driver.quit()
            input('\n按 Enter 返回主選單...')
            return

        # ============================================================
        # 階段 3: API 掃描 - 獲取課程列表與詳細資料
        # ============================================================
        print('\n' + '-' * 70)
        print('[階段 3/5] API 掃描 - 獲取課程列表與詳細資料')
        print('-' * 70)

        api_courses = []
        session_cookie = None
        base_url = None

        try:
            # 提取 Session Cookie
            print('\n提取 Session Cookie...')
            cookies = driver.get_cookies()

            # 嘗試找到 V2-* 格式的 Session Cookie
            for cookie in cookies:
                if cookie['name'].startswith('V2-'):
                    session_cookie = {cookie['name']: cookie['value']}
                    print(f'✓ 找到 Session Cookie: {cookie["name"]}')
                    break

            # 如果沒有找到 V2-* Cookie，使用所有 Cookie
            if not session_cookie:
                print('[WARNING] 未找到 V2-* 格式的 Session Cookie，使用所有 Cookie')
                session_cookie = {c['name']: c['value'] for c in cookies}

            # 調用 /api/my-courses API
            print('\n調用 /api/my-courses API...')

            # 提取基礎 URL
            from urllib.parse import urlparse
            target_url = config.get('target_http')
            parsed = urlparse(target_url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            api_url = f"{base_url}/api/my-courses"

            print(f'[INFO] API URL: {api_url}')

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': base_url,
                'Origin': base_url,
            }

            # 禁用 SSL 警告
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            response = requests.get(
                api_url,
                cookies=session_cookie,
                headers=headers,
                verify=False,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                api_courses = data.get('courses', [])
                print(f'✓ API 課程列表獲取成功，共 {len(api_courses)} 門課程')

                # 遍歷每門 API 課程，獲取詳細資料（activities）
                print('\n正在獲取每門課程的詳細資料（activities）...')
                for i, api_course in enumerate(api_courses, 1):
                    course_id = api_course.get('course_id') or api_course.get('id')
                    course_name = api_course.get('name') or api_course.get('display_name') or ''

                    print(f'  [{i}/{len(api_courses)}] 課程 ID: {course_id} - {course_name[:40]}...')

                    # 獲取 activities
                    activities = self.get_course_activities(course_id, session_cookie, base_url)
                    api_course['activities'] = activities if activities else []

                    if activities:
                        print(f'      ✓ 找到 {len(activities)} 個 activities')

                        # 提取 SCORM chapters
                        for activity in activities:
                            chapters = self.extract_scorm_chapters(activity)
                            activity['chapters'] = chapters
                            if chapters:
                                print(f'          └─ Activity "{activity.get("name", "")[:30]}" 有 {len(chapters)} 個章節')
                    else:
                        print(f'      → 無 activities')

                print(f'\n✓ API 掃描完成')

            else:
                print(f'✗ API 請求失敗，狀態碼: {response.status_code}')
                raise Exception(f'API 請求失敗: {response.status_code}')

        except Exception as e:
            print(f'✗ API 掃描失敗: {e}')
            import traceback
            traceback.print_exc()
            if driver:
                driver.quit()
            input('\n按 Enter 返回主選單...')
            return

        # ============================================================
        # 階段 4: 智能匹配 - Web ↔ API 對應關係
        # ============================================================
        print('\n' + '-' * 70)
        print('[階段 4/5] 智能匹配 - 建立 Web ↔ API 對應關係')
        print('-' * 70)

        match_results = {
            'programs': [],  # 主課程匹配結果
            'stats': {
                'total_web_programs': len(web_programs),
                'total_api_courses': len(api_courses),
                'matched_programs': 0,
                'matched_subcourses': 0,
                'matched_chapters': 0,
                'total_web_subcourses': 0,
                'total_web_chapters': 0
            }
        }

        print('\n正在匹配主課程...')
        for web_program in web_programs:
            web_program_name = web_program['name']

            # 跳過掃描失敗的課程
            if web_program.get('error', False):
                continue

            print(f'\n處理主課程: {web_program_name[:50]}...')

            # 匹配 API 課程
            best_api_match = None
            best_similarity = 0

            for api_course in api_courses:
                api_course_name = api_course.get('name') or api_course.get('display_name') or ''
                similarity = SequenceMatcher(None, web_program_name.lower(), api_course_name.lower()).ratio()

                if similarity > best_similarity:
                    best_similarity = similarity
                    best_api_match = api_course

            program_match = {
                'web_name': web_program_name,
                'api_course': None,
                'match_score': 0,
                'subcourses': []
            }

            if best_similarity >= 0.7:  # 70% 閾值
                print(f'  ✓ 匹配到 API 課程 (相似度: {best_similarity:.2%})')
                program_match['api_course'] = best_api_match
                program_match['match_score'] = best_similarity
                match_results['stats']['matched_programs'] += 1

                # 匹配子課程
                api_activities = best_api_match.get('activities', [])
                print(f'  → 匹配子課程... (Web: {len(web_program["subcourses"])}, API: {len(api_activities)})')

                match_results['stats']['total_web_subcourses'] += len(web_program['subcourses'])

                for web_subcourse in web_program['subcourses']:
                    web_subcourse_name = web_subcourse['name']

                    # 匹配 API activity
                    best_activity_match = None
                    best_activity_similarity = 0

                    for api_activity in api_activities:
                        api_activity_name = api_activity.get('name') or api_activity.get('title') or ''
                        similarity = SequenceMatcher(None, web_subcourse_name.lower(), api_activity_name.lower()).ratio()

                        if similarity > best_activity_similarity:
                            best_activity_similarity = similarity
                            best_activity_match = api_activity

                    subcourse_match = {
                        'web_name': web_subcourse_name,
                        'api_activity': None,
                        'match_score': 0,
                        'chapters': []
                    }

                    if best_activity_similarity >= 0.6:  # 60% 閾值
                        print(f'      ✓ 子課程匹配 "{web_subcourse_name[:30]}" (相似度: {best_activity_similarity:.2%})')
                        subcourse_match['api_activity'] = best_activity_match
                        subcourse_match['match_score'] = best_activity_similarity
                        match_results['stats']['matched_subcourses'] += 1

                        # 匹配孫課程（章節）
                        api_chapters = best_activity_match.get('chapters', [])
                        web_chapters = web_subcourse.get('chapters', [])

                        match_results['stats']['total_web_chapters'] += len(web_chapters)

                        if web_chapters and api_chapters:
                            print(f'          → 匹配章節... (Web: {len(web_chapters)}, API: {len(api_chapters)})')

                            for web_chapter in web_chapters:
                                web_chapter_name = web_chapter.get('name', '')

                                # 匹配 API chapter
                                best_chapter_match = None
                                best_chapter_similarity = 0

                                for api_chapter in api_chapters:
                                    api_chapter_title = api_chapter.get('title', '')
                                    similarity = SequenceMatcher(None, web_chapter_name.lower(), api_chapter_title.lower()).ratio()

                                    if similarity > best_chapter_similarity:
                                        best_chapter_similarity = similarity
                                        best_chapter_match = api_chapter

                                chapter_match = {
                                    'web_name': web_chapter_name,
                                    'api_chapter': None,
                                    'match_score': 0
                                }

                                if best_chapter_similarity >= 0.5:  # 50% 閾值
                                    chapter_match['api_chapter'] = best_chapter_match
                                    chapter_match['match_score'] = best_chapter_similarity
                                    match_results['stats']['matched_chapters'] += 1

                                subcourse_match['chapters'].append(chapter_match)
                    else:
                        print(f'      ✗ 子課程無匹配 "{web_subcourse_name[:30]}"')

                    program_match['subcourses'].append(subcourse_match)
            else:
                print(f'  ✗ 無法匹配 API 課程 (最高相似度: {best_similarity:.2%})')

            match_results['programs'].append(program_match)

        print(f'\n✓ 匹配完成')

        # ============================================================
        # 階段 5: 輸出匹配報告
        # ============================================================
        print('\n' + '=' * 70)
        print('  混合掃描 v2.0 - 匹配分析報告')
        print('=' * 70)

        # 統計摘要
        stats = match_results['stats']
        print('\n' + '=' * 70)
        print('  統計摘要')
        print('=' * 70)

        # 主課程匹配
        print('\n【主課程匹配統計】')
        print(f'  Web 主課程總數:   {stats["total_web_programs"]}')
        print(f'  API 課程總數:     {stats["total_api_courses"]}')
        print(f'  成功匹配:         {stats["matched_programs"]}')
        if stats['total_web_programs'] > 0:
            match_rate = stats['matched_programs'] / stats['total_web_programs'] * 100
            print(f'  匹配率:           {match_rate:.2f}%')

        # 子課程匹配
        print('\n【子課程匹配統計】')
        print(f'  Web 子課程總數:   {stats["total_web_subcourses"]}')
        print(f'  成功匹配:         {stats["matched_subcourses"]}')
        if stats['total_web_subcourses'] > 0:
            submatch_rate = stats['matched_subcourses'] / stats['total_web_subcourses'] * 100
            print(f'  匹配率:           {submatch_rate:.2f}%')

        # 孫課程匹配
        print('\n【孫課程（章節）匹配統計】')
        print(f'  Web 章節總數:     {stats["total_web_chapters"]}')
        print(f'  成功匹配:         {stats["matched_chapters"]}')
        if stats['total_web_chapters'] > 0:
            chapter_match_rate = stats['matched_chapters'] / stats['total_web_chapters'] * 100
            print(f'  匹配率:           {chapter_match_rate:.2f}%')

        print('\n' + '=' * 70)

        # 詳細匹配結果（顯示前 5 個主課程）
        print('\n【詳細匹配結果（前 5 個主課程）】')
        print('=' * 70)

        for i, program_match in enumerate(match_results['programs'][:5], 1):
            print(f'\n[{i}] {program_match["web_name"][:50]}')

            if program_match['api_course']:
                api_name = program_match['api_course'].get('name', 'N/A')
                api_id = program_match['api_course'].get('course_id') or program_match['api_course'].get('id', 'N/A')
                print(f'    ✓ API 匹配: {api_name[:40]} (ID: {api_id}, 相似度: {program_match["match_score"]:.2%})')

                # 子課程匹配
                matched_subs = sum(1 for s in program_match['subcourses'] if s['api_activity'])
                total_subs = len(program_match['subcourses'])
                print(f'    → 子課程: {matched_subs}/{total_subs} 匹配')

                # 章節匹配
                total_chapters = sum(len(s['chapters']) for s in program_match['subcourses'])
                matched_chapters = sum(1 for s in program_match['subcourses'] for c in s['chapters'] if c['api_chapter'])
                if total_chapters > 0:
                    print(f'    → 章節: {matched_chapters}/{total_chapters} 匹配')
            else:
                print(f'    ✗ 無 API 匹配')

        if len(match_results['programs']) > 5:
            print(f'\n... 還有 {len(match_results["programs"]) - 5} 個主課程')

        print('\n' + '=' * 70)

        # 輸出 JSON 文件
        output_file = 'hybrid_scan_v2_result.json'
        try:
            output_data = {
                'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'version': '2.0',
                'summary': stats,
                'web_programs': web_programs,
                'api_courses': api_courses,
                'match_results': match_results
            }

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)

            print(f'\n✓ 結果已輸出到: {output_file}')
        except Exception as e:
            print(f'✗ 輸出檔案失敗: {e}')

        # 關閉瀏覽器
        if driver:
            driver.quit()
            print('\n✓ 瀏覽器已關閉')

        input('\n按 Enter 返回主選單...')

    def display_learning_summary(self):
        """顯示學習履歷摘要 (使用已保存的 cookies)"""
        import requests
        import json
        from pathlib import Path

        try:
            # 禁用 SSL 警告
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            # 嘗試從 cookies.json 讀取 session cookie
            cookies_path = Path("resource/cookies/cookies.json")
            session_cookie = None

            if cookies_path.exists():
                try:
                    with open(cookies_path, 'r') as f:
                        cookies = json.load(f)
                        for cookie in cookies:
                            if cookie.get('name') == 'session':
                                session_cookie = cookie.get('value')
                                break
                except:
                    pass

            if not session_cookie:
                # 沒有保存的 cookies，跳過顯示
                return

            # 調用 API
            url = "https://elearn.post.gov.tw/api/my-courses"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
            }
            cookies_dict = {'session': session_cookie}

            response = requests.get(url, headers=headers, cookies=cookies_dict, timeout=5, verify=False)

            if response.status_code == 200:
                data = response.json()
                courses = data.get('courses', [])

                # 計算統計
                total = len(courses)
                completed = len([c for c in courses if c.get('is_graduated') == True])
                in_progress = total - completed
                progress = (completed / total * 100) if total > 0 else 0

                # 顯示摘要
                print('\n' + '=' * 70)
                print('📊 學習履歷摘要')
                print('=' * 70)
                print(f'  學習進度: {progress:.1f}% | 完成: {completed}/{total} 課程 | 進行中: {in_progress}')
                print('=' * 70)

        except:
            # 靜默失敗，不影響主程式
            pass

    def quick_learning_stats(self):
        """快速查詢學習統計 (不啟動瀏覽器)"""
        import requests
        import json
        from pathlib import Path

        print('\n' + '=' * 70)
        print('  ⚡ 快速學習統計查詢')
        print('=' * 70)

        try:
            # 禁用 SSL 警告
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            # 從 cookies.json 讀取 session cookie
            cookies_path = Path("resource/cookies/cookies.json")
            session_cookie = None

            print('\n[步驟 1/3] 讀取已保存的 session...')
            if cookies_path.exists():
                try:
                    with open(cookies_path, 'r') as f:
                        cookies = json.load(f)
                        for cookie in cookies:
                            if cookie.get('name') == 'session':
                                session_cookie = cookie.get('value')
                                print('  ✓ 找到已保存的 session cookie')
                                break
                except Exception as e:
                    print(f'  ✗ 讀取 cookies 失敗: {e}')

            if not session_cookie:
                print('  ✗ 未找到已保存的 session')
                print('\n💡 提示: 請先執行以下操作之一來保存 session:')
                print('  1. 執行智能推薦 (i)')
                print('  2. 執行混合掃描 (h)')
                print('  3. 執行完整測試 (t)')
                input('\n按 Enter 返回主選單...')
                return

            # 調用 API
            print('\n[步驟 2/3] 調用 API 獲取課程資料...')
            url = "https://elearn.post.gov.tw/api/my-courses"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
            }
            cookies_dict = {'session': session_cookie}

            response = requests.get(url, headers=headers, cookies=cookies_dict, timeout=10, verify=False)

            if response.status_code == 200:
                print('  ✓ API 調用成功')

                data = response.json()
                courses = data.get('courses', [])

                # 計算統計
                total = len(courses)
                completed = len([c for c in courses if c.get('is_graduated') == True])
                in_progress = total - completed
                progress = (completed / total * 100) if total > 0 else 0

                print('\n[步驟 3/3] 生成統計報告...')
                print('  ✓ 統計完成')

                # 顯示詳細統計
                print('\n' + '=' * 70)
                print('📊 學習履歷詳細統計')
                print('=' * 70)
                print(f'\n學習進度: {progress:.1f}%')
                print(f'完成課程: {completed}')
                print(f'進行中課程: {in_progress}')
                print(f'課程總數: {total}')

                # 顯示課程明細
                if courses:
                    print(f'\n📚 課程明細 (顯示前 15 個):')
                    for i, course in enumerate(courses[:15], 1):
                        status = "✅ 已完成" if course.get('is_graduated') else "🔄 進行中"
                        print(f'  [{i:2d}] {status} - {course.get("name")}')

                    if len(courses) > 15:
                        print(f'\n  ... 還有 {len(courses) - 15} 個課程')

                print('\n' + '=' * 70)
                print(f'⚡ 查詢完成！(耗時 < 3 秒，無需啟動瀏覽器)')
                print('=' * 70)

            elif response.status_code == 401:
                print('  ✗ 認證失敗 (Session 已過期)')
                print('\n💡 提示: 請重新登入以更新 session:')
                print('  執行智能推薦 (i) 或混合掃描 (h)')
            else:
                print(f'  ✗ API 調用失敗: HTTP {response.status_code}')

        except requests.exceptions.Timeout:
            print('  ✗ 請求超時，請檢查網路連線')
        except Exception as e:
            print(f'  ✗ 查詢失敗: {e}')

        input('\n按 Enter 返回主選單...')

    def test_learning_stats(self):
        """測試學習履歷統計 API - 研究用功能"""
        import requests
        import json
        from datetime import datetime

        print('\n' + '=' * 70)
        print('  學習履歷統計 API 測試工具')
        print('=' * 70)
        print('\n此功能將：')
        print('  1. 初始化瀏覽器並登入系統')
        print('  2. 提取 session cookie')
        print('  3. 測試方案 1: 從 /api/my-courses 計算統計')
        print('  4. 測試方案 2: 尋找專門的統計 API')
        print('  5. 輸出完整測試報告')

        # ============================================================
        # 階段 1: 初始化與登入
        # ============================================================
        print('\n' + '-' * 70)
        print('[階段 1/5] 初始化與登入')
        print('-' * 70)

        driver = None
        max_retries = 3

        for attempt in range(max_retries):
            try:
                # 導入所需模組
                from src.utils.stealth_extractor import StealthExtractor
                from src.core.config_loader import ConfigLoader
                from src.core.driver_manager import DriverManager
                from src.core.cookie_manager import CookieManager
                from src.pages.login_page import LoginPage

                # 載入配置
                print('\n[初始化 1/3] 載入配置...')
                config = ConfigLoader('config/eebot.cfg')
                config.load()
                print('  ✓ 配置已載入')

                # 啟動瀏覽器
                print('[初始化 2/3] 啟動瀏覽器...')
                extractor = StealthExtractor()
                if not extractor.exists():
                    extractor.run()

                # 初始化核心元件
                driver_manager = DriverManager(config)
                cookie_manager = CookieManager()
                driver = driver_manager.create_driver(use_proxy=False)

                # 初始化頁面物件
                print('[初始化 3/3] 初始化頁面物件...')
                login_page = LoginPage(driver, cookie_manager)
                print('  ✓ 頁面物件已初始化')

                # 登入
                print(f'\n正在登入... (第 {attempt + 1}/{max_retries} 次)')
                login_success = login_page.auto_login(
                    username=config.get('user_name'),
                    password=config.get('password'),
                    url=config.get('target_http')
                )

                if login_success:
                    print('✓ 登入成功！')
                    break
                else:
                    print(f'✗ 登入失敗 (第 {attempt + 1}/{max_retries} 次)')
                    if attempt < max_retries - 1:
                        print('  等待 3 秒後重試...')
                        import time
                        time.sleep(3)
                        if driver:
                            driver.quit()
                            driver = None
                    else:
                        print('\n✗ 已達最大重試次數')
                        if driver:
                            driver.quit()
                        input('\n按 Enter 返回主選單...')
                        return

            except Exception as e:
                print(f'✗ 初始化失敗: {e}')
                if driver:
                    driver.quit()
                    driver = None
                if attempt < max_retries - 1:
                    print(f'  等待 3 秒後重試...')
                    import time
                    time.sleep(3)
                else:
                    print('\n✗ 已達最大重試次數')
                    input('\n按 Enter 返回主選單...')
                    return

        # ============================================================
        # 階段 2: 提取 Session Cookie
        # ============================================================
        print('\n' + '-' * 70)
        print('[階段 2/5] 提取 Session Cookie')
        print('-' * 70)

        session_cookie = None
        try:
            cookies = driver.get_cookies()

            # 先列出所有 cookies 以便除錯
            print(f'\n找到 {len(cookies)} 個 cookies:')
            for cookie in cookies:
                print(f'  - {cookie["name"]}: {len(cookie.get("value", ""))} 字元')

            # 嘗試多個可能的 session cookie 名稱
            possible_names = [
                'aenrich_session',
                'session',
                'PHPSESSID',
                'laravel_session',
                'connect.sid',
                'JSESSIONID'
            ]

            for cookie in cookies:
                if cookie['name'] in possible_names:
                    session_cookie = cookie['value']
                    print(f'\n✓ 成功提取 session cookie: {cookie["name"]}')
                    print(f'  Cookie 長度: {len(session_cookie)} 字元')
                    break

            # 如果沒找到標準名稱,使用最長的 cookie (通常是 session)
            if not session_cookie and cookies:
                longest_cookie = max(cookies, key=lambda c: len(c.get('value', '')))
                if len(longest_cookie.get('value', '')) > 50:  # Session cookie 通常很長
                    session_cookie = longest_cookie['value']
                    print(f'\n⚠️  使用最可能的 session cookie: {longest_cookie["name"]}')
                    print(f'  Cookie 長度: {len(session_cookie)} 字元')

            if not session_cookie:
                print('\n✗ 未找到有效的 session cookie')
                print('請檢查上方的 cookie 列表')
                if driver:
                    driver.quit()
                input('\n按 Enter 返回主選單...')
                return

        except Exception as e:
            print(f'✗ 提取 cookie 失敗: {e}')
            if driver:
                driver.quit()
            input('\n按 Enter 返回主選單...')
            return

        # ============================================================
        # 階段 3: 測試方案 1 - 從 my-courses 計算統計
        # ============================================================
        print('\n' + '-' * 70)
        print('[階段 3/5] 方案 1: 從 /api/my-courses 計算統計')
        print('-' * 70)

        calc_result = {}
        try:
            # 禁用 SSL 警告
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            url = "https://elearn.post.gov.tw/api/my-courses"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Referer': 'https://elearn.post.gov.tw/'
            }
            cookies_dict = {'session': session_cookie}  # 使用正確的 cookie 名稱

            print('\n調用 API: GET /api/my-courses')
            response = requests.get(url, headers=headers, cookies=cookies_dict, timeout=10, verify=False)

            if response.status_code == 200:
                data = response.json()
                courses = data.get('courses', [])

                # 計算統計
                total_courses = len(courses)
                completed_courses = len([c for c in courses if c.get('is_graduated') == True])
                in_progress_courses = total_courses - completed_courses
                progress = (completed_courses / total_courses * 100) if total_courses > 0 else 0

                print('\n✓ API 調用成功！')
                print('\n📊 學習履歷統計:')
                print(f'  學習進度: {progress:.1f}%')
                print(f'  完成課程: {completed_courses}')
                print(f'  進行中課程: {in_progress_courses}')
                print(f'  課程總數: {total_courses}')

                # 詳細列表
                print('\n📚 課程明細:')
                for course in courses[:10]:  # 只顯示前 10 個
                    status = "✅ 已完成" if course.get('is_graduated') else "🔄 進行中"
                    print(f'  {status} - {course.get("name")}')

                if len(courses) > 10:
                    print(f'  ... 還有 {len(courses) - 10} 個課程')

                calc_result = {
                    'success': True,
                    'total': total_courses,
                    'completed': completed_courses,
                    'in_progress': in_progress_courses,
                    'progress': progress,
                    'courses_count': len(courses)
                }

            else:
                print(f'\n✗ API 調用失敗: HTTP {response.status_code}')
                calc_result = {'success': False, 'error': f'HTTP {response.status_code}'}

        except Exception as e:
            print(f'\n✗ 方案 1 失敗: {e}')
            calc_result = {'success': False, 'error': str(e)}

        # ============================================================
        # 階段 4: 測試方案 2 - 尋找專門的統計 API
        # ============================================================
        print('\n' + '-' * 70)
        print('[階段 4/5] 方案 2: 尋找專門的統計 API')
        print('-' * 70)

        # 可能的統計 API 端點列表
        endpoints = [
            "/api/user/statistics",
            "/api/dashboard/summary",
            "/api/learning/progress",
            "/api/my-learning-stats",
            "/api/user/progress",
        ]

        api_results = []
        base_url = "https://elearn.post.gov.tw"

        print(f'\n測試 {len(endpoints)} 個可能的 API 端點...\n')

        for endpoint in endpoints:
            url = base_url + endpoint
            print(f'  測試: {endpoint}', end=' ')

            try:
                response = requests.get(
                    url,
                    headers=headers,
                    cookies=cookies_dict,
                    timeout=5,
                    verify=False  # 禁用 SSL 驗證
                )

                if response.status_code == 200:
                    try:
                        data = response.json()
                        print('✅ 成功!')
                        api_results.append({
                            'endpoint': endpoint,
                            'status': 200,
                            'success': True,
                            'data': data
                        })
                    except:
                        print('⚠️  200 但非 JSON')
                        api_results.append({
                            'endpoint': endpoint,
                            'status': 200,
                            'success': False
                        })
                else:
                    print(f'❌ {response.status_code}')
                    api_results.append({
                        'endpoint': endpoint,
                        'status': response.status_code,
                        'success': False
                    })

            except requests.exceptions.Timeout:
                print('⏰ 超時')
                api_results.append({
                    'endpoint': endpoint,
                    'status': 'timeout',
                    'success': False
                })
            except Exception as e:
                print(f'❌ 錯誤')
                api_results.append({
                    'endpoint': endpoint,
                    'status': 'error',
                    'success': False
                })

        # ============================================================
        # 階段 5: 輸出測試報告
        # ============================================================
        print('\n' + '-' * 70)
        print('[階段 5/5] 生成測試報告')
        print('-' * 70)

        # 總結
        successful_apis = [r for r in api_results if r.get('success')]

        print('\n' + '=' * 70)
        print('  測試結果總結')
        print('=' * 70)

        print(f'\n【方案 1】從 /api/my-courses 計算:')
        if calc_result.get('success'):
            print('  ✅ 成功')
            print(f'  統計: {calc_result.get("completed")}/{calc_result.get("total")} 課程完成 ({calc_result.get("progress"):.1f}%)')
        else:
            print('  ❌ 失敗')

        print(f'\n【方案 2】尋找專門統計 API:')
        if successful_apis:
            print(f'  ✅ 找到 {len(successful_apis)} 個有效 API:')
            for r in successful_apis:
                print(f'    - {r["endpoint"]}')
        else:
            print('  ❌ 未找到專門的統計 API')

        # 儲存結果
        output = {
            'test_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'calculated_from_my_courses': calc_result,
            'api_test_results': api_results,
            'successful_endpoints': successful_apis,
            'recommendation': '建議使用方案 1 (從 my-courses 計算)' if calc_result.get('success') else '需要進一步研究'
        }

        try:
            output_file = 'learning_stats_api_test_result.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            print(f'\n✓ 詳細報告已儲存至: {output_file}')
        except Exception as e:
            print(f'\n✗ 儲存報告失敗: {e}')

        # 關閉瀏覽器
        if driver:
            driver.quit()
            print('\n✓ 瀏覽器已關閉')

        input('\n按 Enter 返回主選單...')

    def hybrid_scan_full(self):
        """混合掃描 (API + Web) - 完整 4 層遍歷（備份版本）"""
        import requests
        from difflib import SequenceMatcher
        import json
        from datetime import datetime

        print('\n' + '=' * 70)
        print('  混合掃描 (API + Web 混合掃描課程結構)')
        print('=' * 70)
        print('\n此功能將：')
        print('  1. 使用 API 快速獲取課程 ID 列表')
        print('  2. 使用 Web 掃描獲取課程結構（主題/子主題）')
        print('  3. 建立 API 課程與 Web 結構的對應關係')
        print('  4. 輸出驗證檔案 hybrid_scan_result.json')

        # ============================================================
        # 階段 1: 初始化與登入
        # ============================================================
        print('\n' + '-' * 70)
        print('[階段 1/4] 初始化瀏覽器與登入系統')
        print('-' * 70)

        driver = None
        max_retries = 3

        for attempt in range(max_retries):
            try:
                # 導入所需模組
                from src.utils.stealth_extractor import StealthExtractor
                from src.core.config_loader import ConfigLoader
                from src.core.driver_manager import DriverManager
                from src.core.cookie_manager import CookieManager
                from src.pages.login_page import LoginPage

                # 1. 載入配置
                print('\n[初始化 1/4] 載入配置...')
                config = ConfigLoader('config/eebot.cfg')
                config.load()
                print('  ✓ 配置已載入')

                # 2. 啟動瀏覽器自動化模式（提取 Stealth JS）
                print('[初始化 2/4] 啟動瀏覽器自動化模式...')
                extractor = StealthExtractor()
                if not extractor.exists():
                    extractor.run()
                else:
                    print('  ✓ 瀏覽器自動化模式就緒，跳過初始化')

                # 3. 初始化核心元件（不使用 proxy）
                print('[初始化 3/4] 初始化核心元件...')
                driver_manager = DriverManager(config)
                cookie_manager = CookieManager(config.get('cookies_file'))
                print('  ✓ 核心元件已初始化')

                # 4. 建立 Driver（停用 proxy）
                print('[初始化 4/4] 啟動瀏覽器...')
                driver = driver_manager.create_driver(use_proxy=False)
                print('  ✓ 瀏覽器已啟動')

                # 5. 初始化頁面物件
                print('[初始化 5/5] 初始化頁面物件...')
                login_page = LoginPage(driver, cookie_manager)
                print('  ✓ 頁面物件已初始化')

                # 6. 登入
                print(f'\n[Step 1] 正在登入... (第 {attempt + 1}/{max_retries} 次)')
                login_success = login_page.auto_login(
                    username=config.get('user_name'),
                    password=config.get('password'),
                    url=config.get('target_http')
                )

                if login_success:
                    print('✓ 登入成功！')
                    break
                else:
                    print(f'✗ 登入失敗 (第 {attempt + 1}/{max_retries} 次)')
                    if attempt < max_retries - 1:
                        print('  等待 3 秒後重試...')
                        import time
                        time.sleep(3)
                        if driver:
                            driver.quit()
                            driver = None
                    else:
                        print('\n✗ 已達最大重試次數，登入失敗')
                        if driver:
                            driver.quit()
                        input('\n按 Enter 返回主選單...')
                        return

            except Exception as e:
                print(f'✗ 初始化失敗: {e}')
                if driver:
                    driver.quit()
                    driver = None
                if attempt < max_retries - 1:
                    print(f'  等待 3 秒後重試... (第 {attempt + 1}/{max_retries} 次)')
                    import time
                    time.sleep(3)
                else:
                    print('\n✗ 已達最大重試次數')
                    input('\n按 Enter 返回主選單...')
                    return

        # ============================================================
        # 階段 2: API 掃描 - 獲取課程 ID 列表
        # ============================================================
        print('\n' + '-' * 70)
        print('[階段 2/4] API 掃描 - 獲取課程 ID 列表')
        print('-' * 70)

        api_courses = []
        session_cookie = None

        try:
            # 提取 Session Cookie
            print('\n提取 Session Cookie...')
            cookies = driver.get_cookies()
            print(f'[INFO] 總共有 {len(cookies)} 個 Cookie')

            # 顯示所有 Cookie 名稱（用於調試）
            print('[DEBUG] Cookie 列表:')
            for cookie in cookies:
                print(f'  - {cookie["name"]}')

            # 嘗試找到 V2-* 格式的 Session Cookie
            for cookie in cookies:
                if cookie['name'].startswith('V2-'):
                    session_cookie = {cookie['name']: cookie['value']}
                    print(f'✓ 找到 Session Cookie: {cookie["name"]}')
                    print(f'  Cookie 值: {cookie["value"][:20]}...')
                    break

            # 如果沒有找到 V2-* Cookie，使用所有 Cookie
            if not session_cookie:
                print('[WARNING] 未找到 V2-* 格式的 Session Cookie')
                print('[INFO] 嘗試使用所有 Cookie')
                session_cookie = {c['name']: c['value'] for c in cookies}

            # 調用 API
            print('\n調用 /api/my-courses API...')

            # 修正 API URL：使用 urlparse 提取基礎 URL
            from urllib.parse import urlparse
            target_url = config.get('target_http')
            parsed = urlparse(target_url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            api_url = f"{base_url}/api/my-courses"

            print(f'[INFO] 基礎 URL: {base_url}')
            print(f'[INFO] API URL: {api_url}')

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': base_url,
                'Origin': base_url,
            }

            # 禁用 SSL 警告
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            print('[INFO] 發送 API 請求...')
            response = requests.get(
                api_url,
                cookies=session_cookie,
                headers=headers,
                verify=False,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()

                # 打印 API 回應的頂層結構
                print(f'\n[DEBUG] API 回應頂層鍵值: {list(data.keys())}')

                api_courses = data.get('courses', [])
                print(f'✓ API 掃描完成，共獲取 {len(api_courses)} 門課程')

                # 顯示第一個課程的完整資料（用於調試）
                if api_courses:
                    print('\n[DEBUG] 第一個課程的完整資料：')
                    print(json.dumps(api_courses[0], ensure_ascii=False, indent=2))

                # 顯示部分課程資訊
                print('\n前 3 門課程範例：')
                for i, course in enumerate(api_courses[:3], 1):
                    # 嘗試不同的可能鍵名
                    course_name = course.get("course_name") or course.get("name") or course.get("title") or "N/A"
                    course_id = course.get("course_id") or course.get("id") or "N/A"
                    print(f'  {i}. {course_name} (ID: {course_id})')
            else:
                print(f'✗ API 請求失敗，狀態碼: {response.status_code}')
                raise Exception(f'API 請求失敗: {response.status_code}')

        except Exception as e:
            print(f'✗ API 掃描失敗: {e}')
            if driver:
                driver.quit()
            input('\n按 Enter 返回主選單...')
            return

        # ============================================================
        # 階段 3: Web 掃描 - 獲取課程結構
        # ============================================================
        print('\n' + '-' * 70)
        print('[階段 3/4] Web 掃描 - 獲取課程結構')
        print('-' * 70)

        web_courses = []

        try:
            from src.pages.course_list_page import CourseListPage
            course_list_page = CourseListPage(driver)

            # 前往我的課程頁面
            print('\n前往我的課程頁面...')
            course_list_page.goto_my_courses()
            import time
            time.sleep(2)
            print('✓ 頁面載入完成')

            # 獲取修習中的主題
            print('\n掃描修習中的主題...')
            programs = course_list_page.get_in_progress_programs()
            print(f'✓ 找到 {len(programs)} 個修習中的主題')

            # 掃描每個主題的課程/考試
            print('\n掃描主題內的課程與考試...')
            for i, program in enumerate(programs, 1):
                program_name = program['name']
                print(f'\n  [{i}/{len(programs)}] 掃描主題: {program_name[:50]}...')

                # get_program_courses_and_exams() 返回 {'courses': [...], 'exams': [...]}
                details = course_list_page.get_program_courses_and_exams(program_name)

                # 處理課程
                for course in details.get('courses', []):
                    # 確保 course 是字串
                    if isinstance(course, dict):
                        # 如果是字典，嘗試提取名稱
                        course_name = course.get('name') or course.get('title') or str(course)
                    else:
                        course_name = str(course) if course else ''

                    # 添加子課程到列表
                    web_course = {
                        'program_name': program_name,
                        'item_name': course_name,
                        'item_type': 'course',
                        'chapters': []  # 初始化章節列表
                    }
                    print(f'    • [課程] {course_name}')

                    # 點擊進入子課程，獲取孫課程（章節）
                    try:
                        chapters = course_list_page.get_course_chapters(course_name)
                        web_course['chapters'] = chapters

                        # 將每個章節也添加到 web_courses 中
                        for chapter in chapters:
                            chapter_name = chapter.get('name', '')
                            web_chapter = {
                                'program_name': program_name,
                                'parent_course': course_name,  # 記錄父課程
                                'item_name': chapter_name,
                                'item_type': 'chapter'
                            }
                            web_courses.append(web_chapter)
                            print(f'      └─ [章節] {chapter_name[:50]}')
                    except Exception as e:
                        print(f'      ✗ 獲取章節失敗: {e}')
                        web_course['chapters'] = []

                    web_courses.append(web_course)

                # 處理考試
                for exam in details.get('exams', []):
                    # 確保 exam 是字串
                    if isinstance(exam, dict):
                        # 如果是字典，嘗試提取名稱
                        exam_name = exam.get('name') or exam.get('title') or str(exam)
                    else:
                        exam_name = str(exam) if exam else ''

                    web_exam = {
                        'program_name': program_name,
                        'item_name': exam_name,
                        'item_type': 'exam'
                    }
                    web_courses.append(web_exam)
                    print(f'    • [考試] {exam_name}')

                # 處理完該主題的所有子課程和考試後，返回到主課程列表
                try:
                    print(f'    ← 返回主課程列表')
                    driver.back()
                    import time
                    time.sleep(2)
                except Exception as e:
                    print(f'    ✗ 返回失敗: {e}')

            print(f'\n✓ Web 掃描完成，共獲取 {len(web_courses)} 個課程/考試項目')

        except Exception as e:
            print(f'✗ Web 掃描失敗: {e}')
            if driver:
                driver.quit()
            input('\n按 Enter 返回主選單...')
            return

        # ============================================================
        # 階段 4: 匹配演算法 - 建立對應關係
        # ============================================================
        print('\n' + '-' * 70)
        print('[階段 4/4] 匹配演算法 - 建立 API 與 Web 的對應關係')
        print('-' * 70)

        matched_courses = []
        # 注意：以 Web 為主，不再追蹤 unmatched_api_courses
        unmatched_api_courses = []  # 保留變數但不使用，避免後續代碼錯誤

        similarity_threshold = 0.7

        print(f'\n使用相似度匹配演算法（以 Web 為主，閾值: {similarity_threshold}）...')
        print('策略：遍歷 Web 掃描結果，為每個 Web 項目尋找對應的 API 數據\n')

        # 已使用的 API 課程 ID（避免重複匹配）
        used_api_ids = set()

        # 按 program_name 分組 Web 課程
        web_programs = {}
        for web_course in web_courses:
            program_name = web_course.get('program_name', '')
            if program_name not in web_programs:
                web_programs[program_name] = []
            web_programs[program_name].append(web_course)

        # 遍歷每個 Web program（主課程）
        for program_name, web_items in web_programs.items():
            print(f'\n處理 Web 主課程: {program_name[:60]}...')

            # 尋找最佳匹配的 API 課程
            best_api_match = None
            best_score = 0

            for api_course in api_courses:
                # 跳過已使用的 API 課程
                api_id = api_course.get('id')
                if api_id in used_api_ids:
                    continue

                api_name = api_course.get('name') or api_course.get('display_name', '')

                # 計算相似度
                similarity = SequenceMatcher(None, api_name, program_name).ratio()

                if similarity > best_score:
                    best_score = similarity
                    best_api_match = api_course

            # 判斷是否達到閾值
            if best_score >= similarity_threshold and best_api_match:
                # 成功匹配
                api_id = best_api_match.get('id')
                api_name = best_api_match.get('name') or best_api_match.get('display_name', '')
                used_api_ids.add(api_id)

                matched_courses.append({
                    'api_data': {
                        'course_id': api_id,
                        'course_name': api_name,
                        'course_code': best_api_match.get('course_code'),
                        'is_graduated': best_api_match.get('is_graduated', False),
                        'credit': best_api_match.get('credit'),
                        'start_date': best_api_match.get('start_date'),
                        'end_date': best_api_match.get('end_date')
                    },
                    'web_data': {
                        'program_name': program_name,
                        'items': web_items  # 保存所有子項目（courses, exams, chapters）
                    },
                    'match_confidence': round(best_score, 4)
                })

                # 顯示匹配結果
                confidence_level = '高' if best_score >= 0.9 else '中' if best_score >= 0.8 else '低'
                print(f'  ✓ [{confidence_level}] 相似度: {best_score:.2%}')
                print(f'      Web: {program_name[:60]}...')
                print(f'      → API: {api_name[:60]}...')
                print(f'      包含 {len(web_items)} 個子項目')
            else:
                # 未找到對應的 API，仍保留該 Web 課程
                matched_courses.append({
                    'api_data': None,  # 沒有對應的 API
                    'web_data': {
                        'program_name': program_name,
                        'items': web_items
                    },
                    'match_confidence': 0.0
                })
                print(f'  ✗ 未找到對應 API (最高相似度: {best_score:.2%})')
                print(f'      Web: {program_name[:60]}...')
                print(f'      包含 {len(web_items)} 個子項目')

        # 注意：以 Web 為主，不再有 unmatched_web_courses
        # 所有 Web 課程都在 matched_courses 中（即使沒有對應的 API）
        unmatched_web_courses_clean = []  # 保留變數但為空，避免後續代碼錯誤

        # ============================================================
        # 階段 4.5: 子課程匹配 - 針對已匹配的主課程獲取子課程並匹配
        # ============================================================
        print('\n' + '-' * 70)
        print('[階段 4.5/4] 子課程匹配 - 獲取並匹配子課程活動')
        print('-' * 70)

        total_api_activities = 0
        total_matched_activities = 0
        total_unmatched_activities = 0

        # 孫課程（章節）統計
        total_api_chapters = 0
        total_matched_chapters = 0
        total_unmatched_chapters = 0

        # 針對每個主課程
        for i, matched_course in enumerate(matched_courses, 1):
            program_name = matched_course['web_data']['program_name']
            web_items = matched_course['web_data']['items']

            # 檢查是否有對應的 API 數據
            if matched_course['api_data'] is None:
                print(f'\n  [{i}/{len(matched_courses)}] 跳過: {program_name[:50]}... (無對應 API)')
                matched_course['activity_matches'] = []
                continue

            course_id = matched_course['api_data']['course_id']
            course_name = matched_course['api_data']['course_name']

            print(f'\n  [{i}/{len(matched_courses)}] 處理課程: {course_name[:50]}...')
            print(f'      對應的 Web 主題: {program_name[:50]}...')

            # 1. 調用 activities API 獲取子課程
            print(f'      → 正在獲取課程 {course_id} 的活動...')
            api_activities = self.get_course_activities(course_id, session_cookie, base_url)

            if not api_activities:
                print(f'      ✗ 未獲取到活動（可能是 API 失敗或課程無活動）')
                matched_course['activity_matches'] = []
                continue

            print(f'      ✓ 獲取到 {len(api_activities)} 個活動')
            total_api_activities += len(api_activities)

            # 2. 獲取對應的 Web 子課程列表（從 web_data['items'] 中獲取）
            web_items_for_program = web_items

            print(f'      ✓ 找到 {len(web_items_for_program)} 個 Web 項目')

            # 3. 執行子課程匹配
            activity_threshold = 0.6
            activity_matches = self.match_activities(api_activities, web_items_for_program, threshold=activity_threshold)

            # 4. 統計匹配結果
            matched_count = sum(1 for m in activity_matches if m['web_item'] is not None)
            unmatched_count = len(activity_matches) - matched_count
            total_matched_activities += matched_count
            total_unmatched_activities += unmatched_count

            print(f'      ✓ 匹配結果: {matched_count} 成功 / {unmatched_count} 失敗')

            # 4.5. 針對每個活動提取並匹配孫課程（章節）
            print(f'      → 正在提取並匹配章節（孫課程）...')

            total_chapters_for_course = 0
            total_matched_chapters_for_course = 0

            for activity_match in activity_matches:
                # 從原始 API activity 中提取章節
                # 需要找到對應的原始 activity 物件
                activity_id = activity_match['api_activity']['id']
                original_activity = next((a for a in api_activities if a.get('id') == activity_id), None)

                if not original_activity:
                    activity_match['chapter_matches'] = []
                    continue

                # 提取章節
                api_chapters = self.extract_scorm_chapters(original_activity)

                if not api_chapters:
                    activity_match['chapter_matches'] = []
                    continue

                total_chapters_for_course += len(api_chapters)

                # 匹配章節與 Web 項目（使用相同的 web_items_for_program）
                chapter_threshold = 0.5
                chapter_matches = self.match_chapters(api_chapters, web_items_for_program, threshold=chapter_threshold)

                # 統計章節匹配結果
                matched_chapters = sum(1 for cm in chapter_matches if cm['web_item'] is not None)
                total_matched_chapters_for_course += matched_chapters

                # 將章節匹配結果添加到 activity_match
                activity_match['chapter_matches'] = chapter_matches

            if total_chapters_for_course > 0:
                chapter_match_rate = (total_matched_chapters_for_course / total_chapters_for_course * 100)
                print(f'      ✓ 章節匹配: {total_matched_chapters_for_course}/{total_chapters_for_course} 成功 ({chapter_match_rate:.1f}%)')

                # 累加到全局統計
                total_api_chapters += total_chapters_for_course
                total_matched_chapters += total_matched_chapters_for_course
                total_unmatched_chapters += (total_chapters_for_course - total_matched_chapters_for_course)
            else:
                print(f'      ℹ️  未找到 SCORM 章節資料')

            # 5. 顯示部分匹配詳情（最多顯示 3 個，包含章節資訊）
            for j, match in enumerate(activity_matches[:3], 1):
                api_title = match['api_activity']['title']
                confidence = match['confidence']
                chapter_matches = match.get('chapter_matches', [])

                if match['web_item']:
                    web_name = match['web_item']['item_name']
                    web_type = match['web_item']['item_type']
                    print(f'        [{j}] API: {api_title[:40]}...')
                    print(f'            → Web: [{web_type}] {web_name[:40]}... (信心度: {confidence:.2%})')

                    # 顯示章節資訊
                    if chapter_matches:
                        matched_chapters_count = sum(1 for cm in chapter_matches if cm['web_item'] is not None)
                        print(f'            └─ 章節: {matched_chapters_count}/{len(chapter_matches)} 匹配')
                        # 顯示前 2 個章節
                        for k, cm in enumerate(chapter_matches[:2], 1):
                            ch_title = cm['api_chapter']['title']
                            if cm['web_item']:
                                print(f'               • {ch_title[:35]}... ✓')
                            else:
                                print(f'               • {ch_title[:35]}... ✗')
                        if len(chapter_matches) > 2:
                            print(f'               ... (還有 {len(chapter_matches) - 2} 個章節)')
                else:
                    print(f'        [{j}] API: {api_title[:40]}... → ✗ 未匹配')

                    # 即使活動未匹配，也顯示章節資訊
                    if chapter_matches:
                        print(f'            └─ 章節: {len(chapter_matches)} 個（未匹配活動）')

            if len(activity_matches) > 3:
                print(f'        ... (還有 {len(activity_matches) - 3} 個活動)')

            # 6. 將匹配結果添加到 matched_course
            matched_course['activity_matches'] = activity_matches

        # 計算子課程匹配率
        activity_match_rate = (
            (total_matched_activities / total_api_activities * 100)
            if total_api_activities > 0 else 0
        )

        # 計算孫課程（章節）匹配率
        chapter_match_rate = (
            (total_matched_chapters / total_api_chapters * 100)
            if total_api_chapters > 0 else 0
        )

        print('\n' + '-' * 70)
        print('子課程 & 孫課程匹配摘要')
        print('-' * 70)
        print('\n【子課程（活動）】')
        print(f'  總活動數:         {total_api_activities}')
        print(f'  成功匹配:         {total_matched_activities}')
        print(f'  未匹配:           {total_unmatched_activities}')
        print(f'  匹配率:           {activity_match_rate:.2f}%')
        print('\n【孫課程（章節）】')
        print(f'  總章節數:         {total_api_chapters}')
        print(f'  成功匹配:         {total_matched_chapters}')
        print(f'  未匹配:           {total_unmatched_chapters}')
        print(f'  匹配率:           {chapter_match_rate:.2f}%')
        print('-' * 70)

        # ============================================================
        # 輸出結果到 JSON 檔案
        # ============================================================
        print('\n' + '-' * 70)
        print('輸出驗證檔案')
        print('-' * 70)

        # 計算有 API 數據的課程數量
        web_programs_count = len(web_programs)
        courses_with_api = sum(1 for mc in matched_courses if mc['api_data'] is not None)
        courses_without_api = web_programs_count - courses_with_api

        # 以 Web 為主的匹配率
        match_rate = (courses_with_api / web_programs_count * 100) if web_programs_count else 0

        result = {
            'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'total_api_courses': len(api_courses),
                'total_web_programs': web_programs_count,  # Web 主課程數量
                'total_web_items': len(web_courses),  # Web 項目總數（含子課程、章節）
                'web_with_api': courses_with_api,  # 有對應 API 的 Web 課程
                'web_without_api': courses_without_api,  # 沒有對應 API 的 Web 課程
                'match_rate': round(match_rate, 2),
                # 子課程統計（新增）
                'total_api_activities': total_api_activities,
                'matched_activities': total_matched_activities,
                'unmatched_activities': total_unmatched_activities,
                'activity_match_rate': round(activity_match_rate, 2),
                # 孫課程（章節）統計（新增）
                'total_api_chapters': total_api_chapters,
                'matched_chapters': total_matched_chapters,
                'unmatched_chapters': total_unmatched_chapters,
                'chapter_match_rate': round(chapter_match_rate, 2)
            },
            'courses': matched_courses,  # 所有 Web 課程（含有/無 API 的）
            'note': '以 Web 為主，courses 包含所有 Web 掃描的課程，api_data 為 None 表示該 Web 課程沒有對應的 API 數據'
        }

        output_file = 'hybrid_scan_result.json'

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            print(f'\n✓ 結果已輸出到: {output_file}')
            print('\n' + '=' * 70)
            print('  掃描摘要（以 Web 為主）')
            print('=' * 70)
            print('\n【主課程匹配】')
            print(f'  API 課程總數:         {len(api_courses)}')
            print(f'  Web 主課程總數:       {web_programs_count}')
            print(f'  Web 項目總數:         {len(web_courses)} (含子課程、章節)')
            print(f'  有對應 API:           {courses_with_api}')
            print(f'  無對應 API:           {courses_without_api}')
            print(f'  匹配率:               {match_rate:.2f}%')
            print('\n【子課程（活動）匹配】')
            print(f'  API 活動總數:     {total_api_activities}')
            print(f'  成功匹配:         {total_matched_activities}')
            print(f'  未匹配:           {total_unmatched_activities}')
            print(f'  匹配率:           {activity_match_rate:.2f}%')
            print('\n【孫課程（章節）匹配】')
            print(f'  API 章節總數:     {total_api_chapters}')
            print(f'  成功匹配:         {total_matched_chapters}')
            print(f'  未匹配:           {total_unmatched_chapters}')
            print(f'  匹配率:           {chapter_match_rate:.2f}%')
            print('=' * 70)

        except Exception as e:
            print(f'✗ 輸出檔案失敗: {e}')

        # 關閉瀏覽器
        if driver:
            driver.quit()
            print('\n✓ 瀏覽器已關閉')

        print('\n✓ 混合掃描完成！')
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

        # A 方案: 顯示學習履歷摘要 (如果有保存的 session)
        self.display_learning_summary()

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

            # 混合掃描
            elif choice == 'h':
                self.hybrid_scan()

            # 快速查詢學習統計 (C 方案)
            elif choice == 'w':
                self.quick_learning_stats()

            # 測試學習履歷統計 API
            elif choice == 't':
                self.test_learning_stats()

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
