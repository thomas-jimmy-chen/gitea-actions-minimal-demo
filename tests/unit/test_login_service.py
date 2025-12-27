# -*- coding: utf-8 -*-
"""
Unit Tests for LoginService.

Tests the login retry mechanism and callback handling.
"""

import pytest
from unittest.mock import MagicMock, call

from src.services.login_service import LoginService, LoginResult


class TestLoginService:
    """Test cases for LoginService class."""

    @pytest.fixture
    def mock_login_page(self):
        """Create a mock LoginPage."""
        page = MagicMock()
        page.auto_login.return_value = True
        page.goto.return_value = None
        return page

    @pytest.fixture
    def mock_config(self):
        """Create a mock config."""
        config = MagicMock()
        config.get.side_effect = lambda key: {
            'user_name': 'test_user',
            'password': 'test_password',
            'target_http': 'https://example.com'
        }.get(key)
        return config

    @pytest.fixture
    def login_service(self, mock_login_page, mock_config):
        """Create a LoginService instance."""
        return LoginService(
            mock_login_page,
            mock_config,
            max_retries=3,
            retry_delay=0  # No delay for tests
        )

    def test_successful_login_first_attempt(self, login_service, mock_login_page):
        """Test successful login on first attempt."""
        mock_login_page.auto_login.return_value = True

        result = login_service.login_with_retry()

        assert result.success is True
        assert result.attempts == 1
        assert result.error_message is None
        mock_login_page.auto_login.assert_called_once()

    def test_successful_login_after_retry(self, login_service, mock_login_page):
        """Test successful login after retries."""
        # Fail first two attempts, succeed on third
        mock_login_page.auto_login.side_effect = [False, False, True]

        result = login_service.login_with_retry()

        assert result.success is True
        assert result.attempts == 3
        assert mock_login_page.auto_login.call_count == 3

    def test_all_attempts_fail(self, login_service, mock_login_page):
        """Test when all login attempts fail."""
        mock_login_page.auto_login.return_value = False

        result = login_service.login_with_retry()

        assert result.success is False
        assert result.attempts == 3
        assert result.error_message == "已達最大重試次數"

    def test_on_success_callback(self, login_service, mock_login_page):
        """Test on_success callback is called."""
        mock_login_page.auto_login.return_value = True
        on_success = MagicMock()

        login_service.login_with_retry(on_success=on_success)

        on_success.assert_called_once()

    def test_on_retry_callback(self, login_service, mock_login_page):
        """Test on_retry callback is called with correct arguments."""
        mock_login_page.auto_login.side_effect = [False, False, True]
        on_retry = MagicMock()

        login_service.login_with_retry(on_retry=on_retry)

        assert on_retry.call_count == 2
        on_retry.assert_any_call(1, 3)
        on_retry.assert_any_call(2, 3)

    def test_on_failure_callback(self, login_service, mock_login_page):
        """Test on_failure callback is called when all attempts fail."""
        mock_login_page.auto_login.return_value = False
        on_failure = MagicMock()

        login_service.login_with_retry(on_failure=on_failure)

        on_failure.assert_called_once()

    def test_no_callback_on_failure_when_success(self, login_service, mock_login_page):
        """Test on_failure callback is NOT called when login succeeds."""
        mock_login_page.auto_login.return_value = True
        on_failure = MagicMock()

        login_service.login_with_retry(on_failure=on_failure)

        on_failure.assert_not_called()

    def test_refresh_on_retry(self, login_service, mock_login_page, mock_config):
        """Test page refresh on retry."""
        mock_login_page.auto_login.side_effect = [False, True]

        login_service.login_with_retry(refresh_on_retry=True)

        mock_login_page.goto.assert_called_once_with('https://example.com')

    def test_no_refresh_on_retry_when_disabled(self, login_service, mock_login_page):
        """Test no page refresh when disabled."""
        mock_login_page.auto_login.side_effect = [False, True]

        login_service.login_with_retry(refresh_on_retry=False)

        mock_login_page.goto.assert_not_called()

    def test_exception_handling(self, login_service, mock_login_page):
        """Test exception handling during login."""
        mock_login_page.auto_login.side_effect = Exception("Network error")

        result = login_service.login_with_retry()

        assert result.success is False
        assert "Network error" in result.error_message

    def test_login_simple(self, login_service, mock_login_page):
        """Test simple login method."""
        mock_login_page.auto_login.return_value = True

        success = login_service.login_simple()

        assert success is True

    def test_login_with_default_messages(self, login_service, mock_login_page, capsys):
        """Test login with default messages."""
        mock_login_page.auto_login.return_value = True

        result = login_service.login_with_default_messages()

        captured = capsys.readouterr()
        assert result.success is True
        assert '✓ 登入成功' in captured.out

    def test_missing_config_values(self, mock_login_page):
        """Test with missing configuration values."""
        config = MagicMock()
        config.get.return_value = None

        service = LoginService(mock_login_page, config)
        result = service.login_with_retry()

        assert result.success is False
        assert '缺少必要的登入配置' in result.error_message

    def test_config_attribute_access(self, mock_login_page):
        """Test config with direct attribute access instead of get()."""
        config = MagicMock(spec=[])  # No get() method
        config.user_name = 'test_user'
        config.password = 'test_password'
        config.target_http = 'https://example.com'

        service = LoginService(mock_login_page, config, retry_delay=0)
        mock_login_page.auto_login.return_value = True

        result = service.login_with_retry()

        assert result.success is True


