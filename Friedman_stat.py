import pandas as pd
import numpy as np
import SimpleITK as sitk
import os
from scipy.stats import friedmanchisquare
import scikit_posthocs as sp

def analyze_ct_images(ct_image_paths, output_file):
    """
    Analyze CT images for a given participant and leg condition.
    
    Parameters:
    - ct_image_paths: list of str, paths to the CT images corresponding to different follow-up visits
    - output_file: str, path to save the CSV output file with the results
    
    Returns:
    - df: pandas DataFrame containing the computed statistics for each visit
    """
    # Initialize a DataFrame to store the results
    columns = ['Visit', 'Participant', 'Leg Condition', 'Mean', 'StdDev', 'Max', 'Min', 'Median', 'IQR']
    df = pd.DataFrame(columns=columns)

    for image_path in ct_image_paths:
        # Extract participant ID and leg condition from the file path
        participant_id = os.path.basename(os.path.dirname(os.path.dirname(image_path)))  # Gets 'SALTACII_0004'
        leg = os.path.basename(os.path.dirname(image_path))  # Gets 'Femur_Left'
        # Determine visit number based on file suffix
        base_name = os.path.basename(image_path)
        if base_name.endswith('_common.nii.gz'):
            visit_number = base_name.replace(f"{participant_id}_", '').replace(f"_{leg}_common.nii.gz", '')
        elif base_name.endswith('_difference.nii.gz'):
            visit_number = base_name.replace(f"{participant_id}_", '').replace(f"_{leg}_difference.nii.gz", '')
        else:
            raise ValueError("File name does not match expected patterns.")
            
        # Load the image
        image = sitk.ReadImage(image_path)
        # Threshold the image to remove values over 1500 (e.g., surgical screws)
        image = sitk.Threshold(image, lower=-np.inf, upper=1500, outsideValue=1500)
        image_array = sitk.GetArrayFromImage(image)
        
        # Extract all non-zero values
        non_zero_values = image_array[image_array != 0]
        mean_non_zero = np.mean(non_zero_values)
        median_non_zero = np.median(non_zero_values)
        std_non_zero = np.std(non_zero_values)
        max_non_zero = np.max(non_zero_values)
        min_non_zero = np.min(non_zero_values)
        p25_non_zero = np.percentile(non_zero_values, 25)
        p75_non_zero = np.percentile(non_zero_values, 75)

        # Append to the DataFrame
        row = pd.DataFrame({
            'Visit': [visit_number],
            'Participant': [participant_id],
            'Leg Condition': [leg],
            'Mean': [mean_non_zero],
            'StdDev': [std_non_zero],
            'Max': [max_non_zero],
            'Min': [min_non_zero],
            'Median': [median_non_zero],
            'IQR': [f"{p25_non_zero}-{p75_non_zero}"]
        })
        
        # Concatenate the new row to the DataFrame
        df = pd.concat([df, row], ignore_index=True)

    # Save the DataFrame to a CSV file
    df.to_csv(output_file, index=False)

    #print(df)
    return df
