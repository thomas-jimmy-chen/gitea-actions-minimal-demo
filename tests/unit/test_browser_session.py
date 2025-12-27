# -*- coding: utf-8 -*-
"""
Unit Tests for BrowserSession.

Tests the browser session management and context manager functionality.
"""

import sys
import pytest
from unittest.mock import MagicMock, patch

# Mock all external dependencies before any imports
mock_modules = [
    'selenium', 'selenium.webdriver', 'selenium.webdriver.common',
    'selenium.webdriver.common.by', 'selenium.webdriver.support',
    'selenium.webdriver.support.ui', 'selenium.webdriver.support.expected_conditions',
    'selenium.webdriver.chrome.options', 'selenium.webdriver.chrome.service',
    'mitmproxy', 'mitmproxy.options', 'mitmproxy.tools.dump',
]

for mod in mock_modules:
    if mod not in sys.modules:
        sys.modules[mod] = MagicMock()

# Mock the core modules to avoid their internal imports
sys.modules['src.core.driver_manager'] = MagicMock()
sys.modules['src.core.cookie_manager'] = MagicMock()
sys.modules['src.core.proxy_manager'] = MagicMock()
sys.modules['src.pages.login_page'] = MagicMock()
sys.modules['src.pages.course_list_page'] = MagicMock()

# Now import the module under test directly
import importlib.util
import os

# Load browser_session directly to avoid __init__.py issues
spec = importlib.util.spec_from_file_location(
    "browser_session",
    os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'core', 'browser_session.py')
)
browser_session_module = importlib.util.module_from_spec(spec)

# Temporarily set up the module's globals for the imports inside the module
browser_session_module.__dict__['logging'] = __import__('logging')
browser_session_module.__dict__['Any'] = type
browser_session_module.__dict__['Optional'] = type
browser_session_module.__dict__['List'] = list
browser_session_module.__dict__['contextmanager'] = __import__('contextlib').contextmanager
browser_session_module.__dict__['dataclass'] = __import__('dataclasses').dataclass
browser_session_module.__dict__['field'] = __import__('dataclasses').field

spec.loader.exec_module(browser_session_module)

BrowserSession = browser_session_module.BrowserSession
SessionConfig = browser_session_module.SessionConfig
browser_session = browser_session_module.browser_session


class TestSessionConfig:
    """Test cases for SessionConfig dataclass."""

    def test_default_values(self):
        """Test default configuration values."""
        config = SessionConfig()

        assert config.use_proxy is False
        assert config.interceptors == []
        assert config.auto_login is True
        assert config.goto_my_courses is False

    def test_custom_values(self):
        """Test custom configuration values."""
        interceptors = [MagicMock(), MagicMock()]
        config = SessionConfig(
            use_proxy=True,
            interceptors=interceptors,
            auto_login=False,
            goto_my_courses=True
        )

        assert config.use_proxy is True
        assert config.interceptors == interceptors
        assert config.auto_login is False
        assert config.goto_my_courses is True


