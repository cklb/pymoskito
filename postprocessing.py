# -*- coding: utf-8 -*-

#pyqt
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSignal

import pyqtgraph as pg

#std
import os
import numpy as np
import scipy as sp

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
        self.resize(600, 400)

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
        self.resultsChanged.connect(self.updateResultList)

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

    def runPostprocessor(self, item):
        if not self.results:
            print 'runPostprocessor(): Error no result file loaded!'
            return

        #TODO
        #self.grid.removeWidget()
        #self.current_figures.clear()
        name = str(item.text())
        print 'PostProcessor() running: ', name

        processFunc = getattr(self, name)
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

    def diff(self, a, b):
        return a-b

    def sum(self, a, b):
        return a+b

    #define your own functions here
    def hauserDiagrams(self, data):
        '''
        create diagrams like hauser did
        '''

        #calculate datasets
        t = data['results']['simTime']
        yd = data['results']['trajectory_output.0']
        y = []
        for i in range(3):
            y.append(data['results']['model_output.'+str(i)]  )

        vDiff = np.vectorize(self.diff)
        eps = vDiff(yd[0], y[0])

        #TODO phi one to three


        plots = pg.GraphicsLayoutWidget()
        p1 = pg.PlotItem(name='Sollwertfehler', lables={'left': 'epsilon', 'bottom':'t'})
        p1.plot(t, eps)
        p2 = pg.PlotItem(name='Sollwertfehler', lables={'left': 'epsilon', 'bottom':'t'})
        p2.plot(t, eps)


        plots.addItem(p1, 0, 0)
        plots.addItem(p2, 1, 0)

        return plots
