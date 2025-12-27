# -*- coding: utf-8 -*-
"""
Unit Tests for Scroll Utilities.

Tests the multi-strategy scroll functionality.
"""

import pytest
from unittest.mock import MagicMock, patch, call

from src.utils.scroll_utils import (
    scroll_to_bottom_multi_strategy,
    scroll_to_element,
    scroll_to_top,
    get_scroll_position,
    _get_scroll_environment,
    _scroll_modal,
    _scroll_container,
    _scroll_window,
    MODAL_SELECTORS,
    SCROLL_CONTAINER_SELECTORS,
)


class TestScrollToBottomMultiStrategy:
    """Test cases for scroll_to_bottom_multi_strategy function."""

    @pytest.fixture
    def mock_driver(self):
        """Create a mock WebDriver."""
        driver = MagicMock()
        # Default scroll environment
        driver.execute_script.side_effect = self._default_script_handler
        return driver

    def _default_script_handler(self, script, *args):
        """Default handler for execute_script calls."""
        if 'bodyHeight' in script:
            return {
                'bodyHeight': 1000,
                'docHeight': 1000,
                'viewHeight': 800,
                'isBodyLocked': False,
                'activeModal': None,
                'hasModalScroll': False,
                'scrollContainer': None
            }
        elif 'innerHeight' in script:
            return 800
        elif 'scrollHeight' in script or 'Math.max' in script:
            return 1000
        elif 'pageXOffset' in script:
            return {'x': 0, 'y': 500}
        return None

    def test_basic_scroll(self, mock_driver):
        """Test basic scroll functionality."""
        # Make height stable to end quickly
        mock_driver.execute_script.side_effect = self._stable_height_handler

        scroll_count = scroll_to_bottom_multi_strategy(
            mock_driver,
            max_scrolls=5,
            wait_time=0.1
        )

        assert scroll_count > 0
        assert mock_driver.execute_script.called

    def _stable_height_handler(self, script, *args):
        """Handler that returns stable height."""
        if 'bodyHeight' in script:
            return {
                'bodyHeight': 1000,
                'docHeight': 1000,
                'viewHeight': 800,
                'isBodyLocked': False,
                'activeModal': None,
                'hasModalScroll': False,
                'scrollContainer': None
            }
        elif 'innerHeight' in script:
            return 800
        elif 'scrollHeight' in script or 'Math.max' in script:
            return 1000  # Always same height = stable
        return None

    def test_modal_scroll(self, mock_driver):
        """Test scroll when modal is active."""
        def modal_handler(script, *args):
            if 'bodyHeight' in script:
                return {
                    'bodyHeight': 1000,
                    'docHeight': 1000,
                    'viewHeight': 800,
                    'isBodyLocked': True,
                    'activeModal': '.modal',
                    'hasModalScroll': True,
                    'scrollContainer': None
                }
            elif 'innerHeight' in script:
                return 800
            elif 'scrollHeight' in script or 'Math.max' in script:
                return 1000
            return None

        mock_driver.execute_script.side_effect = modal_handler

        scroll_count = scroll_to_bottom_multi_strategy(
            mock_driver,
            max_scrolls=3,
            wait_time=0.1
        )

        assert scroll_count > 0

    def test_locked_body_with_container(self, mock_driver):
        """Test scroll when body is locked but container exists."""
        def locked_handler(script, *args):
            if 'bodyHeight' in script:
                return {
                    'bodyHeight': 1000,
                    'docHeight': 1000,
                    'viewHeight': 800,
                    'isBodyLocked': True,
                    'activeModal': None,
                    'hasModalScroll': False,
                    'scrollContainer': '.main-container'
                }
            elif 'innerHeight' in script:
                return 800
            elif 'scrollHeight' in script or 'Math.max' in script:
                return 1000
            return None

        mock_driver.execute_script.side_effect = locked_handler

        scroll_count = scroll_to_bottom_multi_strategy(
            mock_driver,
            max_scrolls=3,
            wait_time=0.1
        )

        assert scroll_count > 0

    def test_max_scrolls_limit(self, mock_driver):
        """Test that max_scrolls is respected."""
        call_count = [0]

        def counting_handler(script, *args):
            if 'bodyHeight' in script:
                return {
                    'bodyHeight': 1000,
                    'docHeight': 1000,
                    'viewHeight': 800,
                    'isBodyLocked': False,
                    'activeModal': None,
                    'hasModalScroll': False,
                    'scrollContainer': None
                }
            elif 'innerHeight' in script:
                return 800
            elif 'scrollHeight' in script or 'Math.max' in script:
                # Height keeps increasing, never stable
                call_count[0] += 1
                return 1000 + call_count[0] * 100
            return None

        mock_driver.execute_script.side_effect = counting_handler

        max_scrolls = 5
        scroll_count = scroll_to_bottom_multi_strategy(
            mock_driver,
            max_scrolls=max_scrolls,
            wait_time=0.05
        )

        assert scroll_count <= max_scrolls

    def test_exam_page_flag(self, mock_driver):
        """Test exam_page parameter."""
        mock_driver.execute_script.side_effect = self._stable_height_handler

        # Should work with exam_page=True
        scroll_count = scroll_to_bottom_multi_strategy(
            mock_driver,
            max_scrolls=3,
            wait_time=0.1,
            exam_page=True
        )

        assert scroll_count > 0


