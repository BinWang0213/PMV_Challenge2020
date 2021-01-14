from paraview.simple import *
import numpy as np
import sys
import os


def getDomainBbox(input_obj):
    bbox=np.array(input_obj.GetDataInformation().DataInformation.GetBounds(),dtype=np.int32)
    bbox_center=np.mean(bbox.reshape(3,2),axis=1)
    return bbox,bbox_center

def loadImage(fname,dataName=None,showColorBar=False):
    #Load a image from file and show it
    img = XMLImageDataReader(FileName=[fname])
    imgDisplay = Show(img)

    if(dataName is None):
        dataName=img.CellData.keys()[0] #Use the first cell data as image color

    #Set data color
    #colorData(img,imgDisplay,dataName,'CIELab Blue to Red',showColorBar)
    colorData(img,imgDisplay,dataName,'erdc_divLow_icePeach',showColorBar)

    #Set visulization type, Surface, Volume, Outline, etc
    imgDisplay.SetRepresentationType('Surface')

    # reset view to fit data bounds
    renderView = GetActiveViewOrCreate('RenderView')
    bbox,bbox_center=getDomainBbox(img)
    renderView.ResetCamera(*bbox)

    renderView.Update()

    return img,imgDisplay

def loadStreamline(fname,dataName=None,showColorBar=False):
    #Load streamline object generated from LagrangianParticleTracker
    SLs = XMLPolyDataReader(FileName=[fname])
    SLsDisplay = Show(SLs)

    if(dataName is None):
        dataName='IntegrationTime'
    
    #Show streamline
    colorData(SLs,SLsDisplay,dataName,'erdc_rainbow_dark',showColorBar)
    SLsDisplay.Opacity = 0.5

    return SLs,SLsDisplay

def loadAnimatedParticles(fname_head,numTimesteps,dataName=None,showColorBar=False):
    #Load animated particles from file
    fileList=[fname_head+str(i)+'.vtp' for i in range(numTimesteps)]
    print(fileList[0],fileList[-1])

    particle_time = XMLPolyDataReader(FileName=fileList)    
    PtsDisplay=Show(particle_time)
    PtsDisplay.SetRepresentationType('Points')
    #PtsDisplay.RenderPointsAsSpheres = 1
    #PtsDisplay.PointSize = 2.0

    if(dataName is None):
        dataName='ParticleVelocity'
    colorData(particle_time,PtsDisplay,dataName,'erdc_rainbow_dark',showColorBar)

    return particle_time,PtsDisplay

def loadAnimatedImages(fname_head,numTimesteps,dataName=None,showColorBar=False):
    #Load a image from file and show it

    fileList=[fname_head+str(i)+'.vti' for i in range(numTimesteps)]
    print(fileList[0],fileList[-1])

    img = XMLImageDataReader(FileName=fileList)
    imgDisplay = Show(img)

    if(dataName is None):
        dataName=img.CellData.keys()[0] #Use the first cell data as image color

    #Set data color
    colorData(img,imgDisplay,dataName,'X Ray',showColorBar)
    #Set visulization type, Surface, Volume, Outline, etc
    imgDisplay.SetRepresentationType('Surface')

    return img,imgDisplay

def extractSubVolume(input_obj,dataName=None,value=0):
    #Extract sub-volume from image by its scalar value
    vol = Threshold(Input=input_obj)
    if(dataName is None):
        dataName=input_obj.CellData.keys()[0] #Use the first cell data as image color
    
    vol.Scalars = ['CELLS', dataName]
    vol.ThresholdRange = [value, value] # Assume 1.0 is rock
    volDisplay = Show(vol)
    volDisplay.SetRepresentationType('Surface')
    return vol,volDisplay

def enhanceSubVolumeEdge(input_obj,value=0):
    #Enhance sub volume edge visulization
    pore_edge,poreDisplay_edge=extractSubVolume(input_obj,None,value) #enhance visual feature
    poreDisplay_edge.SetRepresentationType('Feature Edges')
    poreDisplay_edge.Opacity=0.2
    ColorBy(poreDisplay_edge, None)

    return pore_edge,poreDisplay_edge


def findObject(obj_name):
    #Find the object and its corrsponding display obj
    obj=FindSource(obj_name)
    objDisplay=GetDisplayProperties(obj)
    return obj,objDisplay

def colorData(obj,obj_display,dataName,cmap='erdc_rainbow_dark',showColorBar=False):
    #Show data with a given colormap

    if(dataName in obj.PointData.keys()):
        ColorBy(obj_display, ('POINTS',dataName))
    if(dataName in obj.CellData.keys()):
        ColorBy(obj_display, ('CELLS',dataName))
    
    #Show colorbar
    renderView = GetActiveViewOrCreate('RenderView')
    if(showColorBar):
        obj_display.RescaleTransferFunctionToDataRange(True, False)
        obj_display.SetScalarBarVisibility(renderView, True)

    #Set colomap
    LUT = GetColorTransferFunction(dataName)
    LUT.ApplyPreset(cmap, True)
    PWF = GetOpacityTransferFunction(dataName)

def invertColorMap(dataName):
    #Invert Colormap 
    # get opacity transfer function/opacity map for 'MetaImage'
    metaImagePWF = GetOpacityTransferFunction(dataName)
    if(metaImagePWF.Points==[0.0, 1.0, 0.5, 0.0, 1.0, 0.0, 0.5, 0.0]):
        metaImagePWF.Points=[0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]
    else:
        metaImagePWF.Points = [0.0, 1.0, 0.5, 0.0, 1.0, 0.0, 0.5, 0.0]




