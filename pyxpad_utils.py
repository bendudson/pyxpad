
class XPadDataDim:
    """
    Dimension of a data item
    
    name     Short name (e.g. "t")
    label    Short axis label (e.g. "Time (sec)")
    units    (e.g. "s")
    data     Axis values (NumPy array)
    errl     Low-side error (may be None)
    errh     High-side error (may be None)
    """
    name = ""
    label = ""
    units = ""
    data = None
    errl = None
    errh = None

class XPadDataItem:
    """
    name    The name used to request the data (e.g. "amc_plasma current")
    source  Source of the data as a string (e.g. "15100")
    label   Short description (e.g. "Plasma Current")
    units   Data units (e.g. "kA")
    desc    longer description (if set)
    data    NumPy array of the data
    errl    Low-side error (may be None)
    errh    High-side error (may be None)
    dim     A list of dimensions, each of which contains:
      - label  Short axis label (e.g. "Time (sec)")
      - units  (e.g. "s")
      - data   Axis values (NumPy array)
      - errl   Low-side error (may be None)
      - errh   High-side error (may be None)
    order   Index of time dimension
    time    A shortcut to the time data (dim[order].data). May be None
    
    """
    name   = ""
    source = ""
    label  = ""
    units  = ""
    desc   = ""
    data   = None
    errl   = None
    errh   = None
    dim    = []             # A list of dimensions
    order  = -1             # Index of time dimension
    time   = None           # A shortcut to the time data (dim[order].data). May be None