"""
# Example usage
femur_paths = [
    '/Users/pavlovic/Desktop/SALTACII_0004/Femur_Left/SALTACII_0004_V1_Femur_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0004/Femur_Left/SALTACII_0004_VS_Femur_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0004/Femur_Left/SALTACII_0004_V2_Femur_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0004/Femur_Left/SALTACII_0004_V3_Femur_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0004/Femur_Left/SALTACII_0004_V4_Femur_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0004/Femur_Right/SALTACII_0004_V1_Femur_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0004/Femur_Right/SALTACII_0004_VS_Femur_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0004/Femur_Right/SALTACII_0004_V2_Femur_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0004/Femur_Right/SALTACII_0004_V3_Femur_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0004/Femur_Right/SALTACII_0004_V4_Femur_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0012/Femur_Left/SALTACII_0012_V1_Femur_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Femur_Left/SALTACII_0012_VS_Femur_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0012/Femur_Left/SALTACII_0012_V2_Femur_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0012/Femur_Left/SALTACII_0012_V3_Femur_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Femur_Left/SALTACII_0012_V4_Femur_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Femur_Right/SALTACII_0012_V1_Femur_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Femur_Right/SALTACII_0012_VS_Femur_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0012/Femur_Right/SALTACII_0012_V2_Femur_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0012/Femur_Right/SALTACII_0012_V3_Femur_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Femur_Right/SALTACII_0012_V4_Femur_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0030/Femur_Left/SALTACII_0030_V1_Femur_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0030/Femur_Left/SALTACII_0030_VS_Femur_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0030/Femur_Left/SALTACII_0030_V2_Femur_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0030/Femur_Left/SALTACII_0030_V3_Femur_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0030/Femur_Left/SALTACII_0030_V4_Femur_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0030/Femur_Right/SALTACII_0030_V1_Femur_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0030/Femur_Right/SALTACII_0030_VS_Femur_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0030/Femur_Right/SALTACII_0030_V2_Femur_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0030/Femur_Right/SALTACII_0030_V3_Femur_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0030/Femur_Right/SALTACII_0030_V4_Femur_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0068/Femur_Left/SALTACII_0068_V1_Femur_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0068/Femur_Left/SALTACII_0068_VS_Femur_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0068/Femur_Left/SALTACII_0068_V2_Femur_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0068/Femur_Left/SALTACII_0068_V3_Femur_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0068/Femur_Left/SALTACII_0068_V4_Femur_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0068/Femur_Right/SALTACII_0068_V1_Femur_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0068/Femur_Right/SALTACII_0068_VS_Femur_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0068/Femur_Right/SALTACII_0068_V2_Femur_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0068/Femur_Right/SALTACII_0068_V3_Femur_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0068/Femur_Right/SALTACII_0068_V4_Femur_Right_common.nii.gz'
]

tibia_paths = [
    '/Users/pavlovic/Desktop/SALTACII_0004/Tibia_Left/SALTACII_0004_V1_Tibia_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0004/Tibia_Left/SALTACII_0004_VS_Tibia_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0004/Tibia_Left/SALTACII_0004_V2_Tibia_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0004/Tibia_Left/SALTACII_0004_V3_Tibia_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0004/Tibia_Left/SALTACII_0004_V4_Tibia_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0004/Tibia_Right/SALTACII_0004_V1_Tibia_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0004/Tibia_Right/SALTACII_0004_VS_Tibia_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0004/Tibia_Right/SALTACII_0004_V2_Tibia_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0004/Tibia_Right/SALTACII_0004_V3_Tibia_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0004/Tibia_Right/SALTACII_0004_V4_Tibia_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0012/Tibia_Left/SALTACII_0012_V1_Tibia_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Tibia_Left/SALTACII_0012_VS_Tibia_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0012/Tibia_Left/SALTACII_0012_V2_Tibia_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0012/Tibia_Left/SALTACII_0012_V3_Tibia_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Tibia_Left/SALTACII_0012_V4_Tibia_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Tibia_Right/SALTACII_0012_V1_Tibia_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Tibia_Right/SALTACII_0012_VS_Tibia_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0012/Tibia_Right/SALTACII_0012_V2_Tibia_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0012/Tibia_Right/SALTACII_0012_V3_Tibia_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Tibia_Right/SALTACII_0012_V4_Tibia_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0030/Tibia_Left/SALTACII_0030_V1_Tibia_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0030/Tibia_Left/SALTACII_0030_VS_Tibia_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0030/Tibia_Left/SALTACII_0030_V2_Tibia_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0030/Tibia_Left/SALTACII_0030_V3_Tibia_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0030/Tibia_Left/SALTACII_0030_V4_Tibia_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0030/Tibia_Right/SALTACII_0030_V1_Tibia_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0030/Tibia_Right/SALTACII_0030_VS_Tibia_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0030/Tibia_Right/SALTACII_0030_V2_Tibia_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0030/Tibia_Right/SALTACII_0030_V3_Tibia_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0030/Tibia_Right/SALTACII_0030_V4_Tibia_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0068/Tibia_Left/SALTACII_0068_V1_Tibia_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0068/Tibia_Left/SALTACII_0068_VS_Tibia_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0068/Tibia_Left/SALTACII_0068_V2_Tibia_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0068/Tibia_Left/SALTACII_0068_V3_Tibia_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0068/Tibia_Left/SALTACII_0068_V4_Tibia_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0068/Tibia_Right/SALTACII_0068_V1_Tibia_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0068/Tibia_Right/SALTACII_0068_VS_Tibia_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0068/Tibia_Right/SALTACII_0068_V2_Tibia_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0068/Tibia_Right/SALTACII_0068_V3_Tibia_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0068/Tibia_Right/SALTACII_0068_V4_Tibia_Right_common.nii.gz'
]

patella_paths = [
    '/Users/pavlovic/Desktop/SALTACII_0004/Patella_Left/SALTACII_0004_V1_Patella_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0004/Patella_Left/SALTACII_0004_VS_Patella_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0004/Patella_Left/SALTACII_0004_V2_Patella_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0004/Patella_Left/SALTACII_0004_V3_Patella_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0004/Patella_Left/SALTACII_0004_V4_Patella_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0004/Patella_Right/SALTACII_0004_V1_Patella_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0004/Patella_Right/SALTACII_0004_VS_Patella_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0004/Patella_Right/SALTACII_0004_V2_Patella_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0004/Patella_Right/SALTACII_0004_V3_Patella_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0004/Patella_Right/SALTACII_0004_V4_Patella_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0012/Patella_Left/SALTACII_0012_V1_Patella_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Patella_Left/SALTACII_0012_VS_Patella_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0012/Patella_Left/SALTACII_0012_V2_Patella_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0012/Patella_Left/SALTACII_0012_V3_Patella_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Patella_Left/SALTACII_0012_V4_Patella_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Patella_Right/SALTACII_0012_V1_Patella_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Patella_Right/SALTACII_0012_VS_Patella_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0012/Patella_Right/SALTACII_0012_V2_Patella_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0012/Patella_Right/SALTACII_0012_V3_Patella_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Patella_Right/SALTACII_0012_V4_Patella_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0030/Patella_Left/SALTACII_0030_V1_Patella_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0030/Patella_Left/SALTACII_0030_VS_Patella_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0030/Patella_Left/SALTACII_0030_V2_Patella_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0030/Patella_Left/SALTACII_0030_V3_Patella_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0030/Patella_Left/SALTACII_0030_V4_Patella_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0030/Patella_Right/SALTACII_0030_V1_Patella_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0030/Patella_Right/SALTACII_0030_VS_Patella_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0030/Patella_Right/SALTACII_0030_V2_Patella_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0030/Patella_Right/SALTACII_0030_V3_Patella_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0030/Patella_Right/SALTACII_0030_V4_Patella_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0068/Patella_Left/SALTACII_0068_V1_Patella_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0068/Patella_Left/SALTACII_0068_VS_Patella_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0068/Patella_Left/SALTACII_0068_V2_Patella_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0068/Patella_Left/SALTACII_0068_V3_Patella_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0068/Patella_Left/SALTACII_0068_V4_Patella_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0068/Patella_Right/SALTACII_0068_V1_Patella_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0068/Patella_Right/SALTACII_0068_VS_Patella_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0068/Patella_Right/SALTACII_0068_V2_Patella_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0068/Patella_Right/SALTACII_0068_V3_Patella_Right_common.nii.gz',
    
]

diff_femur_paths = [
    '/Users/pavlovic/Desktop/SALTACII_0004/Femur_Left/SALTACII_0004_V1_VS_Femur_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0004/Femur_Left/SALTACII_0004_V1_V2_Femur_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0004/Femur_Left/SALTACII_0004_V1_V3_Femur_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0004/Femur_Left/SALTACII_0004_V1_V4_Femur_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0004/Femur_Right/SALTACII_0004_V1_VS_Femur_Right_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0004/Femur_Right/SALTACII_0004_V1_V2_Femur_Right_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0004/Femur_Right/SALTACII_0004_V1_V3_Femur_Right_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0004/Femur_Right/SALTACII_0004_V1_V4_Femur_Right_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Femur_Left/SALTACII_0012_V1_VS_Femur_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Femur_Left/SALTACII_0012_V1_V2_Femur_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Femur_Left/SALTACII_0012_V1_V3_Femur_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Femur_Left/SALTACII_0012_V1_V4_Femur_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Femur_Right/SALTACII_0012_V1_VS_Femur_Right_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Femur_Right/SALTACII_0012_V1_V2_Femur_Right_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Femur_Right/SALTACII_0012_V1_V3_Femur_Right_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Femur_Right/SALTACII_0012_V1_V4_Femur_Right_difference.nii.gz',  
    '/Users/pavlovic/Desktop/SALTACII_0030/Femur_Left/SALTACII_0030_V1_VS_Femur_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0030/Femur_Left/SALTACII_0030_V1_V2_Femur_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0030/Femur_Left/SALTACII_0030_V1_V3_Femur_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0030/Femur_Left/SALTACII_0030_V1_V4_Femur_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0030/Femur_Right/SALTACII_0030_V1_VS_Femur_Right_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0030/Femur_Right/SALTACII_0030_V1_V2_Femur_Right_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0030/Femur_Right/SALTACII_0030_V1_V3_Femur_Right_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0030/Femur_Right/SALTACII_0030_V1_V4_Femur_Right_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0068/Femur_Left/SALTACII_0068_V1_VS_Femur_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0068/Femur_Left/SALTACII_0068_V1_V2_Femur_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0068/Femur_Left/SALTACII_0068_V1_V3_Femur_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0068/Femur_Left/SALTACII_0068_V1_V4_Femur_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0068/Femur_Right/SALTACII_0068_V1_VS_Femur_Right_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0068/Femur_Right/SALTACII_0068_V1_V2_Femur_Right_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0068/Femur_Right/SALTACII_0068_V1_V3_Femur_Right_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0068/Femur_Right/SALTACII_0068_V1_V4_Femur_Right_difference.nii.gz'
]
    
    
diff_tibia_paths = [
    '/Users/pavlovic/Desktop/SALTACII_0004/Tibia_Left/SALTACII_0004_V1_VS_Tibia_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0004/Tibia_Left/SALTACII_0004_V1_V2_Tibia_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0004/Tibia_Left/SALTACII_0004_V1_V3_Tibia_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0004/Tibia_Left/SALTACII_0004_V1_V4_Tibia_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0004/Tibia_Right/SALTACII_0004_V1_VS_Tibia_Right_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0004/Tibia_Right/SALTACII_0004_V1_V2_Tibia_Right_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0004/Tibia_Right/SALTACII_0004_V1_V3_Tibia_Right_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0004/Tibia_Right/SALTACII_0004_V1_V4_Tibia_Right_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Tibia_Left/SALTACII_0012_V1_VS_Tibia_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Tibia_Left/SALTACII_0012_V1_V2_Tibia_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Tibia_Left/SALTACII_0012_V1_V3_Tibia_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Tibia_Left/SALTACII_0012_V1_V4_Tibia_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Tibia_Right/SALTACII_0012_V1_VS_Tibia_Right_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Tibia_Right/SALTACII_0012_V1_V2_Tibia_Right_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Tibia_Right/SALTACII_0012_V1_V3_Tibia_Right_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Tibia_Right/SALTACII_0012_V1_V4_Tibia_Right_difference.nii.gz',  
    '/Users/pavlovic/Desktop/SALTACII_0030/Tibia_Left/SALTACII_0030_V1_VS_Tibia_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0030/Tibia_Left/SALTACII_0030_V1_V2_Tibia_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0030/Tibia_Left/SALTACII_0030_V1_V3_Tibia_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0030/Tibia_Left/SALTACII_0030_V1_V4_Tibia_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0030/Tibia_Right/SALTACII_0030_V1_VS_Tibia_Right_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0030/Tibia_Right/SALTACII_0030_V1_V2_Tibia_Right_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0030/Tibia_Right/SALTACII_0030_V1_V3_Tibia_Right_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0030/Tibia_Right/SALTACII_0030_V1_V4_Tibia_Right_difference.nii.gz',
    #'/Users/pavlovic/Desktop/SALTACII_0068/Tibia_Left/SALTACII_0068_V1_VS_Tibia_Left_difference.nii.gz',
    #'/Users/pavlovic/Desktop/SALTACII_0068/Tibia_Left/SALTACII_0068_V1_V2_Tibia_Left_difference.nii.gz',
    #'/Users/pavlovic/Desktop/SALTACII_0068/Tibia_Left/SALTACII_0068_V1_V3_Tibia_Left_difference.nii.gz',
    #'/Users/pavlovic/Desktop/SALTACII_0068/Tibia_Left/SALTACII_0068_V1_V4_Tibia_Left_difference.nii.gz',
    #'/Users/pavlovic/Desktop/SALTACII_0068/Tibia_Right/SALTACII_0068_V1_VS_Tibia_Right_difference.nii.gz',
    #'/Users/pavlovic/Desktop/SALTACII_0068/Tibia_Right/SALTACII_0068_V1_V2_Tibia_Right_difference.nii.gz',
    #'/Users/pavlovic/Desktop/SALTACII_0068/Tibia_Right/SALTACII_0068_V1_V3_Tibia_Right_difference.nii.gz',
    #'/Users/pavlovic/Desktop/SALTACII_0068/Tibia_Right/SALTACII_0068_V1_V4_Tibia_Right_difference.nii.gz'
]
    
    
diff_patella_paths = [
    '/Users/pavlovic/Desktop/SALTACII_0004/Patella_Left/SALTACII_0004_V1_VS_Patella_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0004/Patella_Left/SALTACII_0004_V1_V2_Patella_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0004/Patella_Left/SALTACII_0004_V1_V3_Patella_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0004/Patella_Left/SALTACII_0004_V1_V4_Patella_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0004/Patella_Right/SALTACII_0004_V1_VS_Patella_Right_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0004/Patella_Right/SALTACII_0004_V1_V2_Patella_Right_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0004/Patella_Right/SALTACII_0004_V1_V3_Patella_Right_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0004/Patella_Right/SALTACII_0004_V1_V4_Patella_Right_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Patella_Left/SALTACII_0012_V1_VS_Patella_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Patella_Left/SALTACII_0012_V1_V2_Patella_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Patella_Left/SALTACII_0012_V1_V3_Patella_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Patella_Left/SALTACII_0012_V1_V4_Patella_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Patella_Right/SALTACII_0012_V1_VS_Patella_Right_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Patella_Right/SALTACII_0012_V1_V2_Patella_Right_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Patella_Right/SALTACII_0012_V1_V3_Patella_Right_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0012/Patella_Right/SALTACII_0012_V1_V4_Patella_Right_difference.nii.gz',  
    '/Users/pavlovic/Desktop/SALTACII_0030/Patella_Left/SALTACII_0030_V1_VS_Patella_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0030/Patella_Left/SALTACII_0030_V1_V2_Patella_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0030/Patella_Left/SALTACII_0030_V1_V3_Patella_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0030/Patella_Left/SALTACII_0030_V1_V4_Patella_Left_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0030/Patella_Right/SALTACII_0030_V1_VS_Patella_Right_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0030/Patella_Right/SALTACII_0030_V1_V2_Patella_Right_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0030/Patella_Right/SALTACII_0030_V1_V3_Patella_Right_difference.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0030/Patella_Right/SALTACII_0030_V1_V4_Patella_Right_difference.nii.gz',
    #'/Users/pavlovic/Desktop/SALTACII_0068/Patella_Left/SALTACII_0068_V1_VS_Patella_Left_difference.nii.gz',
    #'/Users/pavlovic/Desktop/SALTACII_0068/Patella_Left/SALTACII_0068_V1_V2_Patella_Left_difference.nii.gz',
    #'/Users/pavlovic/Desktop/SALTACII_0068/Patella_Left/SALTACII_0068_V1_V3_Patella_Left_difference.nii.gz',
    #'/Users/pavlovic/Desktop/SALTACII_0068/Patella_Left/SALTACII_0068_V1_V4_Patella_Left_difference.nii.gz',
    #'/Users/pavlovic/Desktop/SALTACII_0068/Patella_Right/SALTACII_0068_V1_VS_Patella_Right_difference.nii.gz',
    #'/Users/pavlovic/Desktop/SALTACII_0068/Patella_Right/SALTACII_0068_V1_V2_Patella_Right_difference.nii.gz',
    #'/Users/pavlovic/Desktop/SALTACII_0068/Patella_Right/SALTACII_0068_V1_V3_Patella_Right_difference.nii.gz',
    #'/Users/pavlovic/Desktop/SALTACII_0068/Patella_Right/SALTACII_0068_V1_V4_Patella_Right_difference.nii.gz'
]
"""    

