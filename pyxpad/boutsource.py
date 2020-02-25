"""


"""

from boutdata.data import BoutData
from .pyxpad_utils import XPadDataItem, XPadDataDim

import os


class BoutDataSource:
    """

    Functions
      read( name, shot )   Input variable name (string)
                     Output is an XPadDataItem object or None

      size( name )   Returns variable size as a list. [] for scalar

    Attributes

      label         A short string to describe the source
      dimensions    A dictionary of XPadDataDim objects
      varNames      A list of variable names
      variables     A dictionary of XPadDataItem objects with empty data

    """
    def __init__(self, path, parent=None):
        self.label = path

        self.parent = parent
        self.children = []

        # List the directory
        ls = os.listdir(path)

        for name in ls:
            fullname = os.path.join(path, name)
            if os.path.isdir(fullname):
                try:
                    c = BoutDataSource(fullname, parent=self)
                    self.children.append(c)
                except:
                    print("No data in directory "+fullname)

        self.label = path
        self.dimensions = {}
        self.varNames = []
        self.variables = {}
        try:
            self.data = BoutData(path)

            self.varNames = self.data.varNames
            for i, v in enumerate(self.varNames):
                try:
                    # This is for Python 2.x. Python 3.x will raise a NameError
                    # since unicode -> str and str -> bytes
                    if isinstance(v, unicode):
                        v = v.encode('utf-8')
                    v = str(v).translate(None, '\0')
                except NameError:
                    if isinstance(v, str):
                        v = v.encode('utf-8')

                self.varNames[i] = v
        except:
            # No data in path. Check if any children
            if len(self.children) == 0:
                raise

    def read(self, name, shot):
        try:
            if isinstance(name, unicode):
                name = name.encode('utf-8')
        except NameError:
            pass
        name = str(name).translate(None, '\0')

        item = self.data.read(name)

        return XPadDataItem(item)
