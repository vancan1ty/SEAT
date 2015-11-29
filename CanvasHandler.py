# derived from vispy example.
#CB 10/13/2015

import sip
sip.setapi('QString', 2)

from vispy import gloo
from vispy import app
from vispy import scene
from vispy.scene.visuals import Text
import numpy as np
import math
import mne
import mmap
import DataProcessing
from PyQt4 import QtCore
from PyQt4 import QtGui

SAMPLING_RATE=256
START_TIME = 0.0
END_TIME = 6.0

# V["position"] = [[ -0.5, 1, 0], [-0.5, -1, 0],
#                            [0,1, 0],      [0,-1,0],
#                            [0.5, 1, 0], [0.5,-1, 0]]

V = np.zeros(6, [("position", np.float32, 3)])
V["position"] = np.float32((np.random.rand(6,3)*2-1))

V3 = np.zeros(6, [("position", np.float32, 3)])
V3["position"] = np.float32([[-0.2,0.2,0],[0.2,0.2,0],[-0.2,-0.2,0],
                                                           [-0.2,-0.2,0],[0.2,-0.2,0],[0.2,0.2,0]])

zoombox_fragment_shader = """
void main()
{
    gl_FragColor = vec4(0.7, 0.7, 0.0, 0.1);
}
"""

prog2_vertex_shader = """
attribute vec3 position;
void main()
{
    gl_Position = vec4(position, 1.0);
}
"""

prog2_fragment_shader = """
void main()
{
    gl_FragColor = vec4(0.0, 0.5, 0.0, 0.1);
}
"""

SERIES_VERT_SHADER = """
#version 120

// y coordinate of the position.
attribute float a_position;

// row, col, and time index.
attribute vec3 a_index;
varying vec3 v_index;

// 2D scaling factor (zooming).
uniform vec2 u_scale;

// Size of the table.
uniform vec2 u_size;

// Number of samples per signal.
uniform float u_n;

// Color.
attribute vec3 a_color;
varying vec4 v_color;

// Varying variables used for clipping in the fragment shader.
varying vec2 v_position;
varying vec4 v_ab;

void main() {
    float nrows = u_size.x;
    float ncols = u_size.y;

    // Compute the x coordinate from the time index.
    float x = -1 + 2*a_index.z / (u_n-1);
    vec2 position = vec2(x - (1 - 1 / u_scale.x), a_position);

    // Find the affine transformation for the subplots.
    vec2 a = vec2(1./ncols, 1./nrows)*.9;
    vec2 b = vec2(-1 + 2*(a_index.x+.5) / ncols,
                  -1 + 2*(a_index.y+.5) / nrows);
    // Apply the static subplot transformation + scaling.
    gl_Position = vec4(a*u_scale*position+b, 0.0, 1.0);

    v_color = vec4(a_color, 1.);
    v_index = a_index;

    // For clipping test in the fragment shader.
    v_position = gl_Position.xy;
    v_ab = vec4(a, b);
}
"""

SERIES_FRAG_SHADER = """
#version 120

varying vec4 v_color;
varying vec3 v_index;

varying vec2 v_position;
varying vec4 v_ab;

void main() {
    gl_FragColor = v_color;

    // Discard the fragments between the signals (emulate glMultiDrawArrays).
    if ((fract(v_index.x) > 0.) || (fract(v_index.y) > 0.))
        discard;

    // Clipping test.
    vec2 test = abs((v_position.xy-v_ab.zw)/v_ab.xy);
    if ((test.x > 1) || (test.y > 1))
        discard;
}
"""

class EEGCanvas(app.Canvas):
    """ defines a class which encapsulates all information and control relating to the display of EEG data on the canvas

   """
    def __init__(self, startEdit, endEdit, lowEdit, highEdit):
        app.Canvas.__init__(self, title='Use your wheel to scroll!',
                            keys='interactive')
        self.startEdit = startEdit
        self.endEdit = endEdit
        self.lowEdit = lowEdit
        self.highEdit = highEdit
        self.startTime = START_TIME
        self.endTime = END_TIME
        self.storedAmplitude = 1.0
        self.lowPass = 2.0
        self.highPass = 70.0
        self.numchannels = 0 #maybe don't need this because re-rendering

        self.channelPositions = self.getChannelPositions()
        self.mode = 'select'
        self.xScale = 1.
        self.yScale = 1.
        self.min_scale = 0.00005
        self.max_scale = 10
        self.dragZoom = False

        self.show()

    def setupDataDisplay(self):
        """requires that you have already set a number of things on self"""
        self.displayData = DataProcessing.getDisplayData(self.rawData, self.startTime, self.endTime, self.storedAmplitude, self.lowPass, self.highPass)
        self.setupZoom(self.displayData)
        self.channels = self.rawData.ch_names
        self.canvas = scene.SceneCanvas(keys='interactive')
        #print(self.channels)
        self.program = gloo.Program(SERIES_VERT_SHADER, SERIES_FRAG_SHADER)
        self.vertices = gloo.VertexBuffer(V)
        self.zoomBoxBuffer = gloo.VertexBuffer(V3)
        self.prog2 = gloo.Program(prog2_vertex_shader, prog2_fragment_shader)
        self.prog2.bind(self.vertices)

        self.progZoom = gloo.Program(prog2_vertex_shader, zoombox_fragment_shader)
        self.progZoom.bind(self.zoomBoxBuffer)

        self.setupZoomStep2()
        gloo.set_viewport(0, 0, *self.physical_size)
        self.updateTextBoxes()

        self.dragZoom = False
        self.oldPos = None
        self.newPos = None
        self.orig = None
        self.new = None
        self.posDiff = None
        self.events.mouse_press.connect((self, 'mouse_press'))
        self.events.mouse_release.connect((self, 'mouse_release'))
        self.events.mouse_move.connect((self, 'on_mouse_move'))

