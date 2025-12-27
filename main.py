#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
EEBot - Elearn Automation Bot (Refactored Version)
採用 POM (Page Object Model) + API 模組化設計

Original Author: Guy Fawkes (v2.0.0)
Modified by: wizard03 (v2.0.1)
Date: 2025/11/10
Version: 2.0.1
"""

import json
import sys
import os

# 將 src 加入 Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.config_loader import ConfigLoader
from src.core.proxy_manager import ProxyManager
from src.api.interceptors.visit_duration import VisitDurationInterceptor
from src.scenarios.course_learning import CourseLearningScenario
from src.scenarios.exam_learning import ExamLearningScenario
from src.utils.stealth_extractor import StealthExtractor
from src.utils.time_tracker import TimeTracker


def main():
    """主程式入口"""
    print("""
╔══════════════════════════════════════════════════════════╗
║        EEBot - Elearn Automation Bot v2.0.1              ║
║          POM + API Modular Architecture                  ║
║              Modified by wizard03                        ║
╚══════════════════════════════════════════════════════════╝
    """)

    # 初始化時間追蹤器
    tracker = TimeTracker()
    tracker.start_program()

    # 1. 載入配置
    tracker.start_phase('系統初始化')
    print('[Step 1/6] Loading configuration...')
    config = ConfigLoader("config/eebot.cfg")
    try:
        config.load()
        print(f'  ✓ Configuration loaded: {config.config_file}')
    except FileNotFoundError as e:
        print(f'  ✗ {e}')
        return

    # 2. 提取 Stealth JS（如需要）
    print('\n[Step 2/6] Activating browser automation mode...')
    extractor = StealthExtractor()
    if not extractor.exists():
        extractor.run()
    else:
        print('  ✓ Browser automation mode ready, skipping initialization')

    # 2.5. 載入蟲洞功能配置（訪問時長增加值）
    # 統一在這裡讀取，避免在多處 hardcode default 值
    visit_duration_increase = config.get_int('visit_duration_increase', 9000)

    # 3. 啟動 Proxy（如需修改訪問時長）
    proxy = None
    if config.get_bool('modify_visits'):
        print('\n[Step 3/6] Starting network monitoring with visit duration interceptor...')
        interceptor = VisitDurationInterceptor(increase_duration=visit_duration_increase)
        proxy = ProxyManager(config, interceptors=[interceptor])
        proxy.start()
        print(f'[INFO] Wormhole mode activated - Time will be accelerated by {visit_duration_increase // 60} minutes')
    else:
        print('\n[Step 3/6] Proxy disabled (modify_visits=n)')

    # 4. 載入排程資料
    tracker.start_phase('載入排程資料')
    print('\n[Step 4/6] Loading scheduled courses...')
    schedule_file = 'data/schedule.json'
    try:
        with open(schedule_file, 'r', encoding='utf-8-sig') as f:
            schedule_data = json.load(f)
        courses = schedule_data.get('courses', [])

        if not courses:
            print(f'  ✗ Schedule is empty!')
            print(f'  → Please run "python menu.py" to schedule courses first')
            if proxy:
                proxy.stop()
            return

        print(f'  ✓ Loaded {len(courses)} scheduled courses from {schedule_file}')
    except FileNotFoundError:
        print(f'  ✗ Schedule file not found: {schedule_file}')
        print(f'  → Please run "python menu.py" to create and schedule courses first')
        if proxy:
            proxy.stop()
        return
    except json.JSONDecodeError as e:
        print(f'  ✗ Invalid JSON in {schedule_file}: {e}')
        if proxy:
            proxy.stop()
        return

    # 5. 分離課程和考試
    tracker.start_phase('分離課程和考試')
    print('\n[Step 5/6] Separating courses and exams...')
    regular_courses = []
    exams = []

    for item in courses:
        course_type = item.get('course_type', 'course')
        if course_type == 'exam':
            exams.append(item)
        else:
            regular_courses.append(item)

    print(f'  ✓ Found {len(regular_courses)} regular courses and {len(exams)} exams')

    # 6. 執行場景
    tracker.start_phase('執行課程與考試')
    print('\n[Step 6/6] Executing scenarios...')
    try:
        # 從配置讀取是否在錯誤時保持瀏覽器開啟（預設為 False）
        keep_browser_on_error = config.get_bool('keep_browser_on_error', False)

        # 執行一般課程
        if regular_courses:
            tracker.start_phase('執行一般課程')
            print('\n[6.1] Executing regular courses...')
            scenario = CourseLearningScenario(
                config,
                keep_browser_on_error=keep_browser_on_error,
                time_tracker=tracker,
                visit_duration_increase=visit_duration_increase
            )
            print('  ✓ Course scenario initialized')
            scenario.execute(regular_courses)

        # 執行考試
        if exams:
            tracker.start_phase('執行考試')
            print('\n[6.2] Executing exams...')
            print('  → Using smart exam scenario (auto-answer for specific exams only)')

            # 使用考試場景（根據每個考試的 enable_auto_answer 字段決定是否自動答題）
            exam_scenario = ExamLearningScenario(
                config,
                keep_browser_on_error=keep_browser_on_error,
                time_tracker=tracker,
                visit_duration_increase=visit_duration_increase
            )
            print('  ✓ Exam scenario initialized')
            exam_scenario.execute(exams)

    except KeyboardInterrupt:
        print('\n[INFO] User interrupted')
    except Exception as e:
        print(f'\n[ERROR] Scenario execution failed: {e}')
        import traceback
        traceback.print_exc()
    finally:
        # 6. 清理資源
        tracker.start_phase('清理資源')
        if proxy:
            print('\n[Cleanup] Stopping network monitoring...')
            proxy.stop()

        # 7. 刪除臨時檔案（cookies 和 stealth.min.js）
        print('\n[Cleanup] Removing temporary files...')
        temp_files = [
            'cookies.json',                           # 根目錄臨時檔案
            'resource/cookies/cookies.json',          # Cookie 檔案
            'stealth.min.js',                         # 根目錄臨時 stealth
            'resource/plugins/stealth.min.js'         # Stealth 檔案
        ]

        for file_path in temp_files:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    # 將技術性檔名轉為使用者友善的顯示名稱
                    display_name = file_path.replace('stealth.min.js', 'stealth mode file')
                    print(f'  ✓ Removed: {display_name}')
                except OSError as e:
                    display_name = file_path.replace('stealth.min.js', 'stealth mode file')
                    print(f'  ✗ Failed to remove {display_name}: {e}')

        # 8. 清除排程檔案
        print('\n[Cleanup] Clearing schedule...')
        schedule_file = 'data/schedule.json'
        if os.path.exists(schedule_file):
            try:
                # 清空排程（保留檔案結構，但清空課程列表）
                empty_schedule = {
                    "description": "課程執行排程 - 自動清除",
                    "last_cleared": __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "courses": []
                }
                with open(schedule_file, 'w', encoding='utf-8') as f:
                    json.dump(empty_schedule, f, indent=2, ensure_ascii=False)
                print(f'  ✓ Schedule cleared: {schedule_file}')
            except OSError as e:
                print(f'  ✗ Failed to clear schedule: {e}')
        else:
            print(f'  ⚠️  Schedule file not found (already cleared or never created)')

        # 9. 打印時間統計報告
        tracker.end_phase('清理資源')
        tracker.print_report()

    print('\n' + '=' * 60)
    print('Program terminated')
    print('=' * 60)


if __name__ == '__main__':
    main()
