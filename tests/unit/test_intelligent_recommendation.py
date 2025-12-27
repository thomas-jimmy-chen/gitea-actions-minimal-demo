# -*- coding: utf-8 -*-
"""
Unit Tests for IntelligentRecommendationOrchestrator.

Tests the intelligent recommendation workflow orchestration.
"""

import pytest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os
import json

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

from src.orchestrators.intelligent_recommendation import (
    IntelligentRecommendationOrchestrator,
    ScanResult,
)
from src.orchestrators.base_orchestrator import OrchestratorResult


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


class TestScanResult:
    """Test cases for ScanResult dataclass."""

    def test_default_values(self):
        """Test default values."""
        result = ScanResult()

        assert result.programs == []
        assert result.available_courses == []
        assert result.recommendations == []
        assert result.error is None

    def test_with_data(self):
        """Test with actual data."""
        result = ScanResult(
            programs=[{'name': 'Program 1'}],
            recommendations=[{'name': 'Course 1'}],
            error=None
        )

        assert len(result.programs) == 1
        assert len(result.recommendations) == 1


class TestIntelligentRecommendationOrchestrator:
    """Test cases for IntelligentRecommendationOrchestrator."""

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
    def mock_scheduler(self):
        """Create a mock scheduler."""
        scheduler = MagicMock()
        scheduler.scheduled_courses = []
        scheduler.save_schedule = MagicMock()
        return scheduler

    @pytest.fixture
    def orchestrator(self, mock_config):
        """Create an orchestrator instance."""
        return IntelligentRecommendationOrchestrator(mock_config)

    def test_initialization(self, mock_config):
        """Test orchestrator initialization."""
        orch = IntelligentRecommendationOrchestrator(mock_config)

        assert orch.name == "智能推薦"
        assert orch.courses_config_path == 'data/courses.json'
        assert orch.schedule_file == 'data/schedule.json'

    def test_custom_paths(self, mock_config):
        """Test with custom config paths."""
        orch = IntelligentRecommendationOrchestrator(
            mock_config,
            courses_config_path='custom/courses.json',
            schedule_file='custom/schedule.json'
        )

        assert orch.courses_config_path == 'custom/courses.json'
        assert orch.schedule_file == 'custom/schedule.json'

    def test_normalize_text(self, orchestrator):
        """Test text normalization."""
        assert orchestrator._normalize_text("Hello World") == "helloworld"
        assert orchestrator._normalize_text("  spaces  ") == "spaces"
        assert orchestrator._normalize_text("UPPERCASE") == "uppercase"
        assert orchestrator._normalize_text("") == ""
        assert orchestrator._normalize_text(None) == ""

    def test_match_course_exact(self, orchestrator):
        """Test exact course matching."""
        courses = [
            {'lesson_name': 'Python 基礎課程'},
            {'lesson_name': 'JavaScript 進階'},
        ]

        result = orchestrator._match_course('Python 基礎課程', courses)

        assert result is not None
        assert result['lesson_name'] == 'Python 基礎課程'

    def test_match_course_contains(self, orchestrator):
        """Test contains matching."""
        courses = [
            {'lesson_name': 'Python 基礎課程入門指南'},
        ]

        result = orchestrator._match_course('Python 基礎課程', courses)

        assert result is not None

    def test_match_course_fuzzy(self, orchestrator):
        """Test fuzzy matching above 90%."""
        courses = [
            {'lesson_name': 'Python基礎課程'},
        ]

        # Very similar (should match)
        result = orchestrator._match_course('Python 基礎課程', courses)
        assert result is not None

    def test_match_course_no_match(self, orchestrator):
        """Test when no match is found."""
        courses = [
            {'lesson_name': 'Java 進階課程'},
        ]

        result = orchestrator._match_course('Python 基礎', courses)

        assert result is None

    def test_is_duplicate_course(self, orchestrator, mock_scheduler):
        """Test duplicate detection for courses."""
        mock_scheduler.scheduled_courses = [
            {
                'program_name': 'Program A',
                'lesson_name': 'Lesson 1',
                'course_id': 123,
                'course_type': 'course'
            }
        ]

        config_item = {
            'program_name': 'Program A',
            'lesson_name': 'Lesson 1',
            'course_id': 123,
            'course_type': 'course'
        }

        assert orchestrator._is_duplicate(mock_scheduler, config_item) is True

    def test_is_duplicate_exam(self, orchestrator, mock_scheduler):
        """Test duplicate detection for exams."""
        mock_scheduler.scheduled_courses = [
            {
                'program_name': 'Program A',
                'exam_name': 'Exam 1',
                'course_type': 'exam'
            }
        ]

        config_item = {
            'program_name': 'Program A',
            'exam_name': 'Exam 1',
            'course_type': 'exam'
        }

        assert orchestrator._is_duplicate(mock_scheduler, config_item) is True

    def test_is_not_duplicate(self, orchestrator, mock_scheduler):
        """Test when item is not duplicate."""
        mock_scheduler.scheduled_courses = [
            {
                'program_name': 'Program A',
                'lesson_name': 'Lesson 1',
                'course_id': 123
            }
        ]

        config_item = {
            'program_name': 'Program A',
            'lesson_name': 'Lesson 2',
            'course_id': 456
        }

        assert orchestrator._is_duplicate(mock_scheduler, config_item) is False


