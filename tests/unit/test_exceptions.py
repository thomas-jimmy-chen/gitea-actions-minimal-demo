# -*- coding: utf-8 -*-
"""
Unit Tests for EEBot Exceptions.

Tests the custom exception classes and utility functions.
"""

import pytest
from src.exceptions import (
    EEBotError,
    ConfigError,
    LoginError,
    ElementNotFoundError,
    ProxyStartError,
    ScanError,
    APIError,
    APIRequestError,
    APIResponseError,
    APITimeoutError,
    handle_exception,
)


class TestEEBotError:
    """Test cases for EEBotError base class."""

    def test_basic_message(self):
        """Test basic error message."""
        error = EEBotError("Test error")

        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.details == {}

    def test_with_details(self):
        """Test error with details."""
        error = EEBotError("Test error", key1="value1", key2=42)

        assert "key1=value1" in str(error)
        assert "key2=42" in str(error)
        assert error.details == {"key1": "value1", "key2": 42}

    def test_to_dict(self):
        """Test to_dict method."""
        error = EEBotError("Test error", foo="bar")
        result = error.to_dict()

        assert result["error_type"] == "EEBotError"
        assert result["message"] == "Test error"
        assert result["details"] == {"foo": "bar"}

    def test_inheritance_from_exception(self):
        """Test that EEBotError inherits from Exception."""
        error = EEBotError("Test")

        assert isinstance(error, Exception)


class TestConfigError:
    """Test cases for ConfigError."""

    def test_basic_config_error(self):
        """Test basic ConfigError."""
        error = ConfigError("Configuration invalid")

        assert isinstance(error, EEBotError)
        assert str(error) == "Configuration invalid"


class TestLoginError:
    """Test cases for LoginError."""

    def test_basic_login_error(self):
        """Test basic LoginError without parameters."""
        error = LoginError()

        assert "登入失敗" in str(error)
        assert error.username is None
        assert error.reason is None
        assert error.retry_count == 0

    def test_login_error_with_reason(self):
        """Test LoginError with reason."""
        error = LoginError(reason="密碼錯誤")

        assert "密碼錯誤" in str(error)
        assert error.reason == "密碼錯誤"

    def test_login_error_with_all_params(self):
        """Test LoginError with all parameters."""
        error = LoginError(
            username="testuser",
            reason="帳號不存在",
            retry_count=3
        )

        assert error.username == "testuser"
        assert error.reason == "帳號不存在"
        assert error.retry_count == 3

    def test_login_error_inheritance(self):
        """Test that LoginError inherits from EEBotError."""
        error = LoginError()

        assert isinstance(error, EEBotError)


class TestElementNotFoundError:
    """Test cases for ElementNotFoundError."""

    def test_basic_element_error(self):
        """Test basic ElementNotFoundError."""
        locator = ("css selector", ".my-element")
        error = ElementNotFoundError(locator)

        assert "找不到元素" in str(error)
        assert ".my-element" in str(error)
        assert error.locator == locator
        assert error.timeout is None

    def test_element_error_with_timeout(self):
        """Test ElementNotFoundError with timeout."""
        locator = ("id", "my-id")
        error = ElementNotFoundError(locator, timeout=10)

        assert "超時: 10秒" in str(error)
        assert error.timeout == 10


class TestProxyStartError:
    """Test cases for ProxyStartError."""

    def test_basic_proxy_error(self):
        """Test basic ProxyStartError."""
        error = ProxyStartError()

        assert "MitmProxy 啟動失敗" in str(error)
        assert error.port is None
        assert error.reason is None

    def test_proxy_error_with_params(self):
        """Test ProxyStartError with parameters."""
        error = ProxyStartError(port=8080, reason="Port already in use")

        assert "Port already in use" in str(error)
        assert error.port == 8080
        assert error.reason == "Port already in use"


class TestScanError:
    """Test cases for ScanError."""

    def test_basic_scan_error(self):
        """Test basic ScanError."""
        error = ScanError("Scan failed")

        assert isinstance(error, EEBotError)
        assert str(error) == "Scan failed"


class TestAPIError:
    """Test cases for APIError and subclasses."""

    def test_basic_api_error(self):
        """Test basic APIError."""
        error = APIError("API call failed")

        assert "API call failed" in str(error)
        assert error.status_code is None
        assert error.response_text is None

    def test_api_error_with_status(self):
        """Test APIError with status code."""
        error = APIError("Error", status_code=500, response_text="Server Error")

        assert error.status_code == 500
        assert error.response_text == "Server Error"


