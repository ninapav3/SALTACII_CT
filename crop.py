#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 13:10:53 2024

@author: pavlovic
"""
import SimpleITK as sitk
import argparse
import os

def find_mask_bounds(mask_sitk):
    mask_array = sitk.GetArrayFromImage(mask_sitk)
    non_zero_indices = mask_array.nonzero()
    min_x, max_x = non_zero_indices[0].min(), non_zero_indices[0].max()
    min_y, max_y = non_zero_indices[1].min(), non_zero_indices[1].max()
    min_z, max_z = non_zero_indices[2].min(), non_zero_indices[2].max()
    return (min_x, max_x), (min_y, max_y), (min_z, max_z)

def crop_image(image_sitk, mask_sitk, buffer=30):
    #Crops an image and its corresponding mask image with a buffer on the outside so that it is not exactly down to the mask.
    (min_x, max_x), (min_y, max_y), (min_z, max_z) = find_mask_bounds(mask_sitk)
    min_x = max(min_x - buffer, 0)
    max_x = min(max_x + buffer, mask_sitk.GetSize()[2] - 1)
    min_y = max(min_y - buffer, 0)
    max_y = min(max_y + buffer, mask_sitk.GetSize()[1] - 1)
    min_z = max(min_z - buffer, 0)
    max_z = min(max_z + buffer, mask_sitk.GetSize()[0] - 1)
    extract_size = [int(max_z - min_z + 1), int(max_y - min_y + 1), int(max_x - min_x + 1)]
    extract_index = [int(min_z), int(min_y), int(min_x)]
    extractor = sitk.RegionOfInterestImageFilter()
    extractor.SetSize(extract_size)
    extractor.SetIndex(extract_index)
    cropped_image = extractor.Execute(image_sitk)
    cropped_mask = extractor.Execute(mask_sitk)
    return cropped_image, cropped_mask

def main():
    parser = argparse.ArgumentParser(description="Crop an image and its corresponding mask using a buffer.")
    parser.add_argument('image', type=str, help="Path to the input image (e.g., CT scan).")
    parser.add_argument('mask', type=str, help="Path to the input mask image.")
    parser.add_argument('--buffer', type=int, default=30, help="Buffer size around the mask (default: 30).")
    parser.add_argument('--cropped_mask', type=bool, default = False, help="Make a cropped mask file.")

    args = parser.parse_args()

    # Read images
    image_sitk = sitk.ReadImage(args.image)
    mask_sitk = sitk.ReadImage(args.mask)

    # Crop images
    cropped_image, cropped_mask = crop_image(image_sitk, mask_sitk, buffer=args.buffer)
    
    # Extract the directory and base name from the main image path
    output_directory = os.path.dirname(args.image)
    main_image_base_name = os.path.basename(args.image).replace('.nii.gz', '')
    
    output_filename = os.path.join(output_directory, f"{main_image_base_name}_cropped.nii.gz")
    
    # Write output
    sitk.WriteImage(cropped_image, output_filename)
    print(f"Cropped image saved to {output_filename}")
    
    if args.cropped_mask == True :
        output_filename_mask = os.path.join(output_directory, f"{main_image_base_name}_cropped_mask.nii.gz")
        sitk.WriteImage(cropped_mask, output_filename_mask)
        print(f"Cropped mask image saved to {output_filename_mask}")

if __name__ == "__main__":
    main()