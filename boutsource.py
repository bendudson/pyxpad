"""


"""

from boutdata import collect

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
    def __init__(self, path):
        self.label = path
        
        pass
