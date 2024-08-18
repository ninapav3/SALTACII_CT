import SimpleITK as sitk
import pandas as pd
import os
import argparse

# Function to process each label
def process_label(label, description, main_image, mask_image, kernel_radius, output_subdir, base_name):
    # Create binary mask for the current label
    binary_mask = sitk.Equal(mask_image, label)

    # Dilate the binary mask
    dilated_mask = sitk.BinaryDilate(binary_mask, kernel_radius)
    output_filename_mask = os.path.join(output_subdir, f"{base_name}_{description}_mask.nii.gz")
    sitk.WriteImage(dilated_mask, output_filename_mask)
    
    # Apply the dilated mask to the main image
    masked_image = sitk.Mask(main_image, dilated_mask)

    # Save the resulting masked image with the description in the filename
    output_filename_ct = os.path.join(output_subdir, f"{base_name}_{description}.nii.gz")
    sitk.WriteImage(masked_image, output_filename_ct)

    print(f"Processed and saved label {label} ({description}) to {output_filename_ct}")

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
        
        process_label(label, description, main_image, mask_image, kernel_radius, output_subdir, main_image_base_name)
    
    print("Processing complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process and save masked images based on labels.")
    
    # Define command-line arguments
    parser.add_argument('main_image_path', type=str, help='Path to the main image')
    parser.add_argument('mask_image_path', type=str, help='Path to the mask image')
    parser.add_argument('--kernel_radius', type=int, nargs='+', default=[1, 1, 1], help='Kernel radius for dilation (e.g., 2 2 2)')
    parser.add_argument('--label_of_interest', type=int, help='Specific label to process (optional)')

    # Parse arguments
    args = parser.parse_args()

    # Run the main function
    main(args)
