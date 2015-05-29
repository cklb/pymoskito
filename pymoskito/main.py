#!/usr/bin/python2
# -*- coding: utf-8 -*-

#system
import sys
import getopt
import traceback

#Qt
from PyQt4 import QtGui, QtCore

#own
from simulation_gui import SimulationGui, TestGui
from processing_gui import PostProcessor

#--------------------------------------------------------------------- 
# Main Application
#--------------------------------------------------------------------- 
def process(arg):
    # TODO parse command line options
    pass

try:
    opts, args = getopt.getopt(sys.argv[1:], "hp", ["help", "postprocessing"])
except getopt.error, msg:
    print msg
    print "for help use --help"
    sys.exit(2)

# process options
guiType = 'BallBeamGui'
for o, a in opts:
    if o in ("-h", "--help"):
        print __doc__
        sys.exit(0)
    elif o in ('-p', '--postprocessing'):
        guiType = 'PostProcessor'

# process arguments
for arg in args:
    process(arg) 

# Create Gui
app = QtGui.QApplication([])

gui = None
if guiType is 'BallBeamGui':
    gui = SimulationGui()
elif guiType is 'PostProcessor':
    gui = PostProcessor()

gui.show()

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

