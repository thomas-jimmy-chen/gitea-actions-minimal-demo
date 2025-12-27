# -*- coding: utf-8 -*-
"""
Mock Proxy Manager Objects for EEBot Tests.

This module provides mock proxy manager objects that simulate
MitmProxy behavior for testing purposes.
"""

from typing import Dict, Any, Optional, List, Callable
from unittest.mock import MagicMock


class MockProxyManager:
    """
    Mock implementation of ProxyManager.

    Simulates MitmProxy behavior for testing without
    actually starting a proxy server.
    """

    def __init__(self, host: str = '127.0.0.1', port: int = 8899):
        self._host = host
        self._port = port
        self._running = False
        self._interceptors: List[Any] = []
        self._captured_requests: List[Dict[str, Any]] = []
        self._captured_responses: List[Dict[str, Any]] = []

    @property
    def host(self) -> str:
        """Get proxy host."""
        return self._host

    @property
    def port(self) -> int:
        """Get proxy port."""
        return self._port

    def start(self) -> bool:
        """Start the proxy server."""
        self._running = True
        return True

    def stop(self) -> None:
        """Stop the proxy server."""
        self._running = False

    def is_running(self) -> bool:
        """Check if proxy is running."""
        return self._running

    def get_port(self) -> int:
        """Get the proxy port."""
        return self._port

    def add_interceptor(self, interceptor: Any) -> None:
        """Add an interceptor."""
        self._interceptors.append(interceptor)

    def remove_interceptor(self, interceptor: Any) -> None:
        """Remove an interceptor."""
        if interceptor in self._interceptors:
            self._interceptors.remove(interceptor)

    def get_interceptors(self) -> List[Any]:
        """Get all interceptors."""
        return self._interceptors.copy()

    def capture_request(self, request: Dict[str, Any]) -> None:
        """Capture a request for testing."""
        self._captured_requests.append(request)

    def capture_response(self, response: Dict[str, Any]) -> None:
        """Capture a response for testing."""
        self._captured_responses.append(response)

    def get_captured_requests(self) -> List[Dict[str, Any]]:
        """Get captured requests."""
        return self._captured_requests.copy()

    def get_captured_responses(self) -> List[Dict[str, Any]]:
        """Get captured responses."""
        return self._captured_responses.copy()

    def clear_captured(self) -> None:
        """Clear captured requests and responses."""
        self._captured_requests = []
        self._captured_responses = []


class MockFlow:
    """
    Mock implementation of MitmProxy Flow.

    Simulates a request/response flow for testing interceptors.
    """

    def __init__(
        self,
        method: str = 'GET',
        url: str = 'https://example.com/api/test',
        request_body: Optional[str] = None,
        response_body: Optional[str] = None,
        status_code: int = 200
    ):
        self.request = MockRequest(method, url, request_body)
        self.response = MockResponse(status_code, response_body)


class MockRequest:
    """Mock implementation of MitmProxy Request."""

    def __init__(
        self,
        method: str = 'GET',
        url: str = 'https://example.com/api/test',
        body: Optional[str] = None
    ):
        self.method = method
        self.url = url
        self.host = 'example.com'
        self.path = '/api/test'
        self._body = body or ''
        self._headers = {'Content-Type': 'application/json'}

    @property
    def headers(self) -> Dict[str, str]:
        """Get request headers."""
        return self._headers

    def get_text(self) -> str:
        """Get request body as text."""
        return self._body

    def set_text(self, text: str) -> None:
        """Set request body."""
        self._body = text

    def get_json(self) -> Dict[str, Any]:
        """Get request body as JSON."""
        import json
        return json.loads(self._body) if self._body else {}


class MockResponse:
    """Mock implementation of MitmProxy Response."""

    def __init__(
        self,
        status_code: int = 200,
        body: Optional[str] = None
    ):
        self.status_code = status_code
        self._body = body or ''
        self._headers = {'Content-Type': 'application/json'}

    @property
    def headers(self) -> Dict[str, str]:
        """Get response headers."""
        return self._headers

    def get_text(self) -> str:
        """Get response body as text."""
        return self._body

    def set_text(self, text: str) -> None:
        """Set response body."""
        self._body = text

    def get_json(self) -> Dict[str, Any]:
        """Get response body as JSON."""
        import json
        return json.loads(self._body) if self._body else {}


def create_mock_proxy_manager(
    host: str = '127.0.0.1',
    port: int = 8899,
    auto_start: bool = False
) -> MagicMock:
    """
    Create a MagicMock with ProxyManager-like behavior.

    This function creates a MagicMock that can be used in place of
    a real ProxyManager in tests.

    Args:
        host: Proxy host address.
        port: Proxy port number.
        auto_start: Whether to start the proxy automatically.

    Returns:
        MagicMock object configured to behave like ProxyManager.

    Example:
        proxy = create_mock_proxy_manager(port=8888)
        proxy.start()
        assert proxy.is_running()
    """
    mock_manager = MockProxyManager(host, port)

    if auto_start:
        mock_manager.start()

    mock = MagicMock(spec=MockProxyManager)

    # Set up properties
    type(mock).host = property(lambda self: mock_manager._host)
    type(mock).port = property(lambda self: mock_manager._port)

    # Set up methods
    mock.start.side_effect = mock_manager.start
    mock.stop.side_effect = mock_manager.stop
    mock.is_running.side_effect = mock_manager.is_running
    mock.get_port.side_effect = mock_manager.get_port

    mock.add_interceptor.side_effect = mock_manager.add_interceptor
    mock.remove_interceptor.side_effect = mock_manager.remove_interceptor
    mock.get_interceptors.side_effect = mock_manager.get_interceptors

    mock.capture_request.side_effect = mock_manager.capture_request
    mock.capture_response.side_effect = mock_manager.capture_response
    mock.get_captured_requests.side_effect = mock_manager.get_captured_requests
    mock.get_captured_responses.side_effect = mock_manager.get_captured_responses
    mock.clear_captured.side_effect = mock_manager.clear_captured

    # Attach mock manager for direct access
    mock._mock_manager = mock_manager

    return mock


def create_mock_flow(
    method: str = 'GET',
    url: str = 'https://example.com/api/test',
    request_body: Optional[str] = None,
    response_body: Optional[str] = None,
    status_code: int = 200
) -> MockFlow:
    """
    Create a mock flow for testing interceptors.

    Args:
        method: HTTP method.
        url: Request URL.
        request_body: Request body content.
        response_body: Response body content.
        status_code: Response status code.

    Returns:
        MockFlow object for testing.

    Example:
        flow = create_mock_flow(
            method='POST',
            url='https://example.com/api/submit',
            request_body='{"data": "test"}',
            response_body='{"success": true}'
        )
        interceptor.request(flow)
    """
    return MockFlow(method, url, request_body, response_body, status_code)
