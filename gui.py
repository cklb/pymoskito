# -*- coding: utf-8 -*-

#system
import numpy as np
import sys, time, os
import yaml

#Qt
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QTimer, QThread, pyqtSignal

#pyqtgraph
import pyqtgraph as pg
import pyqtgraph.dockarea

#vtk
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

#own
from sim_interface import SimulatorInteractor, SimulatorView
from visualization import VtkVisualizer
from model import BallBeamModel

from postprocessing import PostProcessor

class BallBeamGui(QtGui.QMainWindow):
    '''
    class for the graphical user interface
    '''

    runSimulation = pyqtSignal()
    playbackTimeChanged = pyqtSignal()
    regimeFinished = pyqtSignal()
    finishedRegimeBatch = pyqtSignal()
    
    def __init__(self):
        # constructor of the base class
        QtGui.QMainWindow.__init__(self)

        # Create Simulation Backend
        self.sim = SimulatorInteractor(self)
        self.runSimulation.connect(self.sim.runSimulation)
        self.sim.simulationFinished.connect(self.simulationFinished)
        self.sim.simulationFailed.connect(self.simulationFailed)

        # sim setup viewer
        self.targetView = SimulatorView(self)
        self.targetView.setModel(self.sim.target_model)
        self.targetView.expanded.connect(self.targetViewChanged)
        self.targetView.collapsed.connect(self.targetViewChanged)

        # sim results viewer
        self.resultview = QtGui.QTreeView()

        # dockarea allows to rearrange the user interface at runtime
        self.area = pg.dockarea.DockArea()
        
        # Window properties
        self.setCentralWidget(self.area)
        self.resize(1000, 700)
        self.setWindowTitle('Ball and Beam')
        self.setWindowIcon(QtGui.QIcon('data/ball_and_beam.png'))
        
        # create docks
        self.propertyDock = pg.dockarea.Dock('Properties')
        self.vtkDock = pg.dockarea.Dock('Simulation')
        self.regimeDock = pg.dockarea.Dock('Regimes')
        self.dataDock = pg.dockarea.Dock('Data')
        self.plotDocks = []
        self.plotDocks.append(pg.dockarea.Dock('Placeholder'))
        self.plots = []
        self.plotItems = []
        self.timeLines = []

        # arrange docks
        self.area.addDock(self.vtkDock, 'right')
        self.area.addDock(self.regimeDock, 'left', self.vtkDock)
        self.area.addDock(self.propertyDock, 'bottom', self.regimeDock)
        self.area.addDock(self.dataDock, 'bottom', self.propertyDock)
        self.area.addDock(self.plotDocks[-1], 'bottom', self.vtkDock)
        
        # add widgets to the docks
        self.propertyDock.addWidget(self.targetView)        
        
        #create model for display
        self.model = BallBeamModel()

        # vtk window
        self.vtkLayout = QtGui.QVBoxLayout()
        self.frame = QtGui.QFrame()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vtkLayout.addWidget(self.vtkWidget)
        self.frame.setLayout(self.vtkLayout)
        self.vtkDock.addWidget(self.frame)
        self.visualizer = VtkVisualizer(self.vtkWidget)

        #regime window
        self.regimeList = QtGui.QListWidget(self)
        self.regimeDock.addWidget(self.regimeList)
        self.regimeList.itemDoubleClicked.connect(self.regimeDoubleClicked)

        #data window
        self.dataList = QtGui.QListWidget(self)
        self.dataDock.addWidget(self.dataList)
        self.dataList.itemDoubleClicked.connect(self.createPlot)
        
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

        self.actStop = QtGui.QAction(self)
        self.actStop.setText('Stop')
        self.actStop.setIcon(QtGui.QIcon('data/stop.png'))
        self.actStop.setDisabled(True)
        self.actStop.triggered.connect(self.stopAnimation)

        self.speedDial = QtGui.QDial()
        self.speedDial.setDisabled(True)
        self.speedDial.setMinimum(0)
        self.speedDial.setMaximum(100)
        self.speedDial.setValue(50)
        self.speedDial.setSingleStep(1)
        self.speedDial.resize(24, 24)
        self.speedDial.valueChanged.connect(self.updatePlaybackGain)

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
        
        self.actSave = QtGui.QAction(self)
        self.actSave.setText('Save')
        self.actSave.setIcon(QtGui.QIcon('data/save.png'))
        self.actSave.setDisabled(True)
        self.actSave.triggered.connect(self.saveData)

        self.actLoadRegimes = QtGui.QAction(self)
        self.actLoadRegimes.setText('load regimes')
        self.actLoadRegimes.setIcon(QtGui.QIcon('data/load.png'))
        self.actLoadRegimes.setDisabled(False)
        self.actLoadRegimes.triggered.connect(self.loadRegimeClicked)

        self.actExecuteRegimes = QtGui.QAction(self)
        self.actExecuteRegimes.setText('execute all regimes')
        self.actExecuteRegimes.setIcon(QtGui.QIcon('data/execute_regimes.png'))
        self.actExecuteRegimes.setDisabled(True)
        self.actExecuteRegimes.triggered.connect(self.executeRegimesClicked)
        
        self.actPostprocessing = QtGui.QAction(self)
        self.actPostprocessing.setText('launch postprocessor')
        self.actPostprocessing.setIcon(QtGui.QIcon('data/postprocessing.png'))
        self.actPostprocessing.setDisabled(False)
        self.actPostprocessing.triggered.connect(self.postprocessingClicked)

        # toolbar for control
        self.toolbarSim = QtGui.QToolBar('Simulation')
        self.toolbarSim.setIconSize(QtCore.QSize(24,24))
        self.addToolBar(self.toolbarSim)
        self.toolbarSim.addAction(self.actLoadRegimes)
        self.toolbarSim.addAction(self.actSave)
        self.toolbarSim.addSeparator()
        self.toolbarSim.addAction(self.actSimulate)
        self.toolbarSim.addAction(self.actExecuteRegimes)
        self.toolbarSim.addSeparator()
        self.toolbarSim.addAction(self.actPlayPause)
        self.toolbarSim.addAction(self.actStop)
        self.toolbarSim.addWidget(self.speedDial)
        self.toolbarSim.addWidget(self.timeSlider)
        self.toolbarSim.addAction(self.actPostprocessing)

        #load default config
        self.runningBatch = False
        self.currentRegimeIndex = 0
        self.regimes = None
        configFile = os.path.join('..', 'regimes', 'default.sreg')
        self._loadRegimes(configFile)
        self._applyRegime(self.currentRegimeIndex)
        self.regimeFinished.connect(self.runNextRegime)
        self.finishedRegimeBatch.connect(self.regimeBatchFinished)

        #statusbar
        self.statusBar = QtGui.QStatusBar(self)
        self.setStatusBar(self.statusBar)

    def playAnimation(self):
        '''
        play the animation
        '''
        print 'Gui(): playing animation'
        self.actPlayPause.setText('Pause')
        self.actPlayPause.setIcon(QtGui.QIcon('data/pause.png'))
        self.actPlayPause.triggered.disconnect(self.playAnimation)
        self.actPlayPause.triggered.connect(self.pauseAnimation)
        self.playbackTimer.start(0.2)
                
    def pauseAnimation(self):
        '''
        pause the animation
        '''
        print 'Gui(): pausing animation'
        self.playbackTimer.stop()
        self.actPlayPause.setText('Play')
        self.actPlayPause.setIcon(QtGui.QIcon('data/play.png'))
        self.actPlayPause.triggered.disconnect(self.pauseAnimation)
        self.actPlayPause.triggered.connect(self.playAnimation)
        
    def stopAnimation(self):
        '''
        pause the animation
        '''
        print 'Gui(): stopping animation'
        if self.actPlayPause.text() == 'Pause':
            #animation is playing -> stop it
            self.playbackTimer.stop()
            self.actPlayPause.setText('Play')
            self.actPlayPause.setIcon(QtGui.QIcon('data/play.png'))
            self.actPlayPause.triggered.disconnect(self.pauseAnimation)
            self.actPlayPause.triggered.connect(self.playAnimation)

        self.timeSlider.setValue(0)

    def startSimulation(self):
        '''
        start the simulation and disable start button
        '''
        print 'Gui(): launching simulation'
        self.actSimulate.setDisabled(True)
        self.actExecuteRegimes.setDisabled(True)
        self.simProgress = QtGui.QProgressBar(self)
        self.sim.simulationProgressChanged.connect(self.simProgress.setValue)
        self.statusBar.addWidget(self.simProgress)
        self.runSimulation.emit()
        
    def saveData(self, name='_'):
        '''
        save current dataset
        '''
        print 'Gui(): dumping data'
        self.currentDataset.update({'regime name':name})
        fileName = os.path.join('..', 'results', time.strftime('%Y%m%d-%H%M%S') +'_'+name+'.bbr')
        with open(fileName, 'w+') as f:
            f.write(repr(self.currentDataset))

    def loadRegimeClicked(self):
        repPath = os.path.join('../regimes/')
        fileName = QtGui.QFileDialog.getOpenFileName(self,\
                    "Open Regime File",\
                    repPath,\
                    "Simulation Regime files (*.sreg)")
        self._loadRegimes(fileName)

    def _loadRegimes(self, fileName=None):
        '''
        load simulation regime from file
        '''
        print 'Gui(): loading regime file:', fileName
        with open(fileName, 'r') as f:
            self.regimes = yaml.load(f)

        self._updateRegimeList()
        
        if self.regimes:
            self.actExecuteRegimes.setDisabled(False)
        
        return
        
    def _updateRegimeList(self):
        self.regimeList.clear()
        for reg in self.regimes:
            self.regimeList.addItem(reg['name'])

    def regimeDoubleClicked(self, item):
        '''
        applies the selected regime to the current target
        '''
        regName = str(item.text())
        print 'Gui(): applying regime: ', regName

        self.sim.setRegime(next((reg for reg in self.regimes if reg['name']==regName), None))

    def _applyRegime(self, index=0):
        if index >= len(self.regimes):
            print 'applyRegime(): index error!'
            return

        self.sim.setRegime(self.regimes[index])
            
    def executeRegimesClicked(self):
        '''
        execute all regimes in the current list
        '''
        self.runningBatch = True
        self.currentRegimeIndex = -1
        self.regimeFinished.emit()
        
    def runNextRegime(self):
        '''
        executes the next regime
        '''
        self.currentRegimeIndex += 1
        #are we finished?
        if self.currentRegimeIndex >= len(self.regimes):
            self.finishedRegimeBatch.emit()
            return

        self._applyRegime(self.currentRegimeIndex)
        self.startSimulation()

    def regimeBatchFinished(self):
        self.runningBatch = False
        self.actExecuteRegimes.setDisabled(False)
        self.currentRegimeIndex = 0
        box = QtGui.QMessageBox()
        box.setText('All regimes have been simulated!')
        box.exec_()

    def simulationFinished(self, data):
        '''
        integration finished, enable play button and update plots
        '''
        print 'Gui(): simulation finished'
        self.actSimulate.setDisabled(False)
        self.actPlayPause.setDisabled(False)
        self.actStop.setDisabled(False)
        self.actSave.setDisabled(False)
        self.speedDial.setDisabled(False)
        self.statusBar.removeWidget(self.simProgress)
        self.sim.simulationProgressChanged.disconnect(self.simProgress.setValue)
        del(self.simProgress)

        self.timeSlider.triggerAction(QtGui.QAbstractSlider.SliderToMinimum)

        self.currentDataset = data
        self._readResults()
        self._updateDataList()
        self._updatePlots()

        self.stopAnimation()
        self.playAnimation()

        if self.runningBatch:
            regName = self.regimes[self.currentRegimeIndex]['name']
            self.saveData(regName)
            self.regimeFinished.emit()

    def simulationFailed(self, data):
        '''
        integration failed, enable play button and update plots
        #TODO write warning window
        '''
        print 'Gui(): simulation failed'
        box = QtGui.QMessageBox()
        box.setText('The timestep integration failed!')
        box.exec_()
        self.simulationFinished(data)

    def _readResults(self):
        self.currentStepSize = 1/self.currentDataset['modules']['solver']['measure rate']
        if self.currentStepSize < 1/100:
            self.currentStepSize = 1/100

        self.currentEndTime = self.currentDataset['modules']['solver']['end time']
        self.validData = True

    def addPlotToDock(self, plotWidget):
        self.d3.addWidget(plotWidget)
    
    def incrementPlaybackTime(self):
        '''
        go one step forward in playback
        '''
        if self.playbackTime + self.currentStepSize*self.playbackGain \
                <= self.currentEndTime:
            self.playbackTime += self.currentStepSize*self.playbackGain
            pos = self.playbackTime / self.currentEndTime * self.timeSliderRange
            self.timeSlider.blockSignals(True)
            self.timeSlider.setValue(pos)
            self.timeSlider.blockSignals(False)
            self.playbackTimeChanged.emit()
        else:
            self.pauseAnimation()
            return

    def updatePlaybackGain(self, val):
        '''
        adjust playback time to slider value
        '''
        self.playbackGain = 10**(   \
                5.0*(val - self.speedDial.maximum()/2)/self.speedDial.maximum() \
                )

    def updatePlaybackTime(self):
        '''
        adjust playback time to slider value
        '''
        self.playbackTime = 1.0*self.timeSlider.value()/self.timeSliderRange * self.currentEndTime
        self.playbackTimeChanged.emit()
        return

    def updateGui(self):
        if not self.validData:
            return

        #update time cursor in plots
        self._updateTimeCursor()

        #update state of rendering
        state = [self.interpolate(self.currentDataset['results']['model_output.'+str(i)]) \
                for i in range(self.model.getOutputDimension())]
        r_beam, T_beam, r_ball, T_ball = self.model.calcPositions(state)
        self.visualizer.updateScene(r_beam, T_beam, r_ball, T_ball)

    def interpolate(self, data):
        #find corresponding index in dataset that fitts the current playback time
        #TODO implement real interpolation
        index = 0
        for elem in self.currentDataset['results']['simTime']:
            if elem > self.playbackTime:
                break
            else:
                index += 1
            
        if index >= len(data):
            return 0
        else:
            return data[index]

    def _updateDataList(self):
        self.dataList.clear()
        for key, val in self.currentDataset['results'].iteritems():
            self.dataList.insertItem(0, key)

    def createPlot(self, item):
        ''' creates a plot widget corresponding to the ListItem
        '''
        title = str(item.text())
        data = self.currentDataset['results'][title]
        #TODO check all data types
