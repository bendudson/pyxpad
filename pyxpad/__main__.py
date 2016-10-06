#!/usr/bin/env python3

import os
from pyxpad import PyXPad
from PySide.QtGui import QApplication
import sys

def main():
    app = QApplication(sys.argv)
    path = os.path.dirname(sys.argv[0])
    window = PyXPad()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