femur_paths = [
    '/Users/pavlovic/Desktop/SALTACII_0021/Femur_Left/SALTACII_0021_V1_Femur_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0021/Femur_Left/SALTACII_0021_V2_Femur_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0021/Femur_Left/SALTACII_0021_V3_Femur_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0021/Femur_Left/SALTACII_0021_V4_Femur_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0021/Femur_Right/SALTACII_0021_V1_Femur_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0021/Femur_Right/SALTACII_0021_V2_Femur_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0021/Femur_Right/SALTACII_0021_V3_Femur_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0021/Femur_Right/SALTACII_0021_V4_Femur_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0037/Femur_Left/SALTACII_0037_V1_Femur_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0037/Femur_Left/SALTACII_0037_V2_Femur_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0037/Femur_Left/SALTACII_0037_V3_Femur_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0037/Femur_Left/SALTACII_0037_V4_Femur_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0037/Femur_Right/SALTACII_0037_V1_Femur_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0037/Femur_Right/SALTACII_0037_V2_Femur_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0037/Femur_Right/SALTACII_0037_V3_Femur_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0037/Femur_Right/SALTACII_0037_V4_Femur_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0087/Femur_Left/SALTACII_0087_V1_Femur_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0087/Femur_Left/SALTACII_0087_V2_Femur_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0087/Femur_Left/SALTACII_0087_V3_Femur_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0087/Femur_Left/SALTACII_0087_V4_Femur_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0087/Femur_Right/SALTACII_0087_V1_Femur_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0087/Femur_Right/SALTACII_0087_V2_Femur_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0087/Femur_Right/SALTACII_0087_V3_Femur_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0087/Femur_Right/SALTACII_0087_V4_Femur_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0016/Femur_Left/SALTACII_0016_V1_Femur_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0016/Femur_Left/SALTACII_0016_V2_Femur_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0016/Femur_Left/SALTACII_0016_V3_Femur_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0016/Femur_Left/SALTACII_0016_V4_Femur_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0016/Femur_Right/SALTACII_0016_V1_Femur_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0016/Femur_Right/SALTACII_0016_V2_Femur_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0016/Femur_Right/SALTACII_0016_V3_Femur_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0016/Femur_Right/SALTACII_0016_V4_Femur_Right_common.nii.gz',     
    '/Users/pavlovic/Desktop/SALTACII_0008/Femur_Left/SALTACII_0008_V1_Femur_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0008/Femur_Left/SALTACII_0008_V2_Femur_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0008/Femur_Left/SALTACII_0008_V3_Femur_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0008/Femur_Left/SALTACII_0008_V4_Femur_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0008/Femur_Right/SALTACII_0008_V1_Femur_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0008/Femur_Right/SALTACII_0008_V2_Femur_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0008/Femur_Right/SALTACII_0008_V3_Femur_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0008/Femur_Right/SALTACII_0008_V4_Femur_Right_common.nii.gz', 
    
]

tibia_paths = [
    '/Users/pavlovic/Desktop/SALTACII_0021/Tibia_Left/SALTACII_0021_V1_Tibia_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0021/Tibia_Left/SALTACII_0021_V2_Tibia_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0021/Tibia_Left/SALTACII_0021_V3_Tibia_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0021/Tibia_Left/SALTACII_0021_V4_Tibia_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0021/Tibia_Right/SALTACII_0021_V1_Tibia_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0021/Tibia_Right/SALTACII_0021_V2_Tibia_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0021/Tibia_Right/SALTACII_0021_V3_Tibia_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0021/Tibia_Right/SALTACII_0021_V4_Tibia_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0037/Tibia_Left/SALTACII_0037_V1_Tibia_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0037/Tibia_Left/SALTACII_0037_V2_Tibia_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0037/Tibia_Left/SALTACII_0037_V3_Tibia_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0037/Tibia_Left/SALTACII_0037_V4_Tibia_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0037/Tibia_Right/SALTACII_0037_V1_Tibia_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0037/Tibia_Right/SALTACII_0037_V2_Tibia_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0037/Tibia_Right/SALTACII_0037_V3_Tibia_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0037/Tibia_Right/SALTACII_0037_V4_Tibia_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0087/Tibia_Left/SALTACII_0087_V1_Tibia_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0087/Tibia_Left/SALTACII_0087_V2_Tibia_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0087/Tibia_Left/SALTACII_0087_V3_Tibia_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0087/Tibia_Left/SALTACII_0087_V4_Tibia_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0087/Tibia_Right/SALTACII_0087_V1_Tibia_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0087/Tibia_Right/SALTACII_0087_V2_Tibia_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0087/Tibia_Right/SALTACII_0087_V3_Tibia_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0087/Tibia_Right/SALTACII_0087_V4_Tibia_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0008/Tibia_Left/SALTACII_0008_V1_Tibia_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0008/Tibia_Left/SALTACII_0008_V2_Tibia_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0008/Tibia_Left/SALTACII_0008_V3_Tibia_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0008/Tibia_Left/SALTACII_0008_V4_Tibia_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0008/Tibia_Right/SALTACII_0008_V1_Tibia_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0008/Tibia_Right/SALTACII_0008_V2_Tibia_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0008/Tibia_Right/SALTACII_0008_V3_Tibia_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0008/Tibia_Right/SALTACII_0008_V4_Tibia_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0016/Tibia_Left/SALTACII_0016_V1_Tibia_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0016/Tibia_Left/SALTACII_0016_V2_Tibia_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0016/Tibia_Left/SALTACII_0016_V3_Tibia_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0016/Tibia_Left/SALTACII_0016_V4_Tibia_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0016/Tibia_Right/SALTACII_0016_V1_Tibia_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0016/Tibia_Right/SALTACII_0016_V2_Tibia_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0016/Tibia_Right/SALTACII_0016_V3_Tibia_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0016/Tibia_Right/SALTACII_0016_V4_Tibia_Right_common.nii.gz', 
      
]

