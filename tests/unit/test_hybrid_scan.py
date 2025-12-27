# -*- coding: utf-8 -*-
"""
Unit Tests for HybridScanOrchestrator.

Tests the hybrid scan workflow orchestration.
"""

import pytest
from unittest.mock import MagicMock, patch
import sys

# Save original modules before mocking (for test isolation)
_orig_modules = {
    'src.utils.execution_wrapper': sys.modules.get('src.utils.execution_wrapper'),
    'src.config.feature_flags': sys.modules.get('src.config.feature_flags'),
    'src.core.cookie_manager': sys.modules.get('src.core.cookie_manager'),
    'src.core.driver_manager': sys.modules.get('src.core.driver_manager'),
    'src.pages.course_list_page': sys.modules.get('src.pages.course_list_page'),
    'src.pages.login_page': sys.modules.get('src.pages.login_page'),
    'src.utils.stealth_extractor': sys.modules.get('src.utils.stealth_extractor'),
}

# Mock external dependencies
sys.modules['src.utils.execution_wrapper'] = MagicMock()
sys.modules['src.config.feature_flags'] = MagicMock()
sys.modules['src.core.cookie_manager'] = MagicMock()
sys.modules['src.core.driver_manager'] = MagicMock()
sys.modules['src.pages.course_list_page'] = MagicMock()
sys.modules['src.pages.login_page'] = MagicMock()
sys.modules['src.utils.stealth_extractor'] = MagicMock()

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

