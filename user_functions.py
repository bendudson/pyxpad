"""
Functions which can be used to manipulate data items

Available to the user in the command terminal

"""

import numpy as np

from pyxpad_utils import XPadDataItem, XPadDataDim

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



def chopNew(item, t_min, t_max):
    """
        >>> from user_functions import *
        >>> a = chopNew(XMC_OMV_110, 0.274, 0.276)
        >>> a_amp,a_phase = fftp(a)
        >>> b = chopNew(a_phase, 0.0, 100.0)
        >>> plot(b)
    """
    if len(item.dim) != 1:
        raise ValueError("chop can only operate on 1D traces currently")

    if t_max < t_min or t_max < item.dim[0].data[0] or t_min > item.dim[0].data[-1]:
        raise ValueError("New time-range not defined correctly")

    idx = np.where(np.logical_and(item.dim[0].data >= t_min, item.dim[0].data <= t_max))

    if len(idx[0]) == 0:
        raise ValueError("No data in time-range specified")

    # Calculate the phase
    chopped = XPadDataItem()

    if item.name != "":
        chopped.name = "CHOP( "+item.name+", "+str(t_min)+", "+str(t_max)+" )"
    chopped.source = item.source
    if item.label != "":
        chopped.label = "CHOP( "+item.label+", "+str(t_min)+", "+str(t_max)+" )"
    chopped.units = item.units

    chopped.data = item.data[idx]

    # Create a dimension
    dim = XPadDataDim()

    dim.name = item.dim[0].name
    dim.label = item.dim[0].label
    dim.units = item.dim[0].units

    dim.data = item.dim[0].data[idx]
    chopped.dim = [dim]

    if chopped.dim[0].units in ["s", "S", "sec", "Sec", "SEC"]:
        chopped.order = 0
        chopped.time = chopped.dim[0].data

    return chopped

##########################################################################

"""
    from user_functions import *
    data = read_padsav("omv110-FFTP.padsav")[0]
    plot(data)
"""

from numpy import linspace, rollaxis
from scipy.io import readsav
from warnings import catch_warnings, simplefilter

def read_padsav(file_name, disableUserWarning=False):
    warning_action = "default"
    if (disableUserWarning):
        warning_action = "ignore"

    with catch_warnings():
        simplefilter(warning_action, UserWarning)
        idl_dict = readsav(file_name)

    return parse_padsav(idl_dict)

def parse_padsav(idl_dict):
    """
        Parses padsav object from scipy.io.readsav

        Returns:
            items: list of XPadDataItems
    """

    if not check_padsav(idl_dict): return None

    items = []

    for trace in idl_dict['ptr']:
        item = XPadDataItem()

        item.name = trace['NAME'][0]
        item.source = trace['SOURCE'][0]
        item.label = trace['DINFO'][0]['LABEL'][0]
        item.units = trace['DINFO'][0]['UNITS'][0]

        item.data = rollaxis(trace['DATA'][0], len(trace['DATA'][0].shape) - 1, 0)

        numdims = trace['SIZE'][0][0]

        if numdims > 0:
            # f(t), f(t,x) or f(t,x,y)
            dim = XPadDataDim()
            
            # Use TIME data if it exists, otherwise use linspace with data from TINFO
            if 'TIME' in trace.dtype.names and trace['TIME'][0].size == trace['TINFO'][0]['LENGTH']:
                dim.data = trace['TIME'][0]
            else:
                dim.data = linspace(trace['TINFO'][0]['START'][0],trace['TINFO'][0]['FINISH'][0],trace['TINFO'][0]['LENGTH'])
            dim.name = trace['TINFO'][0]['LABEL'][0]
            dim.label = dim.name
            dim.units = trace['TINFO'][0]['UNITS'][0]

            item.dim = [dim]

            item.order = len(item.dim) - 1
            item.time = item.dim[item.order].data

        if numdims > 2:
            # f(t,x,y)
            dim = XPadDataDim()
            dim.data = trace['Y'][0]
            dim.name = trace['YINFO'][0]['LABEL'][0]
            dim.label = dim.name
            dim.units = trace['YINFO'][0]['UNITS'][0]
            item.dim.append(dim)

        if numdims > 1:
            # f(t,x) or f(t,x,y)
            dim = XPadDataDim()
            dim.data = trace['X'][0]
            dim.name = trace['XINFO'][0]['LABEL'][0]
            dim.label = dim.name
            dim.units = trace['XINFO'][0]['UNITS'][0]
            item.dim.append(dim)

        item.desc = trace['TYPE'][0]

        items.append(item)

    return items

def check_padsav(padsav):
    """
        Accepts padsav data from scipy.io.readsav

        Returns 0 for failure, 1 for success
    """
    if not isinstance(padsav, dict): return 0

    if 'ptr' not in padsav: return 0

    if not padsav['ptr'].size: return 0

    for trace in padsav['ptr']:
        if not check_trace(trace): return 0

    return 1

def check_trace(trace):
    """
        Accepts trace data from scipy.io.readsav

        Returns 0 for failure, 1 for success
    """
    from numpy import prod
    from numpy.core.records import recarray

    # [*] Is instance of numpy.core.records.recarray:
    if not isinstance(trace, recarray): return 0

    # [*] UTYPE == \'DBstructure\':
    if 'UTYPE' not in trace.dtype.names or not trace['UTYPE'][0] == 'DBstructure': return 0

    # [*] Check field names
    for field in ['TYPE','NAME','DATA','DINFO','SOURCE','PROCESS','SIZE','TINFO']:
        if field not in trace.dtype.names: return 0

    # [*] TINFO.UTYLE == \'TINFO\'
    if 'UTYPE' not in trace['TINFO'][0].dtype.names or not trace['TINFO'][0]['UTYPE'][0] == 'TINFO': return 0

    # [*] Check TINFO field names
    for field in ['DOMAINS','START','FINISH','STEP','SAMPLES','LENGTH','UNITS','LABEL']:
        if field not in trace['TINFO'][0].dtype.names: return 0

    types = ['f(t)', 'f(t,x)', 'f(t,x,y)']
    # [*] TYPE in '+str(types)+':
    if not trace['TYPE'][0] in types: return 0

    
    sizes = trace['SIZE'][0]
    numdims = sizes[0]
    # [*] size(DATA) == prod(dim sizes):
    if not trace['DATA'][0].size == prod(sizes[1:]): return 0

    # [*] Correct numdims in SIZE for TYPE:
    if not numdims == types.index(trace['TYPE'][0]) + 1: return 0

    if numdims > 0:
        if 'TIME' in trace.dtype.names:
            # [!] TIME array exist
            # [*] size(TIME) == SIZE[1]:
            if not trace['TIME'][0].size == sizes[1]: return 0

            # [*] size(TIME) == TINFO.LENGTH:
            if not trace['TIME'][0].size == trace['TINFO'][0]['LENGTH'][0]: return 0


    if numdims > 1:
        # [*] X and XINFO exist
        for field in ["X", "XINFO"]:
            if field not in trace.dtype.names: return 0

        # [*] size(X) == SIZE[2]:
        if not trace['X'][0].size == sizes[2]: return 0

    if numdims > 2:
        # [8] Y and YINFO exist
        for field in ["Y", "YINFO"]:
            if field not in trace.dtype.names: return 0

        # [*] size(Y) == SIZE[3]:
        if not trace['Y'][0].size == sizes[3]: return 0

    # .... lots more checks if you so desire
    return 1