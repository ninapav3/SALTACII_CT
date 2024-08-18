#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 17:04:14 2024

@author: pavlovic
"""

import SimpleITK as sitk
import argparse
import vtk
import os
import numpy as np

def create_reader(fn):
    if fn.endswith('.nii') or fn.endswith('nii.gz'):
        reader = vtk.vtkNIFTIImageReader()
        reader.SetFileName(fn)
    elif fn.endswith('.dcm'):
        reader = vtk.vtkDICOMImageReader()
        reader.SetDirectoryName(os.path.dirname(fn))
    elif fn.endswith('.obj'):
        reader = vtk.vtkOBJReader()
        reader.SetFileName(fn)
    else:
        raise ValueError(f"Invalid image filename given (only *.dcm, *.nii, and *.obj supported): {fn}")
    
    reader.Update()
    return reader

V1 = create_reader('/Users/pavlovic/Desktop/SALTACII_0004/Femur_Left/SALTACII_0004_V1_Femur_Left_common.nii.gz')
V2 = create_reader('/Users/pavlovic/Desktop/SALTACII_0004/Femur_Left/SALTACII_0004_V2_Femur_Left_common.nii.gz')
V3 = create_reader('/Users/pavlovic/Desktop/SALTACII_0004/Femur_Left/SALTACII_0004_V3_Femur_Left_common.nii.gz')
V4 = create_reader('/Users/pavlovic/Desktop/SALTACII_0004/Femur_Left/SALTACII_0004_V4_Femur_Left_common.nii.gz')
VS = create_reader('/Users/pavlovic/Desktop/SALTACII_0004/Femur_Left/SALTACII_0004_VS_Femur_Left_common.nii.gz')

difference_V1_V2 = create_reader('/Users/pavlovic/Desktop/SALTACII_0004/Femur_Left/SALTACII_0004_V1_V2_Femur_Left_difference.nii.gz')
#difference_V1_V3 = create_reader('/Users/pavlovic/Desktop/SALTACII_0004/Femur_Left/SALTACII_0004_V1_V3_Femur_Left_difference.nii.gz')
#difference_V1_V4 = create_reader('/Users/pavlovic/Desktop/SALTACII_0004/Femur_Left/SALTACII_0004_V1_V4_Femur_Left_difference.nii.gz')
#difference_V1_VS = create_reader('/Users/pavlovic/Desktop/SALTACII_0004/Femur_Left/SALTACII_0004_V1_VS_Femur_Left_difference.nii.gz')

mask = create_reader('/Users/pavlovic/Desktop/SALTACII_0004/Femur_Left/SALTACII_0004_V1_Femur_Left_cropped_common_mask.nii.gz')

"""parser = argparse.ArgumentParser(description="Process and save masked images based on labels.")

# Define command-line arguments
parser.add_argument('main_image_path', type=str, help='Path to the main image')
parser.add_argument('mask_image_path', type=str, help='Path to the mask image')
parser.add_argument('--kernel_radius', type=int, nargs='+', default=[1, 1, 1], help='Kernel radius for dilation (e.g., 2 2 2)')
parser.add_argument('--label_of_interest', type=int, help='Specific label to process (optional)')

