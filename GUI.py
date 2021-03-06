#!/usr/bin/python
# -*- coding: utf-8 -*-

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

"""
[CB 10/13/15] layers of abstraction
EpWindow --> in charge of majority of GUI interaction and window chrome
EEGCanvas --> in charge of majority of functionality relating to rendering data on canvas.  Also contains rawData and various state variables
DataProcessing.py --> contains a variety of utility functions we use to process data.  also contains matplotlib plotting fns.

BUGS:
1. Can't handle large datasets!

"""
import argparse
import os
os.environ['QT_API'] = 'pyqt'
import sip
sip.setapi("QString", 2)
sip.setapi("QVariant", 2)

import sys
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtGui import QListWidgetItem, QListWidget, QDialog, QPushButton
import CanvasHandler
import DataProcessing
import mne
from mne.time_frequency import tfr_multitaper, tfr_stockwell, tfr_morlet
import numpy as np
from QIPythonWidget import QIPythonWidget
from EEGScrollArea import EEGScrollArea

SAMPLING_RATE=256
START_TIME = 0.0
END_TIME = 6.0


class EpWindow(QtGui.QMainWindow):

    def __init__(self, filePath):
        super(EpWindow, self).__init__()
        self.initUI()
        #CB default initialization below
        self.canvas.loadData(filePath)
        self.populateUICanvas()
        self.ch1Spikes = None


    def runSpikeDetection(self):
        """runs stupid spike detector on only 1st channel"""
        channelIndex = self.canvas.indices[0]
        self.rawCh1Spikes = DataProcessing.stupidIdentifySpikes(self.canvas.rawData[channelIndex,:][0],cutoff=float(self.thresholdEdit.text()))
        self.ch1Spikes = self.canvas.rawData.index_as_time(self.rawCh1Spikes)
        self.canvas.annotationTimes = self.ch1Spikes[0]
        QtGui.QMessageBox.information(None,"Report","{d} spikes found.\n\n{i}".format(d=len(self.ch1Spikes[0]),i=self.ch1Spikes[0]))
        # if self.ch1Spikes is None:
        #     self.ch1Spikes = peakFinder.randomLists()
        #     QtGui.QMessageBox.information(None,"Report","{d} spikes found.".format(d=len(self.ch1Spikes[0])))
        # print self.ch1Spikes

        # ch1Spikes = DataProcessing.stupidIdentifySpikes(self.canvas.rawData[1,:][0],cutoff=self.thresholdEdit.text().toDouble()[0])
        # print ch1Spikes[0]
        # QtGui.QMessageBox.information(None,"Report","{d} spikes found.".format(d=len(ch1Spikes[0])))


    def setModeSelect(self):
        self.canvas.setMode('select')

    def setModeZoom(self):
        self.canvas.setMode('zoom')

    def show_about_window(self):
        QtGui.QMessageBox.information(None,"About SEAT",
"""This project was written as a GT 2015 Capstone project.  Team members were as follows:

Developers: Currell Berry, Justin Jackson
Contributor: Michael Long
Team Members: Johnny Farrow, Utkarsh Garg.

Please see the README.md file for more information about this project.""") 

    def show_file_dialog(self):
        filePath = QtGui.QFileDialog.getOpenFileName(None,"Choose Dataset to Open", ".", "EEG File (*.edf)")
        print filePath
        self.canvas.loadData(filePath)
        self.populateUICanvas()
        self.ch1Spikes = None

    def show_spectral_map(self):
        start = self.canvas.startTime
        end = self.canvas.endTime
        self.canvas.rawData.plot_psd(start,end,picks=self.canvas.indices)

    def show_tfr_plot(self):
        DataProcessing.generate_and_plot_waveletAnalysis(self.canvas.rawData,self.canvas.indices[0],self.canvas.startTime,self.canvas.endTime,self.canvas.samplingRate)

    def buildChannelSelector(self):
        self.channelChooser = QtGui.QDockWidget("Select Channels")
        self.channelsBox = QtGui.QWidget(self.channelChooser)

        self.channelList = QtGui.QListWidget()
        self.channelList.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        pushButtonOK = QtGui.QPushButton()
        pushButtonOK.setText("Update")
        pushButtonOK.clicked.connect(self.on_pushButtonOK_clicked)

        layoutVertical = QtGui.QVBoxLayout()
        layoutVertical.setContentsMargins(0,0,0,0)
        self.channelsBox.setLayout(layoutVertical)
        layoutVertical.addWidget(self.channelList)
        layoutVertical.addWidget(pushButtonOK)

        self.channelChooser.setWidget(self.channelsBox)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea,self.channelChooser)
        self.toggleChannelSelector = self.channelChooser.toggleViewAction()

    def updateChannelSelector(self):
        self.channelList.clear()
        channels = self.canvas.channels
        for i in range(0,len(channels)-1):
            item = QtGui.QListWidgetItem(channels[i])
            self.channelList.addItem(item)
            if i in self.canvas.indices:
                item.setSelected(True)
                #print item.isSelected()


    def on_pushButtonOK_clicked(self):
        self.indices = []
        for item in self.channelList.selectedItems():
            self.indices.append(self.canvas.channels.index(item.text()))

        self.canvas.setupDataDisplay(self.indices)
        print self.indices

    def setupMenus(self, togglePyDock,toggleChannelSelector):
        """set up menubar menus"""
        openAction = QtGui.QAction('&Open', self)
        openAction.setShortcut('Ctrl+o')
        openAction.setStatusTip('Choose Dataset to Open')
        openAction.triggered.connect(self.show_file_dialog)

        exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openAction)
        fileMenu.addAction(exitAction)

        sMapAction = QtGui.QAction('&Show Spectral Map', self)
        sMapAction.setShortcut('Ctrl+m')
        sMapAction.setStatusTip('Calculate a power-frequency spectral map for the dataset over the current time period.')
        sMapAction.triggered.connect(self.show_spectral_map)

        tfMapAction = QtGui.QAction('&Show Time-Frequency Plot', self)
        tfMapAction.setShortcut('Ctrl+t')
        tfMapAction.setStatusTip('Calculate a time-frequency plot using Morlet transform.')
        tfMapAction.triggered.connect(self.show_tfr_plot)

        cutAction = QtGui.QAction('&Cut', self)
        copyAction = QtGui.QAction('&Copy', self)
        pasteAction = QtGui.QAction('&Paste', self)
        editMenu = menubar.addMenu('&Edit')
        editMenu.addAction(tfMapAction)
        editMenu.addAction(sMapAction)
        editMenu.addAction(cutAction)
        editMenu.addAction(copyAction)
        editMenu.addAction(pasteAction)

        #scAction = QtGui.QAction('&Select Channels', self)
        #scAction.triggered.connect(self.buildChannelSelector)
        togglePyDock.setShortcut("Ctrl-r")
        showToolbarAction = QtGui.QAction('&Show Toolbar?', self)
        showEBAction = QtGui.QAction('&Show Events Browser?', self)

        viewMenu = menubar.addMenu('&View')
        viewMenu.addAction(toggleChannelSelector)
        viewMenu.addAction(togglePyDock)
        viewMenu.addAction(showToolbarAction)
        viewMenu.addAction(showEBAction)

        rcAction = QtGui.QAction('&Raw Channels', self)
        avgAction = QtGui.QAction('&Channels vs Avg', self)
        bananaAction = QtGui.QAction('&Banana View', self)
        montageSelect = viewMenu.addMenu("&Select View")
        montageSelect.addAction(rcAction)
        montageSelect.addAction(avgAction)
        montageSelect.addAction(bananaAction)

        helpMenu = menubar.addMenu('&Help')
        aboutAction = QtGui.QAction('&About', self)
        aboutAction.triggered.connect(self.show_about_window)
        helpMenu.addAction(aboutAction)

    def populateUICanvas(self):
        """ called after we have loaded rawData into canvas.  sets the values and such on the various elements """
        freqValidator = QtGui.QDoubleValidator(0.0,SAMPLING_RATE/2.0,10)
        timeValidator = QtGui.QDoubleValidator(0.0, self.canvas.rawData.times[-1], 10)

        self.lowEdit.setValidator(freqValidator)
        self.highEdit.setValidator(freqValidator)
        self.startEdit.setValidator(timeValidator)
        self.endEdit.setValidator(timeValidator)
        self.canvas.setupDataDisplay()
        self.updateChannelSelector()
        self.statusBar().showMessage(self.canvas.dSetName + ".   " + str(self.canvas.rawData.times[-1]) + " seconds.")

    def initUI(self):
        """create the various UI elements"""

        self.statusBar()

        holderWidget = QtGui.QWidget()
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        grid.setColumnStretch(8,1)

        lowLbl = QtGui.QLabel('Low (hz)')
        grid.addWidget(lowLbl, 0, 0)
        self.lowEdit = QtGui.QLineEdit("")
        grid.addWidget(self.lowEdit, 0, 1)

        highLbl = QtGui.QLabel('High (hz)')
        grid.addWidget(highLbl, 0, 2)
        self.highEdit = QtGui.QLineEdit("")
        grid.addWidget(self.highEdit, 0, 3)

        startLbl = QtGui.QLabel('Start Time')
        grid.addWidget(startLbl, 0, 4)
        self.startEdit = QtGui.QLineEdit("")
        grid.addWidget(self.startEdit, 0, 5)

        endLbl = QtGui.QLabel('End Time')
        grid.addWidget(endLbl, 0, 6)
        self.endEdit = QtGui.QLineEdit("")
        grid.addWidget(self.endEdit, 0, 7)

        # modeLbl = QtGui.QLabel('Mode:')
        # grid.addWidget(modeLbl, 0, 9)
        # selectButton = QtGui.QPushButton('Select', holderWidget)
        # grid.addWidget(selectButton, 0, 10)
        # zoomButton = QtGui.QPushButton('Zoom', holderWidget)
        # grid.addWidget(zoomButton, 0, 11)

        sliderLabel = QtGui.QLabel('Amplitude')
        grid.addWidget(sliderLabel, 1, 0)
        self.sliderValue = QtGui.QLabel()
        grid.addWidget(self.sliderValue, 2, 0)

        self.canvas = CanvasHandler.EEGCanvas(self.startEdit, self.endEdit, self.lowEdit, self.highEdit)

        slider = QtGui.QSlider(QtCore.Qt.Vertical,holderWidget)
        slider.setRange(0,100) #qslider does ints, so we divide by ten to get floats
        grid.addWidget(slider, 3, 0,alignment=QtCore.Qt.AlignHCenter)

        spikeLbl = QtGui.QLabel('Threshold')
        grid.addWidget(spikeLbl, 4, 0)
        self.thresholdEdit = QtGui.QLineEdit("0.001")
        self.thresholdEdit.setMaximumWidth(80)
        tValidator = QtGui.QDoubleValidator(0.0,1.0,12)
        self.thresholdEdit.setValidator(tValidator)

        grid.addWidget(self.thresholdEdit, 5, 0)

        spikeButton = QtGui.QPushButton('Find Spikes', holderWidget)
        grid.addWidget(spikeButton, 6, 0)

        self.scroller = EEGScrollArea(self.canvas)
        self.canvas.parentScroller = self.scroller

        #scroller = QtGui.QScrollArea();
        #scroller.setWidget(c.native)
        grid.addWidget(self.scroller, 1, 1, 6, 11)

        QtCore.QObject.connect(slider, QtCore.SIGNAL('valueChanged(int)'), self.onUpdateSliderValue)
        QtCore.QObject.connect(self.startEdit, QtCore.SIGNAL('editingFinished()'), self.onStartEndChanged)
        QtCore.QObject.connect(self.endEdit, QtCore.SIGNAL('editingFinished()'), self.onStartEndChanged)
        QtCore.QObject.connect(self.lowEdit, QtCore.SIGNAL('editingFinished()'), self.onUpdateTextBoxes)
        QtCore.QObject.connect(self.highEdit, QtCore.SIGNAL('editingFinished()'), self.onUpdateTextBoxes)
        QtCore.QObject.connect(spikeButton, QtCore.SIGNAL('clicked()'), self.runSpikeDetection)
        # QtCore.QObject.connect(selectButton, QtCore.SIGNAL('clicked()'), self.setModeSelect)
        # QtCore.QObject.connect(zoomButton, QtCore.SIGNAL('clicked()'), self.setModeZoom)

        slider.setValue(self.canvas.storedAmplitude*10)

        self.pythonScripter = QIPythonWidget(customBanner=
"""
Welcome to SEAT.
All functionality of python and this application is available through this command line
the variable 'window' contains a reference to your current window
here are some commands to get you started:
window.canvas.quickTextDraw('hello world',0,0); window.canvas.update();
window.canvas.displayData

happy scripting
""")
        self.pythonScripter.pushVariables({"window": self})
        #self.pythonScripter.executeCommand(printHelpText)

        pyDockWidget = QtGui.QDockWidget("Python REPL")
        pyDockWidget.setWidget(self.pythonScripter)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea,pyDockWidget)
        toggleViewPyDock = pyDockWidget.toggleViewAction()

        holderWidget.setLayout(grid)

        self.setCentralWidget(holderWidget)
        self.statusBar().showMessage("Use File->Open to choose a dataset to open")

        #create pulldown menus

        self.buildChannelSelector()
        self.setupMenus(toggleViewPyDock,self.toggleChannelSelector)

        self.setGeometry(50, 50, 350, 300)

        self.setWindowTitle('Simple EEG Analysis Tool')
        self.resize(1200, 700)
        self.show()


    def onUpdateSliderValue(self, value):
        rValue = value/10.0
        self.sliderValue.setText(str(rValue))
        self.canvas.onAmplitudeChanged(rValue)


    def onUpdateTextBoxes(self):
        lowPassT = float(self.lowEdit.text())
        highPassT = float(self.highEdit.text())
        self.canvas.onTextBoxesChanged(lowPassT,highPassT)

    def onStartEndChanged(self):
        startTimeT = float(self.startEdit.text())
        endTimeT = float(self.endEdit.text())
        self.scroller.setValue(startTimeT)
        self.canvas.onStartEndChanged(startTimeT,endTimeT)

def main():
    parser = argparse.ArgumentParser(description='Simple EEG Analysis Tool.')
    parser.add_argument('-f', metavar='FILE', type=str, nargs=1,
                        help='EDF file to open, leave blank if none desired', default=["demodata/BC_TEST.edf"])
    args = parser.parse_args()
    print args.f[0]

    app = QtGui.QApplication(sys.argv)
    ex = EpWindow(args.f[0])
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
