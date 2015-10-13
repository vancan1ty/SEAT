#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: gallery 2
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Multiple real-time digital signals with GLSL-based clipping.
"""

from vispy import gloo
from vispy import app
from vispy import scene
from vispy.scene.visuals import Text
import numpy as np
import math
import mne
import simple
from PyQt4 import QtCore

SAMPLING_RATE=256
START_TIME = 0.0
END_TIME = 6.0

def loadData():
    global rawData,dSetName
    dSetName = "BASHAREE_TEST"
    rawData = mne.io.read_raw_edf("../EEGDATA/CAPSTONE_AB/BASHAREE_TEST.edf",preload=True)

def setupZoom(displayData):
    """ this function should be called whenever a "zoom" operation is performed"""
    global nrows, ncols, m, n, y, color, index
    # Number of cols and rows in the table.
    nrows = len(displayData[0])
    ncols = 1

    # Number of signals.
    m = nrows*ncols

    # Number of samples per signal.
    n = len(displayData[1])

    # Various signal amplitudes.
    #amplitudes = .1 + .2 * np.random.rand(m, 1).astype(np.float32)
    #amplitudes = 1*np.ones((m,1),dtype=np.float32)

    # Generate the signals as a (m, n) array.
    #y = amplitudes * np.random.randn(m, n).astype(np.float32)
    y = np.float32(10000*np.array(displayData[0]))

    # Color of each vertex (TODO: make it more efficient by using a GLSL-based
    # color map and the index).
    color = np.repeat(np.random.uniform(size=(m, 3), low=.5, high=.9),
                    n, axis=0).astype(np.float32)

    # Signal 2D index of each vertex (row and col) and x-index (sample index
    # within each signal).
    index = np.c_[np.repeat(np.repeat(np.arange(ncols), nrows), n),
                np.repeat(np.tile(np.arange(nrows), ncols), n),
                np.tile(np.arange(n), m)].astype(np.float32)

VERT_SHADER = """
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

FRAG_SHADER = """
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

class Canvas(app.Canvas):
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
        self.displayData = simple.getDisplayData(rawData, self.startTime, self.endTime, self.storedAmplitude, self.lowPass, self.highPass)
        setupZoom(self.displayData)
        self.channels = rawData.ch_names
        self.canvas = scene.SceneCanvas(keys='interactive')
        print(self.channels)
        self.program = gloo.Program(VERT_SHADER, FRAG_SHADER)
        self.setupZoomStep2()
        gloo.set_viewport(0, 0, *self.physical_size)

        #self.pressed = False
        self.events.mouse_press.connect((self, 'mouse_press'))
        self.events.mouse_release.connect((self, 'mouse_release'))
        #self.events.mouse_move.connect((self, 'on_mouse_move'))

#      self._timer = app.Timer('auto', connect=self.on_timer, start=True)

        gloo.set_state(clear_color='black', blend=True,
                       blend_func=('src_alpha', 'one_minus_src_alpha'))

        self.show()

    def setupZoomStep2(self):
        #print "y: {y}, color: {c}, index: {i}".format(y=y.shape,c=color.shape,i=index.shape)
        self.program['a_position'] = y.reshape(-1, 1)
        self.program['a_color'] = color
        self.program['a_index'] = index
        self.program['u_scale'] = (1., 1.)
        self.program['u_size'] = (nrows, ncols)
        self.program['u_n'] = n
        #print "done with setup zoom"

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
        dx = np.sign(event.delta[1])
        if((self.startTime + dx) > 0.5):
            self.startTime += dx
            self.endTime += dx
        elif ((self.startTime+dx) >= 0.0): #CB handle edge cases as we get close to beginning of dataset
            self.startTime += dx
            self.endTime += dx
        olen=len(self.displayData[0][0])
        self.displayData = simple.getDisplayData(rawData, self.startTime, self.endTime, self.storedAmplitude, self.lowPass, self.highPass)
        if(len(self.displayData[0][0]) != olen):
            self.onStartEndChanged(self.startTime,self.endTime)
        y = np.float32(10000*np.array(self.displayData[0]))
        self.program['a_position'] = y.reshape(-1, 1)
        self.updateTextBoxes()
        self.update()

    def onAmplitudeChanged(self, nAmplitude):
        self.storedAmplitude = nAmplitude;
        self.displayData = simple.getDisplayData(rawData, self.startTime, self.endTime, self.storedAmplitude, self.lowPass, self.highPass)
        y = np.float32(10000*np.array(self.displayData[0]))
        self.program['a_position'] = y.reshape(-1, 1)
        self.update()

    def onTextBoxesChanged(self, lowPass, highPass):
        self.lowPass = lowPass;
        self.highPass = highPass;
        print "startTime: {s}, endTime: {e}, lowPass: {l}, highPass: {h}".format(s=self.startTime, e=self.endTime, l=self.lowPass, h=self.highPass)
        self.displayData = simple.getDisplayData(rawData, self.startTime, self.endTime, self.storedAmplitude, self.lowPass, self.highPass)
        y = np.float32(10000*np.array(self.displayData[0]))
        self.program['a_position'] = y.reshape(-1, 1)
        self.update()

    def onStartEndChanged(self, startTime, endTime):
        self.startTime = startTime;
        self.endTime = endTime;
        self.displayData = simple.getDisplayData(rawData, self.startTime, self.endTime, self.storedAmplitude, self.lowPass, self.highPass)
        setupZoom(self.displayData)
        # self.program.delete()
        # self.program = gloo.Program(VERT_SHADER, FRAG_SHADER)
        self.setupZoomStep2()
        self.update()

    def updateTextBoxes(self):
        #print "self.startTime: {s}".format(s=self.startTime)
        self.startEdit.setText(QtCore.QString.number(self.startTime,'f',1))
        self.endEdit.setText(QtCore.QString.number(self.endTime,'f',1))
        self.lowEdit.setText(QtCore.QString.number(self.lowPass,'f',1))
        self.highEdit.setText(QtCore.QString.number(self.highPass,'f',1))

    def mouse_press(self, event):
        #self.pressed = True
        self.oldPos = (event.pos[0], event.pos[1])

    def mouse_release(self, event):
        #self.pressed = False
        self.newPos = (event.pos[0], event.pos[1])
        """
        CALL ZOOM IN FUNCTION WITH OLDPOS AND NEWPOS COORDS!
        """

        """
    def on_mouse_move(self, event):
        if(self.pressed):
            print(event[0])
        """

    # def on_timer(self, event):
    #     """Add some data at the end of each signal (real-time signals)."""
    #     k = 10
    #     y[:, :-k] = y[:, k:]
    #     y[:, -k:] = amplitudes * np.random.randn(m, k)

    #     self.program['a_position'].set_data(y.ravel().astype(np.float32))
    #     self.update()

    def on_draw(self, event):
        gloo.clear()
        self.program.draw('line_strip')

if __name__ == '__main__':
    c = Canvas()
    app.run()

#c = Canvas()
#app.run()
