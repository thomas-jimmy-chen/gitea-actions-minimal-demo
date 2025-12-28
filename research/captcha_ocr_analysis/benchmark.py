#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Benchmark execution time for each method"""

import os
import glob
import time
import cv2 as cv

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')

def benchmark():
    from improved_ocr import recognize_with_method
    from optimized_ocr import recognize_with_fallback

    samples = sorted(glob.glob(os.path.join(SAMPLES_DIR, "captcha_*.png")))[:50]
    print(f"Benchmarking on {len(samples)} samples...\n")

    # v3_islands
    start = time.time()
    for path in samples:
        recognize_with_method(path, 'v3_islands')
    t1 = time.time() - start

    # optimized
    start = time.time()
    for path in samples:
        recognize_with_fallback(path)
    t2 = time.time() - start

    print("=" * 50)
    print("BENCHMARK RESULTS")
    print("=" * 50)
    print(f"\nv3_islands (single):")
    print(f"  Total: {t1:.2f}s for {len(samples)} samples")
    print(f"  Per image: {t1/len(samples)*1000:.0f}ms")

    print(f"\nOptimized (multi-strategy):")
    print(f"  Total: {t2:.2f}s for {len(samples)} samples")
    print(f"  Per image: {t2/len(samples)*1000:.0f}ms")

    print(f"\nRatio: {t2/t1:.1f}x slower")

if __name__ == "__main__":
    benchmark()
