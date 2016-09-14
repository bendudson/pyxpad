"""
Creates small configuration dialogs from a dictionary of values
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

from PySide.QtGui import QDialog, QGridLayout, QLineEdit, QLabel, QCheckBox, QDialogButtonBox
from PySide.QtCore import Qt


class ConfigDialog(QDialog):
    def __init__(self, settings, parent=None, description=None, pstvOnly = True):
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
            if isinstance(val, str):
                # A string of some kind
                widget = QLineEdit(self)
                widget.setText(val)
            elif isinstance(val, list):
                # A list of alternative values, first is selected
                print("List: ", name)
                continue
            elif isinstance(val, bool):
                widget = QCheckBox(self)
                if val:
                    widget.setCheckState(Qt.CheckState.Checked)
                else:
                    widget.setCheckState(Qt.CheckState.Unchecked)
            elif isinstance(val, int):
                widget = QLineEdit(self)
                widget.setInputMask("9000000")
                widget.setText(str(val).strip())
            elif isinstance(val, float):
                widget = QLineEdit(self)
                if pstvOnly:
                    widget.setInputMask("0.000")
                widget.setText(str(val).strip())
            else:
                print("Ignoring: " + name)
                continue
            widget.config = name
            self.widgets[name] = widget
            self.layout.addWidget(widget, row, 1, 1, 1)
            row += 1
        # Add OK and Cancel buttons
        buttonbox = QDialogButtonBox(QDialogButtonBox.Ok |
                                     QDialogButtonBox.Cancel)
        buttonbox.accepted.connect(self.getValues)
        buttonbox.rejected.connect(self.reject)
        self.layout.addWidget(buttonbox, row, 1, 2, 1)

    def getValues(self):
        # Loop through widgets to extract values
        for name, widget in self.widgets.items():
            val = self.settings[name]  # The old value
            if isinstance(val, str):
                self.settings[name] = widget.text()
            elif isinstance(val, bool):
                self.settings[name] = widget.isChecked()
            elif isinstance(val, int):
                self.settings[name] = int(widget.text())
            elif isinstance(val, float):
                self.settings[name] = float(widget.text())
        self.accept()
