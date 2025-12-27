# -*- coding: utf-8 -*-
"""
Unit Tests for DurationSendOrchestrator.

Tests the duration sending workflow orchestration.
"""

import pytest
from unittest.mock import MagicMock, patch
import sys

# Save original modules before mocking (for test isolation)
_orig_modules = {
    'src.utils.execution_wrapper': sys.modules.get('src.utils.execution_wrapper'),
    'src.config.feature_flags': sys.modules.get('src.config.feature_flags'),
}

# Mock external dependencies
sys.modules['src.utils.execution_wrapper'] = MagicMock()
sys.modules['src.config.feature_flags'] = MagicMock()

# Create mock ExecutionWrapper
mock_wrapper = MagicMock()
mock_wrapper.__enter__ = MagicMock(return_value=mock_wrapper)
mock_wrapper.__exit__ = MagicMock(return_value=False)
mock_wrapper.is_tracking_enabled.return_value = True
mock_wrapper.get_stats.return_value = {}
sys.modules['src.utils.execution_wrapper'].ExecutionWrapper = MagicMock(
    return_value=mock_wrapper
)
sys.modules['src.config.feature_flags'].feature_enabled = MagicMock(
    return_value=False
)

from src.orchestrators.duration_send import (
    DurationSendOrchestrator,
    CourseProgress,
    DurationSendResult,
)


@pytest.fixture(scope="module", autouse=True)
def restore_modules():
    """Restore original modules after all tests in this module complete."""
    yield
    # Cleanup: restore original modules
    for mod_name, original in _orig_modules.items():
        if original is not None:
            sys.modules[mod_name] = original
        elif mod_name in sys.modules:
            del sys.modules[mod_name]


class TestCourseProgress:
    """Test cases for CourseProgress dataclass."""

    def test_creation(self):
        """Test course progress creation."""
        progress = CourseProgress(
            course_id=1,
            course_name="Test Course",
            current_time=1800,
            pass_time=3600,
            target_time=3600
        )

        assert progress.course_id == 1
        assert progress.course_name == "Test Course"
        assert progress.current_time == 1800
        assert progress.pass_time == 3600
        assert progress.sent is False
        assert progress.verified is False

    def test_default_values(self):
        """Test default values."""
        progress = CourseProgress(
            course_id=1,
            course_name="Test"
        )

        assert progress.current_time == 0
        assert progress.pass_time == 0
        assert progress.target_time == 0
        assert progress.error is None


class TestDurationSendResult:
    """Test cases for DurationSendResult dataclass."""

    def test_creation(self):
        """Test result creation."""
        result = DurationSendResult()

        assert result.courses == []
        assert result.total_sent == 0
        assert result.total_verified == 0
        assert result.total_failed == 0
        assert result.error is None

    def test_with_data(self):
        """Test result with data."""
        courses = [
            CourseProgress(1, "Course 1"),
            CourseProgress(2, "Course 2")
        ]
        result = DurationSendResult(
            courses=courses,
            total_sent=2,
            total_verified=1,
            total_failed=1
        )

        assert len(result.courses) == 2
        assert result.total_sent == 2
        assert result.total_failed == 1


