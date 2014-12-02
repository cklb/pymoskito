# -*- coding: utf-8 -*-

#system
from numpy import pi

#Qt
from PyQt4.QtCore import QTimer, QThread, pyqtSignal
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.dockarea import *
import pyqtgraph.parametertree

#vtk
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

#own
import settings as st
from sim_core import Simulator
from model import BallBeamModel
from trajectory import HarmonicGenerator, FixedPointGenerator
from control import PController, FController, GController, JController, LSSController, IOLController
from visualization import VtkVisualizer

class Gui(QtGui.QMainWindow):
    '''
    class for the graphical user interface
    '''

    playbackTimeChanged = pyqtSignal()
    
    def __init__(self):
        # constructor of the base class
        QtGui.QMainWindow.__init__(self)

        # Create Simulation Backend
        self.simData = {}
        self.validData = False
        self.model = BallBeamModel()
        self.simulator = Simulator(self.model)
        self.simThread = QThread()
        self.simThread.started.connect(self.simulator.run)
        self.simulator.finished.connect(self.simulationFinished)
        self.simulator.failed.connect(self.simulationFailed)

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
        self.d3 = Dock('Data')
        #self.d4 = Dock('Plots')
        
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
        self.visualizer = VtkVisualizer(self.vtkWidget)
        
        # action for simulation control
        self.actSimulate = QtGui.QAction(self)
        self.actSimulate.setText('Simulate')
        self.actSimulate.setIcon(QtGui.QIcon('data/simulate.png'))
        self.actSimulate.triggered.connect(self.startSimulation)
        
        # actions for animation control
        self.actPlayPause = QtGui.QAction(self)
        self.actPlayPause.setText('Play')
        self.actPlayPause.setIcon(QtGui.QIcon('data/play.png'))
        self.actPlayPause.setDisabled(True)
        self.actPlayPause.triggered.connect(self.playAnimation)

        self.timeSlider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.timeSlider.setMinimum(0)
        self.timeSliderRange = 1000
        self.timeSlider.setMaximum(self.timeSliderRange)
        self.timeSlider.setTickInterval(1)
        self.timeSlider.setTracking(True)
        self.timeSlider.valueChanged.connect(self.updatePlaybackTime)

        self.playbackTime = 0
        self.playbackGain = 1
        self.playbackTimer = QTimer()
        self.playbackTimer.timeout.connect(self.incrementPlaybackTime)
        self.playbackTimeChanged.connect(self.updateGui)
        
        # toolbar for control
        self.toolbarSim = QtGui.QToolBar('Simulation')
        self.toolbarSim.setIconSize(QtCore.QSize(24,24))
        self.addToolBar(self.toolbarSim)
        self.toolbarSim.addAction(self.actSimulate)
        self.toolbarSim.addSeparator()
        self.toolbarSim.addAction(self.actPlayPause)
        self.toolbarSim.addWidget(self.timeSlider)



        #TODO make them settable and remove this static stuff
        # Trajectory
        self.trajG = HarmonicGenerator()
        self.trajG.setAmplitude(0.5)
        #self.trajG = FixedPointGenerator()
        #self.trajG.setPosition(0.5)

        # Control
        #self.cont = FController()
        #self.cont = GController()
        #self.cont = JController()
        #self.cont = PController()
        self.cont = LSSController()
        #self.cont = IOLController()

        self.simulator.setupSolver()
        self.simulator.setInitialValues(st.q0)
        self.simulator.setEndTime(st.sim_time)
        self.simulator.setController(self.cont)
        self.simulator.setTrajectoryGenerator(self.trajG)
        #until here

    def playAnimation(self):
        '''
        play the animation
        '''
        print 'playing animation'
        self.actPlayPause.setText('Pause')
        self.actPlayPause.setIcon(QtGui.QIcon('data/pause.png'))
        self.actPlayPause.triggered.disconnect(self.playAnimation)
        self.actPlayPause.triggered.connect(self.pauseAnimation)
        self.playbackTimer.start(self.simulator.stepSize * self.playbackGain)
                
    def pauseAnimation(self):
        '''
        pause the animation
        '''
        print 'pausing animation'
        self.playbackTimer.stop()
        self.actPlayPause.setText('Play')
        self.actPlayPause.setIcon(QtGui.QIcon('data/play.png'))
        self.actPlayPause.triggered.disconnect(self.pauseAnimation)
        self.actPlayPause.triggered.connect(self.playAnimation)

    def startSimulation(self):
        '''
        start the simulation and disable start bottom
        '''
        print 'Gui(): launching simulation'
        self.actSimulate.setDisabled(True)
        self.simulator.reset()
        self.simThread.start()

    def simulationFinished(self):
        '''
        integration finished, enable play button and update plots
        '''
        print 'Gui(): simulation finished'
        self.simThread.quit()
        self.actSimulate.setDisabled(False)
        self.actPlayPause.setDisabled(False)
        self.simData = self.simulator.getValues()
        self.validData = True
        self.updatePlots()
        self.timeSlider.triggerAction(QtGui.QAbstractSlider.SliderToMinimum)
        self.playAnimation()

    def simulationFailed(self):
        '''
        integration failed, enable play button and update plots
        #TODO wirte warning window
        '''
        print 'Gui(): simulation failed'
        self.simThread.quit()
        self.actSimulate.setDisabled(False)
        self.actPlayPause.setDisabled(False)
        self.simData = self.simulator.getValues()
        self.validData = True
        self.updatePlots()
        self.timeSlider.triggerAction(QtGui.QAbstractSlider.SliderToMinimum)
        #self.playAnimation()

    def updatePlots(self):
        '''
        plot the fresh simulation data
        '''
        return
    
    def addPlotToDock(self, plotWidget):
        self.d3.addWidget(plotWidget)
    
    def incrementPlaybackTime(self):
        '''
        go one step forward in playback
        '''
        if self.playbackTime + self.simulator.stepSize <= self.simulator.endTime:
            self.playbackTime += self.simulator.stepSize
            pos = self.playbackTime / self.simulator.endTime * self.timeSliderRange
            self.timeSlider.blockSignals(True)
            self.timeSlider.setValue(pos)
            self.timeSlider.blockSignals(False)
            self.playbackTimeChanged.emit()
        else:
            self.pauseAnimation()
            return

    def updatePlaybackTime(self):
        '''
        adjust playback time to slider value
        '''
        self.playbackTime = 1.0*self.timeSlider.value()/self.timeSliderRange * self.simulator.endTime
        self.playbackTimeChanged.emit()
        return

    def updateGui(self):
        if not self.validData:
            return

        #update time cursor in plots
        #TODO

        #update state of rendering
        state = self.interpolate(self.simData['model_output'])
        r_beam, T_beam, r_ball, T_ball = self.simulator.model.calcPositions(state)
        self.visualizer.updateScene(r_beam, T_beam, r_ball, T_ball)

    def interpolate(self, data):
        #find corresponding index in dataset that fitts the current playback time
        #TODO implement real interpolation
        index = 0
        for elem in self.simData['simTime']:
            if elem > self.playbackTime:
                break
            else:
                index += 1
            
        return data[index]


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
