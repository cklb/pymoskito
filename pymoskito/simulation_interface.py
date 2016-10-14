# -*- coding: utf-8 -*-
""" simulator interface
    provides functions to manipulate settings of the simulator and
    to inspect its current state.
"""
import copy
import logging
import sys
import ast
import traceback

from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QModelIndex, QSize, QThread
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QItemDelegate, QComboBox, QTreeView

from . import simulation_modules
from .generic_simulation_modules import *
from .registry import get_registered_simulation_modules, get_simulation_module_class_by_name
from .simulation_core import Simulator, SimulationSettings, SimulationStateChange


class SimulatorModel(QStandardItemModel):
    def __init__(self, parent=None):
        QStandardItemModel.__init__(self, parent=parent)

    def flags(self, index):
        if index.column() == 1:
            return Qt.ItemIsEditable | Qt.ItemIsEnabled
        else:
            return Qt.ItemIsEnabled


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
            # TODO implement dropdown menu if property is a dict
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

    @staticmethod
    def extract_entries(index):
        """
        extract all possible choices for the selected SimulationModule
        """
        entries = ['None']
        idx = index.model().index(index.row(), 0, QModelIndex())
        sim_module_name = str(index.model().itemFromIndex(idx).text())
        sim_module = getattr(simulation_modules, sim_module_name)
        sub_modules = get_registered_simulation_modules(sim_module)
        for sub_module in sub_modules:
            entries.append(sub_module[1])

        return entries


class SimulatorView(QTreeView):
    def __init__(self, parent=None):
        QTreeView.__init__(self, parent)
        self.setItemDelegateForColumn(1, PropertyDelegate(self))

    def sizeHint(self):
        return QSize(300, 150)

    def minimumSizeHint(self):
        return self.sizeHint()