# Parse arguments
args = parser.parse_args()"""

voxel_dimensions = V1.GetOutput().GetSpacing()

# Calculate voxel volume in mm³
voxel_volume_mm3 = np.prod(voxel_dimensions)

# Convert voxel volume to cm³
voxel_volume_cm3 = voxel_volume_mm3 / 1000.0

print(voxel_volume_cm3)

# Convert binary segmentation into stencil
mask_stencil = vtk.vtkImageToImageStencil()
mask_stencil.SetInputData(V1.GetOutput())
mask_stencil.ThresholdBetween(1,1)
mask_stencil.Update()

extract_results = vtk.vtkImageAccumulate()
extract_results.SetInputData(V1.GetOutput())

# Set foreground stencil
extract_results.SetStencilData(mask_stencil.GetOutput())
extract_results.Update()

mean_results = extract_results.GetMean()
sd_results = extract_results.GetStandardDeviation()
max_results = extract_results.GetMax()
min_results = extract_results.GetMin()
voxel_count_results = extract_results.GetVoxelCount()

print("Mean: ", mean_results[0])
print("Standard Deviation: ", sd_results[0])
print("Maximum: ", max_results[0])
print("Minimum: ", min_results[0])
print("Voxel Count: ", voxel_count_results)

extract_results = vtk.vtkImageAccumulate()
extract_results.SetInputData(V2.GetOutput())

# Set foreground stencil
extract_results.SetStencilData(mask_stencil.GetOutput())
extract_results.Update()

mean_results = extract_results.GetMean()
sd_results = extract_results.GetStandardDeviation()
max_results = extract_results.GetMax()
min_results = extract_results.GetMin()
voxel_count_results = extract_results.GetVoxelCount()

print("Mean: ", mean_results[0])
print("Standard Deviation: ", sd_results[0])
print("Maximum: ", max_results[0])
print("Minimum: ", min_results[0])
print("Voxel Count: ", voxel_count_results)

extract_results = vtk.vtkImageAccumulate()
extract_results.SetInputData(difference_V1_V2.GetOutput())

# Set foreground stencil
extract_results.SetStencilData(mask_stencil.GetOutput())
extract_results.Update()

mean_results = extract_results.GetMean()
sd_results = extract_results.GetStandardDeviation()
max_results = extract_results.GetMax()
min_results = extract_results.GetMin()
voxel_count_results = extract_results.GetVoxelCount()

print("Mean: ", mean_results[0])
print("Standard Deviation: ", sd_results[0])
print("Maximum: ", max_results[0])
print("Minimum: ", min_results[0])
print("Voxel Count: ", voxel_count_results)

# Read images
V1 = sitk.ReadImage('/Users/pavlovic/Desktop/SALTACII_0004/Femur_Left/SALTACII_0004_V1_Femur_Left_common.nii.gz')
VS = sitk.ReadImage('/Users/pavlovic/Desktop/SALTACII_0004/Femur_Left/SALTACII_0004_VS_Femur_Left_common.nii.gz')
V2 = sitk.ReadImage('/Users/pavlovic/Desktop/SALTACII_0004/Femur_Left/SALTACII_0004_V2_Femur_Left_common.nii.gz')
V3 = sitk.ReadImage('/Users/pavlovic/Desktop/SALTACII_0004/Femur_Left/SALTACII_0004_V3_Femur_Left_common.nii.gz')
V4 = sitk.ReadImage('/Users/pavlovic/Desktop/SALTACII_0004/Femur_Left/SALTACII_0004_V4_Femur_Left_common.nii.gz')

difference_V1_V2 = sitk.ReadImage('/Users/pavlovic/Desktop/SALTACII_0004/Femur_Left/SALTACII_0004_V1_V2_Femur_Left_difference.nii.gz')

columns = ['Visit', 'Mean', 'StdDev', 'Max', 'Min', 'Median', 'IQR']
df = pd.DataFrame(columns=columns)

V1_array = sitk.GetArrayFromImage(V1)

# Extract all non-zero values
V1_non_zero_values = V1_array[V1_array != 0]
V1_mean_non_zero = np.mean(V1_non_zero_values)
V1_median_non_zero = np.median(V1_non_zero_values)
V1_std_non_zero = np.std(V1_non_zero_values)
V1_max_non_zero = np.max(V1_non_zero_values)
V1_min_non_zero = np.min(V1_non_zero_values)
V1_25p_non_zero = np.percentile(V1_non_zero_values, 25)
V1_75p_non_zero = np.percentile(V1_non_zero_values, 75)

dict = {'mean': V1_mean_non_zero, VS_mean_non_zero, V2_mean_non_zero,V3_mean_non_zero, V4_mean_non_zero}

# Adding a new row using loc
#df.loc[len(df)] = ['David', 40, 'San Francisco']

V2_array = sitk.GetArrayFromImage(V2)
V2_array[V2_array ==0] =np.nan

diff_array = sitk.GetArrayFromImage(difference_V1_V2)
diff_array[diff_array ==0] =np.nan

voxel_count = np.count_nonzero(V1_array)

BMD_total = V1_array.sum()  
BMD_AVG = BMD_total / voxel_count  # [mg/cc K2HPO4]# [mg/cc K2HPO4]

masked_V1 = np.nonzero(V1_array)
V1_array[V1_array ==0] =np.nan

print("Baseline Mean: ", np.nanmean(V1_array))
print("Baseline Standard Deviation: ", np.nanstd(V1_array))
print("Baseline Maximum: ", np.nanmax(V1_array))
print("Baseline Minimum: ", np.nanmin(V1_array))
print("Baseline 25th percentile: ", np.nanpercentile(V1_array, 25))
print("Baseline 75th percentile: ", np.nanpercentile(V1_array, 75))
print("Baseline Median: ", np.nanmedian(V1_array))  

print("Followup Mean: ", np.nanmean(V2_array))
print("Followup Standard Deviation: ", np.nanstd(V2_array))
print("Followup Maximum: ", np.nanmax(V2_array))
print("Followup Minimum: ", np.nanmin(V2_array))
print("Followup 25th percentile: ", np.nanpercentile(V2_array, 25))
print("Followup 75th percentile: ", np.nanpercentile(V2_array, 75))
print("Followup Median: ", np.nanmedian(V2_array))

print("Diff Mean: ", np.nanmean(diff_array))
print("Diff Standard Deviation: ", np.nanstd(diff_array))
print("Diff Maximum: ", np.nanmax(diff_array))
print("Diff Minimum: ", np.nanmin(diff_array))
print("Diff 25th percentile: ", np.nanpercentile(diff_array, 25))
print("Diff 75th percentile: ", np.nanpercentile(diff_array, 75))
print("Diff Median: ", np.nanmedian(diff_array))

# Create a binary mask where non-zero pixels are set to 1, and zero pixels are set to 0
binary_mask = sitk.Cast(V1 != 0, sitk.sitkUInt8)

# Apply the binary mask to remove zero values from the image
masked_V1 = sitk.Mask(V1, binary_mask)

stats = sitk.StatisticsImageFilter()
stats.Execute(masked_V1)

# Retrieve the statistics
min_intensity = stats.GetMinimum()
max_intensity = stats.GetMaximum()
mean_intensity = stats.GetMean()
std_dev_intensity = stats.GetSigma()  # This returns the standard deviation
variance = stats.GetVariance()
sum_intensity = stats.GetSum()

# Print the results
print(f"Minimum Intensity: {min_intensity}")
print(f"Maximum Intensity: {max_intensity}")
print(f"Mean Intensity: {mean_intensity}")
print(f"Standard Deviation: {std_dev_intensity}")
print(f"Variance: {variance}")
print(f"Sum of Intensities: {sum_intensity}")
