#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Parameter Tuning for CAPTCHA OCR

Grid search to find optimal parameters for each technique.
"""

import os
import glob
import cv2 as cv
import numpy as np
from PIL import Image
import re
from itertools import product

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


def remove_noise_multidim(binary_img, min_area, min_width, min_height, max_width, max_height, ar_min, ar_max):
    num_labels, labels, stats, _ = cv.connectedComponentsWithStats(binary_img, connectivity=8)
    output = np.zeros_like(binary_img)
    for i in range(1, num_labels):
        area = stats[i, cv.CC_STAT_AREA]
        w = stats[i, cv.CC_STAT_WIDTH]
        h = stats[i, cv.CC_STAT_HEIGHT]
        ar = w / h if h > 0 else 0
        if (area >= min_area and min_width <= w <= max_width and
            min_height <= h <= max_height and ar_min <= ar <= ar_max):
            output[labels == i] = 255
    return output


def recognize(processed_img):
    """OCR recognition"""
    pil_img = Image.fromarray(processed_img)
    config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789'
    raw = pytesseract.image_to_string(pil_img, config=config).strip()
    digits = re.findall(r'\d+', raw)
    result = ''.join(digits) if digits else raw
    return len(result) == 4 and result.isdigit()


def test_islands_params(samples, min_size, blur_before, blur_after):
    """Test islands method with specific params"""
    success = 0
    for path in samples:
        image = cv.imread(path)
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        if blur_before > 0:
            gray = cv.medianBlur(gray, blur_before)
        _, binary = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)
        cleaned = remove_noise_by_area(binary, min_size)
        if blur_after > 0:
            cleaned = cv.medianBlur(cleaned, blur_after)
        cv.bitwise_not(cleaned, cleaned)
        if recognize(cleaned):
            success += 1
    return success / len(samples) * 100


def test_twostage_params(samples, erosion_k, erosion_iter, min_size, dilation_k, dilation_iter):
    """Test twostage method with specific params"""
    success = 0
    for path in samples:
        image = cv.imread(path)
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        gray = cv.medianBlur(gray, 3)
        _, binary = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)

        kernel = cv.getStructuringElement(cv.MORPH_RECT, (erosion_k, erosion_k))
        eroded = cv.erode(binary, kernel, iterations=erosion_iter)
        cleaned = remove_noise_by_area(eroded, min_size)
        kernel = cv.getStructuringElement(cv.MORPH_RECT, (dilation_k, dilation_k))
        restored = cv.dilate(cleaned, kernel, iterations=dilation_iter)
        restored = cv.medianBlur(restored, 3)
        cv.bitwise_not(restored, restored)
        if recognize(restored):
            success += 1
    return success / len(samples) * 100


def test_multidim_params(samples, min_area, min_w, min_h, max_w, max_h, ar_min, ar_max):
    """Test multidim method with specific params"""
    success = 0
    for path in samples:
        image = cv.imread(path)
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        gray = cv.medianBlur(gray, 3)
        _, binary = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)
        cleaned = remove_noise_multidim(binary, min_area, min_w, min_h, max_w, max_h, ar_min, ar_max)
        kernel = cv.getStructuringElement(cv.MORPH_RECT, (2, 2))
        cleaned = cv.morphologyEx(cleaned, cv.MORPH_CLOSE, kernel)
        cv.bitwise_not(cleaned, cleaned)
        if recognize(cleaned):
            success += 1
    return success / len(samples) * 100


def tune_islands(samples):
    """Grid search for islands method"""
    print("\n" + "=" * 60)
    print("Tuning: Islands (Area Filtering)")
    print("=" * 60)

    best_rate = 0
    best_params = None

    # Parameter grid
    min_sizes = [25, 30, 35, 40, 45, 50, 55]
    blur_befores = [0, 3, 5]
    blur_afters = [0, 3, 5]

    total = len(min_sizes) * len(blur_befores) * len(blur_afters)
    count = 0

    for min_size, blur_b, blur_a in product(min_sizes, blur_befores, blur_afters):
        count += 1
        rate = test_islands_params(samples, min_size, blur_b, blur_a)
        if rate > best_rate:
            best_rate = rate
            best_params = {'min_size': min_size, 'blur_before': blur_b, 'blur_after': blur_a}
            print(f"[{count}/{total}] NEW BEST: {rate:.1f}% - {best_params}")

    print(f"\n>>> BEST Islands: {best_rate:.1f}% with {best_params}")
    return best_rate, best_params


def tune_twostage(samples):
    """Grid search for twostage method"""
    print("\n" + "=" * 60)
    print("Tuning: Two-Stage (Erosion + Components)")
    print("=" * 60)

    best_rate = 0
    best_params = None

    # Parameter grid
    erosion_ks = [2, 3]
    erosion_iters = [1, 2]
    min_sizes = [20, 25, 30, 35]
    dilation_ks = [2, 3]
    dilation_iters = [1, 2]

    total = len(erosion_ks) * len(erosion_iters) * len(min_sizes) * len(dilation_ks) * len(dilation_iters)
    count = 0

    for e_k, e_i, min_s, d_k, d_i in product(erosion_ks, erosion_iters, min_sizes, dilation_ks, dilation_iters):
        count += 1
        rate = test_twostage_params(samples, e_k, e_i, min_s, d_k, d_i)
        if rate > best_rate:
            best_rate = rate
            best_params = {
                'erosion_kernel': e_k, 'erosion_iter': e_i,
                'min_size': min_s,
                'dilation_kernel': d_k, 'dilation_iter': d_i
            }
            print(f"[{count}/{total}] NEW BEST: {rate:.1f}% - {best_params}")

    print(f"\n>>> BEST Twostage: {best_rate:.1f}% with {best_params}")
    return best_rate, best_params


def tune_multidim(samples):
    """Grid search for multidim method"""
    print("\n" + "=" * 60)
    print("Tuning: Multi-Dimensional Filtering")
    print("=" * 60)

    best_rate = 0
    best_params = None

    # Parameter grid (reduced for speed)
    min_areas = [20, 25, 30, 35]
    min_widths = [2, 3, 4]
    min_heights = [6, 8, 10]
    max_widths = [50, 60, 70]
    max_heights = [45, 50, 55]
    ar_mins = [0.1, 0.15, 0.2]
    ar_maxs = [2.5, 3.0]

    # Sample subset for faster tuning
    total_combos = (len(min_areas) * len(min_widths) * len(min_heights) *
                   len(max_widths) * len(max_heights) * len(ar_mins) * len(ar_maxs))
    print(f"Total combinations: {total_combos}")

    count = 0
    for ma, mw, mh, xw, xh, ar_min, ar_max in product(
        min_areas, min_widths, min_heights, max_widths, max_heights, ar_mins, ar_maxs
    ):
        count += 1
        rate = test_multidim_params(samples, ma, mw, mh, xw, xh, ar_min, ar_max)
        if rate > best_rate:
            best_rate = rate
            best_params = {
                'min_area': ma, 'min_width': mw, 'min_height': mh,
                'max_width': xw, 'max_height': xh,
                'ar_range': (ar_min, ar_max)
            }
            print(f"[{count}/{total_combos}] NEW BEST: {rate:.1f}% - {best_params}")

        if count % 500 == 0:
            print(f"Progress: {count}/{total_combos}")

    print(f"\n>>> BEST Multidim: {best_rate:.1f}% with {best_params}")
    return best_rate, best_params


def main():
    samples = sorted(glob.glob(os.path.join(SAMPLES_DIR, "captcha_*.png")))
    print(f"Loaded {len(samples)} samples")

    print("\n" + "=" * 70)
    print("PARAMETER TUNING - Finding Optimal Configuration")
    print("=" * 70)

    # Tune each method
    islands_rate, islands_params = tune_islands(samples)
    twostage_rate, twostage_params = tune_twostage(samples)
    multidim_rate, multidim_params = tune_multidim(samples)

    # Summary
    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)

    results = [
        ('Islands', islands_rate, islands_params),
        ('Twostage', twostage_rate, twostage_params),
        ('Multidim', multidim_rate, multidim_params),
    ]

    for name, rate, params in sorted(results, key=lambda x: x[1], reverse=True):
        print(f"\n{name}: {rate:.1f}%")
        print(f"  Params: {params}")

    best = max(results, key=lambda x: x[1])
    print(f"\n{'='*70}")
    print(f"WINNER: {best[0]} with {best[1]:.1f}%")
    print(f"Optimal params: {best[2]}")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
