#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Auto CAPTCHA Collector

Automatically collect CAPTCHA samples from TronClass login page
for OCR accuracy testing.

This only accesses the public login page - no login required.
"""

import os
import sys
import time
import base64
from datetime import datetime

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Settings
LOGIN_URL = "https://elearn.post.gov.tw/login"
CAPTCHA_XPATH = "//form//img[contains(@src,'captcha')]"
SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')
DEFAULT_SAMPLE_COUNT = 20


def setup_driver():
    """Setup Chrome WebDriver"""
    options = Options()
    options.add_argument('--headless')  # Run in background
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')

    # Disable images except captcha to speed up
    prefs = {
        'profile.managed_default_content_settings.images': 1
    }
    options.add_experimental_option('prefs', prefs)

    driver = webdriver.Chrome(options=options)
    return driver


def save_captcha_image(driver, output_path: str) -> bool:
    """
    Save CAPTCHA image using Canvas method

    Args:
        driver: WebDriver instance
        output_path: Path to save the image

    Returns:
        True if successful
    """
    try:
        # Find CAPTCHA image element
        img_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, CAPTCHA_XPATH))
        )

        # Use Canvas to capture image as base64
        img_base64 = driver.execute_script("""
            let e = arguments[0], c = document.createElement('canvas');
            c.width = e.width; c.height = e.height;
            c.getContext('2d').drawImage(e, 0, 0);
            return c.toDataURL('image/png').split(',')[1];
        """, img_element)

        # Decode and save
        with open(output_path, 'wb') as f:
            f.write(base64.b64decode(img_base64))

        return True

    except Exception as e:
        print(f"[ERROR] Failed to save captcha: {e}")
        return False


def refresh_captcha(driver):
    """Refresh the page to get new CAPTCHA"""
    driver.refresh()
    time.sleep(1)  # Wait for new captcha to load


def collect_samples(count: int = DEFAULT_SAMPLE_COUNT, delay: float = 1.5):
    """
    Collect multiple CAPTCHA samples

    Args:
        count: Number of samples to collect
        delay: Delay between refreshes (seconds)
    """
    # Setup
    if not os.path.exists(SAMPLES_DIR):
        os.makedirs(SAMPLES_DIR)
        print(f"[INFO] Created: {SAMPLES_DIR}")

    print(f"\n{'='*50}")
    print(f"CAPTCHA Sample Collector")
    print(f"{'='*50}")
    print(f"Target: {LOGIN_URL}")
    print(f"Samples to collect: {count}")
    print(f"Output directory: {SAMPLES_DIR}")
    print(f"{'='*50}\n")

    driver = None
    collected = 0

    try:
        print("[INFO] Starting Chrome (headless)...")
        driver = setup_driver()

        print(f"[INFO] Navigating to {LOGIN_URL}...")
        driver.get(LOGIN_URL)
        time.sleep(2)  # Initial load

        for i in range(count):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
            filename = f"captcha_{timestamp}.png"
            filepath = os.path.join(SAMPLES_DIR, filename)

            if save_captcha_image(driver, filepath):
                collected += 1
                print(f"[{collected}/{count}] Saved: {filename}")
            else:
                print(f"[{i+1}/{count}] FAILED")

            # Refresh for next captcha (except last iteration)
            if i < count - 1:
                refresh_captcha(driver)
                time.sleep(delay)

        print(f"\n{'='*50}")
        print(f"Collection Complete!")
        print(f"{'='*50}")
        print(f"Collected: {collected}/{count}")
        print(f"Location: {SAMPLES_DIR}")

    except Exception as e:
        print(f"\n[ERROR] {e}")

    finally:
        if driver:
            driver.quit()
            print("[INFO] Browser closed")

    return collected


def interactive_labeling():
    """Interactive mode to label collected samples"""
    from test_eebot_captcha import recognize_captcha

    if not os.path.exists(SAMPLES_DIR):
        print("[ERROR] No samples directory. Run collection first.")
        return

    samples = [f for f in os.listdir(SAMPLES_DIR)
               if f.endswith('.png') and '_label_' not in f]

    if not samples:
        print("[INFO] No unlabeled samples found")
        return

    print(f"\n{'='*50}")
    print(f"Interactive Labeling Mode")
    print(f"{'='*50}")
    print(f"Unlabeled samples: {len(samples)}")
    print("Enter 's' to skip, 'q' to quit")
    print(f"{'='*50}\n")

    labeled_count = 0

    for sample in sorted(samples):
        filepath = os.path.join(SAMPLES_DIR, sample)

        # Try OCR first
        success, ocr_result, confidence = recognize_captcha(filepath)

        print(f"\nFile: {sample}")
        print(f"OCR Result: {ocr_result} (confidence: {confidence})")
        print(f"Please view: {filepath}")

        user_input = input("Enter correct value (or s=skip, q=quit): ").strip()

        if user_input.lower() == 'q':
            break
        elif user_input.lower() == 's':
            continue
        elif user_input.isdigit() and len(user_input) == 4:
            # Rename with label
            new_name = sample.replace('.png', f'_label_{user_input}.png')
            new_path = os.path.join(SAMPLES_DIR, new_name)
            os.rename(filepath, new_path)

            match = "[OK]" if user_input == ocr_result else "[WRONG]"
            print(f"Labeled: {new_name} {match}")
            labeled_count += 1
        else:
            print("[SKIP] Invalid input (need 4 digits)")

    print(f"\n[INFO] Labeled {labeled_count} samples")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Auto CAPTCHA Collector')
    parser.add_argument('action', nargs='?', default='collect',
                       choices=['collect', 'label', 'test'],
                       help='Action: collect, label, or test')
    parser.add_argument('-n', '--count', type=int, default=DEFAULT_SAMPLE_COUNT,
                       help=f'Number of samples to collect (default: {DEFAULT_SAMPLE_COUNT})')
    parser.add_argument('-d', '--delay', type=float, default=1.5,
                       help='Delay between refreshes in seconds (default: 1.5)')

    args = parser.parse_args()

    if args.action == 'collect':
        collect_samples(count=args.count, delay=args.delay)

    elif args.action == 'label':
        interactive_labeling()

    elif args.action == 'test':
        from test_eebot_captcha import run_accuracy_test
        from collect_samples import get_expected_values

        expected = get_expected_values()
        if expected:
            print(f"\nTesting {len(expected)} labeled samples...")
            run_accuracy_test(SAMPLES_DIR, expected)
        else:
            print("[WARN] No labeled samples. Run 'label' first.")
