from paraview.simple import *
import sys
import os
sys.path.append(r"E:\Code_Repos\PMV_Challenge2020\utils")
import numpy as np
import camera_path as cp

from paraview_DRV_helper import *

#-------------------Stage 5 Animation---------------------------
#Time: 6 secs
#Introduction: Show velocity field by rotating
#---------------------------------------------------------------
frameID=1050
out_dir = r"E:\Code_Repos\PMV_Challenge2020\output"

Title = Text(registrationName='Text1')
Title_Display=Show(Title)
Title.Text = 'Digital rock visulization: Velocity Field'
Title_Display.WindowLocation = 'AnyLocation'
Title_Display.Position = [0.35, 0.85]
Title_Display.FontSize = 35

#Retrive Data from Stage 1
image_binary = FindSource('XMLImageDataReader1')
bbox,bbox_center=getDomainBbox(image_binary)

renderView = GetActiveViewOrCreate('RenderView')
#renderView.CameraPosition = [-174.36, 156.18,  330.82]
renderView.CameraFocalPoint = bbox_center
renderView.CameraViewUp = [0.,  1.,  0.]

#Prepare object for slicing
rock,rockDisplay=extractSubVolume(image_binary,value=1.0)
#pore,poreDisplay=extractSubVolume(image_binary,value=0.0)
#rock_edge,rockDisplay_edge=enhanceSubVolumeEdge(image_binary,value=1.0) #enhance visual feature


vel,vel_Display=loadImage('E:/Code_Repos/PMV_Challenge2020/image_vel.vti')
colorData(vel,vel_Display,'Velocity(um/s)','erdc_rainbow_dark',showColorBar=False)

#Init View
Hide(image_binary)
#Hide(pore)
disp=GetDisplayProperties(image_binary)
disp.SetScalarBarVisibility(renderView, False)

vel_Display.SetRepresentationType('Volume')
#Set volume opacity
velocityumsPWF = GetOpacityTransferFunction('Velocityums')
opacity=0.5
velocityumsPWF.Points = [0.0, 0.0, 0.5, 0.0, 
                         #0.5, 1.0, 0.5, 0.0,
                         vel.CellData['Velocity(um/s)'].GetRange()[1], opacity, 0.5, 0.0] #Half opacity
#473.931884765625

#Show Velocity arrow (crash on large dataset)
#glyph1 = Glyph(Input=vel, GlyphType='Arrow')
#glyph1.OrientationArray = ['CELLS', 'Velocity(um/s)']
#glyph1.ScaleArray = ['CELLS', 'Velocity(um/s)']
#glyph1.ScaleFactor = 0.05
#glyph1Display = Show(glyph1)
#ColorBy(glyph1Display, ('POINTS', 'Velocity(um/s)'))

#--------------------------------------------
#-------------ANIMATION Step1----------------
#--------------------------------------------
#Moive parameters
animationScene = GetAnimationScene()
animationScene.StartTime = 0
animationScene.EndTime = 1
animationScene.PlayMode = 'Sequence'

nsecs=8
fps=25
nb_frames =nsecs*fps 

center      = bbox_center
up_vector   = [ 0.,  1.,  0.] #Y axis
initial_pos = renderView.CameraPosition
focal_point = bbox_center
c = cp.AbsoluteOrbit(0, nb_frames, 
                     center=center,
                     up_vector=up_vector,
                     initial_pos = renderView.CameraPosition,
                     focal_point=focal_point)
frameID=RotateEffect(animationScene,camera_path_obj=c,
            nframes=nb_frames,frameID=frameID,
            saveAnimation=False,output_dir=out_dir)

print('Stage 4.1 End @',renderView.CameraPosition,'FrameID=',frameID)


#Clean data
for name,src in zip(GetSources().keys(),GetSources().values()):
   if('DataReader' in name[0]): continue
   if('Threshold' in name[0]): continue
   Delete(src)


#Delete(rock_edge)
#del rock_edge
Delete(Title)
del Title

#Reset view