class TestAPIRequestError:
    """Test cases for APIRequestError."""

    def test_basic_request_error(self):
        """Test basic APIRequestError."""
        error = APIRequestError()

        assert "API 請求失敗" in str(error)

    def test_request_error_with_url(self):
        """Test APIRequestError with URL."""
        error = APIRequestError(
            url="https://api.example.com/test",
            method="POST",
            status_code=404
        )

        assert "POST" in str(error)
        assert "https://api.example.com/test" in str(error)
        assert error.url == "https://api.example.com/test"
        assert error.method == "POST"
        assert error.status_code == 404

    def test_request_error_default_method(self):
        """Test that default method is GET."""
        error = APIRequestError(url="https://example.com")

        assert "GET" in str(error)


class TestAPIResponseError:
    """Test cases for APIResponseError."""

    def test_basic_response_error(self):
        """Test basic APIResponseError."""
        error = APIResponseError()

        assert "API 響應格式錯誤" in str(error)

    def test_response_error_with_custom_message(self):
        """Test APIResponseError with custom message."""
        error = APIResponseError(
            message="Invalid JSON response",
            status_code=200,
            response_text="not json"
        )

        assert "Invalid JSON response" in str(error)
        assert error.status_code == 200


class TestAPITimeoutError:
    """Test cases for APITimeoutError."""

    def test_basic_timeout_error(self):
        """Test basic APITimeoutError."""
        error = APITimeoutError()

        assert "API 請求超時" in str(error)
        assert error.url is None
        assert error.timeout is None

    def test_timeout_error_with_url(self):
        """Test APITimeoutError with URL."""
        error = APITimeoutError(
            url="https://slow.api.com",
            timeout=30
        )

        assert "https://slow.api.com" in str(error)
        assert error.url == "https://slow.api.com"
        assert error.timeout == 30


class TestHandleException:
    """Test cases for handle_exception function."""

    def test_handle_eebot_error(self):
        """Test handling EEBotError."""
        error = LoginError(username="test", reason="fail")
        result = handle_exception(error)

        assert result["error_type"] == "LoginError"
        assert "登入失敗" in result["message"]
        assert "username" in result["details"]

    def test_handle_generic_exception(self):
        """Test handling generic Python exception."""
        error = ValueError("Invalid value")
        result = handle_exception(error)

        assert result["error_type"] == "ValueError"
        assert result["message"] == "Invalid value"
        assert result["details"] == {}

    def test_handle_with_log_func(self):
        """Test handling exception with log function."""
        logged_messages = []

        def mock_log(msg):
            logged_messages.append(msg)

        error = APIError("Test API error")
        handle_exception(error, log_func=mock_log)

        assert len(logged_messages) == 1
        assert "[APIError]" in logged_messages[0]
        assert "Test API error" in logged_messages[0]

    def test_handle_exception_returns_dict(self):
        """Test that handle_exception always returns a dict."""
        result1 = handle_exception(EEBotError("test"))
        result2 = handle_exception(Exception("test"))

        assert isinstance(result1, dict)
        assert isinstance(result2, dict)
        assert "error_type" in result1
        assert "message" in result1
        assert "details" in result1


class TestExceptionHierarchy:
    """Test the exception inheritance hierarchy."""

    def test_all_inherit_from_eebot_error(self):
        """Test that all custom exceptions inherit from EEBotError."""
        exceptions = [
            ConfigError("test"),
            LoginError(),
            ElementNotFoundError(("id", "test")),
            ProxyStartError(),
            ScanError("test"),
            APIError("test"),
            APIRequestError(),
            APIResponseError(),
            APITimeoutError(),
        ]

        for exc in exceptions:
            assert isinstance(exc, EEBotError), f"{type(exc)} should inherit from EEBotError"

    def test_api_errors_inherit_from_api_error(self):
        """Test that API error subclasses inherit from APIError."""
        api_exceptions = [
            APIRequestError(),
            APIResponseError(),
            APITimeoutError(),
        ]

        for exc in api_exceptions:
            assert isinstance(exc, APIError), f"{type(exc)} should inherit from APIError"
