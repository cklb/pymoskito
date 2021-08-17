# -*- coding: utf-8 -*-

# system
import logging
import numpy as np
import os
import pickle
import time
import pkg_resources
import webbrowser
import yaml
from operator import itemgetter
from scipy.interpolate import interp1d

# Qt
from PyQt5.QtCore import (pyqtSignal, pyqtSlot, Qt, QTimer, QSize, QSettings,
                          QCoreApplication, QModelIndex)
from PyQt5.QtGui import QIcon, QKeySequence, QColor
from PyQt5.QtWidgets import (
    QApplication, QMainWindow,
    QWidget, QAction,
    QSlider, QLabel, QFrame,
    QPushButton, QComboBox,
    QListWidget, QListWidgetItem, QTreeView, QTreeWidget, QTreeWidgetItem,
    QAbstractItemView,
    QToolBar, QStatusBar, QProgressBar,
    QTextEdit, QFileDialog, QInputDialog,
    QVBoxLayout, QHBoxLayout, QMessageBox,
)

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
from .registry import get_registered_visualizers
from .simulation_interface import SimulatorInteractor, SimulatorView
from .visualization import MplVisualizer, VtkVisualizer, DummyVisualizer
from .processing_gui import PostProcessor
from .tools import (
    get_resource, PlainTextLogger, Exporter, create_button_from_action
)

__all__ = ["SimulationGui", "run"]


def run(regimes=None):
    """ Helper function to launch the PyMoskito GUI
    """
    app = QApplication([])
    prog = SimulationGui()
    if regimes is not None:
        prog.load_regimes_from_file(regimes)
    prog.show()
    app.exec_()


