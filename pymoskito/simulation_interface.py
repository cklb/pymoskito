# -*- coding: utf-8 -*-
""" simulator interface
    provides functions to manipulate settings of the simulator and
    to inspect its current state.
"""
import copy
import logging
import sys
import ast
from collections import OrderedDict
import numpy as np

from PyQt5.QtCore import (
    Qt, QObject, pyqtSignal, pyqtSlot, QModelIndex, QSize, QThread, QVariant,
)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QItemDelegate, QComboBox, QTreeView

from . import simulation_modules
from .registry import (
    get_registered_simulation_modules, get_simulation_module_class_by_name
)
from .simulation_core import (
    Simulator, SimulationSettings, SimulationStateChange
)


class SimulatorModel(QStandardItemModel):
    def __init__(self, parent=None):
        QStandardItemModel.__init__(self, parent=parent)

    def flags(self, index):
        if index.column() == 1:
            return Qt.ItemIsEditable | Qt.ItemIsEnabled
        else:
            return Qt.ItemIsEnabled


class PropertyItem(QStandardItem):

    RawDataRole = Qt.UserRole + 1

    def __init__(self, data):
        QStandardItem.__init__(self)
        self._logger = logging.getLogger(self.__class__.__name__)
        self._data = data
        self._text = self._get_text(data)

    def type(self):
        return QStandardItem.UserType

    def _get_text(self, data):
        return str(data)

    def setData(self, Any, role=None, *args, **kwargs):
        if role == Qt.EditRole:
            try:
                self._data = ast.literal_eval(Any)
            except (SyntaxError, ValueError) as e:
                # print(e)
                self._logger.exception(e)
                return
            self._text = str(self._data)

        elif role == self.RawDataRole:
            self._data = Any
            self._text = self._get_text(Any)

        else:
            raise NotImplementedError

        self.emitDataChanged()

    def data(self, role=None, *args, **kwargs):
        if role == Qt.DisplayRole:
            return self._text
        elif role == Qt.EditRole:
            if isinstance(self._data, str):
                return "'" + self._text + "'"
            else:
                return self._text
        elif role == self.RawDataRole:
            return self._data

        else:
            return super().data(role, *args, **kwargs)


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
        model.setData(
            index,
            editor.currentText() if editor.currentText() != "None" else None,
            role=PropertyItem.RawDataRole)

    @pyqtSlot(int)
    def current_index_changed(self, idx):
        self.commitData.emit(self.sender())

    @staticmethod
    def extract_entries(index):
        """
        extract all possible choices for the selected SimulationModule
        """
        entries = ["None"]
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
    simulation_finalized = pyqtSignal(str, dict)
    simulationProgressChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self._logger = logging.getLogger(self.__class__.__name__)

        self.last_progress = 0
        self.end_time = 0
        self._setup_model()

        self._worker = None
        self._sim_settings = None
        self.simThread = QThread()
        self._sim_modules = {}
        self._sim_data = None
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

        # push init of Trajectory module to the end because it needs the
        # derivative orders of controller and feedforward
        setup_list.append("Trajectory")
        setup_list.remove("Trajectory")

        # insert main items
        for sim_module in setup_list:
            name = PropertyItem(sim_module)
            value = PropertyItem(None)
            new_items = [name, value]
            self.target_model.appendRow(new_items)

        # insert settings
        for row in range(self.target_model.rowCount()):
            index = self.target_model.index(row, 0)
            self._add_settings(index)

    def _add_settings(self, index):
        parent = index.model().itemFromIndex(index)
        child = index.model().item(index.row(), 1)
        module_name = parent.data(role=PropertyItem.RawDataRole)
        sub_module_name = child.data(role=PropertyItem.RawDataRole)
        if sub_module_name is None:
            return

        settings = self._read_settings(module_name, sub_module_name)
        for key, val in settings.items():
            setting_name = PropertyItem(key)
            setting_value = PropertyItem(val)
            parent.appendRow([setting_name, setting_value])

    def _read_settings(self, module_name, sub_module_name):
        """
        Read the public settings from a simulation module
        """
        module_cls = getattr(simulation_modules, module_name)
        sub_module_cls = get_simulation_module_class_by_name(module_cls,
                                                             sub_module_name)
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
            property_name = self.target_model.data(item.child(row, 0).index(),
                                                   role=PropertyItem.RawDataRole)
            property_val = self.target_model.data(item.child(row, 1).index(),
                                                  role=PropertyItem.RawDataRole)
            settings.update({property_name: property_val})

        return settings

    def _setup_sim_modules(self, model):
        """
        Setup simulation Modules.

        :param model: model holding the public settings of each module

        Returns:
            bool: If setup was successful.
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
            sub_module_cls = get_simulation_module_class_by_name(
                module_cls,
                sub_module_name)

            # get public settings for module
            settings = self._get_settings(self.target_model, module_item.text())
            if settings is None:
                return False
            settings.update({"type": sub_module_name})
            settings.update({"modules": self._sim_modules})

            # append special settings
            if module_name == "Solver":
                if "Model" not in settings["modules"]:
                    return False
                self._sim_settings = SimulationSettings(
                    settings["start time"],
                    settings["end time"],
                    settings["step size"],
                    settings["measure rate"])

            # build object
            slot = sub_module_cls(settings)

            # add to simulation modules
            self._sim_modules.update({module_name: slot})

            # store settings
            # self._sim_data['modules'].update({module_name: settings})

        if all([mod in self._sim_modules
                for mod in Simulator.static_module_list]):
            return True

        return False

    def set_regime(self, reg):
        """
        Load the given regimes settings into the target model.

        Returns:
            bool: `True` if successful, `False` if errors occurred.
        """
        if reg is None:
            return
        if isinstance(reg, list):
            self._logger.error("setRegime(): only scalar input allowed!")
            return False

        return self._apply_regime(reg)

    def _apply_regime(self, reg):
        """
        Set all module settings to those provided in the regime.

        Returns:
            bool: `True` if successful, `False` if errors occurred.
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
                self._logger.error("_apply_regime(): No module called {0}"
                                   "".format(module_name))
                return False

            items = self.target_model.findItems(module_name)
            if not len(items):
                self._logger.error("_apply_regime(): No item in List called {0}"
                                   "".format(module_name))
                return False

            module_item = items.pop(0)
            module_type = value["type"]

            # sanity check
            sub_module_cls = get_simulation_module_class_by_name(module_cls,
                                                                 module_type)

            if not sub_module_cls:
                self._logger.error("_apply_regime(): No sub-module called {0}"
                                   "".format(module_type))
                return False

            module_index = module_item.index()
            module_type_index = module_index.model().index(module_index.row(),
                                                           1)
            module_index.model().setData(module_type_index,
                                         module_type,
                                         role=PropertyItem.RawDataRole)
            # due to signal connections, default settings are loaded
            # automatically in the back

            # overwrite specific settings
            for key, val in value.items():
                if key == "type":
                    continue

                found = False
                for row in range(module_item.rowCount()):
                    if self.target_model.data(
                            module_item.child(row, 0).index()) == key:
                    # if str(module_item.child(row, 0).text()) == key:
                        value_idx = self.target_model.index(row, 1, module_index)
                        self.target_model.setData(value_idx,
                                                  val,
                                                  role=PropertyItem.RawDataRole)
                        found = True
                        break

                if not found:
                    self._logger.error("_applyRegime(): Setting: '{0}' not "
                                       "available for Module: '{1}'".format(
                        key, module_type))
                    return False

        return True

    @pyqtSlot()
    def run_simulation(self):
        """
        entry hook for time step simulation
        - use settings to create modules in simulation loop
        - move them into an extra thread
        - start simulation
        """
        # setup simulation modules
        suc = self._setup_sim_modules(self.target_model)
        if not suc:
            self._logger.error("Simulation Setup failed. Check Configuration.")
            self.simulation_finalized.emit("aborted", dict())
            return

        # setup simulator
        self._worker = Simulator(self._sim_settings, self._sim_modules)
        self._worker.moveToThread(self.simThread)

        # setup simulation modules
        for _module in self._sim_modules.values():
            _module.moveToThread(self.simThread)

        # setup signal connections
        self.simThread.started.connect(self._worker.run)
        self._worker.state_changed.connect(self.simulation_state_changed)
        self._worker.work_done.connect(self.simThread.quit)
        self.simThread.finished.connect(self.thread_finished)
        self.end_time = self._sim_settings.end_time

        # run
        self.simThread.start()

    @pyqtSlot(SimulationStateChange)
    def simulation_state_changed(self, state_change):
        """
        slot for simulation state changes

        :param state_change: see :cls:SimulationStateChange
        """
        self._logger.debug("simulation state change '{}'".format(
            state_change.type))

        if state_change.type == "start":
            self._sim_state = "running"

        elif state_change.type == "time":
            self._logger.debug("Reached simulation time {0}".format(
                state_change.t))
            progress = int(state_change.t / self._sim_settings.end_time * 100)
            if progress != self.last_progress:
                self._logger.info("Simulation reached {0}%".format(progress))
                self.simulationProgressChanged.emit(progress)
                self.last_progress = progress

        elif state_change.type == "abort":
            self._sim_state = "aborted"
            self._sim_data = copy.deepcopy(state_change.data)
            if isinstance(state_change.info, str):
                self._logger.info(state_change.info)
            else:
                self._logger.error("Simulation has been aborted due to an "
                                   "exception",
                                   exc_info=state_change.info)
                self._logger.warning("check your configuration")

        elif state_change.type == "finish":
            self._sim_state = "finished"
            self._sim_data = copy.deepcopy(state_change.data)

        else:
            self._logger.error(
                "simulation_state_changed(): ERROR Unknown state {0}".format(
                    state_change.type))

    @pyqtSlot()
    def stop_simulation(self):
        self._worker.stop()

    def _sim_aftercare(self):
        # reset internal states
        self._sim_settings = None

        # delete modules
        for module in self._sim_modules.keys():
            del module
        self._sim_modules = {}

        # don't disconnect signals in debug-mode
        if sys.gettrace() is None:
            self.simThread.started.disconnect(self._worker.run)
            self._worker.state_changed.disconnect(self.simulation_state_changed)
            self._worker.work_done.disconnect(self.simThread.quit)
            self.simThread.finished.disconnect(self.thread_finished)

        # delete simulator
        self._logger.info("deleting simulator")
        del self._worker

    def _postprocessing(self):
        """
        calculation of some basic metrics for quick judging of simulation results
        """

        # TODO make the entries to compare selectable
        # control and observer error
        if "Trajectory" in self._sim_data["results"]:
            m_data = self._get_result_by_name("Model")
            t_data = self._get_result_by_name("Trajectory")
            if len(t_data.shape) == 2:
                c_error = m_data[..., 0] - t_data[:, 0]
            elif len(t_data.shape) == 3:
                c_error = np.array([m_data[:, idx] - t_data[:, idx, 0]
                                    for idx in range(m_data.shape[1])]).T
            else:
                raise ValueError("Unknown Trajectory Format.")
            self._sim_data["results"].update(control_error=c_error)

        if "Observer" in self._sim_data["results"]:
            o_error = (self._get_result_by_name("Observer")
                       - self._get_result_by_name("Solver"))
            self._sim_data["results"].update(observer_error=o_error)

    def _get_result_by_name(self, name):
        return self._sim_data["results"][name]

    @pyqtSlot()
    def thread_finished(self):
        """
        Slot to be called when the simulation thread is finished.
        """
        assert self._sim_state == "finished" or self._sim_state == "aborted"

        # Add some error prone calculations (TODO move this somewhere else)
        self._postprocessing()

        # Rest internal states and disconnect signal connections
        self._sim_aftercare()

        # Signal gui that new data is available
        self.simulation_finalized.emit(self._sim_state, self._sim_data)

