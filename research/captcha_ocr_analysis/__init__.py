#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
CAPTCHA OCR Analysis Module

Provides OCR solutions for different CAPTCHA types:

1. e大學 (elearn.post.gov.tw) - Pure numeric (4 digits)
   - Uses: Tesseract OCR with multi-strategy preprocessing
   - Accuracy: 97.6%
   - Module: optimized_ocr

2. KMUH TMS (tms.kmuh.org.tw) - Alphanumeric (4 chars)
   - Uses: ddddocr (deep learning)
   - Accuracy: ~85-90%
   - Module: kmuh_ocr_wrapper

Usage:
    # For e大學
    from research.captcha_ocr_analysis.optimized_ocr import recognize_with_fallback

    # For KMUH TMS (can be called from any environment)
    from research.captcha_ocr_analysis.kmuh_ocr_wrapper import (
        solve_kmuh_captcha,
        solve_kmuh_captcha_with_confidence,
        KmuhCaptchaOCRWrapper
    )
"""

# e大學 OCR exports
try:
    from .optimized_ocr import recognize_with_fallback
except ImportError:
    pass

# KMUH OCR exports (wrapper - works from any env)
try:
    from .kmuh_ocr_wrapper import (
        solve_kmuh_captcha,
        solve_kmuh_captcha_with_confidence,
        solve_kmuh_captcha_bytes,
        KmuhCaptchaOCRWrapper,
    )
except ImportError:
    pass

__all__ = [
    # e大學
    'recognize_with_fallback',
    # KMUH
    'solve_kmuh_captcha',
    'solve_kmuh_captcha_with_confidence',
    'solve_kmuh_captcha_bytes',
    'KmuhCaptchaOCRWrapper',
]
