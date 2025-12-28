# -*- coding: utf-8 -*-
"""
Unit Tests for Feature Flags Module.

Tests the feature flag mechanism for progressive refactoring.
"""

import os
import sys
import importlib
import pytest


def _get_fresh_module():
    """Get a fresh import of the feature_flags module."""
    module_name = 'src.config.feature_flags'

    # Check if it's a Mock and clear it
    if module_name in sys.modules:
        module = sys.modules[module_name]
        if hasattr(module, '_mock_name') or 'MagicMock' in str(type(module)):
            del sys.modules[module_name]
            for mod_name in list(sys.modules.keys()):
                if mod_name.startswith('src.config') and hasattr(sys.modules[mod_name], '_mock_name'):
                    del sys.modules[mod_name]

    # Import fresh
    return importlib.import_module(module_name)


# Get initial references (may be updated by fixtures)
_ff_module = _get_fresh_module()
FeatureFlags = _ff_module.FeatureFlags
feature_enabled = _ff_module.feature_enabled
get_feature_flags = _ff_module.get_feature_flags
with_feature_fallback = _ff_module.with_feature_fallback


@pytest.fixture(autouse=True)
def refresh_module_references():
    """Refresh module references before each test to ensure we use real module."""
    global FeatureFlags, feature_enabled, get_feature_flags, with_feature_fallback

    # Clear mock if needed and reload
    module_name = 'src.config.feature_flags'
    if module_name in sys.modules:
        module = sys.modules[module_name]
        if hasattr(module, '_mock_name') or 'MagicMock' in str(type(module)):
            del sys.modules[module_name]
            importlib.import_module(module_name)

    # Reload and get fresh references
    module = importlib.reload(sys.modules[module_name])
    FeatureFlags = module.FeatureFlags
    feature_enabled = module.feature_enabled
    get_feature_flags = module.get_feature_flags
    with_feature_fallback = module.with_feature_fallback

    # Reset the singleton
    FeatureFlags.reset_instance()

    yield

    # Reset after test
    FeatureFlags.reset_instance()


