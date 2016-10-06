"""



"""

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

import os

from .pyxpad_utils import XPadDataItem, XPadDataDim

try:
    import pyidam as idam
    gotidam = True
except ImportError:
    try:
        import idam
        gotidam = True
    except ImportError:
        print("Warning: IDAM library not found. Cannot read data")
        gotidam = False


class XPadSource:
    def __init__(self, path, parent=None):

        # Convert path to string, strip NULL chars
        path = str(path)

        self.label = os.path.basename(os.path.normpath(path))
        self.dimensions = {}
        self.varNames = []
        self.variables = {}

        self.parent = parent

        # Define configuration dictionary
        if parent is None:
            self.config = {'Host': 'mast.fusion.org.uk',
                           'Port': 56565,
                           'verbose': True,
                           'debug': False}
        else:
            self.config = parent.config

        if os.path.isdir(path):
            # List directory
            ls = os.listdir(path)

            # Check if a name is supplied
            if 'title' in ls:
                # Read file to get the label
                f = open(os.path.join(path, 'title'), 'r')
                self.label = f.readline().strip()
                f.close()

            # Create a child for each subdirectory
            self.children = [XPadSource(os.path.join(path, name), parent=self)  # Create child
                             for name in ls
                             # For each directory which isn't hidden
                             if os.path.isdir(os.path.join(path, name)) and name[0] != '.']

            # Find items
            for name in ls:
                if os.path.isfile(os.path.join(path, name)) and (os.path.splitext(name)[1] == ".item"):
                    self.children.append(XPadSource(os.path.join(path, name), parent=self))
        else:
            # Given an item file to read
            f = open(path, 'r')
            self.label = f.readline().strip()  # First line is the label
            nitems = int((f.readline().split('$', 1))[0].strip())  # Number of items
            for i in range(nitems):
                line = f.readline()
                # Split at '$'
                s = line.split('$', 1)
                name = s[0].strip()
                if len(name) == 0:
                    continue
                try:
                    desc = s[1].strip()
                except:
                    desc = ""
                item = XPadDataItem()
                item.name = name
                item.label = item.desc = desc
                item.source = path
                self.variables[name] = item
                self.varNames.append(name)

            if parent is not None:
                parent.addVariables(self.variables)
            f.close()

    def addVariables(self, vardict):
        # Add to dictionary of variables and list of names
        for name, var in vardict.items():
            self.variables[name] = var
            self.varNames.append(name)

        if self.parent is not None:
            self.parent.addVariables(vardict)  # Variables go from children up to parent

    def read(self, name, shot):
        """ Read data from IDAM """
        if not gotidam:
            raise ImportError("No IDAM library available")
        try:
            if isinstance(name, unicode):
                name = name.encode('utf-8')
        except NameError:
            pass
        name = str(name).strip()
        shot = str(shot).strip()

        # Start client
        if not hasattr(self, "client"):
            # Set configuration
            idam.Client.server = self.config['Host']
            idam.Client.port = self.config['Port']
            self.client = idam.Client()

        # Read data
        data = self.client.get(name, shot)

        if hasattr(data, "dims") and not hasattr(data, "dim"):
            data.dim = data.dims

        #Give data a name
        try:
            data.name = name
            data.source = "Shot " + shot
        except AttributeError:
            # Probably IDAM has set something to be read-only property
            pass

        return XPadDataItem(data)

    def size(self, name):
        pass

    def __getstate__(self):
        # We need to remove the IDAM client in order to pickle
        # instances of this class
        if hasattr(self, "client"):
            state = self.__dict__.copy()
            del state['client']
            return state
        else:
            return self.__dict__
