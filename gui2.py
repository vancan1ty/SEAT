#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui
from PyQt4 import QtCore
import signalsdemo2


def show_about_window():
    QtGui.QMessageBox.information(None,"About Epilepsy Modeling","This amazing project\n\nwas created by:\nUtkarsh Garg\nJohnny Farrow\nJustin Jackson\nCurrell Berry\nMichael Long")
        
class Example(QtGui.QMainWindow):
    
    def __init__(self):
        super(Example, self).__init__()
        
        self.initUI()

    def setupMenus(self):

        exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
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
        aboutAction.triggered.connect(show_about_window)
        helpMenu.addAction(aboutAction)


    def initUI(self):
        #create gui widgets, top to bottom, little to big.

        #create pulldown menus 
        self.setupMenus()

        self.statusBar()
        
        holderWidget = QtGui.QWidget()
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        grid.setColumnStretch(8,1)

        validator = QtGui.QDoubleValidator(0.0,128.0,10)

        lowLbl = QtGui.QLabel('Lowpass (hz)')
        grid.addWidget(lowLbl, 0, 0)
        self.lowEdit = QtGui.QLineEdit("2.0")
        self.lowEdit.setValidator(validator)
        grid.addWidget(self.lowEdit, 0, 1)

        highLbl = QtGui.QLabel('Highpass (hz)')
        grid.addWidget(highLbl, 0, 2)
        self.highEdit = QtGui.QLineEdit("70.0")
        self.highEdit.setValidator(validator)
        grid.addWidget(self.highEdit, 0, 3)

        startLbl = QtGui.QLabel('Start Time')
        grid.addWidget(startLbl, 0, 4)
        self.startEdit = QtGui.QLineEdit("20.0")
        grid.addWidget(self.startEdit, 0, 5)

        endLbl = QtGui.QLabel('End Time')
        grid.addWidget(endLbl, 0, 6)
        self.endEdit = QtGui.QLineEdit("30.0")
        grid.addWidget(self.endEdit, 0, 7)

        sliderLabel = QtGui.QLabel('Amplitude')
        grid.addWidget(sliderLabel, 1, 0)
        self.sliderValue = QtGui.QLabel()
        grid.addWidget(self.sliderValue, 2, 0)

        slider = QtGui.QSlider(QtCore.Qt.Vertical,holderWidget)
        slider.setRange(0,100) #qslider does ints, so we divide by ten to get floats
        grid.addWidget(slider, 3, 0)

        self.canvas = signalsdemo2.Canvas(self.startEdit, self.endEdit, self.lowEdit, self.highEdit)
        #scroller = QtGui.QScrollArea();
        #scroller.setWidget(c.native)
        grid.addWidget(self.canvas.native, 1, 1, 6, 9)

        QtCore.QObject.connect(slider, QtCore.SIGNAL('valueChanged(int)'), self.onUpdateSliderValue)
        QtCore.QObject.connect(self.startEdit, QtCore.SIGNAL('editingFinished()'), self.onUpdateTextBoxes)
        QtCore.QObject.connect(self.endEdit, QtCore.SIGNAL('editingFinished()'), self.onUpdateTextBoxes)
        QtCore.QObject.connect(self.lowEdit, QtCore.SIGNAL('editingFinished()'), self.onUpdateTextBoxes)
        QtCore.QObject.connect(self.highEdit, QtCore.SIGNAL('editingFinished()'), self.onUpdateTextBoxes)

        slider.setValue(self.canvas.storedAmplitude*10)

        holderWidget.setLayout(grid) 

        self.setCentralWidget(holderWidget)
        self.statusBar().showMessage('Ready')
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
        startTimeT = self.startEdit.text().toDouble()
        endTimeT = self.endEdit.text().toDouble()

        self.canvas.onTextBoxesChanged(lowPassT[0],highPassT[0],startTimeT[0],endTimeT[0])
        
        
def main():
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
