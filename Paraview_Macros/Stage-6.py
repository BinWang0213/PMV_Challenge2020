from paraview.simple import *
import sys
import os
sys.path.append(r"E:\Code_Repos\PMV_Challenge2020\utils")
import numpy as np
import camera_path as cp

from paraview_DRV_helper import *

#-------------------Stage 6 Animation---------------------------
#Time: 6 secs
#Introduction: Show Velocity Field by animated streamlines
#              Step1. Fade-out of pore space
#              Step2. Show animated streamlines + Center Cut View
#---------------------------------------------------------------
frameID=1250
out_dir = r"E:\Code_Repos\PMV_Challenge2020\output"

Title = Text(registrationName='Text1')
Title_Display=Show(Title)
Title.Text = 'Digital rock visulization: Streamline View'
Title_Display.WindowLocation = 'AnyLocation'
Title_Display.Position = [0.35, 0.85]
Title_Display.FontSize = 35

#Retrive Data from Stage 1
image_binary,image_binary_Display = findObject('XMLImageDataReader1')
bbox,bbox_center=getDomainBbox(image_binary)


renderView = GetActiveViewOrCreate('RenderView')
#renderView.CameraPosition = [-174.36, 156.18,  330.82]
renderView.CameraFocalPoint = bbox_center
renderView.CameraViewUp = [0.,  1.,  0.]

#Retrive pore and rock volume
rock,rockDisplay=findObject('Threshold1')
#pore,poreDisplay=findObject('Threshold2')
#rock,rockDisplay=extractSubVolume(image_binary,value=1.0)
pore,poreDisplay=extractSubVolume(image_binary,value=0.0)
poreDisplay.Opacity=0.0

#Retrive velocity field
vel,vel_Display=findObject('XMLImageDataReader2')
#vel,vel_Display=loadImage('E:/Code_Repos/PMV_Challenge2020/image_vel.vti')
#colorData(vel,vel_Display,'Velocity(um/s)','erdc_rainbow_dark',showColorBar=False)

#Init View
image_binary_Display.SetScalarBarVisibility(renderView, False)

#Show Center Cut view

Blocks=[]
Blocks_Display=[]
'''
#Small memory case
for i in range(3):
   block=XMLUnstructuredGridReader(FileName=['E:/Code_Repos/PMV_Challenge2020/Rock_Cut_%d.vtu'%(i+1)])
   block_show=Show(block)
   #colorData(block,block_show,'MetaImage','erdc_divLow_icePeach',showColorBar=False)
   Blocks+=[block]
   Blocks_Display+=[block_show]
'''

#Large memory case
for cutRange in [(0.0,0.15),(0.15,0.85),(0.85,1.0)]:
   clip1 = Clip(Input=rock)
   clip1.ClipType = 'Box'
   clip1.ClipType.UseReferenceBounds = 1
   clip1.ClipType.Bounds = [cutRange[0], cutRange[1], 0.0, 1.0, 0.0, 1.0]
   clip1.Invert = 1
   clip1.Crinkleclip = 1

   clip1_Display=Show(clip1)
   Hide3DWidgets(proxy=clip1.ClipType)

   Blocks+=[clip1]
   Blocks_Display+=[clip1_Display]


Hide(rock)

#Load Streamline
SLs,SLS_Display=loadStreamline('E:/Code_Repos/PMV_Challenge2020/Streamlines.vtp')
#Hide(SLs)

#Delete(xx)

#Show streamline tracing process
integrationTimeLUT = GetColorTransferFunction('IntegrationTime')
integrationTimeLUT.RescaleTransferFunction(0.0, 1e-5)
integrationTimePWF = GetOpacityTransferFunction('IntegrationTime')
integrationTimePWF.RescaleTransferFunction(0.0, 1e-5)

#Hide(rock)
#Hide(pore)
#Hide(image_binary)
#Hide(vel)
Show(pore)

#--------------------------------------------
#-------------ANIMATION Step1----------------
#--------------------------------------------
#Moive parameters
nsecs=1
fps=25
nb_frames =nsecs*fps 


