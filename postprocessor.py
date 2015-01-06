# -*- coding: utf-8 -*-

#pyqt
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSignal

#std
import os

#own
import settings as st

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
        print 'PostProcessor() running: ', name

        module = __import__('.'.join(['postprocessing',name]))
        processor = getattr(getattr(module, name), name)()

        self.current_figures = processor.process(self.results)

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

        processFunc = processor.run
        self.current_metaFigures = processFunc(self.postResults)

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
        return

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

class PostProcessingModule(ProcessingModule):
    '''
    Base Class for Postprocessing Modules
    defines some basic functions that can later be vectorized
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
        '''
        y = data['results']['model_output.0']
        yd = data['results']['trajectory_output.0']
        dt = 1.0/data['modules']['solver']['measure rate']

        if not data['results']['finished']:
            L1NormITAE = None
        else:
            L1NormITAE = 0
            for idx, val in enumerate(y):
                # Variante 1
                L1NormITAE += abs(yd[idx] - val)*dt*(idx*dt)
                # Variante 2
                # L1NormITAE += abs(yd[idx] - val - (y[-1] - yd[-1]))*dt*(idx*dt)
        return L1NormITAE
        
    def calcL1NormAbs(self, data):
        '''
        this function calculate the L1 Norm 
        (absolute criterium)
        '''
        y = data['results']['model_output.0']
        yd = data['results']['trajectory_output.0']
        dt = 1.0/data['modules']['solver']['measure rate']
        
        if not data['results']['finished']:
            L1NormAbs = None
        else:
            L1NormAbs = 0
            for idx, val in enumerate(y):
                # Variante 1 (bisher implementiert)
                L1NormAbs += abs(yd[idx] - val)*dt
                # Variante 2 (implementierung nach Wikipedia)
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
        
        fileName = os.path.join(filePath, regimeName)
        with open(fileName+'.pof', 'w') as f: #POF - Postprocessing Output File
            f.write(repr(output))
        
        figure.savefig(fileName + '.png')
        #figure.savefig(fileName + '.pdf')
        #figure.savefig(fileName + '.svg')

class MetaProcessingModule(ProcessingModule):
    '''
    Base Class for Meta-Processing Modules
    '''
    def __init__(self):
        ProcessingModule.__init__(self)
        return
    
    def plotSettings(self, axes, titel, grid, xlabel, ylabel):
        axes.set_title(titel, size=st.title_size)
        if grid == True:
            axes.grid(color='#ababab', linestyle='--')
        axes.set_xlabel(xlabel, size=st.label_size)
        axes.set_ylabel(ylabel, size=st.label_size)
        axes.legend(fontsize='small')

        
        return axes
    
    def plotVariousController(self, dic, axes, x, y, typ):
        
        width = 0.1
        counter = 0
        x_all = []
        
        for i in dic:
            controller = i
            xList = dic[i][x]
            yList = dic[i][y]
            
            #add times to t_all
            for j in xList:
                if x_all.count(j) == 0:
                    x_all.append(j)
            
