"""
Calculus on XPadDataItem objects

"""

from .pyxpad_utils import XPadDataItem
from numpy import zeros, cumsum


def integrate(item):
    """
    Integrate the given trace

    Inputs
    ------

    item  - an XPadDataItem object (or equivalent)

    Returns
    -------

    an XPadDataItem object

    """

    if len(item.dim) != 1:
        raise ValueError("Can only integrate 1D traces currently")

    # Create a result
    result = XPadDataItem()
    if item.name != "":
        result.name = "INTG( "+item.name+" )"
    result.source = item.source
    if item.label != "":
        result.label = "INTG( "+item.label+" )"
    if item.units != "":
        result.units = item.units+"*"+item.dim[0].units

    result.data = zeros(item.data.shape)

    time = item.dim[0].data

    result.data[1:] = cumsum(0.5*(time[1:]-time[0:-1])*(item.data[1:] + item.data[0:-1]))

    result.dim = item.dim
    result.order = item.order
    result.time = item.time

    return result


def differentiate(item):
    """
    Differentiates the given trace

    Inputs
    ------

    item  - an XPadDataItem object (or equivalent)

    Returns
    -------

    an XPadDataItem object

    """

    if len(item.dim) != 1:
        raise ValueError("Can only differentiate 1D traces")

    # Create a result
    result = XPadDataItem()
    if item.name != "":
        result.name = "Diff(" + item.name + ")"
    result.source = item.source
    if item.label != "":
        result.label = "Diff(" + item.label + ")"
    if item.units != "":
        result.units = item.units + item.dim[0].units + chr(0x207B) + chr(0x00B9)
    result.dim = item.dim
    result.order = item.order
    result.time = item.time

    time = item.dim[item.order].data

    result.data = zeros(len(item.data))

    for i in range(1, len(result.data)-1):
        result.data[i] = (item.data[i+1]-item.data[i-1])/(time[i+1]-time[i-1])

    result.data[-1] = result.data[-2]
    result.data[0] = result.data[1]

    return result
