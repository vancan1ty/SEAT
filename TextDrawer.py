#[CB 11/28/2015]
#this module defines functionality related to creating text in vispy opengl gloo
#follows outline given here:
#http://www.opengl-tutorial.org/intermediate-tutorials/tutorial-11-2d-text/

import csv
import vispy
from vispy import gloo
import numpy as np

class TextDrawer():
    #fwData = []
    #cFWData = [] #"corrected" font width data, adjusted for screen size
    fHeight = 0
    fWidth = 0
    viewHeight = -1
    viewWidth = -1

    def __init__(self,viewHeight,viewWidth):
        #self.fwData = readInFontsWidthData()
        #self.cFWData = self.adjustFontWidthData(viewWidth)
        self.viewHeight = viewHeight
        self.viewWidth = viewWidth
        self.updateFontDimensions()

    def onChangeDimensions(self, viewHeight, viewWidth):
        self.viewHeight = viewHeight
        self.viewWidth = viewWidth
        self.updateFontDimensions()

    #think I will further have to divide w and h by 2
    def updateFontDimensions(self):
        nfHeight = (2.0/self.viewHeight)*16;
        nfWidth =  (2.0/self.viewWidth)*16; 
        # print "nfHeight: {a}, nfWidth: {b}".format(a=nfHeight,b=nfWidth)
        self.fHeight = nfHeight
        self.fWidth = nfWidth

    #np.array([(x,y,u,v),(x,y,u,v)])
    def computeTextData(self,x,y,text):
        return computeTextData(x,y,self.fHeight,self.fWidth,text,
                               self.viewHeight,self.viewWidth)

    def computeTextsData(self,positionToTextMap):
        return computeTextsData(positionToTextMap,self.fHeight,self.fWidth,self.viewHeight,self.viewWidth)

def computeTextsData(positionToTextMap,fHeight,fWidth,viewHeight,viewWidth):
    allVerts = []
    for key, value in positionToTextMap.iteritems():
        vtData = computeTextData(key[0],key[1],fHeight,fWidth,value,viewHeight,viewWidth)
        allVerts.append(vtData)
    return np.concatenate(allVerts,axis=0)
    
def computeTextData(x,y,fHeight,fWidth,text,viewHeight,viewWidth):
    vertices = np.zeros(len(text)*6,[("position",np.float32,2),("uv",np.float32,2)])

    xpos = x
    for i in range(0,len(text)):
        charIndex = ord(text[i])-ord(' ')+16
        vertex_up_left = (xpos, y+fHeight)
        vertex_up_right = (xpos+fWidth, y+fHeight)
        vertex_down_right = (xpos+fWidth, y)
        vertex_down_left  = (xpos, y)
        xpos+=fWidth*0.7

        vertices["position"][i*6]=vertex_up_left
        vertices["position"][i*6+1]=vertex_down_left
        vertices["position"][i*6+2]=vertex_up_right

        vertices["position"][i*6+3]=vertex_down_right
        vertices["position"][i*6+4]=vertex_up_right
        vertices["position"][i*6+5]=vertex_down_left

        uv_x = (charIndex%16)/16.0
        uv_y = 1-(charIndex/16)/16.0

        uv_up_left = (uv_x,   1.0 - (uv_y + 1.0/16.0)  );
        uv_up_right = (uv_x+1.0/16.0,    1.0 - (uv_y + 1.0/16.0)  );
        uv_down_right = (uv_x+1.0/16.0,  1.0 - uv_y )
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

    
