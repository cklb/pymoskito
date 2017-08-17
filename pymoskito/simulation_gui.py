# -*- coding: utf-8 -*-

# system
import logging
import time
import os
from operator import itemgetter
import yaml
import pickle
import pkg_resources
import webbrowser

import numpy as np

# Qt
from PyQt5.QtCore import (pyqtSignal, pyqtSlot, Qt, QTimer, QSize, QSettings,
                          QCoreApplication, QModelIndex)
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import (QWidget, QAction, QSlider, QMainWindow,
                             QTreeView, QListWidget, QListWidgetItem,
                             QAbstractItemView,
                             QToolBar, QStatusBar, QProgressBar, QLabel,
                             QPlainTextEdit, QLineEdit, QFileDialog, QInputDialog,
                             QAbstractSlider, QFrame, QVBoxLayout, QMenu,
                             QMessageBox, QDialogButtonBox)

# pyqtgraph
import pyqtgraph as pg
from pyqtgraph.dockarea import DockArea

# vtk
vtk_error_msg = ""
try:
    import vtk

    from vtk import vtkRenderer
    from vtk import qt
    # import patched class that fixes scroll problem
    from .visualization import QVTKRenderWindowInteractor
    vtk_available = True
except ImportError as e:
    vtk_available = False
    vtk_error_msg = e
    vtkRenderer = None
    QVTKRenderWindowInteractor = None

# pymoskito
from .visualization import MplVisualizer, VtkVisualizer
from .registry import get_registered_visualizers
from .simulation_interface import SimulatorInteractor, SimulatorView
from .processing_gui import PostProcessor
from .tools import get_resource, PlainTextLogger


__all__ = ["SimulationGui"]


