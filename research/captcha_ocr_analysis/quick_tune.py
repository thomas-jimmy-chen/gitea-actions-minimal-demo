#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Quick Parameter Tuning - Focused search on most impactful parameters
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


# ===== MULTIDIM (simplified) =====
def remove_noise_multidim(binary_img, min_area, ar_min, ar_max):
    num_labels, labels, stats, _ = cv.connectedComponentsWithStats(binary_img, connectivity=8)
    output = np.zeros_like(binary_img)
    for i in range(1, num_labels):
        area = stats[i, cv.CC_STAT_AREA]
        w = stats[i, cv.CC_STAT_WIDTH]
        h = stats[i, cv.CC_STAT_HEIGHT]
        ar = w / h if h > 0 else 0
        if area >= min_area and ar_min <= ar <= ar_max:
            output[labels == i] = 255
    return output


def preprocess_multidim(image, params):
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    gray = cv.medianBlur(gray, 3)
    _, binary = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)
    cleaned = remove_noise_multidim(binary, params['min_area'], params['ar_min'], params['ar_max'])
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (2, 2))
    cleaned = cv.morphologyEx(cleaned, cv.MORPH_CLOSE, kernel)
    cv.bitwise_not(cleaned, cleaned)
    return cleaned


def main():
    samples = sorted(glob.glob(os.path.join(SAMPLES_DIR, "captcha_*.png")))
    print(f"Loaded {len(samples)} samples")
    print("=" * 70)

    best_overall = {'method': None, 'rate': 0, 'params': None}

    # ===== TUNE ISLANDS =====
    print("\n[1/3] Tuning Islands...")
    best_islands = {'rate': 0, 'params': None}
    for min_size in [30, 35, 40, 45, 50]:
        for blur_b in [0, 3, 5]:
            for blur_a in [0, 3]:
                params = {'min_size': min_size, 'blur_before': blur_b, 'blur_after': blur_a}
                rate = test_params(samples, preprocess_islands, params)
                if rate > best_islands['rate']:
                    best_islands = {'rate': rate, 'params': params}
                    print(f"  NEW BEST: {rate:.1f}% - {params}")

    print(f"\n>>> Islands Best: {best_islands['rate']:.1f}%")
    if best_islands['rate'] > best_overall['rate']:
        best_overall = {'method': 'Islands', **best_islands}

    # ===== TUNE TWOSTAGE =====
    print("\n[2/3] Tuning Twostage...")
    best_twostage = {'rate': 0, 'params': None}
    for e_k in [2, 3]:
        for e_i in [1, 2]:
            for min_s in [20, 25, 30, 35]:
                for d_k in [2, 3]:
                    for d_i in [1, 2]:
                        params = {
                            'erosion_k': e_k, 'erosion_iter': e_i,
                            'min_size': min_s,
                            'dilation_k': d_k, 'dilation_iter': d_i
                        }
                        rate = test_params(samples, preprocess_twostage, params)
                        if rate > best_twostage['rate']:
                            best_twostage = {'rate': rate, 'params': params}
                            print(f"  NEW BEST: {rate:.1f}% - {params}")

    print(f"\n>>> Twostage Best: {best_twostage['rate']:.1f}%")
    if best_twostage['rate'] > best_overall['rate']:
        best_overall = {'method': 'Twostage', **best_twostage}

    # ===== TUNE MULTIDIM (simplified) =====
    print("\n[3/3] Tuning Multidim (simplified)...")
    best_multidim = {'rate': 0, 'params': None}
    for min_area in [20, 25, 30, 35, 40]:
        for ar_min in [0.1, 0.15, 0.2]:
            for ar_max in [2.0, 2.5, 3.0]:
                params = {'min_area': min_area, 'ar_min': ar_min, 'ar_max': ar_max}
                rate = test_params(samples, preprocess_multidim, params)
                if rate > best_multidim['rate']:
                    best_multidim = {'rate': rate, 'params': params}
                    print(f"  NEW BEST: {rate:.1f}% - {params}")

    print(f"\n>>> Multidim Best: {best_multidim['rate']:.1f}%")
    if best_multidim['rate'] > best_overall['rate']:
        best_overall = {'method': 'Multidim', **best_multidim}

    # ===== SUMMARY =====
    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    print(f"\nIslands:  {best_islands['rate']:.1f}%  {best_islands['params']}")
    print(f"Twostage: {best_twostage['rate']:.1f}%  {best_twostage['params']}")
    print(f"Multidim: {best_multidim['rate']:.1f}%  {best_multidim['params']}")

    print("\n" + "=" * 70)
    print(f"WINNER: {best_overall['method']} with {best_overall['rate']:.1f}%")
    print(f"Params: {best_overall['params']}")
    print("=" * 70)

    return best_overall


if __name__ == "__main__":
    main()
