"""
Fourier transform based methods on XPadDataItem objects
"""

from .pyxpad_utils import XPadDataItem, XPadDataDim

from numpy.fft import rfft, rfftfreq
from numpy import abs, arctan2, array, pi, zeros

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

def runfft(item, stride, width):
    """
    Performs a running Fourier transform on a data trace
    """

    # Check trace dimensions
    if len(item.dim) != 1:
        raise ValueError("runfft can only operate on 1D traces currently")

    time = item.dim[item.order]

    # Create dimensions
    time_dim = XPadDataDim(time)
    time_dim.data = []

    freq_dim = XPadDataDim()
    freq_dim.name = "Frequency"
    freq_dim.units = item.units + chr(0x207B) + chr(0x00B9)
    freq_dim.data = []
    if time_dim.units in ["s", "S", "sec", "Sec", "SEC"]:
        freq_dim.units = "kHz"

    # Assume time dimension is uniformly spaced
    # Explicit assumption of FFTW
    dt = time.data[1] - time.data[0]
    # Width and stride of window in index-space
    index_width = int(width / dt)
    index_stride = int(stride / dt)

    time_len = ((len(time.data) - index_width) // index_stride) + 1
    freq_len = (index_width // 2) + 1

    # Create result XPadDataItems for:
    # Amplitude
    amp = XPadDataItem()
    if item.name != "":
        amp.name = "runfft({}, stride={}, width={})".format(item.name, stride, width)
    amp.source = item.source
    if item.label != "":
        amp.label = "runfft({}, stride={}, width={})".format(item.name, stride, width)
    amp.units = item.units
    amp.dim = [freq_dim, time_dim]
    amp.order = -1
    amp.time = amp.dim[amp.order]
    amp.data = zeros((freq_len, time_len))

    window_freq = rfftfreq(index_width, dt)
    if time_dim.units in ["s", "S", "sec", "Sec", "SEC"]:
        window_freq /= 1000.
    freq_dim.data = window_freq

    for window_index, time_index in enumerate(range(0, len(time.data) - index_width, index_stride)):
        window_data = item.data[time_index:time_index + index_width]
        window_time = time.data[time_index:time_index + index_width]

        window_fft = rfft(window_data) / index_width
        amp.data[:, window_index]  = abs(window_fft)

        # Update time
        time_dim.data.append((window_time[0] + window_time[-1])/2.)

    return amp
