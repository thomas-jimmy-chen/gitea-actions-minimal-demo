# -*- coding: utf-8 -*-
"""
Integration Tests for Menu Orchestrator Routing.

Tests that menu.py correctly routes to orchestrators when feature flags are enabled.
"""

import pytest
from unittest.mock import MagicMock, patch
import sys


class TestMenuOrchestratorRouting:
    """Test cases for menu orchestrator routing."""

    @pytest.fixture
    def mock_feature_flags(self):
        """Mock feature flags module."""
        with patch('menu._use_orchestrators') as mock:
            yield mock

    @pytest.fixture
    def mock_config(self):
        """Mock config loader."""
        with patch('menu._get_config') as mock:
            config = MagicMock()
            config.get.return_value = 'test_value'
            config.load_timing_config.return_value = {'screenshot': {'enabled': False}}
            mock.return_value = config
            yield mock

    def test_intelligent_recommendation_uses_orchestrator_when_enabled(
        self, mock_feature_flags, mock_config
    ):
        """Test that intelligent recommendation uses orchestrator when flag is enabled."""
        mock_feature_flags.return_value = True

        # Mock the orchestrator (patch at the import location)
        with patch(
            'src.orchestrators.IntelligentRecommendationOrchestrator'
        ) as mock_orch_class:
            mock_orch = MagicMock()
            mock_orch.execute.return_value = MagicMock(
                success=True,
                data={'scanned_count': 5, 'executed_count': 3}
            )
            mock_orch_class.return_value = mock_orch

            # Import after patching
            from menu import CourseScheduler

            scheduler = CourseScheduler()

            # Mock input to skip confirmation
            with patch('builtins.input', side_effect=['y', '']):
                scheduler.handle_intelligent_recommendation()

            # Verify orchestrator was called
            mock_orch.execute.assert_called_once()

    def test_intelligent_recommendation_uses_legacy_when_disabled(
        self, mock_feature_flags
    ):
        """Test that intelligent recommendation uses legacy when flag is disabled."""
        mock_feature_flags.return_value = False

        from menu import CourseScheduler

        scheduler = CourseScheduler()

        # Mock the legacy method
        scheduler._handle_intelligent_recommendation_legacy = MagicMock()

        # Mock input to skip confirmation
        with patch('builtins.input', side_effect=['y', '']):
            scheduler.handle_intelligent_recommendation()

        # Verify legacy method was called
        scheduler._handle_intelligent_recommendation_legacy.assert_called_once()

    def test_hybrid_duration_uses_orchestrator_when_enabled(
        self, mock_feature_flags, mock_config
    ):
        """Test that hybrid duration mode uses orchestrator when flag is enabled."""
        mock_feature_flags.return_value = True

        with patch('src.orchestrators.HybridScanOrchestrator') as mock_orch_class:
            with patch('src.orchestrators.HybridMode') as mock_mode:
                mock_orch = MagicMock()
                mock_orch.execute.return_value = MagicMock(
                    success=True,
                    data={
                        'payloads_count': 10,
                        'selected_count': 5,
                        'sent_count': 5,
                        'verified_count': 5
                    }
                )
                mock_orch_class.return_value = mock_orch

                from menu import CourseScheduler

                scheduler = CourseScheduler()

                with patch('builtins.input', return_value=''):
                    scheduler._handle_hybrid_with_mode('duration')

                mock_orch.execute.assert_called_once()

    def test_hybrid_batch_uses_orchestrator_when_enabled(
        self, mock_feature_flags, mock_config
    ):
        """Test that hybrid batch mode uses orchestrator when flag is enabled."""
        mock_feature_flags.return_value = True

        with patch('src.orchestrators.HybridScanOrchestrator') as mock_orch_class:
            with patch('src.orchestrators.HybridMode'):
                mock_orch = MagicMock()
                mock_orch.execute.return_value = MagicMock(success=True, data={})
                mock_orch_class.return_value = mock_orch

                from menu import CourseScheduler

                scheduler = CourseScheduler()

                with patch('builtins.input', return_value=''):
                    scheduler._handle_hybrid_with_mode('batch')

                mock_orch.execute.assert_called_once()

    def test_hybrid_exam_uses_orchestrator_when_enabled(
        self, mock_feature_flags, mock_config
    ):
        """Test that hybrid exam mode uses orchestrator when flag is enabled."""
        mock_feature_flags.return_value = True

        with patch('src.orchestrators.HybridScanOrchestrator') as mock_orch_class:
            with patch('src.orchestrators.HybridMode'):
                mock_orch = MagicMock()
                mock_orch.execute.return_value = MagicMock(success=True, data={})
                mock_orch_class.return_value = mock_orch

                from menu import CourseScheduler

                scheduler = CourseScheduler()

                with patch('builtins.input', return_value=''):
                    scheduler._handle_hybrid_with_mode('exam')

                mock_orch.execute.assert_called_once()

    def test_hybrid_uses_legacy_when_disabled(self, mock_feature_flags):
        """Test that hybrid mode uses legacy when flag is disabled."""
        mock_feature_flags.return_value = False

        from menu import CourseScheduler

        scheduler = CourseScheduler()

        # Mock legacy methods
        scheduler.handle_hybrid_duration_send = MagicMock()
        scheduler.handle_hybrid_batch_mode = MagicMock()
        scheduler.handle_hybrid_exam_auto_answer = MagicMock()

        scheduler._handle_hybrid_with_mode('duration')
        scheduler.handle_hybrid_duration_send.assert_called_once()

        scheduler._handle_hybrid_with_mode('batch')
        scheduler.handle_hybrid_batch_mode.assert_called_once()

        scheduler._handle_hybrid_with_mode('exam')
        scheduler.handle_hybrid_exam_auto_answer.assert_called_once()


class TestOrchestratorFallback:
    """Test cases for orchestrator error fallback."""

    @pytest.fixture
    def mock_feature_flags_enabled(self):
        """Mock feature flags to be enabled."""
        with patch('menu._use_orchestrators', return_value=True):
            yield

    def test_fallback_to_legacy_on_orchestrator_error(self, mock_feature_flags_enabled):
        """Test fallback to legacy when orchestrator fails and fallback is enabled."""
        with patch('menu._get_config') as mock_config:
            mock_config.return_value = MagicMock()

            with patch(
                'src.orchestrators.IntelligentRecommendationOrchestrator'
            ) as mock_orch:
                # Make orchestrator raise an error
                mock_orch.side_effect = Exception("Orchestrator failed")

                # Mock feature_enabled for fallback check
                with patch('src.config.feature_flags.feature_enabled', return_value=True):
                    from menu import CourseScheduler

                    scheduler = CourseScheduler()
                    scheduler._handle_intelligent_recommendation_legacy = MagicMock()

                    with patch('builtins.input', return_value=''):
                        scheduler._handle_intelligent_recommendation_orchestrator()

                    # Verify legacy was called as fallback
                    scheduler._handle_intelligent_recommendation_legacy.assert_called_once()