class SimulationGui(QMainWindow):
    """
    class for the graphical user interface
    """
    # TODO enable closing plot docks by right-clicking their name

    runSimulation = pyqtSignal()
    stopSimulation = pyqtSignal()
    playbackTimeChanged = pyqtSignal()
    regimeFinished = pyqtSignal()
    finishedRegimeBatch = pyqtSignal(bool)

    def __init__(self):
        # constructor of the base class
        QMainWindow.__init__(self)

        QCoreApplication.setOrganizationName("RST")
        QCoreApplication.setOrganizationDomain("https://tu-dresden.de/rst")
        QCoreApplication.setApplicationVersion(
            pkg_resources.require("PyMoskito")[0].version)
        QCoreApplication.setApplicationName(globals()["__package__"])

        # load settings
        self._settings = QSettings()
        self._read_settings()

        # initialize logger
        self._logger = logging.getLogger(self.__class__.__name__)

        # Create Simulation Backend
        self.guiProgress = None
        self.cmdProgress = None
        self.sim = SimulatorInteractor(self)
        self.runSimulation.connect(self.sim.run_simulation)
        self.stopSimulation.connect(self.sim.stop_simulation)
        self.sim.simulation_finalized.connect(self.new_simulation_data)
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
        icon_size = QSize(25, 25)
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
        self.plotDockPlaceholder = pg.dockarea.Dock("Placeholder")

        # arrange docks
        self.area.addDock(self.animationDock, "right")
        self.area.addDock(self.regimeDock, "left", self.animationDock)
        self.area.addDock(self.propertyDock, "bottom", self.regimeDock)
        self.area.addDock(self.dataDock, "bottom", self.propertyDock)
        self.area.addDock(self.plotDockPlaceholder, "bottom", self.animationDock)
        self.area.addDock(self.logDock, "bottom", self.dataDock)
        self.non_plotting_docks = list(self.area.findAll()[1].keys())

        # add widgets to the docks
        self.propertyDock.addWidget(self.targetView)

        if not vtk_available:
            self._logger.error("loading vtk failed with:{}".format(vtk_error_msg))

        # check if there is a registered visualizer
        available_vis = get_registered_visualizers()
        self._logger.info("found visualizers: {}".format(
            [name for cls, name in available_vis]))
        if available_vis:
            # instantiate the first visualizer
            self._logger.info("loading visualizer '{}'".format(available_vis[0][1]))
            self.animationLayout = QVBoxLayout()

            if issubclass(available_vis[0][0], MplVisualizer):
                self.animationWidget = QWidget()
                self.visualizer = available_vis[0][0](self.animationWidget,
                                                      self.animationLayout)
                self.animationDock.addWidget(self.animationWidget)
            elif issubclass(available_vis[0][0], VtkVisualizer):
                if vtk_available:
                    # vtk window
                    self.animationFrame = QFrame()
                    self.vtkWidget = QVTKRenderWindowInteractor(
                        self.animationFrame)
                    self.animationLayout.addWidget(self.vtkWidget)
                    self.animationFrame.setLayout(self.animationLayout)
                    self.animationDock.addWidget(self.animationFrame)
                    self.vtk_renderer = vtkRenderer()
                    self.vtkWidget.GetRenderWindow().AddRenderer(
                        self.vtk_renderer)
                    self.visualizer = available_vis[0][0](self.vtk_renderer)
                    self.vtkWidget.Initialize()
                else:
                    self._logger.warning("visualizer depends on vtk which is "
                                         "not available on this system!")
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

        self.actDeleteRegimes = QAction(self.regime_list)
        self.actDeleteRegimes.setText("&Delete Selected Regimes")
        # TODO shortcut works always, not only with focus on the regime list
        # self.actDeleteRegimes.setShortcutContext(Qt.WindowShortcut)
        self.actDeleteRegimes.setShortcut(QKeySequence(Qt.Key_Delete))
        self.actDeleteRegimes.triggered.connect(self.remove_regime_items)

        self.actSave = QAction(self)
        self.actSave.setText('Save Results As')
        self.actSave.setIcon(QIcon(get_resource("save.png")))
        self.actSave.setDisabled(True)
        self.actSave.setShortcut(QKeySequence.Save)
        self.actSave.triggered.connect(self.export_simulation_data)

        self.actLoadRegimes = QAction(self)
        self.actLoadRegimes.setText("Load Regimes from File")
        self.actLoadRegimes.setIcon(QIcon(get_resource("load.png")))
        self.actLoadRegimes.setDisabled(False)
        self.actLoadRegimes.setShortcut(QKeySequence.Open)
        self.actLoadRegimes.triggered.connect(self.load_regime_dialog)

        self.actExitOnBatchCompletion = QAction(self)
        self.actExitOnBatchCompletion.setText("&Exit On Batch Completion")
        self.actExitOnBatchCompletion.setCheckable(True)
        self.actExitOnBatchCompletion.setChecked(
            self._settings.value("control/exit_on_batch_completion") == "True"
        )
        self.actExitOnBatchCompletion.changed.connect(
            self.update_exit_on_batch_completion_setting)

        # regime management
        self.runningBatch = False
        self._current_regime_index = None
        self._current_regime_name = None
        self._regimes = []

        self.regimeFinished.connect(self.run_next_regime)
        self.finishedRegimeBatch.connect(self.regime_batch_finished)

        # data window
        self.dataList = QListWidget(self)
        self.dataDock.addWidget(self.dataList)
        self.dataList.itemDoubleClicked.connect(self.create_plot)

        # actions for simulation control
        self.actSimulateCurrent = QAction(self)
        self.actSimulateCurrent.setText("&Simulate Current Regime")
        self.actSimulateCurrent.setIcon(QIcon(get_resource("simulate.png")))
        self.actSimulateCurrent.setShortcut(QKeySequence("F5"))
        self.actSimulateCurrent.triggered.connect(self.start_simulation)

        self.actSimulateAll = QAction(self)
        self.actSimulateAll.setText("Simulate &All Regimes")
        self.actSimulateAll.setIcon(QIcon(get_resource("execute_regimes.png")))
        self.actSimulateAll.setShortcut(QKeySequence("F6"))
        self.actSimulateAll.setDisabled(True)
        self.actSimulateAll.triggered.connect(self.start_regime_execution)

        # actions for animation control
        self.actAutoPlay = QAction(self)
        self.actAutoPlay.setText("&Autoplay Simulation")
        self.actAutoPlay.setCheckable(True)
        self.actAutoPlay.setChecked(
            self._settings.value("control/autoplay_animation") == "True"
        )
        self.actAutoPlay.changed.connect(self.update_autoplay_setting)

        self.actPlayPause = QAction(self)
        self.actPlayPause.setText("Play Animation")
        self.actPlayPause.setIcon(QIcon(get_resource("play.png")))
        self.actPlayPause.setDisabled(True)
        self.actPlayPause.setShortcut(QKeySequence(Qt.Key_Space))
        self.actPlayPause.triggered.connect(self.play_animation)

        self.actStop = QAction(self)
        self.actStop.setText("Stop")
        self.actStop.setIcon(QIcon(get_resource("stop.png")))
        self.actStop.setDisabled(True)
        self.actStop.triggered.connect(self.stop_animation)

        self.actSlow = QAction(self)
        self.actSlow.setText("Slowest")
        self.actSlow.setIcon(QIcon(get_resource("slow.png")))
        self.actSlow.setDisabled(False)
        self.actSlow.triggered.connect(self.set_slowest_playback_speed)

        self.actFast = QAction(self)
        self.actFast.setText("Fastest")
        self.actFast.setIcon(QIcon(get_resource("fast.png")))
        self.actFast.setDisabled(False)
        self.actFast.triggered.connect(self.set_fastest_playback_speed)

        self.speedControl = QSlider(Qt.Horizontal, self)
        self.speedControl.setMaximumSize(200, 25)
        self.speedControl.setTickPosition(QSlider.TicksBothSides)
        self.speedControl.setDisabled(False)
        self.speedControl.setMinimum(0)
        self.speedControl.setMaximum(12)
        self.speedControl.setValue(6)
        self.speedControl.setTickInterval(6)
        self.speedControl.setSingleStep(2)
        self.speedControl.setPageStep(3)
        self.speedControl.valueChanged.connect(self.update_playback_speed)

        self.timeSlider = QSlider(Qt.Horizontal, self)
        self.timeSlider.setMinimum(0)
        self.timeSliderRange = 1000
        self.timeSlider.setMaximum(self.timeSliderRange)
        self.timeSlider.setTickInterval(1)
        self.timeSlider.setTracking(True)
        self.timeSlider.setDisabled(True)
        self.timeSlider.valueChanged.connect(self.update_playback_time)

        self.playbackTime = .0
        self.playbackGain = 1
        self.currentStepSize = .0
        self.currentEndTime = .0
        self.playbackTimer = QTimer()
        self.playbackTimer.timeout.connect(self.increment_playback_time)
        self.playbackTimeChanged.connect(self.update_gui)
        self.playbackTimeout = 33  # in [ms] -> 30 fps

        self.actResetCamera = QAction(self)
        self.actResetCamera.setText("Reset Camera")
        self.actResetCamera.setIcon(QIcon(get_resource("reset_camera.png")))
        self.actResetCamera.setDisabled(True)
        if available_vis:
            self.actResetCamera.setEnabled(self.visualizer.can_reset_view)
        self.actResetCamera.triggered.connect(self.reset_camera_clicked)

        # postprocessing
        self.actPostprocessing = QAction(self)
        self.actPostprocessing.setText("Launch Postprocessor")
        self.actPostprocessing.setIcon(QIcon(get_resource("processing.png")))
        self.actPostprocessing.setDisabled(False)
        self.actPostprocessing.triggered.connect(self.postprocessing_clicked)
        self.actPostprocessing.setShortcut(QKeySequence("F7"))

        self.postprocessor = None

        # toolbar
        self.toolbarSim = QToolBar("Simulation")
        self.toolbarSim.setContextMenuPolicy(Qt.PreventContextMenu)
        self.toolbarSim.setMovable(False)
        self.toolbarSim.setIconSize(icon_size)
        self.addToolBar(self.toolbarSim)
        self.toolbarSim.addAction(self.actLoadRegimes)
        self.toolbarSim.addAction(self.actSave)
        self.toolbarSim.addSeparator()
        self.toolbarSim.addAction(self.actSimulateCurrent)
        self.toolbarSim.addAction(self.actSimulateAll)
        self.toolbarSim.addSeparator()
        self.toolbarSim.addAction(self.actPlayPause)
        self.toolbarSim.addAction(self.actStop)
        self.toolbarSim.addWidget(self.timeSlider)
        self.toolbarSim.addSeparator()
        self.toolbarSim.addAction(self.actSlow)
        self.toolbarSim.addWidget(self.speedControl)
        self.toolbarSim.addAction(self.actFast)
        self.toolbarSim.addSeparator()
        self.toolbarSim.addAction(self.actPostprocessing)
        self.toolbarSim.addAction(self.actResetCamera)
        self.postprocessor = None

        # log dock
        self.logBox = QPlainTextEdit(self)
        self.logBox.setReadOnly(True)
        self.logDock.addWidget(self.logBox)

        # init logger for logging box
        self.textLogger = PlainTextLogger(logging.INFO)
        self.textLogger.set_target_cb(self.logBox.appendPlainText)
        logging.getLogger().addHandler(self.textLogger)

        # menu bar
        fileMenu = self.menuBar().addMenu("&File")
        fileMenu.addAction(self.actLoadRegimes)
        fileMenu.addAction(self.actSave)
        fileMenu.addAction("&Quit", self.close)

        editMenu = self.menuBar().addMenu("&Edit")
        editMenu.addAction(self.actDeleteRegimes)

        simMenu = self.menuBar().addMenu("&Simulation")
        simMenu.addAction(self.actSimulateCurrent)
        simMenu.addAction(self.actSimulateAll)
        simMenu.addAction(self.actExitOnBatchCompletion)
        simMenu.addAction(self.actPostprocessing)

        animMenu = self.menuBar().addMenu("&Animation")
        animMenu.addAction(self.actPlayPause)
        animMenu.addAction("&Increase Playback Speed",
                           self.increment_playback_speed,
                           QKeySequence(Qt.CTRL + Qt.Key_Plus))
        animMenu.addAction("&Decrease Playback Speed",
                           self.decrement_playback_speed,
                           QKeySequence(Qt.CTRL + Qt.Key_Minus))
        animMenu.addAction("&Reset Playback Speed",
                           self.reset_playback_speed,
                           QKeySequence(Qt.CTRL + Qt.Key_0))
        animMenu.addAction(self.actAutoPlay)
        animMenu.addAction(self.actResetCamera)

        helpMenu = self.menuBar().addMenu("&Help")
        helpMenu.addAction("&Online Documentation", self.show_online_docs)
        helpMenu.addAction("&About", self.show_info)

        # status bar
        self.status = QStatusBar(self)
        self.setStatusBar(self.status)
        self.statusLabel = QLabel("Ready.")
        self.statusBar().addPermanentWidget(self.statusLabel)
        self.timeLabel = QLabel("current time: 0.0")
        self.statusBar().addPermanentWidget(self.timeLabel)

        self._logger.info("Simulation GUI is up and running.")

    def _read_settings(self):

        # add default settings if none are present
        if not self._settings.contains("path/simulation_results"):
            self._settings.setValue("path/simulation_results",
                                    os.path.join(os.path.curdir,
                                                 "results",
                                                 "simulation"))
        if not self._settings.contains("path/postprocessing_results"):
            self._settings.setValue("path/postprocessing_results",
                                    os.path.join(os.path.curdir,
                                                 "results",
                                                 "postprocessing"))
        if not self._settings.contains("path/metaprocessing_results"):
            self._settings.setValue("path/metaprocessing_results",
                                    os.path.join(os.path.curdir,
                                                 "results",
                                                 "metaprocessing"))

        if not self._settings.contains("control/autoplay_animation"):
            self._settings.setValue("control/autoplay_animation", "False")

        if not self._settings.contains("control/exit_on_batch_completion"):
            self._settings.setValue("control/exit_on_batch_completion", "False")

    def _write_settings(self):
        """ Store the application state. """
        pass

    @pyqtSlot()
    def update_autoplay_setting(self):
        self._settings.setValue("control/autoplay_animation",
                                str(self.actAutoPlay.isChecked()))

    @pyqtSlot()
    def update_exit_on_batch_completion_setting(self, state=None):
        if state is None:
            state = self.actExitOnBatchCompletion.isChecked()
        self._settings.setValue("control/exit_on_batch_completion", str(state))

    def set_visualizer(self, vis):
        self.visualizer = vis
        self.vtkWidget.Initialize()

    @pyqtSlot()
    def play_animation(self):
        """
        play the animation
        """
        self._logger.debug("Starting Playback")

        # if we are at the end, start from the beginning
        if self.playbackTime == self.currentEndTime:
            self.timeSlider.setValue(0)

        self.actPlayPause.setText("Pause Animation")
        self.actPlayPause.setIcon(QIcon(get_resource("pause.png")))
        self.actPlayPause.triggered.disconnect(self.play_animation)
        self.actPlayPause.triggered.connect(self.pause_animation)
        self.playbackTimer.start(self.playbackTimeout)

    @pyqtSlot()
    def pause_animation(self):
        """
        pause the animation
        """
        self._logger.debug("Pausing Playback")
        self.playbackTimer.stop()
        self.actPlayPause.setText("Play Animation")
        self.actPlayPause.setIcon(QIcon(get_resource("play.png")))
        self.actPlayPause.triggered.disconnect(self.pause_animation)
        self.actPlayPause.triggered.connect(self.play_animation)

    def stop_animation(self):
        """
        Stop the animation if it is running and reset the playback time.
        """
        self._logger.debug("Stopping Playback")
        if self.actPlayPause.text() == "Pause Animation":
            # animation is playing -> stop it
            self.playbackTimer.stop()
            self.actPlayPause.setText("Play Animation")
            self.actPlayPause.setIcon(QIcon(get_resource("play.png")))
            self.actPlayPause.triggered.disconnect(self.pause_animation)
            self.actPlayPause.triggered.connect(self.play_animation)

        self.timeSlider.setValue(0)

    @pyqtSlot()
    def start_simulation(self):
        """
        start the simulation and disable start button
        """
        if self._current_regime_index is None:
            regime_name = ""
        else:
            regime_name = str(self.regime_list.item(
                self._current_regime_index).text())

        self.statusLabel.setText("simulating {}".format(regime_name))
        self._logger.info("Simulating: {}".format(regime_name))

        self.actSimulateCurrent.setIcon(QIcon(
            get_resource("stop_simulation.png")))
        self.actSimulateCurrent.setText("Abort &Simulation")
        self.actSimulateCurrent.triggered.disconnect(self.start_simulation)
        self.actSimulateCurrent.triggered.connect(self.stop_simulation)

        if not self.runningBatch:
            self.actSimulateAll.setDisabled(True)

        self.guiProgress = QProgressBar(self)
        self.sim.simulationProgressChanged.connect(self.guiProgress.setValue)
        self.statusBar().addWidget(self.guiProgress)
        self.runSimulation.emit()

    @pyqtSlot()
    def stop_simulation(self):
        self.stopSimulation.emit()

    def export_simulation_data(self, ok):
        """
        Query the user for a custom name and export the current simulation
        results.

        :param ok: unused parameter from QAction.triggered() Signal
        """
        self._save_data()

    def _save_data(self, file_path=None):
        """
        Save the current simulation results.

        If *fie_name* is given, the result will be saved to the specified
        location, making automated exporting easier.

        Args:
            file_path(str): Absolute path of the target file. If `None` the
                use will be asked for a storage location.
        """
        regime_name = self._regimes[self._current_regime_index]["Name"]

        if file_path is None:
            # get default path
            path = self._settings.value("path/simulation_results")

            # create canonic file name
            suggestion = self._simfile_name(regime_name)
        else:
            path = os.path.dirname(file_path)
            suggestion = os.path.basename(file_path)

        # check if path exists otherwise create it
        if not os.path.isdir(path):
            box = QMessageBox()
            box.setText("Export Folder does not exist yet.")
            box.setInformativeText("Do you want to create it? \n"
                                   "{}".format(os.path.abspath(path)))
            box.setStandardButtons(QMessageBox.Ok | QMessageBox.No)
            box.setDefaultButton(QMessageBox.Ok)
            ret = box.exec_()
            if ret == QMessageBox.Ok:
                os.makedirs(path)
            else:
                path = os.path.abspath(os.path.curdir)
                file_path = None

        # If no path was given, present the default and let the user choose
        if file_path is None:
            dialog = QFileDialog(self)
            dialog.setAcceptMode(QFileDialog.AcceptSave)
            dialog.setFileMode(QFileDialog.AnyFile)
            dialog.setDirectory(path)
            dialog.setNameFilter("PyMoskito Results (*.pmr)")
            dialog.selectFile(suggestion)

            if dialog.exec_():
                file_path = dialog.selectedFiles()[0]
            else:
                self._logger.warning("Export Aborted")
                return -1

        # ask whether this should act as new default
        path = os.path.abspath(os.path.dirname(file_path))
        if path != self._settings.value("path/simulation_results"):
            box = QMessageBox()
            box.setText("Use this path as new default?")
            box.setInformativeText("{}".format(path))
            box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            box.setDefaultButton(QMessageBox.Yes)
            ret = box.exec_()
            if ret == QMessageBox.Yes:
                self._settings.setValue("path/simulation_results", path)

        self.currentDataset.update({"regime name": regime_name})
        with open(file_path, "wb") as f:
            pickle.dump(self.currentDataset, f, protocol=4)

        self.statusLabel.setText("results saved to {}".format(file_path))
        self._logger.info("results saved to {}".format(file_path))

    def _simfile_name(self, regime_name):
        """ Create a canonical name for a simulation result file
        """
        suggestion = (time.strftime("%Y%m%d-%H%M%S")
                      + "_" + regime_name + ".pmr")
        return suggestion

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
            self.actSimulateAll.setDisabled(False)

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

    @pyqtSlot(QListWidgetItem)
    def regime_dclicked(self, item):
        """
        Apply the selected regime to the current target.
        """
        self.apply_regime_by_name(str(item.text()))

    def apply_regime_by_name(self, regime_name):
        """
        Apply the regime given by `regime_name` und update the regime index.

        Returns:
            bool: `True` if successful, `False` if errors occurred.
        """
        # get regime idx
        try:
            idx = list(map(itemgetter("Name"), self._regimes)).index(regime_name)
        except ValueError as e:
            self._logger.error("apply_regime_by_name(): Error no regime called "
                               "'{0}'".format(regime_name))
            return False

        # apply
        return self._apply_regime_by_idx(idx)

    def _apply_regime_by_idx(self, index=0):
        """
        Apply the given regime.

        Args:
            index(int): Index of the regime in the `RegimeList` .

        Returns:
            bool: `True` if successful, `False` if errors occurred.
        """
        if index >= len(self._regimes):
            self._logger.error("applyRegime: index error! ({})".format(index))
            return False

        reg_name = self._regimes[index]["Name"]
        self.statusBar().showMessage("regime {} applied.".format(reg_name),
                                     1000)
        self._logger.info("applying regime '{}'".format(reg_name))

        self._current_regime_index = index
        self._current_regime_name = reg_name

        return self.sim.set_regime(self._regimes[index])

    @pyqtSlot()
    def start_regime_execution(self):
        """
        Simulate all regimes in the regime list.
        """
        self.actSimulateAll.setText("Stop Simulating &All Regimes")
        self.actSimulateAll.setIcon(QIcon(get_resource("stop_batch.png")))
        self.actSimulateAll.triggered.disconnect(self.start_regime_execution)
        self.actSimulateAll.triggered.connect(self.stop_regime_excecution)

        self.runningBatch = True
        self._current_regime_index = -1
        self.regimeFinished.emit()

    def run_next_regime(self):
        """
        Execute the next regime in the regime batch.
        """
        # are we finished?
        if self._current_regime_index == len(self._regimes) - 1:
            self.finishedRegimeBatch.emit(True)
            return

        suc = self._apply_regime_by_idx(self._current_regime_index + 1)
        if not suc:
            self.finishedRegimeBatch.emit(False)
            return

        self.start_simulation()

    @pyqtSlot()
    def stop_regime_excecution(self):
        """ Stop the batch process.
        """
        self.stopSimulation.emit()
        self.finishedRegimeBatch.emit(False)

    def regime_batch_finished(self, status):
        self.runningBatch = False
        self.actSimulateAll.setDisabled(False)
        self.actSave.setDisabled(True)

        self.actSimulateAll.setText("Simulate &All Regimes")
        self.actSimulateAll.setIcon(QIcon(get_resource("execute_regimes.png")))
        self.actSimulateAll.triggered.disconnect(self.stop_regime_excecution)
        self.actSimulateAll.triggered.connect(self.start_regime_execution)

        if status:
            self.statusLabel.setText("All regimes have been simulated")
            self._logger.info("All Regimes have been simulated")
        else:
            self._logger.error("Batch simulation has been aborted")

        if self._settings.value("control/exit_on_batch_completion") == "True":
            self._logger.info("Shutting down SimulationGUI")
            self.close()

    @pyqtSlot(str, dict, name="new_simulation_data")
    def new_simulation_data(self, status, data):
        """
        Slot to be called when the simulation interface has completed the
        current jpb and new data is available.

        Args:
            status (str): Status of the simulation, either
                - `finished` : Simulation has been finished successfully or
                - `failed` : Simulation has failed.
            data (dict): Dictionary, holding the simulation data.
        """
        self._logger.info("Simulation {}".format(status))
        self.statusLabel.setText("Simulation {}".format(status))

        self.actSimulateCurrent.setText("&Simulate Current Regime")
        self.actSimulateCurrent.setIcon(QIcon(get_resource("simulate.png")))
        self.actSimulateCurrent.triggered.disconnect(self.stop_simulation)
        self.actSimulateCurrent.triggered.connect(self.start_simulation)

        self.actPlayPause.setDisabled(False)
        self.actStop.setDisabled(False)
        self.actSave.setDisabled(False)
        self.speedControl.setDisabled(False)
        self.timeSlider.setDisabled(False)

        self.sim.simulationProgressChanged.disconnect(self.guiProgress.setValue)
        self.statusBar().removeWidget(self.guiProgress)

        self.stop_animation()

        self.currentDataset = data
        if data:
            self._read_results()
            self._update_data_list()
            self._update_plots()

        if self._settings.value("control/autoplay_animation") == "True":
            self.actPlayPause.trigger()

        if self.runningBatch:
            regime_name = self._regimes[self._current_regime_index]["Name"]
            file_name = self._simfile_name(regime_name)
            self._save_data(os.path.join(
                self._settings.value("path/simulation_results"),
                file_name))
            self.regimeFinished.emit()
        else:
            self.actSimulateAll.setDisabled(False)

    def _read_results(self):
        self.currentStepSize = 1.0/self.currentDataset["simulation"][
            "measure rate"]
        self.currentEndTime = self.currentDataset["simulation"]["end time"]
        self.validData = True

    def increment_playback_speed(self):
        self.speedControl.setValue(self.speedControl.value()
                                   + self.speedControl.singleStep())

    def decrement_playback_speed(self):
        self.speedControl.setValue(self.speedControl.value()
                                   - self.speedControl.singleStep())

    def reset_playback_speed(self):
        self.speedControl.setValue((self.speedControl.maximum()
                                    - self.speedControl.minimum())/2)

    def set_slowest_playback_speed(self):
        self.speedControl.setValue(self.speedControl.minimum())

    def set_fastest_playback_speed(self):
        self.speedControl.setValue(self.speedControl.maximum())

    def update_playback_speed(self, val):
        """
        adjust playback time to slider value

        :param val:
        """
        maximum = self.speedControl.maximum()
        self.playbackGain = 10**(3.0 * (val - maximum / 2) / maximum)

    @pyqtSlot()
    def increment_playback_time(self):
        """
        go one time step forward in playback
        """
        if self.playbackTime == self.currentEndTime:
            self.pause_animation()
            return

        increment = self.playbackGain * self.playbackTimeout / 1000
        self.playbackTime = min(self.currentEndTime,
                                self.playbackTime + increment)
        pos = int(self.playbackTime / self.currentEndTime
                  * self.timeSliderRange)
        self.timeSlider.blockSignals(True)
        self.timeSlider.setValue(pos)
        self.timeSlider.blockSignals(False)
        self.playbackTimeChanged.emit()

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
        self._update_time_cursors()

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
        for module_name, results in self.currentDataset["results"].items():
            if not isinstance(results, np.ndarray):
                continue
            if len(results.shape) == 1:
                self.dataList.insertItem(0, module_name)
            elif len(results.shape) == 2:
                for col in range(results.shape[1]):
                    self.dataList.insertItem(
                        0,
                        self._build_entry_name(module_name, (col, ))
                    )
            elif len(results.shape) == 3:
                for col in range(results.shape[1]):
                    for der in range(results.shape[2]):
                        self.dataList.insertItem(
                            0,
                            self._build_entry_name(module_name, (col, der))
                        )

    def _build_entry_name(self, module_name, idx):
        """
        Construct an identifier for a given entry of a module.
        Args:
            module_name (str): name of the module the entry belongs to.
            idx (tuple): Index of the entry.

        Returns:
            str: Identifier to use for display.
        """
        # save the user from defining 1d entries via tuples
        if len(idx) == 1:
            m_idx = idx[0]
        else:
            m_idx = idx

        mod_settings = self.currentDataset["modules"]
        info = mod_settings.get(module_name, {}).get("output_info", None)
        if info:
            if m_idx in info:
                return ".".join([module_name, info[m_idx]["Name"]])

        return ".".join([module_name] + [str(i) for i in idx])

    def _get_index_from_suffix(self, module_name, suffix):
        info = self.currentDataset["modules"].get(module_name, {}).get(
            "output_info", None)
        idx = next((i for i in info if info[i]["Name"] == suffix), None)
        return idx

    def _get_units(self, entry):
        """
        Return the unit that corresponds to a given entry.

        If no information is available, None is returned.

        Args:
            entry (str): Name of the entry. This can either be "Model.a.b" where
                a and b are numbers or if information is available "Model.Signal"
                where signal is the name of that part.

        Returns:

        """
        args = entry.split(".")
        module_name = args.pop(0)
        info = self.currentDataset["modules"].get(module_name, {}).get(
            "output_info", None)
        if info is None:
            return None

        if len(args) == 1:
            try:
                idx = int(args[0])
            except ValueError:
                idx = next((i for i in info if info[i]["Name"] == args[0]),
                           None)
        else:
            idx = (int(a) for a in args)

        return info[idx]["Unit"]

    def create_plot(self, item):
        """
        Creates a plot widget based on the given item.

        If a plot for this item is already open no new plot is created but the
        existing one is raised up again.

        Args:
            item(Qt.ListItem): Item to plot.
        """
        title = str(item.text())
        if title in self.non_plotting_docks:
            self._logger.error("Title '{}' not allowed for a plot window since"
                               "it would shadow on of the reserved "
                               "names".format(title))

        # check if plot has already been opened
        if title in self.area.findAll()[1]:
            self.area.docks[title].raiseDock()
            return

        # collect data
        data = self._get_data_by_name(title)
        t = self.currentDataset["results"]["time"]
        unit = self._get_units(title)
        if "." in title:
            name = title.split(".")[1]
        else:
            name = title

        # create plot widget
        widget = pg.PlotWidget(title=title)
        widget.showGrid(True, True)
        widget.plot(x=t, y=data)
        widget.getPlotItem().getAxis("bottom").setLabel(text="Time", units="s")
        widget.getPlotItem().getAxis("left").setLabel(text=name, units=unit)

        # add a time line
        time_line = pg.InfiniteLine(self.playbackTime,
                                    angle=90,
                                    movable=False,
                                    pen=pg.mkPen("#FF0000", width=2.0))
        widget.getPlotItem().addItem(time_line)

        # create dock container and add it to dock area
        dock = pg.dockarea.Dock(title, closable=True)
        dock.addWidget(widget)
        self.area.addDock(dock, "above", self.plotDockPlaceholder)

    def _get_data_by_name(self, name):
        tmp = name.split(".")
        module_name = tmp[0]
        if len(tmp) == 1:
            data = np.array(self.currentDataset["results"][module_name])
        elif len(tmp) == 2:
            try:
                idx = int(tmp[1])
            except ValueError:
                idx = self._get_index_from_suffix(module_name, tmp[1])
            finally:
                data = self.currentDataset["results"][module_name][..., idx]
        elif len(tmp) == 3:
            idx = int(tmp[1])
            der = int(tmp[2])
            data = self.currentDataset["results"][module_name][..., idx, der]
        else:
            raise ValueError("Format not supported")

        return data

    def _update_time_cursors(self):
        """
        Update the time lines of all plot windows
        """
        for title, dock in self.area.findAll()[1].items():
            if title in self.non_plotting_docks:
                continue
            for widget in dock.widgets:
                for item in widget.getPlotItem().items:
                    if isinstance(item, pg.InfiniteLine):
                        item.setValue(self.playbackTime)

    def _update_plots(self):
        """
        Update the data in all plot windows
        """
        for title, dock in self.area.findAll()[1].items():
            if title in self.non_plotting_docks:
                continue

            if not self.dataList.findItems(dock.name(), Qt.MatchExactly):
                # no data for this plot -> remove it
                dock.close()
                continue

            for widget in dock.widgets:
                for item in widget.getPlotItem().items:
                    if isinstance(item, pg.PlotDataItem):
                        x_data = self.currentDataset["results"]["time"]
                        y_data = self._get_data_by_name(dock.name())
                        item.setData(x=x_data, y=y_data)

    @pyqtSlot(QModelIndex)
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

    def show_info(self):
        icon_lic = open(get_resource("license.txt"), "r").read()
        text = "This application was build using PyMoskito ver. {} .<br />" \
               "PyMoskito is free software distributed under GPLv3. <br />" \
               "It is developed by members of the " \
               "<a href=\'https://tu-dresden.de/ing/elektrotechnik/rst'>" \
               "Institute of Control Theory</a>" \
               " at the <a href=\'https://tu-dresden.de'>" \
               "Dresden University of Technology</a>. <br />" \
               "".format(pkg_resources.require("PyMoskito")[0].version) \
               + "<br />" + icon_lic
        box = QMessageBox.about(self, "PyMoskito", text)

    def show_online_docs(self):
        webbrowser.open("https://pymoskito.readthedocs.org")

    def closeEvent(self, QCloseEvent):
        self._logger.info("Close Event received, shutting down.")
        logging.getLogger().removeHandler(self.textLogger)
        super().closeEvent(QCloseEvent)
