from paraview.simple import *
import sys
import os
sys.path.append(r"E:\Code_Repos\PMV_Challenge2020\utils")
import numpy as np
import camera_path as cp

from paraview_DRV_helper import *

# load plugin
PluginPath=os.path.join(os.getcwd(),
                   'paraview-'+str(GetParaViewVersion()),
                   'plugins','LagrangianParticleTracker','LagrangianParticleTracker.dll')
LoadPlugin(PluginPath, remote=False, ns=globals())

vel,vel_Display=loadImage('E:/Code_Repos/PMV_Challenge2020/image_vel_track.vti')
ColorBy(vel_Display, ('CELLS', 'Velocity(um/s)', 'Magnitude'))

bbox,bbox_center=getDomainBbox(vel)

seeds=XMLPolyDataReader(FileName=['E:/Code_Repos/PMV_Challenge2020/particle_seeds.vtp'])
seeds_Display=Show(seeds)
ColorBy(seeds_Display, ('POINTS', 'Velocity(um/s)', 'Magnitude'))

surface = XMLMultiBlockDataReader(FileName=['E:/Code_Repos/PMV_Challenge2020/Wall.vtm'])
surface_Display=Show(surface)
ColorBy(surface_Display, ('FIELD', 'SurfaceType'))


#Run streamline tracker
SetActiveSource(vel)

# create a new 'Lagrangian Particle Tracker'
Tracker1 = LagrangianParticleTracker(
    FlowInput=vel,
    ParticleSeeds=seeds,
    Surface=surface)
Tracker1.IntegrationModel = 'Matida Integration Model'
Tracker1.Integrator = 'Runge Kutta 4/5'

# init the 'Matida Integration Model' selected for 'IntegrationModel'
Tracker1.IntegrationModel.Locator = 'Static Cell Locator'
Tracker1.IntegrationModel.ParticleInitialVelocity = ['POINTS', 'Velocity(um/s)']
Tracker1.IntegrationModel.ParticleInitialIntegrationTime = ['POINTS', 'Density']
Tracker1.IntegrationModel.FlowVelocity = ['CELLS', 'Velocity(um/s)']
Tracker1.IntegrationModel.FlowDensity = ['CELLS', 'FluidDensity']
Tracker1.IntegrationModel.FlowDynamicViscosity = ['CELLS', 'FluidViscosity']
Tracker1.IntegrationModel.ParticleDiameter = ['POINTS', 'Diameter']
Tracker1.IntegrationModel.ParticleDensity = ['POINTS', 'Density']

Tracker1.MinStep = 0.3
Tracker1.MaxStep = 0.5
Tracker1.NumberOfSteps = 1000

#Show streamlines and interaction points
Hide(vel)
Hide(surface)

Tracker1 = GetActiveSource()
SetActiveSource(Tracker1)

Tracker1Display = Show(Tracker1)
ColorBy(Tracker1Display, ('POINTS', 'StepNumber'))

Tracker1IntDisplay = Show(OutputPort(Tracker1, 1))
ColorBy(Tracker1IntDisplay, ('POINTS', 'Interaction'))

#Save streamline to file
SaveData('E:\Code_Repos\PMV_Challenge2020\Streamlines.vtp', proxy=Tracker1, ChooseArraysToWrite=1,
    PointDataArrays=['IntegrationTime', 'ParticleVelocity', 'StepNumber'],
    CellDataArrays=['Density', 'Diameter'],
    CompressorType='ZLib')

