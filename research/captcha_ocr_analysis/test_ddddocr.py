#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Test ddddocr with and without v3_islands preprocessing
"""

import os
import glob
import cv2 as cv
import numpy as np

# Install: pip install ddddocr
import ddddocr

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')


def remove_noise_by_area(binary_img, min_size=40):
    """Connected components area filtering"""
    num_labels, labels, stats, _ = cv.connectedComponentsWithStats(
        binary_img, connectivity=8
    )
    output = np.zeros_like(binary_img)
    for i in range(1, num_labels):
        if stats[i, cv.CC_STAT_AREA] >= min_size:
            output[labels == i] = 255
    return output


def preprocess_v3_islands(image):
    """v3_islands preprocessing"""
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    blurred = cv.medianBlur(gray, 3)
    _, binary = cv.threshold(blurred, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)
    cleaned = remove_noise_by_area(binary, min_size=40)
    cleaned = cv.medianBlur(cleaned, 3)
    cv.bitwise_not(cleaned, cleaned)
    return cleaned


def test_ddddocr(samples, use_preprocessing=False, limit=100):
    """Test ddddocr on samples"""
    ocr = ddddocr.DdddOcr()

    success_count = 0
    high_conf = 0

    for i, path in enumerate(samples[:limit]):
        try:
            if use_preprocessing:
                # Read and preprocess
                image = cv.imread(path)
                processed = preprocess_v3_islands(image)
                # Encode to bytes
                _, buffer = cv.imencode('.png', processed)
                img_bytes = buffer.tobytes()
            else:
                # Read raw image
                with open(path, 'rb') as f:
                    img_bytes = f.read()

            # OCR
            result = ocr.classification(img_bytes)

            # Validate (4 digits)
            if len(result) == 4 and result.isdigit():
                success_count += 1
                high_conf += 1
            elif len(result) >= 3 and result.replace(' ', '').isdigit():
                success_count += 1

        except Exception as e:
            pass

        if (i + 1) % 20 == 0:
            print(f"Progress: {i+1}/{limit} - Success: {success_count}")

    return success_count, high_conf


def main():
    samples = sorted(glob.glob(os.path.join(SAMPLES_DIR, "captcha_*.png")))
    print(f"Total samples: {len(samples)}")

    limit = min(420, len(samples))

    print("\n" + "=" * 60)
    print("Test 1: ddddocr (raw image, no preprocessing)")
    print("=" * 60)
    raw_success, raw_high = test_ddddocr(samples, use_preprocessing=False, limit=limit)
    raw_rate = raw_success / limit * 100
    raw_high_rate = raw_high / limit * 100
    print(f"\nResult: {raw_success}/{limit} ({raw_rate:.1f}%)")
    print(f"High confidence (4-digit): {raw_high} ({raw_high_rate:.1f}%)")

    print("\n" + "=" * 60)
    print("Test 2: ddddocr + v3_islands preprocessing")
    print("=" * 60)
    pre_success, pre_high = test_ddddocr(samples, use_preprocessing=True, limit=limit)
    pre_rate = pre_success / limit * 100
    pre_high_rate = pre_high / limit * 100
    print(f"\nResult: {pre_success}/{limit} ({pre_rate:.1f}%)")
    print(f"High confidence (4-digit): {pre_high} ({pre_high_rate:.1f}%)")

    print("\n" + "=" * 60)
    print("COMPARISON")
    print("=" * 60)
    print(f"ddddocr (raw):           {raw_rate:.1f}% (high: {raw_high_rate:.1f}%)")
    print(f"ddddocr + v3_islands:    {pre_rate:.1f}% (high: {pre_high_rate:.1f}%)")
    print(f"pytesseract + v3_islands: 75.7% (high: 52.1%)")

    if pre_rate > raw_rate:
        print(f"\nv3_islands preprocessing improved ddddocr by +{pre_rate - raw_rate:.1f}%")
    elif raw_rate > pre_rate:
        print(f"\nddddocr works better with raw images (+{raw_rate - pre_rate:.1f}%)")


if __name__ == "__main__":
    main()