class TestScrollEnvironment:
    """Test cases for _get_scroll_environment function."""

    def test_normal_page(self):
        """Test scroll environment detection on normal page."""
        driver = MagicMock()
        driver.execute_script.return_value = {
            'bodyHeight': 2000,
            'docHeight': 2000,
            'viewHeight': 800,
            'isBodyLocked': False,
            'activeModal': None,
            'hasModalScroll': False,
            'scrollContainer': None
        }

        env = _get_scroll_environment(driver)

        assert env['bodyHeight'] == 2000
        assert env['isBodyLocked'] is False
        assert env['activeModal'] is None

    def test_error_handling(self):
        """Test error handling when script fails."""
        driver = MagicMock()
        driver.execute_script.side_effect = Exception("Script error")

        env = _get_scroll_environment(driver)

        assert env['bodyHeight'] == 0
        assert env['isBodyLocked'] is False


class TestHelperFunctions:
    """Test cases for helper scroll functions."""

    def test_scroll_to_element(self):
        """Test scroll_to_element function."""
        driver = MagicMock()
        element = MagicMock()

        scroll_to_element(driver, element, block='center', behavior='smooth')

        driver.execute_script.assert_called_once()
        call_args = driver.execute_script.call_args
        assert 'scrollIntoView' in call_args[0][0]
        assert element == call_args[0][1]

    def test_scroll_to_top(self):
        """Test scroll_to_top function."""
        driver = MagicMock()

        scroll_to_top(driver)

        driver.execute_script.assert_called_once_with("window.scrollTo(0, 0);")

    def test_get_scroll_position(self):
        """Test get_scroll_position function."""
        driver = MagicMock()
        driver.execute_script.return_value = {'x': 100, 'y': 500}

        position = get_scroll_position(driver)

        assert position['x'] == 100
        assert position['y'] == 500


class TestScrollInternalFunctions:
    """Test internal scroll helper functions."""

    def test_scroll_modal(self):
        """Test _scroll_modal function."""
        driver = MagicMock()

        _scroll_modal(driver, '.modal')

        driver.execute_script.assert_called_once()
        assert '.modal' in driver.execute_script.call_args[0][0]

    def test_scroll_container(self):
        """Test _scroll_container function."""
        driver = MagicMock()

        _scroll_container(driver, '.main-container')

        driver.execute_script.assert_called_once()
        assert '.main-container' in driver.execute_script.call_args[0][0]

    def test_scroll_window(self):
        """Test _scroll_window function."""
        driver = MagicMock()

        _scroll_window(driver)

        driver.execute_script.assert_called_once_with(
            "window.scrollTo(0, document.body.scrollHeight);"
        )


class TestConstants:
    """Test scroll-related constants."""

    def test_modal_selectors_not_empty(self):
        """Test that modal selectors list is not empty."""
        assert len(MODAL_SELECTORS) > 0

    def test_container_selectors_not_empty(self):
        """Test that container selectors list is not empty."""
        assert len(SCROLL_CONTAINER_SELECTORS) > 0

    def test_exam_selectors_included(self):
        """Test that exam-specific selectors are included."""
        all_selectors = ' '.join(SCROLL_CONTAINER_SELECTORS)
        assert 'exam' in all_selectors.lower() or 'fullscreen' in all_selectors.lower()
