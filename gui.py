from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.dockarea import *
from numpy import pi
from visualization import VtkVisualizer

#vtk
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

import pyqtgraph.parametertree

#own
import settings as st

class Gui(QtGui.QMainWindow):
    '''
    class for the graphical user interface
    '''
    
    def __init__(self):
        # constructor of the base class
        QtGui.QMainWindow.__init__(self)
        
        # dockarea allows to rearrange the user interface at runtime
        self.area = DockArea()
        
        # Window properties
        self.setCentralWidget(self.area)
        self.resize(1000,500)
        self.setWindowTitle('Ball and Beam')
        self.setWindowIcon(QtGui.QIcon('data/ball_and_beam.png'))
        
        # create docks
        self.d1 = Dock('Parameter')
        self.d2 = Dock('Simulation')
        self.d3 = Dock('Plots')
        
        # arrange docks
        self.area.addDock(self.d1, 'left')
        self.area.addDock(self.d2, 'top')
        self.area.addDock(self.d3, 'right')
        
        self.parameter = Parameter()
        
        # add widgets to the docks
        self.d1.addWidget(self.parameter)        
        
        # vtk window
        self.vtkLayout = QtGui.QVBoxLayout()
        self.frame = QtGui.QFrame()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vtkLayout.addWidget(self.vtkWidget)
        self.frame.setLayout(self.vtkLayout)
        self.d2.addWidget(self.frame)
        
        # actions for simulationcontrol
        self.actPlay = QtGui.QAction(self)
        self.actPlay.setText('Play')
        self.actPlay.setIcon(QtGui.QIcon('data/play.png'))
#        self.actPlay.triggered.connect(self.startAnimation)

        self.actStop = QtGui.QAction(self)
        self.actStop.setText('Stop')
        self.actStop.setIcon(QtGui.QIcon('data/stop.png'))
        self.actStop.setDisabled(True)
#        self.actStop.triggered.connect(self.stopAnimation)
        
        # toolbar for simulationcontrol
        self.toolbarSim = QtGui.QToolBar('Simulation')
        self.toolbarSim.setIconSize(QtCore.QSize(24,24))
        self.addToolBar(self.toolbarSim)
        self.toolbarSim.addAction(self.actPlay)
        self.toolbarSim.addAction(self.actStop)
    
    def startSimulation(self):
        '''
        start the simulation and disable start bottom
        '''
        self.actPlay.setDisabled(True)
        self.actStop.setDisabled(False)        
                
        
    def stopSimulation(self):
        '''
        stop the simulation and disable stop bottom
        '''
        self.actPlay.setDisabled(False)
        self.actStop.setDisabled(True)
    
    def addPlotToDock(self, plotWidget):
        self.d3.addWidget(plotWidget)
    
    def getVtkWidget(self):
        '''
        return the created vtkWidget
        '''
        return self.vtkWidget
        
        



class Parameter(pyqtgraph.parametertree.ParameterTree):
    '''
    shows all system parameter in a widget
    '''
    
    def __init__(self):
        # constructor of the base class
        pyqtgraph.parametertree.ParameterTree.__init__(self)
        
        self.params = [
            {'name': 'System parameter', 'type': 'group', 'children': [
                {'name': 'Mass of the ball in [kg]', 'type': 'float', 'value': st.M, 'step': 0.01},
                {'name': 'Radius of the ball in [m]', 'type': 'float', 'value': st.R, 'step': 0.01},
                {'name': 'Moment of inertia of the ball in [kgm^2]', 'type': 'float', 'value': st.J},
                {'name': 'Moment of inertia of the beam in [kgm^2]', 'type': 'float', 'value': st.Jb},
                {'name': 'Beam length (min=1,max=6) in [m]', 'type': 'float', 'value': st.beam_length, 'step': 0.5, 'limits': (1,6)},
            ]},
            {'name': 'Initial States', 'type': 'group', 'children': [
                {'name': 'Initial radius in [m]', 'type': 'float', 'value': st.q0[0], 'step': 0.1, 'limits': (-st.beam_length/2,st.beam_length/2)},
                {'name': 'Initial velocity in [m/s]', 'type': 'float', 'value': st.q0[1]},
                {'name': 'Initial rotation angle in [Grad]', 'type': 'float', 'value': st.q0[2]*180/pi, 'step': 1},
                {'name': 'Initial rotation velocity in [Grad/s]', 'type': 'float', 'value': st.q0[3]*180/pi, 'step': 1},
            ]},
        ]
        
        # create a tree of parameter objects
        self.p = pyqtgraph.parametertree.Parameter.create(name='params', types='group', children=self.params)
        self.setParameters(self.p, showTop = False)
        
        self.p.sigTreeStateChanged.connect(self.change)
        
        
    def change(self, parameter, changes):
        '''
        detect the changes in parametertree and save the changes in settings
        '''
        print parameter
        for param, change, data in changes:
            path = parameter.childPath(param)
            if path is not None:
                childName = '.'.join(path)
            else:
                childName = param.name()
            print('  parameter: %s'% childName)
            print('  change:    %s'% change)
            print('  data:      %s'% str(data))
            print('  ----------')
        if childName == 'Initial States.Initial radius in [m]':
            print'r: ',st.q0[0]
            st.q0[0] = data
            print'r: ',st.q0[0]

# weitere if Anweisungen fuer andere Parameter, sehr umstaendlich: HILFE
