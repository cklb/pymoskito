# -*- coding: utf-8 -*-

# system
import logging
import time
import os
from operator import itemgetter
import yaml
import pickle

import numpy as np

# Qt
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import (QWidget, QAction, QSlider, QDial, QMainWindow, QTreeView, QListWidget,
                             QAbstractItemView, QToolBar, QStatusBar, QProgressBar, QLabel, QShortcut,
                             QLineEdit, QFileDialog, QInputDialog, QAbstractSlider, QFrame, QVBoxLayout)

# pyqtgraph
import pyqtgraph as pg
from pyqtgraph.dockarea import DockArea

# vtk
vtk_error_msg = ""
try:
    import vtk

    from vtk import vtkRenderer
    from vtk import qt
    from .visualization import QVTKRenderWindowInteractor  # import patched class
    vtk_available = True
except ImportError as e:
    vtk_available = False
    vtk_error_msg = e.msg
    vtkRenderer = None
    QVTKRenderWindowInteractor = None

# pymoskito
from .visualization import MplVisualizer, VtkVisualizer
from .registry import get_registered_visualizers
from .simulation_interface import SimulatorInteractor, SimulatorView
from .processing_gui import PostProcessor
from .tools import get_resource, PostFilter, QPlainTextEditLogger


class SimulationGui(QMainWindow):
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
        QMainWindow.__init__(self)

        self._logger = logging.getLogger(self.__class__.__name__)

        # Create Simulation Backend
        self.guiProgress = None
        self.cmdProgress = None
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
        self.result_view = QTreeView()

        # the docking area allows to rearrange the user interface at runtime
        self.area = pg.dockarea.DockArea()

        # Window properties
        self.setCentralWidget(self.area)
        self.resize(1000, 700)
        self.setWindowTitle("PyMoskito")
        res_path = get_resource("mosquito.png")
        icon = QIcon(res_path)
        self.setWindowIcon(icon)

        # create docks
        self.propertyDock = pg.dockarea.Dock("Properties")
        self.animationDock = pg.dockarea.Dock("Animation")
        self.regimeDock = pg.dockarea.Dock("Regimes")
        self.dataDock = pg.dockarea.Dock("Data")
        self.logDock = pg.dockarea.Dock("Log")
        self.plotDocks = []
        self.plotDocks.append(pg.dockarea.Dock("Placeholder"))
        self.plotWidgets = []
        self.timeLines = []

        # arrange docks
        self.area.addDock(self.animationDock, "right")
        self.area.addDock(self.regimeDock, "left", self.animationDock)
        self.area.addDock(self.propertyDock, "bottom", self.regimeDock)
        self.area.addDock(self.dataDock, "bottom", self.propertyDock)
        self.area.addDock(self.plotDocks[-1], "bottom", self.animationDock)
        self.area.addDock(self.logDock, "bottom", self.dataDock)

        # add widgets to the docks
        self.propertyDock.addWidget(self.targetView)

        if not vtk_available:
            self._logger.error("loading vtk failed with:{}".format(vtk_error_msg))

        # check if there is a registered visualizer
        available_vis = get_registered_visualizers()
        self._logger.info("found visualizers: {}".format([name for cls, name in available_vis]))
        if available_vis:
            # instantiate the first visualizer
            self._logger.info("loading visualizer '{}'".format(available_vis[0][1]))
            self.animationLayout = QVBoxLayout()

            if issubclass(available_vis[0][0], MplVisualizer):
                self.animationWidget = QWidget()
                self.visualizer = available_vis[0][0](self.animationWidget, self.animationLayout)
                self.animationDock.addWidget(self.animationWidget)
            elif issubclass(available_vis[0][0], VtkVisualizer):
                if vtk_available:
                    # vtk window
                    self.animationFrame = QFrame()
                    self.vtkWidget = QVTKRenderWindowInteractor(self.animationFrame)
                    self.animationLayout.addWidget(self.vtkWidget)
                    self.animationFrame.setLayout(self.animationLayout)
                    self.animationDock.addWidget(self.animationFrame)
                    self.vtk_renderer = vtkRenderer()
                    self.vtkWidget.GetRenderWindow().AddRenderer(self.vtk_renderer)
                    self.visualizer = available_vis[0][0](self.vtk_renderer)
                    self.vtkWidget.Initialize()
                else:
                    self._logger.warn("visualizer depends on vtk which is not available on this system!")
            elif available_vis:
                raise NotImplementedError
        else:
            self.visualizer = None

        # regime window
        self.regime_list = QListWidget(self)
        self.regime_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.regimeDock.addWidget(self.regime_list)
        self.regime_list.itemDoubleClicked.connect(self.regime_dclicked)
        self._regimes = []
        self.regime_file_name = ""

        # data window
        self.dataList = QListWidget(self)
        self.dataDock.addWidget(self.dataList)
        self.dataList.itemDoubleClicked.connect(self.create_plot)

        # actions for simulation control
        self.actSimulate = QAction(self)
        self.actSimulate.setText("Simulate")
        self.actSimulate.setIcon(QIcon(get_resource("simulate.png")))
        self.actSimulate.triggered.connect(self.start_simulation)

        # actions for animation control
        self.actPlayPause = QAction(self)
        self.actPlayPause.setText("Play")
        self.actPlayPause.setIcon(QIcon(get_resource("play.png")))
        self.actPlayPause.setDisabled(True)
        self.actPlayPause.triggered.connect(self.play_animation)

        self.actStop = QAction(self)
        self.actStop.setText("Stop")
        self.actStop.setIcon(QIcon(get_resource("stop.png")))
        self.actStop.setDisabled(True)
        self.actStop.triggered.connect(self.stop_animation)

        self.speedDial = QDial()
        self.speedDial.setDisabled(True)
        self.speedDial.setMinimum(0)
        self.speedDial.setMaximum(100)
        self.speedDial.setValue(50)
        self.speedDial.setSingleStep(1)
        self.speedDial.resize(24, 24)
        self.speedDial.valueChanged.connect(self.update_playback_gain)

        self.timeSlider = QSlider(Qt.Horizontal, self)
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

        self.actSave = QAction(self)
        self.actSave.setText('Save')
        self.actSave.setIcon(QIcon(get_resource("save.png")))
        self.actSave.setDisabled(True)
        self.actSave.triggered.connect(self.export_simulation_data)

        self.actLoadRegimes = QAction(self)
        self.actLoadRegimes.setText("load regimes")
        self.actLoadRegimes.setIcon(QIcon(get_resource("load.png")))
        self.actLoadRegimes.setDisabled(False)
        self.actLoadRegimes.triggered.connect(self.load_regime_dialog)

        self.actExecuteRegimes = QAction(self)
        self.actExecuteRegimes.setText("execute all regimes")
        self.actExecuteRegimes.setIcon(QIcon(get_resource("execute_regimes.png")))
        self.actExecuteRegimes.setDisabled(True)
        self.actExecuteRegimes.triggered.connect(self.execute_regimes_clicked)

        self.actPostprocessing = QAction(self)
        self.actPostprocessing.setText("launch postprocessor")
        self.actPostprocessing.setIcon(QIcon(get_resource("processing.png")))
        self.actPostprocessing.setDisabled(False)
        self.actPostprocessing.triggered.connect(self.postprocessing_clicked)

        self.act_reset_camera = QAction(self)
        self.act_reset_camera.setText("reset camera")
        self.act_reset_camera.setIcon(QIcon(get_resource("reset_camera.png")))
        if available_vis:
            self.act_reset_camera.setDisabled(not self.visualizer.can_reset_view)
        self.act_reset_camera.triggered.connect(self.reset_camera_clicked)

        # toolbar for control
        self.toolbarSim = QToolBar("Simulation")
        self.toolbarSim.setIconSize(QSize(32, 32))
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
        self._current_regime_index = 0
        self._regimes = []

        self.regimeFinished.connect(self.run_next_regime)
        self.finishedRegimeBatch.connect(self.regime_batch_finished)

        # log dock
        self.logBox = QPlainTextEditLogger(self)
        self.logBox.setLevel(logging.INFO)

        formatter = logging.Formatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                                      datefmt="%H:%M:%S")
        self.logBox.setFormatter(formatter)

        self.log_filter = PostFilter(invert=True)
        self.logBox.addFilter(self.log_filter)

        logging.getLogger().addHandler(self.logBox)
        self.logDock.addWidget(self.logBox.widget)

        # status bar
        self.status = QStatusBar(self)
        self.setStatusBar(self.status)
        self.statusLabel = QLabel("Ready.")
        self.statusBar().addPermanentWidget(self.statusLabel)
        self.timeLabel = QLabel("current time: 0.0")
        self.statusBar().addPermanentWidget(self.timeLabel)

        # shortcuts
        self.delShort = QShortcut(QKeySequence(Qt.Key_Delete), self.regime_list)
        self.delShort.activated.connect(self.remove_regime_items)

        self.shortOpenRegime = QShortcut(QKeySequence.Open, self)
        self.shortOpenRegime.activated.connect(self.load_regime_dialog)

        self.shortSaveResult = QShortcut(QKeySequence.Save, self)
        self.shortSaveResult.activated.connect(self.export_simulation_data)
        self.shortSaveResult.setEnabled(False)

        self.shortSpeedUp = QShortcut(QKeySequence.ZoomIn, self)
        self.shortSpeedUp.activated.connect(self.increment_playback_speed)

        self.shortSpeedDown = QShortcut(QKeySequence.ZoomOut, self)
        self.shortSpeedDown.activated.connect(self.decrement_playback_speed)

        self.shortSpeedReset = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_0), self)
        self.shortSpeedReset.activated.connect(self.reset_playback_speed)

        self.shortRunSimulation = QShortcut(QKeySequence('F5'), self)
        self.shortRunSimulation.activated.connect(self.start_simulation)

        self.shortRunRegimeBatch = QShortcut(QKeySequence('F6'), self)
        self.shortRunRegimeBatch.activated.connect(self.execute_regimes_clicked)

        self.shortRunPostprocessing = QShortcut(QKeySequence('F7'), self)
        self.shortRunPostprocessing.activated.connect(self.postprocessing_clicked)

        self.shortPlayPause = QShortcut(QKeySequence(Qt.Key_Space), self)
        self.shortPlayPause.activated.connect(self.play_animation)
        self.shortPlayPause.setEnabled(False)

        self.postprocessor = None
        self._logger.info("Simulation GUI is up and running.")

    def set_visualizer(self, vis):
        self.visualizer = vis
        self.vtkWidget.Initialize()

    def play_animation(self):
        """
        play the animation
        """
        # self.statusLabel.setText('playing animation')
        self.actPlayPause.setText("Pause")
        self.actPlayPause.setIcon(QIcon(get_resource("pause.png")))
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
        self.actPlayPause.setText("Play")
        self.actPlayPause.setIcon(QIcon(get_resource("play.png")))
        self.actPlayPause.triggered.disconnect(self.pause_animation)
        self.actPlayPause.triggered.connect(self.play_animation)
        self.shortPlayPause.activated.disconnect(self.pause_animation)
        self.shortPlayPause.activated.connect(self.play_animation)

    def stop_animation(self):
        """
        pause the animation
        """
        # self.statusLabel.setText('stopping animation')
        if self.actPlayPause.text() == "Pause":
            # animation is playing -> stop it
            self.playbackTimer.stop()
            self.actPlayPause.setText("Play")
            self.actPlayPause.setIcon(QIcon(get_resource("play.png")))
            self.actPlayPause.triggered.disconnect(self.pause_animation)
            self.actPlayPause.triggered.connect(self.play_animation)
            self.shortPlayPause.activated.disconnect(self.pause_animation)
            self.shortPlayPause.activated.connect(self.play_animation)

        self.timeSlider.setValue(0)

    def start_simulation(self):
        """
        start the simulation and disable start button
        """
        regime_name = str(self.regime_list.item(self._current_regime_index).text())
        self.statusLabel.setText("simulating {}".format(regime_name))
        self._logger.info("Simulating: {}".format(regime_name))

        self.actSimulate.setDisabled(True)
        self.shortRunSimulation.setEnabled(False)
        self.shortRunRegimeBatch.setEnabled(False)
        self.actExecuteRegimes.setDisabled(True)
        self.guiProgress = QProgressBar(self)
        self.sim.simulationProgressChanged.connect(self.guiProgress.setValue)
        self.statusBar().addWidget(self.guiProgress)
        self.runSimulation.emit()

    def export_simulation_data(self, ok):
        """
        query the user for a custom name and export the current simulation results

        :param ok: unused parameter from QAction.triggered() Signal
        """
        self._save_data()

    def _save_data(self, regime_name=None):
        """
        Save the result data for a given regime.
        If *regime_name* is given, the result will be saved to a default path, making automated exporting easier.

        :param regime_name: name of the regime to export
        """
        if regime_name is None:
            regime_name = self._regimes[self._current_regime_index]["Name"]
            suggestion = time.strftime("%Y%m%d-%H%M%S") + "_" + regime_name + ".pmr"
            export_path = os.path.join(os.curdir)

            dialog = QFileDialog(self)
            dialog.setAcceptMode(QFileDialog.AcceptSave)
            dialog.setFileMode(QFileDialog.AnyFile)
            dialog.setDirectory(export_path)
            dialog.setNameFilter("PyMoskito Results (*.pmr)")
            dialog.selectFile(suggestion)

            if dialog.exec_():
                path = dialog.selectedFiles()[0]
            else:
                self._logger.warning("exported aborted")
                return

            # TODO for existence of file and aks for overwrite permission
        else:
            # create default path
            path = os.path.join(os.path.curdir, "results", "simulation")
            if not os.path.isdir(path):
                os.makedirs(path)

            path = os.path.join(path, time.strftime("%Y%m%d-%H%M%S") + "_" + regime_name + ".pmr")

        self.currentDataset.update({"regime name": regime_name})
        with open(path, "wb") as f:
            pickle.dump(self.currentDataset, f, protocol=4)

        self.statusLabel.setText("results saved to {}".format(path))
        self._logger.info("results saved to {}".format(path))

    def load_regime_dialog(self):
        regime_path = os.path.join(os.curdir)

        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setDirectory(regime_path)
        dialog.setNameFilter("Simulation Regime files (*.sreg)")

        if dialog.exec_():
            file = dialog.selectedFiles()[0]
            self.load_regimes_from_file(file)

    def load_regimes_from_file(self, file_name):
        """
        load simulation regime from file
        :param file_name:
        """
        self.regime_file_name = os.path.split(file_name)[-1][:-5]
        self._logger.info("loading regime file: {0}".format(self.regime_file_name))
        with open(file_name.encode(), "r") as f:
            self._regimes += yaml.load(f)

        self._update_regime_list()

        if self._regimes:
            self.actExecuteRegimes.setDisabled(False)

        self._logger.info("loaded {} regimes".format(len(self._regimes)))
        self.statusBar().showMessage("loaded {} regimes.".format(len(self._regimes)), 1000)
        return

    def _update_regime_list(self):
        self.regime_list.clear()
        for reg in self._regimes:
            self._logger.debug("adding '{}' to regime list".format(reg["Name"]))
            self.regime_list.addItem(reg["Name"])

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
        # get regime idx
        try:
            idx = list(map(itemgetter("Name"), self._regimes)).index(regime_name)
        except ValueError as e:
            self._logger.error("apply_regime_by_name(): Error no regime called {0}".format(regime_name))
            return

        # apply
        self._apply_regime_by_idx(idx)

    def _apply_regime_by_idx(self, index=0):
        if index >= len(self._regimes):
            self._logger.error("applyRegime: index error! ({})".format(index))
            return

        reg_name = self._regimes[index]["Name"]
        self.statusBar().showMessage("regime {} applied.".format(reg_name), 1000)
        self._logger.info("applying regime '{}'".format(reg_name))

        self._current_regime_index = index
        self.sim.set_regime(self._regimes[index])

    def execute_regimes_clicked(self):
        """
        execute all regimes in the current list
        """
        self.runningBatch = True
        self._current_regime_index = -1
        self.regimeFinished.emit()

    def run_next_regime(self):
        """
        executes the next regime
        """
        # are we finished?
        if self._current_regime_index == len(self._regimes)-1:
            self.finishedRegimeBatch.emit()
            return

        self._apply_regime_by_idx(self._current_regime_index + 1)
        self.start_simulation()

    def regime_batch_finished(self):
        self.runningBatch = False
        self.actExecuteRegimes.setDisabled(False)
        # self._current_regime_index = 0
        self.statusLabel.setText("All regimes have been simulated!")
        self.actSave.setDisabled(True)

    def simulation_finished(self, data):
        """
        main hook to be called by the simulation interface if integration is finished
        integration finished, enable play button and update plots

        :param data: dict with simulation data
        """
        self._logger.info("simulation finished")
        self.statusLabel.setText("simulation finished.")

        self.actSimulate.setDisabled(False)
        self.shortRunSimulation.setEnabled(True)
        self.shortRunRegimeBatch.setEnabled(True)
        self.actPlayPause.setDisabled(False)
        self.shortPlayPause.setEnabled(True)
        self.shortSaveResult.setEnabled(True)
        self.actStop.setDisabled(False)
        self.actSave.setDisabled(False)
        self.speedDial.setDisabled(False)
        self.timeSlider.setDisabled(False)

        self.sim.simulationProgressChanged.disconnect(self.guiProgress.setValue)
        self.statusBar().removeWidget(self.guiProgress)

        self.timeSlider.triggerAction(QAbstractSlider.SliderToMinimum)

        self.currentDataset = data
        self._read_results()
        self._update_data_list()
        self._update_plots()

        self.stop_animation()
        # self.playAnimation()

        if self.runningBatch:
            regime_name = self._regimes[self._current_regime_index]["Name"]
            self._save_data(regime_name)
            self.regimeFinished.emit()
        else:
            self.actExecuteRegimes.setDisabled(False)

    def simulation_failed(self, data):
        """
        integration failed, enable play button and update plots

        :param data:
        """
        self.statusLabel.setText("simulation failed!")
        self.simulation_finished(data)

    def _read_results(self):
        self.currentStepSize = 1.0/self.currentDataset["results"]["Simulation"]['measure rate']
        self.currentEndTime = self.currentDataset["results"]["Simulation"]["end time"]
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
            - time cursor in diagrams
        """
        if not self.validData:
            return

        self.timeLabel.setText("current time: %4f" % self.playbackTime)

        # update time cursor in plots
        self._update_time_cursor()

        # update state of rendering
        if self.visualizer:
            state = self.interpolate(self.currentDataset["results"]["Solver"])
            self.visualizer.update_scene(state)
            if isinstance(self.visualizer, MplVisualizer):
                pass
            elif isinstance(self.visualizer, VtkVisualizer):
                self.vtkWidget.GetRenderWindow().Render()

    def interpolate(self, data):
        """
        find corresponding item in data-set that fits the current playback time

        :param data: data-set in which the correct datum has to be found
        :return: datum fitting the current playback time
        """
        idx = next((index for index, val in enumerate(self.currentDataset["results"]["time"])
                    if val >= self.playbackTime), None)

        if idx is None:
            self._logger.info("interpolate(): Error no entry found for t={0}".format(self.playbackTime))
            return None
        else:
            if len(data.shape) == 1:
                return data[idx]
            elif len(data.shape) == 2:
                return data[idx, :]
            else:
                self._logger.info("interpolate(): Error Dimension {0} not understood.".format(data.shape))
                return None

    def _update_data_list(self):
        self.dataList.clear()
        for module, results in self.currentDataset["results"].items():
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

        :param item: ListItem
        """

        title = str(item.text())
        data = self._get_data_by_name(title)
        t = self.currentDataset["results"]["time"]

        dock = pg.dockarea.Dock(title)
        self.area.addDock(dock, "above", self.plotDocks[-1])

        widget = pg.PlotWidget(title=title)
        widget.plot(x=t, y=data)

        time_line = pg.InfiniteLine(self.playbackTime, angle=90, movable=False, pen=pg.mkPen("#FF0000", width=2.0))
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
            data = self.currentDataset["results"][tmp[0]]
            # if the data-set contains 1d array -> convert to float
            data = [float(x) for x in data]
        elif len(tmp) == 2:
            if len(self.currentDataset["results"][tmp[0]].shape) == 2:
                data = self.currentDataset["results"][tmp[0]][:, tmp[1]]
            if len(self.currentDataset["results"][tmp[0]].shape) == 3:  # data-set has the structure [ [[1]], [[2]] ]
                data = self.currentDataset['results'][tmp[0]][..., tmp[1], 0]

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
                if not self.dataList.findItems(dock.name(), Qt.MatchExactly):
                    # no data for this plot -> reset it
                    widget.getPlotItem().clear()
                    # TODO remove tab from dock and del instance
                else:
                    widget.getPlotItem().clear()
                    x_data = self.currentDataset["results"]["time"]
                    y_data = self._get_data_by_name(dock.name())
                    widget.getPlotItem().plot(x=x_data, y=y_data)

    def target_view_changed(self, index):
        self.targetView.resizeColumnToContents(0)

    def postprocessing_clicked(self):
        """
        starts the post- and metaprocessing application
        """
        self._logger.info("launching postprocessor")
        self.statusBar().showMessage("launching postprocessor", 1000)
        if self.postprocessor is None:
            self.postprocessor = PostProcessor()

        self.postprocessor.show()

    def reset_camera_clicked(self):
        """
        reset camera in vtk window
        """
        self.visualizer.reset_camera()
        self.vtkWidget.GetRenderWindow().Render()
