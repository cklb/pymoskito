# -*- coding: utf-8 -*-
"""
Created on Sat Nov 22 13:09:50 2014

@author: Christoph
"""

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.dockarea import *
from settings import *
from numpy import pi

import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType

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


area.addDock(d1, 'left')

params = [
    {'name': 'System parameter', 'type': 'group', 'children': [
        {'name': 'Mass of the ball in [kg]', 'type': 'float', 'value': M, 'step': 0.01},
        {'name': 'Radius of the ball in [m]', 'type': 'float', 'value': R, 'step': 0.01},
        {'name': 'Moment of inertia of the ball in [kgm^2]', 'type': 'float', 'value': J},
        {'name': 'Moment of inertia of the beam in [kgm^2]', 'type': 'float', 'value': Jb},
        {'name': 'Beam length (min=1,max=6)', 'type': 'float', 'value': beam_length, 'step': 0.5, 'limits': (1,6)},
    ]},
    {'name': 'Initial States', 'type': 'group', 'children': [
        {'name': 'Initial radius in [m]', 'type': 'float', 'value': q0[0], 'step': 0.1, 'limits': (-beam_length/2,beam_length/2)},
        {'name': 'Initial velocity in [m/s]', 'type': 'float', 'value': q0[1]},
        {'name': 'Initial rotation angle in [Grad]', 'type': 'float', 'value': q0[2]*180/pi, 'step': 1},
        {'name': 'Initial rotation velocity in [Grad/s]', 'type': 'float', 'value': q0[3]*180/pi, 'step': 1},
    ]},
]


# create Widgets
# create a tree of parameter objects
p = Parameter.create(name='params', types='group', children=params)
t = ParameterTree()
t.setParameters(p, showTop = False)
t.setWindowTitle('Parameter')

d1.addWidget(t)










win.show()


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()