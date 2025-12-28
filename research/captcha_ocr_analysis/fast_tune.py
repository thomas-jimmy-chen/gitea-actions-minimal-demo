#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Fast Parameter Tuning - Use 100 samples for search, verify on full set
"""

import os
import glob
import cv2 as cv
import numpy as np
from PIL import Image
import re
import random

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


def remove_noise_by_area(binary_img, min_size=50):
    num_labels, labels, stats, _ = cv.connectedComponentsWithStats(binary_img, connectivity=8)
    output = np.zeros_like(binary_img)
    for i in range(1, num_labels):
        if stats[i, cv.CC_STAT_AREA] >= min_size:
            output[labels == i] = 255
    return output


def recognize(processed_img):
    pil_img = Image.fromarray(processed_img)
    config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789'
    raw = pytesseract.image_to_string(pil_img, config=config).strip()
    digits = re.findall(r'\d+', raw)
    result = ''.join(digits) if digits else raw
    return len(result) == 4 and result.isdigit()


def test_params(samples, preprocess_func, params):
    success = 0
    for path in samples:
        image = cv.imread(path)
        processed = preprocess_func(image, params)
        if recognize(processed):
            success += 1
    return success / len(samples) * 100


# ===== ISLANDS =====
def preprocess_islands(image, params):
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    if params['blur_before'] > 0:
        gray = cv.medianBlur(gray, params['blur_before'])
    _, binary = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)
    cleaned = remove_noise_by_area(binary, params['min_size'])
    if params['blur_after'] > 0:
        cleaned = cv.medianBlur(cleaned, params['blur_after'])
    cv.bitwise_not(cleaned, cleaned)
    return cleaned


# ===== TWOSTAGE =====
def preprocess_twostage(image, params):
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    gray = cv.medianBlur(gray, 3)
    _, binary = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (params['erosion_k'], params['erosion_k']))
    eroded = cv.erode(binary, kernel, iterations=params['erosion_iter'])
    cleaned = remove_noise_by_area(eroded, params['min_size'])
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (params['dilation_k'], params['dilation_k']))
    restored = cv.dilate(cleaned, kernel, iterations=params['dilation_iter'])
    restored = cv.medianBlur(restored, 3)
    cv.bitwise_not(restored, restored)
    return restored


def main():
    all_samples = sorted(glob.glob(os.path.join(SAMPLES_DIR, "captcha_*.png")))
    random.seed(42)
    search_samples = random.sample(all_samples, min(100, len(all_samples)))

    print(f"Total samples: {len(all_samples)}")
    print(f"Search samples: {len(search_samples)}")
    print("=" * 70)

    # ===== TUNE ISLANDS (主要方法) =====
    print("\n[1/2] Tuning Islands (primary method)...")
    best_islands = {'rate': 0, 'params': None}

    for min_size in range(25, 56, 5):  # 25, 30, 35, 40, 45, 50, 55
        for blur_b in [0, 3, 5]:
            for blur_a in [0, 3]:
                params = {'min_size': min_size, 'blur_before': blur_b, 'blur_after': blur_a}
                rate = test_params(search_samples, preprocess_islands, params)
                if rate > best_islands['rate']:
                    best_islands = {'rate': rate, 'params': params}
                    print(f"  NEW BEST: {rate:.1f}% - {params}")

    # ===== TUNE TWOSTAGE =====
    print("\n[2/2] Tuning Twostage...")
    best_twostage = {'rate': 0, 'params': None}

    for e_k in [2, 3]:
        for e_i in [1, 2]:
            for min_s in [20, 25, 30]:
                for d_k in [2, 3]:
                    for d_i in [1, 2]:
                        params = {
                            'erosion_k': e_k, 'erosion_iter': e_i,
                            'min_size': min_s,
                            'dilation_k': d_k, 'dilation_iter': d_i
                        }
                        rate = test_params(search_samples, preprocess_twostage, params)
                        if rate > best_twostage['rate']:
                            best_twostage = {'rate': rate, 'params': params}
                            print(f"  NEW BEST: {rate:.1f}% - {params}")

    # ===== VERIFY ON FULL SAMPLE =====
    print("\n" + "=" * 70)
    print("VERIFICATION on full sample set...")
    print("=" * 70)

    # Verify best parameters
    islands_full = test_params(all_samples, preprocess_islands, best_islands['params'])
    twostage_full = test_params(all_samples, preprocess_twostage, best_twostage['params'])

    # Also test current defaults
    current_default = {'min_size': 40, 'blur_before': 3, 'blur_after': 3}
    current_rate = test_params(all_samples, preprocess_islands, current_default)

    print(f"\nCurrent default (min_size=40, blur=3/3): {current_rate:.1f}%")
    print(f"Best Islands {best_islands['params']}: {islands_full:.1f}%")
    print(f"Best Twostage {best_twostage['params']}: {twostage_full:.1f}%")

    # ===== SUMMARY =====
    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)

    results = [
        ('Current Default', current_rate, current_default),
        ('Optimized Islands', islands_full, best_islands['params']),
        ('Optimized Twostage', twostage_full, best_twostage['params']),
    ]

    for name, rate, params in sorted(results, key=lambda x: x[1], reverse=True):
        print(f"\n{name}: {rate:.1f}%")
        print(f"  Params: {params}")

    winner = max(results, key=lambda x: x[1])
    print("\n" + "=" * 70)
    print(f"WINNER: {winner[0]} with {winner[1]:.1f}%")
    print(f"Params: {winner[2]}")
    print("=" * 70)

    # Improvement
    improvement = winner[1] - current_rate
    if improvement > 0:
        print(f"\nImprovement over current: +{improvement:.1f}%")
    else:
        print(f"\nCurrent default is already optimal!")


if __name__ == "__main__":
    main()
