#[CB 11/28/2015]
#this module defines functionality related to creating text in vispy opengl gloo
#follows outline given here:
#http://www.opengl-tutorial.org/intermediate-tutorials/tutorial-11-2d-text/

import csv
import vispy
from vispy import gloo
import numpy as np

class LineDrawer():
    #fwData = []
    #cFWData = [] #"corrected" font width data, adjusted for screen size

    def __init__(self):
        pass

    def computeLinesData(self,timesList,startTime,endTime):
        return computeLinesData(timesList,startTime,endTime)

#rgbColor should be in form (0.9,0.2,1.0) (up to 1)
def computeLinesData(timesList,startTime,endTime,rgbColor=(1.0,0.0,0.0)):
    timesToShow = []
    for i in timesList:
        if (i >= startTime and i <= endTime):
            timesToShow.append(i)
    vertices = np.zeros(2*len(timesToShow),[("position",np.float32,2),("a_color",np.float32,3)])

    for i in range(0,len(timesToShow)):
        time = timesToShow[i]
        vTime = ((time-startTime)/(endTime-startTime))*2-1
        vertex_up= (vTime, 1)
        vertex_down= (vTime, -1)

        vertices["position"][i*2]=vertex_up
        vertices["position"][i*2+1]=vertex_down

        vertices["a_color"][i*2]=rgbColor
        vertices["a_color"][i*2+1]=rgbColor
    return vertices
