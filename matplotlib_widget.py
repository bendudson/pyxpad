#
# Initial code taken from  http://stackoverflow.com/questions/6723527/getting-pyside-to-work-with-matplotlib
# Additional bits from https://gist.github.com/jfburkhart/2423179
#

import matplotlib

matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4'] = 'PySide'

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
try:
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
except ImportError:
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.pyplot import setp

from PySide.QtGui import QVBoxLayout
from PySide.QtGui import QDialog, QGridLayout, QDialogButtonBox, QPushButton
from PySide.QtCore import Qt
from PySide.QtGui import QInputDialog

import numpy as np


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
        self.axes.clear()
        self.figure.clear()
        self.axes.grid(True)
        for plotnum, p in enumerate(args, 1):
            # For each plot
            if plotnum == 1:
                self.axes = self.figure.add_subplot(nplots, 1, plotnum)
                ax = self.axes
            else:
                self.axes = self.figure.add_subplot(nplots, 1, plotnum, sharex=ax)
                setp(self.axes.get_xticklabels(), visible=False)
            try:
                # Assume each p is a list of data items to be overplotted
                for data in p:
                    # Plot data
                    #self.axes.plot(data.time, data.data)
                    label = data.desc
                    if label == "":
                        label = data.label
                    label += " " + data.source

                    time = data.time
                    if time is None:
                        if len(data.dim) != 1:
                            print(data.dim)
                            raise ValueError("Cannot plot '"+data.label+"' as it has too many dimensions")
                        time = data.dim[0].data

                    self.axes.plot(time, data.data, label=label)
                if plotnum == 0:
                    self.axes.set_xlabel(p[0].dim[p[0].order].label)
                self.axes.legend()
            except TypeError:
                # p not iterable, so just plot item
                #self.axes.plot(p.time, p.data)
                time = p.time.data
                xlabel = p.dim[p.order].label
                if time is None:
                    if len(p.dim) != 1:
                        raise ValueError("Cannot plot '"+p.label+"' as it has too many dimensions")
                    time = p.dim[0].data
                    xlabel = p.dim[0].label

                data = p.data
                # Check the size of the array
                size = len(time)
                if size > 10000:
                    fac = int(len(time) / 10000)
                    time = time[::fac]
                    data = data[::fac]
                    print("Warning: too many samples (%d). Down-sampling to %d points" % (size, len(time)))

                self.axes.plot(time, data)

                ylabel = p.desc
                if ylabel == "":
                    ylabel = p.label
                    if p.units != "":
                        ylabel += " ("+p.units+")"
                self.axes.set_ylabel(ylabel)
                if plotnum == 0:
                    self.axes.set_xlabel(xlabel)

        self.figure.subplots_adjust(left=0.08, right=0.98, top=0.95, bottom=0.07, hspace=0.001)

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

    def oplot(self, *args):
        """
        Make an overplot from multiple traces
        """
        ntraces = len(args)
        if len(args) == 1:
            plot(self, *args)
        self.axes.clear()
        self.figure.clear()
        self.axes.grid(True)
        for tracenum, trace in enumerate(args, 1):
            self.axes = self.figure.add_subplot(1, 1, 1)
            try:
                for data in trace:
                    label = data.desc
                    if label == "":
                        label = data.name + " (" + data.units + ") " + data.source

                    time = data.time
                    if time is None:
                        if len(data.dim) != 1:
                            print(data.dim)
                            raise ValueError("Cannot plot '"+data.label+"' as it has too many dimensions")
                        time = data.dim[0].data

                    self.axes.plot(time, data.data, label=label)
                if tracenum == 0:
                    self.axes.set_xlabel(trace[0].dim[trace[0].order].label)
                self.axes.legend()
            except TypeError:
                #Trace not iterable
                time = trace.time.data
                xlabel = trace.dim[trace.order].label
                if time is None:
                    if len(trace.dim) != 1:
                        raise ValueError("Cannot plot '"+trace.label+"' as it has too many dimensions")
                    time = trace.dim[0].data
                    xlabel = trace.dim[0].label

                data = trace.data
                # Check array size
                size = len(time)
                if size > 10000:
                    fac = int(len(time) / 10000)
                    time = time[::fac]
                    data = data[::fac]
                    print("Warning: too many samples (%d). Down-sampling to %d points" % (size, len(time)))

                self.axes.plot(time, data)

                ylabel = trace.desc
                if ylabel == "":
                    ylabel = trace.label
                    if trace.units != "":
                        ylabel += " ("+trace.units+") "
                self.axes.set_ylabel(ylabel)

        self.canvas.draw()

    def mplot(self, *args):
        """
        Make a custom number of plots with a custom number of traces on each
        """
        # Create a dialog box to get the plot format
        def getFormat():
            parent = QDialog()
            title = "Plot Format"
            label = 'Enter number of traces in each plot separated by ", ":'
            dialog = QInputDialog.getText(parent, title, label)
            if dialog[1]:
                form = dialog[0].split(',')
                form = [int(i) for i in form]
                return form
            else:
                raise ValueError("No format entered")

        pltform = getFormat()
        nplots = len(pltform)
        ntraces = len(args)

        # Check validity of the plot format
        if ntraces != np.sum(pltform):
            raise ValueError("Number of traces does not equal sum of traces to be plotted in format")

        self.axes.clear()
        self.figure.clear()
        self.axes.grid(True)

        # Split data items up into correct plots according to plot format
        traces = []
        maxindx = 0
        for i in range(nplots):
            plotdat = []
            minindx = maxindx
            maxindx += pltform[i]
            for j in range(ntraces):
                if j >= minindx and j < maxindx:
                    plotdat.append(args[j][0])
            traces.append(plotdat)

        # Set axes
        for plotnum in range(nplots):
            if plotnum == 0:
                self.axes = self.figure.add_subplot(nplots, 1, plotnum+1)
                ax = self.axes
            else:
                self.axes = self.figure.add_subplot(nplots, 1, plotnum+1, sharex=ax)
                setp(self.axes.get_xticklabels(), visible=False)

            # Create OPlots for each subfigure
            try:
                for data in traces[plotnum]:
                    label = data.desc
                    if label == "":
                        label = data.name + " (" + data.units + ")"
                    label += " " + data.source

                    time = data.time
                    if time is None:
                        if len(data.dim) != 1:
                            raise ValueError("Cannot plot '"+data.name+"' as it has too many dimensions")
                        time = data.dim[0].data

                    self.axes.plot(time, data.data, label=label)
                if plotnum == 0:
                    self.axes.set_xlabel(traces[0][0].dim[traces[0][0].order].label)
                self.axes.legend()

            except TypeError:
                # Traces[plotnum] not iterable
                time = traces[plotnum].time.data
                xlabel = traces[plotnum].dim[traces[plotnum.order]].label
                if time is None:
                    if len(traces[plotnum].dim) != 1:
                        raise ValueError("Cannot plot '"+traces[plotnum].label+"' as it has too many dimensions")
                    time = traces[plotnum].dim[0].data
                    xlabel = traces[plotnum].dim[0].label

                data = traces[plotnum].data
                if size > 10000:
                    fac = int(len(time) / 10000)
                    time = time[::fac]
                    data = data[::fac]
                    print("Warning: too many samples (%d). Down-sampling to %d points" % (size, len(time)))

                self.axes.plot(time, data)

                ylabel = traces[plotnum].desc
                if ylabel == "":
                    ylabel = traces[plotnum].label
                    if traces[plotnum].units != "":
                        ylabel += " ("+traces[plotnum].units+")"
                self.axes.set_ylabel(ylabel)
                if plotnum == 0:
                    self.axes.set_xlabel(xlabel)

        self.figure.subplots_adjust(left=0.08, right=0.98, top=0.95, bottom=0.07, hspace=0.001)
        self.canvas.draw

    def contour(self, item):
        if len(item.data.shape) != 2:  # Must be 2D
            print("Data must be 2 dimensional")
            return

        self.axes.clear()
        self.figure.clear()
        self.axes = self.figure.add_subplot(111)
        self.figure.subplots_adjust(left=0.07, right=0.98, top=0.95, bottom=0.08)
        self.axes.contour(item.data)
        self.canvas.draw()

    def contourf(self, item):
        if len(item.data.shape) != 2:  # Must be 2D
            print("Data must be 2 dimensional")
            return

        self.axes.clear()
        self.figure.clear()
        self.axes = self.figure.add_subplot(111)
        self.figure.subplots_adjust(left=0.07, right=0.98, top=0.95, bottom=0.08)
        self.axes.contourf(item.data)
        self.canvas.draw()
