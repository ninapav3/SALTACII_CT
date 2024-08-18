#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 17:23:36 2024

@author: pavlovic
"""

import SimpleITK as sitk
import os
import argparse
import numpy as np

# Set up argument parser
parser = argparse.ArgumentParser(description='Compute and save the voxel difference between two images.')
parser.add_argument('baseline_path', type=str, help='Path to the baseline image.')
parser.add_argument('followup_path', type=str, help='Path to the follow-up image')
parser.add_argument('baseline_label', type=str, help='Label for the baseline image')
parser.add_argument('followup_label', type=str, help='Label for the follow-up image')
parser.add_argument('--gaussian_filter', type=bool, default=False, help='Apply Gaussian filter after voxel subtraction')
parser.add_argument('--gaussian_sigma', type=float, help='Sigma for the Gaussian filter')

args = parser.parse_args()

# Read the baseline and follow-up images
baseline = sitk.ReadImage(args.baseline_path) 
followup = sitk.ReadImage(args.followup_path)

# Threshold the image to remove values over 1500 (e.g., surgical screws)
screwless_followup = sitk.Threshold(followup, lower=-np.inf, upper=1500, outsideValue=1500)

# Compute the voxel-wise difference
difference = sitk.Subtract(followup, baseline)
# Extract the directory and base name from the baseline image path

output_directory = os.path.dirname(args.baseline_path)
main_image_base_name = os.path.basename(args.baseline_path).replace('_common.nii.gz', '').replace('V1', f"{args.baseline_label}_{args.followup_label}")

if args.gaussian_filter == True:
    gaussian = sitk.SmoothingRecursiveGaussianImageFilter()
    gaussian.SetSigma(args.gaussian_sigma)
    difference_gaussian = gaussian.Execute(difference)
    # Define the output filename
    output_filename = os.path.join(output_directory, f"{main_image_base_name}_difference_gaussian_sigma_{args.gaussian_sigma}.nii.gz")
    # Write the output image
    sitk.WriteImage(difference_gaussian, output_filename)
else:
    # Define the output filename
    output_filename = os.path.join(output_directory, f"{main_image_base_name}_difference.nii.gz")
    # Write the output image
    sitk.WriteImage(difference, output_filename)

print(f"Voxel difference image saved to {output_filename}")