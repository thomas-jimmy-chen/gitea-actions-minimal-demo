#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
Eebot - Elearn Automation Bot (Refactored Version)
採用 POM (Page Object Model) + API 模組化設計

Author: Guy Fawkes
Date: 2025/1/1
Version: 2.0.0
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
from src.utils.stealth_extractor import StealthExtractor


def main():
    """主程式入口"""
    print("""
╔══════════════════════════════════════════════════════════╗
║          Eebot - Elearn Automation Bot v2.0              ║
║          POM + API Modular Architecture                  ║
╚══════════════════════════════════════════════════════════╝
    """)

    # 1. 載入配置
    print('[Step 1/6] Loading configuration...')
    config = ConfigLoader("config/eebot.cfg")
    try:
        config.load()
        print(f'  ✓ Configuration loaded: {config.config_file}')
    except FileNotFoundError as e:
        print(f'  ✗ {e}')
        return

    # 2. 提取 Stealth JS（如需要）
    print('\n[Step 2/6] Extracting stealth evasions...')
    extractor = StealthExtractor()
    if not extractor.exists():
        extractor.run()
    else:
        print('  ✓ Stealth evasions already exist, skipping extraction')

    # 3. 啟動 Proxy（如需修改訪問時長）
    proxy = None
    if config.get_bool('modify_visits'):
        print('\n[Step 3/6] Starting mitmproxy with visit duration interceptor...')
        interceptor = VisitDurationInterceptor(increase_duration=9000)
        proxy = ProxyManager(config, interceptors=[interceptor])
        proxy.start()
    else:
        print('\n[Step 3/6] Proxy disabled (modify_visits=n)')

    # 4. 載入課程資料
    print('\n[Step 4/6] Loading course data...')
    courses_file = 'data/courses.json'
    try:
        with open(courses_file, 'r', encoding='utf-8') as f:
            course_data = json.load(f)
        courses = course_data.get('courses', [])
        print(f'  ✓ Loaded {len(courses)} courses from {courses_file}')
    except FileNotFoundError:
        print(f'  ✗ Course data file not found: {courses_file}')
        if proxy:
            proxy.stop()
        return
    except json.JSONDecodeError as e:
        print(f'  ✗ Invalid JSON in {courses_file}: {e}')
        if proxy:
            proxy.stop()
        return

    # 5. 執行場景
    print('\n[Step 5/6] Initializing course learning scenario...')
    try:
        # 從配置讀取是否在錯誤時保持瀏覽器開啟（預設為 False）
        keep_browser_on_error = config.get_bool('keep_browser_on_error', False)

        scenario = CourseLearningScenario(config, keep_browser_on_error=keep_browser_on_error)
        print('  ✓ Scenario initialized')

        print('\n[Step 6/6] Executing scenario...')
        scenario.execute(courses)

    except KeyboardInterrupt:
        print('\n[INFO] User interrupted')
    except Exception as e:
        print(f'\n[ERROR] Scenario execution failed: {e}')
        import traceback
        traceback.print_exc()
    finally:
        # 6. 清理資源
        if proxy:
            print('\n[Cleanup] Stopping mitmproxy...')
            proxy.stop()

    print('\n' + '=' * 60)
    print('Program terminated')
    print('=' * 60)


if __name__ == '__main__':
    main()