class TestLoginResult:
    """Test cases for LoginResult dataclass."""

    def test_successful_result(self):
        """Test successful login result."""
        result = LoginResult(success=True, attempts=1)

        assert result.success is True
        assert result.attempts == 1
        assert result.error_message is None

    def test_failed_result(self):
        """Test failed login result."""
        result = LoginResult(
            success=False,
            attempts=3,
            error_message="Max retries exceeded"
        )

        assert result.success is False
        assert result.attempts == 3
        assert result.error_message == "Max retries exceeded"


class TestLoginServiceIntegration:
    """Integration tests for LoginService."""

    def test_complete_login_flow_success(self):
        """Test complete login flow with success."""
        # Setup
        login_page = MagicMock()
        login_page.auto_login.return_value = True

        config = MagicMock()
        config.get.side_effect = lambda k: {
            'user_name': 'user',
            'password': 'pass',
            'target_http': 'https://example.com'
        }[k]

        service = LoginService(login_page, config, retry_delay=0)

        # Track callbacks
        callback_log = []

        result = service.login_with_retry(
            on_success=lambda: callback_log.append('success'),
            on_retry=lambda a, m: callback_log.append(f'retry_{a}'),
            on_failure=lambda: callback_log.append('failure')
        )

        assert result.success is True
        assert callback_log == ['success']

    def test_complete_login_flow_with_retries(self):
        """Test complete login flow with retries then success."""
        login_page = MagicMock()
        login_page.auto_login.side_effect = [False, False, True]

        config = MagicMock()
        config.get.side_effect = lambda k: {
            'user_name': 'user',
            'password': 'pass',
            'target_http': 'https://example.com'
        }[k]

        service = LoginService(login_page, config, max_retries=3, retry_delay=0)

        callback_log = []

        result = service.login_with_retry(
            on_success=lambda: callback_log.append('success'),
            on_retry=lambda a, m: callback_log.append(f'retry_{a}'),
            on_failure=lambda: callback_log.append('failure')
        )

        assert result.success is True
        assert callback_log == ['retry_1', 'retry_2', 'success']

    def test_complete_login_flow_all_fail(self):
        """Test complete login flow with all attempts failing."""
        login_page = MagicMock()
        login_page.auto_login.return_value = False

        config = MagicMock()
        config.get.side_effect = lambda k: {
            'user_name': 'user',
            'password': 'pass',
            'target_http': 'https://example.com'
        }[k]

        service = LoginService(login_page, config, max_retries=3, retry_delay=0)

        callback_log = []

        result = service.login_with_retry(
            on_success=lambda: callback_log.append('success'),
            on_retry=lambda a, m: callback_log.append(f'retry_{a}'),
            on_failure=lambda: callback_log.append('failure')
        )

        assert result.success is False
        assert callback_log == ['retry_1', 'retry_2', 'failure']
