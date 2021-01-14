from paraview.simple import *
import sys
import os
sys.path.append(r"E:\Code_Repos\PMV_Challenge2020\utils")
import numpy as np
import camera_path as cp

from paraview_DRV_helper import *

#-------------------Stage 4 Animation---------------------------
#Time: 6 secs
#Introduction: Show Pore and rock grain by moving slicer and cliper
#              Step1. Remove Pore from domain by slicing plane
#              Step2. Rotate 360
#---------------------------------------------------------------
frameID=800
out_dir = r"E:\Code_Repos\PMV_Challenge2020\output"

Title = Text(registrationName='Text1')
Title_Display=Show(Title)
Title.Text = 'Digital rock visulization: Pore Space'
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

SlicePlane="XZ"

#Prepare object for slicing
rock,rockDisplay=extractSubVolume(image_binary,value=1.0)
pore,poreDisplay=extractSubVolume(image_binary,value=0.0)
#pore_edge,poreDisplay_edge=enhanceSubVolumeEdge(image_binary,value=0.0) #enhance visual feature

#Prepare slicer
slicer,slicerDisplay=createFastCutter(image_binary, renderView)
#slicerDisplay.Opacity=0.55

#Init Slice view
Hide(rock)
Hide(image_binary)
renderView.Update()



#--------------------------------------------
#-------------ANIMATION Step2----------------
#--------------------------------------------
animationScene = GetAnimationScene()
animationScene.StartTime = 0
animationScene.EndTime = 1
animationScene.PlayMode = 'Sequence'

nsecs=1
fps=25
nb_frames =nsecs*fps 

#Fade-in effect for Pore Space
frameID=FadeEffect(animationScene, 
           input_objs_display=[slicerDisplay], 
           start_opacitys=[slicerDisplay.Opacity],
           end_opacitys=[0.55], 
           nframes=nb_frames,frameID=frameID,
           saveAnimation=True,output_dir=out_dir)

#--------------------------------------------
#-------------ANIMATION Step1----------------
#--------------------------------------------
#Moive parameters
nsecs=8
fps=25
nb_frames =nsecs*fps 


center      = bbox_center
up_vector   = [ 0.,  1.,  0.] #Y axis
initial_pos = renderView.CameraPosition
focal_point = bbox_center
c = cp.AbsoluteOrbit(0, nb_frames, # rotate half circle
                     center=center,
                     up_vector=up_vector,
                     initial_pos = initial_pos,
                     focal_point=focal_point)

#Play animation
animationScene.GoToFirst()

animationScene.NumberOfFrames += nb_frames
bbox_center=[bbox[1]/2.0,bbox[3]/2.0,bbox[5]/2.0]
slice_I=0
for i in range(nb_frames):
   renderView.Update()

   if(i==0):
      print('Stage 3.1 Start @',renderView.CameraPosition)

   renderView.CameraPosition = c.interpolate_position(i, None, None, None)
   renderView.CameraFocalPoint = c.interpolate_focal_point(i, None, None)
   renderView.CameraViewUp = c.interpolate_up_vector(i, None)
   
   #i*2.5 accelerate removing rate
   slice_I=interpPlaneLoc(i,nb_frames,bbox,plane=SlicePlane,inverse=True)
   #print(i,SlicePlane,slice_I)
   setCliperRange(slicer,bbox,plane=SlicePlane,loc_range=[0,slice_I])
   slicerDisplay.Opacity=0.55



   animationScene.GoToNext()

   #Animation saving 
   image_name = os.path.join(out_dir, "%06d.png" % (frameID))
   SaveScreenshot(image_name,ImageResolution=[1920, 1080])
   frameID+=1


#Restore to the original location
renderView.CameraPosition = initial_pos
renderView.CameraFocalPoint = bbox_center
renderView.CameraViewUp = [0.,  1.,  0.]

print('Stage 4.1 End @',renderView.CameraPosition,'FrameID=',frameID)


#Reset Slice view
Hide(slicer)
#--------------------------------------------
#-------------ANIMATION Step2----------------
#--------------------------------------------
nsecs=1
fps=25
nb_frames =nsecs*fps 

#Fade-in effect for Rock Space
Show(rock)
rockDisplay.Opacity=0.0
frameID=FadeEffect(animationScene, 
           input_objs_display=[rockDisplay], 
           start_opacitys=[rockDisplay.Opacity],
           end_opacitys=[1.0], 
           nframes=nb_frames,frameID=frameID,
           saveAnimation=True,output_dir=out_dir)


#Clean data
for name,src in zip(GetSources().keys(),GetSources().values()):
   if('DataReader' in name[0]): continue
   Delete(src)

#Delete(pore_edge)
#del pore_edge
Delete(Title)
del Title

#Show(image_binary)