class TestCleanupMethods:
    """Test cases for cleanup methods."""

    @pytest.fixture
    def mock_config(self):
        config = MagicMock()
        config.get.return_value = None
        config.load_timing_config.return_value = {'screenshot': {'enabled': False}}
        return config

    @pytest.fixture
    def orchestrator(self, mock_config):
        return IntelligentRecommendationOrchestrator(mock_config)

    @patch('os.path.exists')
    @patch('os.remove')
    def test_cleanup_temp_files(self, mock_remove, mock_exists, orchestrator):
        """Test temporary file cleanup."""
        mock_exists.return_value = True

        orchestrator._cleanup_temp_files()

        # Should try to remove all temp files
        assert mock_remove.call_count == len(orchestrator.TEMP_FILES)

    @patch('os.path.exists')
    @patch('os.remove')
    def test_cleanup_temp_files_file_not_exists(
        self, mock_remove, mock_exists, orchestrator
    ):
        """Test cleanup when files don't exist."""
        mock_exists.return_value = False

        orchestrator._cleanup_temp_files()

        mock_remove.assert_not_called()

    @patch('os.path.exists')
    @patch('os.remove')
    def test_cleanup_before_execution(
        self, mock_remove, mock_exists, orchestrator
    ):
        """Test pre-execution cleanup."""
        mock_exists.return_value = True
        mock_scheduler = MagicMock()
        mock_scheduler.scheduled_courses = [{'course': 1}]

        orchestrator._cleanup_before_execution(mock_scheduler)

        assert mock_scheduler.scheduled_courses == []


class TestMatchWithConfig:
    """Test cases for config matching."""

    @pytest.fixture
    def mock_config(self):
        config = MagicMock()
        config.get.return_value = None
        config.load_timing_config.return_value = {'screenshot': {'enabled': False}}
        return config

    @pytest.fixture
    def orchestrator(self, mock_config):
        return IntelligentRecommendationOrchestrator(mock_config)

    def test_match_with_config_success(self, orchestrator):
        """Test successful config matching."""
        available_courses = [
            {
                'program_name': 'Program A',
                'courses': [{'name': 'Python 基礎'}],
                'exams': [{'name': '期末考試'}]
            }
        ]

        config_data = {
            'courses': [
                {'lesson_name': 'Python 基礎', 'course_id': 1},
                {'exam_name': '期末考試', 'enable_auto_answer': True}
            ]
        }

        with patch('builtins.open', mock_open(read_data=json.dumps(config_data))):
            result = orchestrator._match_with_config(available_courses)

        assert len(result) == 2
        # Check course match
        course_match = next(r for r in result if r['type'] == 'course')
        assert course_match['item_name'] == 'Python 基礎'

        # Check exam match
        exam_match = next(r for r in result if r['type'] == 'exam')
        assert exam_match['item_name'] == '期末考試'
        assert exam_match['auto_answer'] is True

    def test_match_with_config_no_matches(self, orchestrator):
        """Test when no courses match config."""
        available_courses = [
            {
                'program_name': 'Program A',
                'courses': [{'name': 'Unknown Course'}],
                'exams': []
            }
        ]

        config_data = {
            'courses': [
                {'lesson_name': 'Python 基礎'}
            ]
        }

        with patch('builtins.open', mock_open(read_data=json.dumps(config_data))):
            result = orchestrator._match_with_config(available_courses)

        assert len(result) == 0

    def test_match_with_config_file_error(self, orchestrator):
        """Test handling of config file errors."""
        available_courses = [
            {
                'program_name': 'Program A',
                'courses': [{'name': 'Test'}],
                'exams': []
            }
        ]

        with patch('builtins.open', side_effect=FileNotFoundError()):
            result = orchestrator._match_with_config(available_courses)

        assert result == []


class TestAddToSchedule:
    """Test cases for add_to_schedule method."""

    @pytest.fixture
    def mock_config(self):
        config = MagicMock()
        config.get.return_value = None
        config.load_timing_config.return_value = {'screenshot': {'enabled': False}}
        return config

    @pytest.fixture
    def orchestrator(self, mock_config):
        return IntelligentRecommendationOrchestrator(mock_config)

    def test_add_to_schedule_success(self, orchestrator):
        """Test successful schedule addition."""
        scheduler = MagicMock()
        scheduler.scheduled_courses = []

        recommendations = [
            {
                'item_name': 'Course 1',
                'config': {'lesson_name': 'Course 1', 'course_id': 1}
            },
            {
                'item_name': 'Course 2',
                'config': {'lesson_name': 'Course 2', 'course_id': 2}
            }
        ]

        count = orchestrator._add_to_schedule(scheduler, recommendations)

        assert count == 2
        assert len(scheduler.scheduled_courses) == 2

    def test_add_to_schedule_skip_duplicates(self, orchestrator):
        """Test that duplicates are skipped."""
        scheduler = MagicMock()
        scheduler.scheduled_courses = [
            {'lesson_name': 'Course 1', 'course_id': 1, 'program_name': 'P1'}
        ]

        recommendations = [
            {
                'item_name': 'Course 1',
                'config': {
                    'lesson_name': 'Course 1',
                    'course_id': 1,
                    'program_name': 'P1'
                }
            },
            {
                'item_name': 'Course 2',
                'config': {
                    'lesson_name': 'Course 2',
                    'course_id': 2,
                    'program_name': 'P1'
                }
            }
        ]

        count = orchestrator._add_to_schedule(scheduler, recommendations)

        assert count == 1  # Only Course 2 added

    def test_add_to_schedule_no_scheduler(self, orchestrator):
        """Test when scheduler is None."""
        recommendations = [
            {'item_name': 'Course 1', 'config': {}}
        ]

        count = orchestrator._add_to_schedule(None, recommendations)

        assert count == 0
