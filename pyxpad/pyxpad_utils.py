#
# Author: Ben Dudson, Department of Physics, University of York
#         benjamin.dudson@york.ac.uk
#
# This file is part of PyXPad.
#
# PyXPad is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyXPad is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

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

    def __init__(self, other=None):  # Constructor
        # Instance Variables
        self.name = ""
        self.label = ""
        self.units = ""
        self.data = None
        self.errl = None
        self.errh = None

        if other is not None:
            try:
                # List of variables to copy
                varlist = ["name", "label", "units",
                           "data", "errl", "errh"]
                for name in varlist:
                    # Check if other has this property
                    try:
                        setattr(self, name, getattr(other, name))
                    except AttributeError:
                        pass
                if self.name == "":
                    self.name = self.label
            except:
                pass

    def __str__(self):
        return self.name

    def __repr__(self):
        return ("XPadDataDim( {'name':'"+self.name +
                "', 'label':'"+self.label +
                "', 'units':'"+self.units+"'} )")

    def __eq__(self, other):
        return ((self.name == other.name) and
                (self.units == other.units) and
                all(self.data == other.data))


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

    def __init__(self, other=None):  # Constructor
        # Instance Variables
        self.name   = ""
        self.source = ""
        self.label  = ""
        self.units  = ""
        self.desc   = ""
        self.data   = None
        self.errl   = None
        self.errh   = None
        self.rank   = None
        self.dim    = XPadDataDim()             # A list of dimensions
        self.order  = -1             # Index of time dimension
        self.time   = None           # A shortcut to the time data (dim[order].data). May be None

        if other is not None:
            if hasattr(other, "data"):
                # List of variables to copy
                varlist = ["name", "source", "label", "units", "desc",
                           "data", "rank", "errl", "errh", "order", "time"]
                for name in varlist:
                    # Check if other has this property
                    try:
                        setattr(self, name, getattr(other, name))
                    except AttributeError:
                        pass
                if self.name == "":
                    self.name = other.label
                try:
                    self.dim = [XPadDataDim(dim) for
                                dim in other.dim]
                except AttributeError:
                    pass
            else:
                # Assume it's a numerical type
                self.data = other
                self.name = str(other)

    # def __coerce__(self, other):
    #    # Convert other to an XPadDataItem and return
    #    item = XPadDataItem

    def __str__(self):
        """
        Returns a summary of the data as a string
        """
        s = self.name + "("+self.units+")"

        if len(self.dim) > 0:
            s += " [" + ",".join([str(d) for d in self.dim]) + "]"

        return s

    def __repr__(self):
        return ("XPadDataItem( {'name':'"+self.name +
                "', 'source':'"+self.source +
                "', 'label':'"+self.label +
                "', 'units':'"+self.units +
                "', 'desc':'"+self.desc+"'} )")

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
            if (self.dim == other.dim):
                self.dim = other.dim
            else:
                raise ValueError("Incompatible dims: {} and {}".format(
                    self.dim, other.dim))

            # Low-side error
            if self.errl is not None and other.errl is not None:
                self.errl = sqrt(self.errl**2 + other.errl**2)
            elif other.errl is not None:
                self.errl = other.errl

            # High-side error
            if self.errh is not None and other.errh is not None:
                self.errh = sqrt(self.errh**2 + other.errh**2)
            elif other.errh is not None:
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
            if (self.dim == other.dim):
                self.dim = other.dim
            else:
                raise ValueError("Incompatible dims: {} and {}".format(
                    self.dim, other.dim))

            # Low-side error. Note h and l swap for other
            if self.errl is not None and other.errh is not None:
                self.errl = sqrt(self.errl**2 + other.errh**2)
            elif other.errh is not None:
                self.errl = other.errh

            # High-side error
            if self.errh is not None and other.errl is not None:
                self.errh = sqrt(self.errh**2 + other.errl**2)
            elif other.errl is not None:
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
            if (self.dim == other.dim):
                self.dim = other.dim
            else:
                raise ValueError("Incompatible dims: {} and {}".format(
                    self.dim, other.dim))

            # Units
            if self.units == other.units:
                self.units += chr(0x00B2)
            else:
                self.units += other.units

            # Low-side error
            if self.errl is not None and other.errl is not None:
                self.errl = sqrt( (other.data*self.errl)**2 + (self.data * other.errl)**2 )
            elif other.errl is not None:
                self.errl = self.data * other.errl
            elif self.errl is not None:
                self.errl = other.data * self.errl

            # High-side error
            if self.errh is not None and other.errh is not None:
                self.errh = sqrt( (other.data*self.errh)**2 + (self.data * other.errh)**2 )
            elif other.errh is not None:
                self.errh = self.data * other.errh
            elif self.errh is not None:
                self.errh = other.data * self.errh

            # Data
            self.data = self.data * other.data
        except:
            self.name = "( " + self.name + " * " + str(other) + " )"
            if self.label != "":
                self.label = "( " + self.label + " * " + str(other) + " )"
            self.data = self.data * other
            if self.errl is not None:
                self.errl = self.errl * other
            if self.errh is not None:
                self.errh = self.errh * other
        return self

    def __truediv__(self, other):  # /
        item = XPadDataItem(self)
        item /= other
        return item

    def __itruediv__(self, other):  # /=
        try:
            # Metadata
            self.name += " / " + other.name
            if (self.label != "") and (other.label != ""):
                self.label += " / " + other.label
            else:
                self.label = self.name

            # Dimensions
            if (self.dim == other.dim):
                self.dim = other.dim
            else:
                raise ValueError("Incompatible dims: {} and {}".format(
                    self.dim, other.dim))

            #Units
            if self.units == other.units:
                self.units = ""
            elif self.units == "":
                self.units = other.units + chr(0x207B) + chr(0x00B9)
            else:
                self.units += "/" + other.units

            # Low-side error. Note h and l swap for other
            if self.errl is not None and other.errh is not None:
                self.errl = sqrt((self.errl / other.data)**2 + (self.data * other.errh / other.data**2)**2)
            elif other.errh is not None:
                self.errl = self.data * other.errh / other.data**2
            elif self.errl is not None:
                self.errl = self.errl / other.data

            # High-side error
            if self.errh is not None and other.errl is not None:
                self.errh = sqrt((self.errh / other.data)**2 + (self.data * other.errl / other.data**2)**2)
            elif other.errl is not None:
                self.errh = self.data * other.errl / other.data**2
            elif self.errh is not None:
                self.errh = self.errh / other.data

            # Data
            self.data = self.data / other.data
        except AttributeError:
            self.name = "( " + self.name + " / " + str(other)+" )"
            if self.label != "":
                self.label = "( " + self.label + " / " + str(other)+" )"
            self.data = self.data / other
            if self.errl is not None:
                self.errl = self.errl / other
            if self.errh is not None:
                self.errh = self.errh / other
        return self

    def __rtruediv__(self, other):  #
        item = XPadDataItem(other)
        item /= self
        return item

    def __neg__(self):  # Unary minus
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
        if self.errl is not None and self.errh is not None:
            pass
        if self.errl is not None:
            item.errh = self.errl

        # Low side error is zero
        item.errl = 0.0

        return item


def chop(item):
    """
    Selects a range of indices

    """
    pass

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
    print(d.data, d.name)

    print(b.data, b.errl, b.errh)
    print(b.name)