patella_paths = [
    '/Users/pavlovic/Desktop/SALTACII_0021/Patella_Left/SALTACII_0021_V1_Patella_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0021/Patella_Left/SALTACII_0021_V2_Patella_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0021/Patella_Left/SALTACII_0021_V3_Patella_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0021/Patella_Left/SALTACII_0021_V4_Patella_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0021/Patella_Right/SALTACII_0021_V1_Patella_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0021/Patella_Right/SALTACII_0021_V2_Patella_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0021/Patella_Right/SALTACII_0021_V3_Patella_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0021/Patella_Right/SALTACII_0021_V4_Patella_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0037/Patella_Left/SALTACII_0037_V1_Patella_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0037/Patella_Left/SALTACII_0037_V2_Patella_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0037/Patella_Left/SALTACII_0037_V3_Patella_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0037/Patella_Left/SALTACII_0037_V4_Patella_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0037/Patella_Right/SALTACII_0037_V1_Patella_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0037/Patella_Right/SALTACII_0037_V2_Patella_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0037/Patella_Right/SALTACII_0037_V3_Patella_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0037/Patella_Right/SALTACII_0037_V4_Patella_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0087/Patella_Left/SALTACII_0087_V1_Patella_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0087/Patella_Left/SALTACII_0087_V2_Patella_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0087/Patella_Left/SALTACII_0087_V3_Patella_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0087/Patella_Left/SALTACII_0087_V4_Patella_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0087/Patella_Right/SALTACII_0087_V1_Patella_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0087/Patella_Right/SALTACII_0087_V2_Patella_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0087/Patella_Right/SALTACII_0087_V3_Patella_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0087/Patella_Right/SALTACII_0087_V4_Patella_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0008/Patella_Left/SALTACII_0008_V1_Patella_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0008/Patella_Left/SALTACII_0008_V2_Patella_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0008/Patella_Left/SALTACII_0008_V3_Patella_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0008/Patella_Left/SALTACII_0008_V4_Patella_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0008/Patella_Right/SALTACII_0008_V1_Patella_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0008/Patella_Right/SALTACII_0008_V2_Patella_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0008/Patella_Right/SALTACII_0008_V3_Patella_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0008/Patella_Right/SALTACII_0008_V4_Patella_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0016/Patella_Left/SALTACII_0016_V1_Patella_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0016/Patella_Left/SALTACII_0016_V2_Patella_Left_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0016/Patella_Left/SALTACII_0016_V3_Patella_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0016/Patella_Left/SALTACII_0016_V4_Patella_Left_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0016/Patella_Right/SALTACII_0016_V1_Patella_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0016/Patella_Right/SALTACII_0016_V2_Patella_Right_common.nii.gz', 
    '/Users/pavlovic/Desktop/SALTACII_0016/Patella_Right/SALTACII_0016_V3_Patella_Right_common.nii.gz',
    '/Users/pavlovic/Desktop/SALTACII_0016/Patella_Right/SALTACII_0016_V4_Patella_Right_common.nii.gz', 
        
]

femur = analyze_ct_images(ct_image_paths=femur_paths, output_file='femur_statistics.csv')
tibia = analyze_ct_images(ct_image_paths=tibia_paths, output_file='tibia_statistics.csv')
patella = analyze_ct_images(ct_image_paths=patella_paths, output_file='patella_statistics.csv')

# Modify the Leg Condition column after the DataFrame is created
femur.loc[(femur['Participant'] == 'SALTACII_0021') & (femur['Leg Condition'] == 'Femur_Right'), 'Leg Condition'] = 'Injured'
femur.loc[(femur['Participant'] == 'SALTACII_0021') & (femur['Leg Condition'] == 'Femur_Left'), 'Leg Condition'] = 'Contralateral'
femur.loc[(femur['Participant'] == 'SALTACII_0037') & (femur['Leg Condition'] == 'Femur_Left'), 'Leg Condition'] = 'Injured'
femur.loc[(femur['Participant'] == 'SALTACII_0037') & (femur['Leg Condition'] == 'Femur_Right'), 'Leg Condition'] = 'Contralateral'
femur.loc[(femur['Participant'] == 'SALTACII_0087') & (femur['Leg Condition'] == 'Femur_Left'), 'Leg Condition'] = 'Injured'
femur.loc[(femur['Participant'] == 'SALTACII_0087') & (femur['Leg Condition'] == 'Femur_Right'), 'Leg Condition'] = 'Contralateral'
femur.loc[(femur['Participant'] == 'SALTACII_0008') & (femur['Leg Condition'] == 'Femur_Left'), 'Leg Condition'] = 'Injured'
femur.loc[(femur['Participant'] == 'SALTACII_0008') & (femur['Leg Condition'] == 'Femur_Right'), 'Leg Condition'] = 'Contralateral'
femur.loc[(femur['Participant'] == 'SALTACII_0016') & (femur['Leg Condition'] == 'Femur_Left'), 'Leg Condition'] = 'Injured'
femur.loc[(femur['Participant'] == 'SALTACII_0016') & (femur['Leg Condition'] == 'Femur_Right'), 'Leg Condition'] = 'Contralateral'

# Modify the Leg Condition column after the DataFrame is created
tibia.loc[(tibia['Participant'] == 'SALTACII_0021') & (tibia['Leg Condition'] == 'Tibia_Right'), 'Leg Condition'] = 'Injured'
tibia.loc[(tibia['Participant'] == 'SALTACII_0021') & (tibia['Leg Condition'] == 'Tibia_Left'), 'Leg Condition'] = 'Contralateral'
tibia.loc[(tibia['Participant'] == 'SALTACII_0037') & (tibia['Leg Condition'] == 'Tibia_Left'), 'Leg Condition'] = 'Injured'
tibia.loc[(tibia['Participant'] == 'SALTACII_0037') & (tibia['Leg Condition'] == 'Tibia_Right'), 'Leg Condition'] = 'Contralateral'
tibia.loc[(tibia['Participant'] == 'SALTACII_0087') & (tibia['Leg Condition'] == 'Tibia_Left'), 'Leg Condition'] = 'Injured'
tibia.loc[(tibia['Participant'] == 'SALTACII_0087') & (tibia['Leg Condition'] == 'Tibia_Right'), 'Leg Condition'] = 'Contralateral'
tibia.loc[(tibia['Participant'] == 'SALTACII_0008') & (tibia['Leg Condition'] == 'Tibia_Left'), 'Leg Condition'] = 'Injured'
tibia.loc[(tibia['Participant'] == 'SALTACII_0008') & (tibia['Leg Condition'] == 'Tibia_Right'), 'Leg Condition'] = 'Contralateral'
tibia.loc[(tibia['Participant'] == 'SALTACII_0016') & (tibia['Leg Condition'] == 'Tibia_Left'), 'Leg Condition'] = 'Injured'
tibia.loc[(tibia['Participant'] == 'SALTACII_0016') & (tibia['Leg Condition'] == 'Tibia_Right'), 'Leg Condition'] = 'Contralateral'

# Modify the Leg Condition column after the DataFrame is created
patella.loc[(patella['Participant'] == 'SALTACII_0021') & (patella['Leg Condition'] == 'Patella_Right'), 'Leg Condition'] = 'Injured'
patella.loc[(patella['Participant'] == 'SALTACII_0021') & (patella['Leg Condition'] == 'Patella_Left'), 'Leg Condition'] = 'Contralateral'
patella.loc[(patella['Participant'] == 'SALTACII_0037') & (patella['Leg Condition'] == 'Patella_Left'), 'Leg Condition'] = 'Injured'
patella.loc[(patella['Participant'] == 'SALTACII_0037') & (patella['Leg Condition'] == 'Patella_Right'), 'Leg Condition'] = 'Contralateral'
patella.loc[(patella['Participant'] == 'SALTACII_0087') & (patella['Leg Condition'] == 'Patella_Left'), 'Leg Condition'] = 'Injured'
patella.loc[(patella['Participant'] == 'SALTACII_0087') & (patella['Leg Condition'] == 'Patella_Right'), 'Leg Condition'] = 'Contralateral'
patella.loc[(patella['Participant'] == 'SALTACII_0008') & (patella['Leg Condition'] == 'Patella_Left'), 'Leg Condition'] = 'Injured'
patella.loc[(patella['Participant'] == 'SALTACII_0008') & (patella['Leg Condition'] == 'Patella_Right'), 'Leg Condition'] = 'Contralateral'
patella.loc[(patella['Participant'] == 'SALTACII_0016') & (patella['Leg Condition'] == 'Patella_Left'), 'Leg Condition'] = 'Injured'
patella.loc[(patella['Participant'] == 'SALTACII_0016') & (patella['Leg Condition'] == 'Patella_Right'), 'Leg Condition'] = 'Contralateral'

