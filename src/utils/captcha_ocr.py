#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
CAPTCHA OCR Module
Provides CAPTCHA recognition with configurable retry and confidence levels

支援兩種 OCR 引擎:
- optimized: 針對 e大學 4 位數字驗證碼優化 (97.6% 準確率)
- ddddocr: 通用 OCR，支援數字+字母混合驗證碼

Usage:
    from src.utils.captcha_ocr import solve_captcha, solve_captcha_ddddocr

    # e大學 4 位數字驗證碼
    result = solve_captcha('captcha.png')

    # 通用驗證碼 (如 tour.post 6 位數字+字母)
    result = solve_captcha_ddddocr('captcha.png')

    # 進階用法
    ocr = CaptchaOCR(engine='ddddocr')
    result = ocr.recognize('captcha.png')
"""

import os
import sys
from typing import Optional, Tuple

# Ensure research module is accessible
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from research.captcha_ocr_analysis.optimized_ocr import recognize_with_fallback

# ddddocr 延遲載入，避免未安裝時報錯
_ddddocr_instance = None


def _get_ddddocr():
    """延遲載入 ddddocr 實例"""
    global _ddddocr_instance
    if _ddddocr_instance is None:
        try:
            import ddddocr
            _ddddocr_instance = ddddocr.DdddOcr()
        except ImportError:
            raise ImportError(
                "ddddocr 未安裝。請執行: pip install ddddocr"
            )
    return _ddddocr_instance


class CaptchaOCR:
    """
    CAPTCHA OCR with configurable settings

    Attributes:
        engine: OCR 引擎 ('optimized' 或 'ddddocr')
        min_confidence: Minimum confidence level ('high', 'medium', 'low')
        expected_length: 預期驗證碼長度 (None 表示不限制)
        allow_letters: 是否允許字母 (ddddocr 專用)
    """

    CONFIDENCE_LEVELS = ['high', 'medium', 'low']
    SUPPORTED_ENGINES = ['optimized', 'ddddocr']

    def __init__(
        self,
        engine: str = 'optimized',
        min_confidence: str = 'medium',
        expected_length: Optional[int] = None,
        allow_letters: bool = False
    ):
        """
        Initialize CaptchaOCR

        Args:
            engine: OCR 引擎 ('optimized' 或 'ddddocr')
            min_confidence: Minimum acceptable confidence level
            expected_length: 預期驗證碼長度 (None 表示不限制)
            allow_letters: 是否允許字母 (ddddocr 專用)
        """
        if engine not in self.SUPPORTED_ENGINES:
            raise ValueError(f"engine must be one of {self.SUPPORTED_ENGINES}")
        if min_confidence not in self.CONFIDENCE_LEVELS:
            raise ValueError(f"min_confidence must be one of {self.CONFIDENCE_LEVELS}")

        self.engine = engine
        self.min_confidence = min_confidence
        self.expected_length = expected_length
        self.allow_letters = allow_letters

        # 設定預設值
        if engine == 'optimized' and expected_length is None:
            self.expected_length = 4
            self.allow_letters = False

    def recognize(self, image_path: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Recognize CAPTCHA from image

        Args:
            image_path: Path to CAPTCHA image

        Returns:
            tuple: (result, confidence) or (None, None) if failed
        """
        if not os.path.exists(image_path):
            return None, None

        if self.engine == 'ddddocr':
            return self._recognize_ddddocr(image_path)
        else:
            return self._recognize_optimized(image_path)

    def _recognize_optimized(self, image_path: str) -> Tuple[Optional[str], Optional[str]]:
        """使用 optimized 引擎辨識 (e大學 4 位數字)"""
        success, result, confidence = recognize_with_fallback(image_path)

        if not success:
            return None, None

        # Validate result format (must be 4 digits)
        if not self._is_valid_optimized(result):
            return None, confidence

        # Check confidence level
        min_idx = self.CONFIDENCE_LEVELS.index(self.min_confidence)
        result_idx = self.CONFIDENCE_LEVELS.index(confidence) if confidence in self.CONFIDENCE_LEVELS else 2

        if result_idx <= min_idx:
            return result, confidence

        return None, confidence

    def _recognize_ddddocr(self, image_path: str) -> Tuple[Optional[str], Optional[str]]:
        """使用 ddddocr 引擎辨識 (通用驗證碼)"""
        try:
            ocr = _get_ddddocr()

            with open(image_path, 'rb') as f:
                image_bytes = f.read()

            result = ocr.classification(image_bytes)

            if not result:
                return None, None

            # 驗證結果
            if not self._is_valid_ddddocr(result):
                return None, 'low'

            # ddddocr 沒有信心值，根據結果長度判斷
            if self.expected_length and len(result) == self.expected_length:
                confidence = 'high'
            elif self.expected_length and abs(len(result) - self.expected_length) == 1:
                confidence = 'medium'
            else:
                confidence = 'low' if self.expected_length else 'medium'

            return result, confidence

        except Exception as e:
            print(f"[ddddocr] 辨識失敗: {e}")
            return None, None

    def _is_valid_optimized(self, result: str) -> bool:
        """驗證 optimized 引擎結果 (4 位數字)"""
        return result is not None and len(result) == 4 and result.isdigit()

    def _is_valid_ddddocr(self, result: str) -> bool:
        """驗證 ddddocr 引擎結果"""
        if result is None or len(result) == 0:
            return False

        # 檢查長度
        if self.expected_length and len(result) != self.expected_length:
            # 允許長度差 1 (可能漏字符)
            if abs(len(result) - self.expected_length) > 1:
                return False

        # 檢查字符類型
        if self.allow_letters:
            return result.replace('x', 'X').replace('X', '').isdigit() or result.isalnum()
        else:
            return result.isdigit()

    def is_valid_result(self, result: str) -> bool:
        """
        Validate CAPTCHA result format (向後兼容)

        Args:
            result: OCR result string

        Returns:
            bool: True if result appears valid
        """
        if self.engine == 'ddddocr':
            return self._is_valid_ddddocr(result)
        return self._is_valid_optimized(result)


