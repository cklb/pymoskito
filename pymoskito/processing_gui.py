# -*- coding: utf-8 -*-
import os
import cPickle
import traceback
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSignal

import pymoskito as pm
from processing_core import ProcessingModule, PostProcessingModule, MetaProcessingModule
import generic_processing_modules
# import generic_metaprocessing_modules
from tools import get_resource


class PostProcessor(QtGui.QMainWindow):

    resultsChanged = pyqtSignal()
    postResultsChanged = pyqtSignal()

    figures_changed = pyqtSignal(list, str)

    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setWindowTitle("Postprocessing")
        self.setWindowIcon(QtGui.QIcon(get_resource("postprocessing.png")))
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
        
        self.resultList = QtGui.QListWidget(self)
        self.resultsChanged.connect(self.update_result_list)
        self.results = []

        self.delShort = QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Delete), self.resultList)
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

        self.postResultList = QtGui.QListWidget(self)
        self.postResultsChanged.connect(self.update_post_result_list)
        self.postResults = []
        self.delShortPost = QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Backspace), self.postResultList)
        self.delShortPost.activated.connect(self.remove_post_result_item)

        self.grid.addWidget(QtGui.QLabel("result files:"), 0, 0)
        self.grid.addWidget(self.resultList, 1, 0)
        self.grid.addWidget(QtGui.QLabel("postprocessors:"), 2, 0)
        self.grid.addWidget(self.methodList, 3, 0)
        self.grid.addWidget(QtGui.QLabel("figures:"), 4, 0)
        self.grid.addWidget(self.post_figure_list, 5, 0)
        self.grid.addWidget(QtGui.QLabel("selected figure:"), 0, 1)
        self.grid.addWidget(QtGui.QLabel("postprocessor files:"), 0, 2)
        self.grid.addWidget(self.postResultList, 1, 2)
        self.grid.addWidget(QtGui.QLabel("metaprocessors:"), 2, 2)
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
            for selectedFile in files:
                self._load_result_file(selectedFile)

    def _load_result_file(self, file_name):
        """
        loads a result file
        """
        with open(file_name, 'rb') as f:
            self.results.append(cPickle.load(f))

        self.resultsChanged.emit()

    def update_result_list(self):
        self.resultList.clear()
        for res in self.results:
            name = res['regime name']
            self.resultList.addItem(name)

    def remove_result_item(self):
        if self.resultList.currentRow() >= 0:
            del self.results[self.resultList.currentRow()]
            self.resultList.takeItem(self.resultList.currentRow())

    def load_post_result_files(self):
        path = os.path.join(os.path.pardir, "results", "postprocessing")
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
        with open(file_name, 'r') as f:
            results = eval(f.read())
            results.update({'name': name})
            self.postResults.append(results)

        self.postResultsChanged.emit()

    def update_post_result_list(self):
        self.postResultList.clear()
        for res in self.postResults:
            name = res['name']
            self.postResultList.addItem(name)

    def remove_post_result_item(self):
        if self.postResultList.currentRow() >= 0:
            del self.postResults[self.postResultList.currentRow()]
            self.postResultList.takeItem(self.postResultList.currentRow())

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
        if not self.results:
            print 'run_processor() Error: no result file loaded!'
            return

        # if self.post_figure_list.currentRow() >= 0:
        #     self.grid.removeWidget(self.current_figures[self.post_figure_list.currentRow()]['figure'])
        # del self.current_figures[:]

        if processor_type == "post":
            base_cls = PostProcessingModule
        elif processor_type == "meta":
            base_cls = MetaProcessingModule
        else:
            raise ValueError("unknown processor type {0}".format(processor_type))

        processor_cls = pm.get_processing_module_class_by_name(base_cls, name)
        processor = processor_cls()

        figs = []
        try:
            print(">>> Processor() running: {0}".format(name))
            figs = processor.process(self.results)
        except Exception, err:
            print 'Error in Postprocessor!'
            print traceback.format_exc()

        print '>>> finished.'

        self.post_figure_list.setFocus()
        self.figures_changed.emit(figs, processor_type)
        
    # def run_meta_processor(self, item):
    #     if not self.postResults:
    #         print 'runMetaprocessor(): Error no post-result files loaded!'
    #         return
    #
    #     if self.meta_figure_list.currentRow() >= 0:
    #         self.grid.removeWidget(self.current_metaFigures[self.meta_figure_list.currentRow()]['figure'])
    #
    #     del self.current_metaFigures[:]
    #
    #     name = str(item.text())
    #     print 'MetaProcessor() running: ', name
    #
    #     module = __import__('.'.join(['metaprocessing', name]))
    #     processor = getattr(getattr(module, name), name)()
    #
    #     figs = []
    #     try:
    #         figs = processor.run(self.postResults)
    #         self.current_metaFigures = figs
    #
    #     except Exception, err:
    #         print 'Error in Metaprocessor!'
    #         print traceback.format_exc()
    #
    #     self.meta_figure_list.setFocus()
    #     self.metaFiguresChanged.emit(figs, "meta")
    
    def update_figure_lists(self, figures, target_type):
        # remove no longer needed elements TODO make this work
        for item, fig in [(key, val[0]) for key, val in self._figure_dict.iteritems() if val[1] == target_type]:
            if fig not in [fig["figure"] for fig in figures]:
                if target_type == "post":
                    self.post_figure_list.removeItemWidget(item)
                elif target_type == "meta":
                    self.meta_figure_list.removeItemWidget(item)
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

        if current_item:
            figure_widget = figures[current_item][0]
            self.grid.addWidget(figure_widget, 1, 1, 5, 1)
            figure_widget.setVisible(True)
            self.lastFigure = figure_widget
        
    def switch_sides(self):
        self.displayLeft = not self.displayLeft
        if self.displayLeft:
            self.actSwitch.setIcon(QtGui.QIcon('data/left_mode.png'))
            self.post_figure_list.setFocus()
            self.current_figure_changed(self.post_figure_list.currentItem())
        else:
            self.actSwitch.setIcon(QtGui.QIcon('data/right_mode.png'))
            self.meta_figure_list.setFocus()
            self.current_figure_changed(self.meta_figure_list.currentItem())
