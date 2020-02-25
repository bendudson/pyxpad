"""
Author: Ben Dudson, Department of Physics, University of York
        benjamin.dudson@york.ac.uk
        Edward Blair, Peter Hill, John Wilson

This file is part of PyXPad.

PyXPad is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PyXPad is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
"""

from Qt.QtWidgets import (QAbstractItemView, QAction,
                          QFileDialog, QMainWindow, QMenu, QMessageBox,
                          QStyle, QTableWidgetItem, QTreeWidgetItem, QWidget)
from Qt.QtGui import (QCursor, QIcon,)
from Qt.QtCore import Qt, QTextCodec, QDir

from .pyxpad_main import Ui_MainWindow
from .configdialog import ConfigDialog

from collections import OrderedDict

try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    from StringIO import StringIO  # Python 2
except ImportError:
    from io import StringIO

import sys
import os
import re
import string
import fnmatch  # For matching names to wildcard patterns
from keyword import iskeyword  # Test if a string is a keyword
import xdg                     # Names of XDG directories for config

from pyxpad import fourier         # FFT-based methods
from pyxpad import calculus        # Integration and differentiation methods
from pyxpad import user_functions  # Miscellaneous useful functions


class Sources:
    sources = []  # List of sources

    def __init__(self, mainwindow):
        self.main = mainwindow
        self.main.sourceDescription.stateChanged.connect(self.updateDisplay)

        self.groupIcon = QIcon()
        self.groupIcon.addPixmap(mainwindow.style().standardPixmap(QStyle.SP_DirClosedIcon),
                                 QIcon.Normal, QIcon.Off)
        self.groupIcon.addPixmap(mainwindow.style().standardPixmap(QStyle.SP_DirOpenIcon),
                                 QIcon.Normal, QIcon.On)
        self.keyIcon = QIcon()
        self.keyIcon.addPixmap(mainwindow.style().standardPixmap(QStyle.SP_FileIcon))

        self.main.treeView.itemSelectionChanged.connect(self.updateDisplay)
        self.main.tracePattern.returnPressed.connect(self.updateDisplay)
        self.main.treeView.setContextMenuPolicy(Qt.CustomContextMenu)  # Enable popup menus

        # Context menu
        self.main.treeView.customContextMenuRequested.connect(self.handlePopupMenu)

        # Context menu actions
        self.actionAdd = QAction("Add", self.main, statusTip="Add a new source")

        self.actionDelete = QAction("Delete", self.main, statusTip="Remove source from tree")
        self.actionDelete.triggered.connect(self.deleteSource)

        self.actionConfig = QAction("Configure", self.main, statusTip="Configure source")
        self.actionConfig.triggered.connect(self.configureSource)

    def saveState(self, f):
        pickle.dump(self.sources, f)

    def loadState(self, f):
        try:
            sources = pickle.load(f)
        except EOFError:
            sources = []
        for s in sources:
            self.addSource(s)
        self.updateDisplay()

    def handlePopupMenu(self):
        """
        Called when user right-clicks on the sources tree
        """
        menu = QMenu()
        menu.addAction(self.actionAdd)

        selected = self.main.treeView.selectedItems()
        if len(selected) != 0:
            if 'config' in selected[0].source.__dict__:
                menu.addAction(self.actionConfig)
            menu.addAction(self.actionDelete)

        menu.exec_(QCursor.pos())

    def addNetCDF(self):
        """
        Add a NetCDF file as a data source
        """
        try:
            from pyxpad.datafile import NetCDFDataSource
        except ImportError:
            self.main.write("Sorry, no NetCDF support")
            return
        try:
            # Get the file name
            tr = self.main.tr
            fname, _ = QFileDialog.getOpenFileName(self.main, tr('Open file'), '.',
                                                   filter=tr("NetCDF files (*.nc *.cdl)"))
            if (fname is None) or (fname == ""):
                return  # Cancelled

            s = NetCDFDataSource(fname)

            self.addSource(s)
            self.updateDisplay()
        except:
            self.main.write("Error creating NetCDFDataSource")
            self.main.write(str(sys.exc_info()))

    def addXPADtree(self):
        try:
            from pyxpad.xpadsource import XPadSource
        except ImportError:
            self.main.write("Sorry, no XPAD tree support")
            self.main.write(str(sys.exc_info()))
            return

        try:
            # Select the directory
            tr = self.main.tr
            dname = QFileDialog.getExistingDirectory(self.main, tr('Open XPAD directory'),
                                                     QDir.currentPath())
            if (dname == "") or (dname is None):
                return
            # Create data source
            s = XPadSource(dname)

            # Add data source and update
            self.addSource(s)
            self.updateDisplay()
        except:
            self.main.write("Error creating XPadSource")
            self.main.write(str(sys.exc_info()))
            raise

    def addBOUT(self):
        """
        Add a BOUT++ directory source
        """
        try:
            from pyxpad.boutsource import BoutDataSource

            # Select the directory
            tr = self.main.tr
            dname = QFileDialog.getExistingDirectory(self.main, tr('Open BOUT++ directory'),
                                                     QDir.currentPath())
            if (dname == "") or (dname is None):
                return
            # Create data source
            s = BoutDataSource(dname)

            # Add data source and update
            self.addSource(s)
            self.updateDisplay()
        except:
            self.main.write("Sorry, no BOUT++ support")
            raise
            return

    def addSource(self, source):
        self.sources.append(source)
        it = QTreeWidgetItem(self.main.treeView, [source.label])
        it.setIcon(0, self.groupIcon)
        it.source = source
        self.main.treeView.addTopLevelItem(it)

        def buildtree(parent, it):
            # Check for children
            try:
                for child in parent.children:
                    itchild = QTreeWidgetItem(it, [child.label])
                    itchild.source = child
                    buildtree(child, itchild)  # Add child's children
                    it.addChild(itchild)
            except AttributeError:
                # Probably no children
                return

        buildtree(source, it)

    def deleteSource(self):
        tree = self.main.treeView
        selected = tree.selectedItems()
        if len(selected) == 0:
            return
        source = selected[0].source
        tree.takeTopLevelItem(tree.indexOfTopLevelItem(selected[0]))  # Remove from tree
        # Remove from list of sources
        i = self.sources.index(source)
        del self.sources[i]
        # Update the display
        self.updateDisplay()

    def configureSource(self):
        """
        Configure a data source, changing the source's
        'config' dictionary.
        """
        selected = self.main.treeView.selectedItems()
        if len(selected) == 0:
            return
        source = selected[0].source
        c = ConfigDialog(source.config, self.main)
        c.exec_()

    def updateDisplay(self):
        table = self.main.sourceTable
        # Find which source is selected, and update table view
        selected = self.main.treeView.selectedItems()
        if len(selected) == 0:
            table.clearContents()
            table.setRowCount(0)
            return
        s = selected[0].source

        # Check if any items selected
        selecteditems = table.selectedItems()
        selectedvars = []
        nextra = 0
        for item in selecteditems:
            if 'source' in item.__dict__:
                name = item.text()
                selectedvars.append((name, item.source))
                if item.source != s:
                    nextra += 1

        table.clearContents()  # Clear the table and selections

        pattern = self.main.tracePattern.text()
        if pattern == "":
            varNames = s.varNames
        else:
            # Filter the variable names
            varNames = [name for name in s.varNames
                        if fnmatch.fnmatch(name.lower(), pattern.lower())]

        varNames.sort(key=str.lower)

        if self.main.sourceDescription.isChecked():
            # Provide description for each variable (if available)

            table.setColumnCount(2)
            table.setRowCount(len(varNames) + nextra)
            table.setSelectionBehavior(QAbstractItemView.SelectRows)

            def addVar(name, source, selected=False):
                var = source.variables[name]
                item = QTableWidgetItem(name)
                item.source = source
                table.setItem(addVar.ind, 0, item)
                item.setSelected(selected)
                comment = var.desc
                if comment == "":
                    comment = var.label
                    if var.units != "":
                        comment += " ("+var.units+") "

                if var.dim:
                    try:
                        comment += " [" + ", ".join([str(v) for v in var.dim]) + "]"
                    except TypeError:
                        if str(var.dim):
                            comment += " [" + str(var.dim) + "]"
                item = QTableWidgetItem(comment)
                table.setItem(addVar.ind, 1, item)
                item.setSelected(selected)
                addVar.ind += 1
        else:
            # Just a list of variable names. Can use multiple columns
            maxrows = 20
            n = len(varNames) + nextra
            ncols = int(n / maxrows) + 1
            table.setColumnCount(ncols)
            table.setRowCount(min([n, maxrows]))
            table.setSelectionBehavior(QAbstractItemView.SelectItems)

            def addVar(name, source, selected=False):
                row = addVar.ind % maxrows
                col = int(addVar.ind / maxrows)
                item = QTableWidgetItem(name)
                item.source = source
                table.setItem(row, col, item)
                item.setSelected(selected)
                addVar.ind += 1

        addVar.ind = 0
        for name, source in selectedvars:
            addVar(name, source, True)
        sel = [name for name, source in selectedvars if source == s]
        for name in varNames:
            if name not in sel:
                addVar(name, s)

    def read(self):
        """
        Read the selected data and return as a list of data items

        Input
        -----
            None

        Returns
        ------
            [ XPadDataItem ]  or equivalent

        Modifies
        --------
            None
        """

        # Get list of shots
        shotlist = self.main.shotInput.text().split(',')

        table = self.main.sourceTable
        tableitems = table.selectedItems()
        data = []
        for item in tableitems:
            if 'source' in item.__dict__:
                name = item.text()

                for shot in shotlist:
                    s = "Reading " + name + " from " + item.source.label
                    if shot != "":
                        s += " shot = " + shot
                    self.main.write(s)
                    # Run in a sandbox to catch exceptions and display output
                    self.main.runSandboxed(lambda: data.append(item.source.read(name, shot)))

            else:
                print("Ignoring "+item.text())
        return data


