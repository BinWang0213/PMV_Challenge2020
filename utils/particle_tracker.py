import numpy as np
from tqdm.notebook import tqdm

def find_interval_ids(A, target):
    #A must be sorted
    #https://stackoverflow.com/questions/8914491/
    idx = A.searchsorted(target)
    idx = np.clip(idx, 0, len(A)-1)
    left = A[idx-1]
    right = A[idx]
    idx -= target - left >0
    return idx

def getSLInfo(pv_streamlines):
    #Collect streamline-wise info from pyvista vtp

    SLIds=pv_streamlines.lines
    SLs=[]
    startID=0
    for i in range(pv_streamlines.number_of_cells):
        length=SLIds[startID]
        endID=startID+length+1
        SLId=np.array(SLIds[startID+1:endID])
        SLs+=[SLId]
        startID=endID
    return SLs

def samplePts(Times,SLs,SLId):    
    #Sample pts from a streamline by given required snanpshot time

    TravelTime=np.array(SLs['IntegrationTime'][SLId])
    SL_vel=np.array(SLs['ParticleVelocity'][SLId])
    SL_pts=np.array(SLs.points[SLId,:])
    #print(TravelTime,SL_vel,SL_pts)

    #Interpolate particle location on given time series along streamline
    Intervals=find_interval_ids(TravelTime,Times)
    Pts_local=(Times-TravelTime[Intervals])/(TravelTime[Intervals+1]-TravelTime[Intervals])
    if(len(np.where(Pts_local>1.0)[0])>0):#Terminate time < Times
        Pts_local[Pts_local>1.0]=Pts_local[np.where(Pts_local>1.0)[0][0]-1]

    Intervals_vec=SL_pts[Intervals+1,:]-SL_pts[Intervals,:]
    Intervals_length=np.linalg.norm(Intervals_vec,axis=1)
    Pts=SL_pts[Intervals,:]+Pts_local[:,np.newaxis]*Intervals_length[:,np.newaxis]*Intervals_vec

    Intervals_vec=SL_vel[Intervals+1,:]-SL_vel[Intervals,:]
    Intervals_length=np.linalg.norm(Intervals_vec,axis=1)
    Vels=SL_vel[Intervals,:]+Pts_local[:,np.newaxis]*Intervals_length[:,np.newaxis]*Intervals_vec

    #SL_new=pv.PolyData(Pts)
    return Pts,Vels

def Streamline2Particle(Times,pv_streamlines):
    #Sample particle from streamline by given time

    SLs=getSLInfo(pv_streamlines)

    Streamlines_Pts=[]
    Streamlines_Vel=[]
    for i in tqdm(range(pv_streamlines.n_cells)):
        Pts,Vels=samplePts(Times,pv_streamlines,SLs[i])
        Streamlines_Pts+=[np.array(Pts)]
        Streamlines_Vel+=[np.array(Vels)]
    
    return Streamlines_Pts,Streamlines_Vel