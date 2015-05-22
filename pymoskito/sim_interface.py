# -*- coding: utf-8 -*-
''' simulator interface
    provides functions to manipulate settings of the simulator and
    to inspect its current state.
'''
import sys
import inspect
import copy

#Qt
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QStandardItemModel, QStandardItem, QItemDelegate, QComboBox

#own
from sim_core import Simulator

class SimulatorModel(QStandardItemModel):

    def __init__(self, parent=None):
        QStandardItemModel.__init__(self, parent=parent)

    def flags(self, index):
        if index.column() == 1:
            return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled
        else:
            return QtCore.Qt.ItemIsEnabled

class PropertyDelegate(QItemDelegate):
    """
    A delegate that manages all property settings.
    For now it uses a combobox for simulationModules and a standard
    delegate for the rest.
    """
    def __init__(self, parent =None):
        QItemDelegate.__init__(self, parent)
        self.comboDel = ComboDelegate()

    def createEditor(self, parent, option, index):
        if index.parent().isValid():
            return QItemDelegate.createEditor(self, parent, option, index)
        else:
            return self.comboDel.createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        if isinstance(editor, QComboBox):
            self.comboDel.setEditorData(editor, index)
        else:
            QItemDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        if isinstance(editor, QComboBox):
            self.comboDel.setModelData(editor, model, index)
        else:
            QItemDelegate.setModelData(self, editor, model, index)


class ComboDelegate(QItemDelegate):
    """
    A delegate that adds a combobox to a cell which provides
    all available types of this speciel simulationModule
    """

    def __init__(self, parent=None):
        QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItems(self.extractEntries(index))
        editor.currentIndexChanged.connect(self.currentIndexChanged)
        return editor

    def setEditorData(self, editor, index):
        name = index.model().itemFromIndex(index).text()
        editor.blockSignals(True)
        editor.setCurrentIndex(editor.findText(name)) 
        editor.blockSignals(False)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText())

    def currentIndexChanged(self, idx):
        self.commitData.emit(self.sender())

    def extractEntries(self, index):
        """
            extract all possible choices for the selected SimulationModule
        """
        entries = ['None']
        idx = index.model().index(index.row(), 0, QtCore.QModelIndex())
        modName = str(index.model().itemFromIndex(idx).text())
        module = __import__(modName)
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj):
                cName = name.split('.')[-1]
                if len(cName) > len(modName) and modName.capitalize() in cName:
                    entries.append(cName)
        
        return entries


class SimulatorView(QtGui.QTreeView):

    def __init__(self, parent=None):
        QtGui.QTreeView.__init__(self, parent)
        self.setItemDelegateForColumn(1, PropertyDelegate(self))
    
    def sizeHint(self):
        return QtCore.QSize(300, 150)

    def minimumSizeHint(self):
        return self.sizeHint()

