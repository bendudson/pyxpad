
from numpy import sqrt, abs, max

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
    Data item class for PyXPad. Provides a standard interface
    and numerical operators

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

    def __init__(self, other=None): # Construct 
        if other != None:
            try:
                # List of variables to copy
                varlist = ["name", "source", "label", "units", "desc",
                           "data", "errl", "errh", "dim", "order", "time"]
                for name in varlist:
                    # Check if other has this property
                    if other.__dict__.has_key("name"):
                        setattr(self, name, getattr(other, name))
            except AttributeError:
                # Assume it's a numerical type
                self.data = other
                self.name = str(other)

    #def __coerce__(self, other):
    #    # Convert other to an XPadDataItem and return
    #    item = XPadDataItem

    def __add__(self, other):  # +
        item = XPadDataItem(self)
        item += other
        return item

    def __radd__(self, other):
        return self.__add__(other)

    def __iadd__(self, other):  # += 
        try:
            # Metadata
            self.name += " + " + other.name
            if (self.label != "") and (other.label != ""):
                self.label += " + " + other.label
            else:
                self.label = self.name
        
            # Dimensions
        
            # Low-side error
            if self.errl != None and other.errl != None:
                self.errl = sqrt(self.errl**2 + other.errl**2)
            elif other.errl != None:
                self.errl = other.errl
            
            # High-side error
            if self.errh != None and other.errh != None:
                self.errh = sqrt(self.errh**2 + other.errh**2)
            elif other.errh != None:
                self.errh = other.errh
                
            # Data
            self.data = self.data + other.data
        except AttributeError:
            # other probably just a numeric type
            self.name += " + " + str(other)
            if self.label != "":
                self.label += " + " + str(other)
            self.data = self.data + other
            
        return self
    
    def __sub__(self, other):  # -
        item = XPadDataItem(self)
        item -= other
        return item

    def __rsub__(self, other):  # -
        item = -(self - other)  # Lazy way
        return item

    def __isub__(self, other):         # -=
        try:
            # Metadata
            self.name += " - " + other.name
            if (self.label != "") and (other.label != ""):
                self.label += " - " + other.label
            else:
                self.label = self.name

            # Dimensions

            # Low-side error. Note h and l swap for other
            if self.errl != None and other.errh != None:
                self.errl = sqrt(self.errl**2 + other.errh**2)
            elif other.errh != None:
                self.errl = other.errh

            # High-side error
            if self.errh != None and other.errl != None:
                self.errh = sqrt(self.errh**2 + other.errl**2)
            elif other.errl != None:
                self.errh = other.errl

            # Data
            self.data = self.data - other.data
        except:
            self.name += " - " + str(other)
            if self.label != "":
                self.label += " - " + str(other)
            self.data = self.data - other
        return self
    
    def __mul__(self, other):  # *
        item = XPadDataItem(self)
        item *= other
        return item

    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __imul__(self, other):         # *=
        try:
            # Metadata
            self.name += " * " + other.name
            if (self.label != "") and (other.label != ""):
                self.label += " * " + other.label
            else:
                self.label = self.name

            # Dimensions

            # Low-side error
            if self.errl != None and other.errl != None:
                self.errl = sqrt( (other.data*self.errl)**2 + (self.data * other.errl)**2 )
            elif other.errl != None:
                self.errl = self.data * other.errl
            elif self.errl != None:
                self.errl = other.data * self.errl

            # High-side error
            if self.errh != None and other.errh != None:
                self.errh = sqrt( (other.data*self.errh)**2 + (self.data * other.errh)**2 )
            elif other.errh != None:
                self.errh = self.data * other.errh
            elif self.errh != None:
                self.errh = other.data * self.errh

            # Data
            self.data = self.data * other.data
        except:
            self.name = "( " +self.name + " * " + str(other)+" )"
            if self.label != "":
                self.label = "( " + self.label + " * " + str(other)+" )"
            self.data = self.data * other
            if self.errl != None:
                self.errl = self.errl * other
            if self.errh != None:
                self.errh = self.errh * other
        return self
    
    def __div__(self, other):  # /
        item = XPadDataItem(self)
        item /= other
        return item
    
    def __idiv__(self, other): # /=
        # Metadata
        self.name += " / " + other.name
        if (self.label != "") and (other.label != ""):
            self.label += " / " + other.label
        else:
            self.label = self.name
        
        # Dimensions
        
        
        # Low-side error. Note h and l swap for other
        if self.errl != None and other.errh != None:
            self.errl = sqrt((self.errl / other.data)**2 + (self.data * other.errh / other.data**2)**2)
        elif other.errh != None:
            self.errl = self.data * other.errh / other.data**2
        elif self.errl != None:
            self.errl = self.errl / other.data

        # High-side error
        if self.errh != None and other.errl != None:
            self.errh = sqrt((self.errh / other.data)**2 + (self.data * other.errl / other.data**2)**2)
        elif other.errl != None:
            self.errh = self.data * other.errl / other.data**2
        elif self.errh != None:
            self.errh = self.errh / other.data
        
        # Data
        self.data = self.data / other.data

        return self

    def __rdiv__(self, other): #
        item = XPadDataItem(other)
        item /= self
        return item
    
    def __neg__(self): # Unary minus
        item = XPadDataItem(self)
        item.name = "-"+self.name
        if self.label != "":
            item.label = "-"+self.label
        
        item.data = -self.data
        # Swap high and low errors
        item.errl = self.errh
        item.errh = self.errl
        
        return item

    def __pos__(self):
        return self

    def __abs__(self):
        item = XPadDataItem(self)
        item.name = "abs( "+self.name+" )"
        if self.label != "":
            item.label = "abs( "+self.label+" )"

        item.data = abs(self.data)
        # High side error is maximum of low and high
        if self.errl != None and self.errh != None:
            pass
        if self.errl != None:
            item.errh = self.errl
        
        # Low side error is zero
        item.errl = 0.0
        
        return item


if __name__ == "__main__":
    # Run test cases
    
    a = XPadDataItem()
    a.name = "a"
    a.data = 1
    a.errl = 0.1
    a.errh = 0.2
    
    b = abs(a*3 + 2)
    
    c = 2 * a
    
    d = 4 / a
    print d.data, d.name

    print b.data, b.errl, b.errh
    print b.name