class TestBrowserSession:
    """Test cases for BrowserSession class."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration."""
        config = MagicMock()
        config.get.side_effect = lambda key, default=None: {
            'user_name': 'test_user',
            'password': 'test_password',
            'target_http': 'https://example.com',
            'cookies_file': 'cookies.json'
        }.get(key, default)
        return config

    def test_initialization(self, mock_config):
        """Test BrowserSession initialization."""
        session = BrowserSession(mock_config)

        assert session.config == mock_config
        assert session.session_config.use_proxy is False
        assert session._is_initialized is False

    def test_initialization_with_proxy(self, mock_config):
        """Test BrowserSession initialization with proxy."""
        interceptors = [MagicMock()]
        session = BrowserSession(
            mock_config,
            use_proxy=True,
            interceptors=interceptors
        )

        assert session.session_config.use_proxy is True
        assert session.session_config.interceptors == interceptors

    def test_get_config_value_with_get_method(self, mock_config):
        """Test _get_config_value with get() method."""
        session = BrowserSession(mock_config)

        result = session._get_config_value('user_name')

        assert result == 'test_user'

    def test_get_config_value_with_attribute(self):
        """Test _get_config_value with attribute access."""
        config = MagicMock(spec=[])  # No get() method
        config.user_name = 'attr_user'

        session = BrowserSession(config)
        result = session._get_config_value('user_name')

        assert result == 'attr_user'

    def test_is_proxy_enabled_false(self, mock_config):
        """Test is_proxy_enabled when proxy is not enabled."""
        session = BrowserSession(mock_config)

        assert session.is_proxy_enabled is False

    def test_get_current_url_when_no_driver(self, mock_config):
        """Test get_current_url when driver is None."""
        session = BrowserSession(mock_config)

        assert session.get_current_url() == ""

    def test_login_without_initialization_raises_error(self, mock_config):
        """Test that login without initialization raises error."""
        session = BrowserSession(mock_config)

        with pytest.raises(RuntimeError, match="尚未初始化"):
            session.login()

    def test_goto_my_courses_without_initialization_raises_error(self, mock_config):
        """Test that goto_my_courses without initialization raises error."""
        session = BrowserSession(mock_config)

        with pytest.raises(RuntimeError, match="尚未初始化"):
            session.goto_my_courses()

    def test_is_logged_in_default(self, mock_config):
        """Test is_logged_in returns False by default."""
        session = BrowserSession(mock_config)

        assert session.is_logged_in() is False


class TestBrowserSessionWithMockedInit:
    """Test cases that require mocked initialization."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration."""
        config = MagicMock()
        config.get.side_effect = lambda key, default=None: {
            'user_name': 'test_user',
            'password': 'test_password',
            'target_http': 'https://example.com',
            'cookies_file': 'cookies.json'
        }.get(key, default)
        return config

    @pytest.fixture
    def session_with_mocked_init(self, mock_config):
        """Create a session with mocked _initialize method."""
        session = BrowserSession(mock_config, auto_login=False)

        # Mock the initialization
        session.driver = MagicMock()
        session.driver_manager = MagicMock()
        session.cookie_manager = MagicMock()
        session.login_page = MagicMock()
        session.login_page.auto_login.return_value = True
        session.course_list_page = MagicMock()
        session._is_initialized = True

        return session

    def test_login_success(self, session_with_mocked_init):
        """Test successful login."""
        result = session_with_mocked_init.login()

        assert result is True
        assert session_with_mocked_init._login_success is True
        session_with_mocked_init.login_page.auto_login.assert_called()

    def test_login_with_retries(self, session_with_mocked_init):
        """Test login with retries."""
        session_with_mocked_init.login_page.auto_login.side_effect = [
            False, False, True
        ]

        result = session_with_mocked_init.login(max_retries=3)

        assert result is True
        assert session_with_mocked_init.login_page.auto_login.call_count == 3

    def test_login_all_fail(self, session_with_mocked_init):
        """Test login when all attempts fail."""
        session_with_mocked_init.login_page.auto_login.return_value = False

        result = session_with_mocked_init.login(max_retries=3)

        assert result is False
        assert session_with_mocked_init._login_success is False

    def test_goto_my_courses(self, session_with_mocked_init):
        """Test goto_my_courses method."""
        session_with_mocked_init.goto_my_courses()

        session_with_mocked_init.course_list_page.goto_my_courses.assert_called_once()

    def test_is_logged_in_after_login(self, session_with_mocked_init):
        """Test is_logged_in after successful login."""
        session_with_mocked_init.login()

        assert session_with_mocked_init.is_logged_in() is True

    def test_get_current_url(self, session_with_mocked_init):
        """Test get_current_url method."""
        session_with_mocked_init.driver.current_url = 'https://example.com/page'

        url = session_with_mocked_init.get_current_url()

        assert url == 'https://example.com/page'

    def test_save_cookies(self, session_with_mocked_init):
        """Test save_cookies method."""
        session_with_mocked_init.driver.get_cookies.return_value = [
            {'name': 'session', 'value': 'abc123'}
        ]

        session_with_mocked_init.save_cookies()

        session_with_mocked_init.driver.get_cookies.assert_called_once()
        session_with_mocked_init.cookie_manager.save.assert_called_once()

    def test_cleanup(self, session_with_mocked_init):
        """Test _cleanup method."""
        driver = session_with_mocked_init.driver

        session_with_mocked_init._cleanup()

        driver.quit.assert_called_once()
        assert session_with_mocked_init.driver is None
        assert session_with_mocked_init._is_initialized is False


