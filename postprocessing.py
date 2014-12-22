# -*- coding: utf-8 -*-

#pyqt
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSignal

#std
import os

#own

class PostProcessor(QtGui.QMainWindow):

    resultsChanged = pyqtSignal()

    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setWindowTitle('Postprocessing')
        self.setWindowIcon(QtGui.QIcon('data/postprocessing.png'))
        self.frame = QtGui.QFrame()
        self.setCentralWidget(self.frame)
        self.resize(400, 400)

        #toolbar
        self.toolBar = QtGui.QToolBar('file control')
        self.toolBar.setIconSize(QtCore.QSize(24,24))
        self.addToolBar(self.toolBar)

        self.actLoad= QtGui.QAction(self)
        self.actLoad.setText('load result file')
        self.actLoad.setIcon(QtGui.QIcon('data/load.png'))
        self.actLoad.setDisabled(False)
        self.actLoad.triggered.connect(self.loadResultFilesClicked)
        self.results = []

        self.toolBar.addAction(self.actLoad)

        #main window
        self.grid = QtGui.QGridLayout(self)
        self.frame.setLayout(self.grid)

        self.methodList = QtGui.QListWidget(self)
        self.methodList.itemDoubleClicked.connect(self.runPostprocessor)
        self.methodList.insertItem(0, 'hauserDiagrams')
        
        self.resultList = QtGui.QListWidget(self)
        #self.resultList.itemDoubleClicked.connect(self.runPostprocessor)

        #self.spacer = QtGui.QSpacerItem(300, 300)
        self.resultsChanged.connect(self.updateResultList)

        self.plotView = QtGui.QGraphicsView()

        self.grid.addWidget(self.resultList, 0, 0)
        self.grid.addWidget(self.methodList, 1, 0)
        self.grid.addWidget(self.plotView, 0, 1)

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

    def runPostprocessor(self, item):
        if self.results:
            print 'runPostprocessor(): Error no result file loaded!'

        name = str(item.text())
        processFunc = getattr(self, name)
        for res in self.results:
            processFunc(res)

    #define your own functions here
    def hauserDiagrams(self, data):
        print 'test'