#            # replace None with 0
#            for index, value in enumerate(yList):
#                if value == None:
#                    yList[index] = 0
            if typ == 'line':
                axes.plot(xList,\
                        yList,\
                        'o-',\
                        label=controller,\
                        color=st.color_cycle[controller])
            if typ == 'bar':
                #remove all None from xList and yList
                xList[:] = [i for i in xList if i]                
                yList[:] = [i for i in yList if i]
                # correction for the position of the bar
                xList[:] = [k + width*counter for k in xList]
                
                axes.bar(xList,\
                        yList,\
                        width,\
                        label=controller,\
                        color=st.color_cycle[controller])
            
            counter += 1            
        
        
        x_all.sort()
        #remove all None from x_all
        x_all[:] = [i for i in x_all if i]
        # does not work for all constellations
        spacing = (x_all[-1] - x_all[0])/(len(x_all) - 1)
        x_all.append(spacing + x_all[-1])
        x_all.append(x_all[0] - spacing)
        x_all.sort()

        x_all_label = [r'$' + str(i) + '$' for i in x_all]
        
        counter -= 1
        if typ=='bar':
            x_all[:] = [i + width*counter for i in x_all]

        axes.set_xticks(x_all)
        axes.set_xticklabels(x_all_label)
        
        return axes
            
    
    def createDictionary(self, data):
        '''
        return a dictionary which contain all 
        relevant data, sorted by Controller
        content:
            - tr                rise-time (Anstiegszeit)
            - tanr              correction time (Anregelzeit)
            - to                overshoot time (Überschwingzeit)
            - do                overshoot
            - doPercent         overshoot in %
            - teps              damping time (Ausregelzeit)
            - L1NormAbs         L1-Norm absolute
            - L1NormITAE        L1-Norm absolute with time weighting
            - t_diff            td - delta_t
            - delta_t           delta_t from trajectory
            - control_deviation control_deviation (Regelabweichung)
            - poles             poles from controller
            - sigma             standard deciation of GaussianNoiseDesturbance
            - frequency         frequency from harmonic trajectory
            - M                 mass of the ball
            - Jb                moment of inertia of the ball
            - delay             time delay of DeadTimeSensor
        '''
        dic = {}
        
        for elem in data:
            # data from postprocessing
            tr = self._getSubElement(elem, ['tr'])
            tanr = self._getSubElement(elem, ['tanr'])
            to = self._getSubElement(elem, ['to'])
            do = self._getSubElement(elem, ['do'])
            doPercent = self._getSubElement(elem, ['doPercent'])
            teps = self._getSubElement(elem, ['teps'])
            L1NormAbs = self._getSubElement(elem, ['L1NormAbs'])
            L1NormITAE = self._getSubElement(elem, ['L1NormITAE'])
            t_diff = self._getSubElement(elem, ['t_diff'])
            delta_t = self._getSubElement(elem, ['delta_t'])
            control_deviation = self._getSubElement(elem, ['control_deviation'])
            
            #data from modules
            #controller            
            controllerName = self._getSubElement(elem, ['modules', 'controller', 'type'])
            poles = self._getSubElement(elem, ['modules', 'controller', 'poles'])
            #disturbance
            sigma = self._getSubElement(elem, ['modules', 'disturbance', 'sigma'])
            #trajectory
            frequency = self._getSubElement(elem, ['modules', 'trajectory', 'Frequency'])
            #model
            M = self._getSubElement(elem, ['modules', 'model', 'M'])
            Jb = self._getSubElement(elem, ['modules', 'model', 'Jb'])
            #sensor
            delay = self._getSubElement(elem, ['modules', 'sensor', 'delay'])
            
            if dic.has_key(controllerName):
                dic[controllerName]['tr'].append(tr)
                dic[controllerName]['tanr'].append(tanr)
                dic[controllerName]['to'].append(to)
                dic[controllerName]['do'].append(do)
                dic[controllerName]['doPercent'].append(doPercent)
                dic[controllerName]['teps'].append(teps)
                dic[controllerName]['L1NormAbs'].append(L1NormAbs)
                dic[controllerName]['L1NormITAE'].append(L1NormITAE)
                dic[controllerName]['t_diff'].append(t_diff)
                dic[controllerName]['delta_t'].append(delta_t)
                dic[controllerName]['control_deviation'].append(control_deviation)
                dic[controllerName]['poles'].append(poles)
                dic[controllerName]['sigma'].append(sigma)
                dic[controllerName]['frequency'].append(frequency)
                dic[controllerName]['M'].append(M)
                dic[controllerName]['Jb'].append(Jb)
                dic[controllerName]['delay'].append(delay)
                
            else:
                dic.update({controllerName:{\
                                        'tr': [tr],\
                                        'tanr': [tanr],\
                                        'to': [to],\
                                        'do': [do],\
                                        'doPercent': [doPercent],\
                                        'teps': [teps],\
                                        'L1NormAbs': [L1NormAbs],\
                                        'L1NormITAE': [L1NormITAE],\
                                        't_diff': [t_diff],\
                                        'delta_t': [delta_t],\
                                        'control_deviation': [control_deviation],\
                                        'poles': [poles],\
                                        'sigma': [sigma],\
                                        'frequency': [frequency],\
                                        'M': [M],\
                                        'Jb': [Jb],\
                                        'delay': [delay],\
                                        }})
        return dic
    
    def _getSubElement(self, topDict, keys):
        subDict = topDict
        for key in keys:
            if subDict.has_key(key):
                subDict = subDict[key]
            else:
                return None
        return subDict
