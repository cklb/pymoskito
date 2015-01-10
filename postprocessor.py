# -*- coding: utf-8 -*-
import cPickle
import sys
import traceback

#pyqt
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSignal

#std
import os

#own
import settings as st
from tools import getSubValue

class PostProcessor(QtGui.QMainWindow):

    resultsChanged = pyqtSignal()
    figuresChanged = pyqtSignal()

    postResultsChanged = pyqtSignal()
    metaFiguresChanged = pyqtSignal()

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

        self.actReloadMetaMethods= QtGui.QAction(self)
        self.actReloadMetaMethods.setText('reload meta methods')
        self.actReloadMetaMethods.setIcon(QtGui.QIcon('data/reload.png'))
        self.actReloadMetaMethods.setDisabled(False)
        self.actReloadMetaMethods.triggered.connect(self.updateMetaMethodList)
        
        self.toolBar.addAction(self.actLoad)
        self.toolBar.addAction(self.actReloadMethods)
        
        self.toolBar.addWidget(self.spacer1)
        self.toolBar.addAction(self.actSwitch)
        self.toolBar.addWidget(self.spacer2)

        self.toolBar.addAction(self.actReloadMetaMethods)
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

        self.metaMethodList = QtGui.QListWidget(self)
        self.metaMethodList.itemDoubleClicked.connect(self.runMetaprocessor)
        self.updateMetaMethodList()
        
        self.postResultList = QtGui.QListWidget(self)
        self.postResultsChanged.connect(self.updatePostResultList)
        self.postResults = []
        self.delShortPost = QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Backspace), self.postResultList)
        self.delShortPost.activated.connect(self.removePostResultItem)

        self.metaFigureList = QtGui.QListWidget(self)
        self.metaFigureList.currentItemChanged.connect(self.currentFigureChanged)
        self.metaFiguresChanged.connect(self.updateMetaFigureList)
        self.current_metaFigures = []
        
        self.grid.addWidget(QtGui.QLabel('result files:'), 0, 0)
        self.grid.addWidget(self.resultList, 1, 0)
        self.grid.addWidget(QtGui.QLabel('postprocessors:'), 2, 0)
        self.grid.addWidget(self.methodList, 3, 0)
        self.grid.addWidget(QtGui.QLabel('figures:'), 4, 0)
        self.grid.addWidget(self.figureList, 5, 0)
        self.grid.addWidget(QtGui.QLabel('selected figure:'), 0, 1)
        self.grid.addWidget(QtGui.QLabel('postprocessor files:'), 0, 2)
        self.grid.addWidget(self.postResultList, 1, 2)
        self.grid.addWidget(QtGui.QLabel('metaprocessors:'), 2, 2)
        self.grid.addWidget(self.metaMethodList, 3, 2)
        self.grid.addWidget(QtGui.QLabel('figures:'), 4, 2)
        self.grid.addWidget(self.metaFigureList, 5, 2)

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
        with open(fileName, 'rb') as f:
            self.results.append(cPickle.load(f))
            #self.results.append(eval(f.read()))

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

    def updateMetaMethodList(self):
        self.metaMethodList.clear()

        # import all modules in current directory and display their names
        moduleNames = []
        path = os.path.join(os.curdir, 'metaprocessing')
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
            self.metaMethodList.addItem(module)

    def runPostprocessor(self, item):
        if not self.results:
            print 'runPostprocessor(): Error no result file loaded!'
            return

        if self.figureList.currentRow()>=0:
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
        
    def runMetaprocessor(self, item):
        if not self.postResults:
            print 'runMetaprocessor(): Error no post-result files loaded!'
            return

        if self.metaFigureList.currentRow()>=0:
            self.grid.removeWidget(self.current_metaFigures[self.metaFigureList.currentRow()]['figure'])

        del self.current_metaFigures[:]

        name = str(item.text())
        print 'MetaProcessor() running: ', name

        module = __import__('.'.join(['metaprocessing',name]))
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
    
    def updateFigureList(self):
        self.figureList.clear()
        for fig in self.current_figures:
            name = fig['name']
            self.figureList.addItem(name)

        self.figureList.setCurrentItem(self.figureList.item(0))

    def updateMetaFigureList(self):
        self.metaFigureList.clear()
        for fig in self.current_metaFigures:
            name = fig['name']
            self.metaFigureList.addItem(name)

        self.metaFigureList.setCurrentItem(self.metaFigureList.item(0))

    def currentFigureChanged(self, currItem, lastItem=None):
        if self.figureList.hasFocus():
            figures = self.current_figures
            figureList = self.figureList
        else:
            figures = self.current_metaFigures
            figureList = self.metaFigureList

        if self.lastFigure:
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
            self.metaFigureList.setFocus()
            self.currentFigureChanged(self.metaFigureList.currentItem())

class ProcessingModule:
    '''
    Base Class for processing Modules
    defines some basic functions that can later be vectorized
    and extracting functionalities for datasets
    '''
    def __init__(self):
        self.name = self.__class__.__name__
        return

    def extractSetting(self, dataList, names, moduleName, settingName):
        '''
        extracts settings from dataList
        '''
        return self.extract(dataList, ['modules', moduleName, settingName], names)

    def extractValues(self, dataList, names, valueName):
        '''
        extracts values for dataList
        '''
        return self.extract(dataList, ['results', valueName], names)

    def extract(self, dataList, keys, names):
        '''
        general extraction from dataList 
        where the regime name contains all strings
        listed in names
        '''
        if not isinstance(names, list):
            names = [names]

        return next((self._getSubDict(result, keys)\
                for result in dataList if all(name in result['regime name'] for name in names)),\
                None)

    def _getSubDict(self, topDict, keys):
        subDict = topDict
        for key in keys:
            subDict = subDict[key]
        return subDict

