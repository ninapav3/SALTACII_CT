#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  9 13:13:32 2024

@author: pavlovic
"""

import argparse
import SimpleITK as sitk
import os

def main():
    parser = argparse.ArgumentParser(description="Multiply the common region by the baseline mask.")
    parser.add_argument("common_region_image", type=str, help="Path to the common region image.")
    parser.add_argument("mask_image", type=str, help="Path to the mask image.")

    args = parser.parse_args()
    output_directory = os.path.dirname(args.mask_image)
    main_image_base_name = os.path.basename(args.mask_image).replace('_cropped_mask.nii.gz', '')  # Remove the file extension

    # Read the images
    common_region = sitk.ReadImage(args.common_region_image)
    mask = sitk.ReadImage(args.mask_image)

    # Multiply the images
    result = common_region * mask
    
    output_filename = os.path.join(output_directory, f"{main_image_base_name}_common_mask.nii.gz")
    
    # Save the result
    sitk.WriteImage(result, output_filename)

if __name__ == "__main__":
    main()