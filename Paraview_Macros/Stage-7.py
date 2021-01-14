from paraview.simple import *
import sys
import os
sys.path.append(r"E:\Code_Repos\PMV_Challenge2020\utils")
import numpy as np
import camera_path as cp

from paraview_DRV_helper import *

#-------------------Stage 7 Animation---------------------------
#Time: 6 secs
#Introduction: Show Velocity Field by animated particles
#              Step1. Rotate camer to center side
#              Step2. Particle injection animation
#---------------------------------------------------------------
frameID=1875
out_dir = r"E:\Code_Repos\PMV_Challenge2020\output"

Title = Text(registrationName='Text1')
Title_Display=Show(Title)
Title.Text = 'Virtual lab: Particle transport'
Title_Display.WindowLocation = 'AnyLocation'
Title_Display.Position = [0.35, 0.9]
Title_Display.FontSize = 35

#Retrive Data from Stage 1
image_binary,image_binary_Display = findObject('XMLImageDataReader1')
bbox,bbox_center=getDomainBbox(image_binary)

renderView = GetActiveViewOrCreate('RenderView')
renderView.CameraPosition = [-626.6760284067612, 1100.7173802645682,  1843.0673421620343]
renderView.CameraFocalPoint = bbox_center
renderView.CameraViewUp = [0.,  1.,  0.]

image_binary_Display.SetScalarBarVisibility(renderView, False)


#rock_left,rock_left_display=findObject('Clip1')
#rock_right,rock_right_display=findObject('Clip3')
rock_left,rock_left_display=findObject('XMLUnstructuredGridReader1')
rock_right,rock_right_display=findObject('XMLUnstructuredGridReader3')

#Load Camera Model
CamModel = STLReader(FileNames=['E:/Code_Repos/PMV_Challenge2020/data/Camera.stl'])
CamModel_Display=Show(CamModel)
CamModel_Display.Position = [500.0, 250.0, 1000.0]
CamModel_Display.Orientation = [0.0, 90.0, 0.0]
CamModel_Display.Scale = [5.0, 5.0, 5.0]
CamModel_Display.Opacity=0.0

#--------------------------------------------
#-------------ANIMATION Step1----------------
#       Rotate View to the front side
#--------------------------------------------

animationScene = GetAnimationScene()
animationScene.StartTime = 0
animationScene.EndTime = 1
animationScene.PlayMode = 'Sequence'

#Hide Streamline
nsecs=1
fps=25
nb_frames =nsecs*fps 
frameID=FadeEffect(animationScene, 
           input_objs_display=[rock_left_display,rock_right_display,CamModel_Display], 
           start_opacitys=[1.0,1.0,0.0],
           end_opacitys=[0.0,0.0,1.0], 
           nframes=nb_frames,frameID=frameID,
           saveAnimation=True,output_dir=out_dir)


#--------------------------------------------
#-------------ANIMATION Step2----------------
#        Inject particles into domain
#--------------------------------------------

#Load animated particles(This has to be loaded after previous animations)
particle,particle_Display=loadAnimatedParticles(
   fname_head='E:/Code_Repos/PMV_Challenge2020/particles/particles_Time',
   numTimesteps=325)

particle_proj,particle_proj_Display=loadAnimatedImages(
   fname_head='E:/Code_Repos/PMV_Challenge2020/particles/proj_particles_Time',
   numTimesteps=325)
particle_proj_Display.Position = [0.0, 0.0, -500.0]


nsecs=18
fps=25
nb_frames =nsecs*fps 

center      = bbox_center
up_vector   = [ 0.,  1.,  0.] #Y axis
initial_pos = renderView.CameraPosition
focal_point = bbox_center
c = cp.AbsoluteOrbit(0, fps*25, 
                     center=center,
                     up_vector=up_vector,
                     initial_pos = renderView.CameraPosition,
                     focal_point=focal_point)

animationScene.NumberOfFrames = nb_frames
for i in range(nb_frames):
   renderView.Update()

   if(i<fps*6):
      renderView.CameraPosition = c.interpolate_position(i, None, None, None)
      renderView.CameraFocalPoint = c.interpolate_focal_point(i, None, None)
      renderView.CameraViewUp = c.interpolate_up_vector(i, None)

   animationScene.GoToNext()

   #Animation saving 
   image_name = os.path.join(out_dir, "%06d.png" % (frameID))
   SaveScreenshot(image_name,ImageResolution=[1920, 1080])

   frameID+=1



#Clean data
#for name,src in zip(GetSources().keys(),GetSources().values()):
#   if('ImageDataReader' in name[0]): continue
#   if('Threshold' in name[0]): continue
#   if('Clip' in name[0]): continue
#   Delete(src)

#Clean data
#Delete(Title)
#del Title