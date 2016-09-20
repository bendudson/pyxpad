"""
Fourier transform based methods on XPadDataItem objects
"""

from pyxpad_utils import XPadDataItem, XPadDataDim

from numpy.fft import rfft, rfftfreq
from numpy import abs, arctan2, pi

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
    data = rfft(item.data)*(1./len(item.data))

    # Create a dimension
    dim = XPadDataDim()

    dim.name = "Frequency"

    step = (item.dim[0].data[1] - item.dim[0].data[0])
    dim.data = rfftfreq(len(item.data), step)

    dim.units = "1/"+item.dim[0].units
    if item.dim[0].units in ["s", "S", "sec", "Sec", "SEC"]:
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

    phase.data = arctan2(data.real, data.imag)

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

def sldfft(item, stride, width):
    """
    Performs a sliding Fourier transform on a data trace
    """

    # Check trace dimensions
    if len(item.dim) != 1:
        raise ValueError("fftp can only operate on 1D traces currently")

    time = item.dim[item.order]

    # Create dimensions
    timdim = XPadDataDim(time)
    timdim.data = []

    fredim = XPadDataDim()
    fredim.name = "Frequency"
    fredim.units = item.units + chr(0x207B) + chr(0x00B9)
    fredim.data = []
    if timdim.units in ["s", "S", "sec", "Sec", "SEC"]:
        fredim.units = "kHz"

    # Set window minimum and maximum
    winmin = 0.
    winmax = width

    # Create result XPadDataItems for:

    # Amplitude
    amp = XPadDataItem()
    if item.name != "":
        amp.name = "AMP(" + item.name + ")"
    amp.source = item.source
    if item.label != "":
        amp.label = "AMP(" + item.label + ")"
    amp.units = item.units
    amp.dim = [fredim, timdim]
    amp.order = -1
    amp.data = []

    # Phase
    phase = XPadDataItem()
    if item.name != "":
        phase.name = "PHASE("+item.name+")"
    phase.source = item.source
    if item.label != "":
        phase.label = "PHASE("+item.label+")"
    phase.units = "Radians"
    phase.dim = [fredim, timdim]
    phase.order = -1
    phase.data = []

    # Perform FFT for each window
    while winmax <= time.data[-1]:

        # Create list of data in window
        windat = []
        wintim = []
        for point in range(len(item.data)):
            if time.data[point] >= winmin:
                if time.data[point] <= winmax:
                    windat.append(item.data[point])
                    wintim.append(time.data[point])

        # Check for data in window
        if len(windat) > 0:

            # Calculate phase and frequency for window
            data = rfft(windat)*(1./len(windat))
            winstp = wintim[1] - wintim[0]
            winfre = rfftfreq(len(windat), winstp)
            winres = rfft(windat)*(1./len(windat))
            winamp = abs(winres)
            winphs = arctan2(winres.real, winres.imag)

            a = winphs - 2*pi
            for i in range (1, len(winphs)):
                if abs(winphs[i-1] - a[i]) < 1.:
                    winphs[i] = a[i]

            a = winphs + 2*pi
            for i in range(1, len(winphs)):
                if abs(winphs[i-1] - a[i]) < 1.:
                    winphs[i] = a[i]

            if timdim.units in ["s", "S", "sec", "Sec", "SEC"]:
                winfre /= 1000.

            # Update amplitude
            amp.data.append(winamp)
            amp.dim[0].data.append(winfre)
            amp.dim[1].data.append((winmin+winmax)/2.)

            # Update phase
            phase.data.append(winphs)
            phase.dim[0].data.append(winfre)
            phase.dim[1].data.append((winmin+winmax)/2)

        # Move window
        winmin += stride
        winmax += stride

    return amp, phase
