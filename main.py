#!/usr/bin/python2
# -*- coding: utf-8 -*-

#system
import sys
import getopt
import traceback

#pyqtgraph related
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.dockarea import *
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType
import numpy as np

#vtk
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

#own
from ballbeam import BallBeam
from trajectory import HarmonicGenerator, FixedPointGenerator
from control import PController, FController, GController, JController, LSSController, IOLController
from sim_core import SimulationThread, Simulator
from model import BallBeamModel, ModelException
from visualization import VtkVisualizer
from logging import DataLogger, LoggerThread
from plotting import PyQtGraphPlotter

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
# Data Aquisition Backend
#----------------------------------------------------------------
l = DataLogger()
logThread = LoggerThread(l)
l.moveToThread(logThread)
logThread.start()

#----------------------------------------------------------------
# Simulation Backend
#----------------------------------------------------------------
simulator = Simulator(l)
simThread = SimulationThread()
simulator.moveToThread(simThread)
simThread.timer.timeout.connect(simulator.calcStep)
simulator.finished.connect(simThread.quit)
#simThread.finished.connect(gui.simFinished)


#----------------------------------------------------------------
# Create Gui
#----------------------------------------------------------------
app = QtGui.QApplication([])
win = QtGui.QMainWindow()
area = DockArea()

# Window properties
win.setCentralWidget(area)
win.resize(1000,500)
win.setWindowTitle('Ball and Beam')
app.setWindowIcon(QtGui.QIcon('ball_and_beam.png'))

d1 = Dock('Parameter')
d2 = Dock('Simulation')
d3 = Dock('System States')
#d4 = Dock('Controller Output')

area.addDock(d1, 'left')
area.addDock(d2, 'top')
area.addDock(d3, 'right')
#area.addDock(d4, 'right')


#----------------------------------------------------------------
# Parameter List
#----------------------------------------------------------------
params = [
    {'name': 'System parameter', 'type': 'group', 'children': [
        {'name': 'Ball Mass', 'type': 'float', 'value': st.M, 'step': 0.01, 'suffix': 'kg'},
        {'name': 'Ball Radius [m]', 'type': 'float', 'value': st.R, 'step': 0.01},
        {'name': 'Ball inertia torque [kgm^2]', 'type': 'float', 'value': st.J},
        {'name': 'Beam inertia torque [kgm^2]', 'type': 'float', 'value': st.Jb},
        {'name': 'Beam length (min=1,max=6)', 'type': 'float', 'value': st.beam_length, 'step': 0.5, 'limits': (1,6)},
    ]},
    {'name': 'Initial States', 'type': 'group', 'children': [
        {'name': 'Ball position [m]', 'type': 'float', 'value': st.q0[0], 'step': 0.1, 'limits':\
                (-st.beam_length/2, st.beam_length/2)},
        {'name': 'Ball velocity [m/s]', 'type': 'float', 'value': st.q0[1]},
        {'name': 'Beam angle [degree]', 'type': 'float', 'value': st.q0[2]*180/np.pi, 'step': 1},
        {'name': 'Beam velocity', 'type': 'float', 'value': st.q0[3]*180/np.pi, 'step': 1},
    ]},
    {'name': 'Controller', 'type': 'int', 'value': 1}
]
# create a tree of parameter objects
p = Parameter.create(name='params', types='group', children=params)
t = ParameterTree()
t.setParameters(p, showTop = False)
t.setWindowTitle('Parameter')
d1.addWidget(t)

#----------------------------------------------------------------
# vtk window
#----------------------------------------------------------------
vtkLayout = QtGui.QVBoxLayout()
frame = QtGui.QFrame()
vtkWidget = QVTKRenderWindowInteractor(frame)
vtkLayout.addWidget(vtkWidget)
frame.setLayout(vtkLayout)
d2.addWidget(frame)
vis = VtkVisualizer(vtkWidget)
#bb.setVisualizer(vis)

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

win.show()

#organize execution
#simTimer = QtCore.QTimer()
#simTimer.timeout.connect(bb.update)
#logTimer = QtCore.QTimer()
#logTimer.timeout.connect(l.update)

#simTimer.start(0.1)
#logTimer.start(0.2)


print 'lets do this'
## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
