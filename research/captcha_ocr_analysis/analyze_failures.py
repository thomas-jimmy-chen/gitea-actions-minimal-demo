#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Analyze failed cases to find optimization opportunities
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


def preprocess_v3_islands(image):
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    blurred = cv.medianBlur(gray, 3)
    _, binary = cv.threshold(blurred, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)
    cleaned = remove_noise_by_area(binary, min_size=40)
    cleaned = cv.medianBlur(cleaned, 3)
    cv.bitwise_not(cleaned, cleaned)
    return cleaned


def recognize(processed_img):
    pil_img = Image.fromarray(processed_img)
    config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789'
    raw = pytesseract.image_to_string(pil_img, config=config).strip()
    digits = re.findall(r'\d+', raw)
    result = ''.join(digits) if digits else raw
    return result


def analyze_image(path):
    """Analyze image characteristics"""
    image = cv.imread(path)
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    # Basic stats
    mean_val = np.mean(gray)
    std_val = np.std(gray)

    # Contrast
    min_val, max_val = np.min(gray), np.max(gray)
    contrast = max_val - min_val

    # Edge density
    edges = cv.Canny(gray, 50, 150)
    edge_density = np.sum(edges > 0) / edges.size

    # Binary analysis
    _, binary = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)
    num_labels, _, stats, _ = cv.connectedComponentsWithStats(binary, connectivity=8)

    # Component analysis
    areas = [stats[i, cv.CC_STAT_AREA] for i in range(1, num_labels)]

    return {
        'mean': mean_val,
        'std': std_val,
        'contrast': contrast,
        'edge_density': edge_density,
        'num_components': num_labels - 1,
        'total_area': sum(areas) if areas else 0,
        'max_area': max(areas) if areas else 0,
        'min_area': min(areas) if areas else 0,
    }


def main():
    samples = sorted(glob.glob(os.path.join(SAMPLES_DIR, "captcha_*.png")))

    print("=" * 70)
    print("Analyzing all samples to categorize success/failure...")
    print("=" * 70)

    success_list = []
    fail_list = []

    for path in samples:
        image = cv.imread(path)
        processed = preprocess_v3_islands(image)
        result = recognize(processed)

        is_success = len(result) >= 3 and result.isdigit()

        info = {
            'path': path,
            'filename': os.path.basename(path),
            'result': result,
            'result_len': len(result),
            **analyze_image(path)
        }

        if is_success:
            success_list.append(info)
        else:
            fail_list.append(info)

    print(f"\nSuccess: {len(success_list)}")
    print(f"Fail: {len(fail_list)}")

    # Analyze differences
    print("\n" + "=" * 70)
    print("CHARACTERISTIC COMPARISON")
    print("=" * 70)

    def avg(lst, key):
        return np.mean([x[key] for x in lst]) if lst else 0

    metrics = ['mean', 'std', 'contrast', 'edge_density', 'num_components', 'total_area']

    print(f"\n{'Metric':<20} {'Success':<15} {'Fail':<15} {'Diff':<15}")
    print("-" * 65)

    for m in metrics:
        s_avg = avg(success_list, m)
        f_avg = avg(fail_list, m)
        diff = f_avg - s_avg
        diff_pct = (diff / s_avg * 100) if s_avg != 0 else 0
        print(f"{m:<20} {s_avg:<15.2f} {f_avg:<15.2f} {diff:+.2f} ({diff_pct:+.1f}%)")

    # Show failed results
    print("\n" + "=" * 70)
    print("FAILED CASES - OCR Output")
    print("=" * 70)

    result_types = {}
    for f in fail_list:
        r = f['result']
        rtype = 'empty' if not r else f'len={len(r)}' if not r.isdigit() else f'digits_len={len(r)}'
        result_types[rtype] = result_types.get(rtype, 0) + 1

    print("\nResult types in failed cases:")
    for rtype, count in sorted(result_types.items(), key=lambda x: -x[1]):
        print(f"  {rtype}: {count}")

    # Sample failed outputs
    print("\nSample failed outputs (first 20):")
    for f in fail_list[:20]:
        print(f"  {f['filename']}: '{f['result']}' (len={f['result_len']})")

    # Find high-contrast failures (potential for improvement)
    print("\n" + "=" * 70)
    print("OPTIMIZATION OPPORTUNITIES")
    print("=" * 70)

    # Failures with good characteristics (should have succeeded)
    good_char_fails = [f for f in fail_list if f['contrast'] > 150 and f['num_components'] < 10]
    print(f"\nHigh-contrast failures (potential fixes): {len(good_char_fails)}")

    # Low contrast (harder cases)
    low_contrast = [f for f in fail_list if f['contrast'] < 100]
    print(f"Low-contrast failures (harder): {len(low_contrast)}")

    # Too many components (noisy)
    noisy = [f for f in fail_list if f['num_components'] > 15]
    print(f"High-noise failures (many components): {len(noisy)}")

    # Save failed samples for manual review
    fail_dir = os.path.join(os.path.dirname(__file__), 'failed_samples')
    if not os.path.exists(fail_dir):
        os.makedirs(fail_dir)

    # Copy first 30 failed samples
    import shutil
    for f in fail_list[:30]:
        src = f['path']
        dst = os.path.join(fail_dir, f['filename'])
        shutil.copy2(src, dst)

        # Also save processed version
        image = cv.imread(src)
        processed = preprocess_v3_islands(image)
        processed_path = os.path.join(fail_dir, f['filename'].replace('.png', '_processed.png'))
        cv.imwrite(processed_path, processed)

    print(f"\nSaved 30 failed samples to: {fail_dir}")
    print("(Both original and processed versions)")

    # Suggest optimizations
    print("\n" + "=" * 70)
    print("SUGGESTED OPTIMIZATIONS")
    print("=" * 70)

    print("""
1. CONTRAST ENHANCEMENT (for low-contrast failures)
   - CLAHE (Contrast Limited Adaptive Histogram Equalization)
   - Before: grayscale -> binarize
   - After:  grayscale -> CLAHE -> binarize

2. ADAPTIVE PARAMETERS (based on image characteristics)
   - High noise -> larger min_size
   - Low contrast -> use adaptive threshold instead of Otsu

3. MULTI-PASS STRATEGY
   - Try multiple preprocessing pipelines
   - Take result with highest confidence

4. DIGIT SEGMENTATION
   - Split into 4 individual digits
   - Recognize each separately
   - Less affected by connected noise

5. POST-PROCESSING
   - If result has 3 digits, try to recover the 4th
   - Common OCR errors: 0<->O, 1<->7, 6<->8
""")


if __name__ == "__main__":
    main()
