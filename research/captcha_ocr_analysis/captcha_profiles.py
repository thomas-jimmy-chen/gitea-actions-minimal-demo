#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
CAPTCHA Preprocessing Profiles

Predefined parameter profiles for different CAPTCHA types.
Each profile is optimized for specific noise patterns.

Usage:
    from captcha_profiles import preprocess_with_profile, PROFILES

    # List available profiles
    print(PROFILES.keys())

    # Use a specific profile
    result = preprocess_with_profile(image, 'tronclass')
    result = preprocess_with_profile(image, 'line_noise')
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


# =============================================================================
# PROFILE DEFINITIONS
# =============================================================================

PROFILES = {
    # -------------------------------------------------------------------------
    # TronClass (郵政 elearn) - 目前使用的 CAPTCHA
    # -------------------------------------------------------------------------
    'tronclass': {
        'description': 'TronClass LMS (elearn.post.gov.tw) - Random dot noise',
        'method': 'islands',
        'params': {
            'min_size': 40,
            'blur_before': 3,
            'blur_after': 3,
        }
    },

    'tronclass_strict': {
        'description': 'TronClass - Stricter filtering for cleaner images',
        'method': 'islands',
        'params': {
            'min_size': 50,
            'blur_before': 3,
            'blur_after': 0,
        }
    },

    # -------------------------------------------------------------------------
    # Line Noise Profiles (v7_multidim based)
    # -------------------------------------------------------------------------
    'line_noise': {
        'description': 'CAPTCHA with thin line noise (scratches, stripes)',
        'method': 'multidim',
        'params': {
            'min_area': 30,
            'min_width': 4,
            'min_height': 10,
            'max_width': 50,
            'max_height': 45,
            'aspect_ratio_range': (0.2, 2.0),  # Filter very thin lines
            'morph_close': True,
        }
    },

    'heavy_line_noise': {
        'description': 'CAPTCHA with heavy line/scratch noise',
        'method': 'multidim',
        'params': {
            'min_area': 40,
            'min_width': 5,
            'min_height': 12,
            'max_width': 45,
            'max_height': 40,
            'aspect_ratio_range': (0.25, 1.8),  # Even stricter on thin shapes
            'morph_close': True,
        }
    },

    # -------------------------------------------------------------------------
    # Connected Noise Profiles (v8_twostage based)
    # -------------------------------------------------------------------------
    'connected_noise': {
        'description': 'CAPTCHA with noise touching/connected to digits',
        'method': 'twostage',
        'params': {
            'erosion_kernel': (2, 2),
            'erosion_iterations': 1,
            'min_size': 25,
            'dilation_kernel': (2, 2),
            'dilation_iterations': 1,
        }
    },

    'heavy_connected_noise': {
        'description': 'CAPTCHA with heavy connected noise',
        'method': 'twostage',
        'params': {
            'erosion_kernel': (3, 3),
            'erosion_iterations': 2,
            'min_size': 30,
            'dilation_kernel': (3, 3),
            'dilation_iterations': 2,
        }
    },

    'light_connected_noise': {
        'description': 'CAPTCHA with light connected noise',
        'method': 'twostage',
        'params': {
            'erosion_kernel': (2, 2),
            'erosion_iterations': 1,
            'min_size': 20,
            'dilation_kernel': (2, 2),
            'dilation_iterations': 1,
        }
    },

    # -------------------------------------------------------------------------
    # Hybrid Profiles (combining techniques)
    # -------------------------------------------------------------------------
    'hybrid_standard': {
        'description': 'Standard hybrid: erosion + multidim + islands',
        'method': 'hybrid',
        'params': {
            'erosion_kernel': (2, 2),
            'erosion_iterations': 1,
            'min_area': 20,
            'min_width': 2,
            'min_height': 6,
            'max_width': 70,
            'max_height': 60,
            'aspect_ratio_range': (0.1, 3.0),
            'final_min_size': 30,
        }
    },

    'hybrid_aggressive': {
        'description': 'Aggressive hybrid for complex noise',
        'method': 'hybrid',
        'params': {
            'erosion_kernel': (3, 3),
            'erosion_iterations': 1,
            'min_area': 35,
            'min_width': 4,
            'min_height': 8,
            'max_width': 55,
            'max_height': 50,
            'aspect_ratio_range': (0.15, 2.5),
            'final_min_size': 40,
        }
    },

    # -------------------------------------------------------------------------
    # Special Profiles
    # -------------------------------------------------------------------------
    'digits_only': {
        'description': 'Optimized for digit-only CAPTCHA (0-9)',
        'method': 'islands',
        'params': {
            'min_size': 35,
            'blur_before': 3,
            'blur_after': 3,
            'resize_factor': 2,  # Resize 2x before processing
        }
    },

    'alphanumeric': {
        'description': 'Optimized for alphanumeric CAPTCHA (A-Z, 0-9)',
        'method': 'multidim',
        'params': {
            'min_area': 20,
            'min_width': 3,
            'min_height': 8,
            'max_width': 60,
            'max_height': 55,
            'aspect_ratio_range': (0.12, 3.0),  # Letters can be taller
            'morph_close': True,
        }
    },
}


