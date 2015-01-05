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

    postResultsChanged = pyqtSignal()
    postFiguresChanged = pyqtSignal()

    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setWindowTitle('Postprocessing')
        self.setWindowIcon(QtGui.QIcon('data/postprocessing.png'))
        self.mainFrame = QtGui.QWidget(self)
        self.resize(1000, 600)

        #toolbar
        self.toolBar = QtGui.QToolBar('file control')
        self.toolBar.setIconSize(QtCore.QSize(24,24))
        self.addToolBar(self.toolBar)

        self.actLoad= QtGui.QAction(self)
        self.actLoad.setText('load result file')
        self.actLoad.setIcon(QtGui.QIcon('data/load.png'))
        self.actLoad.setDisabled(False)
        self.actLoad.triggered.connect(self.loadResultFilesClicked)
        
        self.actPostLoad= QtGui.QAction(self)
        self.actPostLoad.setText('load post-result file')
        self.actPostLoad.setIcon(QtGui.QIcon('data/load.png'))
        self.actPostLoad.setDisabled(False)
        self.actPostLoad.triggered.connect(self.loadPostResultFilesClicked)

        self.actSwitch= QtGui.QAction(self)
        self.actSwitch.setText('switch disply mode')
        self.actSwitch.setIcon(QtGui.QIcon('data/left_mode.png'))
        self.actSwitch.setDisabled(False)
        self.actSwitch.triggered.connect(self.switchDisplaySides)
        self.displayLeft = True

        self.spacer1 = QtGui.QWidget()
        self.spacer2 = QtGui.QWidget()
        self.spacer1.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.spacer2.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        self.actReloadMethods= QtGui.QAction(self)
        self.actReloadMethods.setText('reload methods')
        self.actReloadMethods.setIcon(QtGui.QIcon('data/reload.png'))
        self.actReloadMethods.setDisabled(False)
        self.actReloadMethods.triggered.connect(self.updateMethodList)

        self.actReloadPostMethods= QtGui.QAction(self)
        self.actReloadPostMethods.setText('reload post methods')
        self.actReloadPostMethods.setIcon(QtGui.QIcon('data/reload.png'))
        self.actReloadPostMethods.setDisabled(False)
        self.actReloadPostMethods.triggered.connect(self.updatePostMethodList)
        
        self.toolBar.addAction(self.actLoad)
        self.toolBar.addAction(self.actReloadMethods)
        
        self.toolBar.addWidget(self.spacer1)
        self.toolBar.addAction(self.actSwitch)
        self.toolBar.addWidget(self.spacer2)

        self.toolBar.addAction(self.actReloadPostMethods)
        self.toolBar.addAction(self.actPostLoad)

        #main window
        self.grid = QtGui.QGridLayout(self.mainFrame)
        self.grid.setColumnMinimumWidth(0, 70)
        self.grid.setColumnStretch(0, 0)
        self.grid.setColumnStretch(1, 1)

        self.methodList = QtGui.QListWidget(self)
        self.methodList.itemDoubleClicked.connect(self.runPostprocessor)
        self.updateMethodList()
        
        self.resultList = QtGui.QListWidget(self)
        self.resultsChanged.connect(self.updateResultList)
        self.results = []
        self.delShort = QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Delete), self.resultList)
        self.delShort.activated.connect(self.removeResultItem)

        self.figureList = QtGui.QListWidget(self)
        self.figureList.currentItemChanged.connect(self.currentFigureChanged)
        self.figuresChanged.connect(self.updateFigureList)
        self.current_figures = []
        
        self.plotView = QtGui.QWidget()
        self.lastFigure = None

        self.postMethodList = QtGui.QListWidget(self)
        self.postMethodList.itemDoubleClicked.connect(self.runPostPostprocessor)
        self.updatePostMethodList()
        
        self.postResultList = QtGui.QListWidget(self)
        self.postResultsChanged.connect(self.updatePostResultList)
        self.postResults = []
        self.delShortPost = QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Backspace), self.postResultList)
        self.delShortPost.activated.connect(self.removePostResultItem)

        self.postFigureList = QtGui.QListWidget(self)
        self.postFigureList.currentItemChanged.connect(self.currentFigureChanged)
        self.postFiguresChanged.connect(self.updatePostFigureList)
        self.current_postFigures = []
        
        self.grid.addWidget(QtGui.QLabel('result files:'), 0, 0)
        self.grid.addWidget(self.resultList, 1, 0)
        self.grid.addWidget(QtGui.QLabel('postprocessors:'), 2, 0)
        self.grid.addWidget(self.methodList, 3, 0)
        self.grid.addWidget(QtGui.QLabel('figures:'), 4, 0)
        self.grid.addWidget(self.figureList, 5, 0)
        self.grid.addWidget(QtGui.QLabel('selected figure:'), 0, 1)
        self.grid.addWidget(QtGui.QLabel('postprocessor files:'), 0, 2)
        self.grid.addWidget(self.postResultList, 1, 2)
        self.grid.addWidget(QtGui.QLabel('postpostprocessors:'), 2, 2)
        self.grid.addWidget(self.postMethodList, 3, 2)
        self.grid.addWidget(QtGui.QLabel('figures:'), 4, 2)
        self.grid.addWidget(self.postFigureList, 5, 2)

        self.mainFrame.setLayout(self.grid)
        self.setCentralWidget(self.mainFrame)

        #statusbar
        self.statusBar = QtGui.QStatusBar(self)
        self.setStatusBar(self.statusBar)

        #load test results
        #filePath = os.path.join(os.pardir, 'results', 'simulation', 'default', 'example.bbr')
        #self._loadResultFile(filePath)
        
        #load test post-results
        #filePath = os.path.join(os.pardir, 'results', 'postprocessing', 'default')
        #self._loadResultFile(filePath)
    
    def loadResultFilesClicked(self):
        path = os.path.join(os.path.pardir, 'results', 'simulation')
        dialog = QtGui.QFileDialog(self)
        dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)
        dialog.setDirectory(path)
        dialog.setNameFilter("BallBeam Result files (*.bbr)")

        files = None
        if(dialog.exec_()):
            files = dialog.selectedFiles()

        if files:
            for selectedFile in files:
                self._loadResultFile(selectedFile)

    def _loadResultFile(self, fileName):
        '''
        loads a result file
        '''
        with open(fileName, 'r') as f:
            self.results.append(eval(f.read()))

        self.resultsChanged.emit()

    def updateResultList(self):
        self.resultList.clear()
        for res in self.results:
            name = res['regime name']
            self.resultList.addItem(name)

    def removeResultItem(self):
        if self.resultList.currentRow()>=0:
            del self.results[self.resultList.currentRow()]
            self.resultList.takeItem(self.resultList.currentRow())

    def loadPostResultFilesClicked(self):
        path = os.path.join(os.path.pardir, 'results', 'postprocessing')
        dialog = QtGui.QFileDialog(self)
        dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)
        dialog.setDirectory(path)
        dialog.setNameFilter("Postprocessing Output files (*.pof)")

        files = None
        if(dialog.exec_()):
            files = dialog.selectedFiles()

        if files:
            for selectedFile in files:
                self._loadPostResultFile(str(selectedFile))

    def _loadPostResultFile(self, fileName):
        '''
        loads a post-result file (.pof)
        '''
        name = os.path.split(fileName)[-1][:-4]
        with open(fileName, 'r') as f:
            results = eval(f.read())
            results.update({'name': name})
            self.postResults.append(results)

        self.postResultsChanged.emit()

    def updatePostResultList(self):
        self.postResultList.clear()
        for res in self.postResults:
            name = res['name']
            self.postResultList.addItem(name)

    def removePostResultItem(self):
        if self.postResultList.currentRow()>=0:
            del self.postResults[self.postResultList.currentRow()]
            self.postResultList.takeItem(self.postResultList.currentRow())

    def updateMethodList(self):
        self.methodList.clear()

        # import all modules in current directory and display their names
        moduleNames = []
        path = os.path.join(os.curdir, 'postprocessing')
        for f in os.listdir(path):
            if not os.path.isfile(os.path.join(path, f)):
                continue
            elif f == '__init__.py':
                continue
            elif f[-3:] != '.py':
                continue
            else:
                moduleNames.append(f[:-3])

        for module in moduleNames:
            self.methodList.addItem(module)

    def updatePostMethodList(self):
        self.postMethodList.clear()

        # import all modules in current directory and display their names
        moduleNames = []
        path = os.path.join(os.curdir, 'postpostprocessing')
        for f in os.listdir(path):
            if not os.path.isfile(os.path.join(path, f)):
                continue
            elif f == '__init__.py':
                continue
            elif f[-3:] != '.py':
                continue
            else:
                moduleNames.append(f[:-3])

        for module in moduleNames:
            self.postMethodList.addItem(module)

    def runPostprocessor(self, item):
        if not self.results:
            print 'runPostprocessor(): Error no result file loaded!'
            return

        if self.figureList.currentRow()>=0:
            self.grid.removeWidget(self.current_figures[self.figureList.currentRow()]['figure'])

        del self.current_figures[:]

        name = str(item.text())
        print 'PostProcessor() running: ', name

        module = __import__('.'.join(['postprocessing',name]))
        processor = getattr(getattr(module, name), name)()

        self.current_figures = processor.process(self.results)

        self.figureList.setFocus()
        self.figuresChanged.emit()
        
    def runPostPostprocessor(self, item):
        if not self.postResults:
            print 'runPostPostprocessor(): Error no post-result files loaded!'
            return

        if self.postFigureList.currentRow()>=0:
            self.grid.removeWidget(self.current_postFigures[self.postFigureList.currentRow()]['figure'])

        del self.current_postFigures[:]

        name = str(item.text())
        print 'PostPostProcessor() running: ', name

        module = __import__('.'.join(['postpostprocessing',name]))
        processor = getattr(getattr(module, name), name)()

        processFunc = processor.run
        self.current_postFigures = processFunc(self.postResults)

        self.postFigureList.setFocus()
        self.postFiguresChanged.emit()
    
    def updateFigureList(self):
        self.figureList.clear()
        for fig in self.current_figures:
            name = fig['name']
            self.figureList.addItem(name)

        self.figureList.setCurrentItem(self.figureList.item(0))

    def updatePostFigureList(self):
        self.postFigureList.clear()
        for fig in self.current_postFigures:
            name = fig['name']
            self.postFigureList.addItem(name)

        self.postFigureList.setCurrentItem(self.postFigureList.item(0))

    def currentFigureChanged(self, currItem, lastItem=None):
        if self.figureList.hasFocus():
        #if self.displayLeft == True:
            figures = self.current_figures
            figureList = self.figureList
        else:
            figures = self.current_postFigures
            figureList = self.postFigureList

        if self.lastFigure:
        #if lastItem:
            #oldWidget = figures[figureList.currentRow()]['figure']
            self.grid.removeWidget(self.lastFigure)
            self.lastFigure.setVisible(False)

        if currItem:
            figWidget = figures[figureList.currentRow()]['figure']
            self.grid.addWidget(figWidget, 1, 1, 5, 1)
            figWidget.setVisible(True)
            self.lastFigure = figWidget
        
    def switchDisplaySides(self):
        self.displayLeft = not self.displayLeft
        if self.displayLeft:
            self.actSwitch.setIcon(QtGui.QIcon('data/left_mode.png'))
            self.figureList.setFocus()
            self.currentFigureChanged(self.figureList.currentItem())
        else:
            self.actSwitch.setIcon(QtGui.QIcon('data/right_mode.png'))
            self.postFigureList.setFocus()
            self.currentFigureChanged(self.postFigureList.currentItem())

