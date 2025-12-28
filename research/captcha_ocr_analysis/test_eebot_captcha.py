#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
EEBot CAPTCHA OCR Test Script

Test Auto-WFH OCR method on TronClass CAPTCHA
"""

import os
import sys
import cv2 as cv
from PIL import Image
import re

# Try importing pytesseract
try:
    import pytesseract
    # Windows paths (including conda)
    if os.name == 'nt':
        tesseract_paths = [
            'C:/Program Files/Tesseract-OCR/tesseract.exe',
            'C:/Program Files (x86)/Tesseract-OCR/tesseract.exe',
            os.path.expanduser('~/AppData/Local/Programs/Tesseract-OCR/tesseract.exe'),
            # Conda install paths
            'C:/Users/user123456/miniconda3/envs/eebot/Library/bin/tesseract.exe',
            os.path.expanduser('~/miniconda3/envs/eebot/Library/bin/tesseract.exe'),
            os.path.expanduser('~/anaconda3/envs/eebot/Library/bin/tesseract.exe'),
        ]
        for path in tesseract_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                print(f"[INFO] Tesseract found at: {path}")
                break
        else:
            print("[WARN] Tesseract not found in default paths")
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("[ERROR] pytesseract not installed")


def preprocess_captcha(image_path: str, debug: bool = False):
    """
    Preprocess CAPTCHA image

    Args:
        image_path: Image path
        debug: Save intermediate results

    Returns:
        Processed image (PIL Image)
    """
    # Read image
    image = cv.imread(image_path)
    if image is None:
        raise ValueError(f"Cannot read image: {image_path}")

    # 1. Edge-preserving filter, denoise
    blur = cv.pyrMeanShiftFiltering(image, sp=8, sr=60)
    if debug:
        cv.imwrite(image_path.replace('.png', '_1_blur.png'), blur)

    # 2. Grayscale
    gray = cv.cvtColor(blur, cv.COLOR_BGR2GRAY)
    if debug:
        cv.imwrite(image_path.replace('.png', '_2_gray.png'), gray)

    # 3. Binarization (Otsu's method)
    ret, binary = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)
    if debug:
        cv.imwrite(image_path.replace('.png', '_3_binary.png'), binary)

    # 4. Morphological operations - opening to remove noise
    kernel1 = cv.getStructuringElement(cv.MORPH_RECT, (3, 2))
    bin1 = cv.morphologyEx(binary, cv.MORPH_OPEN, kernel1)

    kernel2 = cv.getStructuringElement(cv.MORPH_RECT, (2, 3))
    bin2 = cv.morphologyEx(bin1, cv.MORPH_OPEN, kernel2)
    if debug:
        cv.imwrite(image_path.replace('.png', '_4_morph.png'), bin2)

    # 5. Invert to white background black text (easier to recognize)
    cv.bitwise_not(bin2, bin2)
    if debug:
        cv.imwrite(image_path.replace('.png', '_5_final.png'), bin2)

    return Image.fromarray(bin2)


def recognize_captcha(image_path: str, debug: bool = False) -> tuple:
    """
    Recognize CAPTCHA

    Args:
        image_path: Image path
        debug: Output debug info

    Returns:
        (success: bool, text: str, confidence: str)
    """
    if not TESSERACT_AVAILABLE:
        return False, "", "Tesseract not available"

    try:
        # Preprocess
        processed_img = preprocess_captcha(image_path, debug=debug)

        # OCR recognition
        # Use digit whitelist to improve accuracy
        custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789'
        raw_text = pytesseract.image_to_string(processed_img, config=custom_config)

        # Extract digits
        text = raw_text.strip()
        digits = re.findall(r'\d+', text)
        result = ''.join(digits) if digits else text

        # Validate result
        if len(result) == 4 and result.isdigit():
            return True, result, "high"
        elif len(result) >= 3 and result.isdigit():
            return True, result, "medium"
        else:
            return False, result, "low"

    except Exception as e:
        return False, str(e), "error"


def test_single_captcha(image_path: str, expected: str = None, debug: bool = False):
    """
    Test single CAPTCHA
    """
    print(f"\n{'='*50}")
    print(f"Testing: {image_path}")

    success, result, confidence = recognize_captcha(image_path, debug=debug)

    print(f"Result: {result}")
    print(f"Success: {success}")
    print(f"Confidence: {confidence}")

    if expected:
        match = (result == expected)
        print(f"Expected: {expected}")
        print(f"Match: {'[OK]' if match else '[FAIL]'}")
        return match

    return success


def run_accuracy_test(test_dir: str, expected_values: dict = None):
    """
    Run accuracy test

    Args:
        test_dir: Test images directory
        expected_values: {filename: expected_value} dict
    """
    import glob

    image_files = glob.glob(os.path.join(test_dir, "*.png"))

    if not image_files:
        print(f"[WARN] No PNG files found in {test_dir}")
        return

    total = len(image_files)
    success_count = 0
    match_count = 0
    results = []

    for img_path in image_files:
        filename = os.path.basename(img_path)
        expected = expected_values.get(filename) if expected_values else None

        success, result, confidence = recognize_captcha(img_path)

        if success:
            success_count += 1

        if expected and result == expected:
            match_count += 1

        results.append({
            'file': filename,
            'result': result,
            'expected': expected,
            'success': success,
            'match': (result == expected) if expected else None,
            'confidence': confidence
        })

    # Output results
    print("\n" + "="*60)
    print("CAPTCHA OCR Recognition Test Report")
    print("="*60)

    for r in results:
        status = "[OK]" if r['success'] else "[FAIL]"
        match_status = ""
        if r['expected']:
            match_status = f" | Match: {'[OK]' if r['match'] else '[FAIL]'}"
        print(f"{status} {r['file']}: {r['result']} (conf: {r['confidence']}){match_status}")

    print("\n" + "-"*60)
    print(f"Total tests: {total}")
    print(f"Successful recognitions: {success_count}")
    print(f"Recognition rate: {success_count/total*100:.1f}%")

    if expected_values:
        print(f"Exact matches: {match_count}")
        print(f"Accuracy: {match_count/total*100:.1f}%")

    return {
        'total': total,
        'success': success_count,
        'recognition_rate': success_count/total*100,
        'match': match_count if expected_values else None,
        'accuracy': match_count/total*100 if expected_values else None
    }


def check_dependencies():
    """Check dependencies"""
    print("="*50)
    print("Dependency Check")
    print("="*50)

    deps = {
        'cv2 (opencv-python)': False,
        'PIL (Pillow)': False,
        'pytesseract': False,
        'Tesseract OCR Engine': False,
    }

    try:
        import cv2
        deps['cv2 (opencv-python)'] = True
        print(f"[OK] OpenCV: {cv2.__version__}")
    except ImportError:
        print("[FAIL] OpenCV: NOT INSTALLED")

    try:
        from PIL import Image
        import PIL
        deps['PIL (Pillow)'] = True
        print(f"[OK] Pillow: {PIL.__version__}")
    except ImportError:
        print("[FAIL] Pillow: NOT INSTALLED")

    try:
        import pytesseract
        deps['pytesseract'] = True
        print(f"[OK] pytesseract: installed")

        # Check Tesseract engine
        try:
            version = pytesseract.get_tesseract_version()
            deps['Tesseract OCR Engine'] = True
            print(f"[OK] Tesseract OCR: {version}")
        except Exception as e:
            print(f"[FAIL] Tesseract OCR Engine: NOT FOUND ({e})")
    except ImportError:
        print("[FAIL] pytesseract: NOT INSTALLED")

    print("-"*50)
    all_ok = all(deps.values())
    print(f"All dependencies OK: {'[YES]' if all_ok else '[NO]'}")

    if not all_ok:
        print("\nInstall commands:")
        print("pip install opencv-python Pillow pytesseract")
        print("\nTesseract OCR install:")
        print("Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        print("Linux: sudo apt install tesseract-ocr")
        print("Mac: brew install tesseract")

    return all_ok


if __name__ == "__main__":
    # Check dependencies
    if not check_dependencies():
        print("\n[ERROR] Please install missing dependencies first")
        sys.exit(1)

    # Test EEBot captcha.png
    eebot_captcha = "../../captcha.png"

    if os.path.exists(eebot_captcha):
        print("\n" + "="*50)
        print("Testing EEBot captcha.png")
        print("="*50)

        # Show path for user reference
        print(f"\nImage path: {os.path.abspath(eebot_captcha)}")

        # Run recognition test
        test_single_captcha(eebot_captcha, debug=True)
    else:
        print(f"\n[INFO] EEBot captcha.png not found: {eebot_captcha}")

    print("\n" + "="*50)
    print("Test Complete")
    print("="*50)
