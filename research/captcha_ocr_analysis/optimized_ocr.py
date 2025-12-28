#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Optimized CAPTCHA OCR - Multi-strategy approach

Improvements over v3_islands:
1. Multiple PSM modes
2. Multiple min_size values
3. CLAHE contrast enhancement
4. Best result selection
"""

import os
import glob
import cv2 as cv
import numpy as np
from PIL import Image
import re

import pytesseract
tesseract_paths = [
    'C:/Users/user123456/miniconda3/envs/eebot/Library/bin/tesseract.exe',
    'C:/Program Files/Tesseract-OCR/tesseract.exe',
]
for path in tesseract_paths:
    if os.path.exists(path):
        pytesseract.pytesseract.tesseract_cmd = path
        break

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')


def remove_noise_by_area(binary_img, min_size=40):
    num_labels, labels, stats, _ = cv.connectedComponentsWithStats(binary_img, connectivity=8)
    output = np.zeros_like(binary_img)
    for i in range(1, num_labels):
        if stats[i, cv.CC_STAT_AREA] >= min_size:
            output[labels == i] = 255
    return output


def preprocess_v3(image, min_size=40):
    """Standard v3_islands"""
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    blurred = cv.medianBlur(gray, 3)
    _, binary = cv.threshold(blurred, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)
    cleaned = remove_noise_by_area(binary, min_size=min_size)
    cleaned = cv.medianBlur(cleaned, 3)
    cv.bitwise_not(cleaned, cleaned)
    return cleaned


def preprocess_clahe(image, min_size=40):
    """CLAHE enhanced version"""
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    # Apply CLAHE
    clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
    enhanced = clahe.apply(gray)
    blurred = cv.medianBlur(enhanced, 3)
    _, binary = cv.threshold(blurred, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)
    cleaned = remove_noise_by_area(binary, min_size=min_size)
    cleaned = cv.medianBlur(cleaned, 3)
    cv.bitwise_not(cleaned, cleaned)
    return cleaned


def preprocess_adaptive(image, min_size=30):
    """Adaptive threshold version"""
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    blurred = cv.medianBlur(gray, 3)
    binary = cv.adaptiveThreshold(blurred, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv.THRESH_BINARY_INV, 11, 2)
    cleaned = remove_noise_by_area(binary, min_size=min_size)
    cv.bitwise_not(cleaned, cleaned)
    return cleaned


def preprocess_sharpen(image, min_size=40):
    """Sharpened version"""
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    # Sharpen kernel
    kernel = np.array([[-1, -1, -1],
                       [-1,  9, -1],
                       [-1, -1, -1]])
    sharpened = cv.filter2D(gray, -1, kernel)
    blurred = cv.medianBlur(sharpened, 3)
    _, binary = cv.threshold(blurred, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)
    cleaned = remove_noise_by_area(binary, min_size=min_size)
    cleaned = cv.medianBlur(cleaned, 3)
    cv.bitwise_not(cleaned, cleaned)
    return cleaned


def ocr_with_config(processed_img, psm=7):
    """Run OCR with specific PSM mode"""
    pil_img = Image.fromarray(processed_img)
    config = f'--oem 3 --psm {psm} -c tessedit_char_whitelist=0123456789'
    raw = pytesseract.image_to_string(pil_img, config=config).strip()
    digits = re.findall(r'\d+', raw)
    return ''.join(digits) if digits else ''


def score_result(result):
    """Score a result - higher is better"""
    if not result:
        return 0
    if not result.isdigit():
        return 0
    # Prefer 4 digits
    if len(result) == 4:
        return 100
    elif len(result) == 3:
        return 50
    elif len(result) > 4:
        return 30  # Too many digits
    else:
        return len(result) * 10


def recognize_multi_strategy(image):
    """
    Try multiple preprocessing + OCR strategies
    Return the best result
    """
    strategies = [
        # (preprocess_func, min_size, psm)
        (preprocess_v3, 40, 7),      # Original
        (preprocess_v3, 35, 7),      # Smaller min_size
        (preprocess_v3, 30, 7),      # Even smaller
        (preprocess_v3, 40, 8),      # PSM 8: single word
        (preprocess_v3, 40, 13),     # PSM 13: raw line
        (preprocess_clahe, 40, 7),   # CLAHE enhanced
        (preprocess_clahe, 35, 7),
        (preprocess_adaptive, 30, 7), # Adaptive threshold
        (preprocess_sharpen, 40, 7),  # Sharpened
    ]

    best_result = ''
    best_score = 0

    for preprocess_func, min_size, psm in strategies:
        try:
            processed = preprocess_func(image, min_size)
            result = ocr_with_config(processed, psm)
            score = score_result(result)

            if score > best_score:
                best_score = score
                best_result = result

            # Early exit if we found perfect 4-digit result
            if score == 100:
                break
        except Exception:
            continue

    return best_result, best_score


def recognize_with_fallback(image_path):
    """
    Main recognition function with multi-strategy fallback
    """
    image = cv.imread(image_path)
    if image is None:
        return False, '', 'error'

    result, score = recognize_multi_strategy(image)

    if score >= 100:
        return True, result, 'high'
    elif score >= 50:
        return True, result, 'medium'
    elif score > 0:
        return True, result, 'low'
    else:
        return False, result, 'fail'


def test_optimized(samples_dir, limit=420):
    """Test optimized method"""
    samples = sorted(glob.glob(os.path.join(samples_dir, "captcha_*.png")))[:limit]

    print(f"Testing optimized multi-strategy OCR on {len(samples)} samples...")
    print("=" * 60)

    success = 0
    high_conf = 0

    for i, path in enumerate(samples):
        ok, result, conf = recognize_with_fallback(path)
        if ok:
            success += 1
            if conf == 'high':
                high_conf += 1

        if (i + 1) % 50 == 0:
            print(f"Progress: {i+1}/{len(samples)} - Success: {success} ({success/(i+1)*100:.1f}%)")

    rate = success / len(samples) * 100
    high_rate = high_conf / len(samples) * 100

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Total: {len(samples)}")
    print(f"Success: {success} ({rate:.1f}%)")
    print(f"High confidence: {high_conf} ({high_rate:.1f}%)")
    print(f"\nComparison:")
    print(f"  v3_islands (single):  75.7% success, 52.1% high")
    print(f"  Optimized (multi):    {rate:.1f}% success, {high_rate:.1f}% high")

    if rate > 75.7:
        print(f"\n[IMPROVEMENT] +{rate - 75.7:.1f}% over baseline!")
    else:
        print(f"\n[NO IMPROVEMENT] Multi-strategy did not help.")

    return rate, high_rate


if __name__ == "__main__":
    test_optimized(SAMPLES_DIR, 420)
