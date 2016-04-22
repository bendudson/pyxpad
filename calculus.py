"""
Calculus on XPadDataItem objects

"""

from pyxpad_utils import XPadDataItem

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
