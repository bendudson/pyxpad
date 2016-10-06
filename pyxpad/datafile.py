# A wrapper around various NetCDF libraries,
#
# Supported libraries:
# -------------------
#
# netCDF4
#
# Scientific.IO.NetCDF
#
# scipy.io.netcdf
#   old version (create_dimension, create_variable)
#   new version (createDimension, createVariable)
#

try:
    import numpy as np
except ImportError:
    print("ERROR: NumPy module not available")
    raise

library = None  # Record which library to use

try:
    from netCDF4 import Dataset
    library = "netCDF4"
except ImportError:
    #print("netcdf4-python module not found")

    try:
        from Scientific.IO.NetCDF import NetCDFFile as Dataset
        from Scientific.N import Int, Float
        library = "Scientific"
        #print("  => Using Scientific.IO.NetCDF instead")
    except ImportError:
        try:
            from scipy.io.netcdf import netcdf_file as Dataset
            library = "scipy"
            #print("Using scipy.io.netcdf library")
        except:
            print("No supported NetCDF modules available")
            raise
import time

from .pyxpad_utils import XPadDataItem, XPadDataDim


class NetCDFDataSource:
    """

    Functions
      read( name , shot)   Input variable name (string)
                           Output is an XPadDataItem object or None

      size( name )   Returns variable size as a list. [] for scalar

    Attributes

      label         A short string to describe the source
      dimensions    A dictionary of XPadDataDim objects
      varNames      A list of variable names
      variables     A dictionary of XPadDataItem objects with empty data

    """
    handle = None

    def open(self, fname=None):
        if fname is None:
            fname = self.filename
        self.handle = Dataset(fname, "r")

    def close(self):
        if self.handle is not None:
            self.handle.close()
        self.handle = None

    def __init__(self, filename):
        self.filename = filename
        self.label = filename   # May need to shorten
        self.open(filename)
        self.dimensions = self.getDimensions()        # A dictionary of XPadDataDim objects
        self.varNames = self.handle.variables.keys()  # A list of variable names
        for i, v in enumerate(self.varNames):
            try:
                # Python 2
                if isinstance(v, unicode):
                    v = v.encode('utf-8')
                v = str(v).translate(None, '\0')
            except NameError:
                # Python 3
                if isinstance(v, str):
                    v = v.encode('utf-8')

            self.varNames[i] = v

        self.variables = {}   # A dictionary of XPadDataItem objects with empty data
        for name, var in self.handle.variables.items():
            item = XPadDataItem()
            item.name   = name
            item.source = self.filename
            item.dim = map(lambda d: self.dimensions[d], var.dimensions)
            self.variables[name] = item
        self.close()

    def __del__(self):
        self.close()

    def read(self, name, shot):
        """Read a variable from the file."""
        self.open()
        if self.handle is None:
            return None

        try:
            var = self.handle.variables[name]
        except KeyError:
            # Not found. Try to find using case-insensitive search
            var = None
            for n in self.handle.variables.keys():
                if n.lower() == name.lower():
                    print("WARNING: Reading '"+n+"' instead of '"+name+"'")
                    var = self.handle.variables[n]
            if var is None:
                return None
        ndims = len(var.dimensions)
        if ndims == 0:
            data = var.getValue()
        else:
            data = var[:]
        item = XPadDataItem()
        item.name   = name
        item.source = self.filename
        item.data   = data
        item.dim = map(lambda d: self.dimensions[d], var.dimensions)

        self.close()
        return item

    def getDimensions(self):
        if self.handle is None:
            return None
        dims = {}
        for name, dim in self.handle.dimensions.items():
            t = type(dim).__name__
            if t == 'int':
                n = dim
            else:
                n = len(dim)
            newdim = XPadDataDim()
            newdim.name = name
            newdim.label = name
            newdim.data  = np.arange(n)
            dims[name] = newdim
        return dims

    def size(self, varname):
        """List of dimension sizes for a variable."""
        if self.handle is None:
            return []
        try:
            var = self.handle.variables[varname]
        except KeyError:
            return []

        def dimlen(d):
            dim = self.handle.dimensions[d]
            if dim is not None:
                t = type(dim).__name__
                if t == 'int':
                    return dim
                return len(dim)
            return 0
        return map(lambda d: dimlen(d), var.dimensions)