animationScene = GetAnimationScene()
animationScene.StartTime = 0
animationScene.EndTime = 1
animationScene.PlayMode = 'Sequence'

poreDisplay.Opacity=0.0
SLS_Display.Opacity=0.0
vel_Display.RescaleTransferFunctionToDataRange(False, True)
frameID=FadeEffect(animationScene, 
           input_objs_display=[poreDisplay,Blocks_Display[1],SLS_Display], 
           start_opacitys=[0.0,1.0,0.0],
           end_opacitys=[0.1,0.0,1.0], 
           vol_obj=vel, vol_dataName='Velocity(um/s)',vol_opacity=[0.5,0.0],
           nframes=nb_frames,frameID=frameID,
           saveAnimation=False,output_dir=out_dir)

Delete(vel)
del vel

#--------------------------------------------
#-------------ANIMATION Step2----------------
#--------------------------------------------
nsecs=12
fps=25
nb_frames =nsecs*fps 

center      = bbox_center
up_vector   = [ 0.,  1.,  0.] #Y axis
initial_pos = renderView.CameraPosition
focal_point = bbox_center
c = cp.AbsoluteOrbit(0, nb_frames*2, # rotate half circle
                     center=center,
                     up_vector=up_vector,
                     initial_pos = initial_pos,
                     focal_point=focal_point)

StepRange=SLs.PointData.GetArray('IntegrationTime').GetRange()
slice_I=0

animationScene.NumberOfFrames += nb_frames
for i in range(nb_frames):
   renderView.Update()

   if(i==0):
      print('Stage 5.1 Start @',renderView.CameraPosition)

   renderView.CameraPosition = c.interpolate_position(i, None, None, None)
   renderView.CameraFocalPoint = c.interpolate_focal_point(i, None, None)
   renderView.CameraViewUp = c.interpolate_up_vector(i, None)

   #Animate streamline
   slice_I=StepRange[0]+i/nb_frames * (StepRange[1]-StepRange[0])
   slice_I=min(max(StepRange[0],slice_I),StepRange[1])
   integrationTimeLUT.RescaleTransferFunction(StepRange[0], slice_I)
   integrationTimePWF.RescaleTransferFunction(StepRange[0], slice_I)

   animationScene.GoToNext()

   #Animation saving 
   image_name = os.path.join(out_dir, "%06d.png" % (frameID))
   #SaveScreenshot(image_name,ImageResolution=[1920, 1080])
   frameID+=1

# rotate another half circle to show streamline velocity field
nsecs=12
fps=25
nb_frames =nsecs*fps 

c = cp.AbsoluteOrbit(0, nb_frames*2, 
                     center=center,
                     up_vector=up_vector,
                     initial_pos = renderView.CameraPosition,
                     focal_point=focal_point)
frameID=RotateEffect(animationScene,camera_path_obj=c,
            nframes=nb_frames,frameID=frameID,
            saveAnimation=False,output_dir=out_dir)


#Restore to the original location
renderView.CameraPosition = initial_pos
renderView.CameraFocalPoint = bbox_center
renderView.CameraViewUp = [0.,  1.,  0.]

#Hide Streamline
nsecs=1
fps=25
nb_frames =nsecs*fps 
frameID=FadeEffect(animationScene, 
           input_objs_display=[SLS_Display], 
           start_opacitys=[SLS_Display.Opacity],
           end_opacitys=[0.0], 
           nframes=nb_frames,frameID=frameID,
           saveAnimation=False,output_dir=out_dir)

#Clean data
for name,src in zip(GetSources().keys(),GetSources().values()):
   if('ImageDataReader' in name[0]): continue
   if('Threshold' in name[0]): continue
   if('Clip' in name[0]): continue
   if('XMLUnstructuredGrid' in name[0]): continue
   Delete(src)

#Clean data
Delete(rock)
del rock
Delete(Blocks[1])
Delete(Title)
del Title