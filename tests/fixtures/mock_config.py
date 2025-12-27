# -*- coding: utf-8 -*-
"""
Mock Configuration Objects for EEBot Tests.

This module provides mock configuration objects that simulate
the ConfigLoader behavior for testing purposes.
"""

from typing import Dict, Any, Optional
from unittest.mock import MagicMock


class MockConfigLoader:
    """
    Mock implementation of ConfigLoader for testing.

    Provides a predictable configuration interface without
    reading actual configuration files.
    """

    def __init__(self, overrides: Optional[Dict[str, Any]] = None):
        """
        Initialize mock config with optional overrides.

        Args:
            overrides: Dictionary of config values to override defaults.
        """
        self._values = {
            # Connection settings
            'target_http': 'https://example.com',
            'execute_file': 'chromedriver.exe',

            # Authentication
            'user_name': 'test_user',
            'password': 'test_password',

            # Proxy settings
            'listen_host': '127.0.0.1',
            'listen_port': 8899,

            # Feature toggles
            'modify_visits': 'y',
            'enable_auto_answer': 'y',
            'silent_mitm': 'y',

            # Timing
            'default_delay': 7.0,
            'screenshot_delay': 1.0,

            # Question bank
            'question_bank_mode': 'total_bank',
            'answer_confidence_threshold': 0.85,
        }

        if overrides:
            self._values.update(overrides)

        # Set attributes for direct access
        for key, value in self._values.items():
            setattr(self, key, value)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._values.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self._values[key] = value
        setattr(self, key, value)

    def load_timing_config(self) -> Dict[str, Any]:
        """Load timing configuration."""
        return {
            'screenshot': {
                'enabled': False,
                'delay': 1.0,
            },
            'page_load': {
                'timeout': 30,
                'delay': 2.0,
            },
        }

    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled."""
        value = self._values.get(feature, 'n')
        if isinstance(value, bool):
            return value
        return str(value).lower() in ('y', 'yes', 'true', '1')


def create_mock_config(overrides: Optional[Dict[str, Any]] = None) -> MagicMock:
    """
    Create a MagicMock with ConfigLoader-like behavior.

    This function creates a MagicMock that can be used in place of
    a real ConfigLoader in tests.

    Args:
        overrides: Dictionary of config values to override defaults.

    Returns:
        MagicMock object configured to behave like ConfigLoader.

    Example:
        config = create_mock_config({'user_name': 'custom_user'})
        assert config.user_name == 'custom_user'
    """
    mock_loader = MockConfigLoader(overrides)
    mock = MagicMock(spec=MockConfigLoader)

    # Set up attribute access
    mock.get.side_effect = mock_loader.get
    mock.set.side_effect = mock_loader.set
    mock.load_timing_config.return_value = mock_loader.load_timing_config()
    mock.is_feature_enabled.side_effect = mock_loader.is_feature_enabled

    # Copy all attributes
    for key in mock_loader._values:
        setattr(mock, key, mock_loader._values[key])

    return mock
