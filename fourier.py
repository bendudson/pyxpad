"""
Fourier transform based methods on XPadDataItem objects
"""

from pyxpad_utils import XPadDataItem, XPadDataDim

from numpy.fft import rfft
from numpy import abs, arange, arctan, pi

def fftp(item):
    """
    Calculate amplitude and phase as a function of frequency
    
    Inputs
    ------

    item  - an XPadDataItem object
    
    Returns
    -------
    
    amplitude, phase pair of XPadDataItem objects
    
    """

    if len(item.dim) != 1:
        raise ValueError("fftp can only operate on 1D traces currently")
    
    # Calculate FFT
    data = rfft(item.data)
    
    # Create a dimension
    dim = XPadDataDim()
    
    dim.name = "Frequency"
    
    step = 1. / (item.dim[0].data[1] - item.dim[0].data[0])*len(item.dim[0].data)
    dim.data = arange(len(data))*step

    dim.units = "1/"+item.dim[0].units
    if item.dim[0].units == "s":
        dim.data /= 1000.
        dim.units = "kHz"
    
    # Calculate the amplitude
    amp = XPadDataItem()
    if item.name != "":
        amp.name = "AMP( "+item.name+" )"
    amp.source = item.source
    if item.label != "":
        amp.label = "AMP( "+item.label+" )"
    amp.units = item.units

    amp.data = abs(data)
    
    amp.dim = [dim]
    
    # Calculate the phase
    phase = XPadDataItem()
    if item.name != "":
        phase.name = "PHASE( "+item.name+" )"
    phase.source = item.source
    if item.label != "":
        phase.label = "PHASE( "+item.label+" )"
    phase.units = "Radians"
    
    phase.data = arctan(data.real, data.imag)

    a = phase.data - 2*pi
    for i in range(1,len(phase.data)):
        if abs(phase.data[i-1] - a[i]) < 1.:
            phase.data[i] = a[i]
            
    a = phase.data + 2*pi
    for i in range(1,len(phase.data)):
        if abs(phase.data[i-1] - a[i]) < 1.:
            phase.data[i] = a[i]
    
    phase.dim = [dim]
    
    return amp, phase
