# -*- coding: utf-8 -*-

from __future__ import division

# system
import collections
import time
import os
import yaml
import cPickle

# Qt
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QTimer, pyqtSignal

# pyqtgraph
import pyqtgraph as pg
import pyqtgraph.dockarea

# vtk
import vtk
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

# pymoskito
from simulation_interface import SimulatorInteractor, SimulatorView
from visualization import Visualizer
from postprocessor import PostProcessor


class SimulationGui(QtGui.QMainWindow):
    """
    class for the graphical user interface
    """
    runSimulation = pyqtSignal()
    playbackTimeChanged = pyqtSignal()
    regimeFinished = pyqtSignal()
    finishedRegimeBatch = pyqtSignal()

    def __init__(self):
        # constructor of the base class
        QtGui.QMainWindow.__init__(self)

        # Create Simulation Backend
        self.simProgress = None
        self.sim = SimulatorInteractor(self)
        self.runSimulation.connect(self.sim.runSimulation)
        self.sim.simulationFinished.connect(self.simulation_finished)
        self.sim.simulationFailed.connect(self.simulation_failed)
        self.currentDataset = None

        # sim setup viewer
        self.targetView = SimulatorView(self)
        self.targetView.setModel(self.sim.target_model)
        self.targetView.expanded.connect(self.target_view_changed)
        self.targetView.collapsed.connect(self.target_view_changed)

        # sim results viewer
        self.result_view = QtGui.QTreeView()

        # the docking area allows to rearrange the user interface at runtime
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
        self.plotWidgets = []
        self.timeLines = []

        # arrange docks
        self.area.addDock(self.vtkDock, 'right')
        self.area.addDock(self.regimeDock, 'left', self.vtkDock)
        self.area.addDock(self.propertyDock, 'bottom', self.regimeDock)
        self.area.addDock(self.dataDock, 'bottom', self.propertyDock)
        self.area.addDock(self.plotDocks[-1], 'bottom', self.vtkDock)

        # add widgets to the docks
        self.propertyDock.addWidget(self.targetView)

        # create model for display
        self.model = BallBeamModel()

        # vtk window
        self.vtkLayout = QtGui.QVBoxLayout()
        self.frame = QtGui.QFrame()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vtkLayout.addWidget(self.vtkWidget)
        self.frame.setLayout(self.vtkLayout)
        self.vtkDock.addWidget(self.frame)
        self.vtk_renderer = vtk.vtkRenderer()
        self.vtkWidget.AddRenderer(self.ren)
        self.visualizer = None

        # regime window
        self.regimeList = QtGui.QListWidget(self)
        self.regimeList.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.regimeDock.addWidget(self.regimeList)
        self.regimeList.itemDoubleClicked.connect(self.regime_dclicked)
        self.regimes = []

        # data window
        self.dataList = QtGui.QListWidget(self)
        self.dataDock.addWidget(self.dataList)
        self.dataList.itemDoubleClicked.connect(self.create_plot)

        # action for simulation control
        self.actSimulate = QtGui.QAction(self)
        self.actSimulate.setText('Simulate')
        self.actSimulate.setIcon(QtGui.QIcon('data/simulate.png'))
        self.actSimulate.triggered.connect(self.start_simulation)

        # actions for animation control
        self.actPlayPause = QtGui.QAction(self)
        self.actPlayPause.setText('Play')
        self.actPlayPause.setIcon(QtGui.QIcon('data/play.png'))
        self.actPlayPause.setDisabled(True)
        self.actPlayPause.triggered.connect(self.play_animation)

        self.actStop = QtGui.QAction(self)
        self.actStop.setText('Stop')
        self.actStop.setIcon(QtGui.QIcon('data/stop.png'))
        self.actStop.setDisabled(True)
        self.actStop.triggered.connect(self.stop_animation)

        self.speedDial = QtGui.QDial()
        self.speedDial.setDisabled(True)
        self.speedDial.setMinimum(0)
        self.speedDial.setMaximum(100)
        self.speedDial.setValue(50)
        self.speedDial.setSingleStep(1)
        self.speedDial.resize(24, 24)
        self.speedDial.valueChanged.connect(self.update_playback_gain)

        self.timeSlider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.timeSlider.setMinimum(0)
        self.timeSliderRange = 1000
        self.timeSlider.setMaximum(self.timeSliderRange)
        self.timeSlider.setTickInterval(1)
        self.timeSlider.setTracking(True)
        self.timeSlider.setDisabled(True)
        self.timeSlider.valueChanged.connect(self.update_playback_time)

        self.playbackTime = 0
        self.playbackGain = 1
        self.currentStepSize = 0
        self.currentEndTime = 0
        self.playbackTimer = QTimer()
        self.playbackTimer.timeout.connect(self.increment_playback_time)
        self.playbackTimeChanged.connect(self.update_gui)
        self.playbackTimeout = 33  # in [ms] -> 30 fps

        self.actSave = QtGui.QAction(self)
        self.actSave.setText('Save')
        self.actSave.setIcon(QtGui.QIcon('data/save.png'))
        self.actSave.setDisabled(True)
        self.actSave.triggered.connect(self.save_data)

        self.actLoadRegimes = QtGui.QAction(self)
        self.actLoadRegimes.setText('load regimes')
        self.actLoadRegimes.setIcon(QtGui.QIcon('data/load.png'))
        self.actLoadRegimes.setDisabled(False)
        self.actLoadRegimes.triggered.connect(self.load_regimes_clicked)

        self.actExecuteRegimes = QtGui.QAction(self)
        self.actExecuteRegimes.setText('execute all regimes')
        self.actExecuteRegimes.setIcon(QtGui.QIcon('data/execute_regimes.png'))
        self.actExecuteRegimes.setDisabled(True)
        self.actExecuteRegimes.triggered.connect(self.execute_regimes_clicked)

        self.actPostprocessing = QtGui.QAction(self)
        self.actPostprocessing.setText('launch postprocessor')
        self.actPostprocessing.setIcon(QtGui.QIcon('data/postprocessing.png'))
        self.actPostprocessing.setDisabled(False)
        self.actPostprocessing.triggered.connect(self.postprocessing_clicked)

        # toolbar for control
        self.toolbarSim = QtGui.QToolBar('Simulation')
        self.toolbarSim.setIconSize(QtCore.QSize(32, 32))
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
        self.postprocessor = None

        # load default config
        self.runningBatch = False
        self.currentRegimeIndex = 0
        self.regimes = []
        configFile = os.path.join('..', 'regimes', 'default.sreg')
        self._load_regimes(configFile)
        self._apply_regime(self.currentRegimeIndex)
        self.regimeFinished.connect(self.run_next_regime)
        self.finishedRegimeBatch.connect(self.regime_batch_finished)

        # statusbar
        self.status = QtGui.QStatusBar(self)
        self.setStatusBar(self.status)
        self.statusLabel = QtGui.QLabel('Ready.')
        self.statusBar().addPermanentWidget(self.statusLabel)
        self.timeLabel = QtGui.QLabel('current time: 0.0')
        self.statusBar().addPermanentWidget(self.timeLabel)

        # shortcuts
        self.delShort = QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Delete), self.regimeList)
        self.delShort.activated.connect(self.remove_regime_items)

        self.shortOpenRegime = QtGui.QShortcut(QtGui.QKeySequence.Open, self)
        self.shortOpenRegime.activated.connect(self.load_regimes_clicked)

        self.shortSaveResult = QtGui.QShortcut(QtGui.QKeySequence.Save, self)
        self.shortSaveResult.activated.connect(self.save_data)
        self.shortSaveResult.setEnabled(False)

        self.shortSpeedUp = QtGui.QShortcut(QtGui.QKeySequence.ZoomIn, self)
        self.shortSpeedUp.activated.connect(self.increment_playback_speed)

        self.shortSpeedDown = QtGui.QShortcut(QtGui.QKeySequence.ZoomOut, self)
        self.shortSpeedDown.activated.connect(self.decrement_playback_speed)

        self.shortSpeedReset = QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_0), self)
        self.shortSpeedReset.activated.connect(self.reset_playback_speed)

        self.shortRunSimulation = QtGui.QShortcut(QtGui.QKeySequence('F5'), self)
        self.shortRunSimulation.activated.connect(self.start_simulation)

        self.shortRunRegimeBatch = QtGui.QShortcut(QtGui.QKeySequence('F6'), self)
        self.shortRunRegimeBatch.activated.connect(self.execute_regimes_clicked)

        self.shortRunPostprocessing = QtGui.QShortcut(QtGui.QKeySequence('F7'), self)
        self.shortRunPostprocessing.activated.connect(self.postprocessing_clicked)

        self.shortPlayPause = QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Space), self)
        self.shortPlayPause.activated.connect(self.play_animation)
        self.shortPlayPause.setEnabled(False)

    def set_visualizer(self, vis):
        assert isinstance(vis, Visualizer)
        self.visualizer = vis

    def play_animation(self):
        """
        play the animation
        """
        # self.statusLabel.setText('playing animation')
        self.actPlayPause.setText('Pause')
        self.actPlayPause.setIcon(QtGui.QIcon('data/pause.png'))
        self.actPlayPause.triggered.disconnect(self.play_animation)
        self.actPlayPause.triggered.connect(self.pause_animation)
        self.shortPlayPause.activated.disconnect(self.play_animation)
        self.shortPlayPause.activated.connect(self.pause_animation)
        self.playbackTimer.start(self.playbackTimeout)

    def pause_animation(self):
        """
        pause the animation
        """
        # self.statusLabel.setText('pausing animation')
        self.playbackTimer.stop()
        self.actPlayPause.setText('Play')
        self.actPlayPause.setIcon(QtGui.QIcon('data/play.png'))
        self.actPlayPause.triggered.disconnect(self.pause_animation)
        self.actPlayPause.triggered.connect(self.play_animation)
        self.shortPlayPause.activated.disconnect(self.pause_animation)
        self.shortPlayPause.activated.connect(self.play_animation)

    def stop_animation(self):
        """
        pause the animation
        """
        # self.statusLabel.setText('stopping animation')
        if self.actPlayPause.text() == 'Pause':
            # animation is playing -> stop it
            self.playbackTimer.stop()
            self.actPlayPause.setText('Play')
            self.actPlayPause.setIcon(QtGui.QIcon('data/play.png'))
            self.actPlayPause.triggered.disconnect(self.pause_animation)
            self.actPlayPause.triggered.connect(self.play_animation)
            self.shortPlayPause.activated.disconnect(self.pause_animation)
            self.shortPlayPause.activated.connect(self.play_animation)

        self.timeSlider.setValue(0)

    def start_simulation(self):
        """
        start the simulation and disable start button
        """
        regime_name = str(self.regimeList.item(self.currentRegimeIndex).text())
        self.statusLabel.setText('simulating ' + regime_name + ':')
        print 'Simulating: ', regime_name

        self.actSimulate.setDisabled(True)
        self.actExecuteRegimes.setDisabled(True)
        self.simProgress = QtGui.QProgressBar(self)
        self.sim.simulationProgressChanged.connect(self.simProgress.setValue)
        self.statusBar().addWidget(self.simProgress)
        self.runSimulation.emit()

    def save_data(self, name=None):
        """
        save current dataset
        """

        if not name:
            name = QtGui.QInputDialog.getText(self,
                                              'Please specify regime name',
                                              'regime name')
            if not name[1]:
                return
            else:
                name = str(name[0])

        self.statusLabel.setText('dumping data')
        self.currentDataset.update({'regime name': name})
        path = os.path.join(os.path.pardir, 'results', 'simulation', self.regimeFileName)

        # check for path existence
        if not os.path.isdir(path):
            os.makedirs(path)

        file_name = os.path.join(path, time.strftime('%Y%m%d-%H%M%S') + '_' + name + '.bbr')
        with open(file_name, 'wb') as f:
            cPickle.dump(self.currentDataset, f, protocol=2)

    def load_regimes_clicked(self):
        regime_path = os.path.join('../regimes/')
        file_name = QtGui.QFileDialog.getOpenFileName(self,
                                                      "Open Regime File",
                                                      regime_path,
                                                      "Simulation Regime files (*.sreg)")
        if not file_name:
            return

        self._load_regimes(str(file_name))

    def _load_regimes(self, file_name):
        """
        load simulation regime from file
        """
        self.regimeFileName = os.path.split(file_name)[-1][:-5]
        print 'loading regime file: ', self.regimeFileName
        with open(file_name, 'r') as f:
            self.regimes += yaml.load(f)

        self._update_regime_list()

        if self.regimes:
            self.actExecuteRegimes.setDisabled(False)

        self.statusBar().showMessage('loaded ' + str(len(self.regimes)) + ' regimes.', 1000)
        return

    def _update_regime_list(self):
        self.regimeList.clear()
        for reg in self.regimes:
            self.regimeList.addItem(reg['name'])

    def remove_regime_items(self):
        if self.regimeList.currentRow() >= 0:
            # flag all selected files as invalid
            items = self.regimeList.selectedItems()
            for item in items:
                del self.regimes[self.regimeList.row(item)]
                self.regimeList.takeItem(self.regimeList.row(item))

    def regime_dclicked(self, item):
        """
        applies the selected regime to the current target
        """
        regime_name = str(item.text())
        self.statusBar().showMessage('applying regime: ' + regime_name, 1000)
        self.sim.setRegime(next((reg for reg in self.regimes if reg['name'] == regime_name), None))

    def _apply_regime(self, index=0):
        if index >= len(self.regimes):
            print 'applyRegime(): index error!'
            return

        self.sim.setRegime(self.regimes[index])

    def execute_regimes_clicked(self):
        """
        execute all regimes in the current list
        """
        self.runningBatch = True
        self.currentRegimeIndex = -1
        self.regimeFinished.emit()

    def run_next_regime(self):
        """
        executes the next regime
        """
        self.currentRegimeIndex += 1
        # are we finished?
        if self.currentRegimeIndex >= len(self.regimes):
            self.finishedRegimeBatch.emit()
            return

        self._apply_regime(self.currentRegimeIndex)
        self.start_simulation()

    def regime_batch_finished(self):
        self.runningBatch = False
        self.actExecuteRegimes.setDisabled(False)
        self.currentRegimeIndex = 0
        self.statusLabel.setText('All regimes have been simulated!')
        self.actSave.setDisabled(True)

    def simulation_finished(self, data):
        """
        main hook to be called by the simulation interface if integration is finished
        integration finished, enable play button and update plots
        """
        self.actSimulate.setDisabled(False)
        self.actPlayPause.setDisabled(False)
        self.shortPlayPause.setEnabled(True)
        self.shortSaveResult.setEnabled(True)
        self.actStop.setDisabled(False)
        self.actSave.setDisabled(False)
        self.speedDial.setDisabled(False)
        self.timeSlider.setDisabled(False)
        self.statusBar().removeWidget(self.simProgress)
        self.statusLabel.setText('simulation finished.')
        self.sim.simulationProgressChanged.disconnect(self.simProgress.setValue)
        del self.simProgress

        self.timeSlider.triggerAction(QtGui.QAbstractSlider.SliderToMinimum)

        self.currentDataset = data
        self._read_results()
        self._update_data_list()
        self._update_plots()

        self.stop_animation()
        # self.playAnimation()

        if self.runningBatch:
            regime_name = self.regimes[self.currentRegimeIndex]['name']
            self.save_data(regime_name)
            self.regimeFinished.emit()
        else:
            self.actExecuteRegimes.setDisabled(False)

    def simulation_failed(self, data):
        """
        integration failed, enable play button and update plots
        #TODO show warning window
        """
        self.statusLabel.setText('simulation failed!')
        self.simulation_finished(data)

    def _read_results(self):
        self.currentStepSize = 1.0 / self.currentDataset['modules']['solver']['measure rate']
        self.currentEndTime = self.currentDataset['modules']['solver']['end time']
        self.validData = True

    def add_plot_to_dock(self, plot_widget):
        self.d3.addWidget(plot_widget)

    def increment_playback_speed(self):
        self.speedDial.setValue(self.speedDial.value() + self.speedDial.singleStep())

    def decrement_playback_speed(self):
        self.speedDial.setValue(self.speedDial.value() - self.speedDial.singleStep())

    def reset_playback_speed(self):
        self.speedDial.setValue(self.speedDial.range() / 2)

    def increment_playback_time(self):
        """
        go one timestep forward in playback
        """
        increment = self.playbackGain * self.playbackTimeout / 1000
        if self.playbackTime + increment <= self.currentEndTime:
            self.playbackTime += increment
            pos = self.playbackTime / self.currentEndTime * self.timeSliderRange
            self.timeSlider.blockSignals(True)
            self.timeSlider.setValue(pos)
            self.timeSlider.blockSignals(False)
            self.playbackTimeChanged.emit()
        else:
            self.pause_animation()
            return

    def update_playback_gain(self, val):
        """
        adjust playback time to slider value
        """
        self.playbackGain = 10 ** (5.0 * (val - self.speedDial.maximum() / 2) / self.speedDial.maximum())

    def update_playback_time(self):
        """
        adjust playback time to slider value
        """
        self.playbackTime = 1.0 * self.timeSlider.value() / self.timeSliderRange * self.currentEndTime
        self.playbackTimeChanged.emit()
        return

    def update_gui(self):
        """
        updates the graphical user interface, including:
            - timestamp
            - visualisation
            - timecurser in diagrams
        """
        if not self.validData:
            return

        self.timeLabel.setText('current time: %4f' % self.playbackTime)

        # update time cursor in plots
        self._update_time_cursor()

        # update state of rendering
        if self.visualizer:
            state = [self.interpolate(self.currentDataset['results']['model_output.' + str(i)])
                     for i in range(self.model.getOutputDimension())]
            self.visualizer.update_scene(state)

    def interpolate(self, data):
        """
        find corresponding index in dataset that fits the current playback time

        :param data: dataset in which the correct datum has to be found
        :return: datum fitting the current playbacktime
        """
        idx = next((index for index, val in enumerate(self.currentDataset['results']['simTime'])
                    if val >= self.playbackTime), None)

        if not idx:
            return 0
        else:
            return data[idx]

    def _update_data_list(self):
        self.dataList.clear()
        for key, val in self.currentDataset['results'].iteritems():
            if type(val) is not str and isinstance(val, collections.Sequence):
                self.dataList.insertItem(0, key)

    def create_plot(self, item):
        """
        creates a plot widget corresponding to the ListItem
        """
        title = str(item.text())
        data = self.currentDataset['results'][title]
        t = self.currentDataset['results']['simTime']

        dock = pg.dockarea.Dock(title)
        self.area.addDock(dock, 'above', self.plotDocks[-1])

        widget = pg.PlotWidget(title=title)
        widget.plot(x=t, y=data)

        time_line = pg.InfiniteLine(self.playbackTime, angle=90, movable=False, pen=pg.mkPen('#FF0000', width=2.0))
        widget.getPlotItem().addItem(time_line)

        dock.addWidget(widget)

        self.plotDocks.append(dock)
        self.plotWidgets.append(widget)
        self.timeLines.append(time_line)

    def _update_time_cursor(self):
        """
        updates the timelines of all plot windows
        """
        for line in self.timeLines:
            line.setValue(self.playbackTime)

    def _update_plots(self):
        """
        plot the fresh simulation data
        """
        for dock in self.plotDocks:
            for widget in dock.widgets:
                if not self.dataList.findItems(dock.name(), QtCore.Qt.MatchExactly):
                    # no data for this plot -> reset it
                    widget.getPlotItem().clear()
                else:
                    widget.getPlotItem().clear()
                    widget.getPlotItem().plot(x=self.currentDataset['results']['simTime'],
                                              y=self.currentDataset['results'][dock.name()])

    def target_view_changed(self, index):
        self.targetView.resizeColumnToContents(0)

    def postprocessing_clicked(self):
        """
        starts to post- and metaprocessing application
        """
        self.statusBar().showMessage('launching postprocessor', 1000)
        if not self.postprocessor:
            self.postprocessor = PostProcessor(self)
        self.post.show()
