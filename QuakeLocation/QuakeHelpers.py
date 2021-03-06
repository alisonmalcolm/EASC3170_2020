import numpy as np
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import math
#from IPython.html.widgets import  interactive, IntSlider, widget, FloatText, FloatSlider, Checkbox
#from IPython.html.ipywidgets import  interactive, IntSlider, widget, FloatText, FloatSlider, Checkbox
from ipywidgets import  interactive, IntSlider, widget, FloatText, FloatSlider, Checkbox, Layout
import os
from math import floor
from matplotlib import patheffects
import matplotlib

stlist=['CMB','TGUH','BBSR','PAYG','RCBR','SDV','SJG','WCI']
lonlist=[-120.387,-87.273,-64.696,-90.286,-35.901,-70.634,-66.15,-86.294]
latlist=[38.035,14.057,32.371,-0.674,-5.827,8.884,18.109,38.229]
SminusPlist=[120.,160.,240.,260.,30.,220.,220.,300.]

filelist1=os.listdir('Waveforms/')
#print(filelist1)
filelist2=[]
for file in filelist1:
    if 'datonly' in file:
        filelist2.append(file)
    
#print(filelist2)
#print(len(filelist2))


class timedata:
    def __init__(self):
        self.name = ''
        self.lat = 0.0    # creates a new empty list
        self.lon = 0.0
        self.filename=''
        self.timeseries=np.array
        self.SminusP=0.0

    
st=[]
for ii in range(len(filelist2)):
    dat=timedata()
    dat.name=stlist[ii]
    dat.lat=latlist[ii]
    dat.lon=lonlist[ii]
    dat.filename='Waveforms/'+filelist2[ii]
    dat.timeseries=np.loadtxt(dat.filename)
    dat.SminusP=SminusPlist[ii]
    st.append(dat)

# degrees to radians
def deg2rad(degrees):
    return math.pi*degrees/180.0
# radians to degrees
def rad2deg(radians):
    return 180.0*radians/math.pi

# Semi-axes of WGS-84 geoidal reference
WGS84_a = 6378137.0  # Major semiaxis [m]
WGS84_b = 6356752.3  # Minor semiaxis [m]

# Earth radius at a given latitude, according to the WGS-84 ellipsoid [m]
def WGS84EarthRadius(lat):
    # http://en.wikipedia.org/wiki/Earth_radius
    An = WGS84_a*WGS84_a * math.cos(lat)
    Bn = WGS84_b*WGS84_b * math.sin(lat)
    Ad = WGS84_a * math.cos(lat)
    Bd = WGS84_b * math.sin(lat)
    return math.sqrt( (An*An + Bn*Bn)/(Ad*Ad + Bd*Bd) )

# Bounding box surrounding the point at given coordinates,
# assuming local approximation of Earth surface as a sphere
# of radius given by WGS84
def boundingBox(latitudeInDegrees, longitudeInDegrees, halfSideInKm):
    lat = deg2rad(latitudeInDegrees)
    lon = deg2rad(longitudeInDegrees)
    halfSide = 1000*halfSideInKm

    # Radius of Earth at given latitude
    radius = WGS84EarthRadius(lat)
    # Radius of the parallel at given latitude
    pradius = radius*math.cos(lat)

    latMin = lat - halfSide/radius
    latMax = lat + halfSide/radius
    lonMin = lon - halfSide/pradius
    lonMax = lon + halfSide/pradius

    return (rad2deg(latMin), rad2deg(lonMin), rad2deg(latMax), rad2deg(lonMax))

def MyCircle(cx,cy,rad):
    #cx,cy in lon/lat, rad in km
    
    lat1,lon1,lat2,lon2=boundingBox(cy,cx,rad)
    radx=0.5*np.abs(lon2-lon1)
    rady=0.5*np.abs(lat2-lat1)
    #print(radx,rady)
    th=np.linspace(0,2*np.pi,100)
    x=cx+radx*np.cos(th)
    y=cy+rady*np.sin(th)
    return x,y
    

#19.421N 78.763

def PlotLocations(R1,R2,R3,ind_to_plot,Show=False):
    
    R=[R1,R2,R3]

    Quake_lat=19.421
    Quake_lon=-78.763

    plt.figure(figsize=(6,6))

    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.stock_img()
    ax.coastlines()

    if Show is True:
        ax.plot(Quake_lon,Quake_lat,'r*',markersize=14,label='Quake Location')

    ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                  linewidth=2, color='gray', alpha=0.5, linestyle='--')

    plt.xlim([-100,-50])
    plt.ylim([0,45])

    #ind_to_plot=[1,2,7]#[0,1,2,3,4,5,6,7]#[1,5,7]
    
    mark='o'
    jj=0
    for ii in ind_to_plot:
#        if ii < 4:
#            mark='o'
#        else:
#            mark='^'
        plt0,=plt.plot(st[ii].lon,st[ii].lat,marker=mark,markersize=12,transform=ccrs.PlateCarree(),label=st[ii].name)
        xc,yc=MyCircle(st[ii].lon,st[ii].lat,R[jj])
        mycol=plt.getp(plt0,'color')
        ax.plot(xc,yc,transform=ccrs.PlateCarree(),color=mycol)
        jj=jj+1
        
    plt.legend()

    plt.xlabel('longitude (deg)')
    plt.ylabel('longitude (deg)')

    return ax
    #TGUH, WCI, BBSR 1,7,2

def PlotCircles(ind_to_plot):
    Q = interactive(lambda R1,R2,R3,Show: PlotLocations(R1,R2,R3,ind_to_plot,Show),
                    R1=IntSlider(min=200, max=3200, step=5, value=60,description=st[ind_to_plot[0]].name,width=5,layout=Layout(width='50%', height='80px')),
                 R2=IntSlider(min=200, max=3200, step=5, value=60,description=st[ind_to_plot[1]].name,layout=Layout(width='50%', height='80px')),
                 R3=IntSlider(min=200, max=3200, step=5, value=60,description=st[ind_to_plot[2]].name,layout=Layout(width='50%', height='80px')),
                 Show=Checkbox(value=False, description='Show True Location',disabled=False))


    return Q

def viewSeismogram(Tp,Ts,stnum):

    ii=stnum
    fig,ax=plt.subplots(1,figsize=(10,3))
    ax.plot(st[ii].timeseries/np.max(st[ii].timeseries))
    plt.title('Station: '+st[ii].name)
    ax.plot([Tp,Tp],[-1,1],label='Tp')
    ax.plot([Ts,Ts],[-1,1],label='Ts')
    plt.xlabel('Time (s)')
    plt.ylabel('Normalized amplitude')

    ax.legend()
    
    return ax

def PlotPicks(stnum):
    Q = interactive(lambda Tp, Ts: viewSeismogram(Tp,Ts,stnum),
                    Tp=IntSlider(min=1, max=660, step=1, value=60,layout=Layout(width='65%', height='80px')),
                    Ts=IntSlider(min=1, max=660, step=1,value=150,continuous_update=True,layout=Layout(width='65%', height='80px')))

    return Q


