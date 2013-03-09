"""
Creates small configuration dialogs from a dictionary of values
"""

from PySide.QtGui import QDialog, QGridLayout, QLineEdit, QLabel, QCheckBox, QDialogButtonBox

class ConfigDialog(QDialog):
    def __init__(self, settings, parent=None, description=None):
        super(ConfigDialog, self).__init__(parent)
        
        self.setWindowTitle("Configure source")
        
        self.layout = QGridLayout(self)
        row = 0
        self.widgets = {}
        self.settings = settings
        
        # Settings should be a dictionary
        for name, val in settings.items():
            
            label = QLabel(self)
            label.setText(str(name))
            self.layout.addWidget(label, row, 0, 1, 1)
            
            # Check the type of each setting, and create widgets accordingly
            if isinstance(val, basestring):
                # A string of some kind
                widget = QLineEdit(self)
                widget.setText(val)
            elif isinstance(val, list):
                # A list of alternative values, first is selected
                print "List: ", name
                continue
            elif isinstance(val, (int,long)):
                widget = QLineEdit(self)
                widget.setInputMask("9000000")
                widget.setText(str(val).strip())
            elif isinstance(val, float):
                print "Floating point", name
                continue
            elif isinstance(val, bool):
                widget = QCheckBox(self)
                widget.setCheckState(val)
            else:
                print "Ignoring: ", name
                continue
            widget.config = name
            self.widgets[name] = widget
            self.layout.addWidget(widget, row, 1, 1, 1)
            row += 1
        # Add OK and Cancel buttons
        buttonbox = QDialogButtonBox(QDialogButtonBox.Ok
                                     | QDialogButtonBox.Cancel)
        buttonbox.accepted.connect(self.getValues)
        buttonbox.rejected.connect(self.reject)
        self.layout.addWidget(buttonbox, row, 1, 2, 1)
        
    def getValues(self):
        # Loop through widgets to extract values
        for name, widget in self.widgets.items():
            val = self.settings[name]  # The old value
            if isinstance(val, basestring):
                self.settings[name] = widget.text()
            elif isinstance(val, (int,long)):
                self.settings[name] = int(widget.text())
            elif isinstance(val, bool):
                self.settings[name] = widget.isChecked()
        self.accept()
