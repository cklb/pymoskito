# -*- coding: utf-8 -*-
import pickle
import logging
import os

from PyQt5.QtCore import Qt, pyqtSignal, QSize, QSettings
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import (
    QWidget, QAction, QMainWindow, QListWidget, QListWidgetItem, QToolBar,
    QStatusBar, QLabel, QShortcut, QFileDialog, QGridLayout, QSizePolicy,
    QPlainTextEdit
)

from . import registry as pm
from .processing_core import PostProcessingModule, MetaProcessingModule
from .tools import get_resource, PlainTextLogger, PostFilter

__all__ = ["PostProcessor"]


class PostProcessor(QMainWindow):

    sim_results_changed = pyqtSignal()
    post_results_changed = pyqtSignal()

    figures_changed = pyqtSignal(list, str)

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self._settings = QSettings()
        self._logger = logging.getLogger(self.__class__.__name__)

        self.setWindowTitle("Processing")
        self.setWindowIcon(QIcon(get_resource("processing.png")))
        self.mainFrame = QWidget(self)
        self.resize(1000, 600)

        # toolbar
        self.toolBar = QToolBar("file control")
        self.toolBar.setIconSize(QSize(24, 24))
        self.addToolBar(self.toolBar)

        self.actLoad = QAction(self)
        self.actLoad.setText("load result file")
        self.actLoad.setIcon(QIcon(get_resource("load.png")))
        self.actLoad.setDisabled(False)
        self.actLoad.triggered.connect(self.load_result_files)

        self.actPostLoad = QAction(self)
        self.actPostLoad.setText("load post-result file")
        self.actPostLoad.setIcon(QIcon(get_resource("load.png")))
        self.actPostLoad.setDisabled(False)
        self.actPostLoad.triggered.connect(self.load_post_result_files)

        self.actSwitch = QAction(self)
        self.actSwitch.setText("switch display mode")
        self.actSwitch.setIcon(QIcon(get_resource("left_mode.png")))
        self.actSwitch.setDisabled(False)
        self.actSwitch.triggered.connect(self.switch_sides)
        self.displayLeft = True

        self.spacer1 = QWidget()
        self.spacer2 = QWidget()
        self.spacer1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.spacer2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.actReloadMethods = QAction(self)
        self.actReloadMethods.setText("reload methods")
        self.actReloadMethods.setIcon(QIcon(get_resource("reload.png")))
        self.actReloadMethods.setDisabled(False)
        self.actReloadMethods.triggered.connect(self.update_post_method_list)

        self.actReloadMetaMethods = QAction(self)
        self.actReloadMetaMethods.setText("reload meta methods")
        self.actReloadMetaMethods.setIcon(QIcon(get_resource("reload.png")))
        self.actReloadMetaMethods.setDisabled(False)
        self.actReloadMetaMethods.triggered.connect(
            self.update_meta_method_list)
        
        self.toolBar.addAction(self.actLoad)
        self.toolBar.addAction(self.actReloadMethods)
        
        self.toolBar.addWidget(self.spacer1)
        self.toolBar.addAction(self.actSwitch)
        self.toolBar.addWidget(self.spacer2)

        self.toolBar.addAction(self.actReloadMetaMethods)
        self.toolBar.addAction(self.actPostLoad)

        # main window
        self.grid = QGridLayout(self.mainFrame)
        self.grid.setColumnMinimumWidth(0, 70)
        self.grid.setColumnStretch(0, 0)
        self.grid.setColumnStretch(1, 1)

        self.methodList = QListWidget(self)
        self.methodList.itemDoubleClicked.connect(
            self.post_processor_clicked)
        self.update_post_method_list()
        self.metaMethodList = QListWidget(self)
        self.metaMethodList.itemDoubleClicked.connect(
            self.meta_processor_clicked)
        self.update_meta_method_list()

        self.sim_result_list = QListWidget(self)
        self.sim_results_changed.connect(self.update_result_list)
        self.results = []

        self.delShort = QShortcut(QKeySequence(Qt.Key_Delete),
                                  self.sim_result_list)
        self.delShort.activated.connect(self.remove_result_item)

        # figures
        self._figure_dict = {}
        self.figures_changed.connect(self.update_figure_lists)

        self.post_figure_list = QListWidget(self)
        self.post_figure_list.currentItemChanged.connect(
            self.current_figure_changed)
        self.meta_figure_list = QListWidget(self)
        self.meta_figure_list.currentItemChanged.connect(
            self.current_figure_changed)

        self.plotView = QWidget()
        self.lastFigure = None

        self.post_result_list = QListWidget(self)
        self.post_results_changed.connect(self.update_post_result_list)
        self.post_results = []
        self.delShortPost = QShortcut(QKeySequence(Qt.Key_Backspace),
                                      self.post_result_list)
        self.delShortPost.activated.connect(self.remove_post_result_item)

        # log dock
        self.logBox = QPlainTextEdit(self)
        self.logBox.setReadOnly(True)

        # init logger for logging box
        self.textLogger = PlainTextLogger(logging.INFO)
        self.textLogger.set_target_cb(self.logBox.appendPlainText)
        logging.getLogger().addHandler(self.textLogger)

        self.grid.addWidget(QLabel("Result Files:"), 0, 0)
        self.grid.addWidget(self.sim_result_list, 1, 0)
        self.grid.addWidget(QLabel("Postprocessors:"), 2, 0)
        self.grid.addWidget(self.methodList, 3, 0)
        self.grid.addWidget(QLabel("Figures:"), 4, 0)
        self.grid.addWidget(self.post_figure_list, 5, 0)
        self.grid.addWidget(QLabel("Selected Figure:"), 0, 1)
        self.grid.addWidget(QLabel("Postprocessor Files:"), 0, 2)
        self.grid.addWidget(self.post_result_list, 1, 2)
        self.grid.addWidget(QLabel("Metaprocessors:"), 2, 2)
        self.grid.addWidget(self.metaMethodList, 3, 2)
        self.grid.addWidget(QLabel("Figures:"), 4, 2)
        self.grid.addWidget(self.meta_figure_list, 5, 2)
        self.grid.addWidget(self.logBox, 6, 0, 1, 3)

        self.mainFrame.setLayout(self.grid)
        self.setCentralWidget(self.mainFrame)

        # status bar
        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)

    def load_result_files(self):
        path = self._settings.value("path/simulation_results")

        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.ExistingFiles)
        dialog.setDirectory(path)
        dialog.setNameFilter("PyMoskito Result files (*.pmr)")

        if dialog.exec_():
            files = dialog.selectedFiles()
            for single_file in files:
                if single_file:
                    self._load_result_file(single_file)

    def _load_result_file(self, file_name):
        """
        loads a result file
        """
        self._logger.info("loading result file {}".format(file_name))
        with open(file_name.encode(), "rb") as f:
            self.results.append(pickle.load(f))

        self.sim_results_changed.emit()

    def update_result_list(self):
        self.sim_result_list.clear()
        for res in self.results:
            name = res["regime name"]
            self.sim_result_list.addItem(name)

    def remove_result_item(self):
        if self.sim_result_list.currentRow() >= 0:
            del self.results[self.sim_result_list.currentRow()]
            self.sim_result_list.takeItem(self.sim_result_list.currentRow())

    def load_post_result_files(self):
        path = self._settings.value("path/processing_results")

        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.ExistingFiles)
        dialog.setDirectory(path)
        dialog.setNameFilter("Postprocessing Output files (*.pof)")

        if dialog.exec_():
            files = dialog.selectedFiles()
            for single_file in files:
                if single_file:
                    self._load_post_result_file(single_file)

    def _load_post_result_file(self, file_name):
        """
        loads a post-result file (.pof)
        """
        name = os.path.split(file_name)[-1][:-4]
        self._logger.info("loading result file {}".format(file_name))
        with open(file_name.encode(), "rb") as f:
            results = pickle.load(f)
            results.update({"name": name})
            self.post_results.append(results)

        self.post_results_changed.emit()

    def update_post_result_list(self):
        self.post_result_list.clear()
        for res in self.post_results:
            name = res["name"]
            self.post_result_list.addItem(name)

    def remove_post_result_item(self):
        if self.post_result_list.currentRow() >= 0:
            del self.post_results[self.post_result_list.currentRow()]
            self.post_result_list.takeItem(self.post_result_list.currentRow())

    def update_post_method_list(self):
        self.methodList.clear()
        modules = pm.get_registered_processing_modules(PostProcessingModule)
        for mod in modules:
            self.methodList.addItem(mod[1])

    def update_meta_method_list(self):
        self.metaMethodList.clear()
        modules = pm.get_registered_processing_modules(MetaProcessingModule)
        for mod in modules:
            self.metaMethodList.addItem(mod[1])

    def post_processor_clicked(self, item):
        self.run_processor(str(item.text()), "post")

    def meta_processor_clicked(self, item):
        self.run_processor(str(item.text()), "meta")

    def run_processor(self, name, processor_type):
        if processor_type == "post":
            result_files = self.results
            base_cls = PostProcessingModule
        elif processor_type == "meta":
            result_files = self.post_results
            base_cls = MetaProcessingModule
        else:
            self._logger.error("unknown processor type {0}".format(
                processor_type))
            raise ValueError("unknown processor type {0}".format(
                processor_type))

        if not result_files:
            self._logger.warning("run_processor() Error: no result file loaded")
            return

        processor_cls = pm.get_processing_module_class_by_name(base_cls, name)
        processor = processor_cls()

        figs = []
        try:
            self._logger.info("executing processor '{0}'".format(name))
            figs = processor.process(self.results)
        except Exception as err:
            self._logger.exception("Error in processor")

        self.figures_changed.emit(figs, processor_type)
        self._logger.info("finished postprocessing")

    def update_figure_lists(self, figures, target_type):
        # remove no longer needed elements
        for item, fig in [(key, val[0])
                          for key, val in self._figure_dict.items()
                          if val[1] == target_type]:
            if fig not in [new_fig["figure"] for new_fig in figures]:
                if target_type == "post":
                    old_item = self.post_figure_list.takeItem(
                        self.post_figure_list.row(item))
                    del old_item
                elif target_type == "meta":
                    old_item = self.meta_figure_list.takeItem(
                        self.meta_figure_list.row(item))
                    del old_item

                del self._figure_dict[item]

        # add new ones to internal storage
        for fig in figures:
            if fig["figure"] not in self._figure_dict.values():
                new_entry = [(fig["name"],
                              (QListWidgetItem(fig["name"]),
                               fig["figure"], target_type)
                              )]
                self._figure_dict.update(new_entry)

        # add to display
        for key, val in self._figure_dict.items():
            if val[2] == "post":
                self.post_figure_list.addItem(val[0])
            elif val[2] == "meta":
                self.meta_figure_list.addItem(val[0])

        self.post_figure_list.setCurrentItem(self.post_figure_list.item(0))
        self.meta_figure_list.setCurrentItem(self.meta_figure_list.item(0))

    def current_figure_changed(self, current_item, last_item=None):
        if current_item is None:
            return

        figures = self._figure_dict

        if self.lastFigure:
            self.grid.removeWidget(self.lastFigure)
            self.lastFigure.setVisible(False)

        if current_item.text() in figures:
            figure_widget = figures[current_item.text()][1]
            self.grid.addWidget(figure_widget, 1, 1, 5, 1)
            figure_widget.setVisible(True)
            self.lastFigure = figure_widget
        
    def switch_sides(self):
        self.displayLeft = not self.displayLeft
        if self.displayLeft:
            self.actSwitch.setIcon(QIcon(get_resource("left_mode.png")))
            self.post_figure_list.setFocus()
            self.current_figure_changed(self.post_figure_list.currentItem())
        else:
            self.actSwitch.setIcon(QIcon(get_resource("right_mode.png")))
            self.meta_figure_list.setFocus()
            self.current_figure_changed(self.meta_figure_list.currentItem())
