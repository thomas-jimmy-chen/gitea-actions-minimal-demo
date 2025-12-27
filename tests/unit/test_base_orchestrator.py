# -*- coding: utf-8 -*-
"""
Unit Tests for BaseOrchestrator.

Tests the abstract base class and template method pattern.
"""

import pytest
from unittest.mock import MagicMock, patch
import sys

# Save original modules before mocking (for test isolation)
_orig_execution_wrapper = sys.modules.get('src.utils.execution_wrapper')
_orig_feature_flags = sys.modules.get('src.config.feature_flags')

# Mock the execution_wrapper and feature_flags before importing
sys.modules['src.utils.execution_wrapper'] = MagicMock()
sys.modules['src.config.feature_flags'] = MagicMock()

# Create mock ExecutionWrapper class
mock_wrapper_instance = MagicMock()
mock_wrapper_instance.__enter__ = MagicMock(return_value=mock_wrapper_instance)
mock_wrapper_instance.__exit__ = MagicMock(return_value=False)
mock_wrapper_instance.is_tracking_enabled.return_value = True
mock_wrapper_instance.get_stats.return_value = {'total_time': 100}

MockExecutionWrapper = MagicMock(return_value=mock_wrapper_instance)
sys.modules['src.utils.execution_wrapper'].ExecutionWrapper = MockExecutionWrapper

# Mock feature_enabled
sys.modules['src.config.feature_flags'].feature_enabled = MagicMock(return_value=False)

# Now import the module under test
from src.orchestrators.base_orchestrator import (
    BaseOrchestrator,
    OrchestratorResult,
    OrchestratorPhase,
)


@pytest.fixture(scope="module", autouse=True)
def restore_modules():
    """Restore original modules after all tests in this module complete."""
    yield
    # Cleanup: restore original modules
    if _orig_execution_wrapper is not None:
        sys.modules['src.utils.execution_wrapper'] = _orig_execution_wrapper
    elif 'src.utils.execution_wrapper' in sys.modules:
        del sys.modules['src.utils.execution_wrapper']
    if _orig_feature_flags is not None:
        sys.modules['src.config.feature_flags'] = _orig_feature_flags
    elif 'src.config.feature_flags' in sys.modules:
        del sys.modules['src.config.feature_flags']


class ConcreteOrchestrator(BaseOrchestrator):
    """Concrete implementation for testing."""

    def __init__(self, config, name="TestOrchestrator", **kwargs):
        super().__init__(config, name, **kwargs)
        self.before_called = False
        self.do_called = False
        self.after_called = False
        self.error_called = False
        self.should_fail = False
        self.return_data = {}

    def _before_execute(self, **kwargs):
        super()._before_execute(**kwargs)
        self.before_called = True

    def _do_execute(self, **kwargs) -> OrchestratorResult:
        self.do_called = True
        if self.should_fail:
            raise RuntimeError("Simulated failure")
        return OrchestratorResult(
            success=True,
            data=self.return_data
        )

    def _after_execute(self, result, **kwargs):
        super()._after_execute(result, **kwargs)
        self.after_called = True

    def _on_error(self, error, **kwargs):
        super()._on_error(error, **kwargs)
        self.error_called = True


class TestOrchestratorResult:
    """Test cases for OrchestratorResult dataclass."""

    def test_successful_result(self):
        """Test creating a successful result."""
        result = OrchestratorResult(
            success=True,
            data={'key': 'value'}
        )

        assert result.success is True
        assert result.data == {'key': 'value'}
        assert result.error is None
        assert result.phase == OrchestratorPhase.COMPLETED

    def test_failed_result(self):
        """Test creating a failed result."""
        result = OrchestratorResult(
            success=False,
            error="Something went wrong",
            phase=OrchestratorPhase.FAILED
        )

        assert result.success is False
        assert result.error == "Something went wrong"
        assert result.phase == OrchestratorPhase.FAILED

    def test_to_dict(self):
        """Test converting result to dictionary."""
        result = OrchestratorResult(
            success=True,
            data={'count': 5},
            metrics={'time': 100}
        )

        result_dict = result.to_dict()

        assert result_dict['success'] is True
        assert result_dict['data'] == {'count': 5}
        assert result_dict['metrics'] == {'time': 100}
        assert result_dict['phase'] == 'completed'

    def test_default_values(self):
        """Test default values for optional fields."""
        result = OrchestratorResult(success=True)

        assert result.data == {}
        assert result.error is None
        assert result.metrics == {}


class TestOrchestratorPhase:
    """Test cases for OrchestratorPhase enum."""

    def test_phase_values(self):
        """Test that all phases have string values."""
        assert OrchestratorPhase.INITIALIZING.value == "initializing"
        assert OrchestratorPhase.BEFORE_EXECUTE.value == "before_execute"
        assert OrchestratorPhase.EXECUTING.value == "executing"
        assert OrchestratorPhase.AFTER_EXECUTE.value == "after_execute"
        assert OrchestratorPhase.COMPLETED.value == "completed"
        assert OrchestratorPhase.FAILED.value == "failed"