#        if title == 'observer_output.0':
#            print type(data)
#            print type(data[0])
#            print len(data)
            
        dock = pg.dockarea.Dock(title)
        self.area.addDock(dock, 'above', self.plotDocks[-1])
        self.plots.append(pg.PlotWidget(title=title))
        self.plotItems.append(self.plots[-1].plot(x=self.currentDataset['results']['simTime'], y=data))
        timeLine = pg.InfiniteLine(0, angle=90, movable=False, pen=pg.mkPen('#FF0000', width=2.0))
        self.plots[-1].addItem(timeLine)
        self.timeLines.append(timeLine)
        dock.addWidget(self.plots[-1])
        self.plotDocks.append(dock)

    def _updateTimeCursor(self):
        '''
        updates the timelines of all plot windows
        '''
        for line in self.timeLines:
            line.setValue(self.playbackTime)

    def _updatePlots(self):
        '''
        plot the fresh simulation data
        '''
        for dock in self.plotDocks:
            for widget in dock.widgets:
                if not self.dataList.findItems(dock.name(), QtCore.Qt.MatchExactly):
                    #no data for this plot -> reset it
                    widget.getPlotItem().clear()
                else:
                    widget.getPlotItem().clear()
                    widget.getPlotItem().plot(x=self.currentDataset['results']['simTime'],\
                            y=self.currentDataset['results'][dock.name()])

    def targetViewChanged(self, index):
        self.targetView.resizeColumnToContents(0)

    def postprocessingClicked(self):
        self.post = PostProcessor(self)
        self.post.show()

class TestGui(QtGui.QMainWindow):
    
    def __init__(self):
        # constructor of the base class
        QtGui.QMainWindow.__init__(self)
        self.sim = SimulatorInteractor(self)

        #viewer
        self.targetView = SimulatorView(self)
        self.targetView.setModel(self.sim.target_model)

        # Window properties
        self.setCentralWidget(self.targetView)
        self.adjustSize()
        #self.resize(500, 500)
        self.setWindowTitle('Sim Test')
       