class SimulationGui(QMainWindow):
    """
    class for the graphical user interface
    """
    # TODO enable closing plot docks by right-clicking their name
    TABLEAU_COLORS = (
        ('blue', '#1f77b4'),
        ('orange', '#ff7f0e'),
        ('green', '#2ca02c'),
        ('red', '#d62728'),
        ('purple', '#9467bd'),
        ('brown', '#8c564b'),
        ('pink', '#e377c2'),
        ('gray', '#7f7f7f'),
        ('olive', '#bcbd22'),
        ('cyan', '#17becf'),
    )

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
        self._init_settings()

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
        self.interpolator = None

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
        self.lastSimDock = pg.dockarea.Dock("Previous Simulations")
        self.dataDock = pg.dockarea.Dock("Data & Plots")
        self.logDock = pg.dockarea.Dock("Log")

        # arrange docks
        self.area.addDock(self.animationDock, "right")
        self.area.addDock(self.lastSimDock, "left", self.animationDock)
        self.area.addDock(self.propertyDock, "bottom", self.lastSimDock)
        self.area.addDock(self.dataDock, "bottom", self.propertyDock)
        self.area.addDock(self.logDock, "bottom", self.dataDock)
        self.area.addDock(self.regimeDock, "left", self.lastSimDock)
        self.non_plotting_docks = list(self.area.findAll()[1].keys())

        self.standardDockState = self.area.saveState()

        # add widgets to the docks
        self.propertyDock.addWidget(self.targetView)

        # setup the visualizer
        self.visuComboBox = QComboBox()
        self.visualizer = None
        self._init_visualizer()

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

        self.regimeFinished.connect(self.run_next_regime)
        self.finishedRegimeBatch.connect(self.regime_batch_finished)

        # last sim window
        self.lastSimList = QListWidget(self)
        self.lastSimList.setFocusPolicy(Qt.NoFocus)
        self.lastSimDock.addWidget(self.lastSimList)
        self._lastSimulations = []
        self.lastSimList.itemDoubleClicked.connect(self.load_last_sim)

        # data window
        self.dataWidget = QWidget()
        self.dataLayout = QHBoxLayout()

        self.dataPointListWidget = QListWidget()
        self.dataPointListLayout = QVBoxLayout()
        self.dataPointListWidget.setLayout(self.dataPointListLayout)
        self.dataPointListWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.dataLayout.addWidget(self.dataPointListWidget)

        self.dataPointManipulationLayout = QVBoxLayout()
        self.dataPointManipulationLayout.addStretch()
        self.dataPointManipulationLayout.setSpacing(5)
        self.dataPointManipulationWidget = QWidget()
        self.dataPointManipulationWidget.setLayout(self.dataPointManipulationLayout)
        self.dataLayout.addWidget(self.dataPointManipulationWidget)

        self.dataPointLabel = QLabel("Data", self)
        self.dataPointLabel.setAlignment(Qt.AlignCenter)
        self.dataPointManipulationLayout.addWidget(self.dataPointLabel)

        self.actAddDataPointToPlot = QAction(self)
        self.actAddDataPointToPlot.setText("&Add selected data to plot")
        self.actAddDataPointToPlot.setIcon(QIcon(get_resource("add.png")))
        self.actAddDataPointToPlot.setToolTip(
            "Add the selected data set from the left to the selected plot "
            "on the right.")
        self.actAddDataPointToPlot.triggered.connect(self.add_data_point_to_tree)
        self.dataPointManipulationLayout.addWidget(
            create_button_from_action(self.actAddDataPointToPlot))

        self.actExportDataPoint = QAction(self)
        self.actExportDataPoint.setText("&Export selected data")
        self.actExportDataPoint.setIcon(QIcon(get_resource("export.png")))
        self.actExportDataPoint.setToolTip(
            "Export the selected data set from the left to a csv or png file."
        )
        self.actExportDataPoint.triggered.connect(self.export_data_points_from_tree)
        self.dataPointManipulationLayout.addWidget(
            create_button_from_action(self.actExportDataPoint))

        self.actRemoveDataPointFromPlot = QAction(self)
        self.actRemoveDataPointFromPlot.setText("&Remove selected data from plot")
        self.actRemoveDataPointFromPlot.setIcon(QIcon(get_resource("delete.png")))
        self.actRemoveDataPointFromPlot.setToolTip(
            "Remove the selected data set from the plot on the right."
        )
        self.actRemoveDataPointFromPlot.triggered.connect(
            self.remove_data_point_from_tree)
        self.dataPointManipulationLayout.addWidget(
            create_button_from_action(self.actRemoveDataPointFromPlot))

        self.plotLabel = QLabel("Plots", self)
        self.plotLabel.setAlignment(Qt.AlignCenter)
        self.dataPointManipulationLayout.addWidget(self.plotLabel)

        self.actCreatePlot = QAction(self)
        self.actCreatePlot.setIcon(QIcon(get_resource("add.png")))
        self.actCreatePlot.setText("&Create a new plot")
        self.actCreatePlot.setToolTip("Create a new plot.")
        self.actCreatePlot.triggered.connect(self.add_plot_tree_item)
        self.dataPointManipulationLayout.addWidget(
            create_button_from_action(self.actCreatePlot))

        self.actShowPlot = QAction(self)
        self.actShowPlot.setText("&Show the selected plot")
        self.actShowPlot.setIcon(QIcon(get_resource("view.png")))
        self.actShowPlot.setToolTip(
            "Show the selected plot (double-click on name)."
        )
        self.actShowPlot.triggered.connect(self.show_selected_plot_tree_item)
        self.dataPointManipulationLayout.addWidget(
            create_button_from_action(self.actShowPlot))

        self.actDeletePlot = QAction(self)
        self.actDeletePlot.setText("&Delete selected plot")
        self.actDeletePlot.setIcon(QIcon(get_resource("delete.png")))
        self.actDeletePlot.setToolTip(
            "Delete the selected plot."
        )
        self.actDeletePlot.triggered.connect(self.remove_selected_plot_tree_items)
        self.dataPointManipulationLayout.addWidget(
            create_button_from_action(self.actDeletePlot))
        self.dataPointManipulationLayout.addStretch()

        self.dataPointTreeWidget = QTreeWidget()
        self.dataPointTreeWidget.setHeaderLabels(["PlotTitle", "DataPoint"])
        # self.dataPointTreeWidget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.dataPointTreeWidget.itemDoubleClicked.connect(self.plot_vector_double_clicked)
        self.dataPointTreeWidget.setExpandsOnDoubleClick(0)
        self.dataPointTreeLayout = QVBoxLayout()

        self.dataPointTreeWidget.setLayout(self.dataPointTreeLayout)
        self.dataLayout.addWidget(self.dataPointTreeWidget)

        self.dataWidget.setLayout(self.dataLayout)
        self.dataDock.addWidget(self.dataWidget)

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
        self.actPlayPause.triggered.connect(self.start_animation)

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

        self.playbackTime = 0
        self.playbackGain = 1
        self.currentStepSize = 0
        self.currentStartTime = 0
        self.currentEndTime = 0
        self.playbackTimer = QTimer()
        self.playbackTimer.timeout.connect(self.increment_playback_time)
        self.playbackTimeChanged.connect(self.update_gui)
        self.playbackTimeout = 33  # in [ms] -> 30 fps

        self.actResetCamera = QAction(self)
        self.actResetCamera.setText("Reset Camera")
        self.actResetCamera.setIcon(QIcon(get_resource("video_camera.png")))
        self.actResetCamera.setDisabled(True)
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
        self.toolbarSim.addAction(self.actResetCamera)
        self.toolbarSim.addWidget(self.visuComboBox)
        self.toolbarSim.addSeparator()
        self.toolbarSim.addAction(self.actPostprocessing)
        self.postprocessor = None

        # log dock
        self.logBox = QTextEdit(self)
        self.logBox.setReadOnly(True)
        self.logBox.setLineWrapMode(QTextEdit.NoWrap)
        self.logBox.ensureCursorVisible()
        self.logDock.addWidget(self.logBox)

        # init logger for logging box
        self.textLogger = PlainTextLogger(self._settings,
                                          logging.INFO)
        self.textLogger.set_target_cb(self.logBox)
        logging.getLogger().addHandler(self.textLogger)

        # menu bar
        fileMenu = self.menuBar().addMenu("&File")
        fileMenu.addAction(self.actLoadRegimes)
        fileMenu.addAction(self.actSave)
        fileMenu.addAction("&Quit", self.close, QKeySequence(Qt.CTRL + Qt.Key_W))

        editMenu = self.menuBar().addMenu("&Edit")
        editMenu.addAction(self.actDeleteRegimes)

        self.viewMenu = self.menuBar().addMenu('&View')
        self.actLoadStandardState = QAction('&Restore Default View')
        self.viewMenu.addAction(self.actLoadStandardState)
        self.actLoadStandardState.triggered.connect(self.loadStandardDockState)
        self.actShowCoords = QAction("&Show Coordinates", self)
        self.actShowCoords.setCheckable(True)
        self.actShowCoords.setChecked(
            self._settings.value("view/show_coordinates") == "True"
        )
        self.viewMenu.addAction(self.actShowCoords)
        self.actShowCoords.changed.connect(self.update_show_coords_setting)

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

        plotMenu = self.menuBar().addMenu("&Plotting")
        plotMenu.addAction(self.actAddDataPointToPlot)
        plotMenu.addAction(self.actExportDataPoint)
        plotMenu.addAction(self.actRemoveDataPointFromPlot)
        plotMenu.addAction(self.actCreatePlot)
        plotMenu.addAction(self.actShowPlot)
        plotMenu.addAction(self.actDeletePlot)

        helpMenu = self.menuBar().addMenu("&Help")
        helpMenu.addAction("&Online Documentation", self.show_online_docs)
        helpMenu.addAction("&About", self.show_info)

        # status bar
        self.status = QStatusBar(self)
        self.setStatusBar(self.status)
        self.statusLabel = QLabel("Idle")
        self.statusBar().addPermanentWidget(self.statusLabel)
        self.timeLabel = QLabel("t=0.0")
        self.statusBar().addPermanentWidget(self.timeLabel)
        self.coordLabel = QLabel("x=0.0 y=0.0")
        self.statusBar().addPermanentWidget(self.coordLabel)

        self._logger.info("Simulation GUI is up and running.")

    def _init_visualizer(self):
        """ Initialize the visualizer combobox """
        self.visuComboBox.currentTextChanged.connect(self._visualizer_changed)
        self.visuComboBox.addItem("None")

        if not vtk_available:
            self._logger.warning(
                "loading vtk failed with:{}".format(vtk_error_msg))

        # get all registered visualizers
        available_vis = get_registered_visualizers()

        # fill the combo box
        for cls, name in available_vis:
            self.visuComboBox.addItem(name)

        # instantiate the first visualizer or None
        if self.visuComboBox.count() > 0:
            self.visuComboBox.setCurrentIndex(1)
        else:
            self.visuComboBox.setCurrentIndex(0)

    @pyqtSlot(str)
    def _visualizer_changed(self, name):
        """ Slot to update the visualizer """
        self._logger.info(
            "selecting visualizer '{}'".format(name))
        available_vis = get_registered_visualizers()
        cls = next((_c for _c, _n in available_vis if _n == name),
                   DummyVisualizer)
        self._update_visualizer(cls)

    def _update_visualizer(self, visu_cls):
        """ Update the current visualizer """
        if self.animationDock.widgets:
            self.animationDock.layout.removeWidget(
                self.animationDock.widgets[0])
            self.animationDock.widgets[0].deleteLater()
            del self.animationDock.widgets[0]

        self.animationLayout = QVBoxLayout()
        if visu_cls is DummyVisualizer:
            self.visualizer = DummyVisualizer()
            # self.animationWidget = QWidget()
            # self.animationDock.addWidget(self.animationWidget, row=0)
        elif issubclass(visu_cls, MplVisualizer):
            self.animationWidget = QWidget()
            self.visualizer = visu_cls(self.animationWidget,
                                       self.animationLayout)
            self.animationDock.addWidget(self.animationWidget, row=0)
        elif issubclass(visu_cls, VtkVisualizer):
            if vtk_available:
                # vtk window
                self.animationFrame = QFrame()
                self.vtkWidget = QVTKRenderWindowInteractor(
                    self.animationFrame)
                self.animationLayout.addWidget(self.vtkWidget)
                self.animationFrame.setLayout(self.animationLayout)
                self.animationDock.addWidget(self.animationFrame, row=0)
                self.vtk_renderer = vtkRenderer()
                self.vtkWidget.GetRenderWindow().AddRenderer(
                    self.vtk_renderer)
                self.visualizer = visu_cls(self.vtk_renderer)
                self.vtkWidget.Initialize()
            else:
                self._logger.warning("visualizer depends on vtk which is "
                                     "not available on this system!")
        else:
            raise NotImplementedError("Unsupported visualizer type '{}'"
                                      "".format(visu_cls))
        if hasattr(self, "actResetCamera"):
            self.actResetCamera.setEnabled(self.visualizer.can_reset_view)

    def add_plot_tree_item(self, default=False):
        text = "plot_{:03d}".format(self.dataPointTreeWidget.topLevelItemCount())
        if not default:
            name, ok = QInputDialog.getText(self,
                                            "Select a plot title",
                                            "name of the new plot:",
                                            text=text)
            if not (ok and name):
                return
        else:
            name = text

        similar_items = self.dataPointTreeWidget.findItems(name,
                                                           Qt.MatchExactly)
        if similar_items:
            self._logger.error("A plot with name '{}' already exists"
                               "".format(name))
            return

        if name in self.non_plotting_docks:
            self._logger.error("Name '{}' not allowed for a plot window "
                               "since it is already taken by another dock."
                               "".format(name))
            return

        top_level_item = QTreeWidgetItem()
        top_level_item.setText(0, name)
        self.dataPointTreeWidget.addTopLevelItem(top_level_item)
        top_level_item.setExpanded(1)
        self.dataPointTreeWidget.setCurrentItem(top_level_item)
        self.plot_vector_double_clicked(top_level_item)

    def show_selected_plot_tree_item(self):
        items = self.dataPointTreeWidget.selectedItems()
        for item in items:
            self.show_plot_tree_item(item)

    def remove_selected_plot_tree_items(self):
        items = self.dataPointTreeWidget.selectedItems()
        if not items:
            self._logger.error("Can't remove plot: no plot selected.")
            return

        for item in items:
            self.remove_plot_tree_item(item)

    def remove_plot_tree_item(self, item):
        # get the  top item
        while item.parent():
            item = item.parent()

        text = "The marked plot '" + item.text(0) + "' will be deleted!"
        reply_button = QMessageBox.warning(self, "Plot delete", text,
                                          QMessageBox.Ok | QMessageBox.Cancel)
        if reply_button == QMessageBox.Ok:
            open_docks = [dock.title() for dock in self.find_all_plot_docks()]
            if item.text(0) in open_docks:
                self.area.docks[item.text(0)].close()

            self.dataPointTreeWidget.takeTopLevelItem(
                self.dataPointTreeWidget.indexOfTopLevelItem(item))

    def add_data_point_to_tree(self):
        if not self.dataPointListWidget.selectedIndexes():
            self._logger.error("Can't add data set: no data set selected.")
            return

        data_points = []
        for item in self.dataPointListWidget.selectedItems():
            data_points.append(item.text())

        top_level_items = self.dataPointTreeWidget.selectedItems()
        if not top_level_items:
            if self.dataPointTreeWidget.topLevelItemCount() < 2:
                if self.dataPointTreeWidget.topLevelItemCount() < 1:
                    self.add_plot_tree_item(default=True)
                top_level_item = self.dataPointTreeWidget.topLevelItem(0)
            else:
                self._logger.error("Can't add data set: no plot selected.")
                return
        else:
            top_level_item = top_level_items[0]

        while top_level_item.parent():
            top_level_item = top_level_item.parent()

        top_level_item_list = []
        for i in range(top_level_item.childCount()):
            top_level_item_list.append(top_level_item.child(i).text(1))

        dock = next((d for d in self.find_all_plot_docks()
                     if d.title() == top_level_item.text(0)), None)

        for data_point in data_points:
            if data_point not in top_level_item_list:
                child = QTreeWidgetItem()
                child.setText(1, data_point)

                color = self._get_color(top_level_item.childCount())
                child.setBackground(0, color)

                top_level_item.addChild(child)

                if dock:
                    widget = dock.widgets[0]
                    self.plot_data_vector_member(child, widget)
            else:
                self._logger.error("Can't add data set: "
                                   "Set '{}' is already present selected plot"
                                   "".format(data_point))

    def export_data_points_from_tree(self):
        data_points = {}
        for item in self.dataPointListWidget.selectedItems():
            data_points[item.text()] = self._get_data_by_name(item.text())

        if not data_points:
            self._logger.error("Data export failed: No data selected.")
            return

        self.export(data_points)

    def remove_data_point_from_tree(self):
        items = self.dataPointTreeWidget.selectedItems()
        if not items:
            self._logger.error("Can't remove data set: no set selected.")
            return

        top_item = items[0]
        while top_item.parent():
            top_item = top_item.parent()

        top_item.takeChild(top_item.indexOfChild(items[0]))

        for i in range(top_item.childCount()):
            color_item = self._get_color(i)
            top_item.child(i).setBackground(0, color_item)

        self._update_plot(top_item)

    def _get_color(self, idx):
        sat_idx = idx % len(self.TABLEAU_COLORS)
        color = QColor(self.TABLEAU_COLORS[sat_idx][1])
        return color

    def _get_pen(self, idx):
        pen = pg.mkPen(self._get_color(idx), width=2)
        return pen

    def plot_vector_double_clicked(self, item):
        # check if a top level item has been clicked
        if not item.parent():
            self.show_plot_tree_item(item)

    def show_plot_tree_item(self, item):
        title = item.text(0)
        # check if plot has already been opened
        open_docks = [dock.title() for dock in self.find_all_plot_docks()]
        if title in open_docks:
            # update and raise the dock
            self._update_plot(item)
            try:
                self.area.docks[title].raiseDock()
            except:
                pass
        else:
            # create a new dock
            self.plot_data_vector(item)

    def load_last_sim(self, item):
        sim_name = str(item.text())
        try:
            idx = self.lastSimList.row(item)
        except ValueError as e:
            self._logger.error("load_last_sim(): No results called "
                               "'{0}'".format(sim_name))
            return False

        if idx >= len(self._lastSimulations):
            self._logger.error("load_last_sim(): Invalid index '{}')".format(idx))
            return False

        self._logger.info("restoring simulation '{}'".format(sim_name))

        self.currentDataset = self._lastSimulations[idx]
        if self._lastSimulations[idx]:
            self._read_results()
            self._update_data_list()
            self._update_plots()
            lsettings = self.currentDataset["modules"]
            self.visualizer.update_config(lsettings)
            lsettings["clear previous"] = True
            self.sim.restore_regime(lsettings)
            self.update_gui()

        self.setQListItemBold(self.lastSimList, item)
        self.setQListItemBold(self.regime_list, item)
        self.statusBar().showMessage(
            "restored simulation '{}'.".format(sim_name),
            1000)

    def _add_setting(self, setting, value):
        """
        Add a setting, if settings is present, no changes are made.

        Args:
            setting(str): Setting to add.
            value: Value to be set.
        """
        if not self._settings.contains(setting):
            self._settings.setValue(setting, value)

    def _init_settings(self):
        """
        Provide initial settings for the config file.

        """
        # path management
        self._add_setting("path/simulation_results",
                          os.path.join(os.path.curdir,
                                       "results",
                                       "simulation"))
        self._add_setting("path/simulation_results",
                          os.path.join(os.path.curdir,
                                       "results",
                                       "simulation"))
        self._add_setting("path/postprocessing_results",
                          os.path.join(os.path.curdir,
                                       "results",
                                       "postprocessing"))
        self._add_setting("path/metaprocessing_results",
                          os.path.join(os.path.curdir,
                                       "results",
                                       "metaprocessing"))
        self._add_setting("path/previous_plot_export", os.path.curdir)
        self._add_setting("path/previous_plot_format", ".csv")

        # control flow management
        self._add_setting("control/autoplay_animation", "False")
        self._add_setting("control/exit_on_batch_completion", "False")

        # view management
        self._add_setting("view/show_coordinates", "True")

        # log management
        self._add_setting("log_colors/CRITICAL", "#DC143C")
        self._add_setting("log_colors/ERROR", "#B22222")
        self._add_setting("log_colors/WARNING", "#DAA520")
        self._add_setting("log_colors/INFO", "#101010")
        self._add_setting("log_colors/DEBUG", "#4682B4")
        self._add_setting("log_colors/NOTSET", "#000000")

        self._add_setting("view/show_time_on_export", "False")
        self._add_setting("view/export_width", "800")
        self._add_setting("view/export_height", "600")

    def _write_settings(self):
        """ Store the application state. """
        pass

    @pyqtSlot()
    def update_autoplay_setting(self):
        self._settings.setValue("control/autoplay_animation",
                                str(self.actAutoPlay.isChecked()))

    @pyqtSlot()
    def update_show_coords_setting(self):
        self._settings.setValue("view/show_coordinates",
                                str(self.actShowCoords.isChecked()))

    @pyqtSlot()
    def update_exit_on_batch_completion_setting(self, state=None):
        if state is None:
            state = self.actExitOnBatchCompletion.isChecked()
        self._settings.setValue("control/exit_on_batch_completion", str(state))

    def set_visualizer(self, vis):
        self.visualizer = vis
        self.vtkWidget.Initialize()

    @pyqtSlot()
    def start_animation(self):
        """
        start the animation
        """
        self._logger.info("Starting Playback")

        # if we are at the end, start from the beginning
        if self.playbackTime >= self.currentEndTime:
            self.playbackTime = self.currentStartTime
            self.playbackTimeChanged.emit()

        self.actPlayPause.setText("Pause Animation")
        self.actPlayPause.setIcon(QIcon(get_resource("pause.png")))
        self.actPlayPause.triggered.disconnect(self.start_animation)
        self.actPlayPause.triggered.connect(self.pause_animation)
        self.playbackTimer.start(self.playbackTimeout)

    @pyqtSlot()
    def pause_animation(self):
        """
        pause the animation
        """
        self._logger.info("Pausing Playback")
        self.playbackTimer.stop()
        self.actPlayPause.setText("Play Animation")
        self.actPlayPause.setIcon(QIcon(get_resource("play.png")))
        self.actPlayPause.triggered.disconnect(self.pause_animation)
        self.actPlayPause.triggered.connect(self.start_animation)

    def stop_animation(self):
        """
        Stop the animation if it is running and reset the playback time.
        """
        self._logger.info("Stopping Playback")
        if self.actPlayPause.text() == "Pause Animation":
            # animation is playing -> stop it
            self.playbackTimer.stop()
            self.actPlayPause.setText("Play Animation")
            self.actPlayPause.setIcon(QIcon(get_resource("play.png")))
            self.actPlayPause.triggered.disconnect(self.pause_animation)
            self.actPlayPause.triggered.connect(self.start_animation)

        self.playbackTime = self.currentStartTime
        self.playbackTimeChanged.emit()

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
            self._regimes += yaml.full_load(f)

        self._update_regime_list()

        if self._regimes:
            self.actSimulateAll.setDisabled(False)

        self._logger.info("loaded {} regimes".format(len(self._regimes)))
        self.statusBar().showMessage("loaded {} regimes.".format(len(self._regimes)), 1000)
        return

    def _update_regime_list(self):
        self.regime_list.clear()
        for reg in self._regimes:
            self._logger.info("adding '{}' to regime list".format(reg["Name"]))
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
        success = self._apply_regime_by_idx(self.regime_list.row(item))

        self.setQListItemBold(self.regime_list, item, success)
        self.setQListItemBold(self.lastSimList, item, success)
        self.dataPointListWidget.clear()

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
            self._logger.error("Invalid index: '{}'".format(index))
            return False

        reg_name = self._regimes[index]["Name"]
        self._logger.info("applying regime '{}'".format(reg_name))

        self._current_regime_index = index
        self._current_regime_name = reg_name

        ret = self.sim.set_regime(self._regimes[index])
        if ret:
            self.statusBar().showMessage("regime {} applied.".format(reg_name),
                                         1000)
        return ret

    @pyqtSlot()
    def start_regime_execution(self):
        """
        Simulate all regimes in the regime list.
        """
        self.actSimulateAll.setText("Stop Simulating &All Regimes")
        self.actSimulateAll.setIcon(QIcon(get_resource("stop_batch.png")))
        self.actSimulateAll.triggered.disconnect(self.start_regime_execution)
        self.actSimulateAll.triggered.connect(self.stop_regime_execution)

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
    def stop_regime_execution(self):
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
        self.actSimulateAll.triggered.disconnect(self.stop_regime_execution)
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
        current job and new data is available.

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

        if data:
            # import new data
            self.currentDataset = data
            self._read_results()
            self._update_data_list()
            self._update_plots()
            self.visualizer.update_config(data["modules"])

            # add results to history
            lastSimCount = self.lastSimList.count()
            lastSimData = {'modules': data['modules'],
                           'results': data['results'],
                           'simulation': data['simulation'],
                           'name': self._current_regime_name,
                           }
            display_name = "{}:{}".format(lastSimCount,
                                          self._current_regime_name)
            self._lastSimulations.append(lastSimData)
            new_item = QListWidgetItem(display_name)
            self.lastSimList.addItem(new_item)
            self.lastSimList.scrollToItem(new_item)
            self.setQListItemBold(self.lastSimList, new_item)

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
        state = self.currentDataset["results"]["Solver"]
        self.interpolator = interp1d(self.currentDataset["results"]["time"],
                                     state,
                                     axis=0,
                                     bounds_error=False,
                                     fill_value=(state[0], state[-1]))
        self.currentStepSize = 1.0 / self.currentDataset["simulation"][
            "measure rate"]
        self.currentStartTime = self.currentDataset["simulation"]["start time"]
        self.currentEndTime = self.currentDataset["simulation"]["end time"]

    def increment_playback_speed(self):
        self.speedControl.setValue(self.speedControl.value()
                                   + self.speedControl.singleStep())

    def decrement_playback_speed(self):
        self.speedControl.setValue(self.speedControl.value()
                                   - self.speedControl.singleStep())

    def reset_playback_speed(self):
        self.speedControl.setValue((self.speedControl.maximum()
                                    - self.speedControl.minimum()) / 2)

    def set_slowest_playback_speed(self):
        self.speedControl.setValue(self.speedControl.minimum())

    def set_fastest_playback_speed(self):
        self.speedControl.setValue(self.speedControl.maximum())

    def update_playback_speed(self, val):
        maximum = self.speedControl.maximum()
        self.playbackGain = 10 ** (3.0 * (val - maximum / 2) / maximum)

    @pyqtSlot()
    def increment_playback_time(self):
        """
        go one time step forward in playback
        """
        if self.playbackTime >= self.currentEndTime:
            self.pause_animation()
            return

        increment = self.playbackGain * self.playbackTimeout / 1000
        self.playbackTime = min(self.currentEndTime,
                                self.playbackTime + increment)
        self.playbackTimeChanged.emit()

    def _update_time_slider(self):
        time_delta = self.currentEndTime - self.currentStartTime
        if time_delta == 0:
            # no meaningful context to update the slider
            return

        rel_pos = (self.playbackTime - self.currentStartTime) / (
            time_delta)
        pos = int(rel_pos * self.timeSliderRange)
        self.timeSlider.blockSignals(True)
        self.timeSlider.setValue(pos)
        self.timeSlider.blockSignals(False)

    def update_playback_time(self):
        """
        adjust playback time to slider value
        """
        self.playbackTime = self.timeSlider.value() / self.timeSliderRange * (
                self.currentEndTime
                - self.currentStartTime
        ) + self.currentStartTime
        self.playbackTimeChanged.emit()

    def update_gui(self):
        """
        Updates the graphical user interface to reflect changes of the current
        display time. 
        
        This includes:
            - timestamp
            - visualisation window
            - time cursors in diagrams
        """
        self.timeLabel.setText("t={0:.3e}".format(self.playbackTime))

        # update timing elements
        self._update_time_slider()
        self._update_time_cursors()

        # update state of rendering
        if self.visualizer is not None and self.interpolator is not None:
            state = self.interpolator(self.playbackTime)
            self.visualizer.update_scene(state)
            if isinstance(self.visualizer, MplVisualizer):
                pass
            elif isinstance(self.visualizer, VtkVisualizer):
                self.vtkWidget.GetRenderWindow().Render()

    def _update_data_list(self):
        # self.dataList.clear()
        self.dataPointListWidget.clear()
        # TODO lets open and check if possible to plot
        # TODO create trees with children instead of plain suffixes
        for module_name, results in self.currentDataset["results"].items():
            if not isinstance(results, np.ndarray):
                continue
            if len(results.shape) == 1:
                self.dataPointListWidget.addItem(module_name)
            elif len(results.shape) == 2:
                for col in range(results.shape[1]):
                    self.dataPointListWidget.addItem(
                        self._build_entry_name(module_name, (col,))
                    )
            elif len(results.shape) == 3:
                for col in range(results.shape[1]):
                    for der in range(results.shape[2]):
                        self.dataPointListWidget.addItem(
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

    def _update_plot(self, item):
        # collect data
        if self.currentDataset is None:
            return

        title = item.text(0)
        t = self.currentDataset["results"]["time"]
        docks = self.find_all_plot_docks()
        target = next((d for d in docks if d.title() == title), None)
        if target is None:
            return

        for widget in target.widgets:
            child_names = [item.child(c_idx).text(1)
                           for c_idx in range(item.childCount())]
            del_list = []
            cnt = 0
            for _item in widget.getPlotItem().items:
                if isinstance(_item, pg.PlotDataItem):
                    if _item.name() in child_names:
                        y_data = self._get_data_by_name(_item.name())
                        if y_data is not None:
                            _item.setData(x=t, y=y_data)
                            _item.setPen(self._get_pen(cnt))
                            cnt += 1
                        else:
                            _item.clear()
                    else:
                        del_list.append(_item)

            for _item in del_list:
                widget.getPlotItem().removeItem(_item)

    def plot_data_vector(self, item):
        """
        Creates a plot widget based on the given item.

        If a plot for this item is already open no new plot is created but the
        existing one is raised up again.

        Args:
            item(Qt.ListItem): Item to plot.
        """
        if self.currentDataset is None:
            return

        title = str(item.text(0))

        # create plot widget
        widget = pg.PlotWidget()
        widget.showGrid(True, True)
        widget.getPlotItem().getAxis("bottom").setLabel(text="Time", units="s")

        for idx in range(item.childCount()):
            self.plot_data_vector_member(item.child(idx), widget)

        # add a time line
        time_line = pg.InfiniteLine(self.playbackTime,
                                    angle=90,
                                    movable=False,
                                    pen=pg.mkPen("#FF0000", width=2.0))
        widget.getPlotItem().addItem(time_line)

        coord_item = pg.TextItem(text='', anchor=(0, 1))
        widget.getPlotItem().addItem(coord_item, ignoreBounds=True)

        def _info_wrapper(pos):
            self.update_coord_info(pos, widget, coord_item)

        widget.scene().sigMouseMoved.connect(_info_wrapper)

        # add custom export entries
        widget.scene().contextMenu = [
            QAction("Export as ...", self),
        ]

        def _export_wrapper(export_func):
            def _wrapper():
                return export_func(widget.getPlotItem(),
                                   title,
                                   coord_item,
                                   time_line)
            return _wrapper

        widget.scene().contextMenu[0].triggered.connect(
            _export_wrapper(self.export_plot_item))

        # create dock container and add it to dock area
        dock = pg.dockarea.Dock(title, closable=True)
        dock.addWidget(widget)

        plotWidgets = self.find_all_plot_docks()
        if plotWidgets:
            self.area.addDock(dock, "above", plotWidgets[0])
        else:
            self.area.addDock(dock, "bottom", self.animationDock)

    def update_coord_info(self, pos, widget, coord_item):
        mouse_coords = widget.getPlotItem().vb.mapSceneToView(pos)
        coord_item.setPos(mouse_coords.x(), mouse_coords.y())
        coord_text = "x={:.3e} y={:.3e}".format(mouse_coords.x(),
                                                mouse_coords.y())
        self.coordLabel.setText(coord_text)

        show_info = self._settings.value("view/show_coordinates") == "True"
        if widget.sceneBoundingRect().contains(pos) and show_info:
            coord_item.setText(coord_text.replace(" ", "\n"))
            coord_item.show()
        else:
            coord_item.hide()

    def plot_data_vector_member(self, item, widget):
        idx = item.parent().indexOfChild(item)

        data_name = item.text(1)
        t = self.currentDataset["results"]["time"]
        data = self._get_data_by_name(data_name)
        if data is None:
            t = None

        widget.plot(x=t,
                    y=data,
                    pen=self._get_pen(idx),
                    name=data_name)

    def find_all_plot_docks(self):
        list = []
        for title, dock in self.area.findAll()[1].items():
            if title in self.non_plotting_docks:
                continue
            else:
                list.append(dock)

        return list

    def export_plot_item(self, plot_item, name, coord_item, time_item):
        plot_data = {}
        for i, c in enumerate(plot_item.curves):
            if c.getData() is None:
                continue
            if len(c.getData()) > 2:
                self._logger.warning("Can not handle data format of entry"
                                     "'{}'!".format(c.name()))
                continue
            if "time" not in plot_data:
                plot_data["time"] = c.getData()[0]

            c_name = c.name()
            c_unit = self._get_units(c_name)
            if c_unit is not None:
                c_name += " ({})".format(c_unit)

            plot_data[c_name] = c.getData()[1]

        self.export(plot_data)

    def export(self, plot_data):
        try:
            exporter = Exporter(data_points=plot_data)
        except Exception as e:
            self._logger.error("Can't instantiate exporter! " + str(e))
            return

        last_path = self._settings.value("path/previous_plot_export")
        last_format = self._settings.value("path/previous_plot_format")
        export_formats = ["CSV Data (*.csv)", "PNG Image (*.png)"]
        if last_format == ".png":
            export_formats[:] = export_formats[::-1]
        format_str = ";;".join(export_formats)
        default_file = os.path.join(last_path, "export" + last_format)
        filename = QFileDialog.getSaveFileName(self,
                                               "Export as ...",
                                               default_file,
                                               format_str)

        if filename[0]:
            file, ext = os.path.splitext(filename[0])
            self._settings.setValue("path/previous_plot_export",
                                    os.path.dirname(file))
            if ext == '.csv':
                exporter.export_csv(filename[0])
                self._settings.setValue("path/previous_plot_format", ".csv")
            elif ext == '.png':
                exporter.export_png(filename[0])
                self._settings.setValue("path/previous_plot_format", ".png")
            else:
                self._logger.error("Wrong extension used!")
                return
            self._logger.info("Export successful as '{}'.".format(filename[0]))

    def _get_data_by_name(self, name):
        tmp = name.split(".")
        module_name = tmp[0]
        try:
            raw_data = self.currentDataset["results"][module_name]
        except KeyError:
            return None

        if len(tmp) == 1:
            data = np.array(raw_data)
        elif len(tmp) == 2:
            try:
                idx = int(tmp[1])
            except ValueError:
                idx = self._get_index_from_suffix(module_name, tmp[1])
            if raw_data.ndim != 2 or raw_data.shape[1] <= idx:
                return None
            data = raw_data[:, idx]
        elif len(tmp) == 3:
            try:
                idx = int(tmp[1])
                der = int(tmp[2])
            except ValueError:
                return None
            if raw_data.ndim != 3 or raw_data.shape[1] <= idx \
                    or raw_data.shape[2] <= der:
                return None
            data = raw_data[:, idx, der]
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
        root = self.dataPointTreeWidget.invisibleRootItem()
        for i in range(root.childCount()):
            self._update_plot(root.child(i))

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
            self.postprocessor = PostProcessor(self._settings)

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

    def loadStandardDockState(self):
        for docks in self.find_all_plot_docks():
            docks.close()
        self.area.restoreState(self.standardDockState)

    def setQListItemBold(self, q_list=None, item=None, state=True):
        for i in range(q_list.count()):
            new_font = q_list.item(i).font()
            if q_list.item(i) == item and state:
                new_font.setBold(1)
            else:
                new_font.setBold(0)
            q_list.item(i).setFont(new_font)
        q_list.repaint()