# =============================================================================
# CORE PREPROCESSING FUNCTIONS
# =============================================================================

def remove_noise_by_area(binary_img, min_size=50):
    """Remove small noise islands by area"""
    num_labels, labels, stats, _ = cv.connectedComponentsWithStats(
        binary_img, connectivity=8
    )
    output = np.zeros_like(binary_img)
    for i in range(1, num_labels):
        if stats[i, cv.CC_STAT_AREA] >= min_size:
            output[labels == i] = 255
    return output


def remove_noise_multidim(binary_img, min_area=30, min_width=3, min_height=8,
                          max_width=50, max_height=50, aspect_ratio_range=(0.1, 3.0)):
    """Multi-dimensional filtering by area, width, height, aspect ratio"""
    num_labels, labels, stats, _ = cv.connectedComponentsWithStats(
        binary_img, connectivity=8
    )
    output = np.zeros_like(binary_img)

    for i in range(1, num_labels):
        area = stats[i, cv.CC_STAT_AREA]
        w = stats[i, cv.CC_STAT_WIDTH]
        h = stats[i, cv.CC_STAT_HEIGHT]
        aspect = w / h if h > 0 else 0

        if (area >= min_area and
            min_width <= w <= max_width and
            min_height <= h <= max_height and
            aspect_ratio_range[0] <= aspect <= aspect_ratio_range[1]):
            output[labels == i] = 255

    return output


def preprocess_islands(image, params):
    """Islands removal method (v3_islands based)"""
    # Optional resize
    if params.get('resize_factor', 1) > 1:
        h, w = image.shape[:2]
        factor = params['resize_factor']
        image = cv.resize(image, (w * factor, h * factor), interpolation=cv.INTER_CUBIC)

    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    # Blur before threshold
    blur_before = params.get('blur_before', 3)
    if blur_before > 0:
        gray = cv.medianBlur(gray, blur_before)

    # Otsu threshold
    _, binary = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)

    # Remove islands by area
    cleaned = remove_noise_by_area(binary, params.get('min_size', 40))

    # Blur after
    blur_after = params.get('blur_after', 3)
    if blur_after > 0:
        cleaned = cv.medianBlur(cleaned, blur_after)

    cv.bitwise_not(cleaned, cleaned)
    return cleaned


def preprocess_multidim(image, params):
    """Multi-dimensional filtering method (v7_multidim based)"""
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    blurred = cv.medianBlur(gray, 3)
    _, binary = cv.threshold(blurred, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)

    cleaned = remove_noise_multidim(
        binary,
        min_area=params.get('min_area', 25),
        min_width=params.get('min_width', 3),
        min_height=params.get('min_height', 8),
        max_width=params.get('max_width', 60),
        max_height=params.get('max_height', 50),
        aspect_ratio_range=params.get('aspect_ratio_range', (0.15, 2.5)),
    )

    if params.get('morph_close', False):
        kernel = cv.getStructuringElement(cv.MORPH_RECT, (2, 2))
        cleaned = cv.morphologyEx(cleaned, cv.MORPH_CLOSE, kernel)

    cv.bitwise_not(cleaned, cleaned)
    return cleaned


