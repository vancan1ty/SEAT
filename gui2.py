#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

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

        cutAction = QtGui.QAction( '&Cut', self)
        copyAction = QtGui.QAction( '&Copy', self)
        pasteAction = QtGui.QAction( '&Paste', self)
        editMenu = menubar.addMenu('&Edit')
        editMenu.addAction(cutAction)
        editMenu.addAction(copyAction)
        editMenu.addAction(pasteAction)

        showToolbarAction = QtGui.QAction( '&Show Toolbar?', self)
        showEBAction = QtGui.QAction( '&Show Events Browser?', self)

        viewMenu = menubar.addMenu('&View')
        viewMenu.addAction(showToolbarAction)
        viewMenu.addAction(showEBAction)

        rcAction = QtGui.QAction( '&Raw Channels', self)
        avgAction = QtGui.QAction( '&Channels vs Avg', self)
        bananaAction = QtGui.QAction( '&Banana View', self)
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

        lowLbl = QtGui.QLabel('Lowpass (hz)')
        grid.addWidget(lowLbl, 0, 0)
        lowEdit = QtGui.QLineEdit()
        grid.addWidget(lowEdit, 0, 1)

        highLbl = QtGui.QLabel('Highpass (hz)')
        grid.addWidget(highLbl, 0, 2)
        highEdit = QtGui.QLineEdit()
        grid.addWidget(highEdit, 0, 3)

        startLbl = QtGui.QLabel('Start Time')
        grid.addWidget(startLbl, 0, 4)
        startEdit = QtGui.QLineEdit()
        grid.addWidget(startEdit, 0, 5)

        endLbl = QtGui.QLabel('End Time')
        grid.addWidget(endLbl, 0, 6)
        endEdit = QtGui.QLineEdit()
        grid.addWidget(endEdit, 0, 7)

        sliderLabel = QtGui.QLabel('Amplitude')
        grid.addWidget(sliderLabel, 1, 0)
        slider = QtGui.QSlider(QtCore.Qt.Vertical,holderWidget)
        grid.addWidget(slider, 2, 0)

        bigEdit = QtGui.QTextEdit()
        grid.addWidget(bigEdit, 1, 1, 6, 9)
        
        holderWidget.setLayout(grid) 

        self.setCentralWidget(holderWidget)
        self.statusBar().showMessage('Ready')
        self.setGeometry(300, 300, 350, 300)

        self.setWindowTitle('Epilepsy Modeling')    
        self.show()
        
def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
