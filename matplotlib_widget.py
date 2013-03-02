#
# Link to matplotlib
# Initial code taken from  http://stackoverflow.com/questions/6723527/getting-pyside-to-work-with-matplotlib
#

import matplotlib

matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4']='PySide'

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

class MatplotlibWidget(FigureCanvas):

    def __init__(self, parent=None,xlabel='x',ylabel='y',title='Title'):
        super(MatplotlibWidget, self).__init__(Figure())

        self.setParent(parent)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.axes = self.figure.add_subplot(111)

        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)
        self.axes.set_title(title)
        
    def plot(self, x, y):
        self.axes.plot(x, y)
        pass