def preprocess_twostage(image, params):
    """Two-stage denoising method (v8_twostage based)"""
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    blurred = cv.medianBlur(gray, 3)
    _, binary = cv.threshold(blurred, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)

    # Stage 1: Erosion
    kernel_size = params.get('erosion_kernel', (2, 2))
    kernel = cv.getStructuringElement(cv.MORPH_RECT, kernel_size)
    eroded = cv.erode(binary, kernel, iterations=params.get('erosion_iterations', 1))

    # Stage 2: Connected components
    cleaned = remove_noise_by_area(eroded, params.get('min_size', 25))

    # Stage 3: Dilation to restore
    kernel_size = params.get('dilation_kernel', (2, 2))
    kernel = cv.getStructuringElement(cv.MORPH_RECT, kernel_size)
    restored = cv.dilate(cleaned, kernel, iterations=params.get('dilation_iterations', 1))

    restored = cv.medianBlur(restored, 3)
    cv.bitwise_not(restored, restored)
    return restored


def preprocess_hybrid(image, params):
    """Hybrid method combining multiple techniques"""
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    blurred = cv.medianBlur(gray, 3)
    _, binary = cv.threshold(blurred, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)

    # Stage 1: Erosion
    kernel_size = params.get('erosion_kernel', (2, 2))
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, kernel_size)
    eroded = cv.erode(binary, kernel, iterations=params.get('erosion_iterations', 1))

    # Stage 2: Multi-dimensional filtering
    cleaned = remove_noise_multidim(
        eroded,
        min_area=params.get('min_area', 20),
        min_width=params.get('min_width', 2),
        min_height=params.get('min_height', 6),
        max_width=params.get('max_width', 70),
        max_height=params.get('max_height', 60),
        aspect_ratio_range=params.get('aspect_ratio_range', (0.1, 3.0)),
    )

    # Stage 3: Dilation
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (2, 2))
    restored = cv.dilate(cleaned, kernel, iterations=1)

    # Stage 4: Final area cleanup
    final = remove_noise_by_area(restored, params.get('final_min_size', 30))

    cv.bitwise_not(final, final)
    return final


# Method dispatcher
METHODS = {
    'islands': preprocess_islands,
    'multidim': preprocess_multidim,
    'twostage': preprocess_twostage,
    'hybrid': preprocess_hybrid,
}


# =============================================================================
# PUBLIC API
# =============================================================================

def preprocess_with_profile(image, profile_name='tronclass'):
    """
    Preprocess image using a named profile

    Args:
        image: OpenCV image (BGR format)
        profile_name: Name of the profile to use

    Returns:
        Preprocessed binary image (white background, black text)
    """
    if profile_name not in PROFILES:
        raise ValueError(f"Unknown profile: {profile_name}. Available: {list(PROFILES.keys())}")

    profile = PROFILES[profile_name]
    method = profile['method']
    params = profile['params']

    preprocess_func = METHODS.get(method)
    if not preprocess_func:
        raise ValueError(f"Unknown method: {method}")

    return preprocess_func(image, params)


