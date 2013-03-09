#
# Initial code taken from  http://stackoverflow.com/questions/6723527/getting-pyside-to-work-with-matplotlib
# Additional bits from https://gist.github.com/jfburkhart/2423179
#

import matplotlib

matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4']='PySide'

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.pyplot import setp

from PySide.QtGui import QVBoxLayout

class MatplotlibWidget():

    def __init__(self, parent):
        
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(parent)
        self.mpl_toolbar = NavigationToolbar(self.canvas, parent)
        self.axes = self.figure.add_subplot(111)
        
        self.grid_layout = QVBoxLayout()
        self.grid_layout.addWidget(self.canvas)
        self.grid_layout.addWidget(self.mpl_toolbar)
        parent.setLayout(self.grid_layout)
        
    def plot(self, *args):
        """
        Make multiple plots
        """
        nplots = len(args)
        print "Number of plots = ", nplots
        self.axes.clear()
        self.figure.clear()
        self.axes.grid(True)
        for plotnum, p in enumerate(args):
            # For each plot
            if plotnum == 0:
                self.axes = self.figure.add_subplot(nplots,1,plotnum)
                ax = self.axes
            else:
                self.axes = self.figure.add_subplot(nplots,1,plotnum, sharex=ax)
                setp(self.axes.get_xticklabels(), visible=False)
            try:
                # Assume each p is a list of data items to be overplotted
                for data in p:
                    # Plot data
                    #self.axes.plot(data.time, data.data)
                    self.axes.plot(data.data)
            except TypeError:
                # p not iterable, so just plot item
                #self.axes.plot(p.time, p.data)
                self.axes.plot(p.data)
                self.axes.set_ylabel(p.name)
                
        #self.figure.subplots_adjust(left=0.05, right=0.98, top=0.95, bottom=0.05)
        self.figure.subplots_adjust(left=0.05, right=0.98, top=0.95, bottom=0.05, hspace = 0.001)
        #self.figure.tight_layout()

        self.canvas.draw()

    def plotxy(self, x, y):
        """
        Plot one variable against another
        """
        self.axes.clear()
        self.figure.clear()
        self.axes = self.figure.add_subplot(111)
        self.figure.subplots_adjust(left=0.07, right=0.98, top=0.95, bottom=0.08)
        self.axes.plot(x.data, y.data)
        self.axes.set_xlabel(x.name)
        self.axes.set_ylabel(y.name)
        self.canvas.draw()
