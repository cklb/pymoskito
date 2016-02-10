# -*- coding: utf-8 -*-

from __future__ import division

# system
import collections
import time
import os
import yaml
import cPickle
import numpy as np

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
from processing_gui import PostProcessor

from tools import get_resource


class SimulationGui(QtGui.QMainWindow):
    """
    class for the graphical user interface
    """
    # TODO enable closing plot docks by right-clicking their name
    # TODO add ability to stop an simulation
    # TODO add ability to stop regime execution

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
        self.runSimulation.connect(self.sim.run_simulation)
        self.sim.simulation_finished.connect(self.simulation_finished)
        self.sim.simulation_failed.connect(self.simulation_failed)
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
        self.setWindowTitle("PyMoskito")
        self.setWindowIcon(QtGui.QIcon(get_resource("mosquito.png")))

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

        # vtk window
        self.vtkLayout = QtGui.QVBoxLayout()
        self.frame = QtGui.QFrame()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vtkLayout.addWidget(self.vtkWidget)
        self.frame.setLayout(self.vtkLayout)
        self.vtkDock.addWidget(self.frame)
        self.vtk_renderer = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.vtk_renderer)
        self.visualizer = None

        # regime window
        self.regime_list = QtGui.QListWidget(self)
        self.regime_list.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.regimeDock.addWidget(self.regime_list)
        self.regime_list.itemDoubleClicked.connect(self.regime_dclicked)
        self._regimes = []
        self.regime_file_name = ""

        # data window
        self.dataList = QtGui.QListWidget(self)
        self.dataDock.addWidget(self.dataList)
        self.dataList.itemDoubleClicked.connect(self.create_plot)

        # actions for simulation control
        self.actSimulate = QtGui.QAction(self)
        self.actSimulate.setText('Simulate')
        self.actSimulate.setIcon(QtGui.QIcon(get_resource("simulate.png")))
        self.actSimulate.triggered.connect(self.start_simulation)

        # actions for animation control
        self.actPlayPause = QtGui.QAction(self)
        self.actPlayPause.setText('Play')
        self.actPlayPause.setIcon(QtGui.QIcon(get_resource("play.png")))
        self.actPlayPause.setDisabled(True)
        self.actPlayPause.triggered.connect(self.play_animation)

        self.actStop = QtGui.QAction(self)
        self.actStop.setText('Stop')
        self.actStop.setIcon(QtGui.QIcon(get_resource("stop.png")))
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
        self.actSave.setIcon(QtGui.QIcon(get_resource("save.png")))
        self.actSave.setDisabled(True)
        self.actSave.triggered.connect(self.save_data)

        self.actLoadRegimes = QtGui.QAction(self)
        self.actLoadRegimes.setText('load regimes')
        self.actLoadRegimes.setIcon(QtGui.QIcon(get_resource("load.png")))
        self.actLoadRegimes.setDisabled(False)
        self.actLoadRegimes.triggered.connect(self.load_regime_dialog)

        self.actExecuteRegimes = QtGui.QAction(self)
        self.actExecuteRegimes.setText('execute all regimes')
        self.actExecuteRegimes.setIcon(QtGui.QIcon(get_resource("execute_regimes.png")))
        self.actExecuteRegimes.setDisabled(True)
        self.actExecuteRegimes.triggered.connect(self.execute_regimes_clicked)

        self.actPostprocessing = QtGui.QAction(self)
        self.actPostprocessing.setText('launch postprocessor')
        self.actPostprocessing.setIcon(QtGui.QIcon(get_resource("processing.png")))
        self.actPostprocessing.setDisabled(False)
        self.actPostprocessing.triggered.connect(self.postprocessing_clicked)

        self.act_reset_camera = QtGui.QAction(self)
        self.act_reset_camera.setText('reset camera')
        self.act_reset_camera.setIcon(QtGui.QIcon(get_resource("reset_camera.png")))
        self.act_reset_camera.setDisabled(False)
        self.act_reset_camera.triggered.connect(self.reset_camera_clicked)


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
        self.toolbarSim.addAction(self.act_reset_camera)
        self.postprocessor = None

        # regime management
        self.runningBatch = False
        self.currentRegimeIndex = 0
        self._regimes = []

        self.regimeFinished.connect(self.run_next_regime)
        self.finishedRegimeBatch.connect(self.regime_batch_finished)

        # status bar
        self.status = QtGui.QStatusBar(self)
        self.setStatusBar(self.status)
        self.statusLabel = QtGui.QLabel('Ready.')
        self.statusBar().addPermanentWidget(self.statusLabel)
        self.timeLabel = QtGui.QLabel('current time: 0.0')
        self.statusBar().addPermanentWidget(self.timeLabel)

        # shortcuts
        self.delShort = QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Delete), self.regime_list)
        self.delShort.activated.connect(self.remove_regime_items)

        self.shortOpenRegime = QtGui.QShortcut(QtGui.QKeySequence.Open, self)
        self.shortOpenRegime.activated.connect(self.load_regime_dialog)

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
        self.vtkWidget.Initialize()

    def play_animation(self):
        """
        play the animation
        """
        # self.statusLabel.setText('playing animation')
        self.actPlayPause.setText('Pause')
        self.actPlayPause.setIcon(QtGui.QIcon(get_resource("pause.png")))
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
        self.actPlayPause.setIcon(QtGui.QIcon(get_resource("play.png")))
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
            self.actPlayPause.setIcon(QtGui.QIcon(get_resource("play.png")))
            self.actPlayPause.triggered.disconnect(self.pause_animation)
            self.actPlayPause.triggered.connect(self.play_animation)
            self.shortPlayPause.activated.disconnect(self.pause_animation)
            self.shortPlayPause.activated.connect(self.play_animation)

        self.timeSlider.setValue(0)

    def start_simulation(self):
        """
        start the simulation and disable start button
        """
        regime_name = str(self.regime_list.item(self.currentRegimeIndex).text())
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
        :param name: name of the file
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
        path = os.path.join(os.path.pardir, 'results', 'simulation', self.regime_file_name)

        # check for path existence
        if not os.path.isdir(path):
            os.makedirs(path)

        # pmr - PyMoskito Result
        file_name = os.path.join(path, time.strftime('%Y%m%d-%H%M%S') + '_' + name + '.pmr')

        with open(file_name, 'wb') as f:
            cPickle.dump(self.currentDataset, f, protocol=2)

    def load_regime_dialog(self):
        regime_path = os.path.join('../regimes/')
        file_name = QtGui.QFileDialog.getOpenFileName(self,
                                                      "Open Regime File",
                                                      regime_path,
                                                      "Simulation Regime files (*.sreg)")
        if not file_name:
            return

        self.load_regimes_from_file(str(file_name))

    def load_regimes_from_file(self, file_name):
        """
        load simulation regime from file
        :param file_name:
        """
        self.regime_file_name = os.path.split(file_name)[-1][:-5]
        print("loading regime file: {0}".format(self.regime_file_name))
        with open(file_name, 'r') as f:
            self._regimes += yaml.load(f)

        self._update_regime_list()

        if self._regimes:
            self.actExecuteRegimes.setDisabled(False)

        self.statusBar().showMessage('loaded ' + str(len(self._regimes)) + ' regimes.', 1000)
        return

    def _update_regime_list(self):
        self.regime_list.clear()
        for reg in self._regimes:
            self.regime_list.addItem(reg['Name'])

    def remove_regime_items(self):
        if self.regime_list.currentRow() >= 0:
            # flag all selected files as invalid
            items = self.regime_list.selectedItems()
            for item in items:
                del self._regimes[self.regime_list.row(item)]
                self.regime_list.takeItem(self.regime_list.row(item))

    def regime_dclicked(self, item):
        """
        applies the selected regime to the current target
        :param item:
        """
        self.apply_regime_by_name(str(item.text()))

    def apply_regime_by_name(self, regime_name):
        """
        :param regime_name:
        :return:
        """
        # get regime obj
        regime = next((reg for reg in self._regimes if reg['Name'] == regime_name), None)
        if regime is None:
            print("apply_regime_by_name(): Error no regime called {0}".format(regime_name))
            return

        # apply
        self.statusBar().showMessage('applying regime: ' + regime_name, 1000)
        self.sim.set_regime(regime)

    def _apply_regime_by_idx(self, index=0):
        if index >= len(self._regimes):
            print 'applyRegime(): index error!'
            return

        self.sim.set_regime(self._regimes[index])

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
        if self.currentRegimeIndex >= len(self._regimes):
            self.finishedRegimeBatch.emit()
            return

        self._apply_regime_by_idx(self.currentRegimeIndex)
        self.start_simulation()

    def regime_batch_finished(self):
        self.runningBatch = False
        self.actExecuteRegimes.setDisabled(False)
        self.currentRegimeIndex = 0
        self.statusLabel.setText('All regimes have been simulated!')
        self.actSave.setDisabled(True)

    def simulation_finished(self, data):
        """
        main.py hook to be called by the simulation interface if integration is finished
        integration finished, enable play button and update plots
        :param data:
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
            regime_name = self._regimes[self.currentRegimeIndex]['name']
            self.save_data(regime_name)
            self.regimeFinished.emit()
        else:
            self.actExecuteRegimes.setDisabled(False)

    def simulation_failed(self, data):
        """
        integration failed, enable play button and update plots
        :param data:
        """
        #TODO show warning window
        self.statusLabel.setText('simulation failed!')
        self.simulation_finished(data)

    def _read_results(self):
        self.currentStepSize = 1.0/self.currentDataset['modules']['Solver']['measure rate']
        self.currentEndTime = self.currentDataset["modules"]["Simulator"].end_time
        self.validData = True

    def add_plot_to_dock(self, plot_widget):
        self.d3.addWidget(plot_widget)

    def increment_playback_speed(self):
        self.speedDial.setValue(self.speedDial.value() + self.speedDial.singleStep())

    def decrement_playback_speed(self):
        self.speedDial.setValue(self.speedDial.value() - self.speedDial.singleStep())

    def reset_playback_speed(self):
        self.speedDial.setValue(self.speedDial.range()/2)

    def increment_playback_time(self):
        """
        go one time step forward in playback
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
        :param val:
        """
        self.playbackGain = 10**(5.0*(val - self.speedDial.maximum()/2)/self.speedDial.maximum())

    def update_playback_time(self):
        """
        adjust playback time to slider value
        """
        self.playbackTime = self.timeSlider.value()/self.timeSliderRange*self.currentEndTime
        self.playbackTimeChanged.emit()
        return

    def update_gui(self):
        """
        updates the graphical user interface, including:
            - timestamp
            - visualisation
            - time curser in diagrams
        """
        if not self.validData:
            return

        self.timeLabel.setText('current time: %4f' % self.playbackTime)

        # update time cursor in plots
        self._update_time_cursor()

        # update state of rendering
        if self.visualizer:
            state = self.interpolate(self.currentDataset["results"]["Solver"])
            self.visualizer.update_scene(state)
            self.vtkWidget.GetRenderWindow().Render()

    def interpolate(self, data):
        """
        find corresponding item in dataset that fits the current playback time

        :param data: dataset in which the correct datum has to be found
        :return: datum fitting the current playback time
        """
        idx = next((index for index, val in enumerate(self.currentDataset['results']['time'])
                    if val >= self.playbackTime), None)

        if idx is None:
            print("interpolate(): Error no entry found for t={0}".format(self.playbackTime))
            return None
        else:
            if len(data.shape) == 1:
                return data[idx]
            elif len(data.shape) == 2:
                return data[idx, :]
            else:
                print("interpolate(): Error Dimension {0} not understood.".format(data.shape))
                return None

    def _update_data_list(self):
        self.dataList.clear()
        for module, results in self.currentDataset['results'].iteritems():
            if not isinstance(results, np.ndarray):
                continue

            if len(results.shape) == 1:
                self.dataList.insertItem(0, "{0}".format(module))
            elif len(results.shape) == 2:
                for col in range(results.shape[1]):
                    self.dataList.insertItem(0, "{0}.{1}".format(module, col))
            elif len(results.shape) == 3:
                for col in range(results.shape[1]):
                    self.dataList.insertItem(0, "{0}.{1}".format(module, col))


    def create_plot(self, item):
        """
        creates a plot widget corresponding to the ListItem
        :param item:
        """

        title = str(item.text())
        data = self._get_data_by_name(title)
        t = self.currentDataset['results']['time']

        dock = pg.dockarea.Dock(title)
        self.area.addDock(dock, 'above', self.plotDocks[-1])

        widget = pg.PlotWidget(title=title)
        widget.plot(x=t, y=data)

        time_line = pg.InfiniteLine(self.playbackTime, angle=90, movable=False, pen=pg.mkPen('#FF0000', width=2.0))
        widget.getPlotItem().addItem(time_line)

        # enable grid
        widget.showGrid(True, True)

        dock.addWidget(widget)

        self.plotDocks.append(dock)
        self.plotWidgets.append(widget)
        self.timeLines.append(time_line)

    def _get_data_by_name(self, name):
        tmp = name.split(".")
        if len(tmp) == 1:
            data = self.currentDataset['results'][tmp[0]]
            # if the dataset contains 1d array, we have to convert it to float
            data = [float(x) for x in data]
        elif len(tmp) == 2:
            if len(self.currentDataset['results'][tmp[0]].shape) == 2:
                data = self.currentDataset['results'][tmp[0]][:, tmp[1]]
            if len(self.currentDataset['results'][tmp[0]].shape) == 3:  # Dataset has the structure [ [[1]], [[2]] ]
                data = self.currentDataset["results"][tmp[0]][..., tmp[1], 0]

        return data

    def _update_time_cursor(self):
        """
        updates the time lines of all plot windows
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
                    # TODO remove tab from dock and del instance
                else:
                    widget.getPlotItem().clear()
                    x_data = self.currentDataset['results']['time']
                    y_data = self._get_data_by_name(dock.name())
                    widget.getPlotItem().plot(x=x_data, y=y_data)

    def target_view_changed(self, index):
        """
        ?
        :param index:
        :return:
        """
        self.targetView.resizeColumnToContents(0)

    def postprocessing_clicked(self):
        """
        starts the post- and metaprocessing application
        """
        self.statusBar().showMessage('launching postprocessor', 1000)
        if hasattr(self, "postprocessor"):
            self.postprocessor = PostProcessor(self)
        self.postprocessor.show()

    def reset_camera_clicked(self):
        """
        reset camera in vtk window
        """
        self.visualizer.reset_camera()
        self.vtkWidget.GetRenderWindow().Render()
