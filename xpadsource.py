"""



"""

import os

class XPadSource:
    def __init__(self, path, parent=None):
        
        self.label = os.path.basename(os.path.normpath(path))
        self.dimensions = {}
        self.varNames = []
        self.variables = {}
        
        self.parent = parent
        
        # List directory
        ls = os.listdir(path)
        
        print "path = ", path
        print "ls = ", ls

        # Check if a name is supplied
        if 'title' in ls:
            # Read file to get the label
            print "Read title"
        
        # Create a child for each subdirectory
        self.children = [ XPadSource( os.path.join(path, name), parent=self )  # Create child
                          for name in ls
                          if os.path.isdir(os.path.join(path, name)) and name[0] != '.' ]  # For each directory which isn't hidden
        
        # Find items 
        
    def readItems(self, filename):
        # Read file
        
        newvars = []
        # Add variables to tree
        self.addVariables(newvars)

    def addVariables(self, vardict):
        # Add to dictionary of variables and list of names
        for name, var in vardict.items():
            self.variables[name] = var
            self.varNames.append(name)
        
        if parent != None:
            parent.addVariables(vardict)  # Variables go from children up to parent
    
    def read(self, name):
        pass
    
    def size(self, name):
        pass
    
    