class SimulatorInteractor(QtCore.QObject):

    #qt general
    simulationFinished = QtCore.pyqtSignal(dict)
    simulationFailed = QtCore.pyqtSignal(dict)
    simulationProgressChanged = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent)
        self._setupModel()
        
        self.sim = None
        self.simThread = QtCore.QThread()

    def _setupModel(self):
        self.target_model = SimulatorModel(self)
        self.target_model.itemChanged.connect(self.itemChanged)
        self.current_model = None

        #insert header
        self.target_model.setHorizontalHeaderLabels(['Property', 'Value'])

        #insert items
        self._setupModelItems()

    def _setupModelItems(self):
        #insert main items
        for module in Simulator.moduleList:
            newItems = []
            name = QStandardItem(module)
            value = QStandardItem('None')
            newItems = [name, value]
            self.target_model.appendRow(newItems)

        #insert settings
        for row in range(self.target_model.rowCount()):
            index = self.target_model.index(row, 0)
            self._addSettings(index)

    def _addSettings(self, index):
        parent = index.model().itemFromIndex(index)
        moduleName = str(parent.text())
        subModuleName = str(index.model().item(index.row(), 1).text())

        settings = self._readSettings(moduleName, subModuleName)
        for key, val in settings.iteritems():
            settingName = QStandardItem(key)
            settingValue = QStandardItem(str(val))
            parent.appendRow([settingName, settingValue])    
            
    def _readSettings(self, moduleName, className):
        ''' 
        reads all possible settings from a module
        '''
        simModule = __import__(moduleName)
        if not hasattr(simModule, className):
            return {}

        specificSimModule = getattr(simModule, className)
        if not hasattr(specificSimModule, 'settings'):
            return {}
        
        return specificSimModule.settings

    def itemChanged(self, item):
        if item.parent():
            return

        idx = item.index()
        modItem = idx.model().item(idx.row())

        #delete all old settings
        modItem.removeRows(0, modItem.rowCount())

        #insert new settings
        self._addSettings(modItem.index())

        return

    def _getSettings(self, model, moduleName):
        item = model.findItems(moduleName).pop(0)

        settings = {}
        for row in range(item.rowCount()):
            propName = str(item.child(row, 0).text())
            propVal = None
            #TODO this is not the good way
            if propName == 'Method':
                propVal = str(item.child(row, 1).text())
            else:
                valStr = str(item.child(row, 1).text())
                if '[' in valStr:
                    #parse vector
                    propVal = [float(x) for x in valStr[1:-1].split(',')]
                else:
                    #parse skalar
                    propVal = float(valStr)

            settings.update({propName: propVal})

        return settings

    def _setupSimlator(self, model):
        sim = Simulator()
   
        # setup simulation Modules
        for row in range(model.rowCount()):
            # build correct object and add it to the simulator
            moduleItem = model.item(row, 0)
            moduleName = str(moduleItem.text())
            subModuleItem = model.item(row, 1)
            module = __import__(str(moduleItem.text()))
            subName = str(subModuleItem.text())

            settings = {}
            if subName != 'None':
                subModule = getattr(module, str(subModuleItem.text()))
                slot = None
                if moduleName == 'solver':
                    slot = subModule(sim.model.getOutputDimension(), sim.model.stateFunc)
                elif moduleName == 'disturbance':
                    slot = subModule(sim.model.getOutputDimension())
                elif moduleName == 'sensor':
                    slot = subModule(sim.model.getOutputDimension())
                elif moduleName == 'trajectory':
                    cOrder = 0
                    fOrder = 0
                    if hasattr(sim, 'controller'):
                        cOrder = sim.controller.getOrder()
                    if hasattr(sim, 'feedforward'):
                        fOrder = sim.feedforward.getOrder()
                    slot = subModule(max([cOrder, fOrder]))
                else:
                    slot = subModule()

                setattr(sim, moduleName, slot)
                self.simModules.append(slot)

                # get settings for module and apply them
                settings = self._getSettings(self.target_model, moduleItem.text())
                settings.update({'type': subName})
                setattr(getattr(sim, moduleName), 'settings', settings)

            # store settings in simData
            self.simData['modules'].update({moduleName: settings})

        return sim

    def setRegime(self, reg):
        if reg is None:
            return
        if isinstance(reg, list):
            print 'setRegime(): only one allowed!'
            return

        self._applyRegime(reg)

    def _applyRegime(self, reg):
        '''
        sets all module settings to those provided in the regime
        '''
        if reg['clear previous']:
            #delete all items
            self.target_model.removeRows(0, self.target_model.rowCount())

            #load module defaults
            self._setupModelItems()

        #overwrite all settings with the provided ones
        for moduleName, value in reg.iteritems():
            if moduleName not in Simulator.moduleList:
                continue

            moduleItem = self.target_model.findItems(moduleName).pop(0)
            moduleType = value['type']
        
            moduleIndex = moduleItem.index()
            moduleTypeIndex = moduleIndex.model().index(moduleIndex.row(), 1)
            moduleIndex.model().setData(moduleTypeIndex, moduleType)
            #due to signal connections, default settings are loaded automatically in the back

            #overwrite specific settings
            for key, val in value.iteritems():
                if key == 'type':
                    continue

                found = False
                for row in range(moduleItem.rowCount()):
                    if str(moduleItem.child(row, 0).text()) == key:
                        valueIndex = self.target_model.index(row, 1, moduleIndex)
                        self.target_model.setData(valueIndex, str(val))
                        found = True
                        break
                    
                if not found:
                    print '_applyRegime(): setting ', key, 'not available for ', moduleType
                    continue



    def runSimulation(self):
        self.simData = {'modules': {}}

        #copy settings from target model
        self.current_model = copy.deepcopy(self.target_model)

        #create and setup simulator
        self.simModules = []
        self.sim = self._setupSimlator(self.target_model)

        #setup threads
        for module in self.simModules:
            module.moveToThread(self.simThread)

        self.sim.moveToThread(self.simThread)
        self.simThread.started.connect(self.sim.run)
        self.sim.finished.connect(self.simFinished)
        self.sim.failed.connect(self.simFailed)
        self.sim.timeChanged.connect(self.simulationStateChanged)
        self.endTime = self.sim.solver.settings['end time']
        self.lastProgress = 0

        #run
        self.simThread.start()

    def simulationStateChanged(self, t):
        '''
        calculate overall progress
        '''
        progress = int(t/self.endTime * 100)
        if progress != self.lastProgress:
            self.simulationProgressChanged.emit(progress)
            self.lastProgress = progress

    def _simAftercare(self):
        #stop thread
        self.simThread.quit()

        #delete modules
        for module in self.simModules:
            del(module)

        del(self.sim)

    def _postprocessing(self):
        #calc main error
        a = 'model_output.0'
        b = 'trajectory_output.0'
        c = 'observer_output.0'
        d = 'model_output.2'
        e = 'observer_output.2'
        self.simData['results'].update({'e ':self._getDiff(b, a)})
        self.simData['results'].update({'epsilon_o':self._getDiff(a, c)})
        self.simData['results'].update({'epsilon_o2':self._getDiff(d, e)})

    def _getDiff(self, a, b):
        data = self.simData['results']
        return [(data[a][i] - data[b][i]) for i in range(len(data['simTime']))]
        
    @QtCore.pyqtSlot(dict)
    def simFinished(self, data):
        self.simData.update({'results':copy.deepcopy(data)})
        self._simAftercare()
        self._postprocessing()
        self.simulationFinished.emit(self.simData)

    @QtCore.pyqtSlot(dict)
    def simFailed(self, data):
        self.simData.update({'results':copy.deepcopy(data)})
        self._simAftercare()
        self._postprocessing()
        self.simulationFailed.emit(self.simData)
