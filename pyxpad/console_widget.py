"""
A Python console custom widget for Qt Designer.

Origin: Merging of

https://qt.gitorious.org/pyside/pyside-examples/source/d4e4c7fdf71ab52083e49ffdea1b7daeff6c8d8d:examples/designer/plugins/widgets/pythonconsolewidget.py
http://www.nullege.com/codes/show/src@e@r@err-1.7.1@errbot@backends@graphic.py/32/PySide.QtGui.QPlainTextEdit

Modified 2014 Ben Dudson <benjamin.dudson@york.ac.uk>
   * Returns the command string without executing it
   * PySide rather than Qt calls


Copyright (C) 2006 David Boddie <david@boddie.org.uk>
Copyright (C) 2005-2006 Trolltech ASA. All rights reserved.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""

from PySide import QtCore, QtGui


class ConsoleWidget(QtGui.QLineEdit):
    """ConsoleWidget

    Provides a custom widget to accept Python expressions and emit output
    to other components via a custom signal.

    """

    # This signal is emitted when a command is entered
    commandEntered = QtCore.Signal(str)

    def __init__(self, parent=None):

        QtGui.QLineEdit.__init__(self, parent)

        self.history = []
        self.current = -1

        self.returnPressed.connect(self.execute)

    def keyReleaseEvent(self, event):

        if event.type() == QtCore.QEvent.KeyRelease:

            if event.key() == QtCore.Qt.Key_Up:
                current = max(0, self.current - 1)
                if 0 <= current < len(self.history):
                    self.setText(self.history[current])
                    self.current = current

                event.accept()

            elif event.key() == QtCore.Qt.Key_Down:
                current = min(len(self.history), self.current + 1)
                if 0 <= current < len(self.history):
                    self.setText(self.history[current])
                else:
                    self.clear()
                self.current = current

                event.accept()

    def execute(self):
        expression = self.text()

        # Clear the line edit, append the expression to the
        # history, and update the current command index.
        self.clear()
        self.history.append(expression)
        self.current = len(self.history)

        # Emit the text
        self.commandEntered.emit(expression)


if __name__ == "__main__":

    import sys

    def runCommand(expr):
        print(expr)

    app = QtGui.QApplication(sys.argv)
    widget = ConsoleWidget()
    widget.commandEntered.connect(runCommand)

    widget.show()
    sys.exit(app.exec_())
