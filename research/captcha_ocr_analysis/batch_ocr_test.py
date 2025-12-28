#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Batch OCR Test

Run OCR on all collected CAPTCHA samples and analyze results.
"""

import os
import sys
import json
import glob
from datetime import datetime

# Import OCR function
from test_eebot_captcha import recognize_captcha, TESSERACT_AVAILABLE

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')
RESULTS_FILE = os.path.join(os.path.dirname(__file__), 'ocr_results.json')


def run_batch_ocr():
    """Run OCR on all samples and save results"""
    if not TESSERACT_AVAILABLE:
        print("[ERROR] Tesseract not available")
        return None

    samples = sorted(glob.glob(os.path.join(SAMPLES_DIR, "*.png")))

    if not samples:
        print("[ERROR] No samples found")
        return None

    print(f"\n{'='*60}")
    print(f"Batch OCR Test")
    print(f"{'='*60}")
    print(f"Samples: {len(samples)}")
    print(f"{'='*60}\n")

    results = []
    success_count = 0
    digit_counts = {str(i): 0 for i in range(10)}

    for i, sample_path in enumerate(samples):
        filename = os.path.basename(sample_path)
        success, text, confidence = recognize_captcha(sample_path)

        results.append({
            'file': filename,
            'result': text,
            'success': success,
            'confidence': confidence
        })

        if success:
            success_count += 1
            # Count digit frequency
            for char in text:
                if char.isdigit():
                    digit_counts[char] += 1

        # Progress
        if (i + 1) % 50 == 0:
            print(f"Progress: {i+1}/{len(samples)} ({success_count} successful)")

    # Save results
    output = {
        'timestamp': datetime.now().isoformat(),
        'total_samples': len(samples),
        'successful_recognitions': success_count,
        'recognition_rate': round(success_count / len(samples) * 100, 2),
        'digit_frequency': digit_counts,
        'results': results
    }

    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"Results saved to: {RESULTS_FILE}")

    return output


def analyze_results():
    """Analyze saved results"""
    if not os.path.exists(RESULTS_FILE):
        print("[ERROR] No results file. Run batch OCR first.")
        return

    with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"\n{'='*60}")
    print(f"OCR Results Analysis")
    print(f"{'='*60}")
    print(f"Test Time: {data['timestamp']}")
    print(f"Total Samples: {data['total_samples']}")
    print(f"Successful Recognitions: {data['successful_recognitions']}")
    print(f"Recognition Rate: {data['recognition_rate']}%")

    print(f"\n{'-'*60}")
    print("Confidence Distribution:")
    confidence_counts = {'high': 0, 'medium': 0, 'low': 0, 'error': 0}
    for r in data['results']:
        conf = r.get('confidence', 'unknown')
        if conf in confidence_counts:
            confidence_counts[conf] += 1

    for conf, count in confidence_counts.items():
        pct = count / data['total_samples'] * 100
        print(f"  {conf}: {count} ({pct:.1f}%)")

    print(f"\n{'-'*60}")
    print("Digit Frequency:")
    for digit, count in sorted(data['digit_frequency'].items()):
        print(f"  {digit}: {count}")

    # Show some sample results
    print(f"\n{'-'*60}")
    print("Sample Results (first 20):")
    for r in data['results'][:20]:
        status = "[OK]" if r['success'] else "[FAIL]"
        print(f"  {status} {r['file']}: {r['result']} ({r['confidence']})")

    # Show failed cases
    failed = [r for r in data['results'] if not r['success']]
    print(f"\n{'-'*60}")
    print(f"Failed Cases: {len(failed)}")
    if failed[:10]:
        print("Sample failures:")
        for r in failed[:10]:
            print(f"  {r['file']}: '{r['result']}' ({r['confidence']})")


def spot_check(n: int = 20):
    """Interactive spot check to verify OCR accuracy"""
    if not os.path.exists(RESULTS_FILE):
        print("[ERROR] No results file. Run batch OCR first.")
        return

    with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Select random samples for spot check
    import random
    successful = [r for r in data['results'] if r['success']]
    samples = random.sample(successful, min(n, len(successful)))

    print(f"\n{'='*60}")
    print(f"Spot Check Mode")
    print(f"{'='*60}")
    print(f"Checking {len(samples)} random samples")
    print("Enter 'y' if correct, 'n' if wrong, 'q' to quit")
    print(f"{'='*60}\n")

    correct = 0
    checked = 0

    for sample in samples:
        filepath = os.path.join(SAMPLES_DIR, sample['file'])
        if not os.path.exists(filepath):
            continue

        print(f"\nFile: {sample['file']}")
        print(f"OCR Result: {sample['result']}")
        print(f"Image path: {filepath}")

        user_input = input("Correct? (y/n/q): ").strip().lower()

        if user_input == 'q':
            break
        elif user_input == 'y':
            correct += 1
            checked += 1
        elif user_input == 'n':
            checked += 1
            actual = input("Enter actual value: ").strip()
            print(f"  Noted: OCR={sample['result']}, Actual={actual}")

    if checked > 0:
        accuracy = correct / checked * 100
        print(f"\n{'='*60}")
        print(f"Spot Check Results")
        print(f"{'='*60}")
        print(f"Checked: {checked}")
        print(f"Correct: {correct}")
        print(f"Estimated Accuracy: {accuracy:.1f}%")
        print(f"{'='*60}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Batch OCR Test')
    parser.add_argument('action', nargs='?', default='run',
                       choices=['run', 'analyze', 'check'],
                       help='Action: run, analyze, or check')
    parser.add_argument('-n', '--count', type=int, default=20,
                       help='Number of samples for spot check')

    args = parser.parse_args()

    if args.action == 'run':
        results = run_batch_ocr()
        if results:
            analyze_results()

    elif args.action == 'analyze':
        analyze_results()

    elif args.action == 'check':
        spot_check(args.count)
