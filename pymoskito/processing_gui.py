# -*- coding: utf-8 -*-
import os
import logging
import cPickle
import traceback
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSignal

import registry as pm
from processing_core import ProcessingModule, PostProcessingModule, MetaProcessingModule
import generic_processing_modules
# import generic_metaprocessing_modules
from tools import get_resource


class PostProcessor(QtGui.QMainWindow):

    sim_results_changed = pyqtSignal()
    post_results_changed = pyqtSignal()

    figures_changed = pyqtSignal(list, str)

    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self._logger = logging.getLogger(self.__class__.__name__)

        self.setWindowTitle("Processing")
        self.setWindowIcon(QtGui.QIcon(get_resource("processing.png")))
        self.mainFrame = QtGui.QWidget(self)
        self.resize(1000, 600)

        # toolbar
        self.toolBar = QtGui.QToolBar("file control")
        self.toolBar.setIconSize(QtCore.QSize(24, 24))
        self.addToolBar(self.toolBar)

        self.actLoad = QtGui.QAction(self)
        self.actLoad.setText("load result file")
        self.actLoad.setIcon(QtGui.QIcon(get_resource("load.png")))
        self.actLoad.setDisabled(False)
        self.actLoad.triggered.connect(self.load_result_files)
        
        self.actPostLoad = QtGui.QAction(self)
        self.actPostLoad.setText("load post-result file")
        self.actPostLoad.setIcon(QtGui.QIcon(get_resource("load.png")))
        self.actPostLoad.setDisabled(False)
        self.actPostLoad.triggered.connect(self.load_post_result_files)

        self.actSwitch = QtGui.QAction(self)
        self.actSwitch.setText("switch display mode")
        self.actSwitch.setIcon(QtGui.QIcon(get_resource("left_mode.png")))
        self.actSwitch.setDisabled(False)
        self.actSwitch.triggered.connect(self.switch_sides)
        self.displayLeft = True

        self.spacer1 = QtGui.QWidget()
        self.spacer2 = QtGui.QWidget()
        self.spacer1.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.spacer2.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        self.actReloadMethods = QtGui.QAction(self)
        self.actReloadMethods.setText("reload methods")
        self.actReloadMethods.setIcon(QtGui.QIcon(get_resource("reload.png")))
        self.actReloadMethods.setDisabled(False)
        self.actReloadMethods.triggered.connect(self.update_post_method_list)

        self.actReloadMetaMethods = QtGui.QAction(self)
        self.actReloadMetaMethods.setText("reload meta methods")
        self.actReloadMetaMethods.setIcon(QtGui.QIcon(get_resource("reload.png")))
        self.actReloadMetaMethods.setDisabled(False)
        self.actReloadMetaMethods.triggered.connect(self.update_meta_method_list)
        
        self.toolBar.addAction(self.actLoad)
        self.toolBar.addAction(self.actReloadMethods)
        
        self.toolBar.addWidget(self.spacer1)
        self.toolBar.addAction(self.actSwitch)
        self.toolBar.addWidget(self.spacer2)

        self.toolBar.addAction(self.actReloadMetaMethods)
        self.toolBar.addAction(self.actPostLoad)

        # main.py window
        self.grid = QtGui.QGridLayout(self.mainFrame)
        self.grid.setColumnMinimumWidth(0, 70)
        self.grid.setColumnStretch(0, 0)
        self.grid.setColumnStretch(1, 1)

        self.methodList = QtGui.QListWidget(self)
        self.methodList.itemDoubleClicked.connect(self.post_processor_clicked)
        self.update_post_method_list()
        self.metaMethodList = QtGui.QListWidget(self)
        self.metaMethodList.itemDoubleClicked.connect(self.meta_processor_clicked)
        self.update_meta_method_list()
        
        self.sim_result_list = QtGui.QListWidget(self)
        self.sim_results_changed.connect(self.update_result_list)
        self.results = []

        self.delShort = QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Delete), self.sim_result_list)
        self.delShort.activated.connect(self.remove_result_item)

        # figures
        self._figure_dict = {}
        self.figures_changed.connect(self.update_figure_lists)

        self.post_figure_list = QtGui.QListWidget(self)
        self.post_figure_list.currentItemChanged.connect(self.current_figure_changed)
        self.meta_figure_list = QtGui.QListWidget(self)
        self.meta_figure_list.currentItemChanged.connect(self.current_figure_changed)

        self.plotView = QtGui.QWidget()
        self.lastFigure = None

        self.post_result_list = QtGui.QListWidget(self)
        self.post_results_changed.connect(self.update_post_result_list)
        self.post_results = []
        self.delShortPost = QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Backspace), self.post_result_list)
        self.delShortPost.activated.connect(self.remove_post_result_item)

        self.grid.addWidget(QtGui.QLabel("result files:"), 0, 0)
        self.grid.addWidget(self.sim_result_list, 1, 0)
        self.grid.addWidget(QtGui.QLabel("Postprocessors:"), 2, 0)
        self.grid.addWidget(self.methodList, 3, 0)
        self.grid.addWidget(QtGui.QLabel("figures:"), 4, 0)
        self.grid.addWidget(self.post_figure_list, 5, 0)
        self.grid.addWidget(QtGui.QLabel("selected figure:"), 0, 1)
        self.grid.addWidget(QtGui.QLabel("postprocessor files:"), 0, 2)
        self.grid.addWidget(self.post_result_list, 1, 2)
        self.grid.addWidget(QtGui.QLabel("Metaprocessors:"), 2, 2)
        self.grid.addWidget(self.metaMethodList, 3, 2)
        self.grid.addWidget(QtGui.QLabel("figures:"), 4, 2)
        self.grid.addWidget(self.meta_figure_list, 5, 2)

        self.mainFrame.setLayout(self.grid)
        self.setCentralWidget(self.mainFrame)

        # statusbar
        self.statusBar = QtGui.QStatusBar(self)
        self.setStatusBar(self.statusBar)

        # load test results
        # filePath = os.path.join(os.pardir, 'results', 'simulation', 'default', 'example.pmr')
        # self._loadResultFile(filePath)
        #
        # load test post-results
        # filePath = os.path.join(os.pardir, 'results', 'postprocessing', 'default')
        # self._loadResultFile(filePath)
    
    def load_result_files(self):
        path = os.path.join(os.path.pardir, "results", "simulation")
        dialog = QtGui.QFileDialog(self)
        dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)
        dialog.setDirectory(path)
        dialog.setNameFilter("PyMoskito Result files (*.pmr)")

        files = None
        if dialog.exec_():
            files = dialog.selectedFiles()

        if files:
            for single_file in files:
                self._load_result_file(unicode(single_file))

    def _load_result_file(self, file_name):
        """
        loads a result file
        """
        self._logger.info("loading result file {}".format(file_name.encode("utf-8")))
        with open(file_name, "rb") as f:
            self.results.append(cPickle.load(f))

        self.sim_results_changed.emit()

    def update_result_list(self):
        self.sim_result_list.clear()
        for res in self.results:
            name = res['regime name']
            self.sim_result_list.addItem(name)

    def remove_result_item(self):
        if self.sim_result_list.currentRow() >= 0:
            del self.results[self.sim_result_list.currentRow()]
            self.sim_result_list.takeItem(self.sim_result_list.currentRow())

    def load_post_result_files(self):
        path = os.path.join(os.path.pardir, "results", "processing")
        dialog = QtGui.QFileDialog(self)
        dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)
        dialog.setDirectory(path)
        dialog.setNameFilter("Postprocessing Output files (*.pof)")

        files = None
        if dialog.exec_():
            files = dialog.selectedFiles()

        if files:
            for selectedFile in files:
                self._load_post_result_file(str(selectedFile))

    def _load_post_result_file(self, file_name):
        """
        loads a post-result file (.pof)
        """
        name = os.path.split(file_name)[-1][:-4]
        with open(file_name, "r") as f:
            results = cPickle.load(f)
            results.update({'name': name})
            self.post_results.append(results)

        self.post_results_changed.emit()

    def update_post_result_list(self):
        self.post_result_list.clear()
        for res in self.post_results:
            name = res['name']
            self.post_result_list.addItem(name)

    def remove_post_result_item(self):
        if self.post_result_list.currentRow() >= 0:
            del self.post_results[self.post_result_list.currentRow()]
            self.post_result_list.takeItem(self.post_result_list.currentRow())

    def update_post_method_list(self):
        self.methodList.clear()
        modules = pm.get_registered_processing_modules(PostProcessingModule)
        for module in modules:
            self.methodList.addItem(module[1])

    def update_meta_method_list(self):
        self.metaMethodList.clear()
        modules = pm.get_registered_processing_modules(MetaProcessingModule)
        for module in modules:
            self.metaMethodList.addItem(module[1])

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
            raise ValueError("unknown processor type {0}".format(processor_type))

        if not result_files:
            self._logger.warning("run_processor() Error: no result file loaded!")
            return

        processor_cls = pm.get_processing_module_class_by_name(base_cls, name)
        processor = processor_cls()

        figs = []
        try:
            self._logger.info("executing processor '{0}'".format(name))
            figs = processor.process(self.results)
        except Exception, err:
            self._logger.exception("Error in processor")

        self.figures_changed.emit(figs, processor_type)
        self._logger.info("finished postprocessing")

    def update_figure_lists(self, figures, target_type):
        # remove no longer needed elements
        for item, fig in [(key, val[0]) for key, val in self._figure_dict.iteritems() if val[1] == target_type]:
            if fig not in [new_fig["figure"] for new_fig in figures]:
                if target_type == "post":
                    old_item = self.post_figure_list.takeItem(self.post_figure_list.row(item))
                    del old_item
                elif target_type == "meta":
                    old_item = self.meta_figure_list.takeItem(self.meta_figure_list.row(item))
                    del old_item

                del self._figure_dict[item]

        # add new ones to internal storage
        for fig in figures:
            if fig["figure"] not in self._figure_dict.values():
                self._figure_dict.update([(QtGui.QListWidgetItem(fig["name"]), (fig["figure"], target_type))])

        # add to display
        for key, val in self._figure_dict.iteritems():
            if val[1] == "post":
                self.post_figure_list.addItem(key)
            elif val[1] == "meta":
                self.meta_figure_list.addItem(key)

        self.post_figure_list.setCurrentItem(self.post_figure_list.item(0))
        self.meta_figure_list.setCurrentItem(self.meta_figure_list.item(0))

    def current_figure_changed(self, current_item, last_item=None):
        figures = self._figure_dict

        if self.lastFigure:
            self.grid.removeWidget(self.lastFigure)
            self.lastFigure.setVisible(False)

        if current_item in figures:
            figure_widget = figures[current_item][0]
            self.grid.addWidget(figure_widget, 1, 1, 5, 1)
            figure_widget.setVisible(True)
            self.lastFigure = figure_widget
        
    def switch_sides(self):
        self.displayLeft = not self.displayLeft
        if self.displayLeft:
            self.actSwitch.setIcon(QtGui.QIcon(get_resource("left_mode.png")))
            self.post_figure_list.setFocus()
            self.current_figure_changed(self.post_figure_list.currentItem())
        else:
            self.actSwitch.setIcon(QtGui.QIcon(get_resource("right_mode.png")))
            self.meta_figure_list.setFocus()
            self.current_figure_changed(self.meta_figure_list.currentItem())