#      self._timer = app.Timer('auto', connect=self.on_timer, start=True)

        gloo.set_state(clear_color='black', blend=True,
                       blend_func=('src_alpha', 'one_minus_src_alpha'))
        self.update()

    def loadData(self,filepath):
        self.dSetName = filepath.split("/")[-1]
        self.rawData = mne.io.read_raw_edf(str(filepath),preload=True)
        self.setupDataDisplay()

    def setupZoom(self,displayData):
        """ this function should be called whenever a "zoom" operation is performed"""
        # Number of cols and rows in the table.
        self.nrows = len(displayData[0])
        self.ncols = 1

        # Number of signals.
        self.numSignals = self.nrows*self.ncols

        # Number of samples per signal.
        self.samplesPerSignal = len(displayData[1])

        # Generate the signals as a (m, n) array.
        #y = amplitudes * np.random.randn(m, n).astype(np.float32)
        self.signalData = np.float32(10000*np.array(displayData[0]))

        # Color of each vertex (TODO: make it more efficient by using a GLSL-based
        # color map and the index).
        self.color = np.repeat(np.random.uniform(size=(self.numSignals, 3), low=.5, high=.9),
                        self.samplesPerSignal, axis=0).astype(np.float32)

        # Signal 2D index of each vertex (row and col) and x-index (sample index
        # within each signal).
        self.index = np.c_[np.repeat(np.repeat(np.arange(self.ncols), self.nrows), self.samplesPerSignal),
                    np.repeat(np.tile(np.arange(self.nrows), self.ncols), self.samplesPerSignal),
                    np.tile(np.arange(self.samplesPerSignal), self.numSignals)].astype(np.float32)


    def setupZoomStep2(self):
        #print "y: {y}, color: {c}, index: {i}".format(y=y.shape,c=color.shape,i=index.shape)
        self.program['a_position'] = self.signalData.reshape(-1, 1)
        self.program['a_color'] = self.color
        self.program['a_index'] = self.index
        self.program['u_scale'] = (1., 1.)
        self.program['u_size'] = (self.nrows, self.ncols)
        self.program['u_n'] = self.samplesPerSignal
        #print "done with setup zoom"


    def getChannelPositions(self):
        """
        TODO:
        self.program['u_size'][0] / self.physical_size[1]

        This will get the amount of vertical space each channel
        has. This gives us a way to determine which spaces are
        selected in order to zoom.
        """

    def setMode(self, mode):
        self.mode = mode

    def zoom(self, xFactor, yFactor):
        # gloo.set_viewport(orig[0], orig[1], size[0], size[1])
        # self.program['resolution'] = [size[0], size[1]]
        self.xScale *= xFactor
        self.yScale *= yFactor
        self.xScale = max(min(self.xScale, self.max_scale), self.min_scale)
        self.yScale = max(min(self.yScale, self.max_scale), self.min_scale)
        self.program["u_scale"] = (self.xScale, self.yScale)

        print " "

    def on_resize(self, event):
        gloo.set_viewport(0, 0, *event.physical_size)

    # def on_mouse_wheel(self, event):
    #     dx = np.sign(event.delta[1]) * .05
    #     scale_x, scale_y = self.program['u_scale']
    #     #print("scale_x: {scale_x}, scale_y: {scale_y}".format(scale_x=scale_x, scale_y=scale_y))
    #     scale_x_new, scale_y_new = (scale_x * math.exp(2.5*dx),
    #                                 scale_y * math.exp(0.0*dx))
    #     self.program['u_scale'] = (max(1, scale_x_new), max(1, scale_y_new))
    #     self.update()
    def on_mouse_wheel(self, event):
        dx = -np.sign(event.delta[1])
        if((self.startTime + dx) > 0.5):
            self.startTime += dx
            self.endTime += dx
        elif ((self.startTime+dx) >= 0.0): #CB handle edge cases as we get close to beginning of dataset
            self.startTime += dx
            self.endTime += dx
        olen=len(self.displayData[0][0])
        self.displayData = DataProcessing.getDisplayData(self.rawData, self.startTime, self.endTime, self.storedAmplitude, self.lowPass, self.highPass)
        if(len(self.displayData[0][0]) != olen):
            self.onStartEndChanged(self.startTime,self.endTime)
        self.signalData = np.float32(10000*np.array(self.displayData[0]))
        self.program['a_position'] = self.signalData.reshape(-1, 1)
        self.updateTextBoxes()
        self.update()

    def onAmplitudeChanged(self, nAmplitude):
        self.storedAmplitude = nAmplitude;
        self.displayData = DataProcessing.getDisplayData(self.rawData, self.startTime, self.endTime, self.storedAmplitude, self.lowPass, self.highPass)
        self.signalData = np.float32(10000*np.array(self.displayData[0]))
        self.program['a_position'] = self.signalData.reshape(-1, 1)
        self.update()

    def onTextBoxesChanged(self, lowPass, highPass):
        self.lowPass = lowPass;
        self.highPass = highPass;
        print "startTime: {s}, endTime: {e}, lowPass: {l}, highPass: {h}".format(s=self.startTime, e=self.endTime, l=self.lowPass, h=self.highPass)
        self.displayData = DataProcessing.getDisplayData(self.rawData, self.startTime, self.endTime, self.storedAmplitude, self.lowPass, self.highPass)
        self.signalData = np.float32(10000*np.array(self.displayData[0]))
        self.program['a_position'] = self.signalData.reshape(-1, 1)
        self.update()

    def onStartEndChanged(self, startTime, endTime):
        self.startTime = startTime;
        self.endTime = endTime;
        self.displayData = DataProcessing.getDisplayData(self.rawData, self.startTime, self.endTime, self.storedAmplitude, self.lowPass, self.highPass)
        self.setupZoom(self.displayData)
        # self.program.delete()
        # self.program = gloo.Program(SERIES_VERT_SHADER, SERIES_FRAG_SHADER)
        self.setupZoomStep2()
        self.update()

    def updateTextBoxes(self):
        #print "self.startTime: {s}".format(s=self.startTime)
        self.startEdit.setText(str(self.startTime))
        self.endEdit.setText(str(self.endTime))
        self.lowEdit.setText(str(self.lowPass))
        self.highEdit.setText(str(self.highPass))

    def mouse_press(self, event):
        self.oldPos = (float(event.pos[0])/self.size[0]*2-1, -((float(event.pos[1])/self.size[1])*2-1))
        self.orig = (event.pos[0], event.pos[1])
        if(self.mode == 'zoom'):
            self.dragZoom = True

        self.update()

    def on_mouse_move(self, event):
        #print "self.size {s}".format(s=self.size)
        self.newPos = ((float(event.pos[0])/self.size[0])*2-1, -((float(event.pos[1])/self.size[1])*2-1))
        self.new = (event.pos[0], event.pos[1])
        self.update()

    def mouse_release(self, event):
        ## Uncomment to work on zoom
        # if(self.mode == 'zoom'):
        #     xDiff = self.new[0]-self.orig[0]
        #     yDiff = self.new[1]-self.orig[1]
        #     xFactor = 1. / (float(abs(xDiff)) / float(self.physical_size[0]))
        #     yFactor = 1. / (float(abs(yDiff)) / float(self.physical_size[1]))
        #     self.zoom(xFactor, yFactor)
        self.dragZoom = False
        self.update()
        #print self.program['u_size'][0]
        #print self.physical_size[1] #height

    # def on_timer(self, event):
    #     """Add some data at the end of each signal (real-time signals)."""
    #     k = 10
    #     y[:, :-k] = y[:, k:]
    #     y[:, -k:] = amplitudes * np.random.randn(m, k)

    #     self.program['a_position'].set_data(y.ravel().astype(np.float32))
    #     self.update()

    def on_draw(self, event):
        gloo.clear()
        if (self.dragZoom and self.mode == 'zoom'):
            xDiff = self.newPos[0]-self.oldPos[0]
            yDiff = self.newPos[1]-self.oldPos[1]
            V4 = np.zeros(6, [("position", np.float32, 3)])
            V4["position"] = np.float32([[self.oldPos[0],self.oldPos[1],0],
                                                           [self.oldPos[0]+xDiff,self.oldPos[1],0],
                                                           [self.oldPos[0],self.oldPos[1]+yDiff,0],
                                                           [self.newPos[0],self.newPos[1],0],
                                                           [self.newPos[0]-xDiff,self.newPos[1],0],
                                                           [self.newPos[0],self.newPos[1]-yDiff,0]])
            self.zoomBoxBuffer.set_data(V4)
            self.progZoom.draw("triangles")
        else:
             V2 = np.zeros(6, [("position", np.float32, 3)])
             V2["position"] = np.float32((np.random.rand(6,3)*2-1))
             self.vertices.set_data(V2)
             #self.prog2.draw('triangles')
        self.program.draw('line_strip')

if __name__ == '__main__':
    c = EEGCanvas()
    app.run()

#c = Canvas()
#app.run()
