from paraview.simple import *
import sys
import os
sys.path.append(r"E:\Code_Repos\PMV_Challenge2020\utils")
import numpy as np
import camera_path as cp

from paraview_DRV_helper import *


#-------------------Stage 1 Animation---------------------------
#Time: 5 secs
#Introduction: Show Binary Image by rotating it 360 degree along 
#              Y axis
#---------------------------------------------------------------
frameID=0
out_dir = r"E:\Code_Repos\PMV_Challenge2020\output"


Title = Text(registrationName='Text1')
Title_Display=Show(Title)
Title.Text = 'Digital rock visulization: Binary image'
Title_Display.WindowLocation = 'AnyLocation'
Title_Display.Position = [0.35, 0.87]
Title_Display.FontSize = 35
#Load Data
image_binary,image_binaryDisplay= loadImage('E:/Code_Repos/PMV_Challenge2020/image_binary.vti')
bbox,bbox_center=getDomainBbox(image_binary)

renderView = GetActiveViewOrCreate('RenderView')

#--------------------------------------------
#-------------------ANIMATION----------------
#--------------------------------------------
#Moive parameters
nsecs=8
fps=25
nb_frames =nsecs*fps 

animationScene = GetAnimationScene()
animationScene.StartTime = 0
animationScene.EndTime = 1
animationScene.NumberOfFrames = 0
animationScene.PlayMode = 'Sequence'

#Play animation
animationScene.GoToFirst()

#Fancy camera operation
#https://blog.kitware.com/lidarview-temporal-camera-animations/
#https://gitlab.kitware.com/LidarView/lidarview-core/-/tree/master/Utilities/Animation
# Example of camera path : orbit around absolute position
center      = bbox_center
up_vector   = [ 0.,  1.,  0.]
#initial_pos = [ -132.49786752362962, 179.0541293593563,  350.8671831]
initial_pos = [ -626.6760284067612, 1100.7173802645682,  1843.0673421620343]
focal_point = bbox_center
c = cp.AbsoluteOrbit(0, nb_frames, # rotate half circle
                     center=center,
                     up_vector=up_vector,
                     initial_pos = initial_pos,
                     focal_point=focal_point)

animationScene.NumberOfFrames += nb_frames
for i in range(nb_frames):
   renderView.Update()
   
   #Rotation of camera
   renderView.CameraPosition = c.interpolate_position(i, None, None, None)
   renderView.CameraFocalPoint = c.interpolate_focal_point(i, None, None)
   renderView.CameraViewUp = c.interpolate_up_vector(i, None)

   if(i==0): print('Stage 1 Start @',renderView.CameraPosition)
   animationScene.GoToNext()
   
   #Animation saving 
   image_name = os.path.join(out_dir, "%06d.png" % (frameID))
   #SaveScreenshot(image_name,ImageResolution=[1920, 1080])
   frameID+=1

#Sync the last Camera location to the first one
renderView.CameraPosition = initial_pos
renderView.CameraFocalPoint = bbox_center
renderView.CameraViewUp = up_vector

#stop_pos = [-185.8788607461567, 156.18, 319.0846687912181]
print('Stage 1 End @',renderView.CameraPosition,'FrameID=',frameID)


#Clean data
Delete(Title)
del Title