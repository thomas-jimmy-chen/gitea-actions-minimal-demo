#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Technique Specialization Analysis

Compare v3_islands, v7_multidim, v8_twostage to find their unique strengths.
"""

import os
import glob
import json
from collections import defaultdict
from improved_ocr import recognize_with_method, PREPROCESS_METHODS
import cv2 as cv
import numpy as np

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')
ANALYSIS_FILE = os.path.join(os.path.dirname(__file__), 'technique_analysis.json')


def analyze_all_samples(limit=420):
    """Run all 3 techniques on all samples and record results"""
    samples = sorted(glob.glob(os.path.join(SAMPLES_DIR, "captcha_*.png")))[:limit]

    techniques = ['v3_islands', 'v7_multidim', 'v8_twostage']

    print(f"Analyzing {len(samples)} samples with 3 techniques...")
    print("=" * 60)

    results = {}
    for sample in samples:
        filename = os.path.basename(sample)
        results[filename] = {}

        for tech in techniques:
            success, result, confidence = recognize_with_method(sample, tech)
            results[filename][tech] = {
                'success': success,
                'result': result,
                'confidence': confidence
            }

    return results


def find_unique_successes(results):
    """Find cases where only one technique succeeds"""
    techniques = ['v3_islands', 'v7_multidim', 'v8_twostage']

    unique = {tech: [] for tech in techniques}
    all_success = []
    all_fail = []

    for filename, tech_results in results.items():
        successes = [t for t in techniques if tech_results[t]['success']]

        if len(successes) == 0:
            all_fail.append(filename)
        elif len(successes) == 3:
            all_success.append(filename)
        elif len(successes) == 1:
            unique[successes[0]].append(filename)

    return unique, all_success, all_fail


def analyze_image_characteristics(filepath):
    """Analyze image characteristics to understand why techniques differ"""
    image = cv.imread(filepath)
    if image is None:
        return None

    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    # Basic stats
    height, width = gray.shape
    mean_intensity = np.mean(gray)
    std_intensity = np.std(gray)

    # Edge density (proxy for noise)
    edges = cv.Canny(gray, 50, 150)
    edge_density = np.sum(edges > 0) / (height * width)

    # Binary analysis
    _, binary = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)

    # Connected components
    num_labels, labels, stats, _ = cv.connectedComponentsWithStats(binary, connectivity=8)

    # Component size distribution
    areas = [stats[i, cv.CC_STAT_AREA] for i in range(1, num_labels)]
    small_components = len([a for a in areas if a < 30])
    medium_components = len([a for a in areas if 30 <= a < 100])
    large_components = len([a for a in areas if a >= 100])

    # Aspect ratios
    aspect_ratios = []
    for i in range(1, num_labels):
        w = stats[i, cv.CC_STAT_WIDTH]
        h = stats[i, cv.CC_STAT_HEIGHT]
        if h > 0:
            aspect_ratios.append(w / h)

    thin_components = len([ar for ar in aspect_ratios if ar < 0.3 or ar > 3.0])

    return {
        'width': width,
        'height': height,
        'mean_intensity': mean_intensity,
        'std_intensity': std_intensity,
        'edge_density': edge_density,
        'total_components': num_labels - 1,
        'small_components': small_components,
        'medium_components': medium_components,
        'large_components': large_components,
        'thin_components': thin_components,
    }


def main():
    print("=" * 60)
    print("Technique Specialization Analysis")
    print("=" * 60)

    # Step 1: Get all results
    results = analyze_all_samples(420)

    # Step 2: Find unique successes
    unique, all_success, all_fail = find_unique_successes(results)

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)

    print(f"\nAll 3 techniques succeed: {len(all_success)} samples")
    print(f"All 3 techniques fail: {len(all_fail)} samples")

    print("\nUnique successes (only this technique works):")
    for tech, files in unique.items():
        print(f"  {tech}: {len(files)} samples")

    # Step 3: Analyze characteristics of unique successes
    print("\n" + "=" * 60)
    print("CHARACTERISTIC ANALYSIS")
    print("=" * 60)

    analysis = {}
    for tech, files in unique.items():
        if not files:
            continue

        print(f"\n--- {tech} unique successes ({len(files)} samples) ---")

        characteristics = []
        for f in files[:10]:  # Analyze first 10
            filepath = os.path.join(SAMPLES_DIR, f)
            chars = analyze_image_characteristics(filepath)
            if chars:
                characteristics.append(chars)
                print(f"  {f}:")
                print(f"    Components: {chars['total_components']} (small:{chars['small_components']}, thin:{chars['thin_components']})")
                print(f"    Edge density: {chars['edge_density']:.4f}")

        if characteristics:
            # Average characteristics
            avg_chars = {}
            for key in characteristics[0].keys():
                if isinstance(characteristics[0][key], (int, float)):
                    avg_chars[key] = np.mean([c[key] for c in characteristics])

            analysis[tech] = {
                'count': len(files),
                'files': files,
                'avg_characteristics': avg_chars
            }

    # Step 4: Compare average characteristics
    print("\n" + "=" * 60)
    print("AVERAGE CHARACTERISTICS BY TECHNIQUE")
    print("=" * 60)

    for tech, data in analysis.items():
        if 'avg_characteristics' in data:
            print(f"\n{tech}:")
            for key, val in data['avg_characteristics'].items():
                print(f"  {key}: {val:.2f}")

    # Step 5: Pairwise comparison
    print("\n" + "=" * 60)
    print("PAIRWISE COMPARISON")
    print("=" * 60)

    techniques = ['v3_islands', 'v7_multidim', 'v8_twostage']

    for i, t1 in enumerate(techniques):
        for t2 in techniques[i+1:]:
            t1_only = 0
            t2_only = 0
            both = 0
            neither = 0

            for filename, tech_results in results.items():
                s1 = tech_results[t1]['success']
                s2 = tech_results[t2]['success']

                if s1 and s2:
                    both += 1
                elif s1 and not s2:
                    t1_only += 1
                elif s2 and not s1:
                    t2_only += 1
                else:
                    neither += 1

            print(f"\n{t1} vs {t2}:")
            print(f"  Both succeed: {both}")
            print(f"  Only {t1}: {t1_only}")
            print(f"  Only {t2}: {t2_only}")
            print(f"  Both fail: {neither}")

    # Save results
    output = {
        'total_samples': len(results),
        'all_success': len(all_success),
        'all_fail': len(all_fail),
        'unique_successes': {k: len(v) for k, v in unique.items()},
        'analysis': {k: {'count': v['count'], 'avg': v.get('avg_characteristics', {})}
                    for k, v in analysis.items()},
        'all_fail_files': all_fail[:20],  # First 20 failed files
    }

    with open(ANALYSIS_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n\nAnalysis saved to: {ANALYSIS_FILE}")

    # Final recommendation
    print("\n" + "=" * 60)
    print("RECOMMENDATION")
    print("=" * 60)

    print("""
Based on the analysis:

1. v3_islands (Pure area filtering):
   - Best overall accuracy
   - Simplest approach
   - Good for: Random dot noise

2. v7_multidim (Multi-dimensional):
   - Filters by width/height/aspect ratio
   - Good for: Line noise (very thin or wide artifacts)
   - Slightly lower accuracy on this CAPTCHA type

3. v8_twostage (Erosion + Components):
   - Similar to v3_islands
   - Better for: Noise connected to characters
   - The erosion step breaks connections first

For EEBot integration:
- Use v3_islands as primary (75.7%)
- If different CAPTCHA types encountered:
  - Line noise -> try v7_multidim
  - Connected noise -> try v8_twostage
  - Complex noise -> try combining results
""")


if __name__ == "__main__":
    main()
