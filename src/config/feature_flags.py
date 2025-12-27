# -*- coding: utf-8 -*-
"""
Feature Flags Module for EEBot Progressive Refactoring.

This module provides a feature flag mechanism to safely switch between
legacy code and new implementations during the refactoring process.

Usage:
    from src.config.feature_flags import feature_enabled

    if feature_enabled('use_login_service'):
        login_service.login_with_retry(...)
    else:
        # Legacy code path
        ...

Environment Variables:
    EEBOT_FF_USE_LOGIN_SERVICE=true
    EEBOT_FF_USE_SCROLL_UTILS=true
    EEBOT_FF_USE_BROWSER_SESSION=true
    EEBOT_FF_USE_ORCHESTRATORS=true
    EEBOT_FF_FALLBACK_ON_ERROR=true
"""

import os
import logging
from typing import Dict, Optional, Any
from threading import Lock

logger = logging.getLogger(__name__)


class FeatureFlags:
    """
    Singleton class to manage feature flags for progressive refactoring.

    Supports three layers of configuration (priority from high to low):
    1. Runtime overrides (set programmatically)
    2. Environment variables (EEBOT_FF_<FLAG_NAME>)
    3. Default values

    Thread-safe implementation for concurrent access.
    """

    _instance: Optional['FeatureFlags'] = None
    _lock = Lock()

    # Default flag values
    # Phase 3 完成後啟用 Orchestrator 層
    DEFAULT_FLAGS: Dict[str, bool] = {
        # Phase 1: Shared logic extraction
        'use_login_service': False,      # Use new LoginService instead of inline login
        'use_scroll_utils': False,       # Use new scroll_utils module
        'use_browser_session': False,    # Use new BrowserSession context manager

        # Phase 2: Orchestrator layer
        'use_orchestrators': True,       # ✅ 啟用 Orchestrator 層 (Phase 3 完成)

        # Safety fallback
        'fallback_on_error': True,       # Fall back to legacy code on error
    }

    def __new__(cls) -> 'FeatureFlags':
        """Singleton pattern with thread-safe double-checked locking."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize feature flags from defaults and environment."""
        if self._initialized:
            return

        self._flags: Dict[str, bool] = self.DEFAULT_FLAGS.copy()
        self._runtime_overrides: Dict[str, bool] = {}
        self._load_from_environment()
        self._initialized = True

        logger.info("Feature flags initialized: %s", self._get_effective_flags())

    def _load_from_environment(self) -> None:
        """Load feature flag values from environment variables."""
        prefix = "EEBOT_FF_"

        for flag_name in self.DEFAULT_FLAGS:
            env_var = prefix + flag_name.upper()
            env_value = os.environ.get(env_var)

            if env_value is not None:
                # Parse boolean from string
                bool_value = env_value.lower() in ('true', '1', 'yes', 'on')
                self._flags[flag_name] = bool_value
                logger.debug(
                    "Feature flag '%s' set to %s from environment variable %s",
                    flag_name, bool_value, env_var
                )

    def _get_effective_flags(self) -> Dict[str, bool]:
        """Get all effective flag values (runtime overrides take priority)."""
        result = self._flags.copy()
        result.update(self._runtime_overrides)
        return result

    def is_enabled(self, flag_name: str) -> bool:
        """
        Check if a feature flag is enabled.

        Args:
            flag_name: The name of the feature flag to check.

        Returns:
            True if the flag is enabled, False otherwise.

        Raises:
            KeyError: If the flag name is not recognized.
        """
        if flag_name not in self.DEFAULT_FLAGS:
            logger.warning("Unknown feature flag requested: %s", flag_name)
            raise KeyError(f"Unknown feature flag: {flag_name}")

        # Runtime overrides take priority
        if flag_name in self._runtime_overrides:
            return self._runtime_overrides[flag_name]

        return self._flags.get(flag_name, False)

    def enable(self, flag_name: str) -> None:
        """
        Enable a feature flag at runtime.

        Args:
            flag_name: The name of the feature flag to enable.
        """
        if flag_name not in self.DEFAULT_FLAGS:
            raise KeyError(f"Unknown feature flag: {flag_name}")

        self._runtime_overrides[flag_name] = True
        logger.info("Feature flag '%s' enabled at runtime", flag_name)

    def disable(self, flag_name: str) -> None:
        """
        Disable a feature flag at runtime.

        Args:
            flag_name: The name of the feature flag to disable.
        """
        if flag_name not in self.DEFAULT_FLAGS:
            raise KeyError(f"Unknown feature flag: {flag_name}")

        self._runtime_overrides[flag_name] = False
        logger.info("Feature flag '%s' disabled at runtime", flag_name)

    def reset(self, flag_name: Optional[str] = None) -> None:
        """
        Reset feature flag(s) to their default/environment values.

        Args:
            flag_name: The name of the flag to reset, or None to reset all.
        """
        if flag_name is None:
            self._runtime_overrides.clear()
            logger.info("All feature flag runtime overrides cleared")
        elif flag_name in self._runtime_overrides:
            del self._runtime_overrides[flag_name]
            logger.info("Feature flag '%s' runtime override cleared", flag_name)

    def get_all_flags(self) -> Dict[str, bool]:
        """
        Get all feature flag values.

        Returns:
            Dictionary of all flag names and their current values.
        """
        return self._get_effective_flags()

    def get_flag_status(self, flag_name: str) -> Dict[str, Any]:
        """
        Get detailed status of a feature flag.

        Args:
            flag_name: The name of the feature flag.

        Returns:
            Dictionary with default, environment, override, and effective values.
        """
        if flag_name not in self.DEFAULT_FLAGS:
            raise KeyError(f"Unknown feature flag: {flag_name}")

        return {
            'name': flag_name,
            'default': self.DEFAULT_FLAGS[flag_name],
            'environment': self._flags.get(flag_name),
            'runtime_override': self._runtime_overrides.get(flag_name),
            'effective': self.is_enabled(flag_name),
        }

    @classmethod
    def reset_instance(cls) -> None:
        """
        Reset the singleton instance (for testing purposes).

        This method should only be used in tests to reset state between test cases.
        """
        with cls._lock:
            cls._instance = None


