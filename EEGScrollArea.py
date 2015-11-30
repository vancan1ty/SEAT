import sys
from PyQt4 import QtGui
from PyQt4 import QtCore
import CanvasHandler
import DataProcessing
import mne
from mne.time_frequency import tfr_multitaper, tfr_stockwell, tfr_morlet
import numpy as np
from collections import deque

class EEGScrollArea(QtGui.QAbstractScrollArea):
    canvas = None
    def __init__(self,canvas):
        super(EEGScrollArea, self).__init__()
        self.canvas = canvas
        self.setViewport(canvas.native)
        self.horizontalScrollBar().setMinimum(0)
        self.pageStep = canvas.getDisplayWidth()
        self.horizontalScrollBar().setPageStep(self.pageStep) 
        self.horizontalScrollBar().setMaximum(self.canvas.getTotalWidth()-self.pageStep)
        self.canvas.show()

    def resetScrollBarStuff(self):
        self.horizontalScrollBar().setMinimum(0)
        self.pageStep = self.canvas.getDisplayWidth()
        self.horizontalScrollBar().setPageStep(self.pageStep) 
        self.horizontalScrollBar().setMaximum(self.canvas.getTotalWidth()-self.pageStep)

    def resizeEvent (self, QResizeEvent):
        self.viewport().resizeEvent(QResizeEvent);
        areaSize = self.viewport().size();
        self.oldHeight = areaSize.height()
        self.oldWidth = areaSize.width()
        #print "height: {h}, width: {w}".format(h=areaSize.height(),w=areaSize.width());
        self.canvas.native.resize(areaSize.width(),areaSize.height())
        self.canvas.update()

    def scrollContentsBy (self, dx, dy):
        hvalue = self.horizontalScrollBar().value();
        self.canvas.handle_scroll(dx)

    def paintEvent(self, event):
        self.viewport().paintEvent(event)