def solve_captcha(image_path: str, min_confidence: str = 'medium') -> Optional[str]:
    """
    Simple function to solve CAPTCHA (e大學 4 位數字)

    Args:
        image_path: Path to CAPTCHA image
        min_confidence: Minimum confidence level ('high', 'medium', 'low')

    Returns:
        str: 4-digit result or None if recognition failed
    """
    ocr = CaptchaOCR(engine='optimized', min_confidence=min_confidence)
    result, confidence = ocr.recognize(image_path)

    if result and ocr.is_valid_result(result):
        return result

    return None


def solve_captcha_with_confidence(image_path: str, min_confidence: str = 'medium') -> Tuple[Optional[str], Optional[str]]:
    """
    Solve CAPTCHA and return confidence level (e大學 4 位數字)

    Args:
        image_path: Path to CAPTCHA image
        min_confidence: Minimum confidence level

    Returns:
        tuple: (result, confidence) or (None, None)
    """
    ocr = CaptchaOCR(engine='optimized', min_confidence=min_confidence)
    return ocr.recognize(image_path)


def solve_captcha_ddddocr(
    image_path: str,
    expected_length: Optional[int] = None,
    allow_letters: bool = True
) -> Optional[str]:
    """
    使用 ddddocr 辨識通用驗證碼

    Args:
        image_path: 驗證碼圖片路徑
        expected_length: 預期驗證碼長度 (如 6)，None 表示不限制
        allow_letters: 是否允許字母 (預設 True)

    Returns:
        str: 辨識結果或 None

    Example:
        # tour.post 6 位數字+字母驗證碼
        result = solve_captcha_ddddocr('captcha.jpg', expected_length=6)
    """
    ocr = CaptchaOCR(
        engine='ddddocr',
        expected_length=expected_length,
        allow_letters=allow_letters
    )
    result, confidence = ocr.recognize(image_path)
    return result


def solve_captcha_bytes(
    image_bytes: bytes,
    engine: str = 'ddddocr',
    expected_length: Optional[int] = None,
    allow_letters: bool = True
) -> Optional[str]:
    """
    從圖片 bytes 辨識驗證碼 (不需要存檔)

    Args:
        image_bytes: 圖片二進位資料
        engine: OCR 引擎 ('ddddocr' 或 'optimized')
        expected_length: 預期驗證碼長度
        allow_letters: 是否允許字母

    Returns:
        str: 辨識結果或 None

    Example:
        # 從網路下載的圖片直接辨識
        response = requests.get(captcha_url)
        result = solve_captcha_bytes(response.content, expected_length=6)
    """
    if engine == 'ddddocr':
        try:
            ocr = _get_ddddocr()
            result = ocr.classification(image_bytes)

            if not result:
                return None

            # 基本驗證
            if expected_length and abs(len(result) - expected_length) > 1:
                return None

            if not allow_letters and not result.isdigit():
                return None

            return result

        except Exception as e:
            print(f"[ddddocr] 辨識失敗: {e}")
            return None
    else:
        # optimized 引擎需要檔案路徑，暫存處理
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            f.write(image_bytes)
            temp_path = f.name

        try:
            return solve_captcha(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