def createFastCutter(input_obj, renderView):
   #One layer subset is much faster than default slicer in Paraview
   extractSubset1 = ExtractSubset(Input=input_obj)
   extractSubset1Display = Show(extractSubset1, renderView, 'UniformGridRepresentation')
   extractSubset1Display.SetRepresentationType('Surface')
   renderView.Update()
   return extractSubset1,extractSubset1Display

def setSliceLoc(slicer,bbox,plane="XY",loc=0):
   #Set slicer location
   VOI=np.array(bbox)
   if(plane=="XY"): 
      VOI[4],VOI[5]=loc,min(bbox[5],(loc+1))
   if(plane=="XZ"): 
      VOI[2],VOI[3]=loc,min(bbox[3],(loc+1))
   if(plane=="YZ"): 
      VOI[0],VOI[1]=loc,min(bbox[1],(loc+1))
   slicer.VOI = VOI

def setCliperRange(cliper,bbox,plane="XY",loc_range=[0,1]):
   #Set cliper range
   VOI=np.array(bbox)
   if(plane=="XY"): 
      VOI[4],VOI[5]=max(bbox[4],loc_range[0]),min(bbox[5],loc_range[1])
   if(plane=="XZ"): 
      VOI[2],VOI[3]=max(bbox[2],loc_range[0]),min(bbox[3],loc_range[1])
   if(plane=="YZ"): 
      VOI[0],VOI[1]=max(bbox[0],loc_range[0]),min(bbox[1],loc_range[1])
   cliper.VOI = VOI

def interpPlaneLoc(i,imax,bbox,plane="XY",inverse=False):
   #Interpolate relative plane location in a bbox by given i in [0,imax]
   if(plane=="XY"): box_max = bbox[5]
   if(plane=="XZ"): box_max = bbox[3]
   if(plane=="YZ"): box_max = bbox[1]
   
   slice_I=int(i/imax * box_max)
   if(inverse): slice_I=box_max-slice_I
   return slice_I

def createFastSliceObject(input_obj, renderView, plane="XY"):
    #Convert a solid object into shell for faster slicing

    if(plane=="XY"): clipNormal=[0.0,0.0,1.0]
    if(plane=="YZ"): clipNormal=[1.0,0.0,0.0]
    if(plane=="XZ"): clipNormal=[0.0,1.0,0.0]

    Hide(input_obj)
    rockSurface = ExtractSurface(Input=input_obj)
    rockSurfaceDisplay = Show(rockSurface)
    rockSurfaceDisplay.SetRepresentationType('Surface')
    renderView.Update()

    Hide(rockSurface)
    clip1 = Clip(Input=rockSurface)
    clip1.ClipType = 'Plane'
    clip1.Scalars = ['CELLS', 'MetaImage']
    clip1.Value = 1.0
    # init the 'Plane' selected for 'ClipType'
    clip1.Crinkleclip = 0
    clip1.ClipType.Normal = clipNormal

    Hide3DWidgets(proxy=clip1.ClipType)

    clip1Display = Show(clip1)
    clip1Display.SetRepresentationType('Surface')

    renderView.Update()
    return clip1,clip1Display


def FadeEffect(animationScene, input_objs_display=[], start_opacitys=[0.0],end_opacitys=[0.0], 
    vol_obj=None,vol_dataName=None,vol_opacity=[],
    nframes=25,frameID=0,saveAnimation=False,output_dir=""):
    #Fade in/out effect
    renderView = GetActiveViewOrCreate('RenderView')

    animationScene.NumberOfFrames += nframes
    for i in range(nframes):
        renderView.Update()

        for j,obj in enumerate(input_objs_display):
            change_rate=(end_opacitys[j]-start_opacitys[j])/nframes
            obj.Opacity= start_opacitys[j] + (i+1)*change_rate

        #Volume data opacity is changed by colormap
        if(vol_dataName is not None):
            velocityumsPWF = GetOpacityTransferFunction(vol_dataName)
            change_rate=(vol_opacity[1]-vol_opacity[0])/nframes
            opacity=vol_opacity[0] + (i+1)*change_rate
            velocityumsPWF.Points = [0.0, 0.0, 0.5, 0.0, 
                                    #0.5, 1.0, 0.5, 0.0,
                                    vol_obj.CellData[vol_dataName].GetRange()[1], opacity, 0.5, 0.0] 

        animationScene.GoToNext()

        if(saveAnimation):
            #Animation saving 
            image_name = os.path.join(output_dir, "%06d.png" % (frameID))
            SaveScreenshot(image_name,ImageResolution=[1920, 1080])
        
        frameID+=1
    
    return frameID


def RotateEffect(animationScene,camera_path_obj,
    nframes=25,frameID=0,saveAnimation=False,output_dir=""):
    renderView = GetActiveViewOrCreate('RenderView')

    animationScene.NumberOfFrames += nframes
    for i in range(nframes):
        renderView.Update()

        renderView.CameraPosition = camera_path_obj.interpolate_position(i, None, None, None)
        renderView.CameraFocalPoint = camera_path_obj.interpolate_focal_point(i, None, None)
        renderView.CameraViewUp = camera_path_obj.interpolate_up_vector(i, None)
        
        animationScene.GoToNext()

        if(saveAnimation):
            #Animation saving 
            image_name = os.path.join(output_dir, "%06d.png" % (frameID))
            SaveScreenshot(image_name,ImageResolution=[1920, 1080])
        
        frameID+=1

    return frameID