# Pivot the data to get each participant's aggregated density values across visits for each leg
pivot_injured_femur_mean = femur[femur['Leg Condition'] == 'Injured'].pivot(index='Participant', columns='Visit', values='Mean')
pivot_contralateral_femur_mean = femur[femur['Leg Condition'] == 'Contralateral'].pivot(index='Participant', columns='Visit', values='Mean')

# Pivot the data to get each participant's aggregated density values across visits for each leg
pivot_injured_femur_median = femur[femur['Leg Condition'] == 'Injured'].pivot(index='Participant', columns='Visit', values='Median')
pivot_contralateral_femur_median = femur[femur['Leg Condition'] == 'Contralateral'].pivot(index='Participant', columns='Visit', values='Median')

# Perform the Friedman test separately for the injured and uninjured legs
stat_injured_femur_mean, p_injured_femur_mean = friedmanchisquare(*pivot_injured_femur_mean.values.T)
stat_contralateral_femur_mean, p_contralateral_femur_mean = friedmanchisquare(*pivot_contralateral_femur_mean.values.T)
# Perform the Friedman test separately for the injured and uninjured legs
stat_injured_femur_median, p_injured_femur_median = friedmanchisquare(*pivot_injured_femur_median.values.T)
stat_contralateral_femur_median, p_contralateral_femur_median = friedmanchisquare(*pivot_contralateral_femur_median.values.T)

print(f'Friedman Test for Injured Femur Mean Density: Chi-square = {stat_injured_femur_mean}, p-value = {p_injured_femur_mean}')
print(f'Friedman Test for Contralateral Femur Mean Density: Chi-square = {stat_contralateral_femur_mean}, p-value = {p_contralateral_femur_mean}')
#print(f'Friedman Test for Injured Femur Median Density: Chi-square = {stat_injured_femur_median}, p-value = {p_injured_femur_median}')
#print(f'Friedman Test for Contralateral Femur Median Density: Chi-square = {stat_contralateral_femur_median}, p-value = {p_contralateral_femur_median}')

# Pivot the data to get each participant's aggregated density values across visits for each leg
pivot_injured_tibia_mean = tibia[tibia['Leg Condition'] == 'Injured'].pivot(index='Participant', columns='Visit', values='Mean')
pivot_contralateral_tibia_mean = tibia[tibia['Leg Condition'] == 'Contralateral'].pivot(index='Participant', columns='Visit', values='Mean')

# Pivot the data to get each participant's aggregated density values across visits for each leg
pivot_injured_tibia_median = tibia[tibia['Leg Condition'] == 'Injured'].pivot(index='Participant', columns='Visit', values='Median')
pivot_contralateral_tibia_median = tibia[tibia['Leg Condition'] == 'Contralateral'].pivot(index='Participant', columns='Visit', values='Median')

# Perform the Friedman test separately for the injured and uninjured legs
stat_injured_tibia_mean, p_injured_tibia_mean = friedmanchisquare(*pivot_injured_tibia_mean.values.T)
stat_contralateral_tibia_mean, p_contralateral_tibia_mean = friedmanchisquare(*pivot_contralateral_tibia_mean.values.T)
# Perform the Friedman test separately for the injured and uninjured legs
stat_injured_tibia_median, p_injured_tibia_median = friedmanchisquare(*pivot_injured_tibia_median.values.T)
stat_contralateral_tibia_median, p_contralateral_tibia_median = friedmanchisquare(*pivot_contralateral_tibia_median.values.T)

print(f'Friedman Test for Injured Tibia Mean Density: Chi-square = {stat_injured_tibia_mean}, p-value = {p_injured_tibia_mean}')
print(f'Friedman Test for Contralateral Tibia Mean Density: Chi-square = {stat_contralateral_tibia_mean}, p-value = {p_contralateral_tibia_mean}')
#print(f'Friedman Test for Injured Tibia Median Density: Chi-square = {stat_injured_tibia_median}, p-value = {p_injured_tibia_median}')
#print(f'Friedman Test for Contralateral Tibia Median Density: Chi-square = {stat_contralateral_tibia_median}, p-value = {p_contralateral_tibia_median}')

# Pivot the data to get each participant's aggregated density values across visits for each leg
pivot_injured_patella_mean = patella[patella['Leg Condition'] == 'Injured'].pivot(index='Participant', columns='Visit', values='Mean')
pivot_contralateral_patella_mean = patella[patella['Leg Condition'] == 'Contralateral'].pivot(index='Participant', columns='Visit', values='Mean')
# Pivot the data to get each participant's aggregated density values across visits for each leg
pivot_injured_patella_median = patella[patella['Leg Condition'] == 'Injured'].pivot(index='Participant', columns='Visit', values='Median')
pivot_contralateral_patella_median = patella[patella['Leg Condition'] == 'Contralateral'].pivot(index='Participant', columns='Visit', values='Median')

# Perform the Friedman test separately for the injured and uninjured legs
stat_injured_patella_mean, p_injured_patella_mean = friedmanchisquare(*pivot_injured_patella_mean.values.T)
stat_contralateral_patella_mean, p_contralateral_patella_mean = friedmanchisquare(*pivot_contralateral_patella_mean.values.T)
# Perform the Friedman test separately for the injured and uninjured legs
stat_injured_patella_median, p_injured_patella_median = friedmanchisquare(*pivot_injured_patella_median.values.T)
stat_contralateral_patella_median, p_contralateral_patella_median = friedmanchisquare(*pivot_contralateral_patella_median.values.T)

print(f'Friedman Test for Injured Patella Mean Density: Chi-square = {stat_injured_patella_mean}, p-value = {p_injured_patella_mean}')
print(f'Friedman Test for Contralateral Patella Mean Density: Chi-square = {stat_contralateral_patella_mean}, p-value = {p_contralateral_patella_mean}')
#print(f'Friedman Test for Injured Patella Median Density: Chi-square = {stat_injured_patella_median}, p-value = {p_injured_patella_median}')
#print(f'Friedman Test for Contralateral Patella Median Density: Chi-square = {stat_contralateral_patella_median}, p-value = {p_contralateral_patella_median}')

# Post hoc Nemenyi test
nemenyi_result_femur = sp.posthoc_nemenyi_friedman(pivot_injured_femur_mean.iloc[:, :])
print(nemenyi_result_femur)

# Post hoc Nemenyi test
nemenyi_result_tibia= sp.posthoc_nemenyi_friedman(pivot_injured_tibia_mean.iloc[:, :])
print(nemenyi_result_tibia)

# Post hoc Nemenyi test
nemenyi_result_patella = sp.posthoc_nemenyi_friedman(pivot_injured_patella_mean.iloc[:, :])
print(nemenyi_result_patella)

# Post hoc Dunn's test with Bonferroni correction
#dunn_result = sp.posthoc_dunn(pivot_injured_patella_mean.iloc[:, 1:], p_adjust='bonferroni')
#print(dunn_result)

