#!/usr/bin/python
# -*- coding: utf-8 -*-
#[CB 9/18/2015] This file contains a demonstration of various gui features
#as of now, here's what's working:
#EEG display (only a few channels at a time), lowpass and highpass filters, amplitude adjustments, time selection.
#simple menus, simple layout
#note that on my computer the data doesn't look like on everyone else's, so I apoligize if the default parameters chose
#(e.g. amplitude) are wrong. 
#derived from various tutorials and sites around the web
#http://effbot.org/tkinterbook/
#http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/index.html
#http://www.tkdocs.com/tutorial/index.html
#http://matplotlib.org/examples/user_interfaces/embedding_in_tk.html

import Tkinter as Tk
import ttk
import matplotlib
import tkMessageBox
matplotlib.use('TkAgg')

from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import mne

import simple

def hello():
    tkMessageBox.showinfo("Hello World", "Hello World!")

def show_about_window():
    tkMessageBox.showinfo(
            "About Epilepsy Modeling",
            "This amazing project\n\nwas created by:\nUtkarsh Garg\nJohnny Farrow\nJustin Jackson\nCurrell Berry\nMichael Long" 
        )        

class MainWindow(Tk.Frame):
  
    def __init__(self, parent):
        Tk.Frame.__init__(self, parent)   
        self.parent = parent
        self.counter = 0
        self.rawData = mne.io.read_raw_edf("../EEGDATA/CAPSTONE_AB/BASHAREE_TEST.edf",preload=True)
        self.startTime = Tk.DoubleVar(value=20.0)
        self.startTime.trace("w", lambda name, index, mode: self.updatePlot()) # http://www.astro.washington.edu/users/rowen/ROTKFolklore.html
        self.endTime= Tk.DoubleVar(value=23.0)
        self.endTime.trace("w", lambda name, index, mode: self.updatePlot()) 
        self.amplitudeAdjust = Tk.DoubleVar(value=1.0)
        self.amplitudeAdjust.trace("w", lambda name, index, mode: self.updatePlot()) 
        self.lowpass = Tk.DoubleVar(value=2.0)
        self.lowpass.trace("w", lambda name, index, mode: self.updatePlot())
        self.highpass = Tk.DoubleVar(value=70.0)
        self.highpass.trace("w", lambda name, index, mode: self.updatePlot())
        self.initUI()

    def updatePlot(self):
        low = self.lowpass.get()
        hi = self.highpass.get()
        amp = self.amplitudeAdjust.get()
        print("updating plot: lowpass: {low}, highpass: {hi}, amplitude: {amp}".format(low=low, hi=hi, amp=amp))
        self.displayData,self.displayTimes= simple.getDisplayData(self.rawData,self.startTime.get(),self.endTime.get(),amp,low,hi)
        self.fig.clear()
        a = self.fig.add_subplot(111)

        offset = 0
        for arr in self.displayData:
            a.plot(self.displayTimes,arr+offset)
            offset=offset+0.0001
        self.fig.canvas.show()
        if (self.counter==0):
            self.fig.clear() 
            self.counter = self.counter + 1

    def initUI(self):
        self.parent.title("Epilepsy Modeling")
        self.style = ttk.Style()
        self.style.theme_use("default")
        self.pack(fill=Tk.BOTH, expand=1)
        menubar = Tk.Menu(self.parent)

        # create a pulldown menu, and add it to the menu bar
        filemenu = Tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=hello)
        filemenu.add_command(label="Save", command=hello)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.parent.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        # create more pulldown menus
        editmenu = Tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label="Cut", command=hello)
        editmenu.add_command(label="Copy", command=hello)
        editmenu.add_command(label="Paste", command=hello)
        menubar.add_cascade(label="Edit", menu=editmenu)

        viewmenu = Tk.Menu(menubar, tearoff=0)
        viewmenu.add_command(label="Show Toolbar?", command=hello)
        viewmenu.add_command(label="Show Events Browser?", command=hello)
        viewmenu.add_command(label="Show Localization View?", command=hello)
        menubar.add_cascade(label="View", menu=viewmenu)

        helpmenu = Tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=show_about_window)
        menubar.add_cascade(label="Help", menu=helpmenu)

        # display the menu
        self.parent.config(menu=menubar)

        lowLbl = Tk.Label(self, text="Lowpass (hz)")
        lowLbl.grid(row=0, column=0,padx=5, pady=5)
        self.lowEntry = Tk.Entry(self, width=10, textvariable=self.lowpass)
        self.lowEntry.grid(row=0,column=1,padx=5, pady=5)

        highLbl = Tk.Label(self, text="Highpass (hz)")
        highLbl.grid(row=0, column=2,padx=5, pady=5)
        self.highEntry = Tk.Entry(self, width=10,textvariable=self.highpass)
        self.highEntry.grid(row=0,column=3,padx=5, pady=5)

        startLbl = Tk.Label(self, text="Start Time")
        startLbl.grid(row=0, column=4,padx=5, pady=5)
        self.startEntry = Tk.Entry(self, width=10,textvariable=self.startTime)
        self.startEntry.grid(row=0,column=5,padx=5, pady=5)

        endLbl = Tk.Label(self, text="End Time")
        endLbl.grid(row=0, column=6,padx=5, pady=5)
        self.endEntry = Tk.Entry(self, width=10,textvariable=self.endTime)
        self.endEntry.grid(row=0,column=7,padx=5, pady=5)

        sliderLabel = Tk.Label(self, text="Amplitude")
        sliderLabel.grid(row=1,column=0)
        self.slider = Tk.Scale(master=self,from_=10, to=0.01,resolution=0.05,variable=self.amplitudeAdjust)
        self.slider.grid(row=2,column=0)

        self.fig = Figure(figsize=(5,4), dpi=100)
        #a = self.fig.add_subplot(111)
        #t = arange(0.0,3.0,0.01)
        #s = sin(2*pi*t)

        #offset = 0
        #for arr in self.data:
        #    a.plot(self.times,arr+offset)
        #    offset=offset+0.02

        canvas = FigureCanvasTkAgg(self.fig, master=self)
        canvas.show()
        canvas.get_tk_widget().grid(row=1, column=1, columnspan=8, rowspan=6, padx=5, sticky=Tk.E+Tk.W+Tk.S+Tk.N)

        #CB this stuff should enable the "zooming" features and such if we can figure out how to reenable it.
        #toolbar = NavigationToolbar2TkAgg( canvas, self)
        #toolbar.update()
        #canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
        #canvas._tkcanvas.grid(row=1, column=1, columnspan=2, rowspan=4, padx=5, sticky=Tk.E+Tk.W+Tk.S+Tk.N)

        # area = Tk.Text(self)
        # area.grid(row=1, column=1, columnspan=2, rowspan=4, 
        #     padx=5, sticky=Tk.E+Tk.W+Tk.S+Tk.N)

        #abtn = Tk.Button(self, text="Activate")
        #abtn.grid(row=1, column=3)

        #cbtn = Tk.Button(self, text="Close")
        #cbtn.grid(row=2, column=3, pady=4)
        
        #hbtn = Tk.Button(self, text="Help")
        #hbtn.grid(row=5, column=0, padx=5)

        #obtn = Tk.Button(self, text="OK")
        #obtn.grid(row=5, column=3)        

        self.grid_columnconfigure(0,weight=0)
        self.grid_columnconfigure(1,weight=0)
        self.grid_columnconfigure(2,weight=0)
        self.grid_columnconfigure(3,weight=0)
        self.grid_columnconfigure(8,weight=5)
        self.grid_rowconfigure(0,weight=0)
        self.grid_rowconfigure(1,weight=0)
        self.grid_rowconfigure(2,weight=0)
        self.grid_rowconfigure(3,weight=5)

        self.updatePlot()
        
              

def main():
    root = Tk.Tk()
    root.geometry("800x600+0+0")
    app = MainWindow(root)
    root.mainloop()  

if __name__ == '__main__':
    main()  

#main()
