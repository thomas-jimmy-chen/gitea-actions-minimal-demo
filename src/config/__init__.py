# -*- coding: utf-8 -*-
"""
Configuration module for EEBot.

This module provides configuration management including feature flags
for safe progressive refactoring.
"""

from .feature_flags import FeatureFlags, feature_enabled, get_feature_flags

__all__ = ['FeatureFlags', 'feature_enabled', 'get_feature_flags']