"""
# Modify the Leg Condition column after the DataFrame is created
femur.loc[(femur['Participant'] == 'SALTACII_0004') & (femur['Leg Condition'] == 'Femur_Left'), 'Leg Condition'] = 'Injured'
femur.loc[(femur['Participant'] == 'SALTACII_0004') & (femur['Leg Condition'] == 'Femur_Right'), 'Leg Condition'] = 'Contralateral'
femur.loc[(femur['Participant'] == 'SALTACII_0012') & (femur['Leg Condition'] == 'Femur_Right'), 'Leg Condition'] = 'Injured'
femur.loc[(femur['Participant'] == 'SALTACII_0012') & (femur['Leg Condition'] == 'Femur_Left'), 'Leg Condition'] = 'Contralateral'
femur.loc[(femur['Participant'] == 'SALTACII_0030') & (femur['Leg Condition'] == 'Femur_Right'), 'Leg Condition'] = 'Injured'
femur.loc[(femur['Participant'] == 'SALTACII_0030') & (femur['Leg Condition'] == 'Femur_Left'), 'Leg Condition'] = 'Contralateral'
femur.loc[(femur['Participant'] == 'SALTACII_0068') & (femur['Leg Condition'] == 'Femur_Left'), 'Leg Condition'] = 'Injured'
femur.loc[(femur['Participant'] == 'SALTACII_0068') & (femur['Leg Condition'] == 'Femur_Right'), 'Leg Condition'] = 'Contralateral'

# Modify the Leg Condition column after the DataFrame is created
tibia.loc[(tibia['Participant'] == 'SALTACII_0004') & (tibia['Leg Condition'] == 'Tibia_Left'), 'Leg Condition'] = 'Injured'
tibia.loc[(tibia['Participant'] == 'SALTACII_0004') & (tibia['Leg Condition'] == 'Tibia_Right'), 'Leg Condition'] = 'Contralateral'
tibia.loc[(tibia['Participant'] == 'SALTACII_0012') & (tibia['Leg Condition'] == 'Tibia_Right'), 'Leg Condition'] = 'Injured'
tibia.loc[(tibia['Participant'] == 'SALTACII_0012') & (tibia['Leg Condition'] == 'Tibia_Left'), 'Leg Condition'] = 'Contralateral'
tibia.loc[(tibia['Participant'] == 'SALTACII_0030') & (tibia['Leg Condition'] == 'Tibia_Right'), 'Leg Condition'] = 'Injured'
tibia.loc[(tibia['Participant'] == 'SALTACII_0030') & (tibia['Leg Condition'] == 'Tibia_Left'), 'Leg Condition'] = 'Contralateral'
tibia.loc[(tibia['Participant'] == 'SALTACII_0068') & (tibia['Leg Condition'] == 'Tibia_Left'), 'Leg Condition'] = 'Injured'
tibia.loc[(tibia['Participant'] == 'SALTACII_0068') & (tibia['Leg Condition'] == 'Tibia_Right'), 'Leg Condition'] = 'Contralateral'

# Modify the Leg Condition column after the DataFrame is created
patella.loc[(patella['Participant'] == 'SALTACII_0004') & (patella['Leg Condition'] == 'Patella_Left'), 'Leg Condition'] = 'Injured'
patella.loc[(patella['Participant'] == 'SALTACII_0004') & (patella['Leg Condition'] == 'Patella_Right'), 'Leg Condition'] = 'Contralateral'
patella.loc[(patella['Participant'] == 'SALTACII_0012') & (patella['Leg Condition'] == 'Patella_Right'), 'Leg Condition'] = 'Injured'
patella.loc[(patella['Participant'] == 'SALTACII_0012') & (patella['Leg Condition'] == 'Patella_Left'), 'Leg Condition'] = 'Contralateral'
patella.loc[(patella['Participant'] == 'SALTACII_0030') & (patella['Leg Condition'] == 'Patella_Right'), 'Leg Condition'] = 'Injured'
patella.loc[(patella['Participant'] == 'SALTACII_0030') & (patella['Leg Condition'] == 'Patella_Left'), 'Leg Condition'] = 'Contralateral'
patella.loc[(patella['Participant'] == 'SALTACII_0068') & (patella['Leg Condition'] == 'Patella_Left'), 'Leg Condition'] = 'Injured'
patella.loc[(patella['Participant'] == 'SALTACII_0068') & (patella['Leg Condition'] == 'Patella_Right'), 'Leg Condition'] = 'Contralateral'

# Modify the Leg Condition column after the DataFrame is created
femur_diff.loc[(femur_diff['Participant'] == 'SALTACII_0004') & (femur_diff['Leg Condition'] == 'Femur_Left'), 'Leg Condition'] = 'Injured'
femur_diff.loc[(femur_diff['Participant'] == 'SALTACII_0004') & (femur_diff['Leg Condition'] == 'Femur_Right'), 'Leg Condition'] = 'Contralateral'
femur_diff.loc[(femur_diff['Participant'] == 'SALTACII_0012') & (femur_diff['Leg Condition'] == 'Femur_Right'), 'Leg Condition'] = 'Injured'
femur_diff.loc[(femur_diff['Participant'] == 'SALTACII_0012') & (femur_diff['Leg Condition'] == 'Femur_Left'), 'Leg Condition'] = 'Contralateral'
femur_diff.loc[(femur_diff['Participant'] == 'SALTACII_0030') & (femur_diff['Leg Condition'] == 'Femur_Right'), 'Leg Condition'] = 'Injured'
femur_diff.loc[(femur_diff['Participant'] == 'SALTACII_0030') & (femur_diff['Leg Condition'] == 'Femur_Left'), 'Leg Condition'] = 'Contralateral'
femur_diff.loc[(femur_diff['Participant'] == 'SALTACII_0068') & (femur_diff['Leg Condition'] == 'Femur_Left'), 'Leg Condition'] = 'Injured'
femur_diff.loc[(femur_diff['Participant'] == 'SALTACII_0068') & (femur_diff['Leg Condition'] == 'Femur_Right'), 'Leg Condition'] = 'Contralateral'

# Modify the Leg Condition column after the DataFrame is created
tibia_diff.loc[(tibia_diff['Participant'] == 'SALTACII_0004') & (tibia_diff['Leg Condition'] == 'Tibia_Left'), 'Leg Condition'] = 'Injured'
tibia_diff.loc[(tibia_diff['Participant'] == 'SALTACII_0004') & (tibia_diff['Leg Condition'] == 'Tibia_Right'), 'Leg Condition'] = 'Contralateral'
tibia_diff.loc[(tibia_diff['Participant'] == 'SALTACII_0012') & (tibia_diff['Leg Condition'] == 'Tibia_Right'), 'Leg Condition'] = 'Injured'
tibia_diff.loc[(tibia_diff['Participant'] == 'SALTACII_0012') & (tibia_diff['Leg Condition'] == 'Tibia_Left'), 'Leg Condition'] = 'Contralateral'
tibia_diff.loc[(tibia_diff['Participant'] == 'SALTACII_0030') & (tibia_diff['Leg Condition'] == 'Tibia_Right'), 'Leg Condition'] = 'Injured'
tibia_diff.loc[(tibia_diff['Participant'] == 'SALTACII_0030') & (tibia_diff['Leg Condition'] == 'Tibia_Left'), 'Leg Condition'] = 'Contralateral'
tibia_diff.loc[(tibia_diff['Participant'] == 'SALTACII_0068') & (tibia_diff['Leg Condition'] == 'Tibia_Left'), 'Leg Condition'] = 'Injured'
tibia_diff.loc[(tibia_diff['Participant'] == 'SALTACII_0068') & (tibia_diff['Leg Condition'] == 'Tibia_Right'), 'Leg Condition'] = 'Contralateral'

# Modify the Leg Condition column after the DataFrame is created
patella_diff.loc[(patella_diff['Participant'] == 'SALTACII_0004') & (patella_diff['Leg Condition'] == 'Patella_Left'), 'Leg Condition'] = 'Injured'
patella_diff.loc[(patella_diff['Participant'] == 'SALTACII_0004') & (patella_diff['Leg Condition'] == 'Patella_Right'), 'Leg Condition'] = 'Contralateral'
patella_diff.loc[(patella_diff['Participant'] == 'SALTACII_0012') & (patella_diff['Leg Condition'] == 'Patella_Right'), 'Leg Condition'] = 'Injured'
patella_diff.loc[(patella_diff['Participant'] == 'SALTACII_0012') & (patella_diff['Leg Condition'] == 'Patella_Left'), 'Leg Condition'] = 'Contralateral'
patella_diff.loc[(patella_diff['Participant'] == 'SALTACII_0030') & (patella_diff['Leg Condition'] == 'Patella_Right'), 'Leg Condition'] = 'Injured'
patella_diff.loc[(patella_diff['Participant'] == 'SALTACII_0030') & (patella_diff['Leg Condition'] == 'Patella_Left'), 'Leg Condition'] = 'Contralateral'
patella_diff.loc[(patella_diff['Participant'] == 'SALTACII_0068') & (patella_diff['Leg Condition'] == 'Patella_Left'), 'Leg Condition'] = 'Injured'
patella_diff.loc[(patella_diff['Participant'] == 'SALTACII_0068') & (patella_diff['Leg Condition'] == 'Patella_Right'), 'Leg Condition'] = 'Contralateral'

# Pivot the data to get each participant's aggregated density values across visits for each leg
pivot_injured_femur_mean = femur[femur['Leg Condition'] == 'Injured'].pivot(index='Participant', columns='Visit', values='Mean')
pivot_contralateral_femur_mean = femur[femur['Leg Condition'] == 'Contralateral'].pivot(index='Participant', columns='Visit', values='Mean')

# Pivot the data to get each participant's aggregated density values across visits for each leg
pivot_injured_femur_median = femur[femur['Leg Condition'] == 'Injured'].pivot(index='Participant', columns='Visit', values='Median')
pivot_contralateral_femur_median = femur[femur['Leg Condition'] == 'Contralateral'].pivot(index='Participant', columns='Visit', values='Median')

# Perform the Friedman test separately for the injured and uninjured legs
stat_injured_femur_mean, p_injured_femur_mean = friedmanchisquare(*pivot_injured_femur_mean.values.T)
stat_contralateral_femur_mean, p_contralateral_femur_mean = friedmanchisquare(*pivot_contralateral_femur_mean.values.T)
# Perform the Friedman test separately for the injured and uninjured legs
stat_injured_femur_median, p_injured_femur_median = friedmanchisquare(*pivot_injured_femur_median.values.T)
stat_contralateral_femur_median, p_contralateral_femur_median = friedmanchisquare(*pivot_contralateral_femur_median.values.T)

#print(f'Friedman Test for Injured Femur Mean Density: Chi-square = {stat_injured_femur_mean}, p-value = {p_injured_femur_mean}')
#print(f'Friedman Test for Contralateral Femur Mean Density: Chi-square = {stat_contralateral_femur_mean}, p-value = {p_contralateral_femur_mean}')
print(f'Friedman Test for Injured Femur Median Density: Chi-square = {stat_injured_femur_median}, p-value = {p_injured_femur_median}')
print(f'Friedman Test for Contralateral Femur Median Density: Chi-square = {stat_contralateral_femur_median}, p-value = {p_contralateral_femur_median}')

# Pivot the data to get each participant's aggregated density values across visits for each leg
pivot_injured_tibia_mean = tibia[tibia['Leg Condition'] == 'Injured'].pivot(index='Participant', columns='Visit', values='Mean')
pivot_contralateral_tibia_mean = tibia[tibia['Leg Condition'] == 'Contralateral'].pivot(index='Participant', columns='Visit', values='Mean')

# Pivot the data to get each participant's aggregated density values across visits for each leg
pivot_injured_tibia_median = tibia[tibia['Leg Condition'] == 'Injured'].pivot(index='Participant', columns='Visit', values='Median')
pivot_contralateral_tibia_median = tibia[tibia['Leg Condition'] == 'Contralateral'].pivot(index='Participant', columns='Visit', values='Median')

# Perform the Friedman test separately for the injured and uninjured legs
stat_injured_tibia_mean, p_injured_tibia_mean = friedmanchisquare(*pivot_injured_tibia_mean.values.T)
stat_contralateral_tibia_mean, p_contralateral_tibia_mean = friedmanchisquare(*pivot_contralateral_tibia_mean.values.T)
# Perform the Friedman test separately for the injured and uninjured legs
stat_injured_tibia_median, p_injured_tibia_median = friedmanchisquare(*pivot_injured_tibia_median.values.T)
stat_contralateral_tibia_median, p_contralateral_tibia_median = friedmanchisquare(*pivot_contralateral_tibia_median.values.T)

#print(f'Friedman Test for Injured Tibia Mean Density: Chi-square = {stat_injured_tibia_mean}, p-value = {p_injured_tibia_mean}')
#print(f'Friedman Test for Contralateral Tibia Mean Density: Chi-square = {stat_contralateral_tibia_mean}, p-value = {p_contralateral_tibia_mean}')
print(f'Friedman Test for Injured Tibia Median Density: Chi-square = {stat_injured_tibia_median}, p-value = {p_injured_tibia_median}')
print(f'Friedman Test for Contralateral Tibia Median Density: Chi-square = {stat_contralateral_tibia_median}, p-value = {p_contralateral_tibia_median}')

# Pivot the data to get each participant's aggregated density values across visits for each leg
pivot_injured_patella_mean = patella[patella['Leg Condition'] == 'Injured'].pivot(index='Participant', columns='Visit', values='Mean')
pivot_contralateral_patella_mean = patella[patella['Leg Condition'] == 'Contralateral'].pivot(index='Participant', columns='Visit', values='Mean')
# Pivot the data to get each participant's aggregated density values across visits for each leg
pivot_injured_patella_median = patella[patella['Leg Condition'] == 'Injured'].pivot(index='Participant', columns='Visit', values='Median')
pivot_contralateral_patella_median = patella[patella['Leg Condition'] == 'Contralateral'].pivot(index='Participant', columns='Visit', values='Median')

# Perform the Friedman test separately for the injured and uninjured legs
stat_injured_patella_mean, p_injured_patella_mean = friedmanchisquare(*pivot_injured_patella_mean.values.T)
stat_contralateral_patella_mean, p_contralateral_patella_mean = friedmanchisquare(*pivot_contralateral_patella_mean.values.T)
# Perform the Friedman test separately for the injured and uninjured legs
stat_injured_patella_median, p_injured_patella_median = friedmanchisquare(*pivot_injured_patella_median.values.T)
stat_contralateral_patella_median, p_contralateral_patella_median = friedmanchisquare(*pivot_contralateral_patella_median.values.T)

#print(f'Friedman Test for Injured Patella Median Density: Chi-square = {stat_injured_patella_mean}, p-value = {p_injured_patella_mean}')
#print(f'Friedman Test for Contralateral Patella Mean Density: Chi-square = {stat_contralateral_patella_mean}, p-value = {p_contralateral_patella_mean}')
print(f'Friedman Test for Injured Patella Median Density: Chi-square = {stat_injured_patella_median}, p-value = {p_injured_patella_median}')
print(f'Friedman Test for Contralateral Patella Median Density: Chi-square = {stat_contralateral_patella_median}, p-value = {p_contralateral_patella_median}')


# Pivot the data to get each participant's aggregated density values across visits for each leg
pivot_injured_femur_diff_mean = femur_diff[femur_diff['Leg Condition'] == 'Injured'].pivot(index='Participant', columns='Visit', values='Mean')
pivot_contralateral_femur_diff_mean = femur_diff[femur_diff['Leg Condition'] == 'Contralateral'].pivot(index='Participant', columns='Visit', values='Mean')

# Pivot the data to get each participant's aggregated density values across visits for each leg
pivot_injured_femur_diff_median = femur_diff[femur_diff['Leg Condition'] == 'Injured'].pivot(index='Participant', columns='Visit', values='Median')
pivot_contralateral_femur_diff_median = femur_diff[femur_diff['Leg Condition'] == 'Contralateral'].pivot(index='Participant', columns='Visit', values='Median')

# Perform the Friedman test separately for the injured and uninjured legs
stat_injured_femur_diff_mean, p_injured_femur_diff_mean = friedmanchisquare(*pivot_injured_femur_diff_mean.values.T)
stat_contralateral_femur_diff_mean, p_contralateral_femur_diff_mean = friedmanchisquare(*pivot_contralateral_femur_diff_mean.values.T)
# Perform the Friedman test separately for the injured and uninjured legs
stat_injured_femur_diff_median, p_injured_femur_diff_median = friedmanchisquare(*pivot_injured_femur_diff_median.values.T)
stat_contralateral_femur_diff_median, p_contralateral_femur_diff_median = friedmanchisquare(*pivot_contralateral_femur_diff_median.values.T)

print(f'Friedman Test for Injured Femur Difference Mean Density: Chi-square = {stat_injured_femur_diff_mean}, p-value = {p_injured_femur_diff_mean}')
print(f'Friedman Test for Contralateral Femur Difference Mean Density: Chi-square = {stat_contralateral_femur_diff_mean}, p-value = {p_contralateral_femur_diff_mean}')
print(f'Friedman Test for Injured Femur Difference Median Density: Chi-square = {stat_injured_femur_diff_median}, p-value = {p_injured_femur_diff_median}')
print(f'Friedman Test for Contralateral Femur Difference Median Density: Chi-square = {stat_contralateral_femur_diff_median}, p-value = {p_contralateral_femur_diff_median}')

# Pivot the data to get each participant's aggregated density values across visits for each leg
pivot_injured_tibia_diff_mean = tibia_diff[tibia_diff['Leg Condition'] == 'Injured'].pivot(index='Participant', columns='Visit', values='Mean')
pivot_contralateral_tibia_diff_mean = tibia_diff[tibia_diff['Leg Condition'] == 'Contralateral'].pivot(index='Participant', columns='Visit', values='Mean')

# Pivot the data to get each participant's aggregated density values across visits for each leg
pivot_injured_tibia_diff_median = tibia_diff[tibia_diff['Leg Condition'] == 'Injured'].pivot(index='Participant', columns='Visit', values='Median')
pivot_contralateral_tibia_diff_median = tibia_diff[tibia_diff['Leg Condition'] == 'Contralateral'].pivot(index='Participant', columns='Visit', values='Median')

# Perform the Friedman test separately for the injured and uninjured legs
stat_injured_tibia_diff_mean, p_injured_tibia_diff_mean = friedmanchisquare(*pivot_injured_tibia_diff_mean.values.T)
stat_contralateral_tibia_diff_mean, p_contralateral_tibia_diff_mean = friedmanchisquare(*pivot_contralateral_tibia_diff_mean.values.T)
# Perform the Friedman test separately for the injured and uninjured legs
stat_injured_tibia_diff_median, p_injured_tibia_diff_median = friedmanchisquare(*pivot_injured_tibia_diff_median.values.T)
stat_contralateral_tibia_diff_median, p_contralateral_tibia_diff_median = friedmanchisquare(*pivot_contralateral_tibia_diff_median.values.T)

print(f'Friedman Test for Injured Tibia Difference Mean Density: Chi-square = {stat_injured_tibia_diff_mean}, p-value = {p_injured_tibia_diff_mean}')
print(f'Friedman Test for Contralateral Tibia Difference Mean Density: Chi-square = {stat_contralateral_tibia_diff_mean}, p-value = {p_contralateral_tibia_diff_mean}')
print(f'Friedman Test for Injured Tibia Difference Median Density: Chi-square = {stat_injured_tibia_diff_median}, p-value = {p_injured_tibia_diff_median}')
print(f'Friedman Test for Contralateral Tibia Difference Median Density: Chi-square = {stat_contralateral_tibia_diff_median}, p-value = {p_contralateral_tibia_diff_median}')

# Pivot the data to get each participant's aggregated density values across visits for each leg
pivot_injured_patella_diff_mean = patella_diff[patella_diff['Leg Condition'] == 'Injured'].pivot(index='Participant', columns='Visit', values='Mean')
pivot_contralateral_patella_diff_mean = patella_diff[patella_diff['Leg Condition'] == 'Contralateral'].pivot(index='Participant', columns='Visit', values='Mean')
# Pivot the data to get each participant's aggregated density values across visits for each leg
pivot_injured_patella_diff_median = patella_diff[patella_diff['Leg Condition'] == 'Injured'].pivot(index='Participant', columns='Visit', values='Median')
pivot_contralateral_patella_diff_median = patella_diff[patella_diff['Leg Condition'] == 'Contralateral'].pivot(index='Participant', columns='Visit', values='Median')

# Perform the Friedman test separately for the injured and uninjured legs
stat_injured_patella_diff_mean, p_injured_patella_diff_mean = friedmanchisquare(*pivot_injured_patella_diff_mean.values.T)
stat_contralateral_patella_diff_mean, p_contralateral_patella_diff_mean = friedmanchisquare(*pivot_contralateral_patella_diff_mean.values.T)
# Perform the Friedman test separately for the injured and uninjured legs
stat_injured_patella_diff_median, p_injured_patella_diff_median = friedmanchisquare(*pivot_injured_patella_diff_median.values.T)
stat_contralateral_patella_diff_median, p_contralateral_patella_diff_median = friedmanchisquare(*pivot_contralateral_patella_diff_median.values.T)

print(f'Friedman Test for Injured Patella Difference Medan Density: Chi-square = {stat_injured_patella_diff_mean}, p-value = {p_injured_patella_diff_mean}')
print(f'Friedman Test for Contralateral Patella Difference Mean Density: Chi-square = {stat_contralateral_patella_diff_mean}, p-value = {p_contralateral_patella_diff_mean}')
print(f'Friedman Test for Injured Patella Difference Median Density: Chi-square = {stat_injured_patella_diff_median}, p-value = {p_injured_patella_diff_median}')
print(f'Friedman Test for Contralateral Patella Difference Median Density: Chi-square = {stat_contralateral_patella_diff_median}, p-value = {p_contralateral_patella_diff_median}')

"""


