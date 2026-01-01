# -*- coding: utf-8 -*-
"""
Tests for TimeTracker - 時間追蹤器測試

測試覆蓋：
- 程式時間追蹤
- 階段時間追蹤
- 課程/考試時間追蹤
- 延遲時間記錄
- 使用者等待時間記錄
- 統計報告生成
"""

import pytest
import time
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.time_tracker import TimeTracker


class TestProgramTracking:
    """測試程式整體時間追蹤"""

    def test_start_program(self):
        """測試程式開始記錄"""
        tracker = TimeTracker()
        tracker.start_program()

        assert tracker.program_start_time is not None
        assert tracker.program_start_time > 0

    def test_end_program(self):
        """測試程式結束記錄"""
        tracker = TimeTracker()
        tracker.start_program()
        time.sleep(0.01)  # 短暫等待
        tracker.end_program()

        assert tracker.program_end_time is not None
        assert tracker.program_end_time > tracker.program_start_time


class TestPhaseTracking:
    """測試階段時間追蹤"""

    def test_start_phase(self):
        """測試階段開始記錄"""
        tracker = TimeTracker()
        tracker.start_phase("初始化")

        assert tracker.current_phase == "初始化"
        assert "初始化" in tracker.phases
        assert tracker.phases["初始化"]["start"] is not None

    def test_end_phase(self):
        """測試階段結束記錄"""
        tracker = TimeTracker()
        tracker.start_phase("初始化")
        time.sleep(0.01)
        tracker.end_phase("初始化")

        assert tracker.phases["初始化"]["end"] is not None
        assert tracker.phases["初始化"]["duration"] > 0
        assert tracker.current_phase is None

    def test_auto_end_previous_phase(self):
        """測試自動結束前一階段"""
        tracker = TimeTracker()
        tracker.start_phase("階段1")
        tracker.start_phase("階段2")  # 應該自動結束階段1

        assert tracker.phases["階段1"]["end"] is not None
        assert tracker.current_phase == "階段2"

    def test_multiple_phases(self):
        """測試多個階段追蹤"""
        tracker = TimeTracker()

        tracker.start_phase("初始化")
        tracker.end_phase("初始化")

        tracker.start_phase("登入")
        tracker.end_phase("登入")

        tracker.start_phase("執行")
        tracker.end_phase("執行")

        assert len(tracker.phases) == 3
        for phase_name in ["初始化", "登入", "執行"]:
            assert phase_name in tracker.phases
            assert tracker.phases[phase_name]["duration"] >= 0


class TestCourseTracking:
    """測試課程時間追蹤"""

    def test_start_course(self):
        """測試課程開始記錄"""
        tracker = TimeTracker()
        tracker.start_course("課程A", "計畫X")

        expected_name = "計畫X > 課程A"
        assert tracker.current_course == expected_name
        assert expected_name in tracker.courses
        assert tracker.courses[expected_name]["start"] is not None

    def test_end_course(self):
        """測試課程結束記錄"""
        tracker = TimeTracker()
        tracker.start_course("課程A", "計畫X")
        time.sleep(0.01)
        tracker.end_course()

        expected_name = "計畫X > 課程A"
        assert tracker.courses[expected_name]["end"] is not None
        assert tracker.courses[expected_name]["duration"] > 0
        assert tracker.current_course is None

    def test_course_without_program(self):
        """測試沒有計畫名稱的課程"""
        tracker = TimeTracker()
        tracker.start_course("課程A")

        assert tracker.current_course == "課程A"
        assert "課程A" in tracker.courses


class TestExamTracking:
    """測試考試時間追蹤"""

    def test_start_exam(self):
        """測試考試開始記錄"""
        tracker = TimeTracker()
        tracker.start_exam("考試1", "計畫Y")

        expected_name = "計畫Y > 考試1"
        assert tracker.current_exam == expected_name
        assert expected_name in tracker.exams

    def test_end_exam(self):
        """測試考試結束記錄"""
        tracker = TimeTracker()
        tracker.start_exam("考試1", "計畫Y")
        time.sleep(0.01)
        tracker.end_exam()

        expected_name = "計畫Y > 考試1"
        assert tracker.exams[expected_name]["end"] is not None
        assert tracker.exams[expected_name]["duration"] > 0


