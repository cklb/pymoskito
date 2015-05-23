# -*- coding: utf-8 -*-
""" simulator interface
    provides functions to manipulate settings of the simulator and
    to inspect its current state.
"""
import inspect
import copy

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QStandardItemModel, QStandardItem, QItemDelegate, QComboBox

from simulation_modules import SimulationModule
from simulation_core import Simulator


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

    def __init__(self, parent=None):
        QItemDelegate.__init__(self, parent)
        self.comboDel = ComboDelegate()

    def createEditor(self, parent, option, index):
        if index.parent().isValid():
            # item has a parent -> no SimulationModule
            return QItemDelegate.createEditor(self, parent, option, index)
        else:
            # no parent -> top of hierarchy
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
    A delegate that adds a combobox to cells that lists
    all available types of Subclasses of SimulationModule
    """

    def __init__(self, parent=None):
        QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItems(self.extract_entries(index))
        editor.currentIndexChanged.connect(self.current_index_changed)
        return editor

    def setEditorData(self, editor, index):
        name = index.model().itemFromIndex(index).text()
        editor.blockSignals(True)
        editor.setCurrentIndex(editor.findText(name))
        editor.blockSignals(False)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText())

    def current_index_changed(self, idx):
        self.commitData.emit(self.sender())

    def extract_entries(self, index):
        """
        extract all possible choices for the selected SimulationModule
        """
        entries = ['None']
        idx = index.model().index(index.row(), 0, QtCore.QModelIndex())
        sim_module_name = str(index.model().itemFromIndex(idx).text())
        sim_module = next((cls for cls in SimulationModule.__subclasses__() if cls.__name__ == sim_module_name),
                          None)
        for sub_module in sim_module.__subclasses__():
            entries.append(sub_module.__name__)

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
    # qt general
    simulationFinished = QtCore.pyqtSignal(dict)
    simulationFailed = QtCore.pyqtSignal(dict)
    simulationProgressChanged = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent)
        self.last_progress = 0
        self.end_time = 0
        self._setup_model()

        self.sim = None
        self.simThread = QtCore.QThread()
        self.sim_modules = []
        self.sim_data = {'modules': {}}

    def _setup_model(self):
        # create model
        self.target_model = SimulatorModel(self)
        self.target_model.itemChanged.connect(self.item_changed)

        # insert header
        self.target_model.setHorizontalHeaderLabels(['Property', 'Value'])

        # insert items
        self._setup_model_items()

    def _setup_model_items(self):
        """
        fill model with items corresponding to all predefined SimulationModules
        """
        # get all integrated simulation modules
        sim_modules = [cls for cls in SimulationModule.__subclasses__()]

        # insert main items
        for module in sim_modules:
            name = QStandardItem(module.__name__)
            value = QStandardItem('None')
            new_items = [name, value]
            self.target_model.appendRow(new_items)

        # insert settings
        for row in range(self.target_model.rowCount()):
            index = self.target_model.index(row, 0)
            self._add_settings(index)

    def _add_settings(self, index):
        parent = index.model().itemFromIndex(index)
        module_name = str(parent.text())
        sub_module_name = str(index.model().item(index.row(), 1).text())
        if sub_module_name == 'None':
            return

        settings = self._read_settings(module_name, sub_module_name)
        for key, val in settings.iteritems():
            setting_name = QStandardItem(key)
            setting_value = QStandardItem(str(val))
            parent.appendRow([setting_name, setting_value])

    def _read_settings(self, module_name, sub_module_name):
        """
        reads the public settings from a simulation module
        """
        module = self._get_derived_class_by_name(SimulationModule, module_name)
        sub_module = self._get_derived_class_by_name(module, sub_module_name)
        return sub_module.public_settings

    def _get_derived_class_by_name(self, parent_cls, name):
        """
        helper function
        :param parent_cls: parent class
        :param name: name of derived class
        :return: derived class
        """
        return next((cls for cls in parent_cls.__subclasses__() if cls.__name__ == name),
                    None)

    def item_changed(self, item):
        if item.parent():
            return

        idx = item.index()
        module_item = idx.model().item(idx.row())

        # delete all old settings
        module_item.removeRows(0, module_item.rowCount())

        # insert new settings
        self._add_settings(module_item.index())

        return

    def _get_settings(self, model, module_name):
        item = model.findItems(module_name).pop(0)

        settings = {}
        for row in range(item.rowCount()):
            property_name = str(item.child(row, 0).text())
            # TODO this is not the good way --> use predefined types
            if property_name == 'Method':
                prop_val = str(item.child(row, 1).text())
            else:
                val_str = str(item.child(row, 1).text())
                if '[' in val_str:
                    # parse vector
                    prop_val = [float(x) for x in val_str[1:-1].split(',')]
                else:
                    # parse scalar
                    prop_val = float(val_str)

            settings.update({property_name: prop_val})

        return settings

    def _setup_simulator(self, model):
        sim = Simulator(self)

        # setup simulation Modules
        for row in range(model.rowCount()):
            # build correct object and add it to the simulator
            module_item = model.item(row, 0)
            module_name = str(module_item.text())
            sub_module_item = model.item(row, 1)
            sub_module_name = str(sub_module_item.text())

            if sub_module_name == 'None':
                continue

            # get class
            module_cls = self._get_derived_class_by_name(SimulationModule, module_name)
            sub_module_cls = self._get_derived_class_by_name(module_cls, sub_module_name)

            # get public settings for module
            settings = self._get_settings(self.target_model, module_item.text())
            settings.update({"type": sub_module_name})

            # append special settings
            if module_name == "solver":
                pass
            elif module_name == "disturbance":
                pass
            elif module_name == "sensor":
                pass
            elif module_name == "trajectory":
                control_order = 0
                feedforward_order = 0
                if hasattr(sim, 'controller'):
                    control_order = sim.controller.input_order()
                if hasattr(sim, 'feedforward'):
                    feedforward_order = sim.feedforward.input_order()
                settings["differential_order"] = max([control_order, feedforward_order])

            # build object
            slot = sub_module_cls(settings)

            # add to simulator
            setattr(sim, module_name, slot)
            self.sim_modules.append(slot)

            # store settings
            self.sim_data['modules'].update({module_name: settings})

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
            self._setup_model_items()

        #overwrite all settings with the provided ones
        for moduleName, value in reg.iteritems():
            if moduleName not in Simulator.module_list:
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

    def run_simulation(self):
        """
        entry hook for timestep simulation
        - use settings to create modules in simulation loop
        - move them into an extra thread
        - start simulation
        """
        # create and setup simulator
        self.sim = self._setup_simulator(self.target_model)

        # setup threads
        for module in self.sim_modules:
            module.moveToThread(self.simThread)

        self.sim.moveToThread(self.simThread)
        self.simThread.started.connect(self.sim.run)
        self.sim.finished.connect(self.sim_finished)
        self.sim.failed.connect(self.sim_failed)
        self.sim.timeChanged.connect(self.simulation_state_changed)
        self.end_time = self.sim.solver.settings['end time']

        # run
        self.simThread.start()

    def simulation_state_changed(self, t):
        """
        calculate overall progress
        """
        progress = int(t / self.end_time * 100)
        if progress != self.last_progress:
            self.simulationProgressChanged.emit(progress)
            self.last_progress = progress

    def _sim_aftercare(self):
        # stop thread
        self.simThread.quit()

        # delete modules
        for module in self.sim_modules:
            del module

        del self.sim

    def _postprocessing(self):
        # calc main error
        a = 'model_output.0'
        b = 'trajectory_output.0'
        c = 'observer_output.0'
        d = 'model_output.2'
        e = 'observer_output.2'
        self.sim_data['results'].update({'e ': self._getDiff(b, a)})
        self.sim_data['results'].update({'epsilon_o': self._getDiff(a, c)})
        self.sim_data['results'].update({'epsilon_o2': self._getDiff(d, e)})

    def _getDiff(self, a, b):
        data = self.sim_data['results']
        return [(data[a][i] - data[b][i]) for i in range(len(data['simTime']))]

    @QtCore.pyqtSlot(dict)
    def sim_finished(self, data):
        self.sim_data.update({'results': copy.deepcopy(data)})
        self._sim_aftercare()
        self._postprocessing()
        self.simulationFinished.emit(self.sim_data)

    @QtCore.pyqtSlot(dict)
    def sim_failed(self, data):
        self.sim_data.update({'results': copy.deepcopy(data)})
        self._sim_aftercare()
        self._postprocessing()
        self.simulationFailed.emit(self.sim_data)
