#    Copyright (C) 2015 Currell Berry, Justin Jackson, and Team 41 Epilepsy Modeling 
#
#    This file is part of SEAT (Simple EEG Analysis Tool).
#
#    SEAT is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    SEAT is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with SEAT.  If not, see <http://www.gnu.org/licenses/>.

#[CB 11/29/2015]
#this module defines functionality related to creating annotation lines in vispy opengl gloo

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
