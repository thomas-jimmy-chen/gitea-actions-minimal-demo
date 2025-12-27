#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
EEBot 互動式選單 - 課程排程管理
允許使用者選擇課程並加入排程

Author: wizard03
Date: 2025/11/10
Version: 2.0.1

Phase 3 重構：整合 Orchestrator 層
- 使用 feature_enabled('use_orchestrators') 控制新舊實現切換
- Orchestrator 層提供更好的可測試性和模組化
"""

import json
import os
import sys

# 設定 Windows 命令行編碼
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


# =============================================================================
# Orchestrator 整合 (Phase 3)
# =============================================================================

def _use_orchestrators() -> bool:
    """檢查是否啟用 Orchestrator 層"""
    try:
        from src.config.feature_flags import feature_enabled
        return feature_enabled('use_orchestrators')
    except ImportError:
        return False


def _get_config():
    """獲取配置對象"""
    from src.core.config_loader import ConfigLoader
    config = ConfigLoader("config/eebot.cfg")
    config.load()
    return config


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
        print('  EEBot 課程排程管理系統')
        print('=' * 70)

        # === 智能掃描 ===
        print('\n[智能掃描] 自動偵測修習中課程')
        print('  i - 一鍵自動執行 (掃描 + 執行)')
        print('  h - 混合掃描 (API + Web 混合模式)')

        # === 快速查詢 ===
        print('\n[快速查詢] 無需瀏覽器')
        print('  w - 學習統計查詢 (< 3 秒)')
        print('  t - 測試 API (研究用)')

        # === 預製排程 ===
        print('\n[預製排程] 114年郵政E大學學員個人課程')
        print('  1-{} - 選擇課程加入排程'.format(len(self.all_courses)))
        print('  v - 查看排程 | c - 清除 | s - 儲存 | r - 執行')

        # 顯示課程列表（精簡版）
        print('\n  課程列表:')
        for i, course in enumerate(self.all_courses, 1):
            course_type = course.get('course_type', 'course')
            if course_type == 'exam':
                name = course.get('exam_name', '')
                print(f'    {i:2d}. {course["program_name"]} - {name} [考試]')
            else:
                name = course.get('lesson_name', '')
                print(f'    {i:2d}. {course["program_name"]} - {name}')

        print('\n  q - 離開')
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

        # =====================================================================
        # Phase 3: Orchestrator 整合
        # =====================================================================
        if _use_orchestrators():
            self._handle_intelligent_recommendation_orchestrator()
            return

        # =====================================================================
        # Legacy 實現 (當 use_orchestrators=False 時使用)
        # =====================================================================
        self._handle_intelligent_recommendation_legacy()

    def _handle_intelligent_recommendation_orchestrator(self):
        """使用 Orchestrator 執行智能推薦"""
        try:
            from src.orchestrators import IntelligentRecommendationOrchestrator

            config = _get_config()
            orchestrator = IntelligentRecommendationOrchestrator(config)

            # 傳入 scheduler 讓 orchestrator 可以存取排程
            result = orchestrator.execute(scheduler=self)

            if result.success:
                print('\n' + '=' * 70)
                print('  ✓ 智能推薦執行完成')
                print('=' * 70)
                print(f"  掃描課程數: {result.data.get('scanned_count', 0)}")
                print(f"  執行課程數: {result.data.get('executed_count', 0)}")
            else:
                print('\n' + '=' * 70)
                print('  ✗ 智能推薦執行失敗')
                print('=' * 70)
                print(f"  錯誤: {result.error}")

        except Exception as e:
            print(f'\n[錯誤] Orchestrator 執行失敗: {e}')
            print('嘗試使用 Legacy 模式...')
            # Fallback to legacy on error
            from src.config.feature_flags import feature_enabled
            if feature_enabled('fallback_on_error'):
                self._handle_intelligent_recommendation_legacy()
            else:
                raise

        input('\n按 Enter 返回主選單...')

    def _handle_intelligent_recommendation_legacy(self):
        """Legacy 實現 - 智能推薦"""

        # ===================================================================
        # 🆕 修改點 1: 提前載入配置（用於 ExecutionWrapper 初始化）
        # ===================================================================
        from src.core.config_loader import ConfigLoader
        config = ConfigLoader("config/eebot.cfg")
        config.load()

        # ===================================================================
        # 🆕 修改點 2: 初始化 ExecutionWrapper
        # ===================================================================
        from src.utils.execution_wrapper import ExecutionWrapper

        with ExecutionWrapper(config, "智能推薦") as wrapper:
            # ===================================================================
            # 🆕 修改點 3: 步驟 1 - 執行前清理（開始階段追蹤）
            # ===================================================================
            wrapper.start_phase("執行前清理")

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
                'resource/plugins/stealth.min.js',
            ]

            for file_path in temp_files:
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        # 將技術性檔名轉為使用者友善的顯示名稱
                        display_name = file_path.replace(
                            'stealth.min.js', 'stealth mode file'
                        )
                        print(f'  ✓ 已刪除: {display_name}')
                    except OSError as e:
                        display_name = file_path.replace(
                            'stealth.min.js', 'stealth mode file'
                        )
                        print(f'  ✗ 刪除失敗 {display_name}: {e}')

            print('  ✓ 執行前清理完成\n')

            # ===================================================================
            # 🆕 修改點 4: 步驟 1 結束階段追蹤
            # ===================================================================
            wrapper.end_phase("執行前清理")

            # ===================================================================
            # 🆕 修改點 5: 步驟 2-4 - 瀏覽器操作與掃描（開始階段追蹤）
            # ===================================================================
            wrapper.start_phase("瀏覽器操作與掃描")

            # ===== 步驟 2-4: 掃描課程 =====
            driver_manager = None

            try:
                from src.core.cookie_manager import CookieManager
                from src.core.driver_manager import DriverManager
                from src.pages.course_list_page import CourseListPage
                from src.pages.login_page import LoginPage
                from src.utils.stealth_extractor import StealthExtractor

                print('[步驟 2/5] 正在啟動瀏覽器...')
                print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')

                # 1. 載入配置（已在外部載入，此處可跳過）
                print('[初始化 1/5] 載入配置...')
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
                        url=config.get('target_http'),
                    )

                    if login_success:
                        print('  ✓ 登入成功\n')
                        break
                    else:
                        if attempt < max_retries - 1:
                            print(
                                f'  ⚠️  登入失敗，重試中... ({attempt + 1}/{max_retries})\n'
                            )
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

                # 獲取 base_url（用於返回失敗時的備用導航）
                from urllib.parse import urlparse
                target_url = config.get('target_http')
                parsed = urlparse(target_url)
                base_url = f'{parsed.scheme}://{parsed.netloc}'

                for i, program in enumerate(programs, 1):
                    program_name = program['name']
                    print(f'  [{i}/{len(programs)}] {program_name[:50]}...')

                    details = course_list_page.get_program_courses_and_exams(
                        program_name
                    )

                    # 檢查是否掃描失敗
                    if details.get('error', False):
                        print(f'  ✗ 掃描失敗: {details.get("error_message", "未知錯誤")}')
                        available_courses.append(
                            {
                                'program_name': program_name,
                                'courses': [],
                                'exams': [],
                            }
                        )

                        # ✨ 掃描失敗時也要返回課程列表（參考 h 選單邏輯）
                        if i < len(programs):
                            print(f'  → 返回課程列表...')
                            try:
                                course_list_page.go_back_to_course_list()
                            except Exception as e1:
                                print(f'  [WARNING] 返回按鈕失敗，嘗試直接導航: {e1}')
                                try:
                                    driver.get(f'{base_url}/user/courses')
                                    time.sleep(2)
                                    print('  ✓ 已導航到課程列表')
                                except Exception as e2:
                                    print(f'  [ERROR] 導航失敗: {e2}')
                        continue

                    available_courses.append(
                        {
                            'program_name': program_name,
                            'courses': details.get('courses', []),
                            'exams': details.get('exams', []),
                        }
                    )

                    # ✨ 關鍵修復：返回課程列表，準備處理下一個課程（參考 h 選單邏輯）
                    if i < len(programs):  # 如果不是最後一個課程
                        print(f'  → 返回課程列表...')
                        try:
                            # 方法 1: 嘗試使用返回按鈕
                            course_list_page.go_back_to_course_list()
                        except Exception as e1:
                            print(f'  [WARNING] 返回按鈕失敗，嘗試直接導航: {e1}')
                            try:
                                # 方法 2: 直接導航到課程列表頁面
                                driver.get(f'{base_url}/user/courses')
                                time.sleep(2)
                                print('  ✓ 已導航到課程列表')
                            except Exception as e2:
                                print(f'  [ERROR] 導航失敗: {e2}')
                                # 不拋出異常，繼續處理下一個課程

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
                        return ''
                    return ''.join(text.split()).lower()

                def match_course(web_name, courses_list):
                    """匹配課程"""
                    web_norm = normalize_text(web_name)
                    for course in courses_list:
                        config_name = course.get('lesson_name') or course.get(
                            'exam_name'
                        )
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
                        similarity = SequenceMatcher(
                            None, web_norm, config_norm
                        ).ratio()
                        if similarity >= 0.90:
                            return course
                    return None

                recommendations = []
                for program in available_courses:
                    program_name = program['program_name']
                    # 比對一般課程
                    for course in program.get('courses', []):
                        matched_config = match_course(
                            course['name'], config_courses
                        )
                        if matched_config:
                            recommendations.append(
                                {
                                    'program_name': program_name,
                                    'item_name': course['name'],
                                    'type': 'course',
                                    'matched': True,
                                    'config': matched_config,
                                }
                            )
                    # 比對考試
                    for exam in program.get('exams', []):
                        matched_config = match_course(exam['name'], config_courses)
                        if matched_config:
                            recommendations.append(
                                {
                                    'program_name': program_name,
                                    'item_name': exam['name'],
                                    'type': 'exam',
                                    'matched': True,
                                    'auto_answer': matched_config.get(
                                        'enable_auto_answer', False
                                    ),
                                    'config': matched_config,
                                }
                            )

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
                    item_type = '考試' if item['type'] == 'exam' else '課程'
                    print(f"{i}. [{item_type}] {item['item_name']}")
                    print(f"   📚 所屬計畫: {item['program_name']}")
                    print(f'   ✅ 已配置')

                    item_config = item.get('config', {})

                    # 顯示課程特性
                    if item['type'] == 'exam':
                        if item.get('auto_answer'):
                            print(f'   🤖 自動答題: 啟用')
                        else:
                            print(f'   📝 手動作答')
                    else:
                        # 一般課程 - 顯示截圖狀態
                        if item_config.get('enable_screenshot', False):
                            print(f'   📸 截圖: 啟用')
                        else:
                            print(f'   📸 截圖: 停用')

                    print()

                print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
                print(f'總計: {len(recommendations)} 個課程可以立即執行')
                print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')

                # ===================================================================
                # 🆕 修改點 6: 步驟 2-4 結束階段追蹤
                # ===================================================================
                wrapper.end_phase("瀏覽器操作與掃描")

                # ===================================================================
                # 🆕 修改點 7: 步驟 3 - 加入排程（開始階段追蹤）
                # ===================================================================
                wrapper.start_phase("加入排程")

                # Step 8: 自動全部加入排程（不再詢問）
                print('[步驟 3/5] 正在加入排程...\n')

                added_count = 0
                skipped_count = 0

                for item in recommendations:
                    config_item = item['config']

                    # 檢查是否已經存在於排程中（去重）
                    is_duplicate = False
                    for existing in self.scheduled_courses:
                        # 判斷重複的邏輯
                        if config_item.get('course_type') == 'exam':
                            # 考試：比對 program_name + exam_name
                            if (
                                existing.get('program_name')
                                == config_item.get('program_name')
                                and existing.get('exam_name')
                                == config_item.get('exam_name')
                                and existing.get('course_type') == 'exam'
                            ):
                                is_duplicate = True
                                break
                        else:
                            # 一般課程：比對 program_name + lesson_name + course_id
                            if (
                                existing.get('program_name')
                                == config_item.get('program_name')
                                and existing.get('lesson_name')
                                == config_item.get('lesson_name')
                                and existing.get('course_id')
                                == config_item.get('course_id')
                            ):
                                is_duplicate = True
                                break

                    if is_duplicate:
                        skipped_count += 1
                        print(f'  ⚠️  跳過重複項目: {item["item_name"][:40]}...')
                    else:
                        self.scheduled_courses.append(config_item)
                        added_count += 1

                print(f'\n✓ 已將 {added_count} 個推薦課程加入排程')
                if skipped_count > 0:
                    print(f'  ⚠️  跳過 {skipped_count} 個重複項目\n')
                else:
                    print()

                # ===================================================================
                # 🆕 修改點 8: 步驟 3 結束階段追蹤
                # ===================================================================
                wrapper.end_phase("加入排程")

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

            # ===================================================================
            # 🆕 修改點 9: 步驟 5 - 執行排程（開始階段追蹤）
            # ===================================================================
            wrapper.start_phase("執行排程")

            print('\n[步驟 5/5] 正在執行排程...')
            print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')

            # 儲存排程
            self.save_schedule()

            # 執行 main.py
            print('\n啟動 main.py...\n')
            print('=' * 70)
            os.system('python main.py')
            print('=' * 70)

            # ===================================================================
            # 🆕 修改點 10: 步驟 5 結束階段追蹤
            # ===================================================================
            wrapper.end_phase("執行排程")

            # ===================================================================
            # 🆕 修改點 11: 執行後清理（開始階段追蹤）
            # ===================================================================
            wrapper.start_phase("執行後清理")

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
                'resource/plugins/stealth.min.js',
            ]

            for file_path in temp_files:
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        # 將技術性檔名轉為使用者友善的顯示名稱
                        display_name = file_path.replace(
                            'stealth.min.js', 'stealth mode file'
                        )
                        print(f'  ✓ 已刪除: {display_name}')
                    except OSError as e:
                        display_name = file_path.replace(
                            'stealth.min.js', 'stealth mode file'
                        )
                        print(f'  ✗ 刪除失敗 {display_name}: {e}')

            print('\n✓ 所有任務已完成！')

            # ===================================================================
            # 🆕 修改點 12: 執行後清理結束階段追蹤
            # ===================================================================
            wrapper.end_phase("執行後清理")

        # ===================================================================
        # 🆕 自動生成報告
        # with 區塊結束時，ExecutionWrapper 會自動：
        # 1. 結束程式計時
        # 2. 生成時間統計報告
        # 3. 保存報告到 reports/智能推薦/time_report_YYYYMMDD_HHMMSS.md
        # 4. 在控制台顯示報告摘要
        # ===================================================================

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

    def handle_hybrid_choice(self):
        """h 功能主選單 - 混合式時長發送/掃描"""
        print('\n' + '=' * 70)
        print('  h - 混合式時長發送功能')
        print('=' * 70)
        print('\n請選擇操作模式：')
        print('  1. 一般課程時長發送 - 掃描→發送→驗證差異')
        print('  2. 批量模式 - 課程+測驗批量發送時長')
        print('  3. 考試自動答題 - 只處理測驗課程')
        print('  q. 返回主選單')
        print('=' * 70)

        choice = input('\n請選擇 (1/2/3/q): ').strip().lower()

        if choice == '1':
            self._handle_hybrid_with_mode('duration')
        elif choice == '2':
            self._handle_hybrid_with_mode('batch')
        elif choice == '3':
            self._handle_hybrid_with_mode('exam')
        elif choice == 'q':
            print('\n返回主選單')
            return
        else:
            print('\n[X] 無效的選項')

    def _handle_hybrid_with_mode(self, mode: str):
        """統一處理混合模式（支援 Orchestrator 路由）

        Args:
            mode: 'duration', 'batch', 或 'exam'
        """
        # =====================================================================
        # Phase 3: Orchestrator 整合
        # =====================================================================
        if _use_orchestrators():
            self._handle_hybrid_orchestrator(mode)
            return

        # Legacy 路由
        if mode == 'duration':
            self.handle_hybrid_duration_send()
        elif mode == 'batch':
            self.handle_hybrid_batch_mode()
        elif mode == 'exam':
            self.handle_hybrid_exam_auto_answer()

    def _handle_hybrid_orchestrator(self, mode: str):
        """使用 Orchestrator 執行混合掃描"""
        try:
            from src.orchestrators import HybridScanOrchestrator, HybridMode

            mode_map = {
                'duration': HybridMode.DURATION,
                'batch': HybridMode.BATCH,
                'exam': HybridMode.EXAM,
            }

            config = _get_config()
            orchestrator = HybridScanOrchestrator(
                config,
                mode=mode_map.get(mode, HybridMode.DURATION)
            )

            result = orchestrator.execute(auto_select=False)

            if result.success:
                print('\n' + '=' * 70)
                print(f'  ✓ 混合掃描 ({mode}) 執行完成')
                print('=' * 70)
                print(f"  掃描 Payload 數: {result.data.get('payloads_count', 0)}")
                print(f"  已選擇課程數: {result.data.get('selected_count', 0)}")
                print(f"  成功發送數: {result.data.get('sent_count', 0)}")
                print(f"  驗證通過數: {result.data.get('verified_count', 0)}")
            else:
                print('\n' + '=' * 70)
                print(f'  ✗ 混合掃描 ({mode}) 執行失敗')
                print('=' * 70)
                print(f"  錯誤: {result.error}")

        except Exception as e:
            print(f'\n[錯誤] Orchestrator 執行失敗: {e}')
            print('嘗試使用 Legacy 模式...')
            from src.config.feature_flags import feature_enabled
            if feature_enabled('fallback_on_error'):
                if mode == 'duration':
                    self.handle_hybrid_duration_send()
                elif mode == 'batch':
                    self.handle_hybrid_batch_mode()
                elif mode == 'exam':
                    self.handle_hybrid_exam_auto_answer()
            else:
                raise

        input('\n按 Enter 返回主選單...')

    def handle_hybrid_duration_send(self):
        """h 選項 1 - 一般課程時長發送 (Legacy)

        完整流程:
        1. 登入與初始化
        2. Payload 捕獲掃描（掃描所有一般課程，排除考試）
        3. 互動選擇課程
        4. 提取通過條件與計算目標時長
        5. 使用 mitmproxy 發送目標時長 + 重刷 + 驗證時長
        6. 顯示差異報告
        """
        import os
        import json
        import time
        from pathlib import Path

        # ===== 顯示功能說明 =====
        print('\n' + '=' * 70)
        print('  h 選項 1 - 一般課程時長發送')
        print('=' * 70)
        print('\n此功能將執行：')
        print('  階段 1: 登入並掃描所有一般課程（排除考試）')
        print('  階段 2: 捕獲每個課程的完整 Payload（17 欄位）')
        print('  階段 3: 互動選單選擇要處理的課程')
        print('  階段 4: 提取通過條件並計算目標時長')
        print('  階段 5: 使用 mitmproxy 發送 + 重刷 + 驗證時長')
        print('  階段 6: 顯示差異報告')
        print('\n特點：')
        print('  - 完整 17 欄位 user-visits payload')
        print('  - 自動提取通過條件並計算目標時長')
        print('  - 自動跳過 Type 3 純考試課程（無時長要求）')
        print('  - 目標模式：直接設定為通過條件所需時長')
        print('  - 精確的前後時數比對')
        print('  - 互動式課程選擇')
        print('=' * 70)

        confirm = input('\n是否繼續？(y/n): ').strip().lower()
        if confirm != 'y':
            print('\n[取消] 返回主選單')
            input('\n按 Enter 返回主選單...')
            return

        # ===== 載入配置 =====
        from src.core.config_loader import ConfigLoader
        config = ConfigLoader('config/eebot.cfg')
        config.load()

        from src.utils.execution_wrapper import ExecutionWrapper

        with ExecutionWrapper(config, "一般課程時長發送") as wrapper:

            driver = None
            proxy = None
            driver_manager = None

            try:
                # ================================================================
                # 階段 1: 登入與初始化（參照 i 功能）
                # ================================================================
                wrapper.start_phase("登入與初始化")
                print('\n[階段 1/7] 登入與初始化...')
                print('━' * 70)

                from src.utils.stealth_extractor import StealthExtractor
                from src.core.driver_manager import DriverManager
                from src.core.cookie_manager import CookieManager
                from src.pages.login_page import LoginPage
                from src.pages.course_list_page import CourseListPage
                from src.pages.course_detail_page import CourseDetailPage

                # 初始化組件
                print('[初始化 1/5] 啟動瀏覽器自動化模式...')
                extractor = StealthExtractor()
                if not extractor.exists():
                    extractor.run()
                else:
                    print('  ✓ 瀏覽器自動化模式就緒')

                print('[初始化 2/5] 初始化核心元件...')
                driver_manager = DriverManager(config)
                cookie_manager = CookieManager(config.get('cookies_file'))
                print('  ✓ 核心元件已初始化')

                print('[初始化 3/5] 啟動瀏覽器...')
                driver = driver_manager.create_driver(use_proxy=False)
                print('  ✓ 瀏覽器已啟動')

                print('[初始化 4/5] 初始化頁面物件...')
                login_page = LoginPage(driver, cookie_manager)
                course_list_page = CourseListPage(driver)
                print('  ✓ 頁面物件已初始化')

                # 登入（with retry）
                print('[初始化 5/5] 登入系統...')
                max_retries = 3
                login_success = False

                for attempt in range(max_retries):
                    login_success = login_page.auto_login(
                        username=config.get('user_name'),
                        password=config.get('password'),
                        url=config.get('target_http'),
                    )

                    if login_success:
                        print('  ✓ 登入成功')
                        break
                    else:
                        if attempt < max_retries - 1:
                            print(f'  ⚠️  登入失敗，重試中... ({attempt + 1}/{max_retries})')
                            login_page.goto(config.get('target_http'))
                        else:
                            print('  ✗ 登入失敗，已達最大重試次數')

                if not login_success:
                    print('\n❌ 登入失敗，流程終止')
                    wrapper.end_phase("登入與初始化")
                    input('\n按 Enter 返回主選單...')
                    return

                # 前往我的課程
                print('\n[前往我的課程]...')
                course_list_page.goto_my_courses()
                time.sleep(5)  # 等待頁面載入
                print('  ✓ 已進入我的課程')

                wrapper.end_phase("登入與初始化")

                # ================================================================
                # 階段 2: 掃描課程並捕獲 Payload
                # ================================================================
                wrapper.start_phase("掃描課程並捕獲 Payload")
                print('\n[階段 2/7] 掃描課程並捕獲 Payload...')
                print('━' * 70)

                # 獲取所有課程計畫
                print('[掃描 1/4] 獲取課程列表...')
                programs = course_list_page.get_in_progress_programs()

                if not programs:
                    print('  ⚠️  未找到任何「修習中」的課程')
                    wrapper.end_phase("掃描課程並捕獲 Payload")
                    input('\n按 Enter 返回主選單...')
                    return

                print(f'  ✓ 找到 {len(programs)} 個課程計畫')

                # ✅ 修復：啟動 mitmproxy（使用統一攔截器，全程不重啟）
                print('\n[掃描 2/4] 啟動 mitmproxy（統一攔截器）...')

                from src.core.proxy_manager import ProxyManager
                from src.api.interceptors.manual_send_duration import ManualSendDurationInterceptor

                # ✨ 使用統一攔截器：同時支持 payload 捕獲和時長修改
                # 初始時 course_duration_map 為空（不修改任何時長），只捕獲 payload
                # 在 Stage 4 用戶選擇課程後，再使用 add_course() 動態添加配置
                unified_interceptor = ManualSendDurationInterceptor(
                    course_duration_map={},
                    use_target_mode=True  # 使用目標時長模式
                )
                proxy = ProxyManager(config, interceptors=[unified_interceptor])
                proxy.start()
                print('  ✓ Mitmproxy 已啟動（統一攔截器：payload 捕獲 + 時長修改）')
                print('  ✓ 全程保持運行，不會重啟（解決端口釋放問題）')

                # 重新啟動瀏覽器（使用 proxy）
                print('\n[掃描 3/4] 重新啟動瀏覽器（使用 proxy）...')
                driver.quit()
                driver = driver_manager.create_driver(use_proxy=True)

                # ✅ 修復：等待 mitmproxy 完全就緒（避免第一個請求 502）
                print('  ⏳ 等待 mitmproxy 完全初始化（SSL/TLS 證書服務）...')
                time.sleep(3)  # 給 mitmproxy 額外 3 秒初始化時間
                print('  ✓ Mitmproxy 已就緒')

                # 重新登入
                login_page = LoginPage(driver, cookie_manager)
                login_success = login_page.auto_login(
                    username=config.get('user_name'),
                    password=config.get('password'),
                    url=config.get('target_http'),
                )

                if not login_success:
                    print('  ✗ 重新登入失敗')
                    wrapper.end_phase("掃描課程並捕獲 Payload")
                    if proxy:
                        proxy.stop()
                    input('\n按 Enter 返回主選單...')
                    return

                print('  ✓ 重新登入成功（使用 proxy）')

                # 前往我的課程
                course_list_page = CourseListPage(driver)
                course_list_page.goto_my_courses()
                time.sleep(5)

                # ✅ 修復: 重新獲取課程計畫（使用新的 driver）
                # 原因: 舊的 programs 列表包含失效的 WebElement（屬於已關閉的 driver）
                print('\n[重新獲取課程列表]...')
                programs = course_list_page.get_in_progress_programs()
                print(f'  ✓ 已重新獲取 {len(programs)} 個課程計畫')

                # 提取 base_url（用於返回失敗時的備用導航）
                from urllib.parse import urlparse
                target_url = config.get('target_http')
                parsed = urlparse(target_url)
                base_url = f'{parsed.scheme}://{parsed.netloc}'

                # 訪問每個課程計畫以觸發 payload 捕獲
                print('\n[掃描 4/4] 訪問課程以捕獲 Payload...')
                print(f'  準備訪問 {len(programs)} 個課程計畫...')

                for i, program in enumerate(programs, 1):
                    program_name = program.get('name', f'課程 {i}')
                    print(f'\n  [{i}/{len(programs)}] {program_name[:50]}...')

                    # ✅ 修復: 使用 select_course_by_name 而不是直接點擊 WebElement
                    # 原因: 每次點擊後返回頁面會導致其他元素變成 stale
                    try:
                        # 使用課程名稱重新查找並點擊（自動處理 stale element）
                        course_list_page.select_course_by_name(program_name, delay=5.0)
                        print(f'      ✓ 已訪問')

                        # ✅ 修復: 使用雙重備援返回機制（參考 i 選項）
                        # 只在不是最後一個課程時才返回
                        if i < len(programs):
                            print(f'      → 返回課程列表...')
                            try:
                                # 方法 1: 使用返回按鈕
                                course_list_page.go_back_to_course_list()
                            except Exception as e1:
                                print(f'      [WARNING] 返回按鈕失敗，嘗試直接導航: {e1}')
                                try:
                                    # 方法 2: 直接導航
                                    driver.get(f'{base_url}/user/courses')
                                    time.sleep(3)
                                    print(f'      ✓ 已導航到課程列表')
                                except Exception as e2:
                                    print(f'      [ERROR] 導航失敗: {e2}')
                    except Exception as e:
                        print(f'      ✗ 無法點擊: {e}')
                        # 即使點擊失敗，也嘗試返回課程列表以繼續處理下一個
                        if i < len(programs):
                            try:
                                driver.get(f'{base_url}/user/courses')
                                time.sleep(3)
                            except Exception:
                                pass

                # ✅ 修復：獲取捕獲的 payloads（不停止 proxy，繼續保持運行）
                print('\n[獲取已捕獲的 Payload]...')
                captured_payloads = unified_interceptor.get_captured_payloads()
                print(f'  ✓ 已捕獲 {len(captured_payloads)} 個課程的 Payload')
                print('  ✓ Mitmproxy 保持運行（稍後在 Stage 5 使用）')

                if not captured_payloads:
                    print('  ⚠️  未捕獲到任何 Payload')
                    wrapper.end_phase("掃描課程並捕獲 Payload")
                    input('\n按 Enter 返回主選單...')
                    return

                # 構建課程數據結構（用於 CourseSelectionMenu）
                print('\n[構建課程數據]...')
                courses_data = []

                for course_id, payload in captured_payloads.items():
                    # 只處理一般課程（排除考試）
                    course_type = payload.get('course_type', 'course')
                    if course_type == 'exam':
                        continue

                    course_data = {
                        "api_course_id": str(course_id),
                        "program_name": payload.get('course_name', '未知課程'),
                        "course_code": payload.get('course_code', 'N/A'),
                        "course_name": payload.get('course_name', '未知'),
                        "required_minutes": 100,  # 預設值，可從 config 讀取
                        "payload": payload.copy(),
                        "item_type": "course"
                    }
                    courses_data.append(course_data)

                print(f'  ✓ 已構建 {len(courses_data)} 個一般課程數據')

                wrapper.end_phase("掃描課程並捕獲 Payload")

                if not courses_data:
                    print('\n  ⚠️  沒有找到一般課程（可能都是考試課程）')
                    input('\n按 Enter 返回主選單...')
                    return

                # ================================================================
                # 階段 3: 互動選擇課程
                # ================================================================
                wrapper.start_phase("互動選擇課程")
                print('\n[階段 3/7] 互動選擇課程...')
                print('━' * 70)

                from src.utils.course_selection_menu import CourseSelectionMenu

                selection_menu = CourseSelectionMenu(courses_data)
                selected_courses = selection_menu.run()

                if not selected_courses:
                    print('\n[已取消] 用戶取消選擇')
                    wrapper.end_phase("互動選擇課程")
                    input('\n按 Enter 返回主選單...')
                    return

                print(f'\n✓ 已選擇 {len(selected_courses)} 個課程')

                wrapper.end_phase("互動選擇課程")

                # ================================================================
                # 階段 4: 提取通過條件與計算目標時長
                # ================================================================
                wrapper.start_phase("提取通過條件與計算目標時長")
                print('\n[階段 4/7] 提取通過條件與計算目標時長...')
                print('━' * 70)

                # 停止 proxy，重新啟動瀏覽器（不使用 proxy）
                print('[準備掃描] 重新啟動瀏覽器（不使用 proxy）...')
                driver.quit()
                driver = driver_manager.create_driver(use_proxy=False)

                # 重新登入
                login_page = LoginPage(driver, cookie_manager)
                login_page.auto_login(
                    username=config.get('user_name'),
                    password=config.get('password'),
                    url=config.get('target_http'),
                )
                print('  ✓ 已重新登入')

                # 前往課程列表頁面
                course_list_page = CourseListPage(driver)
                course_list_page.goto_my_courses()
                time.sleep(5)
                print('  ✓ 已進入我的課程')

                # 提取 base_url（用於返回失敗時的備用導航）
                from urllib.parse import urlparse
                target_url = config.get('target_http')
                parsed = urlparse(target_url)
                base_url = f'{parsed.scheme}://{parsed.netloc}'

                # 掃描每個選中課程的通過條件
                durations_before = {}
                course_duration_map = {}  # 課程 ID -> 目標總時長（秒）
                courses_to_skip = []  # Type 3 課程（純考試，無時長要求）

                for i, course in enumerate(selected_courses, 1):
                    course_id = course.get('api_course_id')
                    program_name = course.get('program_name', f'課程 {i}')

                    print(f'\n  [{i}/{len(selected_courses)}] {program_name[:50]}...')

                    try:
                        # ✅ 修復：使用課程名稱進入課程計畫（與階段 2 相同）
                        print(f'      → 進入課程計畫...')
                        course_list_page.select_course_by_name(program_name, delay=3.0)
                        print(f'      ✓ 已進入課程計畫')

                        # 初始化課程詳情頁面
                        course_detail_page = CourseDetailPage(driver)

                        # 獲取第一個 module ID
                        module_id = course_detail_page.get_first_module_id()

                        if not module_id:
                            print(f'      ⚠️  無法獲取 module ID，跳過此課程')
                            courses_to_skip.append(course_id)
                        else:
                            # 提取通過條件
                            pass_req = course_detail_page.extract_pass_requirement(module_id)
                            required_minutes = pass_req.get('required_minutes')
                            required_score = pass_req.get('required_score')

                            # 判斷課程類型
                            if required_minutes is None and required_score is not None:
                                # Type 3: 純考試課程（只有成績要求，無時長要求）
                                print(f'      → Type 3: 純考試課程（需成績 {required_score} 分，無時長要求）')
                                print(f'      ⚠️  跳過此課程（不發送時長）')
                                courses_to_skip.append(course_id)
                            elif required_minutes is not None:
                                # Type 1 或 Type 2: 有時長要求

                                # ✅ 先提取當前已閱讀時數
                                current_read_time = course_detail_page.extract_current_read_time()
                                durations_before[course_id] = current_read_time
                                current_minutes = current_read_time.get('minutes') or 0

                                print(f'      → 需要時長: {required_minutes} 分鐘')
                                print(f'      → 當前已閱讀: {current_minutes} 分鐘')

                                if required_score:
                                    print(f'      → 需要成績: {required_score} 分 (Type 2)')
                                else:
                                    print(f'      → (Type 1)')

                                # ✅ 無論是否達標，都設定目標時長（用戶要求）
                                target_duration_seconds = required_minutes * 60
                                course_duration_map[course_id] = target_duration_seconds
                                course['target_duration'] = target_duration_seconds
                                course['required_minutes'] = required_minutes

                                if current_minutes >= required_minutes:
                                    print(f'      → 狀態: 已達標（仍會執行發送）')
                                    print(f'      → 將發送目標: {required_minutes} 分鐘 ({target_duration_seconds} 秒)')
                                else:
                                    print(f'      → 狀態: 未達標')
                                    print(f'      → 將發送目標: {required_minutes} 分鐘 ({target_duration_seconds} 秒)')
                                    print(f'      → 預計增加: {required_minutes - current_minutes} 分鐘')
                            else:
                                # 無法提取通過條件，跳過
                                print(f'      ⚠️  無法提取通過條件，跳過此課程')
                                courses_to_skip.append(course_id)

                        # ✅ 返回課程列表（準備處理下一個課程）
                        if i < len(selected_courses):
                            print(f'      → 返回課程列表...')
                            try:
                                # 方法 1: 使用返回按鈕
                                course_list_page.go_back_to_course_list()
                                print(f'      ✓ 已返回')
                            except Exception as e1:
                                print(f'      [WARNING] 返回按鈕失敗，嘗試直接導航: {e1}')
                                try:
                                    # 方法 2: 直接導航
                                    driver.get(f'{base_url}/user/courses')
                                    time.sleep(3)
                                    print(f'      ✓ 已導航到課程列表')
                                except Exception as e2:
                                    print(f'      [ERROR] 導航失敗: {e2}')

                    except Exception as e:
                        print(f'      ✗ 處理失敗: {e}')
                        courses_to_skip.append(course_id)
                        # 即使失敗也嘗試返回課程列表
                        if i < len(selected_courses):
                            try:
                                driver.get(f'{base_url}/user/courses')
                                time.sleep(3)
                            except Exception:
                                pass

                # 移除需要跳過的課程
                if courses_to_skip:
                    print(f'\n[過濾] 移除 {len(courses_to_skip)} 個不需發送時長的課程')
                    print(f'  原因: Type 3（純考試）或 無法提取通過條件')
                    selected_courses = [c for c in selected_courses if c.get('api_course_id') not in courses_to_skip]

                if not selected_courses:
                    print('\n  ⚠️  沒有需要發送時長的課程')
                    wrapper.end_phase("提取通過條件與計算目標時長")
                    input('\n按 Enter 返回主選單...')
                    return

                print(f'\n✓ 掃描完成，{len(selected_courses)} 個課程需要發送時長')

                # ✅ 修復：動態配置統一攔截器（不需要重啟 proxy）
                print('\n[配置 Mitmproxy 攔截器]...')
                for course_id, target_seconds in course_duration_map.items():
                    unified_interceptor.add_course(course_id, target_seconds)
                    course_info = next((c for c in selected_courses if c.get('api_course_id') == course_id), None)
                    if course_info:
                        print(f'  → {course_info.get("program_name", "")[:40]}: {target_seconds//60} 分鐘')
                print('✓ Mitmproxy 攔截器已配置完成（無需重啟）')
                print('✓ Proxy 保持運行，準備發送時長')

                wrapper.end_phase("提取通過條件與計算目標時長")

                # ================================================================
                # 階段 5: 使用 Mitmproxy 發送目標時長
                # ================================================================
                wrapper.start_phase("使用 Mitmproxy 發送目標時長")
                print('\n[階段 5/7] 使用 Mitmproxy 發送目標時長...')
                print('━' * 70)

                # ✅ 修復：Proxy 已在 Stage 2 啟動並配置，無需重啟
                print('\n[確認 Mitmproxy 狀態]...')
                print('  ✓ Mitmproxy 自 Stage 2 起持續運行')
                print('  ✓ 攔截器已配置完成（目標時長模式）')

                # ✅ 關鍵修復：重啟瀏覽器並連接 proxy
                # Stage 4 的瀏覽器是 use_proxy=False，需要重新連接 proxy
                print('\n[重啟瀏覽器] 連接 proxy...')
                driver.quit()
                driver = driver_manager.create_driver(use_proxy=True)
                print('  ✓ 瀏覽器已連接 proxy')

                print('\n[重新登入系統]...')
                login_page = LoginPage(driver, cookie_manager)
                login_success = login_page.auto_login(
                    username=config.get('user_name'),
                    password=config.get('password'),
                    url=config.get('target_http'),
                )

                if not login_success:
                    print('  ✗ 重新登入失敗')
                    wrapper.end_phase("使用 Mitmproxy 發送目標時長")
                    if proxy:
                        proxy.stop()
                    input('\n按 Enter 返回主選單...')
                    return

                print('  ✓ 重新登入成功（使用 proxy）')

                # 訪問每個課程頁面，觸發 mitmproxy 攔截並驗證
                print('\n[訪問課程] 觸發 mitmproxy 攔截、修改時長並驗證...')

                durations_after = {}  # 儲存發送後的時長

                for i, course in enumerate(selected_courses, 1):
                    course_id = course.get('api_course_id')
                    program_name = course.get('program_name', f'課程 {i}')
                    target_minutes = course.get('required_minutes', 0)

                    print(f'\n  [{i}/{len(selected_courses)}] {program_name[:50]}...')
                    print(f'      目標時長: {target_minutes} 分鐘')

                    # 步驟 1: 前往課程頁面（會觸發 user-visits 請求）
                    course_url = f"{config.get('target_http')}/course/{course_id}/content#/"
                    driver.get(course_url)
                    time.sleep(5)  # 等待 user-visits 請求觸發並被攔截
                    print(f'      ✓ 已訪問並觸發攔截')

                    # 步驟 2: 重刷頁面（可能觸發第二次 user-visits）
                    print(f'      → 重刷頁面...')
                    driver.refresh()
                    time.sleep(5)  # 延長等待時間，確保請求完成
                    print(f'      ✓ 已重刷（如攔截器有輸出，表示觸發第二次請求）')

                    # 步驟 3: 提取當前已閱讀時數（驗證時長增加）
                    print(f'      → 驗證時長...')
                    course_detail_page = CourseDetailPage(driver)
                    current_read_time = course_detail_page.extract_current_read_time()
                    durations_after[course_id] = current_read_time

                    current_minutes = current_read_time.get('minutes') or 0
                    before_data = durations_before.get(course_id, {})
                    before_minutes = before_data.get('minutes') if isinstance(before_data, dict) else (before_data or 0)

                    diff = current_minutes - before_minutes
                    print(f'      發送前: {before_minutes} 分鐘')
                    print(f'      發送後: {current_minutes} 分鐘')
                    print(f'      增加量: {diff:+d} 分鐘 {"✓" if diff > 0 else "✗"}')

                # 停止 mitmproxy
                print('\n[停止 Mitmproxy]...')
                proxy.stop()
                proxy = None
                print('  ✓ Mitmproxy 已停止')

                print(f'\n✓ 發送與驗證完成')

                wrapper.end_phase("使用 Mitmproxy 發送目標時長")

                # ================================================================
                # 階段 6: 顯示差異報告
                # ================================================================
                wrapper.start_phase("生成報告")
                print('\n[階段 6/6] 生成差異報告...')
                print('━' * 70)

                print('\n' + '=' * 70)
                print('  時長增加報告')
                print('=' * 70)

                total_increase = 0
                success_count = 0

                for i, course in enumerate(selected_courses, 1):
                    course_id = course.get('api_course_id')
                    program_name = course.get('program_name', f'課程 {i}')

                    # 從字典中提取分鐘數（extract_current_read_time 返回字典）
                    before_data = durations_before.get(course_id, {})
                    after_data = durations_after.get(course_id, {})

                    # 如果是字典，提取 minutes；如果是數字，直接使用
                    if isinstance(before_data, dict):
                        before = before_data.get('minutes') or 0
                    else:
                        before = before_data or 0

                    if isinstance(after_data, dict):
                        after = after_data.get('minutes') or 0
                    else:
                        after = after_data or 0

                    diff = after - before

                    print(f'\n[{i}] {program_name[:55]}')
                    print(f'    發送前: {before} 分鐘')
                    print(f'    發送後: {after} 分鐘')
                    print(f'    增加量: {diff:+d} 分鐘 {"✓" if diff > 0 else "✗"}')

                    total_increase += diff
                    if diff > 0:
                        success_count += 1

                print('\n' + '=' * 70)
                print(f'總結: {success_count}/{len(selected_courses)} 個課程時長增加成功')
                print(f'總增加時長: {total_increase} 分鐘 ({total_increase / 60:.1f} 小時)')
                print('=' * 70)

                wrapper.end_phase("生成報告")

                print('\n✅ 一般課程時長發送完成！')

            except Exception as e:
                print(f'\n❌ 執行過程發生錯誤: {e}')
                import traceback
                traceback.print_exc()

            finally:
                # 清理資源
                if proxy:
                    try:
                        proxy.stop()
                    except:
                        pass
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass

            input('\n按 Enter 返回主選單...')

    def handle_hybrid_batch_mode(self):
        """h 選項 2 - 混合批量模式

        完整流程:
        1. 登入與初始化
        2. 掃描所有課程和考試（使用 get_program_courses_and_exams）
        3. 用戶選擇（支持 all 選項）
        4. 分離一般課程和考試
        5. 執行 h1 邏輯（一般課程）- 如果有選中
        6. 執行 h3 邏輯（考試課程）- 如果有選中
        7. 生成綜合報告
        """
        import os
        import json
        import time
        from pathlib import Path

        # ===== 顯示功能說明 =====
        print('\n' + '=' * 70)
        print('  h 選項 2 - 混合批量模式')
        print('=' * 70)
        print('\n此功能將執行：')
        print('  階段 1: 登入並掃描所有課程（一般課程 + 考試）')
        print('  階段 2: 深度掃描每個課程計畫（提取子課程和考試）')
        print('  階段 3: 顯示選擇選單（支持 all 選項）')
        print('  階段 4: 分離一般課程和考試')
        print('  階段 5: 執行一般課程處理（h1 邏輯）')
        print('  階段 6: 執行考試處理（h3 邏輯）')
        print('  階段 7: 生成綜合報告')
        print('\n特點：')
        print('  - 一般課程 + 考試課程混合處理')
        print('  - 支持用戶選擇（包括 all）')
        print('  - 智能執行：先 h1 再 h3')
        print('  - 動態題庫切換（每個考試加載對應題庫）')
        print('  - 考試截圖（before/after，滾動至底部）')
        print('=' * 70)

        confirm = input('\n是否繼續？(y/n): ').strip().lower()
        if confirm != 'y':
            print('\n[取消] 返回主選單')
            input('\n按 Enter 返回主選單...')
            return

        # ===== 載入配置 =====
        from src.core.config_loader import ConfigLoader
        config = ConfigLoader('config/eebot.cfg')
        config.load()

        from src.utils.execution_wrapper import ExecutionWrapper

        with ExecutionWrapper(config, "混合批量模式") as wrapper:

            driver = None
            proxy = None
            driver_manager = None
            payload_interceptor = None
            exam_interceptor = None

            try:
                # ================================================================
                # 階段 1: 登入與初始化
                # ================================================================
                wrapper.start_phase("登入與初始化")
                print('\n[階段 1/7] 登入與初始化...')
                print('━' * 70)

                from src.utils.stealth_extractor import StealthExtractor
                from src.core.driver_manager import DriverManager
                from src.core.cookie_manager import CookieManager
                from src.pages.login_page import LoginPage
                from src.pages.course_list_page import CourseListPage
                from src.pages.course_detail_page import CourseDetailPage

                # 初始化組件
                print('[初始化 1/5] 啟動瀏覽器自動化模式...')
                extractor = StealthExtractor()
                if not extractor.exists():
                    extractor.run()
                else:
                    print('  ✓ 瀏覽器自動化模式就緒')

                print('[初始化 2/5] 初始化核心元件...')
                driver_manager = DriverManager(config)
                cookie_manager = CookieManager(config.get('cookies_file'))
                print('  ✓ 核心元件已初始化')

                print('[初始化 3/5] 啟動瀏覽器...')
                driver = driver_manager.create_driver(use_proxy=False)
                print('  ✓ 瀏覽器已啟動')

                print('[初始化 4/5] 初始化頁面物件...')
                login_page = LoginPage(driver, cookie_manager)
                course_list_page = CourseListPage(driver)
                print('  ✓ 頁面物件已初始化')

                # 登入（with retry）
                print('[初始化 5/5] 登入系統...')
                max_retries = 3
                login_success = False

                for attempt in range(max_retries):
                    login_success = login_page.auto_login(
                        username=config.get('user_name'),
                        password=config.get('password'),
                        url=config.get('target_http'),
                    )

                    if login_success:
                        print('  ✓ 登入成功')
                        break
                    else:
                        if attempt < max_retries - 1:
                            print(f'  ⚠️  登入失敗，重試中... ({attempt + 1}/{max_retries})')
                            login_page.goto(config.get('target_http'))
                        else:
                            print('  ✗ 登入失敗，已達最大重試次數')

                if not login_success:
                    print('\n❌ 登入失敗，流程終止')
                    wrapper.end_phase("登入與初始化")
                    input('\n按 Enter 返回主選單...')
                    return

                # 前往我的課程
                print('\n[前往我的課程]...')
                course_list_page.goto_my_courses()
                time.sleep(5)  # 等待頁面載入
                print('  ✓ 已進入我的課程')

                wrapper.end_phase("登入與初始化")

                # ================================================================
                # Helper Function: 等待端口釋放
                # ================================================================
                def _wait_for_port_release(proxy, port=8080, max_wait=30):
                    """
                    等待 mitmproxy 完全釋放端口

                    Args:
                        proxy: ProxyManager 實例
                        port: 端口號（默認 8080）
                        max_wait: 最大等待時間（秒，默認 30）
                    """
                    import socket

                    print(f'  → 等待端口 {port} 釋放...')

                    # 等待線程終止
                    if proxy.thread and proxy.thread.is_alive():
                        proxy.thread.join(timeout=10)
                        if proxy.thread.is_alive():
                            print(f'  ⚠️  線程未在 10 秒內終止')

                    # 檢查端口是否停止監聽（通過嘗試連接）
                    # 如果連接失敗（Connection refused），說明端口已釋放
                    start_time = time.time()
                    attempt = 0
                    shown_waiting_msg = False

                    while time.time() - start_time < max_wait:
                        attempt += 1
                        try:
                            # 嘗試連接到端口
                            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            test_socket.settimeout(0.5)
                            result = test_socket.connect_ex(('127.0.0.1', port))
                            test_socket.close()

                            if result != 0:
                                # 連接失敗 -> 端口已釋放
                                elapsed = time.time() - start_time
                                print(f'  ✓ 端口已釋放（耗時 {elapsed:.1f} 秒，{attempt} 次檢查）')
                                return True
                            else:
                                # 連接成功 -> 端口仍在監聽
                                if not shown_waiting_msg:
                                    print(f'  → 端口仍被占用，等待釋放...')
                                    shown_waiting_msg = True
                                time.sleep(1)

                        except Exception as e:
                            # 連接異常也視為端口已釋放
                            elapsed = time.time() - start_time
                            print(f'  ✓ 端口已釋放（耗時 {elapsed:.1f} 秒，{attempt} 次檢查）')
                            return True

                    # 超時 - 但繼續執行（可能 Stage 6 會自動處理）
                    elapsed = time.time() - start_time
                    print(f'  ⚠️  等待 {elapsed:.0f} 秒後超時，但將繼續執行')
                    print(f'  ℹ️  如果 Stage 6 啟動失敗，請手動重啟程式')
                    return False

                # ================================================================
                # 階段 2: 掃描課程並捕獲 Payload（分兩階段）
                # ================================================================
                wrapper.start_phase("掃描課程並捕獲 Payload")
                print('\n[階段 2/7] 掃描課程並捕獲 Payload...')
                print('━' * 70)

                # 獲取所有課程計畫
                print('[掃描 1/6] 獲取課程列表...')
                programs = course_list_page.get_in_progress_programs()

                if not programs:
                    print('  ⚠️  未找到任何「修習中」的課程')
                    wrapper.end_phase("掃描課程並捕獲 Payload")
                    input('\n按 Enter 返回主選單...')
                    return

                print(f'  ✓ 找到 {len(programs)} 個課程計畫')

                # 提取 base_url
                from urllib.parse import urlparse
                target_url = config.get('target_http')
                parsed = urlparse(target_url)
                base_url = f'{parsed.scheme}://{parsed.netloc}'

                # ================================================================
                # 階段 2A: 快速掃描（不使用 mitmproxy）- 收集課程結構信息
                # ================================================================
                print('\n[掃描 2/6] 快速掃描課程結構（不使用 proxy）...')
                print(f'  準備掃描 {len(programs)} 個課程計畫...')

                course_structure = []  # 記錄每個課程計畫的結構
                all_exam_courses = []  # 收集所有測驗
                import re

                for i, program in enumerate(programs, 1):
                    program_name = program.get('name', f'課程 {i}')
                    print(f'\n  [{i}/{len(programs)}] {program_name[:50]}...')

                    try:
                        # 使用 get_program_courses_and_exams() 獲取子課程和考試
                        result = course_list_page.get_program_courses_and_exams(program_name)

                        courses = result.get('courses', [])
                        exams = result.get('exams', [])

                        # 提取課程 ID（從當前 URL）
                        current_url = driver.current_url
                        course_id_match = re.search(r'/course/(\d+)', current_url)
                        course_id = course_id_match.group(1) if course_id_match else None

                        print(f'      ✓ 一般課程: {len(courses)} 個, 考試: {len(exams)} 個')

                        # 記錄課程結構
                        if courses:
                            # 只記錄第一個一般課程
                            first_course = courses[0]

                            # 提取通過條件（需要時長）
                            course_detail_page = CourseDetailPage(driver)
                            module_id = course_detail_page.get_first_module_id()
                            required_minutes = 0

                            if module_id:
                                pass_requirement = course_detail_page.extract_pass_requirement(module_id)
                                required_minutes = pass_requirement.get('required_minutes', 0) or 0

                            course_structure.append({
                                "program_name": program_name,
                                "first_course_name": first_course['name'],
                                "api_course_id": course_id,
                                "required_minutes": required_minutes
                            })

                        # 收集所有測驗（修復：使用 exam_name 而不是 item_name）
                        for exam in exams:
                            exam_data = {
                                "program_name": program_name,
                                "exam_name": exam['name'],
                                "api_course_id": course_id,
                                "item_type": "exam"
                            }
                            all_exam_courses.append(exam_data)

                        # 返回課程列表（如果不是最後一個）
                        if i < len(programs):
                            try:
                                course_list_page.go_back_to_course_list()
                                time.sleep(2)
                            except Exception as e1:
                                driver.get(f'{base_url}/user/courses')
                                time.sleep(3)

                    except Exception as e:
                        print(f'      ✗ 掃描失敗: {e}')
                        # 嘗試恢復
                        if i < len(programs):
                            try:
                                driver.get(f'{base_url}/user/courses')
                                time.sleep(3)
                            except Exception:
                                pass
                        continue

                print(f'\n✓ 快速掃描完成')
                print(f'  - 需要 payload 的課程: {len(course_structure)} 個')
                print(f'  - 測驗: {len(all_exam_courses)} 個')

                # ================================================================
                # 階段 2B: Payload 捕獲（使用 mitmproxy）
                # ================================================================
                all_general_courses = []

                if course_structure:
                    print('\n[掃描 3/6] 啟動 mitmproxy（Payload 捕獲 + 考試答題）...')

                    from src.core.proxy_manager import ProxyManager
                    from src.api.interceptors.payload_capture import PayloadCaptureInterceptor
                    from src.api.interceptors.exam_auto_answer import ExamAutoAnswerInterceptor

                    # ✅ 關鍵改進：同時創建兩個 interceptor，但考試答題先禁用
                    # 初始化題庫服務（考試需要）
                    from src.services.question_bank import QuestionBankService
                    from src.services.answer_matcher import AnswerMatcher
                    question_bank_service = QuestionBankService(config)
                    answer_matcher = AnswerMatcher(confidence_threshold=0.85)

                    payload_interceptor = PayloadCaptureInterceptor()
                    exam_interceptor = ExamAutoAnswerInterceptor(
                        question_bank_service=question_bank_service,
                        answer_matcher=answer_matcher,
                        enable=False  # 先禁用，Stage 6 再啟用
                    )

                    # 一個 mitmproxy，兩個 interceptor
                    proxy = ProxyManager(config, interceptors=[payload_interceptor, exam_interceptor])
                    proxy.start()
                    print('  ✓ Mitmproxy 已啟動（端口 8080）')
                    print('  ℹ️  Payload 捕獲：啟用')
                    print('  ℹ️  考試答題：禁用（Stage 6 再啟用）')

                    # 重新啟動瀏覽器（使用 proxy）
                    print('\n[掃描 4/6] 重新啟動瀏覽器（使用 proxy）...')
                    driver.quit()
                    driver = driver_manager.create_driver(use_proxy=True)
                    time.sleep(3)

                    # 重新登入
                    login_page = LoginPage(driver, cookie_manager)
                    login_success = login_page.auto_login(
                        username=config.get('user_name'),
                        password=config.get('password'),
                        url=config.get('target_http'),
                    )

                    if not login_success:
                        print('  ✗ 重新登入失敗')
                        if proxy:
                            proxy.stop()
                        wrapper.end_phase("掃描課程並捕獲 Payload")
                        input('\n按 Enter 返回主選單...')
                        return

                    print('  ✓ 重新登入成功（使用 proxy）')

                    # 訪問需要 payload 的課程（參照 h1 方式）
                    print('\n[掃描 5/6] 訪問課程以捕獲 Payload...')
                    print(f'  準備訪問 {len(course_structure)} 個課程...')

                    for i, course_info in enumerate(course_structure, 1):
                        program_name = course_info['program_name']
                        first_course_name = course_info['first_course_name']
                        course_id = course_info['api_course_id']

                        print(f'\n  [{i}/{len(course_structure)}] {program_name[:40]}...')
                        print(f'      → 目標: {first_course_name[:40]}...')

                        try:
                            # 前往課程頁面
                            course_url = f"{config.get('target_http')}/course/{course_id}/content#/"
                            driver.get(course_url)
                            time.sleep(5)

                            # 點擊第一個一般課程
                            course_detail_page = CourseDetailPage(driver)
                            course_detail_page.select_lesson_by_name(first_course_name, delay=3.0)
                            time.sleep(3)
                            print(f'      ✓ 已訪問並觸發 payload')

                        except Exception as e:
                            print(f'      ✗ 無法訪問: {e}')

                    # ✅ 不停止 mitmproxy！改為禁用 payload 捕獲
                    print('\n[掃描 6/6] 禁用 Payload 捕獲（保持 mitmproxy 運行）...')
                    if payload_interceptor:
                        captured_payloads = payload_interceptor.get_captured_payloads()
                        payload_interceptor.disable_capture()
                        print(f'  ✓ 已捕獲 {len(captured_payloads)} 個 payload')
                    else:
                        captured_payloads = {}
                        print('  ⚠️  payload_interceptor 未初始化')
                    print(f'  ℹ️  Mitmproxy 保持運行（端口 8080）')

                    # 構建一般課程數據（修復：使用主課程 ID 作為映射鍵）
                    # 需要將 payload 與 course_structure 的信息合併
                    course_structure_map = {
                        info['api_course_id']: info
                        for info in course_structure
                        if info.get('api_course_id')  # 只包含有 ID 的項目
                    }

                    for course_code, payload in captured_payloads.items():
                        # 從 payload 獲取主課程 ID
                        main_course_id = str(payload.get('course_id', ''))
                        course_name = payload.get('course_name', '未知')

                        # 使用主課程 ID 查找對應的課程結構信息
                        structure_info = course_structure_map.get(main_course_id, {})

                        # 如果找不到，嘗試使用子課程 ID
                        if not structure_info:
                            structure_info = course_structure_map.get(str(course_code), {})

                        course_data = {
                            "api_course_id": main_course_id or str(course_code),  # 主課程 ID
                            "program_name": course_name,  # 主課程計畫名稱
                            "course_name": course_name,  # 子課程名稱
                            "course_code": payload.get('course_code', 'N/A'),  # 子課程 ID
                            "required_minutes": structure_info.get('required_minutes', 0),  # 需要時長
                            "payload": payload.copy(),
                            "item_type": "course"
                        }
                        all_general_courses.append(course_data)
                else:
                    print('\n[跳過 Payload 捕獲] 沒有一般課程需要 payload')

                print(f'\n✓ 掃描完成')
                print(f'  - 一般課程總數: {len(all_general_courses)} 個（來自 payload 捕獲）')
                print(f'  - 考試總數: {len(all_exam_courses)} 個（來自 DOM 提取）')

                if not all_general_courses and not all_exam_courses:
                    print('\n  ⚠️  未找到任何課程或考試')
                    wrapper.end_phase("掃描課程並捕獲 Payload")
                    input('\n按 Enter 返回主選單...')
                    return

                wrapper.end_phase("掃描課程並捕獲 Payload")

                # ================================================================
                # 階段 3: 顯示選擇選單
                # ================================================================
                wrapper.start_phase("課程選擇")
                print('\n[階段 3/7] 課程選擇選單...')
                print('━' * 70)

                # 構建選擇列表（一般課程 + 考試）
                all_items = all_general_courses + all_exam_courses

                # 為每個項目添加顯示標籤（修復：處理不同的字段名稱）
                for item in all_items:
                    item_type_label = "【考試】" if item['item_type'] == 'exam' else "【課程】"

                    # 根據類型選擇正確的名稱字段
                    if item['item_type'] == 'exam':
                        item_name = item.get('exam_name', '未知')
                    else:
                        item_name = item.get('course_name', '未知')

                    item['display_name'] = f"{item_type_label} {item['program_name']} - {item_name}"

                print(f'\n  共找到 {len(all_items)} 個項目：')
                print(f'    - 一般課程: {len(all_general_courses)} 個')
                print(f'    - 考試: {len(all_exam_courses)} 個')

                # 顯示選擇選單
                from src.utils.course_selection_menu import CourseSelectionMenu
                selection_menu = CourseSelectionMenu(all_items)
                selected_items = selection_menu.run()

                if not selected_items:
                    print('\n  ⚠️  未選擇任何項目')
                    wrapper.end_phase("課程選擇")
                    input('\n按 Enter 返回主選單...')
                    return

                print(f'\n  ✓ 已選擇 {len(selected_items)} 個項目')

                wrapper.end_phase("課程選擇")

                # ================================================================
                # 階段 4: 分離選中項目
                # ================================================================
                wrapper.start_phase("分離選中項目")
                print('\n[階段 4/7] 分離選中項目...')
                print('━' * 70)

                # 分離一般課程和考試
                selected_general = [item for item in selected_items if item['item_type'] == 'course']
                selected_exams = [item for item in selected_items if item['item_type'] == 'exam']

                print(f'  ✓ 已分離選中項目')
                print(f'    - 一般課程: {len(selected_general)} 個')
                print(f'    - 考試: {len(selected_exams)} 個')

                # 確定執行順序
                if selected_general and selected_exams:
                    print(f'\n  執行順序: 先處理一般課程，再處理考試')
                elif selected_general:
                    print(f'\n  只處理一般課程（h1 邏輯）')
                elif selected_exams:
                    print(f'\n  只處理考試（h3 邏輯）')

                wrapper.end_phase("分離選中項目")

                # ================================================================
                # 階段 5: 執行一般課程處理（h1 邏輯）
                # ================================================================
                durations_before = {}
                durations_after = {}

                if selected_general:
                    wrapper.start_phase("處理一般課程")
                    print('\n[階段 5/7] 處理一般課程（h1 邏輯）...')
                    print('━' * 70)
                    print(f'  將處理 {len(selected_general)} 個一般課程')
                    print(f'  ℹ️  使用 Stage 2 已捕獲的 payloads')

                    # ===== 5.1: 掃描時數（Before） =====
                    print('\n[5.1] 掃描時數（Before）...')

                    # 重新啟動瀏覽器（不使用 proxy）
                    driver.quit()
                    driver = driver_manager.create_driver(use_proxy=False)

                    # 重新登入
                    login_page = LoginPage(driver, cookie_manager)
                    login_page.auto_login(
                        username=config.get('user_name'),
                        password=config.get('password'),
                        url=config.get('target_http'),
                    )

                    # 掃描每個課程的已閱讀時數
                    for i, course in enumerate(selected_general, 1):
                        course_code = course.get('course_code', 'N/A')
                        program_name = course.get('program_name', f'課程 {i}')
                        item_name = course.get('item_name', '未知')

                        print(f'  [{i}/{len(selected_general)}] {program_name[:50]}...')

                        # 從 payload 中獲取 course_id
                        payload = course.get('payload', {})
                        course_id = payload.get('course_id', None)

                        if not course_id:
                            print(f'      ⚠️  無 course_id，跳過')
                            continue

                        course_url = f"{config.get('target_http')}/course/{course_id}/content#/"
                        driver.get(course_url)
                        time.sleep(3)
                        wrapper.record_delay(3.0, f'載入課程頁面: {item_name[:20]}')

                        course_detail_page = CourseDetailPage(driver)
                        read_time_data = course_detail_page.extract_current_read_time()
                        current_minutes = read_time_data.get('minutes', 0)

                        durations_before[course_code] = current_minutes
                        print(f'      當前時數: {current_minutes} 分鐘')

                    # ===== 5.2: 發送修改後的 Payload =====
                    print('\n[5.2] 發送修改後的 Payload...')

                    duration_increase = config.get_int('visit_duration_increase', 6000)
                    print(f'  配置: 增加 {duration_increase} 秒 ({duration_increase//60} 分鐘)')

                    # 獲取認證信息
                    cookies_dict = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}
                    headers = {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'User-Agent': driver.execute_script("return navigator.userAgent"),
                        'Referer': config.get('target_http') + '/learning/my-courses'
                    }

                    import requests
                    api_url = config.get('target_http') + '/statistics/api/user-visits'
                    success_count = 0
                    failed_count = 0

                    for i, course in enumerate(selected_general, 1):
                        program_name = course.get('program_name', f'課程 {i}')
                        item_name = course.get('item_name', '未知')

                        print(f'\n  [{i}/{len(selected_general)}] {program_name[:40]} - {item_name[:40]}...')

                        # ✅ 開始追蹤此課程
                        wrapper.start_item(item_name, program_name, item_type='course')

                        # 使用已捕獲的 payload
                        payload = course.get('payload')
                        if not payload:
                            print(f'      ✗ 無 payload，跳過')
                            failed_count += 1
                            wrapper.end_item()
                            continue

                        # 修改 visit_duration
                        modified_payload = payload.copy()
                        original_duration = modified_payload.get('visit_duration', 0)
                        modified_payload['visit_duration'] = original_duration + duration_increase

                        print(f'      發送時長: {modified_payload["visit_duration"]} 秒 (+{duration_increase})')

                        try:
                            response = requests.post(
                                api_url,
                                json=modified_payload,
                                cookies=cookies_dict,
                                headers=headers,
                                timeout=10,
                                verify=False
                            )

                            if response.status_code in (200, 204):
                                print(f'      ✓ 發送成功 (HTTP {response.status_code})')
                                success_count += 1
                            else:
                                print(f'      ✗ 發送失敗 (HTTP {response.status_code})')
                                failed_count += 1

                        except Exception as e:
                            print(f'      ✗ 發送失敗: {e}')
                            failed_count += 1

                        time.sleep(1)
                        wrapper.record_delay(1.0, '請求間隔')

                        # ✅ 結束追蹤此課程
                        wrapper.end_item()

                    print(f'\n  ✓ 發送完成: {success_count} 成功, {failed_count} 失敗')

                    # ===== 5.3: 掃描時數（After） =====
                    print('\n[5.3] 掃描時數（After）...')

                    for i, course in enumerate(selected_general, 1):
                        course_code = course.get('course_code', 'N/A')
                        program_name = course.get('program_name', f'課程 {i}')

                        print(f'  [{i}/{len(selected_general)}] {program_name[:50]}...')

                        # 從 payload 中獲取 course_id
                        payload = course.get('payload', {})
                        course_id = payload.get('course_id', None)

                        if not course_id:
                            print(f'      ⚠️  無 course_id，跳過')
                            continue

                        course_url = f"{config.get('target_http')}/course/{course_id}/content#/"
                        driver.get(course_url)
                        time.sleep(3)

                        course_detail_page = CourseDetailPage(driver)
                        read_time_data = course_detail_page.extract_current_read_time()
                        current_minutes = read_time_data.get('minutes', 0)

                        durations_after[course_code] = current_minutes
                        print(f'      當前時數: {current_minutes} 分鐘')

                    print(f'\n✓ 一般課程處理完成')
                    wrapper.end_phase("處理一般課程")
                else:
                    print('\n[跳過階段 5] 未選中一般課程')


                # ================================================================
                # 階段 6: 執行考試處理（h3 邏輯）
                # ================================================================
                exam_results = {}

                if selected_exams:
                    wrapper.start_phase("處理考試")
                    print('\n[階段 6/7] 處理考試（h3 邏輯）...')
                    print('━' * 70)
                    print(f'  將處理 {len(selected_exams)} 個考試')

                    # ✅ 關鍵修復：Stage 5 使用 use_proxy=False，需要重啟瀏覽器使用 proxy
                    print('\n[6.1] 重啟瀏覽器（啟用 proxy 模式）...')

                    # 關閉 Stage 5 的無 proxy 瀏覽器
                    try:
                        driver.quit()
                        print('  ✓ 已關閉 Stage 5 瀏覽器（無 proxy）')
                    except Exception:
                        pass

                    # 重新啟動瀏覽器（使用 proxy）
                    driver = driver_manager.create_driver(use_proxy=True)
                    print('  ✓ 已啟動新瀏覽器（使用 proxy 127.0.0.1:8080）')

                    # 重新登入
                    login_page = LoginPage(driver, cookie_manager)
                    login_page.auto_login(
                        username=config.get('user_name'),
                        password=config.get('password'),
                        url=config.get('target_http'),
                    )
                    print('  ✓ 已重新登入')

                    print('\n[6.2] 啟用考試自動答題模式...')
                    if exam_interceptor is None:
                        print('  ✗ 錯誤：exam_interceptor 未初始化')
                        raise RuntimeError("exam_interceptor not initialized")

                    exam_interceptor.enable = True
                    print('  ✓ 考試答題攔截器已啟用')

                    # 初始化頁面物件
                    from src.pages.exam_detail_page import ExamDetailPage
                    from src.pages.exam_answer_page import ExamAnswerPage

                    # 創建截圖目錄
                    screenshot_dir = Path('reports/exam_screenshots')
                    screenshot_dir.mkdir(parents=True, exist_ok=True)

                    # ===== 6.3: 處理每個考試 =====
                    print('\n[6.3] 處理每個考試...')

                    for i, exam in enumerate(selected_exams, 1):
                        exam_id = exam.get('api_course_id')
                        program_name = exam.get('program_name', f'考試 {i}')
                        exam_name = exam.get('exam_name', '未知考試')

                        print(f'\n  [{i}/{len(selected_exams)}] {program_name[:40]} - {exam_name[:40]}...')

                        # ✅ 開始追蹤此考試
                        wrapper.start_item(exam_name, program_name, item_type='exam')

                        # 重置 interceptor 統計（每個考試獨立統計）
                        exam_interceptor.reset_stats()

                        # ✅ 動態切換題庫
                        print(f'      → 載入題庫: {program_name[:40]}...')
                        question_count = question_bank_service.load_question_bank(program_name)
                        if question_count > 0:
                            print(f'         ✓ 題庫已載入: {question_count} 題')
                        else:
                            print(f'         ⚠️  題庫載入失敗或為空')

                        # 前往課程頁面
                        print(f'      → 前往考試頁面...')
                        exam_url = f"{config.get('target_http')}/course/{exam_id}/content#/"

                        try:
                            driver.get(exam_url)
                            print(f'         ✓ 頁面載入成功: {driver.current_url[:60]}...')
                            time.sleep(5)
                            wrapper.record_delay(5.0, '等待考試頁面載入')
                        except Exception as e:
                            print(f'         ✗ 頁面載入失敗: {e}')
                            exam_results[exam_id] = {
                                'program_name': program_name,
                                'exam_name': exam_name,
                                'status': 'error',
                                'error': f'頁面載入失敗: {e}'
                            }
                            wrapper.end_item()
                            continue

                        exam_detail_page = ExamDetailPage(driver)
                        exam_answer_page = ExamAnswerPage(driver)

                        try:
                            # === 多策略滾動函數：滾動到底部並等待 Lazy-load 內容載入 ===
                            def scroll_to_bottom_multi_strategy(drv, max_scrolls=10, wait_time=2.0):
                                """
                                多策略滾動到頁面底部並等待 Lazy-load 元素載入

                                策略 1: 檢測 body 是否被鎖住 (overflow: hidden)
                                策略 2: 檢測 Modal/Dialog 是否存在（雙滾動條問題）
                                策略 3: 偵測真正的滾動容器（可能不是 body）
                                策略 4: scrollTo 直接滾動
                                策略 5: scrollBy 增量滾動
                                策略 6: scrollIntoView 元素定位滾動
                                策略 7: 等待高度穩定（連續確認）
                                """
                                scroll_count = 0

                                # 策略 1 & 2 & 3: 綜合偵測滾動環境
                                scroll_info = drv.execute_script("""
                                    var bodyH = document.body.scrollHeight;
                                    var docH = document.documentElement.scrollHeight;
                                    var viewH = window.innerHeight;

                                    // 策略 1: 檢測 body 是否被鎖住
                                    var bodyOverflow = getComputedStyle(document.body).overflow;
                                    var htmlOverflow = getComputedStyle(document.documentElement).overflow;
                                    var isBodyLocked = (bodyOverflow === 'hidden' || htmlOverflow === 'hidden');

                                    // 策略 2: 檢測 Modal/Dialog（雙滾動條問題）
                                    var modalSelectors = [
                                        // 考試頁面 Modal（基於 Burp Suite 分析）
                                        '.reveal-modal:not([style*="display: none"])',
                                        '.popup-area:not([style*="display: none"])',
                                        // 通用 Modal 選擇器
                                        '.modal', '.modal-dialog', '.modal-content', '.modal-body',
                                        '.dialog', '.popup', '.overlay-content',
                                        '[role="dialog"]', '[role="alertdialog"]',
                                        '.ant-modal', '.el-dialog', '.MuiDialog-root',
                                        '.v-dialog', '.chakra-modal__content'
                                    ];
                                    var activeModal = null;
                                    var modalScrollContainer = null;
                                    for (var i = 0; i < modalSelectors.length; i++) {
                                        var modal = document.querySelector(modalSelectors[i]);
                                        if (modal && modal.offsetParent !== null) {
                                            activeModal = modalSelectors[i];
                                            // 找 Modal 內可滾動的容器
                                            var innerContainers = modal.querySelectorAll('*');
                                            for (var j = 0; j < innerContainers.length; j++) {
                                                var inner = innerContainers[j];
                                                if (inner.scrollHeight > inner.clientHeight + 10) {
                                                    var style = getComputedStyle(inner);
                                                    if (style.overflowY === 'auto' || style.overflowY === 'scroll') {
                                                        modalScrollContainer = inner;
                                                        break;
                                                    }
                                                }
                                            }
                                            break;
                                        }
                                    }

                                    // 策略 3: 尋找一般滾動容器（含考試頁面專用選擇器）
                                    var containers = [
                                        // 考試頁面專用（基於 Burp Suite 分析）
                                        '.fullscreen-right', '.activity-content-box', '.exam-subjects',
                                        '.submission-list.exam-area', '.sync-scroll',
                                        // 通用選擇器
                                        '.main-container', '.content-wrapper', '.scroll-container',
                                        '.app-content', '.page-content', '[class*="scroll"]',
                                        'main', '#main', '#content', '.container'
                                    ];
                                    var scrollContainer = null;
                                    if (!activeModal) {
                                        for (var i = 0; i < containers.length; i++) {
                                            var el = document.querySelector(containers[i]);
                                            if (el && el.scrollHeight > el.clientHeight) {
                                                scrollContainer = containers[i];
                                                break;
                                            }
                                        }
                                    }

                                    return {
                                        bodyHeight: bodyH,
                                        docHeight: docH,
                                        viewHeight: viewH,
                                        isBodyLocked: isBodyLocked,
                                        bodyOverflow: bodyOverflow,
                                        activeModal: activeModal,
                                        hasModalScroll: modalScrollContainer !== null,
                                        scrollContainer: scrollContainer
                                    };
                                """)

                                # 解析診斷資訊
                                body_h = scroll_info.get('bodyHeight', 0)
                                doc_h = scroll_info.get('docHeight', 0)
                                is_body_locked = scroll_info.get('isBodyLocked', False)
                                active_modal = scroll_info.get('activeModal')
                                has_modal_scroll = scroll_info.get('hasModalScroll', False)
                                container = scroll_info.get('scrollContainer')

                                # 決定滾動策略
                                last_height = max(body_h, doc_h)

                                for i in range(max_scrolls):
                                    # 策略 4: 根據環境選擇滾動方式
                                    if active_modal and has_modal_scroll:
                                        # 有 Modal 且 Modal 內有滾動容器 → 滾動 Modal
                                        drv.execute_script(f"""
                                            var modal = document.querySelector('{active_modal}');
                                            if (modal) {{
                                                var scrollables = modal.querySelectorAll('*');
                                                for (var i = 0; i < scrollables.length; i++) {{
                                                    var el = scrollables[i];
                                                    if (el.scrollHeight > el.clientHeight + 10) {{
                                                        var style = getComputedStyle(el);
                                                        if (style.overflowY === 'auto' || style.overflowY === 'scroll') {{
                                                            el.scrollTop = el.scrollHeight;
                                                            break;
                                                        }}
                                                    }}
                                                }}
                                            }}
                                        """)
                                    elif is_body_locked and container:
                                        # body 被鎖住但有其他容器可滾
                                        drv.execute_script(f"""
                                            var el = document.querySelector('{container}');
                                            if (el) el.scrollTop = el.scrollHeight;
                                        """)
                                    elif container:
                                        # 有特定滾動容器
                                        drv.execute_script(f"""
                                            var el = document.querySelector('{container}');
                                            if (el) el.scrollTop = el.scrollHeight;
                                        """)
                                        # 同時也嘗試 window（雙保險）
                                        if not is_body_locked:
                                            drv.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                                    else:
                                        # 預設滾動 window
                                        drv.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                                    scroll_count += 1
                                    time.sleep(wait_time * 0.4)

                                    # 策略 5: 使用 scrollBy 增量滾動（觸發 lazy load）
                                    if not is_body_locked:
                                        viewport_height = drv.execute_script("return window.innerHeight")
                                        drv.execute_script(f"window.scrollBy(0, {viewport_height});")
                                    time.sleep(wait_time * 0.3)

                                    # 策略 6: scrollIntoView 最後一個元素
                                    drv.execute_script("""
                                        var lastElement = document.body.lastElementChild;
                                        if (lastElement) {
                                            lastElement.scrollIntoView({behavior: 'instant', block: 'end'});
                                        }
                                    """)
                                    time.sleep(wait_time * 0.3)

                                    # 策略 7: 等待高度穩定
                                    new_height = drv.execute_script("""
                                        return Math.max(
                                            document.body.scrollHeight,
                                            document.documentElement.scrollHeight
                                        );
                                    """)

                                    if new_height == last_height:
                                        # 高度相同，再確認一次（避免太早判定）
                                        time.sleep(0.5)
                                        confirm_height = drv.execute_script("""
                                            return Math.max(
                                                document.body.scrollHeight,
                                                document.documentElement.scrollHeight
                                            );
                                        """)
                                        if confirm_height == new_height:
                                            # 連續兩次相同，確認載入完成
                                            break
                                        last_height = confirm_height
                                    else:
                                        last_height = new_height

                                # 最終確認：全部策略再執行一次
                                if not is_body_locked:
                                    drv.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                                    time.sleep(0.3)
                                    drv.execute_script("window.scrollBy(0, 100);")
                                    time.sleep(0.3)
                                drv.execute_script("""
                                    var lastEl = document.body.lastElementChild;
                                    if (lastEl) lastEl.scrollIntoView({behavior: 'instant', block: 'end'});
                                """)
                                time.sleep(0.4)

                                return scroll_count

                            # 步驟 1: 點擊考試名稱
                            print('         [1/5] 點擊考試名稱...')
                            exam_detail_page.click_exam_by_name(exam_name, delay=3.0)
                            wrapper.record_delay(3.0, '點擊考試名稱延遲')

                            # 等待進入考試頁面（/learning-activity/full-screen#/exam/XX）
                            print('         → 等待進入考試頁面...')
                            max_wait = 15
                            for wait_sec in range(max_wait):
                                time.sleep(1)
                                current_url = driver.current_url
                                if 'learning-activity/full-screen#/exam/' in current_url:
                                    print(f'         ✓ 已進入考試頁面: {current_url[:70]}...')
                                    break
                            else:
                                print(f'         ⚠️  等待超時，當前 URL: {current_url[:70]}...')
                            wrapper.record_delay(float(min(wait_sec + 1, max_wait)), '等待考試頁面載入')

                            # 步驟 2: Before 截圖（開始答題前）
                            print('         [2/5] Before 截圖（開始答題前）...')
                            print(f'               當前 URL: {driver.current_url[:70]}...')

                            # 使用多策略滾動函數載入所有 Lazy-load 內容
                            print('               → 多策略滾動載入頁面內容...')
                            scroll_count = scroll_to_bottom_multi_strategy(driver, max_scrolls=10, wait_time=2.0)
                            print(f'               → 完成 {scroll_count} 次滾動迭代')
                            wrapper.record_delay(float(scroll_count * 2), '多策略滾動載入')

                            # 額外等待 6 秒確保所有元素完全載入
                            print('               → 額外等待 6 秒確保元素完全載入...')
                            time.sleep(6)
                            wrapper.record_delay(6.0, '額外等待元素載入')

                            # 最後再執行一次多策略滾動確保完全載入
                            print('               → 最後多策略滾動確認...')
                            scroll_to_bottom_multi_strategy(driver, max_scrolls=3, wait_time=1.5)
                            wrapper.record_delay(4.5, '最後多策略滾動確認')

                            # 截圖
                            before_path = screenshot_dir / f'exam_{exam_id}_before.png'
                            driver.save_screenshot(str(before_path))
                            print(f'               ✓ 截圖已保存: {before_path}')

                            # 步驟 3: 點擊「開始答題」進入答題頁面
                            print('         [3/5] 開始答題...')
                            exam_detail_page.click_continue_exam_button(delay=3.0)
                            wrapper.record_delay(3.0, '點擊繼續答題延遲')
                            exam_detail_page.check_agreement_checkbox(delay=3.0)
                            wrapper.record_delay(3.0, '勾選同意延遲')
                            exam_detail_page.click_popup_continue_button(delay=3.0)
                            wrapper.record_delay(3.0, '點擊確認延遲')

                            # 等待答題頁面載入完成
                            print('         → 等待答題頁面載入...')
                            time.sleep(3)
                            wrapper.record_delay(3.0, '等待答題頁面載入')

                            # 步驟 4: 自動提交考卷
                            print('         [4/5] 自動提交考卷...')

                            # 取得 interceptor 的匹配統計
                            interceptor_stats = exam_interceptor.get_stats()
                            matched = interceptor_stats.get('matched_questions', 0)
                            total = interceptor_stats.get('total_questions', 0)

                            # 顯示 API 注入統計
                            print(f"\n{'='*60}")
                            print(f"📊 API 答題注入統計")
                            print(f"{'='*60}")
                            print(f"  總題數: {total}")
                            print(f"  已匹配: {matched} 題")
                            print(f"  未匹配: {total - matched} 題")
                            print(f"{'='*60}\n")

                            # 直接提交
                            success = exam_answer_page.submit_exam_directly()

                            # 步驟 5: After 截圖（提交後）
                            print('         [5/5] After 截圖（提交後）...')

                            # 等待提交結果顯示
                            time.sleep(2)
                            wrapper.record_delay(2.0, '等待結果顯示')

                            print(f'               當前 URL: {driver.current_url[:70]}...')

                            # 使用多策略滾動確保內容載入
                            scroll_to_bottom_multi_strategy(driver, max_scrolls=5, wait_time=1.5)
                            wrapper.record_delay(7.5, '多策略滾動載入')

                            after_path = screenshot_dir / f'exam_{exam_id}_after.png'
                            driver.save_screenshot(str(after_path))
                            print(f'               ✓ 截圖已保存: {after_path}')

                            # 記錄結果
                            exam_results[exam_id] = {
                                'program_name': program_name,
                                'exam_name': exam_name,
                                'status': 'success' if success else 'failed',
                                'matched_questions': matched,
                                'total_questions': total,
                                'before_screenshot': str(before_path),
                                'after_screenshot': str(after_path)
                            }

                            print(f'      ✓ 考試處理完成')

                        except Exception as e:
                            print(f'      ✗ 考試處理失敗: {e}')
                            import traceback
                            traceback.print_exc()

                            exam_results[exam_id] = {
                                'program_name': program_name,
                                'exam_name': exam_name,
                                'status': 'error',
                                'error': str(e)
                            }

                        # ✅ 結束追蹤此考試
                        wrapper.end_item()

                    # ✅ 禁用考試答題（不停止 mitmproxy）
                    print('\n  → 禁用考試答題模式...')
                    if exam_interceptor:
                        exam_interceptor.enable = False
                        print('  ✓ 考試答題已禁用')
                    print('  ℹ️  Mitmproxy 保持運行（稍後統一停止）')

                    print(f'\n✓ 考試處理完成')
                    wrapper.end_phase("處理考試")
                else:
                    print('\n[跳過階段 6] 未選中考試')

                # ================================================================
                # 階段 7: 生成綜合報告
                # ================================================================
                wrapper.start_phase("生成綜合報告")
                print('\n[階段 7/7] 生成綜合報告...')
                print('━' * 70)

                print('\n' + '=' * 70)
                print('  混合批量模式執行報告')
                print('=' * 70)

                # 報告：一般課程
                if selected_general:
                    print('\n【一般課程 - 時長增加報告】')

                    total_increase = 0
                    success_count = 0

                    for i, course in enumerate(selected_general, 1):
                        course_code = course.get('course_code', 'N/A')
                        program_name = course.get('program_name', f'課程 {i}')
                        item_name = course.get('item_name', '未知')

                        before = durations_before.get(course_code, 0)
                        after = durations_after.get(course_code, 0)
                        diff = after - before

                        print(f'\n  [{i}] {program_name[:40]} - {item_name[:40]}')
                        print(f'      發送前: {before} 分鐘')
                        print(f'      發送後: {after} 分鐘')
                        print(f'      增加量: {diff} 分鐘 {"✓" if diff > 0 else "✗"}')

                        total_increase += diff
                        if diff > 0:
                            success_count += 1

                    print(f'\n  總結: {success_count}/{len(selected_general)} 個課程時長增加成功')
                    print(f'  總增加時長: {total_increase} 分鐘 ({total_increase / 60:.1f} 小時)')

                # 報告：考試
                if selected_exams:
                    print('\n【考試 - 自動答題報告】')

                    success_count = 0
                    failed_count = 0
                    error_count = 0

                    for i, exam in enumerate(selected_exams, 1):
                        exam_id = exam.get('api_course_id')
                        program_name = exam.get('program_name', f'考試 {i}')
                        exam_name = exam.get('item_name', '未知')

                        print(f'\n  [E{i}] {program_name[:40]} - {exam_name[:40]}')

                        if exam_id in exam_results:
                            result = exam_results[exam_id]
                            status = result.get('status', 'unknown')

                            if status == 'success':
                                print(f'      狀態: ✓ 成功')
                                success_count += 1
                            elif status == 'failed':
                                print(f'      狀態: ✗ 失敗')
                                failed_count += 1
                            else:
                                print(f'      狀態: ⚠️  錯誤 - {result.get("error", "未知錯誤")}')
                                error_count += 1

                            if 'before_screenshot' in result:
                                print(f'      截圖 (before): {result["before_screenshot"]}')
                            if 'after_screenshot' in result:
                                print(f'      截圖 (after):  {result["after_screenshot"]}')
                        else:
                            print(f'      狀態: ⚠️  未處理')
                            error_count += 1

                    print(f'\n  總結: {len(selected_exams)} 個考試')
                    print(f'    - 成功: {success_count}')
                    print(f'    - 失敗: {failed_count}')
                    print(f'    - 錯誤: {error_count}')

                print('\n' + '=' * 70)
                print('混合批量模式執行完成！')
                print(f'  - 一般課程: {len(selected_general)} 個')
                print(f'  - 考試: {len(selected_exams)} 個')
                print('=' * 70)

                wrapper.end_phase("生成綜合報告")

                print('\n✅ 混合批量模式執行完成！')

            except Exception as e:
                print(f'\n❌ 執行過程發生錯誤: {e}')
                import traceback
                traceback.print_exc()

            finally:
                # 清理資源
                if proxy:
                    try:
                        proxy.stop()
                    except:
                        pass
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass

            input('\n按 Enter 返回主選單...')

    def handle_hybrid_exam_auto_answer(self):
        """h 選項 3 - 考試自動答題

        完整流程:
        1. 登入與初始化（參照 i 功能）
        2. Payload 捕獲掃描（掃描所有考試課程）
        3. 互動選擇考試（或全選）
        4. 載入題庫
        5. 啟動 mitmproxy 並處理考試
        6. 顯示攔截統計報告
        """
        import os
        import json
        import time
        from pathlib import Path

        # ===== 顯示功能說明 =====
        print('\n' + '=' * 70)
        print('  h 選項 3 - 考試自動答題')
        print('=' * 70)
        print('\n此功能將執行：')
        print('  階段 1: 登入並掃描所有考試課程')
        print('  階段 2: 捕獲考試 Payload')
        print('  階段 3: 互動選單選擇要處理的考試')
        print('  階段 4: 載入題庫並初始化攔截器')
        print('  階段 5: 使用 mitmproxy 自動答題')
        print('  階段 6: 顯示攔截統計報告')
        print('\n特點：')
        print('  - 使用 mitmproxy 攔截考試提交 API')
        print('  - 自動匹配題庫並注入正確答案')
        print('  - 考試前後自動截圖')
        print('  - 顯示詳細的攔截統計')
        print('\n注意：')
        print('  - 確保題庫檔案存在：data/question_bank/[課程名稱].json')
        print('  - 需要在瀏覽器中手動開始考試和提交')
        print('=' * 70)

        confirm = input('\n是否繼續？(y/n): ').strip().lower()
        if confirm != 'y':
            print('\n[取消] 返回主選單')
            input('\n按 Enter 返回主選單...')
            return

        # ===== 載入配置 =====
        from src.core.config_loader import ConfigLoader
        config = ConfigLoader('config/eebot.cfg')
        config.load()

        from src.utils.execution_wrapper import ExecutionWrapper

        with ExecutionWrapper(config, "考試自動答題") as wrapper:

            driver = None
            proxy = None
            driver_manager = None

            try:
                # ================================================================
                # 階段 1: 登入與初始化（參照 i 功能）
                # ================================================================
                wrapper.start_phase("登入與初始化")
                print('\n[階段 1/6] 登入與初始化...')
                print('━' * 70)

                from src.utils.stealth_extractor import StealthExtractor
                from src.core.driver_manager import DriverManager
                from src.core.cookie_manager import CookieManager
                from src.pages.login_page import LoginPage
                from src.pages.course_list_page import CourseListPage

                # 初始化組件
                print('[初始化 1/5] 啟動瀏覽器自動化模式...')
                extractor = StealthExtractor()
                if not extractor.exists():
                    extractor.run()
                else:
                    print('  ✓ 瀏覽器自動化模式就緒')

                print('[初始化 2/5] 初始化核心元件...')
                driver_manager = DriverManager(config)
                cookie_manager = CookieManager(config.get('cookies_file'))
                print('  ✓ 核心元件已初始化')

                print('[初始化 3/5] 啟動瀏覽器...')
                driver = driver_manager.create_driver(use_proxy=False)
                print('  ✓ 瀏覽器已啟動')

                print('[初始化 4/5] 初始化頁面物件...')
                login_page = LoginPage(driver, cookie_manager)
                course_list_page = CourseListPage(driver)
                print('  ✓ 頁面物件已初始化')

                # 登入（with retry）
                print('[初始化 5/5] 登入系統...')
                max_retries = 3
                login_success = False

                for attempt in range(max_retries):
                    login_success = login_page.auto_login(
                        username=config.get('user_name'),
                        password=config.get('password'),
                        url=config.get('target_http'),
                    )

                    if login_success:
                        print('  ✓ 登入成功')
                        break
                    else:
                        if attempt < max_retries - 1:
                            print(f'  ⚠️  登入失敗，重試中... ({attempt + 1}/{max_retries})')
                            login_page.goto(config.get('target_http'))
                        else:
                            print('  ✗ 登入失敗，已達最大重試次數')

                if not login_success:
                    print('\n❌ 登入失敗，流程終止')
                    wrapper.end_phase("登入與初始化")
                    input('\n按 Enter 返回主選單...')
                    return

                # 前往我的課程
                print('\n[前往我的課程]...')
                course_list_page.goto_my_courses()
                time.sleep(5)  # 等待頁面載入
                print('  ✓ 已進入我的課程')

                wrapper.end_phase("登入與初始化")

                # ================================================================
                # 階段 2: 掃描考試課程
                # ================================================================
                wrapper.start_phase("掃描考試課程")
                print('\n[階段 2/6] 掃描考試課程...')
                print('━' * 70)

                # 獲取所有課程計畫
                print('[掃描 1/2] 獲取課程列表...')
                programs = course_list_page.get_in_progress_programs()

                if not programs:
                    print('  ⚠️  未找到任何「修習中」的課程')
                    wrapper.end_phase("掃描考試課程")
                    input('\n按 Enter 返回主選單...')
                    return

                print(f'  ✓ 找到 {len(programs)} 個課程計畫')

                # 提取 base_url（用於返回失敗時的備用導航）
                from urllib.parse import urlparse
                target_url = config.get('target_http')
                parsed = urlparse(target_url)
                base_url = f'{parsed.scheme}://{parsed.netloc}'

                # 掃描每個課程計畫，提取考試
                print('\n[掃描 2/2] 掃描課程計畫內的考試...')
                print(f'  準備掃描 {len(programs)} 個課程計畫...')

                exam_courses = []

                for i, program in enumerate(programs, 1):
                    program_name = program.get('name', f'課程 {i}')
                    print(f'\n  [{i}/{len(programs)}] {program_name[:50]}...')

                    try:
                        # 使用 get_program_courses_and_exams() 獲取子課程和考試
                        result = course_list_page.get_program_courses_and_exams(program_name)

                        if result.get('error'):
                            print(f'      ✗ 掃描失敗: {result.get("error_message", "未知錯誤")}')
                        else:
                            courses = result.get('courses', [])
                            exams = result.get('exams', [])
                            print(f'      ✓ 找到 {len(courses)} 個課程, {len(exams)} 個考試')

                            # 提取課程 ID（從當前 URL）
                            current_url = driver.current_url
                            import re
                            course_id_match = re.search(r'/course/(\d+)', current_url)
                            course_id = course_id_match.group(1) if course_id_match else None

                            if course_id:
                                print(f'      → 課程 ID: {course_id}')
                            else:
                                print(f'      ⚠️  無法提取課程 ID from URL: {current_url}')

                            # 只保留考試
                            for exam in exams:
                                exam_data = {
                                    "program_name": program_name,  # 主課程計畫名稱
                                    "exam_name": exam['name'],  # 考試名稱
                                    "api_course_id": course_id,  # ✅ 添加課程 ID
                                    "item_type": "exam"
                                }
                                exam_courses.append(exam_data)
                                print(f'         ✅ 已加入考試: {exam["name"][:40]}')

                        # 返回課程列表（準備掃描下一個課程計畫）
                        if i < len(programs):
                            print(f'      → 返回課程列表...')
                            try:
                                # 方法 1: 使用返回按鈕
                                course_list_page.go_back_to_course_list()
                            except Exception as e1:
                                print(f'      [WARNING] 返回按鈕失敗，嘗試直接導航: {e1}')
                                try:
                                    # 方法 2: 直接導航
                                    driver.get(f'{base_url}/user/courses')
                                    time.sleep(3)
                                    print(f'      ✓ 已導航到課程列表')
                                except Exception as e2:
                                    print(f'      [ERROR] 導航失敗: {e2}')

                    except Exception as e:
                        print(f'      ✗ 無法掃描課程計畫: {e}')
                        # 即使掃描失敗，也嘗試返回課程列表以繼續處理下一個
                        if i < len(programs):
                            try:
                                driver.get(f'{base_url}/user/courses')
                                time.sleep(3)
                            except Exception:
                                pass

                print(f'\n  ✓ 已掃描完成，找到 {len(exam_courses)} 個考試')

                wrapper.end_phase("掃描考試課程")

                if not exam_courses:
                    print('\n  ⚠️  沒有找到考試課程')
                    input('\n按 Enter 返回主選單...')
                    return

                # ================================================================
                # 階段 3: 互動選擇考試
                # ================================================================
                wrapper.start_phase("互動選擇考試")
                print('\n[階段 3/6] 互動選擇考試...')
                print('━' * 70)

                from src.utils.course_selection_menu import CourseSelectionMenu

                selection_menu = CourseSelectionMenu(exam_courses)
                selected_exams = selection_menu.run()

                if not selected_exams:
                    print('\n[已取消] 用戶取消選擇')
                    wrapper.end_phase("互動選擇考試")
                    input('\n按 Enter 返回主選單...')
                    return

                print(f'\n✓ 已選擇 {len(selected_exams)} 個考試')

                wrapper.end_phase("互動選擇考試")

                # ================================================================
                # 階段 4: 載入題庫並初始化攔截器
                # ================================================================
                wrapper.start_phase("載入題庫")
                print('\n[階段 4/6] 載入題庫並初始化攔截器...')
                print('━' * 70)

                from src.services.question_bank import QuestionBankService
                from src.services.answer_matcher import AnswerMatcher
                from src.api.interceptors.exam_auto_answer import ExamAutoAnswerInterceptor

                # 初始化題庫服務（不立即加載，將在處理每個考試時動態加載）
                question_bank_service = QuestionBankService(config)
                answer_matcher = AnswerMatcher(confidence_threshold=0.85)

                print('  ✓ 題庫服務已初始化')
                print('  ✓ 答案匹配器已初始化（信心閾值: 0.85）')
                print('  ℹ️  題庫將在處理每個考試時動態加載')

                # 初始化攔截器
                interceptor = ExamAutoAnswerInterceptor(
                    question_bank_service=question_bank_service,
                    answer_matcher=answer_matcher,
                    enable=True
                )

                print('  ✓ ExamAutoAnswerInterceptor 已初始化')

                wrapper.end_phase("載入題庫")

                # ================================================================
                # 階段 5: 啟動 mitmproxy 並處理考試
                # ================================================================
                wrapper.start_phase("處理考試")
                print('\n[階段 5/6] 啟動 mitmproxy 並處理考試...')
                print('━' * 70)

                # 導入 ProxyManager
                from src.core.proxy_manager import ProxyManager

                # 啟動 mitmproxy
                proxy = ProxyManager(config, interceptors=[interceptor])
                proxy.start()
                print('  ✓ Mitmproxy 已啟動（考試自動答題模式）')

                # 重新啟動瀏覽器（使用 proxy）
                print('\n[準備處理] 重新啟動瀏覽器（使用 proxy）...')
                driver.quit()
                driver = driver_manager.create_driver(use_proxy=True)

                # 重新登入
                login_page = LoginPage(driver, cookie_manager)
                login_page.auto_login(
                    username=config.get('user_name'),
                    password=config.get('password'),
                    url=config.get('target_http'),
                )
                print('  ✓ 已重新登入（使用 proxy）')

                # 處理每個選中的考試
                print('\n[處理考試] 開始處理選中的考試...')

                from src.pages.exam_detail_page import ExamDetailPage
                from src.pages.exam_answer_page import ExamAnswerPage

                exam_screenshots = {}  # 存儲考試截圖路徑

                for i, exam in enumerate(selected_exams, 1):
                    exam_id = exam.get('api_course_id')
                    program_name = exam.get('program_name', f'考試 {i}')
                    exam_name = exam.get('exam_name', '未知考試')

                    print(f'\n  [{i}/{len(selected_exams)}] {program_name[:50]}')
                    print(f'      考試名稱: {exam_name}')

                    # ✅ 動態切換題庫：為當前考試加載對應的題庫
                    print(f'      → 載入題庫: {program_name[:40]}...')
                    question_count = question_bank_service.load_question_bank(program_name)
                    if question_count > 0:
                        print(f'         ✓ 題庫已載入: {question_count} 題')
                    else:
                        print(f'         ⚠️  題庫載入失敗或為空')

                    # 前往課程頁面
                    exam_url = f"{config.get('target_http')}/course/{exam_id}/content#/"
                    print(f'      → 前往課程頁面...')
                    driver.get(exam_url)
                    time.sleep(5)

                    # 準備截圖目錄
                    screenshot_dir = Path('reports/exam_screenshots')
                    screenshot_dir.mkdir(parents=True, exist_ok=True)

                    # 完全自動化考試流程
                    print('      → 開始自動化考試流程...')
                    exam_detail_page = ExamDetailPage(driver)
                    exam_answer_page = ExamAnswerPage(driver)

                    try:
                        # === 多策略滾動函數：滾動到底部並等待 Lazy-load 內容載入 ===
                        def scroll_to_bottom_multi_strategy(drv, max_scrolls=10, wait_time=2.0):
                            """
                            多策略滾動到頁面底部並等待 Lazy-load 元素載入

                            策略 1: 檢測 body 是否被鎖住 (overflow: hidden)
                            策略 2: 檢測 Modal/Dialog 是否存在（雙滾動條問題）
                            策略 3: 偵測真正的滾動容器（可能不是 body）
                            策略 4: scrollTo 直接滾動
                            策略 5: scrollBy 增量滾動
                            策略 6: scrollIntoView 元素定位滾動
                            策略 7: 等待高度穩定（連續確認）
                            """
                            scroll_count = 0

                            # 策略 1 & 2 & 3: 綜合偵測滾動環境
                            scroll_info = drv.execute_script("""
                                var bodyH = document.body.scrollHeight;
                                var docH = document.documentElement.scrollHeight;
                                var viewH = window.innerHeight;

                                // 策略 1: 檢測 body 是否被鎖住
                                var bodyOverflow = getComputedStyle(document.body).overflow;
                                var htmlOverflow = getComputedStyle(document.documentElement).overflow;
                                var isBodyLocked = (bodyOverflow === 'hidden' || htmlOverflow === 'hidden');

                                // 策略 2: 檢測 Modal/Dialog（雙滾動條問題）
                                var modalSelectors = [
                                    // 考試頁面 Modal（基於 Burp Suite 分析）
                                    '.reveal-modal:not([style*="display: none"])',
                                    '.popup-area:not([style*="display: none"])',
                                    // 通用 Modal 選擇器
                                    '.modal', '.modal-dialog', '.modal-content', '.modal-body',
                                    '.dialog', '.popup', '.overlay-content',
                                    '[role="dialog"]', '[role="alertdialog"]',
                                    '.ant-modal', '.el-dialog', '.MuiDialog-root',
                                    '.v-dialog', '.chakra-modal__content'
                                ];
                                var activeModal = null;
                                var modalScrollContainer = null;
                                for (var i = 0; i < modalSelectors.length; i++) {
                                    var modal = document.querySelector(modalSelectors[i]);
                                    if (modal && modal.offsetParent !== null) {
                                        activeModal = modalSelectors[i];
                                        // 找 Modal 內可滾動的容器
                                        var innerContainers = modal.querySelectorAll('*');
                                        for (var j = 0; j < innerContainers.length; j++) {
                                            var inner = innerContainers[j];
                                            if (inner.scrollHeight > inner.clientHeight + 10) {
                                                var style = getComputedStyle(inner);
                                                if (style.overflowY === 'auto' || style.overflowY === 'scroll') {
                                                    modalScrollContainer = inner;
                                                    break;
                                                }
                                            }
                                        }
                                        break;
                                    }
                                }

                                // 策略 3: 尋找一般滾動容器（含考試頁面專用選擇器）
                                var containers = [
                                    // 考試頁面專用（基於 Burp Suite 分析）
                                    '.fullscreen-right', '.activity-content-box', '.exam-subjects',
                                    '.submission-list.exam-area', '.sync-scroll',
                                    // 通用選擇器
                                    '.main-container', '.content-wrapper', '.scroll-container',
                                    '.app-content', '.page-content', '[class*="scroll"]',
                                    'main', '#main', '#content', '.container'
                                ];
                                var scrollContainer = null;
                                if (!activeModal) {
                                    for (var i = 0; i < containers.length; i++) {
                                        var el = document.querySelector(containers[i]);
                                        if (el && el.scrollHeight > el.clientHeight) {
                                            scrollContainer = containers[i];
                                            break;
                                        }
                                    }
                                }

                                return {
                                    bodyHeight: bodyH,
                                    docHeight: docH,
                                    viewHeight: viewH,
                                    isBodyLocked: isBodyLocked,
                                    bodyOverflow: bodyOverflow,
                                    activeModal: activeModal,
                                    hasModalScroll: modalScrollContainer !== null,
                                    scrollContainer: scrollContainer
                                };
                            """)

                            # 解析診斷資訊
                            body_h = scroll_info.get('bodyHeight', 0)
                            doc_h = scroll_info.get('docHeight', 0)
                            is_body_locked = scroll_info.get('isBodyLocked', False)
                            active_modal = scroll_info.get('activeModal')
                            has_modal_scroll = scroll_info.get('hasModalScroll', False)
                            container = scroll_info.get('scrollContainer')

                            # 決定滾動策略
                            last_height = max(body_h, doc_h)

                            for i in range(max_scrolls):
                                # 策略 4: 根據環境選擇滾動方式
                                if active_modal and has_modal_scroll:
                                    # 有 Modal 且 Modal 內有滾動容器 → 滾動 Modal
                                    drv.execute_script(f"""
                                        var modal = document.querySelector('{active_modal}');
                                        if (modal) {{
                                            var scrollables = modal.querySelectorAll('*');
                                            for (var i = 0; i < scrollables.length; i++) {{
                                                var el = scrollables[i];
                                                if (el.scrollHeight > el.clientHeight + 10) {{
                                                    var style = getComputedStyle(el);
                                                    if (style.overflowY === 'auto' || style.overflowY === 'scroll') {{
                                                        el.scrollTop = el.scrollHeight;
                                                        break;
                                                    }}
                                                }}
                                            }}
                                        }}
                                    """)
                                elif is_body_locked and container:
                                    # body 被鎖住但有其他容器可滾
                                    drv.execute_script(f"""
                                        var el = document.querySelector('{container}');
                                        if (el) el.scrollTop = el.scrollHeight;
                                    """)
                                elif container:
                                    # 有特定滾動容器
                                    drv.execute_script(f"""
                                        var el = document.querySelector('{container}');
                                        if (el) el.scrollTop = el.scrollHeight;
                                    """)
                                    # 同時也嘗試 window（雙保險）
                                    if not is_body_locked:
                                        drv.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                                else:
                                    # 預設滾動 window
                                    drv.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                                scroll_count += 1
                                time.sleep(wait_time * 0.4)

                                # 策略 5: 使用 scrollBy 增量滾動（觸發 lazy load）
                                if not is_body_locked:
                                    viewport_height = drv.execute_script("return window.innerHeight")
                                    drv.execute_script(f"window.scrollBy(0, {viewport_height});")
                                time.sleep(wait_time * 0.3)

                                # 策略 6: scrollIntoView 最後一個元素
                                drv.execute_script("""
                                    var lastElement = document.body.lastElementChild;
                                    if (lastElement) {
                                        lastElement.scrollIntoView({behavior: 'instant', block: 'end'});
                                    }
                                """)
                                time.sleep(wait_time * 0.3)

                                # 策略 7: 等待高度穩定
                                new_height = drv.execute_script("""
                                    return Math.max(
                                        document.body.scrollHeight,
                                        document.documentElement.scrollHeight
                                    );
                                """)

                                if new_height == last_height:
                                    # 高度相同，再確認一次（避免太早判定）
                                    time.sleep(0.5)
                                    confirm_height = drv.execute_script("""
                                        return Math.max(
                                            document.body.scrollHeight,
                                            document.documentElement.scrollHeight
                                        );
                                    """)
                                    if confirm_height == new_height:
                                        # 連續兩次相同，確認載入完成
                                        break
                                    last_height = confirm_height
                                else:
                                    last_height = new_height

                            # 最終確認：全部策略再執行一次
                            if not is_body_locked:
                                drv.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                                time.sleep(0.3)
                                drv.execute_script("window.scrollBy(0, 100);")
                                time.sleep(0.3)
                            drv.execute_script("""
                                var lastEl = document.body.lastElementChild;
                                if (lastEl) lastEl.scrollIntoView({behavior: 'instant', block: 'end'});
                            """)
                            time.sleep(0.4)

                            return scroll_count

                        # 步驟 1: 點擊考試名稱（進入測驗區）
                        print('         [1/4] 點擊考試名稱...')
                        exam_detail_page.click_exam_by_name(exam_name, delay=3.0)

                        # 等待進入考試頁面
                        print('         → 等待進入考試頁面...')
                        max_wait = 15
                        for wait_sec in range(max_wait):
                            time.sleep(1)
                            current_url = driver.current_url
                            if 'learning-activity/full-screen#/exam/' in current_url:
                                print(f'         ✓ 已進入考試頁面: {current_url[:70]}...')
                                break
                        else:
                            print(f'         ⚠️  等待超時，當前 URL: {current_url[:70]}...')

                        # Before 截圖（在測驗區，開始答題前）
                        print('         [2/4] Before 截圖（開始答題前）...')
                        print(f'               當前 URL: {driver.current_url[:70]}...')

                        # 使用多策略滾動函數載入所有 Lazy-load 內容
                        print('               → 多策略滾動載入頁面內容...')
                        scroll_count = scroll_to_bottom_multi_strategy(driver, max_scrolls=10, wait_time=2.0)
                        print(f'               → 完成 {scroll_count} 次滾動迭代')

                        # 額外等待 6 秒確保所有元素完全載入
                        print('               → 額外等待 6 秒確保元素完全載入...')
                        time.sleep(6)

                        # 最後再執行一次多策略滾動確保完全載入
                        print('               → 最後多策略滾動確認...')
                        scroll_to_bottom_multi_strategy(driver, max_scrolls=3, wait_time=1.5)

                        # 截圖
                        before_path = screenshot_dir / f'exam_{exam_id}_before.png'
                        driver.save_screenshot(str(before_path))
                        print(f'               ✓ Before: {before_path}')

                        # 步驟 2: 點擊"繼續答題"按鈕並勾選同意
                        print('         [3/4] 開始答題...')
                        exam_detail_page.click_continue_exam_button(delay=3.0)
                        exam_detail_page.check_agreement_checkbox(delay=3.0)
                        exam_detail_page.click_popup_continue_button(delay=3.0)
                        time.sleep(5)  # 等待答題頁面加載

                        # 步驟 3: 自動提交考卷（Mitmproxy 會攔截並注入答案）
                        print('         [4/4] 自動提交考卷...')
                        print('               （Mitmproxy 將攔截並注入答案）')
                        success = exam_answer_page.submit_exam_with_confirmation(auto_submit=True)

                        if success:
                            print('               ✓ 考試已完成')
                        else:
                            print('               ✗ 提交失敗')

                        # 等待結果顯示並返回測驗區
                        time.sleep(5)

                        # After 截圖（提交後）
                        print('      → After 截圖（提交後）...')
                        print(f'         當前 URL: {driver.current_url[:70]}...')

                        # 等待結果頁面穩定
                        time.sleep(2)

                        print('         → 多策略滾動載入頁面內容...')
                        scroll_to_bottom_multi_strategy(driver, max_scrolls=5, wait_time=1.5)
                        after_path = screenshot_dir / f'exam_{exam_id}_after.png'
                        driver.save_screenshot(str(after_path))
                        print(f'         ✓ After: {after_path}')

                    except Exception as e:
                        print(f'         ✗ 自動化流程失敗: {e}')
                        print('         → 截圖錯誤狀態...')
                        # 錯誤截圖
                        error_path = screenshot_dir / f'exam_{exam_id}_error.png'
                        driver.save_screenshot(str(error_path))
                        print(f'         ✓ Error: {error_path}')
                        # 設置 after_path 為 error_path
                        after_path = error_path
                        before_path = screenshot_dir / f'exam_{exam_id}_before.png'

                    exam_screenshots[exam_id] = {
                        'before': str(before_path),
                        'after': str(after_path)
                    }

                    # 返回課程列表（準備處理下一個考試）
                    if i < len(selected_exams):
                        print('      → 返回課程列表...')
                        driver.get(f'{base_url}/user/courses')
                        time.sleep(3)

                print(f'\n✓ 已處理 {len(selected_exams)} 個考試')

                # 停止 mitmproxy
                proxy.stop()
                proxy = None

                wrapper.end_phase("處理考試")

                # ================================================================
                # 階段 6: 顯示攔截統計報告
                # ================================================================
                wrapper.start_phase("生成報告")
                print('\n[階段 6/6] 生成攔截統計報告...')
                print('━' * 70)

                print('\n' + '=' * 70)
                print('  考試自動答題報告')
                print('=' * 70)

                # 獲取攔截器統計（如果 interceptor 提供的話）
                if hasattr(interceptor, 'get_stats'):
                    stats = interceptor.get_stats()
                    print('\n【攔截統計】')
                    print(f'  總攔截次數: {stats.get("total_intercepts", 0)}')
                    print(f'  成功匹配: {stats.get("successful_matches", 0)}')
                    print(f'  匹配失敗: {stats.get("failed_matches", 0)}')

                # 顯示每個考試的詳細信息
                print('\n【考試處理詳情】')

                for i, exam in enumerate(selected_exams, 1):
                    exam_id = exam.get('api_course_id')
                    program_name = exam.get('program_name', f'考試 {i}')

                    print(f'\n  [{i}] {program_name[:55]}')
                    print(f'      狀態: ✓ 已處理')

                    if exam_id in exam_screenshots:
                        screenshots = exam_screenshots[exam_id]
                        print(f'      截圖 (before): {screenshots["before"]}')
                        print(f'      截圖 (after):  {screenshots["after"]}')

                print('\n' + '=' * 70)
                print(f'考試自動答題完成！')
                print(f'  - 處理考試: {len(selected_exams)} 個')
                print(f'  - 截圖保存: reports/exam_screenshots/')
                print('=' * 70)

                wrapper.end_phase("生成報告")

                print('\n✅ 考試自動答題執行完成！')

            except Exception as e:
                print(f'\n❌ 執行過程發生錯誤: {e}')
                import traceback
                traceback.print_exc()

            finally:
                # 清理資源
                if proxy:
                    try:
                        proxy.stop()
                    except:
                        pass
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass

            input('\n按 Enter 返回主選單...')
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

        print('\n歡迎使用 EEBot 課程排程管理系統！')

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
                self.handle_hybrid_choice()

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