class TestDurationSendOrchestrator:
    """Test cases for DurationSendOrchestrator."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration."""
        config = MagicMock()
        config.get.side_effect = lambda key, default=None: {
            'target_http': 'https://example.com',
        }.get(key, default)
        config.load_timing_config.return_value = {'screenshot': {'enabled': False}}
        return config

    @pytest.fixture
    def orchestrator(self, mock_config):
        """Create an orchestrator instance."""
        return DurationSendOrchestrator(mock_config)

    def test_initialization(self, mock_config):
        """Test orchestrator initialization."""
        orch = DurationSendOrchestrator(mock_config)

        assert orch.name == "時長發送"
        assert orch.base_url == "https://example.com"

    def test_initialization_with_custom_base_url(self, mock_config):
        """Test initialization with custom base URL."""
        orch = DurationSendOrchestrator(
            mock_config,
            base_url="https://custom.example.com"
        )

        assert orch.base_url == "https://custom.example.com"

    def test_get_headers(self, orchestrator):
        """Test HTTP headers generation."""
        headers = orchestrator._get_headers()

        assert 'User-Agent' in headers
        assert 'Accept' in headers
        assert 'Content-Type' in headers
        assert headers['Content-Type'] == 'application/json'

    def test_calculate_target_times_auto(self, orchestrator):
        """Test auto target time calculation."""
        courses = [
            CourseProgress(1, "Course 1", pass_time=3600),
            CourseProgress(2, "Course 2", pass_time=1800),
        ]

        orchestrator._calculate_target_times(courses, 60, auto_calculate=True)

        assert courses[0].target_time == 3600  # Uses pass_time
        assert courses[1].target_time == 1800  # Uses pass_time

    def test_calculate_target_times_manual(self, orchestrator):
        """Test manual target time calculation."""
        courses = [
            CourseProgress(1, "Course 1", pass_time=3600),
            CourseProgress(2, "Course 2", pass_time=1800),
        ]

        orchestrator._calculate_target_times(courses, 45, auto_calculate=False)

        assert courses[0].target_time == 2700  # 45 * 60
        assert courses[1].target_time == 2700  # 45 * 60

    def test_get_courses_with_ids(self, orchestrator):
        """Test getting courses with specified IDs."""
        courses = orchestrator._get_courses(course_ids=[1, 2, 3])

        assert len(courses) == 3
        assert courses[0].course_id == 1
        assert courses[1].course_id == 2
        assert courses[2].course_id == 3

    def test_verify_durations(self, orchestrator):
        """Test duration verification."""
        courses = [
            CourseProgress(1, "Course 1"),
            CourseProgress(2, "Course 2"),
        ]
        courses[0].sent = True
        courses[1].sent = True

        verified = orchestrator._verify_durations(courses)

        assert verified == 2
        assert courses[0].verified is True
        assert courses[1].verified is True

    def test_verify_skips_unsent(self, orchestrator):
        """Test that verification skips unsent courses."""
        courses = [
            CourseProgress(1, "Course 1"),
            CourseProgress(2, "Course 2"),
        ]
        courses[0].sent = True
        courses[1].sent = False  # Not sent

        verified = orchestrator._verify_durations(courses)

        assert verified == 1
        assert courses[0].verified is True
        assert courses[1].verified is False


class TestDurationSendOrchestratorExecution:
    """Test cases for execute method."""

    @pytest.fixture
    def mock_config(self):
        config = MagicMock()
        config.get.side_effect = lambda key, default=None: {
            'target_http': 'https://example.com',
        }.get(key, default)
        config.load_timing_config.return_value = {'screenshot': {'enabled': False}}
        return config

    def test_execute_without_cookie_fails(self, mock_config):
        """Test that execution fails without session cookie."""
        orchestrator = DurationSendOrchestrator(mock_config)

        result = orchestrator.execute()

        assert result.success is False
        assert "Session Cookie" in result.error

    def test_execute_with_mocked_flow(self, mock_config):
        """Test execution with mocked internal methods."""
        orchestrator = DurationSendOrchestrator(mock_config)

        # Mock internal methods
        orchestrator._get_courses = MagicMock(return_value=[
            CourseProgress(1, "Course 1", pass_time=3600)
        ])
        orchestrator._send_durations = MagicMock(return_value=1)
        orchestrator._verify_durations = MagicMock(return_value=1)

        result = orchestrator.execute(
            session_cookie={'sessionid': 'test'},
            course_ids=[1]
        )

        assert result.success is True
        assert result.data['total_courses'] == 1
        assert result.data['total_sent'] == 1

    def test_execute_no_courses_found(self, mock_config):
        """Test execution when no courses found."""
        orchestrator = DurationSendOrchestrator(mock_config)

        orchestrator._get_courses = MagicMock(return_value=[])

        result = orchestrator.execute(
            session_cookie={'sessionid': 'test'}
        )

        assert result.success is False
        assert "未找到課程" in result.error

    def test_execute_with_failures(self, mock_config):
        """Test execution with some failures."""
        orchestrator = DurationSendOrchestrator(mock_config)

        courses = [
            CourseProgress(1, "Course 1"),
            CourseProgress(2, "Course 2"),
        ]
        orchestrator._get_courses = MagicMock(return_value=courses)
        orchestrator._send_durations = MagicMock(return_value=2)
        orchestrator._verify_durations = MagicMock(return_value=1)  # One failed

        result = orchestrator.execute(
            session_cookie={'sessionid': 'test'}
        )

        assert result.success is False  # Not all verified
        assert result.data['total_failed'] == 1