class TestBrowserSessionProxyOperations:
    """Test cases for proxy-related operations."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration."""
        config = MagicMock()
        config.get.side_effect = lambda key, default=None: {
            'user_name': 'test_user',
            'password': 'test_password',
            'target_http': 'https://example.com',
            'cookies_file': 'cookies.json'
        }.get(key, default)
        return config

    @pytest.fixture
    def session_with_proxy(self, mock_config):
        """Create a session with proxy enabled."""
        session = BrowserSession(
            mock_config,
            use_proxy=True,
            interceptors=[MagicMock()]
        )

        # Mock initialization
        session.driver = MagicMock()
        session.driver_manager = MagicMock()
        session.driver_manager.create_driver.return_value = MagicMock()
        session.cookie_manager = MagicMock()
        session.login_page = MagicMock()
        session.course_list_page = MagicMock()
        session.proxy = MagicMock()
        session._is_initialized = True

        return session

    def test_is_proxy_enabled_true(self, session_with_proxy):
        """Test is_proxy_enabled when proxy is enabled."""
        assert session_with_proxy.is_proxy_enabled is True

    def test_restart_without_proxy(self, session_with_proxy):
        """Test restart_without_proxy method."""
        old_driver = session_with_proxy.driver
        old_proxy = session_with_proxy.proxy

        # Mock the lazy imports by patching sys.modules
        mock_login_page = MagicMock()
        mock_course_list_page = MagicMock()
        sys.modules['src.pages.login_page'] = MagicMock()
        sys.modules['src.pages.login_page'].LoginPage = mock_login_page
        sys.modules['src.pages.course_list_page'] = MagicMock()
        sys.modules['src.pages.course_list_page'].CourseListPage = mock_course_list_page

        session_with_proxy.restart_without_proxy()

        old_driver.quit.assert_called_once()
        old_proxy.stop.assert_called_once()
        assert session_with_proxy.session_config.use_proxy is False
        assert session_with_proxy.proxy is None
        assert session_with_proxy._login_success is False

    def test_restart_with_proxy(self, mock_config):
        """Test restart_with_proxy method."""
        session = BrowserSession(mock_config, use_proxy=False)

        # Mock initialization without proxy
        session.driver = MagicMock()
        session.driver_manager = MagicMock()
        session.driver_manager.create_driver.return_value = MagicMock()
        session.cookie_manager = MagicMock()
        session.login_page = MagicMock()
        session.course_list_page = MagicMock()
        session._is_initialized = True

        old_driver = session.driver

        # Mock the lazy imports by patching sys.modules
        mock_proxy_manager = MagicMock()
        mock_login_page = MagicMock()
        mock_course_list_page = MagicMock()
        sys.modules['src.core.proxy_manager'] = MagicMock()
        sys.modules['src.core.proxy_manager'].ProxyManager = mock_proxy_manager
        sys.modules['src.pages.login_page'] = MagicMock()
        sys.modules['src.pages.login_page'].LoginPage = mock_login_page
        sys.modules['src.pages.course_list_page'] = MagicMock()
        sys.modules['src.pages.course_list_page'].CourseListPage = mock_course_list_page

        session.restart_with_proxy(interceptors=[MagicMock()])

        old_driver.quit.assert_called_once()
        assert session.session_config.use_proxy is True
        assert session._login_success is False
