#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Quick verification of best parameters"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from improved_ocr import batch_test_method

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')

print("=" * 60)
print("Verifying current best methods")
print("=" * 60)

# Test v3_islands (current best)
print("\n--- v3_islands (min_size=40) ---")
batch_test_method('v3_islands', SAMPLES_DIR, 420)

# Test v8_twostage
print("\n--- v8_twostage ---")
batch_test_method('v8_twostage', SAMPLES_DIR, 420)
