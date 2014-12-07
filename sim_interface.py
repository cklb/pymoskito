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


class SimulatorInteractor(QtCore.QObject):


    #qt general
    simulationFinished = pyqtSignal()
    simulationFailed = pyqtSignal()
    newData = pyqtSignal()

    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent)
        self._setupModel()
        self.sim = None

    def _setupModel(self):
        self.target_model = SimulatorModel(self)
        self.target_model.itemChanged.connect(self.itemChanged)
        self.current_model = None

        #insert main items
        for module in Simulator.moduleList:
            newItems = []
            name = QStandardItem(module)
            if module == 'model':
                value = QStandardItem('BallBeamModel')
            else:
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
            if not isinstance(val, list):
                val = [val]

            settingValues = []
            for data in val:
                settingValues.append(QStandardItem(str(data)))

            settingValues.insert(0, settingName)
            parent.appendRow(settingValues)    
            
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

    def _getSettings(self, model, module):
        item = model.findItem(module)

        settings = {}
        for row in range(item.rowCount()):
            settings.update({ \
                    str(item.child(row, 0).text()): str(item.child(row, 1).text())\
                    })

        return settings

    def _setupSimlator(self):
        self.sim = Simulator(self)
    
        # setup simulation Modules
        for row in range(self.current_model.rowCount()):
            # build correct object and add it the the simulator
            moduleItem = self.current_model.item(row, 0)
            subModuleItem = self.current_model.item(row, 1)
            module = __import__(str(moduleItem.text()))
            subModule = getattr(module, str(subModuleItem.text()))
            self.sim.setattr(str(item.text()), subModule())

            # get settings for module and apply them
            settings = self._getSettings(self.target_model, module)
            getattr(self.sim, module).setattr('settings', settings)

            # store settings in simData
            self.simData.update({'settings': {module, settings}})


    def runSimulation(self):
        self.simData = {}

        #copy settings from target model
        self.current_model = copy.deepcopy(self.target_model)

        #create and setup simulator
        self._setupSimlator()

        #setup threads
        self.simThread = QThread()
        self.sim.moveToThread(self.simThread)
        self.simThread.started.connect(self.simulator.run)
        self.sim.finished.connect(self.simFinished)
        self.sim.failed.connect(self.simFailed)

        #run
        self.simThread.start()

    def _simAftercare(self):
        #stop thread
        self.simThread.quit()
        
        #copy result data
        self.simData.update({'results':copy.deepcopy(self.sim.getValues())})
        
        #delete simulator
        del(self.sim)

    def simFinished(self):
        self._simAftercare()
        self.simulationFinished.emit()

    def simFailed(self):
        self._simAftercare()
        self.simulationFailed.emit()
