#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 16:29:02 2024

@author: pavlovic
"""

import SimpleITK as sitk
import matplotlib.pyplot as plt
import argparse
import os

# Set up argument parser
parser = argparse.ArgumentParser(description='Generate and display a checkerboard image from two images.')
parser.add_argument('baseline_image', type=str, help='Path to the baseline image.')
parser.add_argument('followup_image', type=str, help='Path to the followup image.')
parser.add_argument('baseline_label', type=str, help='Baseline image label for naming')
parser.add_argument('followup_label', type=str, help='Followup image label for naming')
parser.add_argument('--checker_squares', type=int, nargs='+', default=[20,20,20], help='Number of squares in checkerboard (e.g., 20 20 20)')
parser.add_argument('--slice', type=int, default=50, help='Slice number shown in figure')

args = parser.parse_args()

# Read the fixed and registered images
fixed_image = sitk.ReadImage(args.baseline_image)
registered_image = sitk.ReadImage(args.followup_image)

# Create a checker square for each dimension
checker_squares = [int(s) for s in args.checker_squares]

# Generate the checkerboard image
checkerboard_image = sitk.CheckerBoard(fixed_image, registered_image, checker_squares)

# Convert to numpy array for visualization
checkerboard_array = sitk.GetArrayFromImage(checkerboard_image)

# Extract the directory and base name from the main image path
output_directory = os.path.dirname(args.baseline_image)
main_image_base_name = os.path.basename(args.baseline_image).replace('_common.nii.gz', '').replace('V1', f"{args.baseline_label}_{args.followup_label}")
# Define the subdirectory for outputs
output_subdir = os.path.join(output_directory, "Registration_Checkerboards")

# Create the subdirectory if it doesn't exist
os.makedirs(output_subdir, exist_ok=True)

# Save the resulting checkerboard figures with the following filename
output_filename = os.path.join(output_subdir, f"{main_image_base_name}_checkerboard_{args.slice}.png")

# Display the checkerboard image
plt.figure(figsize=(10, 10))
plt.imshow(checkerboard_array[args.slice, :, :], cmap='gray')
plt.title(f"Checkerboard of {args.baseline_label} and {args.followup_label} Images (Slice:{args.slice})")
plt.axis('off')

plt.savefig(output_filename)