class PyXPad(QMainWindow, Ui_MainWindow):
    """

    Attributes

      data    Dictionary of variables containing user data
    """
    def __init__(self, parent=None, loadfile=None, ignoreconfig=False):
        super().__init__(parent)
        self.setupUi(self)

        self.sources = Sources(self)  # Handles data sources
        self.data = OrderedDict()  # User data

        # File menu
        self.actionNetCDF_file.triggered.connect(self.sources.addNetCDF)
        self.actionXPAD_tree.triggered.connect(self.sources.addXPADtree)
        self.actionBOUT_data.triggered.connect(self.sources.addBOUT)

        self.actionExit.triggered.connect(self.close)

        self.actionLoadState.triggered.connect(self.loadState)
        self.actionSaveState.triggered.connect(self.saveState)

        # Graphics menu
        self.actionPlot.triggered.connect(self.handlePlot)
        self.actionOPlot.triggered.connect(self.handleOPlot)
        self.actionMPlot.triggered.connect(self.handleMPlot)
        self.actionXYPlot.triggered.connect(self.handleXYPlot)
        self.actionZPlot.triggered.connect(self.handleZPlot)
        self.actionContour.triggered.connect(self.handleContour)
        self.actionContour_filled.triggered.connect(self.handleContourf)
        self.actionClearFig.triggered.connect(self.handleClearFig)

        # Command menu
        self.actionDeleteTrace.triggered.connect(self.handleDeleteTrace)
        self.actionChop.triggered.connect(self.handleChop)
        self.actionIntegrate.triggered.connect(self.handleIntegrate)
        self.actionDf_dt.triggered.connect(self.handleDifferentiate)
        self.actionAdd.triggered.connect(self.handleAdd)
        self.actionMultiply.triggered.connect(self.handleMultiply)
        self.actionSubtract.triggered.connect(self.handleSubtract)
        self.actionDivide.triggered.connect(self.handleDivide)
        self.actionFFTP.triggered.connect(self.handleFFTP)
        self.actionRunFFT.triggered.connect(self.handleRunFFT)
        self.actionReciprocal.triggered.connect(self.handleReciprocal)
        self.actionExponential.triggered.connect(self.handleExponential)
        self.actionAbsolute.triggered.connect(self.handleAbsolute)
        self.actionArctan.triggered.connect(self.handleArctan)
        self.actionNlog.triggered.connect(self.handleNlog)
        self.actionNorm.triggered.connect(self.handleNorm)
        self.actionInvert.triggered.connect(self.handleInvert)
        self.actionAddCon.triggered.connect(self.handleAddCon)
        self.actionSubCon.triggered.connect(self.handleSubCon)
        self.actionMulCon.triggered.connect(self.handleMulCon)
        self.actionDivCon.triggered.connect(self.handleDivCon)
        self.actionPowCon.triggered.connect(self.handlePowCon)
        self.actionChangeName.triggered.connect(self.handleChangeName)
        self.actionChangeUnits.triggered.connect(self.handleChangeUnit)
        self.actionClip.triggered.connect(self.handleClip)
        self.actionStats.triggered.connect(self.handleStats)
        self.actionTimeOff.triggered.connect(self.handleTimeOff)

        # Help menu
        self.actionAbout.triggered.connect(self.handleAbout)

        # Sources tab
        self.readDataButton.clicked.connect(self.readData)
        self.shotInput.returnPressed.connect(self.readData)
        self.lastShotButton.clicked.connect(self.lastShot)

        self.commandInput.commandEntered.connect(self.commandEntered)
        self.commandButton.clicked.connect(self.commandEntered)

        # Data tab
        self.dataTable.cellChanged.connect(self.dataTableChanged)
        self.dataTable.customContextMenuRequested.connect(self.handlePopupMenu)

        try:
            from pyxpad.matplotlib_widget import MatplotlibWidget
            self.DataPlot = MatplotlibWidget(self.plotTab)
        except:
            raise

        if not ignoreconfig and loadfile is None:
            # Other configuration can be saved in here
            self.config_dir = os.path.join(xdg.XDG_CONFIG_HOME, 'pyxpad')
            if os.path.exists(xdg.XDG_CACHE_HOME):
                os.makedirs(self.config_dir, exist_ok=True)
                defaultfile = os.path.join(self.config_dir, "saved_state.pyx")
                if os.path.exists(defaultfile):
                    loadfile = defaultfile
        else:
            self.config_dir = os.getcwd()

        # Load state
        if loadfile is not None:
            self.config_dir = os.path.dirname(os.path.abspath(loadfile))
            self.loadState(loadfile)

    def saveState(self, filename=None):
        """
        Saves program state to given file. If no file is specified,
        then a dialog is created to ask the user for one.
        """
        if filename is None:
            tr = self.tr
            defaultfile = os.path.join(self.config_dir, "saved_state.pyx")
            filename, _ = QFileDialog.getSaveFileName(self, dir=defaultfile,
                                                      filter=tr("PyXPad save file (*.pyx)"))
        if (filename is None) or (filename == ""):
            return
        try:
            with open(filename, 'wb') as f:
                self.sources.saveState(f)
                pickle.dump(self.data, f)
            self.write("** Saved state to file '"+filename+"'")
        except:
            e = sys.exc_info()
            self.write("Could not save state to file '"+filename+"'")
            self.write("\t ->" + str(e[1]))

    def loadState(self, filename=None):
        """
        Loads program state from the given filename.
        If no filename is specified, then a dialog is created
        to ask the user for a file name.
        """
        if filename is None:
            tr = self.tr
            filename, _ = QFileDialog.getOpenFileName(self, tr('Open file'), '.',
                                                      filter=tr("PyXPad save file (*.pyx)"))
        if (filename is None) or (filename == ""):
            return  # Cancelled
        if not os.path.exists(filename):
            self.write("Could not find " + filename)
            return
        try:
            with open(filename, 'rb') as f:
                self.sources.loadState(f)
                self.data = pickle.load(f)
        except EOFError:
            self.data = OrderedDict()
        except:
            e = sys.exc_info()
            self.write("Could not load state from file '"+filename+"'")
            self.write("\t ->" + str(e[1]))
            raise
        else:
            # If no exception raised, then update tables, lists
            self.data = OrderedDict(self.data)
            self.updateDataTable()
            self.write("** Loaded state from file '"+filename+"'")

    def closeEvent(self, event):
        """
        Called when the main window is closed
        """
        reply = QMessageBox.question(self, 'Message',
                                           "Are you sure to quit?", QMessageBox.Yes |
                                           QMessageBox.No, QMessageBox.Yes)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def write(self, text):
        """
        Write some log text to output text widget
        """
        self.textOutput.append(text)

    def makeUnique(self, name):
        """
        Modifies a given string into a valid Python variable name
        which is not already in self.data

        Input
        -----
            name  ::  string

            self.data   (class member)

        Returns
        ------
            string containing modified name

        Modifies
        --------
            None
        """
        # First make sure the name is a valid variable name
        name = re.sub('\W|^(?=\d)', '_', name)  # Replace invalid characters with '_'

        if iskeyword(name):  # Check if name is a keyword
            name += '2'

        if name in self.data:
            # Name is already in the list. Add a number to the end to make it unique
            i = 1
            while name + "_"+str(i) in self.data:
                i += 1
            return name + "_"+str(i)
        return name

    def uniqueName(self):
        """
        Generates a unique variable name, which
        is not already in self.data
        """

        def findName(name, length):
            """
            Finds a name
            """
            for c in string.ascii_lowercase:
                if length <= 1:
                    if name+c not in self.data:
                        return name+c
                else:
                    r = findName(name+c, length-1)
                    if r is not None:
                        return r
            return None

        length = 1
        while True:
            n = findName("", length)
            if n is not None:
                return n
            length += 1

    def readData(self):
        """
        User pressed the "Read" button to read selected
        data items from given shots.

        Input
        -----
            None

        Returns
        ------
            None

        Modifies
        --------
            self.data


        Calls Sources to read the new data

        Inserts data into self.data, ensuring that the name
        of each data item is unique and a valid Python name

        Updates the data table based on self.data
        """
        # Switch to data tab
        self.tabWidget.setCurrentWidget(self.dataTab)
        # Get the data from the source as a list
        newdata = self.sources.read()
        if (newdata is None) or (newdata == []):
            return  # No data read

        # Add to the data dictionary
        for item in newdata:
            try:
                # Need to make the name unique
                name = self.makeUnique(item.name)
                self.data[name] = item
            except:
                self.write("Error adding item '"+str(item)+"'")

        self.updateDataTable()

    def lastShot(self):
        """
        Get the latest shot number
        """

        # Find an XPadSource in the list of sources
        from pyxpad.xpadsource import XPadSource
        source = None
        for _source in self.sources.sources:
            if isinstance(_source, XPadSource):
                source = _source
        if source is None:
            # None available
            return

        # Now ask for the lastshot
        data_item = source.read("lastshot", "")
        last_shot_number = data_item.data.children[0].lastshot

        # Append the shot number to any existing shot numbers
        current_text = self.sources.main.shotInput.text()
        if current_text == '':
            new_text = str(last_shot_number)
        else:
            new_text = ', '.join([current_text, str(last_shot_number)])
        self.sources.main.shotInput.setText(new_text)

        return last_shot_number

    def updateDataTable(self):
        """
        Updates the table of data based on self.data dictionary
        """
        n = len(self.data)
        table = self.dataTable
        table.setSortingEnabled(False)  # Stops the table rearranging itself
        self.dataTable.cellChanged.disconnect(self.dataTableChanged)  # Don't call the dataTableChanged function
        table.setRowCount(n)
        for row, name in enumerate(self.data):
            item = self.data[name]
            it = QTableWidgetItem(name)
            it.oldname = name  # Save this for when it's changed
            table.setItem(row, 0, it)

            # Assume it's an XPadDataItem
            try:
                it = QTableWidgetItem(item.source)
                it.setFlags(it.flags() ^ Qt.ItemIsEditable)  # Make source read only
                table.setItem(row, 1, it)
            except:
                table.setItem(row, 1, QTableWidgetItem(""))

            try:
                it = QTableWidgetItem(item.name)
                it.setFlags(it.flags() ^ Qt.ItemIsEditable)  # Make trace read only
                table.setItem(row, 2, it)
            except:
                table.setItem(row, 2, QTableWidgetItem(""))

            try:
                try:
                    comment = item.comment
                except AttributeError:
                    comment = item.desc
                    if comment == "":
                        comment = item.label
                        if item.units != "":
                            comment += " ("+item.units+") "

                    if item.dim != []:
                        comment += " [" + item.dim[0].name
                        for d in item.dim[1:]:
                            comment += ", " + d.name
                        comment += "] "
                    else:
                        comment += " = " + str(item.data)

                table.setItem(row, 3, QTableWidgetItem(comment))
            except:
                table.setItem(row, 3, QTableWidgetItem(str(item)))

        table.setSortingEnabled(True)  # Re-enable sorting
        self.dataTable.cellChanged.connect(self.dataTableChanged)

    def dataTableChanged(self, row, col):
        """
        Called when the user changes the value of a cell
        in the data table. This can either be to change
        the name of a variable, or the comment.
        """
        if col == 0:
            # The name of the variable
            it = self.dataTable.item(row, col)
            name = it.text()
            oldname = it.oldname
            if name == oldname:
                return  # Not really changed

            # Need to make sure new name is unique and valid
            name = self.makeUnique(name)
            it.setText(name)
            it.oldname = name
            self.data[name] = self.data[oldname]
            del self.data[oldname]

        if col == 3:
            # Changing the comment
            comment = self.dataTable.item(row, col).text()
            name = self.dataTable.item(row, 0).text()
            self.data[name].comment = comment

        print(row, col)

    def commandEntered(self, text=None):
        """
        Called when a command is entered on the Data tab.
        Gets the command string from the text box, and calls
        the runCommand to run the command.
        """
        # If there's no text, then the "Run" button was probably
        # pressed
        if text is None or text is False:
            text = self.commandInput.text()
            self.commandInput.execute(emit=False)

        self.commandInput.clear()
        self.runCommand(text)

    def selectedDataNames(self):
        """
        Retuns a list of the names of variables selected
        in the Data table.
        """
        # Find which items are selected in the data table
        items = self.dataTable.selectedItems()  # All selected items
        if len(items) == 0:
            return []
        names = []  # List of selected data names
        for it in items:
            try:
                names.append(it.oldname)
            except AttributeError:
                pass  # Ignore if doesn't have a name
        return names

    def handlePopupMenu(self):
        """
        Called when user right-clicks on a trace
        """
        menu = QMenu()

        selected = self.selectedDataNames()
        if len(selected) != 0:
            menu.addAction(self.actionDeleteTrace)

        menu.exec_(QCursor.pos())

    ##################### Plot menu actions #####################

    def handlePlot(self):
        # Find which items are selected
        names = self.selectedDataNames()
        if len(names) == 0:
            return

        # Sort by trace name
        def trace(name):
            try:
                return self.data[name].name
            except:
                return ""
        namelist = [(name, trace(name)) for name in names]
        values = set(map(lambda x: x[1], namelist))
        groups = [[y[0] for y in namelist if y[1] == x] for x in values]

        def plotStr(items):
            return "[" + ", ".join(items) + "]"

        # Create a command to execute
        cmd = "plot(" + ", ".join([plotStr(group) for group in groups]) + ")"

        # Run the command within sandboxed environment
        # Also shows user the command which can be entered
        self.runCommand(cmd)
        self.tabWidget.setCurrentWidget(self.plotTab)

    def handleOPlot(self):
        """
        Creates an overlap plot of selected traces
        """

        names = self.selectedDataNames()

        if len(names) == 0:
            return

        def trace(name):
            try:
                return self.data[name].name
            except:
                return ""
        namelist = [(name, trace(name)) for name in names]
        values = set(map(lambda x: x[1], namelist))
        groups = [[y[0] for y in namelist if y[1] == x] for x in values]

        def plotStr(items):
            return "[" + ", ".join(items) + "]"

        cmd = "oplot(" + ", ".join([plotStr(group) for group in groups]) + ")"
        self.runCommand(cmd)
        self.tabWidget.setCurrentWidget(self.plotTab)

    def handleMPlot(self):
        """
        Creates multiple subplots of multiple traces input by the user
        """

        names = self.selectedDataNames()

        if len(names) == 0:
            return

        def trace(name):
            try:
                return self.data[name].name
            except:
                return ""

        namelist = [(name, trace(name)) for name in names]
        values = set(map(lambda x: x[1], namelist))
        groups = [[y[0] for y in namelist if y[1] == x] for x in values]

        def plotStr(items):
            return "[" + ", ".join(items) + "]"

        cmd = "mplot(" + ", ".join([plotStr(group) for group in groups]) + ")"
        self.runCommand(cmd)
        self.tabWidget.setCurrentWidget(self.plotTab)

    def handleXYPlot(self):
        names = self.selectedDataNames()
        if len(names) != 2:
            self.write("** Two data items must be selected for X-Y plotting")
            return
        # Run the command in sandbox
        self.runCommand("plotxy( "+names[0]+", "+names[1]+")")
        self.tabWidget.setCurrentWidget(self.plotTab)

    def handleZPlot(self):
        """
        Creates an zoomed plot of selected traces
        """

        names = self.selectedDataNames()

        if len(names) == 0:
            return

        def trace(name):
            try:
                return self.data[name].name
            except:
                return ""
        namelist = [(name, trace(name)) for name in names]
        values = set(map(lambda x: x[1], namelist))
        groups = [[y[0] for y in namelist if y[1] == x] for x in values]

        def plotStr(items):
            return "[" + ", ".join(items) + "]"

        cmd = "zplot(" + ", ".join([plotStr(group) for group in groups]) + ")"
        self.runCommand(cmd)
        self.tabWidget.setCurrentWidget(self.plotTab)

    def handleClearFig(self):
        self.runCommand("clearFig()")

    def handleContour(self):
        """
        Make a contour plot of a 2D trace
        """
        names = self.selectedDataNames()
        if len(names) != 1:
            self.write("** One data item must be selected for contour")
            return

        self.runCommand("contour("+names[0]+")")
        self.tabWidget.setCurrentWidget(self.plotTab)

    def handleContourf(self):
        """
        Make a contour plot of a 2D trace
        """
        names = self.selectedDataNames()
        if len(names) != 1:
            self.write("** One data item must be selected for contourf")
            return

        self.runCommand("contourf("+names[0]+")")
        self.tabWidget.setCurrentWidget(self.plotTab)

    def handleCommandAction(self, command):
        names = self.selectedDataNames()
        if len(names) != 1:
            self.write("** One data item must be selected for "+command)
            return
        # Run the command in sandbox
        self.runCommand(command+"( "+names[0]+" )")

    ######## Command menu handlers

    def handleDeleteTrace(self):
        """
        Delete selected traces
        """
        # Get list of selected variables
        names = self.selectedDataNames()

        if len(names) == 0:
            return

        for name in names:
            self.runCommand("del({})".format(name))

    def handleChop(self):
        """
        Chops a signal, keeping only specified time range
        """
        # Get list of selected variables
        names = self.selectedDataNames()

        if len(names) == 0:
            return

        try:
            # Get current time range from first variable
            var = self.data[names[0]]
            if var.time is not None:
                tmin = var.time[0]
                tmax = var.time[-1]
            else:
                tmin = var.dim[0].data[0]
                tmax = var.dim[0].data[-1]
        except:
            return

        # Use a dialog box to get time range
        config = OrderedDict({"min": float(tmin), "max": float(tmax)})

        c = ConfigDialog(config, self)
        c.exec_()

        for n in names:
            self.runCommand(self.makeUnique(n+"_chop") + " = " +
                            "chop( "+n+", %e, %e )" % (config["min"], config["max"]))

    def handleIntegrate(self):
        """
        Integrates one or more traces
        """
        names = self.selectedDataNames()

        for n in names:
            self.runCommand(self.uniqueName() + " = " + "intg( "+n+" )")

    def handleDifferentiate(self):
        """
        Differentiates one or more traces
        """
        names = self.selectedDataNames()

        for n in names:
            self.runCommand(self.uniqueName() + " = " + "diff(" + n + ")")

    def handleAdd(self):
        """
        Adds all selected traces together
        """
        names = self.selectedDataNames()
        if len(names) < 2:
            self.write("** At least two data items must be selected to add together")
            return

        self.runCommand(self.uniqueName() + " = " + "+".join(names))

    def handleMultiply(self):
        """
        Adds all selected traces together
        """
        names = self.selectedDataNames()
        if len(names) < 2:
            self.write("** At least two data items must be selected to multiply together")
            return

        self.runCommand(self.uniqueName() + " = " + "*".join(names))

    def handleSubtract(self):
        """
        Subtracts one trace from another

        """
        names = self.selectedDataNames()
        if len(names) != 2:
            self.write("** Two data items must be selected to subtract one from another")
            return
        self.runCommand(self.uniqueName()+" = " + names[0] + " - " + names[1])

    def handleDivide(self):
        """
        Divide one trace by another
        """
        names = self.selectedDataNames()
        if len(names) != 2:
            self.write("** Two data items must be selected to subtract one from another")
            return
        self.runCommand(self.uniqueName()+" = " + names[0] + " / " + names[1])

    def handleFFTP(self):
        """
        Perform FFT, returning amplitude and phase

        """

        for n in self.selectedDataNames():
            # Create a unique name for amplitude and phase
            ampname = self.makeUnique(n+"_amp")
            phasename = self.makeUnique(n+"_phase")
            self.runCommand(ampname+","+phasename + " = " + "fftp( "+n+" )")

    def handleRunFFT(self):
        """
        Perform Running FFT
        """

        names = self.selectedDataNames()

        if len(names) == 0:
            return

        stride = 0.001
        width = 0.001

        # Use a dialog box to get width and stride
        config = OrderedDict({"stride": float(width), "width": float(stride)})

        c = ConfigDialog(config, self)
        c.exec_()

        for name in names:
            # Create a unique name
            new_name = self.makeUnique(name + "_runfft")
            self.runCommand(new_name + " = " +
                            "runfft({}, stride={}, width={})".format(name, config["stride"], config["width"]))

    def handleReciprocal(self):
        """
        Returns the reciprocal of one or more trace(s)
        """
        names = self.selectedDataNames()

        for n in names:
            self.runCommand(self.uniqueName() + " = " + "recip( "+n+" )")

    def handleExponential(self):
        """
        Returns the reciprocal of one or more trace(s)
        """
        names = self.selectedDataNames()

        for n in names:
            self.runCommand(self.uniqueName() + " = " + "exp( "+n+" )")

    def handleAbsolute(self):
        """
        Returns the absolute value of one or more trace(s)
        """
        names = self.selectedDataNames()

        for n in names:
            self.runCommand(self.uniqueName() + " = " + "abs( "+n+" )")

    def handleArctan(self):
        """
        Returns the arctan of one or more trace(s)
        """
        names = self.selectedDataNames()

        for n in names:
            self.runCommand(self.uniqueName() + " = " + "atan( "+n+" )")

    def handleNlog(self):
        """
        Returns the natural log of one or more trace(s)
        """
        names = self.selectedDataNames()

        for n in names:
            self.runCommand(self.uniqueName() + " = " + "ln( "+n+" )")

    def handleNorm(self):
        """
        Normalises and returns one or more trace(s)
        """
        names = self.selectedDataNames()

        for n in names:
            self.runCommand(self.uniqueName() + " = " + "norm( "+n+" )")

    def handleInvert(self):
        """
        Returns the inversion of one or more trace(s)
        """
        names = self.selectedDataNames()

        for n in names:
            self.runCommand(self.uniqueName() + " = " + "inv( "+n+" )")

    def handleAddCon(self):
        """
        Adds a constant to and returns one or more trace(s)
        """
        names = self.selectedDataNames()

        for n in names:
            self.runCommand(self.uniqueName() + " = " + "addcons( "+n+" )")

    def handleSubCon(self):
        """
        Subtracts a constant from and returns one or more trace(s)
        """
        names = self.selectedDataNames()

        for n in names:
            self.runCommand(self.uniqueName() + " = " + "subcons( "+n+" )")

    def handleMulCon(self):
        """
        Multiplies by a constant and returns one or more trace(s)
        """
        names = self.selectedDataNames()

        for n in names:
            self.runCommand(self.uniqueName() + " = " + "mulcons( "+n+" )")

    def handleDivCon(self):
        """
        Divides by a constant and returns one or more trace(s)
        """
        names = self.selectedDataNames()

        for n in names:
            self.runCommand(self.uniqueName() + " = " + "divcons( "+n+" )")

    def handlePowCon(self):
        """
        Raises to the power of a constant and returns one or more trace(s)
        """
        names = self.selectedDataNames()

        for n in names:
            self.runCommand(self.uniqueName() + " = " + "powcons( "+n+" )")

    def handleChangeName(self):
        """
        Changes the name of one or more trace(s)
        """
        names = self.selectedDataNames()

        for n in names:
            name = user_functions.inputname()
            self.runCommand(self.makeUnique(name) + " = " + "renamed( "+n+" )")

    def handleChangeUnit(self):
        """
        Changes the units of one or more trace(s)
        """
        names = self.selectedDataNames()

        for n in names:
            self.runCommand(self.uniqueName() + " = " + "newunits( "+n+" )")

    def handleClip(self):
        """
        Clips a signal, keeping only a specified value ranged
        """

        names = self.selectedDataNames()

        if len(names) == 0:
            return

        try:
            # Get current data range from first variable
            var = self.data[names[0]]
            valmin = var.data[0]
            valmax = var.data[0]
            for point in var.data:
                if point < valmin:
                    valmin = point
                if point > valmax:
                    valmax = point
        except:
            return

        # Use a dialog box to get value range
        config = OrderedDict({"min": float(valmin), "max": float(valmax)})

        c = ConfigDialog(config, self, pstvOnly=False)
        c.exec_()

        for n in names:
            self.runCommand(self.makeUnique(n+"_clip") + " = " +
                            "clip("+n+", %e, %e )" % (config["min"], config["max"]))

    def handleStats(self):
        """
        Returns the statistics (mean, standard deviation and range) of one or more traces
        """

        names = self.selectedDataNames()

        if len(names) == 0:
            return

        for n in names:
            self.runCommand("stats("+n+")")

    def handleTimeOff(self):
        """
        Adds a time offset to one or more traces
        """

        names = self.selectedDataNames()

        for n in names:
            self.runCommand(self.uniqueName() + " = " + "timoff("+n+")")

    ########## Help menu handlers ##########

    def handleAbout(self):
        """
        Displays the About dialog
        """

        about_box = QMessageBox()
        about_box.setText(__doc__)
        about_box.exec_()

    ##########

    def runSandboxed(self, func, args=()):
        # To capture print statements stdout is temporarily directed to a StringIO buffer
        buffer = StringIO()
        oldstdout = sys.stdout
        sys.stdout = buffer
        val = None
        try:
            val = func(*args)
        except:
            e = sys.exc_info()
            self.write("Error: " + str(e[0]))
            self.write("Reason: " + str(e[1]))
        sys.stdout = oldstdout
        output = buffer.getvalue()
        if len(output) > 0:
            self.write(output)
        return val

    def _runExec(self, cmd, glob, loc):
        """
        This is a wrapper around exec
        Needed because exec isn't allowed in a lambda or nested function
        and can't be passed as a function pointer.
        """
        exec(cmd, glob, loc)

    def runCommand(self, cmd):
        # Output the command
        self.write(">>> " + cmd)

        glob = globals()
        glob['plot']     = self.DataPlot.plot
        glob['oplot']    = self.DataPlot.oplot
        glob['mplot']    = self.DataPlot.mplot
        glob['plotxy']   = self.DataPlot.plotxy
        glob['zplot']    = self.DataPlot.zplot
        glob['contour']  = self.DataPlot.contour
        glob['contourf'] = self.DataPlot.contourf
        glob['clearFig'] = self.DataPlot.clearFig

        glob['intg']     = calculus.integrate
        glob['diff']     = calculus.differentiate
        glob['fftp']     = fourier.fftp
        glob['runfft']   = fourier.runfft
        glob['chop']     = user_functions.chop
        glob['recip']    = user_functions.reciprocal
        glob['exp']      = user_functions.exponential
        glob['abs']      = user_functions.absolute
        glob['atan']     = user_functions.arctan
        glob['ln']       = user_functions.nlog
        glob['norm']     = user_functions.normalise
        glob['inv']      = user_functions.invert
        glob['addcons']  = user_functions.addcon
        glob['subcons']  = user_functions.subcon
        glob['mulcons']  = user_functions.mulcon
        glob['divcons']  = user_functions.divcon
        glob['powcons']  = user_functions.powcon
        glob['renamed']  = user_functions.changename
        glob['newunits'] = user_functions.changeunits
        glob['clip']     = user_functions.clip
        glob['stats']    = user_functions.statistics
        glob['timoff']   = user_functions.timeOffset

        # Evaluate the command, catching any exceptions
        # Local scope is set to self.data to allow access to user data
        self.runSandboxed(self._runExec, args=(cmd, glob, self.data))
        self.updateDataTable()