class TestBaseOrchestrator:
    """Test cases for BaseOrchestrator class."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration."""
        config = MagicMock()
        config.load_timing_config.return_value = {'screenshot': {'enabled': False}}
        return config

    @pytest.fixture
    def orchestrator(self, mock_config):
        """Create a concrete orchestrator instance."""
        return ConcreteOrchestrator(mock_config)

    def test_initialization(self, mock_config):
        """Test orchestrator initialization."""
        orch = ConcreteOrchestrator(mock_config, "Test")

        assert orch.name == "Test"
        assert orch.config == mock_config
        assert orch.current_phase == OrchestratorPhase.INITIALIZING
        assert orch.wrapper is None

    def test_execute_calls_all_hooks(self, orchestrator):
        """Test that execute() calls all hook methods in order."""
        result = orchestrator.execute()

        assert orchestrator.before_called is True
        assert orchestrator.do_called is True
        assert orchestrator.after_called is True
        assert result.success is True

    def test_execute_passes_kwargs(self, orchestrator):
        """Test that kwargs are passed to hook methods."""
        received_kwargs = {}

        def capture_do_execute(**kwargs):
            received_kwargs.update(kwargs)
            return OrchestratorResult(success=True)

        orchestrator._do_execute = capture_do_execute
        orchestrator.execute(param1="value1", param2=42)

        assert received_kwargs.get('param1') == "value1"
        assert received_kwargs.get('param2') == 42

    def test_execute_handles_error(self, orchestrator):
        """Test that execute() handles exceptions properly."""
        orchestrator.should_fail = True

        result = orchestrator.execute()

        assert result.success is False
        assert "Simulated failure" in result.error
        assert result.phase == OrchestratorPhase.FAILED
        assert orchestrator.error_called is True

    def test_execute_returns_data(self, orchestrator):
        """Test that execute() returns data from _do_execute."""
        orchestrator.return_data = {'items': [1, 2, 3], 'count': 3}

        result = orchestrator.execute()

        assert result.success is True
        assert result.data == {'items': [1, 2, 3], 'count': 3}

    def test_current_phase_property(self, orchestrator):
        """Test current_phase property."""
        assert orchestrator.current_phase == OrchestratorPhase.INITIALIZING

    def test_repr(self, orchestrator):
        """Test string representation."""
        repr_str = repr(orchestrator)

        assert "ConcreteOrchestrator" in repr_str
        assert "TestOrchestrator" in repr_str

    def test_context_management(self, orchestrator):
        """Test execution context get/set."""
        orchestrator.set_context('key1', 'value1')

        assert orchestrator.get_context('key1') == 'value1'
        assert orchestrator.get_context('missing', 'default') == 'default'


class TestOrchestratorWrapperIntegration:
    """Test cases for wrapper method delegation."""

    @pytest.fixture
    def mock_config(self):
        config = MagicMock()
        config.load_timing_config.return_value = {'screenshot': {'enabled': False}}
        return config

    @pytest.fixture
    def orchestrator(self, mock_config):
        return ConcreteOrchestrator(mock_config)

    def test_start_phase_delegates_to_wrapper(self, orchestrator):
        """Test that start_phase delegates to wrapper."""
        mock_wrapper = MagicMock()
        orchestrator.wrapper = mock_wrapper

        orchestrator.start_phase("test_phase")

        mock_wrapper.start_phase.assert_called_once_with("test_phase")

    def test_end_phase_delegates_to_wrapper(self, orchestrator):
        """Test that end_phase delegates to wrapper."""
        mock_wrapper = MagicMock()
        orchestrator.wrapper = mock_wrapper

        orchestrator.end_phase("test_phase")

        mock_wrapper.end_phase.assert_called_once_with("test_phase")

    def test_start_item_delegates_to_wrapper(self, orchestrator):
        """Test that start_item delegates to wrapper."""
        mock_wrapper = MagicMock()
        orchestrator.wrapper = mock_wrapper

        orchestrator.start_item("course1", "program1", "course")

        mock_wrapper.start_item.assert_called_once_with(
            "course1", "program1", "course"
        )

    def test_end_item_delegates_to_wrapper(self, orchestrator):
        """Test that end_item delegates to wrapper."""
        mock_wrapper = MagicMock()
        orchestrator.wrapper = mock_wrapper

        orchestrator.end_item("course1")

        mock_wrapper.end_item.assert_called_once_with("course1")

    def test_record_delay_delegates_to_wrapper(self, orchestrator):
        """Test that record_delay delegates to wrapper."""
        mock_wrapper = MagicMock()
        orchestrator.wrapper = mock_wrapper

        orchestrator.record_delay(5.0, "waiting")

        mock_wrapper.record_delay.assert_called_once_with(5.0, "waiting")

    def test_take_screenshot_delegates_to_wrapper(self, orchestrator):
        """Test that take_screenshot delegates to wrapper."""
        mock_wrapper = MagicMock()
        mock_wrapper.take_screenshot.return_value = "/path/to/screenshot.png"
        orchestrator.wrapper = mock_wrapper
        mock_driver = MagicMock()

        result = orchestrator.take_screenshot(mock_driver, "item1", 1)

        mock_wrapper.take_screenshot.assert_called_once_with(mock_driver, "item1", 1)
        assert result == "/path/to/screenshot.png"

    def test_methods_safe_when_no_wrapper(self, orchestrator):
        """Test that wrapper methods don't fail when wrapper is None."""
        orchestrator.wrapper = None

        # These should not raise exceptions
        orchestrator.start_phase("test")
        orchestrator.end_phase("test")
        orchestrator.start_item("item")
        orchestrator.end_item("item")
        orchestrator.record_delay(1.0)
        result = orchestrator.take_screenshot(MagicMock(), "item")

        assert result is None


class TestOrchestratorAbstraction:
    """Test that BaseOrchestrator is properly abstract."""

    def test_cannot_instantiate_base_class(self):
        """Test that BaseOrchestrator cannot be instantiated directly."""
        config = MagicMock()

        with pytest.raises(TypeError):
            BaseOrchestrator(config, "Test")

    def test_must_implement_do_execute(self):
        """Test that subclass must implement _do_execute."""

        class IncompleteOrchestrator(BaseOrchestrator):
            pass

        config = MagicMock()

        with pytest.raises(TypeError):
            IncompleteOrchestrator(config, "Test")
