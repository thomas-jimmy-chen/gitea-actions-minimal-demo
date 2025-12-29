#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
CAPTCHA OCR Module
Provides CAPTCHA recognition with configurable retry and confidence levels

Usage:
    from src.utils.captcha_ocr import solve_captcha, CaptchaOCR

    # Simple usage
    result = solve_captcha('captcha.png')

    # Advanced usage with custom settings
    ocr = CaptchaOCR(min_confidence='high')
    result, confidence = ocr.recognize('captcha.png')
"""

import os
import sys

# Ensure research module is accessible
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from research.captcha_ocr_analysis.optimized_ocr import recognize_with_fallback


class CaptchaOCR:
    """
    CAPTCHA OCR with configurable settings

    Attributes:
        min_confidence: Minimum confidence level ('high', 'medium', 'low')
    """

    CONFIDENCE_LEVELS = ['high', 'medium', 'low']

    def __init__(self, min_confidence: str = 'medium'):
        """
        Initialize CaptchaOCR

        Args:
            min_confidence: Minimum acceptable confidence level
        """
        if min_confidence not in self.CONFIDENCE_LEVELS:
            raise ValueError(f"min_confidence must be one of {self.CONFIDENCE_LEVELS}")
        self.min_confidence = min_confidence

    def recognize(self, image_path: str) -> tuple:
        """
        Recognize CAPTCHA from image

        Args:
            image_path: Path to CAPTCHA image

        Returns:
            tuple: (result, confidence) or (None, None) if failed
        """
        if not os.path.exists(image_path):
            return None, None

        success, result, confidence = recognize_with_fallback(image_path)

        if not success:
            return None, None

        # Validate result format (must be 4 digits)
        if not self.is_valid_result(result):
            return None, confidence

        # Check confidence level
        min_idx = self.CONFIDENCE_LEVELS.index(self.min_confidence)
        result_idx = self.CONFIDENCE_LEVELS.index(confidence) if confidence in self.CONFIDENCE_LEVELS else 2

        if result_idx <= min_idx:
            return result, confidence

        return None, confidence

    def is_valid_result(self, result: str) -> bool:
        """
        Validate CAPTCHA result format

        Args:
            result: OCR result string

        Returns:
            bool: True if result appears valid (4 digits)
        """
        return result is not None and len(result) == 4 and result.isdigit()


def solve_captcha(image_path: str, min_confidence: str = 'medium') -> str:
    """
    Simple function to solve CAPTCHA

    Args:
        image_path: Path to CAPTCHA image
        min_confidence: Minimum confidence level ('high', 'medium', 'low')

    Returns:
        str: 4-digit result or None if recognition failed
    """
    ocr = CaptchaOCR(min_confidence=min_confidence)
    result, confidence = ocr.recognize(image_path)

    if result and ocr.is_valid_result(result):
        return result

    return None


def solve_captcha_with_confidence(image_path: str, min_confidence: str = 'medium') -> tuple:
    """
    Solve CAPTCHA and return confidence level

    Args:
        image_path: Path to CAPTCHA image
        min_confidence: Minimum confidence level

    Returns:
        tuple: (result, confidence) or (None, None)
    """
    ocr = CaptchaOCR(min_confidence=min_confidence)
    return ocr.recognize(image_path)