def recognize_with_profile(image_path, profile_name='tronclass', char_whitelist='0123456789'):
    """
    Recognize CAPTCHA using a named profile

    Args:
        image_path: Path to CAPTCHA image
        profile_name: Name of the profile to use
        char_whitelist: Characters to recognize (default: digits only)

    Returns:
        (success, result, confidence)
    """
    try:
        image = cv.imread(image_path)
        if image is None:
            return False, "", "error"

        processed = preprocess_with_profile(image, profile_name)
        pil_img = Image.fromarray(processed)

        config = f'--oem 3 --psm 7 -c tessedit_char_whitelist={char_whitelist}'
        raw_text = pytesseract.image_to_string(pil_img, config=config)

        text = raw_text.strip()
        if char_whitelist == '0123456789':
            digits = re.findall(r'\d+', text)
            result = ''.join(digits) if digits else text

            if len(result) == 4 and result.isdigit():
                return True, result, "high"
            elif len(result) >= 3 and result.isdigit():
                return True, result, "medium"
            else:
                return False, result, "low"
        else:
            # Alphanumeric
            result = re.sub(r'[^A-Za-z0-9]', '', text)
            if len(result) >= 3:
                return True, result, "medium"
            else:
                return False, result, "low"

    except Exception as e:
        return False, str(e), "error"


def list_profiles():
    """List all available profiles with descriptions"""
    print("\n" + "=" * 70)
    print("Available CAPTCHA Profiles")
    print("=" * 70)

    for name, profile in PROFILES.items():
        method = profile['method']
        desc = profile['description']
        print(f"\n  [{name}]")
        print(f"    Method: {method}")
        print(f"    Description: {desc}")

    print("\n" + "=" * 70)


def test_all_profiles(image_path):
    """Test all profiles on a single image"""
    print(f"\nTesting all profiles on: {os.path.basename(image_path)}")
    print("-" * 60)

    image = cv.imread(image_path)
    if image is None:
        print("[ERROR] Cannot read image")
        return

    for name in PROFILES.keys():
        success, result, confidence = recognize_with_profile(image_path, name)
        status = "[OK]" if success else "[FAIL]"
        print(f"  {name:20} {status} -> {result:6} ({confidence})")


def batch_test_profile(profile_name, samples_dir, limit=100):
    """Test a specific profile on multiple samples"""
    import glob

    samples = sorted(glob.glob(os.path.join(samples_dir, "captcha_*.png")))[:limit]

    print(f"\n{'='*60}")
    print(f"Testing profile: {profile_name}")
    print(f"Description: {PROFILES[profile_name]['description']}")
    print(f"Samples: {len(samples)}")
    print(f"{'='*60}\n")

    success_count = 0
    for i, sample in enumerate(samples):
        success, result, confidence = recognize_with_profile(sample, profile_name)
        if success:
            success_count += 1

        if (i + 1) % 50 == 0:
            print(f"Progress: {i+1}/{len(samples)} - Success: {success_count}")

    rate = success_count / len(samples) * 100
    print(f"\n{'-'*60}")
    print(f"Profile: {profile_name}")
    print(f"Success rate: {success_count}/{len(samples)} ({rate:.1f}%)")

    return rate


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='CAPTCHA Profile System')
    parser.add_argument('action', nargs='?', default='list',
                       choices=['list', 'test', 'batch', 'compare'],
                       help='Action to perform')
    parser.add_argument('-p', '--profile', default='tronclass',
                       help='Profile name to use')
    parser.add_argument('-f', '--file', type=str,
                       help='Single file to test')
    parser.add_argument('-n', '--limit', type=int, default=100,
                       help='Number of samples for batch test')

    args = parser.parse_args()

    SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')

    if args.action == 'list':
        list_profiles()

    elif args.action == 'test':
        if args.file:
            test_all_profiles(args.file)
        else:
            import glob
            samples = sorted(glob.glob(os.path.join(SAMPLES_DIR, "captcha_*.png")))
            if samples:
                test_all_profiles(samples[0])

    elif args.action == 'batch':
        batch_test_profile(args.profile, SAMPLES_DIR, args.limit)

    elif args.action == 'compare':
        print("\n" + "=" * 70)
        print("Comparing Key Profiles")
        print("=" * 70)

        key_profiles = ['tronclass', 'line_noise', 'connected_noise', 'hybrid_standard']
        results = []

        for profile in key_profiles:
            rate = batch_test_profile(profile, SAMPLES_DIR, args.limit)
            results.append((profile, rate))

        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        for profile, rate in sorted(results, key=lambda x: x[1], reverse=True):
            print(f"  {profile:20} {rate:.1f}%")