import matplotlib.pyplot as plt
import seaborn as sns

# Plot spaghetti plots for each subject and leg
plt.figure(figsize=(10, 6))
sns.lineplot(data=femur, x='Visit', y='Mean', hue='Participant', style='Leg Condition', markers=True, dashes=True)
plt.title('Spaghetti Plot of Mean Femur Density Over Time')
plt.xlabel('Visit')
plt.ylabel('Bone Density')
plt.legend(loc='upper right')
plt.grid(True)
plt.show()

# Plot spaghetti plots for each subject and leg
plt.figure(figsize=(10, 6))
sns.lineplot(data=tibia, x='Visit', y='Mean', hue='Participant', style='Leg Condition', markers=True, dashes=True)
plt.title('Spaghetti Plot of Mean Tibia Density Over Time')
plt.xlabel('Visit')
plt.ylabel('Bone Density')
plt.legend(loc='upper right')
plt.grid(True)
plt.show()

# Plot spaghetti plots for each subject and leg
plt.figure(figsize=(10, 6))
sns.lineplot(data=patella, x='Visit', y='Mean', hue='Participant', style='Leg Condition', markers=True, dashes=True)
plt.title('Spaghetti Plot of Mean Patella Density Over Time')
plt.xlabel('Visit')
plt.ylabel('Bone Density')
plt.legend(loc='upper right')
plt.grid(True)
plt.show()
'''
# Create a 2x2 grid of plots
fig, axes = plt.subplots(2, 2, figsize=(12, 10), gridspec_kw={'height_ratios': [1, 1]})

# Plot femur density in the top-left cell
sns.lineplot(data=femur, x='Visit', y='Median', hue='Participant', style='Leg Condition', markers=True, dashes=False, ax=axes[0, 0], legend=False)
axes[0, 0].set_title('Femur Density Over Time')
axes[0, 0].set_xlabel('Visit')
axes[0, 0].set_ylabel('Density')
axes[0, 0].grid(True)

# Plot tibial density in the top-right cell
sns.lineplot(data=tibia, x='Visit', y='Median', hue='Participant', style='Leg Condition', markers=True, dashes=False, ax=axes[0, 1], legend=False)
axes[0, 1].set_title('Tibial Density Over Time')
axes[0, 1].set_xlabel('Visit')
axes[0, 1].set_ylabel('Density')
axes[0, 1].grid(True)

# Plot patellar density in the bottom-left cell
sns.lineplot(data=patella, x='Visit', y='Median', hue='Participant', style='Leg Condition', markers=True, dashes=False, ax=axes[1, 0], legend=False)
axes[1, 0].set_title('Patellar Density Over Time')
axes[1, 0].set_xlabel('Visit')
axes[1, 0].set_ylabel('Density')
axes[1, 0].grid(True)


# The bottom-right cell for legend
axes[1, 1].axis('off')  # Hide the axes

# Add a shared legend
handles, labels = axes[0, 0].get_legend_handles_labels()  # Get handles and labels from one of the plots
fig.legend(handles, labels, loc='right', bbox_to_anchor=(0.5, 0.5), ncol=len(labels)//2, title='Participant', fontsize='small')

plt.tight_layout(rect=[0, 0, 1, 0.9])  # Adjust layout to make room for the legend
plt.show()
'''
# Pivot the data for heatmap
heatmap_data = femur.pivot_table(index='Visit', columns='Leg Condition', values='Mean', aggfunc=np.mean)