class TestDelayTracking:
    """測試延遲時間追蹤"""

    def test_record_delay(self):
        """測試記錄延遲時間"""
        tracker = TimeTracker()
        tracker.record_delay(5.0, "等待頁面載入")

        assert tracker.total_delays == 5.0

    def test_record_delay_to_current_course(self):
        """測試延遲記錄到當前課程"""
        tracker = TimeTracker()
        tracker.start_course("課程A")
        tracker.record_delay(3.0, "等待")

        assert tracker.courses["課程A"]["delays"] == 3.0

    def test_record_delay_to_current_exam(self):
        """測試延遲記錄到當前考試"""
        tracker = TimeTracker()
        tracker.start_exam("考試1")
        tracker.record_delay(2.0, "等待")

        assert tracker.exams["考試1"]["delays"] == 2.0

    def test_cumulative_delays(self):
        """測試累計延遲"""
        tracker = TimeTracker()
        tracker.record_delay(1.0)
        tracker.record_delay(2.0)
        tracker.record_delay(3.0)

        assert tracker.total_delays == 6.0


class TestUserWaitTracking:
    """測試使用者等待時間追蹤"""

    def test_start_user_wait(self):
        """測試使用者等待開始記錄"""
        tracker = TimeTracker()
        tracker.start_user_wait("等待輸入")

        assert tracker._user_wait_start is not None

    def test_end_user_wait(self):
        """測試使用者等待結束記錄"""
        tracker = TimeTracker()
        tracker.start_user_wait("等待輸入")
        time.sleep(0.01)
        tracker.end_user_wait()

        assert len(tracker.user_input_waits) == 1
        assert tracker.user_input_waits[0]["description"] == "等待輸入"
        assert tracker.user_input_waits[0]["duration"] > 0
        assert tracker.total_user_wait > 0


class TestFormatDuration:
    """測試時長格式化"""

    def test_format_seconds_only(self):
        """測試只有秒的格式化"""
        tracker = TimeTracker()
        result = tracker._format_duration(45)
        assert result == "45s"

    def test_format_minutes_and_seconds(self):
        """測試分鐘和秒的格式化"""
        tracker = TimeTracker()
        result = tracker._format_duration(125)  # 2分5秒
        assert "2m" in result
        assert "5s" in result

    def test_format_hours_minutes_seconds(self):
        """測試小時、分鐘和秒的格式化"""
        tracker = TimeTracker()
        result = tracker._format_duration(3725)  # 1小時2分5秒
        assert "1h" in result
        assert "2m" in result
        assert "5s" in result

    def test_format_negative_duration(self):
        """測試負數時長"""
        tracker = TimeTracker()
        result = tracker._format_duration(-5)
        assert result == "0s"

    def test_format_zero_duration(self):
        """測試零時長"""
        tracker = TimeTracker()
        result = tracker._format_duration(0)
        assert result == "0s"


class TestGetProgramStats:
    """測試課程計畫統計"""

    def test_get_program_stats_empty(self):
        """測試空統計"""
        tracker = TimeTracker()
        stats = tracker.get_program_stats()
        assert stats == {}

    def test_get_program_stats_with_courses(self):
        """測試有課程的統計"""
        tracker = TimeTracker()

        tracker.start_course("課程A", "計畫X")
        tracker.record_delay(1.0)
        tracker.end_course()

        tracker.start_course("課程B", "計畫X")
        tracker.end_course()

        stats = tracker.get_program_stats()

        assert "計畫X" in stats
        assert len(stats["計畫X"]["courses"]) == 2
        assert stats["計畫X"]["total_delays"] == 1.0

    def test_get_program_stats_with_exams(self):
        """測試有考試的統計"""
        tracker = TimeTracker()

        tracker.start_exam("考試1", "計畫Y")
        tracker.end_exam()

        stats = tracker.get_program_stats()

        assert "計畫Y" in stats
        assert len(stats["計畫Y"]["exams"]) == 1


class TestRepr:
    """測試字串表示"""

    def test_repr_empty(self):
        """測試空追蹤器的字串表示"""
        tracker = TimeTracker()
        result = repr(tracker)

        assert "TimeTracker" in result
        assert "courses=0" in result
        assert "exams=0" in result

    def test_repr_with_data(self):
        """測試有資料的字串表示"""
        tracker = TimeTracker()
        tracker.start_course("課程A")
        tracker.end_course()
        tracker.start_exam("考試1")
        tracker.end_exam()

        result = repr(tracker)

        assert "courses=1" in result
        assert "exams=1" in result
