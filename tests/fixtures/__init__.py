# -*- coding: utf-8 -*-
"""
Test Fixtures Module for EEBot.

This module provides reusable mock objects and test utilities.
"""

from .mock_config import create_mock_config, MockConfigLoader
from .mock_driver import create_mock_driver, MockWebDriver
from .mock_proxy import create_mock_proxy_manager, MockProxyManager

__all__ = [
    'create_mock_config',
    'MockConfigLoader',
    'create_mock_driver',
    'MockWebDriver',
    'create_mock_proxy_manager',
    'MockProxyManager',
]
