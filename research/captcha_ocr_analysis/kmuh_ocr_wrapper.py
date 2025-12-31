#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
KMUH CAPTCHA OCR Wrapper
Allows calling ddddocr from any Python environment via subprocess

This wrapper can be used from the main eebot environment to call
the ddddocr-based OCR in its dedicated conda environment.

Usage:
    from kmuh_ocr_wrapper import solve_kmuh_captcha

    result = solve_kmuh_captcha('captcha.png')
    print(result)  # e.g., 'x9dh'
"""

import os
import subprocess
import tempfile

# ddddocr environment Python path
DDDDOCR_PYTHON = r"C:\Users\user123456\miniconda3\envs\ddddocr\python.exe"

# Path to the OCR module
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
KMUH_OCR_SCRIPT = os.path.join(_SCRIPT_DIR, "kmuh_ocr.py")


def solve_kmuh_captcha(image_path: str, timeout: int = 30) -> str:
    """
    Solve KMUH TMS CAPTCHA using ddddocr

    Args:
        image_path: Path to CAPTCHA image
        timeout: Timeout in seconds

    Returns:
        str: Recognition result (4 chars) or None if failed
    """
    result, confidence = solve_kmuh_captcha_with_confidence(image_path, timeout)
    return result


def solve_kmuh_captcha_with_confidence(image_path: str, timeout: int = 30) -> tuple:
    """
    Solve KMUH TMS CAPTCHA and return confidence

    Args:
        image_path: Path to CAPTCHA image
        timeout: Timeout in seconds

    Returns:
        tuple: (result, confidence)
    """
    if not os.path.exists(image_path):
        return None, 'fail'

    if not os.path.exists(DDDDOCR_PYTHON):
        print(f"[ERROR] ddddocr environment not found: {DDDDOCR_PYTHON}")
        return None, 'fail'

    try:
        # Call the OCR script in ddddocr environment
        result = subprocess.run(
            [DDDDOCR_PYTHON, KMUH_OCR_SCRIPT, image_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=_SCRIPT_DIR
        )

        if result.returncode == 0:
            output = result.stdout.strip()
            if '|' in output:
                parts = output.split('|')
                ocr_result = parts[0] if parts[0] else None
                confidence = parts[1] if len(parts) > 1 else 'fail'
                return ocr_result, confidence

        # Error handling
        if result.stderr:
            print(f"[ERROR] OCR stderr: {result.stderr}")

        return None, 'fail'

    except subprocess.TimeoutExpired:
        print(f"[ERROR] OCR timeout after {timeout}s")
        return None, 'fail'
    except Exception as e:
        print(f"[ERROR] OCR failed: {e}")
        return None, 'fail'


def solve_kmuh_captcha_bytes(img_bytes: bytes, timeout: int = 30) -> tuple:
    """
    Solve KMUH TMS CAPTCHA from image bytes

    Args:
        img_bytes: Image data as bytes
        timeout: Timeout in seconds

    Returns:
        tuple: (result, confidence)
    """
    # Save bytes to temp file
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        f.write(img_bytes)
        temp_path = f.name

    try:
        return solve_kmuh_captcha_with_confidence(temp_path, timeout)
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_path)
        except:
            pass


class KmuhCaptchaOCRWrapper:
    """
    Wrapper class for KMUH CAPTCHA OCR

    Compatible with the e大學 CaptchaOCR interface
    """

    CONFIDENCE_LEVELS = ['high', 'medium', 'low']

    def __init__(self, min_confidence: str = 'medium'):
        """
        Initialize wrapper

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
        result, confidence = solve_kmuh_captcha_with_confidence(image_path)

        if not result:
            return None, confidence

        # Check confidence level
        if confidence in self.CONFIDENCE_LEVELS:
            min_idx = self.CONFIDENCE_LEVELS.index(self.min_confidence)
            result_idx = self.CONFIDENCE_LEVELS.index(confidence)

            if result_idx <= min_idx:
                return result, confidence

        return None, confidence

    def is_valid_result(self, result: str) -> bool:
        """
        Validate CAPTCHA result format

        Args:
            result: OCR result string

        Returns:
            bool: True if result appears valid (4 alphanumeric chars)
        """
        return result is not None and len(result) == 4 and result.isalnum()


# Test function
def test_wrapper():
    """Test the wrapper with sample images"""
    import glob

    samples_dir = os.path.join(_SCRIPT_DIR, 'samples_kmuh')
    samples = sorted(glob.glob(os.path.join(samples_dir, "kmuh_captcha_*.png")))[:10]

    print("=" * 60)
    print("  KMUH OCR Wrapper Test")
    print("=" * 60)

    for path in samples:
        result, confidence = solve_kmuh_captcha_with_confidence(path)
        filename = os.path.basename(path)
        print(f"  {filename}: {result or 'FAILED':<10} ({confidence})")

    print("=" * 60)


if __name__ == "__main__":
    test_wrapper()
