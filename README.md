Porous media visualization and data reuse challenge
==============================================================================================
Bin Wang (binwang.0213@gmail.com)
Craft & Hawkins Department of Petroleum Engineering, Louisiana State University, US

<p align="center">
<img src="../main/output/Cover.jpg?raw=true" height="350" />
</p>

## Description

Fluid flow in porous media is important in many subsurface processes, including waste disposal, oil and natural gas recovery and CO2 sequestration. Recent advances in computational and experimental techniques have shed new light into the microscopic fluid flow analysis in various image-based digital rocks.  However, intuitive velocity field visualization for a digital rock with complex pore structure remains a challenge. In this work, a digital rock visualization workflow, focused on fluid flow and particle transport visualization, is explored based on a free visualization software, Paraview. In the developed workflow, built-in filters, a screenshot tool, a camera tool and a python scripting tool in Paraview are used to programmatically generate visualizations with a moving camera. To illustrate the capability of the workflow, a random sphere packing dataset (1000 x 500 x 500) with an experimental 3D velocity field is adopted. A 1:50 mins video is created with 7 scenes to visualize binary images, pore/grain structures, velocity fields and particle transport. In the last scene of the video, a virtual experiment is also performed to reproduce the tracer transport movies captured in the experiment by visualizing a projected particle density field for 100k particles. The developed workflow could be extended to support more physical processes for abritary image-based data on DRP, such as multiphase flow, rock deformation, etc, in various image-based digital rocks.

* DRP Dataset: https://www.digitalrocksportal.org/projects/175
* Paraview Dataset (Merge files into the `data` folder): https://doi.org/10.5281/zenodo.4437847

## Dependences:
* `Anaconda` with Python 3.6+ (https://www.anaconda.com/download/)
* `Paraview` 5.8.1+ (https://www.paraview.org/download/)
* `pyvista` 0.27.4+ (https://anaconda.org/conda-forge/pyvista)
* `moviepy` 1.0.3+ (https://pypi.org/project/moviepy/)

## Reference
* [1] Souzy, M., Lhuissier, H., Méheust, Y., Le Borgne, T., & Metzger, B. (2020). Velocity distributions, dispersion and stretching in three-dimensional porous media. Journal of Fluid Mechanics, 891, A16. doi:10.1017/jfm.2020.113

* [2] https://blog.kitware.com/lidarview-temporal-camera-animations/