class TestFeatureFlags:
    """Test cases for FeatureFlags class."""

    def test_singleton_instance(self, reset_feature_flags):
        """Test that FeatureFlags is a singleton."""
        flags1 = FeatureFlags()
        flags2 = FeatureFlags()

        assert flags1 is flags2

    def test_default_flags_disabled(self, reset_feature_flags):
        """Test that BrowserSession flag is disabled by default (not yet integrated)."""
        flags = FeatureFlags()

        # BrowserSession is still disabled (not integrated yet)
        assert not flags.is_enabled('use_browser_session')

    def test_phase1_flags_status(self, reset_feature_flags):
        """Test Phase 1 flags current status."""
        flags = FeatureFlags()

        # use_login_service is disabled (needs debugging)
        assert not flags.is_enabled('use_login_service')
        # use_scroll_utils is enabled (integration complete)
        assert flags.is_enabled('use_scroll_utils')

    def test_orchestrators_enabled_by_default(self, reset_feature_flags):
        """Test that use_orchestrators is enabled by default (Service layer complete)."""
        flags = FeatureFlags()

        assert flags.is_enabled('use_orchestrators')

    def test_fallback_enabled_by_default(self, reset_feature_flags):
        """Test that fallback_on_error is enabled by default."""
        flags = FeatureFlags()

        assert flags.is_enabled('fallback_on_error')

    def test_enable_flag(self, reset_feature_flags):
        """Test enabling a feature flag at runtime."""
        flags = FeatureFlags()

        # use_browser_session is disabled by default
        assert not flags.is_enabled('use_browser_session')

        flags.enable('use_browser_session')

        assert flags.is_enabled('use_browser_session')

    def test_disable_flag(self, reset_feature_flags):
        """Test disabling a feature flag at runtime."""
        flags = FeatureFlags()

        # use_orchestrators is enabled by default, disable it
        assert flags.is_enabled('use_orchestrators')

        flags.disable('use_orchestrators')

        assert not flags.is_enabled('use_orchestrators')

    def test_reset_single_flag(self, reset_feature_flags):
        """Test resetting a single flag to default."""
        flags = FeatureFlags()

        # Disable enabled-by-default flags
        flags.disable('use_orchestrators')
        flags.disable('use_scroll_utils')

        flags.reset('use_orchestrators')

        # Should be back to default (True)
        assert flags.is_enabled('use_orchestrators')
        # Should still be overridden (False)
        assert not flags.is_enabled('use_scroll_utils')

    def test_reset_all_flags(self, reset_feature_flags):
        """Test resetting all flags to defaults."""
        flags = FeatureFlags()

        # Override all flags to opposite of default
        flags.disable('use_orchestrators')
        flags.disable('use_scroll_utils')
        flags.enable('use_browser_session')

        flags.reset()

        # Should be back to defaults
        assert flags.is_enabled('use_orchestrators')
        assert flags.is_enabled('use_scroll_utils')
        assert not flags.is_enabled('use_browser_session')

    def test_unknown_flag_raises_error(self, reset_feature_flags):
        """Test that accessing unknown flag raises KeyError."""
        flags = FeatureFlags()

        with pytest.raises(KeyError, match='Unknown feature flag'):
            flags.is_enabled('unknown_flag')

    def test_enable_unknown_flag_raises_error(self, reset_feature_flags):
        """Test that enabling unknown flag raises KeyError."""
        flags = FeatureFlags()

        with pytest.raises(KeyError, match='Unknown feature flag'):
            flags.enable('unknown_flag')

    def test_disable_unknown_flag_raises_error(self, reset_feature_flags):
        """Test that disabling unknown flag raises KeyError."""
        flags = FeatureFlags()

        with pytest.raises(KeyError, match='Unknown feature flag'):
            flags.disable('unknown_flag')

    def test_get_all_flags(self, reset_feature_flags):
        """Test getting all flag values."""
        flags = FeatureFlags()

        all_flags = flags.get_all_flags()

        assert 'use_login_service' in all_flags
        assert 'use_scroll_utils' in all_flags
        assert 'use_browser_session' in all_flags
        assert 'use_orchestrators' in all_flags
        assert 'fallback_on_error' in all_flags

    def test_get_flag_status(self, reset_feature_flags):
        """Test getting detailed flag status."""
        flags = FeatureFlags()

        # Enable a disabled-by-default flag
        flags.enable('use_browser_session')

        status = flags.get_flag_status('use_browser_session')

        assert status['name'] == 'use_browser_session'
        assert status['default'] is False
        assert status['runtime_override'] is True
        assert status['effective'] is True


class TestEnvironmentVariables:
    """Test cases for environment variable configuration."""

    def test_env_var_true(self, reset_feature_flags, clean_env):
        """Test enabling flag via environment variable."""
        os.environ['EEBOT_FF_USE_LOGIN_SERVICE'] = 'true'

        flags = FeatureFlags()

        assert flags.is_enabled('use_login_service')

    def test_env_var_false(self, reset_feature_flags, clean_env):
        """Test disabling fallback via environment variable."""
        os.environ['EEBOT_FF_FALLBACK_ON_ERROR'] = 'false'

        flags = FeatureFlags()

        assert not flags.is_enabled('fallback_on_error')

    def test_env_var_yes(self, reset_feature_flags, clean_env):
        """Test 'yes' value for environment variable."""
        os.environ['EEBOT_FF_USE_SCROLL_UTILS'] = 'yes'

        flags = FeatureFlags()

        assert flags.is_enabled('use_scroll_utils')

    def test_env_var_1(self, reset_feature_flags, clean_env):
        """Test '1' value for environment variable."""
        os.environ['EEBOT_FF_USE_BROWSER_SESSION'] = '1'

        flags = FeatureFlags()

        assert flags.is_enabled('use_browser_session')

    def test_runtime_override_takes_priority(self, reset_feature_flags, clean_env):
        """Test that runtime overrides take priority over environment."""
        os.environ['EEBOT_FF_USE_LOGIN_SERVICE'] = 'true'

        flags = FeatureFlags()
        assert flags.is_enabled('use_login_service')

        flags.disable('use_login_service')

        assert not flags.is_enabled('use_login_service')


