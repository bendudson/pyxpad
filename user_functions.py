"""
Functions which can be used to manipulate data items

Available to the user in the command terminal

"""

import numpy as np

from pyxpad_utils import XPadDataItem

def XPadFunction(func, name="f"):
    """
    Turns a NumPy function into a function of data item
    """
    def newfunc(data):
        result = XPadDataItem()
        if data.name != "":
            result.name   = name + "( " + data.name + " )"
        result.source = data.source
        if data.label != "":
            result.label  = name + "( " + data.label + " )"
        result.data   = func(data.data)
        result.dim    = data.dim
        result.order  = data.order
        result.time   = data.time
        return result
    return newfunc


sin = XPadFunction(np.sin, "sin")
cos = XPadFunction(np.cos, "cos")
tan = XPadFunction(np.tan, "tan")

exp = XPadFunction(np.exp, "exp")
log = XPadFunction(np.log, "log")

sqrt = XPadFunction(np.sqrt, "sqrt")

