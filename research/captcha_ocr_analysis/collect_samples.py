#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
CAPTCHA Sample Collector

Collect multiple CAPTCHA samples for accuracy testing
"""

import os
import sys
import shutil
from datetime import datetime

# Add eebot to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')


def setup_samples_dir():
    """Create samples directory"""
    if not os.path.exists(SAMPLES_DIR):
        os.makedirs(SAMPLES_DIR)
        print(f"[INFO] Created samples directory: {SAMPLES_DIR}")
    return SAMPLES_DIR


def collect_from_eebot():
    """Copy current captcha.png to samples with timestamp"""
    eebot_captcha = os.path.join(os.path.dirname(__file__), '..', '..', 'captcha.png')

    if not os.path.exists(eebot_captcha):
        print("[WARN] captcha.png not found")
        return None

    setup_samples_dir()

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    dest_path = os.path.join(SAMPLES_DIR, f'captcha_{timestamp}.png')

    shutil.copy2(eebot_captcha, dest_path)
    print(f"[OK] Copied to: {dest_path}")

    return dest_path


def label_sample(image_path: str, label: str):
    """Rename sample with correct label"""
    if not os.path.exists(image_path):
        print(f"[ERROR] File not found: {image_path}")
        return None

    # Get directory and base name
    dirname = os.path.dirname(image_path)
    basename = os.path.basename(image_path)

    # Create new name with label
    name_parts = basename.rsplit('.', 1)
    new_name = f"{name_parts[0]}_label_{label}.{name_parts[1]}"
    new_path = os.path.join(dirname, new_name)

    os.rename(image_path, new_path)
    print(f"[OK] Labeled: {new_name}")

    return new_path


def list_samples():
    """List all samples"""
    if not os.path.exists(SAMPLES_DIR):
        print("[INFO] No samples directory")
        return []

    samples = [f for f in os.listdir(SAMPLES_DIR) if f.endswith('.png')]

    print(f"\n{'='*50}")
    print(f"Total samples: {len(samples)}")
    print('='*50)

    labeled = []
    unlabeled = []

    for s in sorted(samples):
        if '_label_' in s:
            labeled.append(s)
        else:
            unlabeled.append(s)

    print(f"\nLabeled ({len(labeled)}):")
    for s in labeled:
        print(f"  {s}")

    print(f"\nUnlabeled ({len(unlabeled)}):")
    for s in unlabeled:
        print(f"  {s}")

    return samples


def get_expected_values():
    """Extract expected values from labeled samples"""
    if not os.path.exists(SAMPLES_DIR):
        return {}

    expected = {}
    for f in os.listdir(SAMPLES_DIR):
        if '_label_' in f and f.endswith('.png'):
            # Extract label from filename
            parts = f.split('_label_')
            if len(parts) == 2:
                label = parts[1].replace('.png', '')
                expected[f] = label

    return expected


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='CAPTCHA Sample Collector')
    parser.add_argument('action', choices=['collect', 'label', 'list', 'test'],
                       help='Action to perform')
    parser.add_argument('--label', '-l', type=str, help='Label for the sample')
    parser.add_argument('--file', '-f', type=str, help='File to label')

    args = parser.parse_args()

    if args.action == 'collect':
        collect_from_eebot()

    elif args.action == 'label':
        if not args.file or not args.label:
            print("[ERROR] --file and --label required")
            sys.exit(1)
        label_sample(args.file, args.label)

    elif args.action == 'list':
        list_samples()

    elif args.action == 'test':
        # Run accuracy test on labeled samples
        from test_eebot_captcha import run_accuracy_test
        expected = get_expected_values()

        if not expected:
            print("[WARN] No labeled samples found")
            print("Use: python collect_samples.py collect")
            print("Then: python collect_samples.py label -f <file> -l <value>")
        else:
            print(f"\nFound {len(expected)} labeled samples")
            run_accuracy_test(SAMPLES_DIR, expected)