class TestConvenienceFunctions:
    """Test cases for module-level convenience functions."""

    def test_feature_enabled_function(self, reset_feature_flags):
        """Test feature_enabled convenience function."""
        # use_browser_session is disabled by default
        assert not feature_enabled('use_browser_session')

        get_feature_flags().enable('use_browser_session')

        assert feature_enabled('use_browser_session')

    def test_get_feature_flags_returns_singleton(self, reset_feature_flags):
        """Test get_feature_flags returns singleton."""
        flags1 = get_feature_flags()
        flags2 = get_feature_flags()

        assert flags1 is flags2


class TestWithFeatureFallback:
    """Test cases for with_feature_fallback decorator."""

    def test_fallback_when_feature_disabled(self, reset_feature_flags):
        """Test fallback is called when feature is disabled."""
        call_log = []

        # use_browser_session is disabled by default
        @with_feature_fallback('use_browser_session')
        def new_function():
            call_log.append('new')
            return 'new_result'

        @new_function.legacy
        def legacy_function():
            call_log.append('legacy')
            return 'legacy_result'

        result = new_function()

        assert result == 'legacy_result'
        assert call_log == ['legacy']

    def test_new_function_when_feature_enabled(self, reset_feature_flags):
        """Test new function is called when feature is enabled."""
        call_log = []

        get_feature_flags().enable('use_browser_session')

        @with_feature_fallback('use_browser_session')
        def new_function():
            call_log.append('new')
            return 'new_result'

        @new_function.legacy
        def legacy_function():
            call_log.append('legacy')
            return 'legacy_result'

        result = new_function()

        assert result == 'new_result'
        assert call_log == ['new']

    def test_fallback_on_error(self, reset_feature_flags):
        """Test fallback is called when new function raises error."""
        call_log = []

        flags = get_feature_flags()
        flags.enable('use_browser_session')
        flags.enable('fallback_on_error')

        @with_feature_fallback('use_browser_session')
        def new_function():
            call_log.append('new')
            raise ValueError("New function failed")

        @new_function.legacy
        def legacy_function():
            call_log.append('legacy')
            return 'legacy_result'

        result = new_function()

        assert result == 'legacy_result'
        assert call_log == ['new', 'legacy']

    def test_error_propagates_when_fallback_disabled(self, reset_feature_flags):
        """Test error propagates when fallback_on_error is disabled."""
        flags = get_feature_flags()
        flags.enable('use_browser_session')
        flags.disable('fallback_on_error')

        @with_feature_fallback('use_browser_session')
        def new_function():
            raise ValueError("New function failed")

        @new_function.legacy
        def legacy_function():
            return 'legacy_result'

        with pytest.raises(ValueError, match="New function failed"):
            new_function()

    def test_error_when_no_legacy_and_feature_disabled(self, reset_feature_flags):
        """Test error when feature disabled but no legacy function."""
        # use_browser_session is disabled by default
        @with_feature_fallback('use_browser_session')
        def new_function():
            return 'new_result'

        with pytest.raises(RuntimeError, match="no legacy function provided"):
            new_function()


class TestThreadSafety:
    """Test cases for thread safety."""

    def test_concurrent_access(self, reset_feature_flags):
        """Test concurrent access to feature flags."""
        import threading

        flags = get_feature_flags()
        results = []
        errors = []

        def toggle_flag():
            try:
                for _ in range(100):
                    flags.enable('use_login_service')
                    flags.is_enabled('use_login_service')
                    flags.disable('use_login_service')
                results.append('success')
            except Exception as e:
                errors.append(str(e))

        threads = [threading.Thread(target=toggle_flag) for _ in range(10)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(results) == 10