class PostProcessingModule:
    '''
    Base Class for Postprocessing Modules
    defines some basic functions that can later be vectorized
    '''
    def __init__(self):
        return

    def process(self, files):
        '''
        function that processes an array of result files
        This is an convinience wrapper for simple processor
        implementaion. Overload to add more functionality
        '''
        output = []
        for res in files:
            output.append(self.run(res))

        return output

    #def run(self, data):
        #return

    def extractSetting(self, dataList, name, moduleName, settingName):
        '''
        extracts settings from dataList
        '''
        return self.extract(dataList, ['modules', moduleName, settingName], name)

    def extractValues(self, dataList, name, valueName):
        '''
        extracts values for dataList
        '''
        return self.extract(dataList, ['results', valueName], name)

    def extract(self, dataList, keys, name):
        '''
        general extraction from regime that mathed name in partial
        '''
        return next((self._getSubDict(res, keys)\
                for res in dataList if name in res['regime name']),\
                None)

    def _getSubDict(self, topDict, keys):
        subDict = topDict
        for key in keys:
            subDict = subDict[key]
        return subDict

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

    def div(self, a, b):
        if b == 0:
            raise Exception('Division through 0 is impossible')
            return        
        return a/b

class PostPostProcessingModule:
    '''
    Base Class for Post-Post-Processing Modules
    '''
    def __init__(self):
        return