# Plot the heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(heatmap_data, annot=True, cmap='coolwarm', fmt=".1f", linewidths=.5)
plt.title('Heatmap of Femur Density Over Time')
plt.xlabel('Leg')
plt.ylabel('Visit')
plt.show()

# Pivot the data for heatmap
heatmap_data = tibia.pivot_table(index='Visit', columns='Leg Condition', values='Mean', aggfunc=np.mean)

# Plot the heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(heatmap_data, annot=True, cmap='coolwarm', fmt=".1f", linewidths=.5)
plt.title('Heatmap of Tibia Density Over Time')
plt.xlabel('Leg')
plt.ylabel('Visit')
plt.show()

# Pivot the data for heatmap
heatmap_data = patella.pivot_table(index='Visit', columns='Leg Condition', values='Mean', aggfunc=np.mean)

# Plot the heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(heatmap_data, annot=True, cmap='coolwarm', fmt=".1f", linewidths=.5)
plt.title('Heatmap of Patella Density Over Time')
plt.xlabel('Leg')
plt.ylabel('Visit')
plt.show()

age_SALTACII_0021 = 55.190729446874336
age_SALTACII_0037 = 35.423154935876
age_SALTACII_0087 = 51.72716300357525
age_SALTACII_0008 = 41.4657157003
age_SALTACII_0016 = 48.389768441515 

print(np.mean([age_SALTACII_0021,age_SALTACII_0037, age_SALTACII_0087, age_SALTACII_0008, age_SALTACII_0016]))
print(np.std([age_SALTACII_0021,age_SALTACII_0037, age_SALTACII_0087, age_SALTACII_0008, age_SALTACII_0016]))

"""
age_SALTACII_0004 = 47.51101437173
age_SALTACII_0012 = 39.434188701114
age_SALTACII_0030 = 35.86658179154945
age_SALTACII_0068 = 36.82484924399543

print(np.mean([age_SALTACII_0004,age_SALTACII_0012, age_SALTACII_0030,age_SALTACII_0068]))
print(np.std([age_SALTACII_0004,age_SALTACII_0012, age_SALTACII_0030,age_SALTACII_0068]))
"""
