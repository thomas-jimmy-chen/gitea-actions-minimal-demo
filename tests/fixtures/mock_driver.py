# -*- coding: utf-8 -*-
"""
Mock WebDriver Objects for EEBot Tests.

This module provides mock WebDriver objects that simulate
Selenium WebDriver behavior for testing purposes.
"""

from typing import List, Dict, Any, Optional
from unittest.mock import MagicMock


class MockWebElement:
    """
    Mock implementation of Selenium WebElement.

    Simulates a web page element for testing.
    """

    def __init__(
        self,
        text: str = 'Test Element',
        tag_name: str = 'div',
        attributes: Optional[Dict[str, str]] = None
    ):
        self.text = text
        self.tag_name = tag_name
        self._attributes = attributes or {}
        self._displayed = True
        self._enabled = True
        self._selected = False

    def get_attribute(self, name: str) -> Optional[str]:
        """Get an element attribute."""
        return self._attributes.get(name)

    def is_displayed(self) -> bool:
        """Check if element is displayed."""
        return self._displayed

    def is_enabled(self) -> bool:
        """Check if element is enabled."""
        return self._enabled

    def is_selected(self) -> bool:
        """Check if element is selected."""
        return self._selected

    def click(self) -> None:
        """Click the element."""
        pass

    def send_keys(self, *keys) -> None:
        """Send keys to the element."""
        pass

    def clear(self) -> None:
        """Clear the element content."""
        pass

    def submit(self) -> None:
        """Submit the form."""
        pass


class MockWebDriver:
    """
    Mock implementation of Selenium WebDriver.

    Simulates browser behavior for testing without
    actually opening a browser.
    """

    def __init__(self):
        self._url = 'about:blank'
        self._title = ''
        self._page_source = '<html><body></body></html>'
        self._cookies: List[Dict[str, Any]] = []
        self._windows = ['main']
        self._current_window = 'main'
        self._elements: Dict[str, MockWebElement] = {}
        self._closed = False

    @property
    def current_url(self) -> str:
        """Get current URL."""
        return self._url

    @property
    def title(self) -> str:
        """Get page title."""
        return self._title

    @property
    def page_source(self) -> str:
        """Get page source HTML."""
        return self._page_source

    def get(self, url: str) -> None:
        """Navigate to URL."""
        self._url = url
        self._title = f'Page at {url}'

    def refresh(self) -> None:
        """Refresh the page."""
        pass

    def back(self) -> None:
        """Go back in history."""
        pass

    def forward(self) -> None:
        """Go forward in history."""
        pass

    def quit(self) -> None:
        """Quit the browser."""
        self._closed = True

    def close(self) -> None:
        """Close the current window."""
        pass

    def find_element(self, by: str, value: str) -> MockWebElement:
        """Find a single element."""
        key = f'{by}:{value}'
        if key not in self._elements:
            self._elements[key] = MockWebElement(text=f'Element({value})')
        return self._elements[key]

    def find_elements(self, by: str, value: str) -> List[MockWebElement]:
        """Find multiple elements."""
        return [self.find_element(by, value)]

    def execute_script(self, script: str, *args) -> Any:
        """Execute JavaScript."""
        # Return common script results
        if 'scrollHeight' in script:
            return 1000
        if 'scrollTop' in script:
            return 0
        if 'return document' in script:
            return None
        return None

    def execute_async_script(self, script: str, *args) -> Any:
        """Execute async JavaScript."""
        return None

    def get_cookies(self) -> List[Dict[str, Any]]:
        """Get all cookies."""
        return self._cookies

    def get_cookie(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific cookie."""
        for cookie in self._cookies:
            if cookie.get('name') == name:
                return cookie
        return None

    def add_cookie(self, cookie: Dict[str, Any]) -> None:
        """Add a cookie."""
        self._cookies.append(cookie)

    def delete_cookie(self, name: str) -> None:
        """Delete a cookie."""
        self._cookies = [c for c in self._cookies if c.get('name') != name]

    def delete_all_cookies(self) -> None:
        """Delete all cookies."""
        self._cookies = []

    @property
    def window_handles(self) -> List[str]:
        """Get all window handles."""
        return self._windows

    @property
    def current_window_handle(self) -> str:
        """Get current window handle."""
        return self._current_window

    def switch_to_window(self, handle: str) -> None:
        """Switch to a window."""
        self._current_window = handle

    def set_element(self, by: str, value: str, element: MockWebElement) -> None:
        """Set a mock element for testing."""
        key = f'{by}:{value}'
        self._elements[key] = element

    def set_page_source(self, html: str) -> None:
        """Set the page source for testing."""
        self._page_source = html

    def set_cookies(self, cookies: List[Dict[str, Any]]) -> None:
        """Set cookies for testing."""
        self._cookies = cookies


def create_mock_driver(
    url: str = 'https://example.com',
    cookies: Optional[List[Dict[str, Any]]] = None
) -> MagicMock:
    """
    Create a MagicMock with WebDriver-like behavior.

    This function creates a MagicMock that can be used in place of
    a real WebDriver in tests.

    Args:
        url: Initial URL for the driver.
        cookies: Initial cookies.

    Returns:
        MagicMock object configured to behave like WebDriver.

    Example:
        driver = create_mock_driver('https://example.com')
        driver.get('https://other.com')
    """
    mock_driver = MockWebDriver()
    mock_driver._url = url

    if cookies:
        mock_driver._cookies = cookies
    else:
        mock_driver._cookies = [
            {'name': 'session', 'value': 'test_session_id'}
        ]

    mock = MagicMock(spec=MockWebDriver)

    # Set up properties
    type(mock).current_url = property(lambda self: mock_driver._url)
    type(mock).title = property(lambda self: mock_driver._title)
    type(mock).page_source = property(lambda self: mock_driver._page_source)
    type(mock).window_handles = property(lambda self: mock_driver._windows)
    type(mock).current_window_handle = property(lambda self: mock_driver._current_window)

    # Set up methods
    mock.get.side_effect = mock_driver.get
    mock.refresh.return_value = None
    mock.quit.side_effect = mock_driver.quit
    mock.close.return_value = None

    mock.find_element.side_effect = mock_driver.find_element
    mock.find_elements.side_effect = mock_driver.find_elements
    mock.execute_script.side_effect = mock_driver.execute_script

    mock.get_cookies.side_effect = mock_driver.get_cookies
    mock.get_cookie.side_effect = mock_driver.get_cookie
    mock.add_cookie.side_effect = mock_driver.add_cookie
    mock.delete_cookie.side_effect = mock_driver.delete_cookie
    mock.delete_all_cookies.side_effect = mock_driver.delete_all_cookies

    # Attach the mock driver for direct access in tests
    mock._mock_driver = mock_driver

    return mock