class PostProcessingModule(ProcessingModule):
    '''
    Base Class for Postprocessing Modules
    '''
    def __init__(self):
        ProcessingModule.__init__(self)
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
        
    def calcL1NormITAE(self, data):
        '''
        this function calculate the L1 Norm  with a
        additional time weighting
        unit: m*s**2
        '''
        y = data['results']['model_output.0']
        yd = data['results']['trajectory_output.0']
        dt = 1.0/data['modules']['solver']['measure rate']

        if not data['results']['finished']:
            L1NormITAE = None
        else:
            L1NormITAE = 0
            for idx, val in enumerate(y):
                # version 1
                L1NormITAE += abs(yd[idx] - val)*dt*(idx*dt)
                # version 2 see also wikipedia
                # L1NormITAE += abs(yd[idx] - val - (y[-1] - yd[-1]))*dt*(idx*dt)
        return L1NormITAE
        
    def calcL1NormAbs(self, data):
        '''
        this function calculate the L1 Norm 
        (absolute criterium)
        unit: m*s
        '''
        y = data['results']['model_output.0']
        yd = data['results']['trajectory_output.0']
        dt = 1.0/data['modules']['solver']['measure rate']
        
        if not data['results']['finished']:
            L1NormAbs = None
        else:
            L1NormAbs = 0
            for idx, val in enumerate(y):
                # version 1
                L1NormAbs += abs(yd[idx] - val)*dt
                # version 2 see also wikipedia
                # L1NormAbs += abs(yd[idx] - val - (y[-1] - yd[-1]))*dt
        return L1NormAbs

    def writeOutputFiles(self, processorName, regimeName, figure, output):
        '''
        this function save calculated values
        in a POF (postprocessing output file) File
        and create pdf, png, svg datafiles from the plots        
        '''
        
        filePath = os.path.join(os.path.pardir, 'results', 'postprocessing', processorName)
        if not os.path.isdir(filePath):
            os.makedirs(filePath)
            
        if regimeName:
            fileName = os.path.join(filePath, regimeName)
            with open(fileName+'.pof', 'w') as f: #POF - Postprocessing Output File
                f.write(repr(output))
            
        if figure:
            figure.savefig(fileName + '.png')
            figure.savefig(fileName + '.pdf')
            figure.savefig(fileName + '.svg')


class MetaProcessingModule(ProcessingModule):
    '''
    Base Class for Meta-Processing Modules
    '''
    def __init__(self):
        ProcessingModule.__init__(self)
        return
    
    def sortLists(self, a, b):
        b = [x for (y, x) in sorted(zip(a, b))]
        a = sorted(a)
        return a, b

    def plotSettings(self, axes, titel, grid, xlabel, ylabel):
        axes.set_title(titel, size=st.title_size)
        if grid == True:
            axes.grid(color='#ababab', linestyle='--')
        axes.set_xlabel(xlabel, size=st.label_size)
        axes.set_ylabel(ylabel, size=st.label_size)
        axes.legend(fontsize='small')
        return axes
    
    def plotVariousController(self, source, axes, xPath, yPath, typ, xIndex=-1, yIndex=-1):
        '''
        plots y over x for all controllers
        '''

        width = 0.2
        counter = 0
        x_all = []
        
        for controller in source:
            xList = getSubValue(source[controller], xPath)
            yList = getSubValue(source[controller], yPath)
            xList, yList = self.sortLists(xList, yList)
            
            if xIndex >= 0:
                xList[:] = [x[xIndex] for x in xList]
            if yIndex >= 0:
                yList[:] = [y[yIndex] for y in yList]
            
            #add x values to x_all if there are not in x_all
            for val in xList:
                if val not in x_all:
                    x_all.append(val)            

            if typ == 'line':
                axes.plot(xList,\
                        yList,\
                        'o-',\
                        label=controller,\
                        color=st.color_cycle[controller])
            elif typ == 'bar':
                #remove all None from yList
                xList[:] = [x for x,y in zip(xList, yList) if y]
                yList[:] = [i for i in yList if i]
                
                # correction for the position of the bar
                xList[:] = [k + width*counter for k in xList]
                
                axes.bar(xList,\
                        yList,\
                        width,\
                        label=controller,\
                        color=st.color_cycle[controller])
                counter += 1            
                
                if len(x_all) > 1:
                    #remove all None from x_all
                    x_all.sort()
                    x_all[:] = [i for i in x_all if i]

                    # does not work for all constellations
                    spacing = (x_all[-1] - x_all[0])/(len(x_all) - 1)
                    x_all.append(spacing + x_all[-1])
                    x_all.append(x_all[0] - spacing)
                    x_all.sort()

                    #x_all_label = [r'$' + str(i) + '$' for i in x_all]
                    counter -= 1
                    if typ=='bar':
                        x_all[:] = [i + width*counter for i in x_all]

                    #axes.set_xticks(x_all)
                    #axes.set_xticklabels(x_all_label)
        
        return axes
    
    def writeOutputFiles(self, name, figure):
        '''
        this function create pdf, png, svg datafiles from the plots        
        '''
        filePath = os.path.join(os.path.pardir,\
                    'results', 'metaprocessing', self.name)
        if not os.path.isdir(filePath):
            os.makedirs(filePath)
            
        fileName = os.path.join(filePath, name)
            
        if figure:
            figure.savefig(fileName + '.png')
            #figure.savefig(fileName + '.pdf')
            #figure.savefig(fileName + '.svg')

