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
    parser.add_argument("-i", "--ignore-config", help="Ignore existing config files",
                        action="store_true", default=False)
    args = parser.parse_args()

    loadfile = args.config[0] if args.config is not None else None

    app = QApplication(sys.argv[0])
    window = PyXPad(loadfile=loadfile, ignoreconfig=args.ignore_config)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