from src.orchestrators.hybrid_scan import (
    HybridScanOrchestrator,
    HybridMode,
    PayloadData,
    HybridScanResult,
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


class TestHybridMode:
    """Test cases for HybridMode enum."""

    def test_mode_values(self):
        """Test mode enum values."""
        assert HybridMode.DURATION.value == "duration"
        assert HybridMode.BATCH.value == "batch"
        assert HybridMode.EXAM.value == "exam"

    def test_all_modes(self):
        """Test that all modes are defined."""
        modes = list(HybridMode)
        assert len(modes) == 3


class TestPayloadData:
    """Test cases for PayloadData dataclass."""

    def test_creation(self):
        """Test payload data creation."""
        payload = PayloadData(
            course_id=1,
            course_name="Test Course",
            program_name="Test Program",
            payload={'key': 'value'},
            read_time=30,
            pass_time=60,
            target_time=60
        )

        assert payload.course_id == 1
        assert payload.course_name == "Test Course"
        assert payload.program_name == "Test Program"
        assert payload.read_time == 30
        assert payload.pass_time == 60

    def test_default_values(self):
        """Test default values."""
        payload = PayloadData(
            course_id=1,
            course_name="Test",
            program_name="Program",
            payload={}
        )

        assert payload.read_time == 0
        assert payload.pass_time == 0
        assert payload.target_time == 0


class TestHybridScanResult:
    """Test cases for HybridScanResult dataclass."""

    def test_creation(self):
        """Test result creation."""
        result = HybridScanResult(mode=HybridMode.DURATION)

        assert result.mode == HybridMode.DURATION
        assert result.payloads == []
        assert result.selected_courses == []
        assert result.sent_count == 0
        assert result.verified_count == 0
        assert result.error is None

    def test_with_data(self):
        """Test result with actual data."""
        payload = PayloadData(
            course_id=1,
            course_name="Test",
            program_name="Program",
            payload={}
        )
        result = HybridScanResult(
            mode=HybridMode.BATCH,
            payloads=[payload],
            selected_courses=[payload],
            sent_count=1,
            verified_count=1
        )

        assert len(result.payloads) == 1
        assert len(result.selected_courses) == 1
        assert result.sent_count == 1


class TestHybridScanOrchestrator:
    """Test cases for HybridScanOrchestrator."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration."""
        config = MagicMock()
        config.get.side_effect = lambda key, default=None: {
            'user_name': 'test_user',
            'password': 'test_pass',
            'target_http': 'https://example.com',
            'cookies_file': 'cookies.json'
        }.get(key, default)
        config.load_timing_config.return_value = {'screenshot': {'enabled': False}}
        return config

    @pytest.fixture
    def orchestrator(self, mock_config):
        """Create an orchestrator instance."""
        return HybridScanOrchestrator(mock_config)

    def test_initialization_default_mode(self, mock_config):
        """Test default mode initialization."""
        orch = HybridScanOrchestrator(mock_config)

        assert orch.mode == HybridMode.DURATION
        assert "一般課程時長發送" in orch.name

    def test_initialization_batch_mode(self, mock_config):
        """Test batch mode initialization."""
        orch = HybridScanOrchestrator(mock_config, mode=HybridMode.BATCH)

        assert orch.mode == HybridMode.BATCH
        assert "批量模式" in orch.name

    def test_initialization_exam_mode(self, mock_config):
        """Test exam mode initialization."""
        orch = HybridScanOrchestrator(mock_config, mode=HybridMode.EXAM)

        assert orch.mode == HybridMode.EXAM
        assert "考試自動答題" in orch.name

    def test_select_courses_auto(self, orchestrator):
        """Test auto course selection."""
        payloads = [
            PayloadData(1, "Course 1", "Program 1", {}),
            PayloadData(2, "Course 2", "Program 1", {}),
        ]

        selected = orchestrator._select_courses(payloads, auto_select=True)

        assert len(selected) == 2

    def test_send_duration(self, orchestrator):
        """Test duration sending."""
        courses = [
            PayloadData(1, "Course 1", "Program 1", {}, target_time=60),
            PayloadData(2, "Course 2", "Program 1", {}, target_time=30),
        ]

        sent_count = orchestrator._send_duration(courses)

        assert sent_count == 2

    def test_verify_duration(self, orchestrator):
        """Test duration verification."""
        courses = [
            PayloadData(1, "Course 1", "Program 1", {}),
        ]

        verified_count = orchestrator._verify_duration(courses)

        assert verified_count == 1

    def test_generate_report(self, orchestrator):
        """Test report generation."""
        result = HybridScanResult(
            mode=HybridMode.DURATION,
            payloads=[PayloadData(1, "Test", "Prog", {})],
            selected_courses=[PayloadData(1, "Test", "Prog", {})],
            sent_count=1,
            verified_count=1
        )

        # Should not raise
        orchestrator._generate_report(result)

    def test_cleanup_no_resources(self, orchestrator):
        """Test cleanup when no resources to clean."""
        orchestrator._driver_manager = None
        orchestrator._proxy = None

        # Should not raise
        orchestrator._cleanup()


class TestHybridScanOrchestratorIntegration:
    """Integration test cases."""

    @pytest.fixture
    def mock_config(self):
        config = MagicMock()
        config.get.side_effect = lambda key, default=None: {
            'user_name': 'test_user',
            'password': 'test_pass',
            'target_http': 'https://example.com',
            'cookies_file': 'cookies.json'
        }.get(key, default)
        config.load_timing_config.return_value = {'screenshot': {'enabled': False}}
        return config

    def test_full_flow_simulation(self, mock_config):
        """Test full flow with mocked components."""
        orchestrator = HybridScanOrchestrator(mock_config, mode=HybridMode.DURATION)

        # Mock internal methods to simulate successful flow
        orchestrator._initialize_and_login = MagicMock(return_value=True)
        orchestrator._scan_payloads = MagicMock(return_value=[
            PayloadData(1, "Course 1", "Program 1", {}, target_time=60)
        ])
        orchestrator._cleanup = MagicMock()

        # Execute with auto_select
        result = orchestrator.execute(auto_select=True)

        # Verify the flow
        orchestrator._initialize_and_login.assert_called_once()
        orchestrator._scan_payloads.assert_called_once()
        orchestrator._cleanup.assert_called_once()

    def test_login_failure_handling(self, mock_config):
        """Test handling of login failure."""
        orchestrator = HybridScanOrchestrator(mock_config)

        # Mock login to fail
        orchestrator._initialize_and_login = MagicMock(return_value=False)
        orchestrator._cleanup = MagicMock()

        result = orchestrator.execute()

        assert result.success is False
        assert "登入失敗" in result.error

    def test_no_payloads_handling(self, mock_config):
        """Test handling when no payloads are captured."""
        orchestrator = HybridScanOrchestrator(mock_config)

        orchestrator._initialize_and_login = MagicMock(return_value=True)
        orchestrator._scan_payloads = MagicMock(return_value=[])
        orchestrator._cleanup = MagicMock()

        result = orchestrator.execute()

        assert result.success is False
        assert "Payload" in result.error
