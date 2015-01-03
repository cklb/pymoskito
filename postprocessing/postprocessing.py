# -*- coding: utf-8 -*-

#pyqt
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSignal

#std
import os

#own
class PostProcessor(QtGui.QMainWindow):

    resultsChanged = pyqtSignal()
    figuresChanged = pyqtSignal()

    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setWindowTitle('Postprocessing')
        self.setWindowIcon(QtGui.QIcon('data/postprocessing.png'))
        self.frame = QtGui.QFrame()
        self.setCentralWidget(self.frame)
        self.resize(500, 400)

        #toolbar
        self.toolBar = QtGui.QToolBar('file control')
        self.toolBar.setIconSize(QtCore.QSize(24,24))
        self.addToolBar(self.toolBar)

        self.actLoad= QtGui.QAction(self)
        self.actLoad.setText('load result file')
        self.actLoad.setIcon(QtGui.QIcon('data/load.png'))
        self.actLoad.setDisabled(False)
        self.actLoad.triggered.connect(self.loadResultFilesClicked)
        
        self.actReloadMethods= QtGui.QAction(self)
        self.actReloadMethods.setText('reload methods')
        self.actReloadMethods.setIcon(QtGui.QIcon('data/reload.png'))
        self.actReloadMethods.setDisabled(False)
        self.actReloadMethods.triggered.connect(self.updateMethodList)

        self.toolBar.addAction(self.actLoad)
        self.toolBar.addAction(self.actReloadMethods)

        #main window
        self.grid = QtGui.QGridLayout(self)
        self.frame.setLayout(self.grid)

        self.methodList = QtGui.QListWidget(self)
        self.methodList.itemDoubleClicked.connect(self.runPostprocessor)
        self.updateMethodList()
        
        self.resultList = QtGui.QListWidget(self)
        #self.resultList.itemDoubleClicked.connect(self.runPostprocessor)
        self.resultsChanged.connect(self.updateResultList)
        self.results = []

        #self.spacer = QtGui.QSpacerItem(300, 300)

        self.figureList = QtGui.QListWidget(self)
        self.figureList.itemDoubleClicked.connect(self.figureDoubleClicked)
        self.figuresChanged.connect(self.updateFigureList)
        
        self.plotView = QtGui.QGraphicsView()
        self.current_figures = []

        
        self.grid.addWidget(QtGui.QLabel('result files:'), 0, 0)
        self.grid.addWidget(self.resultList, 1, 0)
        self.grid.addWidget(QtGui.QLabel('postprocessors:'), 2, 0)
        self.grid.addWidget(self.methodList, 3, 0)
        self.grid.addWidget(QtGui.QLabel('figures:'), 4, 0)
        self.grid.addWidget(self.figureList, 5, 0)
        self.grid.addWidget(QtGui.QLabel('selected figure:'), 0, 1)

        #statusbar
        self.statusBar = QtGui.QStatusBar(self)
        self.setStatusBar(self.statusBar)
        #self.statusBar.setMessage('no datset loaded')
    
    def loadResultFilesClicked(self):
        path = os.path.join('../results/')
        dialog = QtGui.QFileDialog(self)
        dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)
        dialog.setDirectory(path)
        dialog.setNameFilter("BallBeam Result files (*.bbr)")

        files = None
        if(dialog.exec_()):
            files = dialog.selectedFiles()

        if files:
            for selectedFile in files:
                with open(selectedFile, 'r') as f:
                    self.results.append(eval(f.read()))
        
        self.resultsChanged.emit()

    def updateResultList(self):
        self.resultList.clear()
        for res in self.results:
            name = res['regime name']
            self.resultList.addItem(name)

    def updateMethodList(self):
        self.methodList.clear()

        # import all modules in current directory and display their names
        moduleNames = []
        path = os.path.join(os.curdir, 'postprocessing')
        for f in os.listdir(path):
            if not os.path.isfile(os.path.join(path, f)):
                continue
            elif f == 'postprocessing.py' or f == '__init__.py':
                continue
            elif f[-3:] != '.py':
                continue
            else:
                moduleNames.append(f[:-3])

        for module in moduleNames:
            self.methodList.addItem(module)

    def runPostprocessor(self, item):
        if not self.results:
            print 'runPostprocessor(): Error no result file loaded!'
            return

        #TODO
        #self.grid.removeWidget()
        #self.current_figures.clear()
        name = str(item.text())
        print 'PostProcessor() running: ', name

        module = __import__('.'.join(['postprocessing',name]))
        processor = getattr(getattr(module, name), name)()

        processFunc = processor.run
        for res in self.results:
            self.current_figures.append({'name':'_'.join([res['regime name'], name]),\
                    'figure': processFunc(res)})

        self.figuresChanged.emit()
    
    def updateFigureList(self):
        print self.current_figures
        for fig in self.current_figures:
            name = fig['name']
            self.figureList.addItem(name)
        
    def figureDoubleClicked(self, item):
        figWidget = next((figure['figure'] for figure in self.current_figures if figure['name']==str(item.text())), None)
        self.grid.addWidget(figWidget, 1, 1, 5, 1)



class PostProcessingModule:
    '''
    Base Class for Postprocessing Modules
    defines some basic functions that can later be vectorized
    '''
    def __init__(self):
        return

    def diff(self, a, b):
        return a-b

    def sum(self, a, b):
        return a+b
        
    def add(self, a, b):
        return a+b
        
    def subt(self, a, b):
        return a-b
    
    def mul(self, a, b):
        return a*b
        
