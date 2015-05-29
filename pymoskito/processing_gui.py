# -*- coding: utf-8 -*-
import os
import cPickle
import traceback
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSignal

from tools import get_resource


class PostProcessor(QtGui.QMainWindow):

    resultsChanged = pyqtSignal()
    figuresChanged = pyqtSignal()

    postResultsChanged = pyqtSignal()
    metaFiguresChanged = pyqtSignal()

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
        self.actReloadMethods.triggered.connect(self.update_method_list)

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

        # main window
        self.grid = QtGui.QGridLayout(self.mainFrame)
        self.grid.setColumnMinimumWidth(0, 70)
        self.grid.setColumnStretch(0, 0)
        self.grid.setColumnStretch(1, 1)

        self.methodList = QtGui.QListWidget(self)
        self.methodList.itemDoubleClicked.connect(self.run_post_processor)
        self.update_method_list()
        
        self.resultList = QtGui.QListWidget(self)
        self.resultsChanged.connect(self.update_result_list)
        self.results = []

        self.delShort = QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Delete), self.resultList)
        self.delShort.activated.connect(self.remove_result_item)

        self.figureList = QtGui.QListWidget(self)
        self.figureList.currentItemChanged.connect(self.current_figure_changed)
        self.figuresChanged.connect(self.update_post_figure_list)
        self.current_figures = []
        
        self.plotView = QtGui.QWidget()
        self.lastFigure = None

        self.metaMethodList = QtGui.QListWidget(self)
        self.metaMethodList.itemDoubleClicked.connect(self.run_meta_processor)
        self.update_meta_method_list()
        
        self.postResultList = QtGui.QListWidget(self)
        self.postResultsChanged.connect(self.update_post_result_list)
        self.postResults = []
        self.delShortPost = QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Backspace), self.postResultList)
        self.delShortPost.activated.connect(self.remove_post_result_item)

        self.metaFigureList = QtGui.QListWidget(self)
        self.metaFigureList.currentItemChanged.connect(self.current_figure_changed)
        self.metaFiguresChanged.connect(self.update_meta_figure_list)
        self.current_metaFigures = []
        
        self.grid.addWidget(QtGui.QLabel("result files:"), 0, 0)
        self.grid.addWidget(self.resultList, 1, 0)
        self.grid.addWidget(QtGui.QLabel("postprocessors:"), 2, 0)
        self.grid.addWidget(self.methodList, 3, 0)
        self.grid.addWidget(QtGui.QLabel("figures:"), 4, 0)
        self.grid.addWidget(self.figureList, 5, 0)
        self.grid.addWidget(QtGui.QLabel("selected figure:"), 0, 1)
        self.grid.addWidget(QtGui.QLabel("postprocessor files:"), 0, 2)
        self.grid.addWidget(self.postResultList, 1, 2)
        self.grid.addWidget(QtGui.QLabel("metaprocessors:"), 2, 2)
        self.grid.addWidget(self.metaMethodList, 3, 2)
        self.grid.addWidget(QtGui.QLabel("figures:"), 4, 2)
        self.grid.addWidget(self.metaFigureList, 5, 2)

        self.mainFrame.setLayout(self.grid)
        self.setCentralWidget(self.mainFrame)

        # statusbar
        self.statusBar = QtGui.QStatusBar(self)
        self.setStatusBar(self.statusBar)

        # load test results
        # filePath = os.path.join(os.pardir, 'results', 'simulation', 'default', 'example.bbr')
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
        dialog.setNameFilter("BallBeam Result files (*.bbr)")

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

    def update_method_list(self):
        self.methodList.clear()
         # TODO correct to new structure

        # import all modules in current directory and display their names
        module_names = []
        path = os.path.join(os.curdir, 'postprocessing')
        for f in os.listdir(path):
            if not os.path.isfile(os.path.join(path, f)):
                continue
            elif f == '__init__.py':
                continue
            elif f[-3:] != '.py':
                continue
            else:
                module_names.append(f[:-3])

        for module in module_names:
            self.methodList.addItem(module)

    def update_meta_method_list(self):
        self.metaMethodList.clear()
        # TODO correct to new structure

        # import all modules in current directory and display their names
        module_names = []
        path = os.path.join(os.curdir, "metaprocessing")
        for f in os.listdir(path):
            if not os.path.isfile(os.path.join(path, f)):
                continue
            elif f == '__init__.py':
                continue
            elif f[-3:] != '.py':
                continue
            else:
                module_names.append(f[:-3])

        for module in module_names:
            self.metaMethodList.addItem(module)

    def run_post_processor(self, item):
        if not self.results:
            print 'runPostprocessor(): Error no result file loaded!'
            return

        if self.figureList.currentRow() >= 0:
            self.grid.removeWidget(self.current_figures[self.figureList.currentRow()]['figure'])

        del self.current_figures[:]

        name = str(item.text())
        print '>>> PostProcessor() running: ', name

        module = __import__('.'.join(['postprocessing',name]))
        processor = getattr(getattr(module, name), name)()

        figs = []
        try:
            figs = processor.process(self.results)
            self.current_figures = figs

        except Exception, err:
            print 'Error in Postprocessor!'
            print traceback.format_exc()

        print '>>> finished.'

        self.figureList.setFocus()
        self.figuresChanged.emit()
        
    def run_meta_processor(self, item):
        if not self.postResults:
            print 'runMetaprocessor(): Error no post-result files loaded!'
            return

        if self.metaFigureList.currentRow() >= 0:
            self.grid.removeWidget(self.current_metaFigures[self.metaFigureList.currentRow()]['figure'])

        del self.current_metaFigures[:]

        name = str(item.text())
        print 'MetaProcessor() running: ', name

        module = __import__('.'.join(['metaprocessing', name]))
        processor = getattr(getattr(module, name), name)()

        figs = []
        try:
            figs = processor.run(self.postResults)
            self.current_metaFigures = figs

        except Exception, err:
            print 'Error in Metaprocessor!'
            print traceback.format_exc()

        self.metaFigureList.setFocus()
        self.metaFiguresChanged.emit()
    
    def update_post_figure_list(self):
        self.figureList.clear()
        for fig in self.current_figures:
            name = fig['name']
            self.figureList.addItem(name)

        self.figureList.setCurrentItem(self.figureList.item(0))

    def update_meta_figure_list(self):
        self.metaFigureList.clear()
        for fig in self.current_metaFigures:
            name = fig['name']
            self.metaFigureList.addItem(name)

        self.metaFigureList.setCurrentItem(self.metaFigureList.item(0))

    def current_figure_changed(self, current_item, last_item=None):
        if self.figureList.hasFocus():
            figures = self.current_figures
            figure_list = self.figureList
        else:
            figures = self.current_metaFigures
            figure_list = self.metaFigureList

        if self.lastFigure:
            self.grid.removeWidget(self.lastFigure)
            self.lastFigure.setVisible(False)

        if current_item:
            figure_widget = figures[figure_list.currentRow()]['figure']
            self.grid.addWidget(figure_widget, 1, 1, 5, 1)
            figure_widget.setVisible(True)
            self.lastFigure = figure_widget
        
    def switch_sides(self):
        self.displayLeft = not self.displayLeft
        if self.displayLeft:
            self.actSwitch.setIcon(QtGui.QIcon('data/left_mode.png'))
            self.figureList.setFocus()
            self.current_figure_changed(self.figureList.currentItem())
        else:
            self.actSwitch.setIcon(QtGui.QIcon('data/right_mode.png'))
            self.metaFigureList.setFocus()
            self.current_figure_changed(self.metaFigureList.currentItem())
