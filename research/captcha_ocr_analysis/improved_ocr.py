#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Improved CAPTCHA OCR

Multiple preprocessing strategies for better recognition:
1. Connected Components - Remove noise islands
2. Adaptive Thresholding
3. Non-local Means Denoising
4. Multiple kernel sizes for morphological operations
"""

import os
import cv2 as cv
import numpy as np
from PIL import Image
import re

# Tesseract setup
import pytesseract
tesseract_paths = [
    'C:/Users/user123456/miniconda3/envs/eebot/Library/bin/tesseract.exe',
    'C:/Program Files/Tesseract-OCR/tesseract.exe',
]
for path in tesseract_paths:
    if os.path.exists(path):
        pytesseract.pytesseract.tesseract_cmd = path
        break


def remove_noise_islands(binary_img, min_size=50):
    """
    Remove small noise islands using connected components

    Args:
        binary_img: Binary image (white text on black background)
        min_size: Minimum pixel count to keep a component

    Returns:
        Cleaned binary image
    """
    # Find connected components
    num_labels, labels, stats, centroids = cv.connectedComponentsWithStats(
        binary_img, connectivity=8
    )

    # Create output image
    output = np.zeros_like(binary_img)

    # Keep only large components (skip background label 0)
    for i in range(1, num_labels):
        area = stats[i, cv.CC_STAT_AREA]
        if area >= min_size:
            output[labels == i] = 255

    return output


def preprocess_v1_original(image):
    """Original Auto-WFH method"""
    blur = cv.pyrMeanShiftFiltering(image, sp=8, sr=60)
    gray = cv.cvtColor(blur, cv.COLOR_BGR2GRAY)
    ret, binary = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)
    kernel1 = cv.getStructuringElement(cv.MORPH_RECT, (3, 2))
    bin1 = cv.morphologyEx(binary, cv.MORPH_OPEN, kernel1)
    kernel2 = cv.getStructuringElement(cv.MORPH_RECT, (2, 3))
    bin2 = cv.morphologyEx(bin1, cv.MORPH_OPEN, kernel2)
    cv.bitwise_not(bin2, bin2)
    return bin2


def preprocess_v2_denoise(image):
    """Non-local means denoising + adaptive threshold"""
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    # Denoise
    denoised = cv.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)
    # Adaptive threshold
    binary = cv.adaptiveThreshold(
        denoised, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv.THRESH_BINARY_INV, 11, 2
    )
    # Remove small noise
    cleaned = remove_noise_islands(binary, min_size=30)
    cv.bitwise_not(cleaned, cleaned)
    return cleaned


def preprocess_v3_islands(image):
    """Focus on islands removal"""
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    # Median blur first
    blurred = cv.medianBlur(gray, 3)
    # Binary threshold
    ret, binary = cv.threshold(blurred, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)
    # Remove islands
    cleaned = remove_noise_islands(binary, min_size=40)
    # Second median blur
    cleaned = cv.medianBlur(cleaned, 3)
    cv.bitwise_not(cleaned, cleaned)
    return cleaned


def preprocess_v4_resize(image):
    """Resize + denoise (larger image = better OCR)"""
    # Resize 2x
    h, w = image.shape[:2]
    resized = cv.resize(image, (w * 2, h * 2), interpolation=cv.INTER_CUBIC)

    gray = cv.cvtColor(resized, cv.COLOR_BGR2GRAY)
    # Gaussian blur
    blurred = cv.GaussianBlur(gray, (3, 3), 0)
    # Otsu threshold
    ret, binary = cv.threshold(blurred, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)
    # Morphological close
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (3, 3))
    closed = cv.morphologyEx(binary, cv.MORPH_CLOSE, kernel)
    # Remove noise
    cleaned = remove_noise_islands(closed, min_size=80)
    cv.bitwise_not(cleaned, cleaned)
    return cleaned


def preprocess_v5_combined(image):
    """Combined best techniques"""
    # Resize 2x
    h, w = image.shape[:2]
    resized = cv.resize(image, (w * 2, h * 2), interpolation=cv.INTER_CUBIC)

    gray = cv.cvtColor(resized, cv.COLOR_BGR2GRAY)

    # Denoise
    denoised = cv.fastNlMeansDenoising(gray, None, h=8, templateWindowSize=7, searchWindowSize=21)

    # Median blur
    blurred = cv.medianBlur(denoised, 3)

    # Otsu threshold
    ret, binary = cv.threshold(blurred, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)

    # Morphological operations
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (2, 2))
    opened = cv.morphologyEx(binary, cv.MORPH_OPEN, kernel)

    # Remove islands
    cleaned = remove_noise_islands(opened, min_size=60)

    cv.bitwise_not(cleaned, cleaned)
    return cleaned


def preprocess_v6_simple(image):
    """Simple: grayscale + high threshold + resize"""
    # Resize 3x
    h, w = image.shape[:2]
    resized = cv.resize(image, (w * 3, h * 3), interpolation=cv.INTER_CUBIC)

    gray = cv.cvtColor(resized, cv.COLOR_BGR2GRAY)

    # High threshold to keep only dark pixels
    ret, binary = cv.threshold(gray, 180, 255, cv.THRESH_BINARY)

    return binary


def remove_noise_multidim(binary_img, min_area=30, min_width=3, min_height=8,
                          max_width=50, max_height=50, aspect_ratio_range=(0.1, 3.0)):
    """
    Multi-dimensional filtering (PyImageSearch style)
    Filter by: area, width, height, aspect ratio

    Specialization: Better for structured noise (lines, dots with specific shapes)

    Args:
        binary_img: Binary image (white text on black background)
        min_area: Minimum pixel area
        min_width/max_width: Width bounds
        min_height/max_height: Height bounds
        aspect_ratio_range: (min, max) width/height ratio

    Returns:
        Cleaned binary image
    """
    num_labels, labels, stats, centroids = cv.connectedComponentsWithStats(
        binary_img, connectivity=8
    )

    output = np.zeros_like(binary_img)

    for i in range(1, num_labels):
        area = stats[i, cv.CC_STAT_AREA]
        w = stats[i, cv.CC_STAT_WIDTH]
        h = stats[i, cv.CC_STAT_HEIGHT]

        # Avoid division by zero
        aspect_ratio = w / h if h > 0 else 0

        # Multi-dimensional filtering
        keep_area = area >= min_area
        keep_width = min_width <= w <= max_width
        keep_height = min_height <= h <= max_height
        keep_aspect = aspect_ratio_range[0] <= aspect_ratio <= aspect_ratio_range[1]

        if all([keep_area, keep_width, keep_height, keep_aspect]):
            output[labels == i] = 255

    return output


def preprocess_v7_multidim(image):
    """
    Multi-dimensional filtering (PyImageSearch style)

    Technique: Filter connected components by multiple criteria
    - Area (pixel count)
    - Width/Height bounds
    - Aspect ratio

    Best for: Noise with specific geometric properties
    - Long thin lines (filtered by aspect ratio)
    - Small dots (filtered by area)
    - Large blobs (filtered by max dimensions)
    """
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    # Median blur
    blurred = cv.medianBlur(gray, 3)

    # Otsu threshold
    ret, binary = cv.threshold(blurred, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)

    # Multi-dimensional filtering
    # Parameters tuned for 4-digit CAPTCHA (digits are typically 10-30px wide, 15-40px tall)
    cleaned = remove_noise_multidim(
        binary,
        min_area=25,           # Remove tiny dots
        min_width=3,           # Minimum digit width
        min_height=8,          # Minimum digit height
        max_width=60,          # Maximum (avoid huge noise blobs)
        max_height=50,         # Maximum height
        aspect_ratio_range=(0.15, 2.5)  # Filter very thin lines or very wide shapes
    )

    # Light morphological cleanup
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (2, 2))
    cleaned = cv.morphologyEx(cleaned, cv.MORPH_CLOSE, kernel)

    cv.bitwise_not(cleaned, cleaned)
    return cleaned


def preprocess_v8_twostage(image):
    """
    Two-stage denoising (kingsman142 style)

    Technique: Erosion first to weaken noise, then connected components
    - Stage 1: Morphological erosion weakens small noise
    - Stage 2: Connected components removes remaining islands
    - Stage 3: Dilation to restore character thickness

    Best for: Dense noise that connects to characters
    - Noise touching digits
    - Overlapping artifacts
    """
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    # Initial blur
    blurred = cv.medianBlur(gray, 3)

    # Otsu threshold
    ret, binary = cv.threshold(blurred, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)

    # === Stage 1: Erosion to weaken noise ===
    # Small kernel erodes thin connections between noise and characters
    kernel_erode = cv.getStructuringElement(cv.MORPH_RECT, (2, 2))
    eroded = cv.erode(binary, kernel_erode, iterations=1)

    # === Stage 2: Connected components cleanup ===
    # After erosion, small noise becomes disconnected and can be removed
    cleaned = remove_noise_islands(eroded, min_size=25)

    # === Stage 3: Dilation to restore character thickness ===
    kernel_dilate = cv.getStructuringElement(cv.MORPH_RECT, (2, 2))
    restored = cv.dilate(cleaned, kernel_dilate, iterations=1)

    # Final median blur
    restored = cv.medianBlur(restored, 3)

    cv.bitwise_not(restored, restored)
    return restored


def preprocess_v9_hybrid(image):
    """
    Hybrid: Combines v3_islands + v7_multidim + v8_twostage

    Technique: Apply multiple strategies in sequence
    - Erosion first (from v8)
    - Multi-dimensional filtering (from v7)
    - Final cleanup

    Best for: Complex CAPTCHA with multiple noise types
    """
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    # Median blur
    blurred = cv.medianBlur(gray, 3)

    # Otsu threshold
    ret, binary = cv.threshold(blurred, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)

    # Stage 1: Light erosion
    kernel_erode = cv.getStructuringElement(cv.MORPH_ELLIPSE, (2, 2))
    eroded = cv.erode(binary, kernel_erode, iterations=1)

    # Stage 2: Multi-dimensional filtering
    cleaned = remove_noise_multidim(
        eroded,
        min_area=20,
        min_width=2,
        min_height=6,
        max_width=70,
        max_height=60,
        aspect_ratio_range=(0.1, 3.0)
    )

    # Stage 3: Restore with dilation
    kernel_dilate = cv.getStructuringElement(cv.MORPH_RECT, (2, 2))
    restored = cv.dilate(cleaned, kernel_dilate, iterations=1)

    # Stage 4: Final area-based cleanup
    final = remove_noise_islands(restored, min_size=30)

    cv.bitwise_not(final, final)
    return final


PREPROCESS_METHODS = {
    'v1_original': preprocess_v1_original,
    'v2_denoise': preprocess_v2_denoise,
    'v3_islands': preprocess_v3_islands,
    'v4_resize': preprocess_v4_resize,
    'v5_combined': preprocess_v5_combined,
    'v6_simple': preprocess_v6_simple,
    'v7_multidim': preprocess_v7_multidim,
    'v8_twostage': preprocess_v8_twostage,
    'v9_hybrid': preprocess_v9_hybrid,
}


def recognize_with_method(image_path: str, method: str = 'v5_combined') -> tuple:
    """
    Recognize CAPTCHA with specified preprocessing method

    Returns:
        (success, result, confidence)
    """
    try:
        image = cv.imread(image_path)
        if image is None:
            return False, "", "error"

        # Apply preprocessing
        preprocess_func = PREPROCESS_METHODS.get(method, preprocess_v5_combined)
        processed = preprocess_func(image)

        # Convert to PIL
        pil_img = Image.fromarray(processed)

        # OCR with digit whitelist
        config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789'
        raw_text = pytesseract.image_to_string(pil_img, config=config)

        # Extract digits
        text = raw_text.strip()
        digits = re.findall(r'\d+', text)
        result = ''.join(digits) if digits else text

        # Validate
        if len(result) == 4 and result.isdigit():
            return True, result, "high"
        elif len(result) >= 3 and result.isdigit():
            return True, result, "medium"
        else:
            return False, result, "low"

    except Exception as e:
        return False, str(e), "error"


def compare_methods(image_path: str, debug: bool = False):
    """Compare all preprocessing methods on a single image"""
    print(f"\nComparing methods on: {os.path.basename(image_path)}")
    print("-" * 50)

    image = cv.imread(image_path)
    if image is None:
        print("[ERROR] Cannot read image")
        return

    results = {}
    for name, func in PREPROCESS_METHODS.items():
        success, result, confidence = recognize_with_method(image_path, name)
        results[name] = {'result': result, 'success': success, 'confidence': confidence}

        status = "[OK]" if success else "[FAIL]"
        print(f"  {name:15} {status} -> {result:6} ({confidence})")

        # Save debug images
        if debug:
            processed = func(image)
            debug_path = image_path.replace('.png', f'_{name}.png')
            cv.imwrite(debug_path, processed)

    return results


def batch_test_method(method: str, samples_dir: str, limit: int = 100):
    """Test a specific method on multiple samples"""
    import glob

    samples = sorted(glob.glob(os.path.join(samples_dir, "captcha_*.png")))[:limit]

    print(f"\n{'='*60}")
    print(f"Testing method: {method}")
    print(f"Samples: {len(samples)}")
    print(f"{'='*60}\n")

    success_count = 0
    high_conf = 0

    for i, sample in enumerate(samples):
        success, result, confidence = recognize_with_method(sample, method)
        if success:
            success_count += 1
            if confidence == 'high':
                high_conf += 1

        if (i + 1) % 20 == 0:
            print(f"Progress: {i+1}/{len(samples)} - Success: {success_count}")

    rate = success_count / len(samples) * 100
    high_rate = high_conf / len(samples) * 100

    print(f"\n{'-'*60}")
    print(f"Method: {method}")
    print(f"Total: {len(samples)}")
    print(f"Successful: {success_count} ({rate:.1f}%)")
    print(f"High confidence: {high_conf} ({high_rate:.1f}%)")

    return {'method': method, 'total': len(samples), 'success': success_count, 'rate': rate}


def compare_all_methods(samples_dir: str, limit: int = 100):
    """Compare all methods on the same sample set"""
    results = []

    for method in PREPROCESS_METHODS.keys():
        r = batch_test_method(method, samples_dir, limit)
        results.append(r)

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY - All Methods Comparison")
    print(f"{'='*60}")
    print(f"{'Method':<15} {'Success':<10} {'Rate':<10}")
    print(f"{'-'*60}")

    for r in sorted(results, key=lambda x: x['rate'], reverse=True):
        print(f"{r['method']:<15} {r['success']:<10} {r['rate']:.1f}%")

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Improved CAPTCHA OCR')
    parser.add_argument('action', nargs='?', default='compare',
                       choices=['compare', 'test', 'single', 'debug'],
                       help='Action to perform')
    parser.add_argument('-m', '--method', default='v5_combined',
                       choices=list(PREPROCESS_METHODS.keys()),
                       help='Preprocessing method')
    parser.add_argument('-n', '--limit', type=int, default=100,
                       help='Number of samples to test')
    parser.add_argument('-f', '--file', type=str,
                       help='Single file to test')

    args = parser.parse_args()

    SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')

    if args.action == 'compare':
        compare_all_methods(SAMPLES_DIR, args.limit)

    elif args.action == 'test':
        batch_test_method(args.method, SAMPLES_DIR, args.limit)

    elif args.action == 'single' and args.file:
        compare_methods(args.file, debug=True)

    elif args.action == 'debug':
        # Test on first sample with debug output
        import glob
        samples = sorted(glob.glob(os.path.join(SAMPLES_DIR, "captcha_*.png")))
        if samples:
            compare_methods(samples[0], debug=True)
