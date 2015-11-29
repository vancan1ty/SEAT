#[CB 11/28/2015]
#this module defines functionality related to creating text in vispy opengl gloo
#follows outline given here:
#http://www.opengl-tutorial.org/intermediate-tutorials/tutorial-11-2d-text/

import csv
import vispy
from vispy import gloo
import numpy as np

class TextDrawer():
    fwData = []
    cFWData = [] #"corrected" font width data, adjusted for screen size
    fHeight = 0

    def __init__(self,viewHeight,viewWidth):
        self.fwData = readInFontsWidthData()
        self.cFWData = self.adjustFontWidthData(viewWidth)
        self.fHeight = self.computeFontHeight(viewHeight)

    def onChangeDimensions(self, viewHeight, viewWidth):
        self.fHeight = self.computeFontHeight(viewHeight)
        self.cFWData = self.adjustFontWidthData(viewWidth)

    #think I will further have to divide w and h by 2
    def computeFontHeight(self,viewHeight):
        print "viewHeight: " + str(viewHeight)
        return ((20*1.0)/viewHeight)*3

    def adjustFontWidthData(self, viewWidth):
        out=[]
        for i in range(0,len(self.fwData)):
            out.append(((self.fwData[i]*1.0)/viewWidth)*3.0)
        return out

    #np.array([(x,y,u,v),(x,y,u,v)])
    def computeTextData(self,x,y,text):
        return computeTextData(x,y,self.cFWData,self.fHeight,text)

def computeTextData(x,y,cFWData,fHeight,text):
    #text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    vertices = np.zeros(len(text)*6+6,[("position",np.float32,2),("uv",np.float32,2)])
    ypos = y
    vertex_up_left = (-1,1)
    vertex_up_right = (0, 1)
    vertex_down_right = (0, 0)
    vertex_down_left  = (-1, 0)

    vertices["position"][0]=vertex_up_left
    vertices["position"][1]=vertex_down_left
    vertices["position"][2]=vertex_up_right

    vertices["position"][3]=vertex_down_right
    vertices["position"][4]=vertex_up_right
    vertices["position"][5]=vertex_down_left

    uv_up_left = (0, 0);
    uv_up_right = (1, 0);
    uv_down_right = (1, 1)
    uv_down_left  = (0, 1)

    vertices["uv"][0]=uv_up_left
    vertices["uv"][1]=uv_down_left
    vertices["uv"][2]=uv_up_right

    vertices["uv"][3]=uv_down_right
    vertices["uv"][4]=uv_up_right
    vertices["uv"][5]=uv_down_left

    for i in range(1,len(text)):
        charIndex = ord(text[i])-ord(' ')+7
        vSize = fHeight
        size = fHeight  #cFWData[charIndex]
        vertex_up_left = (x+i*size, y+vSize)
        vertex_up_right = (x+i*size+size, y+vSize)
        vertex_down_right = (x+i*size+size, y)
        vertex_down_left  = ( x+i*size, y)

        vertices["position"][i*6]=vertex_up_left
        vertices["position"][i*6+1]=vertex_down_left
        vertices["position"][i*6+2]=vertex_up_right

        vertices["position"][i*6+3]=vertex_down_right
        vertices["position"][i*6+4]=vertex_up_right
        vertices["position"][i*6+5]=vertex_down_left

        uv_x = (charIndex%8)/8.0
        uv_y = 1-(charIndex/8)/8.0

        uv_up_left = (uv_x,   1.0 - (uv_y + 1.0/8.0)  );
        uv_up_right = (uv_x+1.0/8.0,    1.0 - (uv_y + 1.0/8.0)  );
        uv_down_right = (uv_x+1.0/8.0,  1.0 - uv_y )
        uv_down_left  = (uv_x,  1.0 - uv_y )

        vertices["uv"][i*6]=uv_up_left
        vertices["uv"][i*6+1]=uv_down_left
        vertices["uv"][i*6+2]=uv_up_right

        vertices["uv"][i*6+3]=uv_down_right
        vertices["uv"][i*6+4]=uv_up_right
        vertices["uv"][i*6+5]=uv_down_left
    return vertices

def readInFontsWidthData():
    out = []
    with open('ArialSubset32UpFontData.csv','rb') as csvfile:
        reader = csv.reader(csvfile)
        index = 0
        for row in reader:
            if(index < 40):
                pass
            elif(index < 104):
                out.append(int(row[1]))
            else:
                break
            index+=1
    return out


#data = vispy.io.imread("ArialSubset32Up.bmp")
#gloo.Texture2D(data)

    
