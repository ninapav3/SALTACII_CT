#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 18:49:25 2024

@author: pavlovic
"""
import vtk
import argparse
import os

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

def main():
    parser = argparse.ArgumentParser(description='Volume Rendering with VTK.')
    parser.add_argument('difference_path', type=str, 
                        help='Path to the difference image file (.nii, .nii.gz, .dcm, or .obj)')
    parser.add_argument('--elevation', type=float, default=0,
                        help='Elevation angle for the camera (default: 0)')
    parser.add_argument('--azimuth', type=float, default=0,
                        help='Azimuth angle for the camera (default: 0)')
    args = parser.parse_args()

    difference = create_reader(args.difference_path)
    elevation = args.elevation
    azimuth = args.azimuth
    ibounds = difference.GetOutput().GetBounds()

    scalar_opacity = vtk.vtkPiecewiseFunction()
    scalar_opacity.AddPoint(-1000, 1.0)
    scalar_opacity.AddPoint(0, 0.0)
    scalar_opacity.AddPoint(1000, 1.0)

    color_transfer_function = vtk.vtkColorTransferFunction()
    color_transfer_function.SetColorSpaceToDiverging()
    color_transfer_function.AddRGBPoint(0, 1.0, 1.0, 1.0)
    color_transfer_function.AddRGBPoint(-200, 0.0, 0.0, 1.0)
    color_transfer_function.AddRGBPoint(200, *vtk.vtkNamedColors().GetColor3d('cobalt_green'))
    color_transfer_function.GetTable(-1000, 1000, 1)
    color_transfer_function.SetNanColor(1.0, 1.0, 1.0)

    mapper = vtk.vtkFixedPointVolumeRayCastMapper()
    mapper.SetInputData(difference.GetOutput())

    color_bar_mapper = vtk.vtkPolyDataMapper()
    color_bar_mapper.SetLookupTable(color_transfer_function)

    volumeProperty = vtk.vtkVolumeProperty()
    volumeProperty.SetScalarOpacity(scalar_opacity)
    volumeProperty.SetColor(color_transfer_function)

    actor = vtk.vtkVolume()
    actor.SetMapper(mapper)
    actor.SetProperty(volumeProperty)

    scalar_bar = vtk.vtkScalarBarActor()
    scalar_bar.SetLookupTable(color_bar_mapper.GetLookupTable())
    scalar_bar.SetTitle("Δ BMD (mg HA/ccm)")
    scalar_bar.AnnotationTextScalingOn()

    text_property = vtk.vtkTextProperty()
    text_property.SetColor(0.0, 0.0, 0.0)
    text_property.SetFontSize(30)
    scalar_bar.SetLabelTextProperty(text_property)
    scalar_bar.SetTitleTextProperty(text_property)
    scalar_bar.UnconstrainedFontSizeOn()

    renderer = vtk.vtkRenderer()
    renderer.AddVolume(actor)
    renderer.AddActor2D(scalar_bar)
    renderer.SetBackground(1.0, 1.0, 1.0)
    renderer.GetActiveCamera().SetViewUp(0, 0, -1)
    renderer.GetActiveCamera().SetPosition((ibounds[1]-ibounds[0]),
                                           (ibounds[3]-ibounds[2])*5,
                                           (ibounds[5]-ibounds[4]))
    renderer.GetActiveCamera().SetFocalPoint((ibounds[1]-ibounds[0]),
                                             (ibounds[3]-ibounds[2]),
                                             (ibounds[5]-ibounds[4]))
    renderer.GetActiveCamera().Elevation(elevation)
    renderer.GetActiveCamera().Azimuth(azimuth)
    renderer.ResetCamera()

    render_window = vtk.vtkRenderWindow()
    render_window.SetSize(2000, 1000)
    render_window.AddRenderer(renderer)
    render_window.SetWindowName('VolumeRendering')

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    render_window.Render()
    interactor.Start()

if __name__ == "__main__":
    main()