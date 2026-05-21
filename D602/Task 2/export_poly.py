#!/usr/bin/env python
# coding: utf-8

# ============================================================
# export_poly.py
# Run this script ONCE from your Task 2 folder to save the
# polynomial transformer as poly.pkl alongside finalized_model.pkl
#
# Usage:
#   python export_poly.py
#
# Then copy both files to your Task 3 project root:
#   - finalized_model.pkl
#   - poly.pkl
# ============================================================

import pickle
import argparse
from sklearn.preprocessing import PolynomialFeatures

# Match the order used during your Task 2 training.
# Default is 1 (as specified in the template comments).
parser = argparse.ArgumentParser()
parser.add_argument('--order', type=int, default=1, help='Polynomial order used in Task 2 training')
args, _ = parser.parse_known_args()

# Recreate the polynomial transformer with the same order
poly = PolynomialFeatures(degree=args.order)

# Save it
with open('poly.pkl', 'wb') as f:
    pickle.dump(poly, f)

print(f"poly.pkl saved with degree={args.order}")
print("Now copy both finalized_model.pkl and poly.pkl into your Task 3 project root.")