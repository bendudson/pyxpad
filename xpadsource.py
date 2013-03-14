"""



"""

import os

from pyxpad_utils import XPadDataItem, XPadDataDim

#import idam

class XPadSource:
    def __init__(self, path, parent=None):
        
        self.label = os.path.basename(os.path.normpath(path))
        self.dimensions = {}
        self.varNames = []
        self.variables = {}
        
        self.parent = parent
        
        # Define configuration dictionary
        if parent == None:
            self.config = {'Host':'mast.culham', 'Port':55}
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
            self.children = [ XPadSource( os.path.join(path, name), parent=self )  # Create child
                              for name in ls
                              if os.path.isdir(os.path.join(path, name)) and name[0] != '.' ]  # For each directory which isn't hidden
            
            # Find items 
            for name in ls:
                if os.path.isfile(os.path.join(path, name)) and ( os.path.splitext(name)[1] == ".item" ):
                    self.children.append( XPadSource( os.path.join(path, name), parent=self) )
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
                
            if parent != None:
                parent.addVariables(self.variables)
            f.close()
            
    def addVariables(self, vardict):
        # Add to dictionary of variables and list of names
        for name, var in vardict.items():
            self.variables[name] = var
            self.varNames.append(name)
        
        if self.parent != None:
            self.parent.addVariables(vardict)  # Variables go from children up to parent
    
    def read(self, name, shot):
        """ Read data from IDAM """
        
        # Set configuration
        idam.setHost(self.config['Host'])
        idam.setPort(self.config['Port'])
        
        # Read data
        data = idam.Data(name, shot)
        
        return XPadDataItem(data)
    
    def size(self, name):
        pass
    
    
