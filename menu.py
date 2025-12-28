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

from src.exceptions import EEBotError
from src.utils.error_handler import handle_error

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


def _use_scroll_utils() -> bool:
    """檢查是否啟用 scroll_utils 模組"""
    try:
        from src.config.feature_flags import feature_enabled
        return feature_enabled('use_scroll_utils')
    except ImportError:
        return False


def _get_scroll_function():
    """獲取滾動函數 - 根據 feature flag 返回模組版本或內聯版本"""
    if _use_scroll_utils():
        from src.utils.scroll_utils import scroll_to_bottom_multi_strategy
        return scroll_to_bottom_multi_strategy
    return None  # 返回 None 表示使用內聯版本


def _use_login_service() -> bool:
    """檢查是否啟用 LoginService"""
    try:
        from src.config.feature_flags import feature_enabled
        return feature_enabled('use_login_service')
    except ImportError:
        return False


def _do_login_with_service(login_page, config):
    """使用 LoginService 執行登入"""
    from src.services.login_service import LoginService
    service = LoginService(login_page, config)
    result = service.login_with_default_messages()
    return result.success


def _do_login_legacy(login_page, config, max_retries=3):
    """Legacy 登入邏輯"""
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
    return login_success


def _perform_login(login_page, config, max_retries=3):
    """統一登入入口 - 根據 feature flag 選擇實現"""
    if _use_login_service():
        return _do_login_with_service(login_page, config)
    return _do_login_legacy(login_page, config, max_retries)


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
        print('                  EEBot 自動化學習系統 v2.4')
        print('=' * 70)

        # === 主要功能（醒目顯示）===
        print('\n  ┌' + '─' * 66 + '┐')
        print('  │  [i] 智能推薦      自動掃描修習中課程 → 匹配 → 執行             │')
        print('  │  [h] 混合掃描      h1:時長  h2:課程+考試  h3:考試答題           │')
        print('  └' + '─' * 66 + '┘')

        # === 其他選項 ===
        print('\n  [w] 學習統計查詢 (快速)')
        print('  [m] 更多選項...')
        print('  [q] 離開')

        print('=' * 70)

    def display_more_options(self):
        """顯示更多選項子選單"""
        print('\n' + '─' * 70)
        print('  更多選項')
        print('─' * 70)
        print('  [t] API 測試 (研究用)')
        print('  [p] 預製排程 (舊版功能)')
        print('  [q] 返回主選單')
        print('─' * 70)

    def display_preset_menu(self):
        """顯示預製排程子選單"""
        print('\n' + '─' * 70)
        print('  預製排程 (舊版功能)')
        print('─' * 70)
        print('  1-{} - 選擇課程加入排程'.format(len(self.all_courses)))
        print('  v - 查看排程 | c - 清除 | s - 儲存 | r - 執行')

        # 顯示課程列表
        print('\n  課程列表:')
        for i, course in enumerate(self.all_courses, 1):
            course_type = course.get('course_type', 'course')
            if course_type == 'exam':
                name = course.get('exam_name', '')
                print(f'    {i:2d}. {course["program_name"]} - {name} [考試]')
            else:
                name = course.get('lesson_name', '')
                print(f'    {i:2d}. {course["program_name"]} - {name}')

        print('\n  q - 返回主選單')
        print('─' * 70)

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
        # Phase 3: Orchestrator 整合 (Legacy 已移除)
        # =====================================================================
        self._handle_intelligent_recommendation_orchestrator()

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
                print(f"  掃描課程計畫數: {result.data.get('programs_count', 0)}")
                print(f"  發現課程數: {result.data.get('courses_found', 0)}")
                print(f"  發現考試數: {result.data.get('exams_found', 0)}")
                print(f"  加入排程數: {result.data.get('added_count', 0)}")
            else:
                print('\n' + '=' * 70)
                print('  ✗ 智能推薦執行失敗')
                print('=' * 70)
                print(f"  錯誤: {result.error}")

        except EEBotError as e:
            handle_error(e, driver=None, context="智能推薦 Orchestrator", is_known=True)
        except Exception as e:
            handle_error(e, driver=None, context="智能推薦 Orchestrator", is_known=False)

        input('\n按 Enter 返回主選單...')

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

        # Legacy 路由已全部移除，所有模式只使用 Orchestrator
        print(f'\n[INFO] {mode} 模式已整合至 Orchestrator，請啟用 use_orchestrators')
        return

    def _show_hybrid_description_and_confirm(self, mode: str) -> bool:
        """顯示功能說明並確認是否繼續"""
        descriptions = {
            'duration': {
                'title': 'h 選項 1 - 一般課程時長發送',
                'stages': [
                    '階段 1: 登入與初始化（啟動 mitmproxy 捕獲模式）',
                    '階段 2: 掃描所有課程（捕獲 Payload，排除考試）',
                    '階段 3: 顯示選擇選單（支持 all 選項）',
                    '階段 4: 提取通過條件與計算目標時長',
                    '階段 5: 使用 mitmproxy 發送目標時長',
                    '階段 6: 重刷頁面並驗證時長差異',
                    '階段 7: 顯示差異報告',
                ],
                'features': [
                    '自動捕獲 visit_duration API Payload',
                    '智能計算目標時長（基於通過條件）',
                    '發送後自動驗證時長差異',
                ],
            },
            'batch': {
                'title': 'h 選項 2 - 混合批量模式',
                'stages': [
                    '階段 1: 登入並掃描所有課程（一般課程 + 考試）',
                    '階段 2: 深度掃描每個課程計畫（提取子課程和考試）',
                    '階段 3: 顯示選擇選單（支持 all 選項）',
                    '階段 4: 分離一般課程和考試',
                    '階段 5: 執行一般課程處理（h1 邏輯）',
                    '階段 6: 執行考試處理（h3 邏輯）',
                    '階段 7: 生成綜合報告',
                ],
                'features': [
                    '一般課程 + 考試課程混合處理',
                    '支持用戶選擇（包括 all）',
                    '智能執行：先 h1 再 h3',
                    '動態題庫切換（每個考試加載對應題庫）',
                    '考試截圖（before/after，滾動至底部）',
                ],
            },
            'exam': {
                'title': 'h 選項 3 - 考試自動答題',
                'stages': [
                    '階段 1: 登入與初始化',
                    '階段 2: 掃描測驗課程（僅考試類型）',
                    '階段 3: 顯示選擇選單（支持 all 選項）',
                    '階段 4: 針對每個考試：加載題庫 → 答題 → 提交',
                    '階段 5: 生成考試報告',
                ],
                'features': [
                    '動態題庫切換（每個考試加載對應題庫）',
                    '自動匹配題目與答案',
                    '考試前後截圖（滾動至底部）',
                    '支持多種題型：單選、多選、是非',
                ],
                'notes': [
                    '需要預先配置題庫（data/question_banks/）',
                    '題庫格式：JSON 或 TXT',
                ],
            },
        }

        desc = descriptions.get(mode, descriptions['duration'])

        print('\n' + '=' * 70)
        print(f'  {desc["title"]}')
        print('=' * 70)
        print('\n此功能將執行：')
        for stage in desc['stages']:
            print(f'  {stage}')

        print('\n特點：')
        for feature in desc['features']:
            print(f'  - {feature}')

        if 'notes' in desc:
            print('\n注意事項：')
            for note in desc['notes']:
                print(f'  ⚠️  {note}')

        print('=' * 70)

        confirm = input('\n是否繼續？(y/n): ').strip().lower()
        return confirm == 'y'

    def _handle_hybrid_orchestrator(self, mode: str):
        """使用 Orchestrator 執行混合掃描"""
        # 顯示功能說明並確認
        if not self._show_hybrid_description_and_confirm(mode):
            print('\n已取消')
            return

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
                print(f"  掃描 Payload 數: {result.data.get('payloads_captured', 0)}")
                print(f"  已選擇課程數: {result.data.get('courses_selected', 0)}")
                print(f"  成功處理數: {result.data.get('courses_processed', 0)}")
                print(f"  成功數: {result.data.get('success_count', 0)}")
            else:
                print('\n' + '=' * 70)
                print(f'  ✗ 混合掃描 ({mode}) 執行失敗')
                print('=' * 70)
                print(f"  錯誤: {result.error}")

        except EEBotError as e:
            handle_error(e, driver=None, context=f"混合掃描 ({mode}) Orchestrator", is_known=True)
        except Exception as e:
            handle_error(e, driver=None, context=f"混合掃描 ({mode}) Orchestrator", is_known=False)

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

    def handle_more_options(self):
        """處理更多選項子選單"""
        while True:
            self.display_more_options()
            choice = input('\n請輸入選項: ').strip().lower()

            if choice == 't':
                self.test_learning_stats()
                input('\n按 Enter 繼續...')

            elif choice == 'p':
                self.handle_preset_schedule()

            elif choice == 'q':
                break

            else:
                print('\n✗ 無效的選項')
                input('\n按 Enter 繼續...')

    def handle_preset_schedule(self):
        """處理預製排程子選單（舊版功能）"""
        while True:
            self.display_preset_menu()

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

            # 儲存排程
            elif choice == 's':
                if not self.scheduled_courses:
                    print('\n✗ 排程為空，無需儲存')
                else:
                    self.save_schedule()

            # 執行排程
            elif choice == 'r':
                self.run_schedule()

            # 返回主選單
            elif choice == 'q':
                break

            else:
                print('\n✗ 無效的選項')

            input('\n按 Enter 繼續...')

    def run(self):
        """執行互動式選單"""
        # 載入課程資料
        if not self.load_courses():
            return

        # 載入已存在的排程
        self.load_schedule()

        print('\n歡迎使用 EEBot 自動化學習系統！')

        # 顯示學習履歷摘要 (如果有保存的 session)
        self.display_learning_summary()

        while True:
            self.display_menu()

            choice = input('\n請輸入選項: ').strip().lower()

            # 智能推薦
            if choice == 'i':
                self.handle_intelligent_recommendation()
                input('\n按 Enter 繼續...')

            # 混合掃描
            elif choice == 'h':
                self.handle_hybrid_choice()
                input('\n按 Enter 繼續...')

            # 快速查詢學習統計
            elif choice == 'w':
                self.quick_learning_stats()
                input('\n按 Enter 繼續...')

            # 更多選項
            elif choice == 'm':
                self.handle_more_options()

            # 離開
            elif choice == 'q':
                print('\n再見！')
                break

            else:
                print('\n✗ 無效的選項，請輸入 i, h, w, m 或 q')
                input('\n按 Enter 繼續...')


def main():
    """主程式入口"""
    scheduler = CourseScheduler()
    scheduler.run()


if __name__ == '__main__':
    main()
