#!/usr/bin/env python3

import argparse
import os
from pyxpad import PyXPad
from PySide.QtGui import QApplication
import sys


def main():
    """
    Data visualisation and analysis tool in Python,
    intended to be familiar to users of XPAD.

    Primarily for IDAM data from the MAST tokamak experiment,
    but can be used to view NetCDF files currently.
    """
    # Add command line arguments
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("-c", "--config", nargs=1, help="Config file to load",
                        default=None)
    args = parser.parse_args()

    app = QApplication(sys.argv)
    path = os.path.dirname(sys.argv[0])
    window = PyXPad(loadfile=args.config[0])
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
