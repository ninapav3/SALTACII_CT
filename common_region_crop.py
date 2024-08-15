#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 14:12:58 2024

@author: pavlovic
"""

import SimpleITK as sitk
import os
import argparse

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

def main(args):
    # Read the main image and the mask image
    main_image = sitk.ReadImage(args.transformed_image_path)
    mask_image = sitk.ReadImage(args.common_region_mask_path)
    #print(sitk.GetSize(main_image))
    #print(sitk.GetSize(mask_image))
    
    # Extract the directory and base name from the main image path
    output_directory = os.path.dirname(args.transformed_image_path)
    main_image_base_name = os.path.basename(args.transformed_image_path).replace('_Transformed.nii.gz', '').replace('_cropped.nii.gz','')

    # Apply the dilated mask to the main image
    masked_image = sitk.Mask(main_image, mask_image)
    
    # Crop images
    cropped_image, cropped_mask = crop_image(masked_image, mask_image, buffer=args.buffer)
    
    # Extract the directory and base name from the main image path
    output_filename = os.path.join(output_directory, f"{main_image_base_name}_common.nii.gz")
    
    # Write output
    sitk.WriteImage(cropped_image, output_filename)
    print(f"Cropped image saved to {output_filename}")
    
    if args.cropped_mask == True :
        output_filename_mask = os.path.join(output_directory, f"{main_image_base_name}_cropped_common_mask.nii.gz")
        sitk.WriteImage(cropped_mask, output_filename_mask)
        print(f"Cropped mask image saved to {output_filename_mask}")
    
    print("Processing complete.")
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract and Crop the images to the size of the common region mask")
    
    # Define command-line arguments
    parser.add_argument('transformed_image_path', type=str, help='Path to the transformed image')
    parser.add_argument('common_region_mask_path', type=str, help='Path to the common region mask')
    parser.add_argument('--buffer', type=int, default=30, help="Buffer size around the mask (default: 30).")
    parser.add_argument('--cropped_mask', type=bool, default = False, help="Make a cropped mask file.")

    # Parse arguments
    args = parser.parse_args()

    # Run the main function
    main(args)
