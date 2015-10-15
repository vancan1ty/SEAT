#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
[CB 10/13/15] layers of abstraction
EpWindow --> in charge of majority of GUI interaction and window chrome
EEGCanvas --> in charge of majority of functionality relating to rendering data on canvas.  Also contains rawData and various state variables
DataProcessing.py --> contains a variety of utility functions we use to process data

BUGS:
1. Can't handle large datasets!

"""
import sys
from PyQt4 import QtGui
from PyQt4 import QtCore
import CanvasHandler

SAMPLING_RATE=256
START_TIME = 0.0
END_TIME = 6.0

class EpWindow(QtGui.QMainWindow):
    
    def __init__(self):
        super(EpWindow, self).__init__()
        self.initUI()

    def show_about_window(self):
        QtGui.QMessageBox.information(None,"About Epilepsy Modeling","This amazing project\n\nwas created by:\nUtkarsh Garg\nJohnny Farrow\nJustin Jackson\nCurrell Berry\nMichael Long")

    def show_file_dialog(self):
        filePath = QtGui.QFileDialog.getOpenFileName(None,"Choose Dataset to Open", ".", "EEG File (*.edf)")
        self.canvas.loadData(filePath)
        self.populateUICanvas()

    def setupMenus(self):
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

        cutAction = QtGui.QAction('&Cut', self)
        copyAction = QtGui.QAction('&Copy', self)
        pasteAction = QtGui.QAction('&Paste', self)
        editMenu = menubar.addMenu('&Edit')
        editMenu.addAction(cutAction)
        editMenu.addAction(copyAction)
        editMenu.addAction(pasteAction)

        showToolbarAction = QtGui.QAction('&Show Toolbar?', self)
        showEBAction = QtGui.QAction('&Show Events Browser?', self)

        viewMenu = menubar.addMenu('&View')
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
        self.statusBar().showMessage(self.canvas.dSetName + ".   " + str(self.canvas.rawData.times[-1]) + " seconds.")

    def initUI(self):
        """create the various UI elements"""
        #create pulldown menus 
        self.setupMenus()

        self.statusBar()
        
        holderWidget = QtGui.QWidget()
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        grid.setColumnStretch(8,1)

        lowLbl = QtGui.QLabel('Lowpass (hz)')
        grid.addWidget(lowLbl, 0, 0)
        self.lowEdit = QtGui.QLineEdit("")
        grid.addWidget(self.lowEdit, 0, 1)

        highLbl = QtGui.QLabel('Highpass (hz)')
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

        sliderLabel = QtGui.QLabel('Amplitude')
        grid.addWidget(sliderLabel, 1, 0)
        self.sliderValue = QtGui.QLabel()
        grid.addWidget(self.sliderValue, 2, 0)

        self.canvas = CanvasHandler.EEGCanvas(self.startEdit, self.endEdit, self.lowEdit, self.highEdit)

        slider = QtGui.QSlider(QtCore.Qt.Vertical,holderWidget)
        slider.setRange(0,100) #qslider does ints, so we divide by ten to get floats
        grid.addWidget(slider, 3, 0)

        #scroller = QtGui.QScrollArea();
        #scroller.setWidget(c.native)
        grid.addWidget(self.canvas.native, 1, 1, 6, 9)

        QtCore.QObject.connect(slider, QtCore.SIGNAL('valueChanged(int)'), self.onUpdateSliderValue)
        QtCore.QObject.connect(self.startEdit, QtCore.SIGNAL('editingFinished()'), self.onStartEndChanged)
        QtCore.QObject.connect(self.endEdit, QtCore.SIGNAL('editingFinished()'), self.onStartEndChanged)
        QtCore.QObject.connect(self.lowEdit, QtCore.SIGNAL('editingFinished()'), self.onUpdateTextBoxes)
        QtCore.QObject.connect(self.highEdit, QtCore.SIGNAL('editingFinished()'), self.onUpdateTextBoxes)

        slider.setValue(self.canvas.storedAmplitude*10)

        holderWidget.setLayout(grid) 

        self.setCentralWidget(holderWidget)
        self.statusBar().showMessage("Use File->Open to choose a dataset to open")
        self.setGeometry(300, 300, 350, 300)

        self.setWindowTitle('Epilepsy Modeling')    
        self.show()

    def onUpdateSliderValue(self, value):
        rValue = value/10.0
        self.sliderValue.setText(str(rValue))
        self.canvas.onAmplitudeChanged(rValue)

    def onUpdateTextBoxes(self):
        lowPassT = self.lowEdit.text().toDouble()
        highPassT = self.highEdit.text().toDouble()
        self.canvas.onTextBoxesChanged(lowPassT[0],highPassT[0])

    def onStartEndChanged(self):
        startTimeT = self.startEdit.text().toDouble()
        endTimeT = self.endEdit.text().toDouble()
        self.canvas.onStartEndChanged(startTimeT[0],endTimeT[0])

        
        
def main():
    app = QtGui.QApplication(sys.argv)
    ex = EpWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
