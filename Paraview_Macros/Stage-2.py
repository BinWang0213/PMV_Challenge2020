from paraview.simple import *
import sys
import os
sys.path.append(r"E:\Code_Repos\PMV_Challenge2020\utils")
import numpy as np
import camera_path as cp

from paraview_DRV_helper import *

#-------------------Stage 3 Animation---------------------------
#Time: 5 secs
#Introduction: Show Binary Image by moving slicing plane
#          Step1. Clip image to three slice plane
#          Step2. Moving slice planes while rotating 360 degree
#---------------------------------------------------------------
frameID=200
out_dir = r"E:\Code_Repos\PMV_Challenge2020\output"

Title = Text(registrationName='Text1')
Title_Display=Show(Title)
Title.Text = 'Digital rock visulization: Binary image'
Title_Display.WindowLocation = 'AnyLocation'
Title_Display.Position = [0.35, 0.85]
Title_Display.FontSize = 35

#One main img object
image_binary = FindSource('XMLImageDataReader1')
bbox,bbox_center=getDomainBbox(image_binary)
print('bbox',bbox)

renderView = GetActiveViewOrCreate('RenderView')
#renderView.CameraPosition = [ -893.5565509930346, 601.500007391076,  1335.7260326756277]
renderView.CameraFocalPoint = bbox_center
renderView.CameraViewUp = [0.,  1.,  0.]

#Three slicing planes
slicers=[None]*3
slicers_disp=[None]*3
SlicePlanes=['XY','YZ','XZ']
SliceLocs=[0,bbox[1]-1,0]
for i in range(3):
   slicers[i],slicers_disp[i]=createFastCutter(image_binary,renderView)
   setSliceLoc(slicers[i],bbox,plane=SlicePlanes[i],loc=SliceLocs[i])

#One main clipper
cliper,cliper_disp=createFastCutter(image_binary,renderView)

#Init Slice view
Hide(image_binary)

#--------------------------------------------
#-------------ANIMATION Step1----------------
#               Move cliper
#--------------------------------------------
#Moive parameters
nsecs=6
fps=25
nb_frames =nsecs*fps
n_steps=2

animationScene = GetAnimationScene()
animationScene.StartTime = 0
animationScene.EndTime = 1
animationScene.PlayMode = 'Sequence'

#Play animation
animationScene.GoToFirst()

animationScene.NumberOfFrames += nb_frames
slice_I=0
for i in range(nb_frames):
   renderView.Update()

   if(i==0):
      print('Stage 2 Start @',renderView.CameraPosition)

   slice_I=bbox[5]-int(i/nb_frames*bbox[5])-1
   setCliperRange(cliper,bbox,plane="XY",
                  loc_range=[0,slice_I])
   print(i,slice_I,bbox[5])

   if animationScene.AnimationTime == animationScene.EndTime:
      break
   animationScene.GoToNext()

   #Animation saving 
   image_name = os.path.join(out_dir, "%06d.png" % (frameID))
   SaveScreenshot(image_name,ImageResolution=[1920, 1080])
   frameID+=1

#stop_pos = [-185.8788607461567, 156.18, 319.0846687912181]
print('Stage 2 End @',renderView.CameraPosition)


#Reset Slice view
Hide(cliper)

#--------------------------------------------
#-------------ANIMATION Step2----------------
#        Rotate 360 + Moving slice planes
#--------------------------------------------
nsecs=8
fps=25
nb_frames =nsecs*fps

center      = bbox_center
up_vector   = [ 0.,  1.,  0.] #Y axis
#initial_pos = [-174.36, 156.18,  330.82]
initial_pos = renderView.CameraPosition
focal_point = bbox_center
c = cp.AbsoluteOrbit(0, nb_frames, # rotate half circle
                     center=center,
                     up_vector=up_vector,
                     initial_pos = initial_pos,
                     focal_point=focal_point)

animationScene.NumberOfFrames += nb_frames
slice_I=0
for i in range(nb_frames):
   renderView.Update()

   if(i==0):
      print('Stage 2 Start @',renderView.CameraPosition)

   #Rotation of camera
   renderView.CameraPosition = c.interpolate_position(i, None, None, None)
   renderView.CameraFocalPoint = c.interpolate_focal_point(i, None, None)
   renderView.CameraViewUp = c.interpolate_up_vector(i, None)

   #Move slice planes
   slice_I=interpPlaneLoc(i,nb_frames,bbox,plane=SlicePlanes[0],inverse=False)
   setSliceLoc(slicers[0],bbox,plane=SlicePlanes[0],loc=slice_I)
   slice_I=interpPlaneLoc(i,nb_frames,bbox,plane=SlicePlanes[1],inverse=True)-2
   setSliceLoc(slicers[1],bbox,plane=SlicePlanes[1],loc=max(0,slice_I))
   slice_I=interpPlaneLoc(i,nb_frames,bbox,plane=SlicePlanes[2],inverse=False)
   setSliceLoc(slicers[2],bbox,plane=SlicePlanes[2],loc=slice_I)

   animationScene.GoToNext()

   #Animation saving 
   image_name = os.path.join(out_dir, "%06d.png" % (frameID))
   SaveScreenshot(image_name,ImageResolution=[1920, 1080])
   frameID+=1

#Restore to the original location
#renderView.CameraPosition = [-174.36, 156.18,  330.82]
renderView.CameraPosition = initial_pos
renderView.CameraFocalPoint = bbox_center
renderView.CameraViewUp = [0.,  1.,  0.]

print('Stage 2 End @',renderView.CameraPosition,'FrameID=',frameID)

renderView.Update()

#Clean data
for obj in slicers:
    Delete(obj)
    del obj
Delete(cliper)
del cliper
Delete(Title)
del Title

#Restore main image
Show(image_binary)
