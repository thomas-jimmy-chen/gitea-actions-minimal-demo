# -*- coding: utf-8 -*-
"""
Pytest Configuration and Shared Fixtures for EEBot Tests.

This module provides common fixtures and configuration for all tests.
Fixtures are automatically discovered by pytest.

Usage:
    # In any test file, fixtures are automatically available
    def test_something(mock_config, mock_driver):
        ...
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any
from unittest.mock import MagicMock, patch

import pytest

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# =============================================================================
# Configuration Fixtures
# =============================================================================

@pytest.fixture
def mock_config() -> MagicMock:
    """
    Create a mock configuration object.

    Returns:
        MagicMock object simulating ConfigLoader.
    """
    config = MagicMock()
    config.get.return_value = 'test_value'
    config.load_timing_config.return_value = {
        'screenshot': {'enabled': False}
    }

    # Common config values
    config.target_http = 'https://example.com'
    config.user_name = 'test_user'
    config.password = 'test_password'
    config.listen_host = '127.0.0.1'
    config.listen_port = 8899

    return config


@pytest.fixture
def config_dict() -> Dict[str, Any]:
    """
    Create a configuration dictionary for testing.

    Returns:
        Dictionary with common configuration values.
    """
    return {
        'target_http': 'https://example.com',
        'user_name': 'test_user',
        'password': 'test_password',
        'listen_host': '127.0.0.1',
        'listen_port': 8899,
        'modify_visits': True,
        'enable_auto_answer': True,
        'question_bank_mode': 'total_bank',
        'silent_mitm': True,
    }


# =============================================================================
# WebDriver Fixtures
# =============================================================================

@pytest.fixture
def mock_driver() -> MagicMock:
    """
    Create a mock Selenium WebDriver.

    Returns:
        MagicMock object simulating WebDriver.
    """
    driver = MagicMock()

    # Basic WebDriver methods
    driver.get.return_value = None
    driver.quit.return_value = None
    driver.close.return_value = None
    driver.refresh.return_value = None

    # Window methods
    driver.current_url = 'https://example.com/page'
    driver.title = 'Test Page'
    driver.page_source = '<html><body>Test</body></html>'

    # Element finding
    mock_element = MagicMock()
    mock_element.text = 'Test Element'
    mock_element.get_attribute.return_value = 'test_attribute'
    mock_element.is_displayed.return_value = True
    mock_element.is_enabled.return_value = True

    driver.find_element.return_value = mock_element
    driver.find_elements.return_value = [mock_element]

    # JavaScript execution
    driver.execute_script.return_value = None

    # Cookie management
    driver.get_cookies.return_value = [
        {'name': 'session', 'value': 'test_session_id'}
    ]

    return driver


@pytest.fixture
def mock_wait() -> MagicMock:
    """
    Create a mock WebDriverWait.

    Returns:
        MagicMock object simulating WebDriverWait.
    """
    wait = MagicMock()
    wait.until.return_value = MagicMock()
    return wait


# =============================================================================
# Proxy Fixtures
# =============================================================================

@pytest.fixture
def mock_proxy_manager() -> MagicMock:
    """
    Create a mock ProxyManager.

    Returns:
        MagicMock object simulating ProxyManager.
    """
    proxy = MagicMock()
    proxy.start.return_value = True
    proxy.stop.return_value = None
    proxy.is_running.return_value = True
    proxy.get_port.return_value = 8899
    return proxy


# =============================================================================
# Page Object Fixtures
# =============================================================================

@pytest.fixture
def mock_login_page() -> MagicMock:
    """
    Create a mock LoginPage.

    Returns:
        MagicMock object simulating LoginPage.
    """
    page = MagicMock()
    page.login.return_value = True
    page.is_logged_in.return_value = True
    page.try_cookie_login.return_value = True
    return page


@pytest.fixture
def mock_course_list_page() -> MagicMock:
    """
    Create a mock CourseListPage.

    Returns:
        MagicMock object simulating CourseListPage.
    """
    page = MagicMock()
    page.get_courses.return_value = [
        {'id': 1, 'name': 'Test Course 1', 'status': 'in_progress'},
        {'id': 2, 'name': 'Test Course 2', 'status': 'completed'},
    ]
    page.select_course.return_value = True
    return page


# =============================================================================
# Feature Flags Fixtures
# =============================================================================

@pytest.fixture
def reset_feature_flags():
    """
    Reset feature flags before and after each test.

    This fixture ensures clean state for feature flag tests.
    It also handles cases where the module may have been mocked by other tests.
    """
    import importlib

    # First, ensure we have the real module (not a mock)
    module_name = 'src.config.feature_flags'
    if module_name in sys.modules:
        module = sys.modules[module_name]
        if hasattr(module, '_mock_name') or 'MagicMock' in str(type(module)):
            del sys.modules[module_name]
            # Force reimport
            importlib.import_module(module_name)

    from src.config.feature_flags import FeatureFlags

    # Reset before test
    FeatureFlags.reset_instance()
    yield
    # Reset after test
    FeatureFlags.reset_instance()


@pytest.fixture
def feature_flags_enabled():
    """
    Enable all feature flags for testing new code paths.

    Returns:
        Dictionary of enabled flag names.
    """
    from src.config.feature_flags import get_feature_flags

    flags = get_feature_flags()
    enabled_flags = [
        'use_login_service',
        'use_scroll_utils',
        'use_browser_session',
        'use_orchestrators',
    ]

    for flag in enabled_flags:
        flags.enable(flag)

    return enabled_flags


# =============================================================================
# Temporary Files Fixtures
# =============================================================================

@pytest.fixture
def temp_dir(tmp_path) -> Path:
    """
    Create a temporary directory for test files.

    Args:
        tmp_path: pytest built-in fixture for temporary paths.

    Returns:
        Path to temporary directory.
    """
    return tmp_path


@pytest.fixture
def temp_config_file(tmp_path) -> Path:
    """
    Create a temporary configuration file.

    Args:
        tmp_path: pytest built-in fixture for temporary paths.

    Returns:
        Path to temporary config file.
    """
    config_content = """[SETTINGS]
target_http=https://example.com
user_name=test_user
password=test_password
listen_host=127.0.0.1
listen_port=8899
modify_visits=y
"""
    config_file = tmp_path / 'eebot.cfg'
    config_file.write_text(config_content)
    return config_file


# =============================================================================
# Environment Variable Fixtures
# =============================================================================

@pytest.fixture
def clean_env():
    """
    Clean environment variables before and after test.

    Removes all EEBOT_ prefixed environment variables.
    """
    # Store original values
    original_env = {k: v for k, v in os.environ.items() if k.startswith('EEBOT_')}

    # Remove EEBOT_ variables
    for key in original_env:
        del os.environ[key]

    yield

    # Restore original values
    for key in list(os.environ.keys()):
        if key.startswith('EEBOT_'):
            del os.environ[key]
    os.environ.update(original_env)


# =============================================================================
# Pytest Hooks
# =============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "smoke: marks tests as smoke tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on markers."""
    # Skip slow tests unless explicitly requested
    if not config.getoption("-m"):
        skip_slow = pytest.mark.skip(reason="slow test, use -m slow to run")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)
