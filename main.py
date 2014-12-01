#!/usr/bin/python2
# -*- coding: utf-8 -*-

#system
import sys
import getopt
import traceback
#Qt
from PyQt4.QtCore import QObject, QThread, pyqtSignal, QTimer

#pyqtgraph related
from pyqtgraph.Qt import QtCore, QtGui

#own
from ballbeam import BallBeam
from trajectory import HarmonicGenerator, FixedPointGenerator
from control import PController, FController, GController, JController, LSSController, IOLController
from sim_core import Simulator
from model import BallBeamModel, ModelException
from visualization import VtkVisualizer
from plotting import PyQtGraphPlotter
from gui import Gui

import settings as st
#--------------------------------------------------------------------- 
# Main Application
#--------------------------------------------------------------------- 
def process(arg):
    pass

'''
Ball and Beam Simulation Toolkit
'''
# parse command line options TODO
try:
    opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
except getopt.error, msg:
    print msg
    print "for help use --help"
    sys.exit(2)

# process options
for o, a in opts:
    if o in ("-h", "--help"):
        print __doc__
        sys.exit(0)

# process arguments
for arg in args:
    process(arg) 

#----------------------------------------------------------------
# Simulation Backend
#----------------------------------------------------------------


#Model
model = BallBeamModel()
simulator = Simulator(model)
simThread = QThread()
simulator.moveToThread(simThread)
simThread.started.connect(simulator.run)

def simFinished():
    print 'exiting thread'
    simThread.quit()

simulator.finished.connect(simFinished)
#----------------------------------------------------------------
# Create Gui
#----------------------------------------------------------------
app = QtGui.QApplication([])
gui = Gui()

vis = VtkVisualizer(gui.getVtkWidget())
bb.setVisualizer(vis)

#----------------------------------------------------------------
# pyqt windows
#----------------------------------------------------------------
#create plotter for x1
#plotX1 = PyQtGraphPlotter(['x1'], l)
#d3.addWidget(plotX1.getWidget())
##create plotter for x2
#plotX2 = PyQtGraphPlotter(['x2'], l)
#d3.addWidget(plotX2.getWidget())
##create plotter for x3
#plotX3 = PyQtGraphPlotter(['x3'], l)
#d3.addWidget(plotX3.getWidget())
##create plotter for x4
#plotX4 = PyQtGraphPlotter(['x4'], l)
#d3.addWidget(plotX4.getWidget())

#create plotter for u
#d4.addWidget(PyQtGraphPlotter(['u'], l).getWidget())


gui.show()


print 'lets do this'



# Trajectory
trajG = HarmonicGenerator()
trajG.setAmplitude(0.5)
#trajG = FixedPointGenerator()
#trajG.setPosition(0.5)

# Control
#cont = FController()
#cont = GController()
#cont = JController()
#cont = PController()
cont = LSSController()
#cont = IOLController()

simulator.setupSolver()
simulator.setInitialValues(st.q0)
simulator.setEndTime(5)
simulator.setController(cont)
simulator.setTrajectoryGenerator(trajG)


simThread.start()
## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
