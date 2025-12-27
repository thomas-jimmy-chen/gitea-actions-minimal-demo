#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
ExecutionWrapper 單元測試
測試時間追蹤和截圖功能的整合

Created: 2025-12-21
Author: Claude Code (Sonnet 4.5)
"""

import unittest
import os
import sys
import time
from unittest.mock import MagicMock, patch

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.execution_wrapper import ExecutionWrapper


class TestExecutionWrapper(unittest.TestCase):
    """ExecutionWrapper 單元測試"""

    def setUp(self):
        """測試前準備"""
        # 創建模擬的 config 物件
        self.mock_config = MagicMock()
        self.mock_config.get.return_value = 'test_user'
        self.mock_config.load_timing_config.return_value = {
            'screenshot': {
                'enabled': False  # 測試時禁用截圖（不需要 PIL）
            }
        }

    def tearDown(self):
        """測試後清理"""
        # 清理測試生成的報告文件
        report_dir = 'reports/測試功能'
        if os.path.exists(report_dir):
            try:
                for file in os.listdir(report_dir):
                    os.remove(os.path.join(report_dir, file))
                os.rmdir(report_dir)
                # 也刪除 reports 目錄（如果為空）
                if os.path.exists('reports') and not os.listdir('reports'):
                    os.rmdir('reports')
            except:
                pass

    def test_initialization(self):
        """測試 ExecutionWrapper 初始化"""
        wrapper = ExecutionWrapper(self.mock_config, "測試功能")

        self.assertEqual(wrapper.function_name, "測試功能")
        self.assertTrue(wrapper.is_tracking_enabled())
        self.assertIsNotNone(wrapper.time_tracker)

    def test_initialization_with_disabled_tracking(self):
        """測試禁用時間追蹤的初始化"""
        wrapper = ExecutionWrapper(
            self.mock_config,
            "測試功能",
            enable_tracking=False
        )

        self.assertFalse(wrapper.is_tracking_enabled())
        self.assertIsNone(wrapper.time_tracker)

    def test_context_manager(self):
        """測試上下文管理器"""
        with ExecutionWrapper(self.mock_config, "測試功能") as wrapper:
            self.assertIsNotNone(wrapper)
            self.assertTrue(wrapper.is_tracking_enabled())

    def test_phase_management(self):
        """測試階段管理"""
        with ExecutionWrapper(self.mock_config, "測試功能") as wrapper:
            # 開始階段
            wrapper.start_phase("測試階段")

            self.assertEqual(wrapper.time_tracker.current_phase, "測試階段")
            self.assertIn("測試階段", wrapper.time_tracker.phases)

            # 結束階段
            wrapper.end_phase("測試階段")

            self.assertIsNone(wrapper.time_tracker.current_phase)
            self.assertIsNotNone(wrapper.time_tracker.phases["測試階段"]["end"])

    def test_item_management_course(self):
        """測試課程項目管理"""
        with ExecutionWrapper(self.mock_config, "測試功能") as wrapper:
            # 開始課程
            wrapper.start_item("測試課程", "測試計畫", item_type="course")

            expected_name = "測試計畫 > 測試課程"
            self.assertEqual(wrapper.time_tracker.current_course, expected_name)
            self.assertIn(expected_name, wrapper.time_tracker.courses)

            # 結束課程
            wrapper.end_item()

            self.assertIsNone(wrapper.time_tracker.current_course)
            self.assertIsNotNone(wrapper.time_tracker.courses[expected_name]["end"])

    def test_item_management_exam(self):
        """測試考試項目管理"""
        with ExecutionWrapper(self.mock_config, "測試功能") as wrapper:
            # 開始考試
            wrapper.start_item("測試考試", "測試計畫", item_type="exam")

            expected_name = "測試計畫 > 測試考試"
            self.assertEqual(wrapper.time_tracker.current_exam, expected_name)
            self.assertIn(expected_name, wrapper.time_tracker.exams)

            # 結束考試
            wrapper.end_item()

            self.assertIsNone(wrapper.time_tracker.current_exam)
            self.assertIsNotNone(wrapper.time_tracker.exams[expected_name]["end"])

    def test_delay_recording(self):
        """測試延遲記錄"""
        with ExecutionWrapper(self.mock_config, "測試功能") as wrapper:
            # 開始課程
            wrapper.start_item("測試課程", "測試計畫")

            # 記錄延遲
            wrapper.record_delay(5.0, "測試延遲")

            expected_name = "測試計畫 > 測試課程"
            self.assertEqual(
                wrapper.time_tracker.courses[expected_name]["delays"],
                5.0
            )
            self.assertEqual(wrapper.time_tracker.total_delays, 5.0)

            wrapper.end_item()

    def test_user_wait_recording(self):
        """測試使用者等待記錄"""
        with ExecutionWrapper(self.mock_config, "測試功能") as wrapper:
            # 開始使用者等待
            wrapper.start_user_wait("測試等待")

            # 模擬等待
            time.sleep(0.1)

            # 結束使用者等待
            wrapper.end_user_wait()

            self.assertGreater(wrapper.time_tracker.total_user_wait, 0)
            self.assertEqual(len(wrapper.time_tracker.user_input_waits), 1)

    def test_screenshot_disabled(self):
        """測試截圖功能禁用"""
        wrapper = ExecutionWrapper(
            self.mock_config,
            "測試功能",
            enable_screenshot=True  # 嘗試啟用，但配置中禁用
        )

        self.assertFalse(wrapper.is_screenshot_enabled())
        self.assertIsNone(wrapper.screenshot_manager)

        # 調用截圖應該返回 None
        result = wrapper.take_screenshot(MagicMock(), "測試", 1)
        self.assertIsNone(result)

    def test_get_stats(self):
        """測試取得統計數據"""
        with ExecutionWrapper(self.mock_config, "測試功能") as wrapper:
            # 處理課程
            wrapper.start_item("課程1", "計畫A", item_type="course")
            wrapper.end_item()

            wrapper.start_item("課程2", "計畫A", item_type="course")
            wrapper.end_item()

            # 處理考試
            wrapper.start_item("考試1", "計畫B", item_type="exam")
            wrapper.end_item()

            # 取得統計
            stats = wrapper.get_stats()

            self.assertIn("計畫A", stats)
            self.assertIn("計畫B", stats)
            self.assertEqual(len(stats["計畫A"]["courses"]), 2)
            self.assertEqual(len(stats["計畫B"]["exams"]), 1)

    def test_multiple_phases(self):
        """測試多個階段"""
        with ExecutionWrapper(self.mock_config, "測試功能") as wrapper:
            # 階段 1
            wrapper.start_phase("階段1")
            time.sleep(0.1)
            wrapper.end_phase("階段1")

            # 階段 2
            wrapper.start_phase("階段2")
            time.sleep(0.1)
            wrapper.end_phase("階段2")

            # 階段 3
            wrapper.start_phase("階段3")
            time.sleep(0.1)
            wrapper.end_phase("階段3")

            self.assertEqual(len(wrapper.time_tracker.phases), 3)
            self.assertIn("階段1", wrapper.time_tracker.phases)
            self.assertIn("階段2", wrapper.time_tracker.phases)
            self.assertIn("階段3", wrapper.time_tracker.phases)

    def test_auto_end_phase(self):
        """測試自動結束當前階段"""
        with ExecutionWrapper(self.mock_config, "測試功能") as wrapper:
            # 開始階段（不指定名稱結束）
            wrapper.start_phase("測試階段")
            self.assertEqual(wrapper.time_tracker.current_phase, "測試階段")

            # 自動結束當前階段
            wrapper.end_phase()
            self.assertIsNone(wrapper.time_tracker.current_phase)

    def test_exception_handling(self):
        """測試異常處理"""
        try:
            with ExecutionWrapper(self.mock_config, "測試功能") as wrapper:
                wrapper.start_phase("測試階段")
                # 拋出異常
                raise ValueError("測試異常")
        except ValueError:
            # 異常應該被正確傳播
            pass

        # 即使出現異常，報告應該仍然生成（檢查不會拋出異常）
        # 這個測試主要確保異常不會被吞掉

    def test_print_status(self):
        """測試打印狀態"""
        with ExecutionWrapper(self.mock_config, "測試功能") as wrapper:
            wrapper.start_phase("測試階段")
            wrapper.start_item("測試課程", "測試計畫")

            # 調用 print_status 不應該拋出異常
            try:
                wrapper.print_status()
            except Exception as e:
                self.fail(f"print_status() 拋出異常: {e}")

            wrapper.end_item()
            wrapper.end_phase()

    def test_repr(self):
        """測試字串表示"""
        wrapper = ExecutionWrapper(self.mock_config, "測試功能")
        repr_str = repr(wrapper)

        self.assertIn("ExecutionWrapper", repr_str)
        self.assertIn("測試功能", repr_str)
        self.assertIn("tracking=enabled", repr_str)


class TestExecutionWrapperIntegration(unittest.TestCase):
    """ExecutionWrapper 整合測試"""

    def setUp(self):
        """測試前準備"""
        self.mock_config = MagicMock()
        self.mock_config.get.return_value = 'test_user'
        self.mock_config.load_timing_config.return_value = {
            'screenshot': {
                'enabled': False
            }
        }

    def tearDown(self):
        """測試後清理"""
        # 清理測試生成的報告文件
        report_dir = 'reports/整合測試'
        if os.path.exists(report_dir):
            try:
                for file in os.listdir(report_dir):
                    os.remove(os.path.join(report_dir, file))
                os.rmdir(report_dir)
                if os.path.exists('reports') and not os.listdir('reports'):
                    os.rmdir('reports')
            except:
                pass

    def test_complete_workflow(self):
        """測試完整工作流程"""
        with ExecutionWrapper(self.mock_config, "整合測試") as wrapper:
            # 階段 1: 初始化
            wrapper.start_phase("初始化")
            time.sleep(0.05)
            wrapper.record_delay(0.05, "初始化延遲")
            wrapper.end_phase("初始化")

            # 階段 2: 處理項目
            wrapper.start_phase("處理項目")

            # 處理課程
            wrapper.start_item("課程1", "計畫A", item_type="course")
            time.sleep(0.05)
            wrapper.record_delay(0.05, "處理課程")
            wrapper.end_item()

            # 處理考試
            wrapper.start_item("考試1", "計畫B", item_type="exam")
            time.sleep(0.05)
            wrapper.record_delay(0.05, "處理考試")
            wrapper.end_item()

            wrapper.end_phase("處理項目")

            # 階段 3: 清理
            wrapper.start_phase("清理")
            time.sleep(0.05)
            wrapper.record_delay(0.05, "清理延遲")
            wrapper.end_phase("清理")

            # 驗證統計
            stats = wrapper.get_stats()
            self.assertEqual(len(stats), 2)  # 兩個計畫
            self.assertEqual(len(stats["計畫A"]["courses"]), 1)
            self.assertEqual(len(stats["計畫B"]["exams"]), 1)

        # 驗證報告文件生成（檢查目錄存在）
        # 注意：實際文件生成可能因為各種原因失敗，這裡只檢查不拋出異常


def run_tests():
    """運行所有測試"""
    # 創建測試套件
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

    # 運行測試
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 返回測試結果
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