# Module-level convenience functions

def get_feature_flags() -> FeatureFlags:
    """
    Get the singleton FeatureFlags instance.

    Returns:
        The FeatureFlags singleton instance.
    """
    return FeatureFlags()


def feature_enabled(flag_name: str) -> bool:
    """
    Check if a feature flag is enabled.

    This is a convenience function that delegates to the FeatureFlags singleton.

    Args:
        flag_name: The name of the feature flag to check.

    Returns:
        True if the flag is enabled, False otherwise.

    Example:
        if feature_enabled('use_login_service'):
            login_service.login_with_retry(...)
        else:
            # Legacy code
            ...
    """
    return get_feature_flags().is_enabled(flag_name)


def with_feature_fallback(flag_name: str):
    """
    Decorator that provides automatic fallback on errors when a feature is enabled.

    If the decorated function raises an exception and 'fallback_on_error' is enabled,
    the original function marked with @legacy will be called instead.

    Usage:
        @with_feature_fallback('use_login_service')
        def new_login_method():
            ...

        @new_login_method.legacy
        def legacy_login_method():
            ...

    Args:
        flag_name: The name of the feature flag to check.

    Returns:
        Decorator function.
    """
    def decorator(new_func):
        legacy_func = None

        def wrapper(*args, **kwargs):
            nonlocal legacy_func

            if not feature_enabled(flag_name):
                # Feature not enabled, use legacy code
                if legacy_func is not None:
                    return legacy_func(*args, **kwargs)
                raise RuntimeError(
                    f"Feature '{flag_name}' is disabled but no legacy function provided"
                )

            try:
                return new_func(*args, **kwargs)
            except Exception as e:
                if feature_enabled('fallback_on_error') and legacy_func is not None:
                    logger.warning(
                        "Feature '%s' failed with error: %s. Falling back to legacy code.",
                        flag_name, str(e)
                    )
                    return legacy_func(*args, **kwargs)
                raise

        def legacy(func):
            nonlocal legacy_func
            legacy_func = func
            return func

        wrapper.legacy = legacy
        wrapper.__name__ = new_func.__name__
        wrapper.__doc__ = new_func.__doc__

        return wrapper

    return decorator