class SimulatorInteractor(QObject):
    """
    Class that interacts between the gui which controls the programs execution
    and the Simulator which handles the time step simulation
    """

    # signals
    simulation_finished = pyqtSignal(dict)
    simulation_failed = pyqtSignal(dict)
    simulationProgressChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self._logger = logging.getLogger(self.__class__.__name__)

        self.last_progress = 0
        self.end_time = 0
        self._setup_model()

        self._sim = None
        self._sim_settings = None
        self.simThread = QThread()
        self._sim_modules = {}
        self._sim_data = {'modules': {}}
        self._sim_state = None

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

        # build initialisation list
        setup_list = Simulator.module_list

        # TODO remove the next lines
        # complete sorting therefore add observer, sensor and so on again
        setup_list.append("Trajectory")
        setup_list.remove("Trajectory")

        # insert main items
        for module in setup_list:
            name = QStandardItem(module)
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
        for key, val in settings.items():
            setting_name = QStandardItem(key)
            setting_value = QStandardItem(str(val))
            parent.appendRow([setting_name, setting_value])

    def _read_settings(self, module_name, sub_module_name):
        """
        reads the public settings from a simulation module
        """
        module_cls = getattr(simulation_modules, module_name)
        sub_module_cls = get_simulation_module_class_by_name(module_cls, sub_module_name)
        return sub_module_cls.public_settings

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

        # TODO this is not the good way --> switch to pyqtgraphs implementation
        settings = OrderedDict()
        for row in range(item.rowCount()):
            property_name = str(item.child(row, 0).text())
            property_val_str = str(item.child(row, 1).text())

            if "np." in property_val_str or "numpy." in property_val_str:
                self._logger.warn("In module '" + module_name + "' and property '" + property_name + "'"
                                  " a numpy-object was detected. Only standard python types are supported!")
            elif "pi" in property_val_str or "Pi" in property_val_str or "PI" in property_val_str:
                property_val = np.pi
            elif (("exp(" in property_val_str and property_val_str[-1] == ")")
                  or ("e^(" in property_val_str and property_val_str[-1] is ")")):
                tmp = property_val_str[:-1]  # cut off last bracket
                tmp = tmp.replace("exp(", "")
                tmp = tmp.replace("e^(", "")
                try:
                    property_val = ast.literal_eval(tmp)
                    property_val = np.exp(property_val)
                except ValueError:
                    property_val = property_val_str
            else:
                try:
                    property_val = ast.literal_eval(property_val_str)
                except ValueError:
                    # property_val_str can not be parsed by literal_eval
                    # save string in dict
                    property_val = property_val_str

            settings.update({property_name: property_val})

        return settings

    def _setup_sim_modules(self, model):
        """
        setup simulation Modules
        :param model: model holding the public settings of each module
        """

        for row in range(model.rowCount()):
            # build correct object and add it to the simulator
            module_item = model.item(row, 0)
            module_name = str(module_item.text())
            sub_module_item = model.item(row, 1)
            sub_module_name = str(sub_module_item.text())

            if sub_module_name == 'None':
                continue

            # get class
            module_cls = getattr(simulation_modules, module_name)
            sub_module_cls = get_simulation_module_class_by_name(module_cls, sub_module_name)

            # get public settings for module
            settings = self._get_settings(self.target_model, module_item.text())
            settings.update({"type": sub_module_name})
            settings.update({"modules": self._sim_modules})

            # append special settings
            if module_name == "Solver":
                self._sim_settings = SimulationSettings(settings["start time"],
                                                        settings["end time"],
                                                        settings["measure rate"])

            # build object
            slot = sub_module_cls(settings)

            # add to simulation modules
            self._sim_modules.update({module_name: slot})

            # store settings
            self._sim_data['modules'].update({module_name: settings})

    def set_regime(self, reg):
        if reg is None:
            return
        if isinstance(reg, list):
            self._logger.error("setRegime(): only scalar input allowed!")
            return

        self._apply_regime(reg)

    def _apply_regime(self, reg):
        """
        sets all module settings to those provided in the regime
        """
        if reg["clear previous"]:
            # delete all items
            self.target_model.removeRows(0, self.target_model.rowCount())

            # load module defaults
            self._setup_model_items()

        # overwrite all settings with the provided ones
        for module_name, value in reg.items():
            if module_name == "Name" or module_name == "clear previous":
                continue

            # sanity check
            module_cls = getattr(simulation_modules, module_name)
            if not module_cls:
                raise AttributeError("_apply_regime(): No module called {0}".format(module_name))

            items = self.target_model.findItems(module_name)
            # items = self.target_model.findItems(string.capwords(module_name))
            if not len(items):
                raise ValueError("_apply_regime(): No item in List called {0}".format(module_name))
            module_item = items.pop(0)
            module_type = value["type"]

            # sanity check
            sub_module_cls = get_simulation_module_class_by_name(module_cls, module_type)

            if not sub_module_cls:
                raise AttributeError("_apply_regime(): No sub-module called {0}".format(module_type))

            module_index = module_item.index()
            module_type_index = module_index.model().index(module_index.row(), 1)
            module_index.model().setData(module_type_index, module_type)
            # due to signal connections, default settings are loaded automatically in the back

            # overwrite specific settings
            for key, val in value.items():
                if key == "type":
                    continue

                found = False
                for row in range(module_item.rowCount()):
                    if str(module_item.child(row, 0).text()) == key:
                        value_idx = self.target_model.index(row, 1, module_index)
                        self.target_model.setData(value_idx, str(val))
                        found = True
                        break

                if not found:
                    self._logger.error("_applyRegime(): setting {0} not available for {1}".format(key, module_type))
                    continue

    def run_simulation(self):
        """
        entry hook for time step simulation
        - use settings to create modules in simulation loop
        - move them into an extra thread
        - start simulation
        """
        # setup simulation modules
        self._setup_sim_modules(self.target_model)

        # setup simulator
        self._sim = Simulator(self._sim_settings, self._sim_modules)
        self._sim.moveToThread(self.simThread)

        # setup simulation modules
        for module in self._sim_modules.values():
            module.moveToThread(self.simThread)

        # setup signal connections
        self.simThread.started.connect(self._sim.run)
        self._sim.state_changed.connect(self.simulation_state_changed)
        self._sim.finished.connect(self.simThread.quit)
        self.simThread.finished.connect(self.sim_finished)
        self.end_time = self._sim_settings.end_time

        # run
        self.simThread.start()

    @pyqtSlot(SimulationStateChange)
    def simulation_state_changed(self, state_change):
        """
        slot for simulation state changes

        :param state_change: see :cls:SimulationStateChange
        """
        self._logger.debug("simulation state change '{}'".format(state_change.type))

        if state_change.type == "start":
            self._sim_state = "running"
        elif state_change.type == "time":
            self._logger.debug("reached simulation time {0}".format(state_change.t))
            progress = int(state_change.t / self._sim_settings.end_time * 100)
            if progress != self.last_progress:
                self._logger.info("simulation reached {0}%".format(progress))
                self.simulationProgressChanged.emit(progress)
                self.last_progress = progress
        elif state_change.type == "abort":
            self._sim_state = "aborted"
            self._sim_data.update({'results': copy.deepcopy(state_change.data)})
            self._logger.error("simulation has been aborted due to an exception:", exc_info=state_change.info)
            self._logger.info("check your configuration")
        elif state_change.type == "finish":
            self._sim_state = "finished"
            self._sim_data.update({'results': copy.deepcopy(state_change.data)})
        else:
            self._logger.error("simulation_state_changed(): ERROR Unknown state {0}".format(state_change.type))

    def _sim_aftercare(self):
        # delete modules
        for module in self._sim_modules.keys():
            del module
        self._sim_modules = {}

        # don't disconnect signals in debug-mode
        if sys.gettrace() is None:
            self.simThread.started.disconnect(self._sim.run)
            self._sim.state_changed.disconnect(self.simulation_state_changed)
            self._sim.finished.disconnect(self.simThread.quit)
            self.simThread.finished.disconnect(self.sim_finished)

        # delete simulator
        del self._sim

    def _postprocessing(self):
        """
        calculation of some basic metrics for quick judging of simulation results
        """

        # TODO make this able to calc error for vector-like model output
        # control and observer error
        if "Trajectory" in self._sim_data["results"]:
            # take only the first column
            c_error = self._get_result_by_name("Trajectory")[:, :, 0] - self._get_result_by_name("Model")[:, :, 0]
            self._sim_data['results'].update(control_error=c_error)
        if "Observer" in self._sim_data["results"]:
            o_error = self._get_result_by_name("Solver") - self._get_result_by_name("Observer")
            self._sim_data['results'].update(observer_error=o_error)

    def _get_result_by_name(self, name):
        return self._sim_data["results"][name]

    def sim_finished(self):
        """
        slot to be called when the simulator reached the target time or aborted
        simulation due to an error
        """
        self._sim_aftercare()
        self._postprocessing()

        assert self._sim_state == "finished" or self._sim_state == "aborted"
        if self._sim_state == "finished":
            self.simulation_finished.emit(self._sim_data)
        else:
            self.simulation_failed.emit(self._sim_data)
