#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 18 14:41:11 2024

@author: pavlovic
"""

import SimpleITK as sitk
import pandas as pd
import os
import argparse

# Function to process each label
def process_label(label, description, main_image, mask_image, kernel_radius):
    # Create binary mask for the current label
    binary_mask = sitk.Equal(mask_image, label)

    # Dilate the binary mask
    dilated_mask = sitk.BinaryDilate(binary_mask, kernel_radius)
    
    return dilated_mask 

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
    main_image = sitk.ReadImage(args.main_image_path)
    mask_image = sitk.ReadImage(args.mask_image_path)

    # Create a minimal kernel radius for each dimension
    kernel_radius = [int(r) for r in args.kernel_radius]

    # Hardcoded path to the CSV file containing labels and descriptions
    labels_csv_path = '/Users/pavlovic/Desktop/Analysis/SALTACII_CT/ML_labels.csv'

    # Read the DataFrame containing labels and descriptions
    labels_list = pd.read_csv(labels_csv_path)
    
    # Extract the directory and base name from the main image path
    output_directory = os.path.dirname(args.main_image_path)
    main_image_base_name = os.path.basename(args.main_image_path).replace('_CAL.nii.gz', '')  # Remove the file extension
    
    # Filter labels based on the label of interest, if provided
    if args.label_of_interest is not None:
        labels_list = labels_list[labels_list['IND'] == args.label_of_interest]

    # Process each row in the DataFrame
    for index, row in labels_list.iterrows():
        label = row['IND']
        description = row['LABEL'].replace(" ", "_")  # Replace spaces with underscores for filenames
        # Define the subdirectory for outputs
        output_subdir = os.path.join(output_directory, f"{description}")
        
        # Create the subdirectory if it doesn't exist
        os.makedirs(output_subdir, exist_ok=True)
        
        dilated_mask = process_label(label, description, main_image, mask_image, kernel_radius)
        
        # Crop images
        cropped_image, cropped_mask = crop_image(main_image, dilated_mask, buffer=args.buffer)
        
        # Extract the directory and base name from the main image path
        output_directory = os.path.dirname(args.main_image_path)

        output_filename = os.path.join(output_subdir, f"{main_image_base_name}_{description}_treece_cropped.nii.gz")
        
        # Write output
        sitk.WriteImage(cropped_image, output_filename)
        print(f"Cropped image saved to {output_filename}")
        
        if args.cropped_mask == True :
            output_filename_mask = os.path.join(output_subdir, f"{main_image_base_name}_{description}_treece_cropped_mask.nii.gz")
            sitk.WriteImage(cropped_mask, output_filename_mask)
            print(f"Cropped mask image saved to {output_filename_mask}")
        
    
    print("Processing complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process and save masked images based on labels.")
    
    # Define command-line arguments
    parser.add_argument('main_image_path', type=str, help='Path to the main image')
    parser.add_argument('mask_image_path', type=str, help='Path to the mask image')
    parser.add_argument('--kernel_radius', type=int, nargs='+', default=[2, 2, 2], help='Kernel radius for dilation (e.g., 2 2 2)')
    parser.add_argument('--label_of_interest', type=int, help='Specific label to process (optional)')

    #Deine command-line arguments for cropping
    parser.add_argument('--buffer', type=int, default=30, help="Buffer size around the mask (default: 30).")
    parser.add_argument('--cropped_mask', type=bool, default = False, help="Make a cropped mask file.")

    args = parser.parse_args()

    # Run the main function
    main(args)
