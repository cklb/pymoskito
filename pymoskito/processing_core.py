import logging
import os
from abc import ABCMeta, abstractmethod
from pickle import dump

import numpy as np
from scipy.integrate import simps
from PyQt5.QtCore import QObject, QSettings
from PyQt5.QtWidgets import QMessageBox, QFileDialog
pyqtWrapperType = type(QObject)

from .tools import get_sub_value

__all__ = ["PostProcessingModule", "MetaProcessingModule"]

"""
Base Classes for modules in the result-processing environment
"""


class ProcessingModuleMeta(ABCMeta, pyqtWrapperType):
    pass


class ProcessingModule(QObject, metaclass=ProcessingModuleMeta):
    """
    Base Class for processing Modules.
    Each Module's run method is called with a list of results by the processing_gui
    """

    # fonts
    _base_font_size = 14
    _title_font_size = 1.5 * _base_font_size
    _label_font_size = 1 * _base_font_size

    # colors
    _grid_color = "#ababab"

    # lines
    _grid_line_style = "--"

    _export_formats = [
        ".pdf",
        # ".png",
        # ".svg",
        # ".eps"
    ]

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.name = self.__class__.__name__
        self._settings = QSettings()
        self._logger = logging.getLogger(self.name)

        self._path_name = None
        self._file_type = None
        self._file_info = None

    @abstractmethod
    def process(self, result_data):
        """
        function that is called when the Processing environment processes all
        loaded result files.

        :param result_data: list of result dicts
        :return: list of diagrams
        """
        pass

    def extract_setting(self, data_list, names, module_name, setting_name):
        """
        extracts settings from simulation data
        :param data_list:
        :param names:
        :param module_name:
        :param setting_name:
        :return:
        """
        return self.extract(data_list, ["modules", module_name, setting_name],
                            names)

    def extract_values(self, data_list, names, value_name):
        """
        extracts values from simulation data
        :param data_list:
        :param names:
        :param value_name:
        :return:
        """
        return self.extract(data_list, ["results", value_name], names)

    def extract(self, data_list, keys, names):
        """
        general extraction from simulation data
        where the regime name contains all strings
        listed in names
        :param data_list:
        :param keys:
        :param names:
        :return:
        """
        if not isinstance(names, list):
            names = [names]

        return next((self._get_sub_dict(result, keys) for result in data_list if
                     all(name in result['regime name'] for name in names)),
                    None)

    @staticmethod
    def _get_sub_dict(top_dict, keys):
        sub_dict = top_dict
        for key in keys:
            sub_dict = sub_dict[key]
        return sub_dict

    def write_output_files(self, result_name, figure, output=None):
        """
        Export the created diagrams and save calculation results in a POF
        (processing output file) file.

        :param result_name:
        :param figure:
        :param output:
        :return:
        """
        path = self._settings.value(self._path_name)
        if not os.path.isdir(path):
            box = QMessageBox()
            box.setText("Export Folder does not exist yet.")
            box.setInformativeText("Do you want to create it? \n"
                                   "{}".format(os.path.abspath(path)))
            box.setStandardButtons(QMessageBox.Ok | QMessageBox.No)
            box.setDefaultButton(QMessageBox.Ok)
            ret = box.exec_()
            if ret == QMessageBox.Ok:
                os.makedirs(path)
            else:
                path = os.path.curdir

        sub_path = os.path.join(path, self.name)
        if not os.path.isdir(sub_path):
            os.makedirs(sub_path)

        dialog = QFileDialog()
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setDirectory(sub_path)
        dialog.setNameFilter("{} (*{})".format(self._file_info,
                                               self._file_type))
        dialog.selectFile(result_name + self._file_type)

        if dialog.exec_():
            file_path = dialog.selectedFiles()[0]
        else:
            self._logger.warning("Export Aborted")
            return

        new_path = os.path.sep.join(file_path.split(os.path.sep)[:-2])
        if new_path != self._settings.value(self._path_name):
            box = QMessageBox()
            box.setText("Use this path as new default?")
            box.setInformativeText("{}".format(new_path))
            box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            box.setDefaultButton(QMessageBox.Yes)
            ret = box.exec_()
            if ret == QMessageBox.Yes:
                self._settings.setValue(self._path_name, new_path)

        if output:
            with open(file_path, "wb") as f:
                dump(output, f, protocol=4)

        if figure:
            for export_format in self._export_formats:
                figure.savefig(file_path.split(".")[0] + export_format,
                               bbox_inches='tight')
                # setting bbox_inches='tight' removes the white space around
                # a saved image


class PostProcessingModule(ProcessingModule):
    """
    Base Class for Postprocessing Modules
    """

    def __init__(self):
        ProcessingModule.__init__(self)

        self.figure = None
        self.axes = None
        self.label_counter = 0
        self.results = {}

        self._path_name = "path/postprocessing_results"
        self._file_info = "Processing Output Files"
        self._file_type = ".pof"

    def process(self, files):
        """
        worker-wrapper function that processes an array of result files
        This is an convenience wrapper for simple processor implementation.
        Overload for more sophisticated implementations
        :param files:
        """
        result_list = []
        for data in files:
            self._logger.info("processing data set: {0}".format(data["regime name"]))
            result_list.extend(self.run(data))

        return result_list

    @abstractmethod
    def run(self, data):
        """
        Run this postprocessor.
        
        This function will be called from :py:func:`process` with the simulation
        results from one simulation result file.
        
        Overwrite this function to implement your own PostProcessor.

        Args;
        param data: simulation results from a pymoskito simulation result file.
        
        Returns:
             Dict: With a figure Canvas an a name.
        """
        self._logger.warning("placeholder routine called!")
        return {"name": "* placeholder *", "figure": None}

    @staticmethod
    def calc_label_pos(values):
        return np.arange(np.min(values[0]) + 0.1 * values[1],
                         values[1],
                         (values[1] - np.min(values[1])) / 4)

    @staticmethod
    def calc_l1_norm_itae(meas_values, desired_values, step_width):
        """
        Calculate the L1-Norm of the ITAE (Integral of Time-multiplied Absolute
        value of Error).

        Args:
            step_width (float): Time difference between measurements.
            desired_values (array-like): Desired values.
            meas_values (array-like): Measured values.
        """
        def e_func(_t):
            _idx = np.floor_divide(_t, step_width).astype(int)
            e = t * np.abs(desired_values[_idx, ..., 0]
                           - meas_values[_idx, ..., 0])
            return e

        t = np.array([x * step_width for x in range(len(desired_values))])
        err = e_func(t)
        l1norm_itae = simps(err, t)
        return l1norm_itae

    @staticmethod
    def calc_l1_norm_abs(meas_values, desired_values, step_width):
        """
        Calculate the L1-Norm of the absolute error.

        Args:
            step_width (float): Time difference between measurements.
            desired_values (array-like): Desired values.
            meas_values (array-like): Measured values.
        """
        def e_func(_t):
            _idx = np.floor_divide(_t, step_width).astype(int)
            e = np.abs(desired_values[_idx, ..., 0]
                       - meas_values[_idx, ..., 0])
            return e

        t = np.array([x * step_width for x in range(len(desired_values))])
        err = e_func(t)
        l1norm_abs = simps(err, t)
        return l1norm_abs


class MetaProcessingModule(ProcessingModule):
    """
    Base Class for Meta-Processing Modules
    """

    def __init__(self):
        ProcessingModule.__init__(self)

        self._path_name = "path/metaprocessing_results"
        self._file_info = "Meta Output Files"
        self._file_type = ".mof"

    def set_plot_labeling(self, title="", grid=True, x_label="", y_label="", line_type="line"):
        """
        helper to quickly set axis labeling with the good font sizes
        :param title:
        :param grid:
        :param x_label:
        :param y_label:
        :param line_type:
        :return:
        """
        self.axes.set_title(title, size=self._title_font_size)
        self.axes.set_xlabel(x_label, size=self._label_font_size)
        self.axes.set_ylabel(y_label, size=self._label_font_size)

        if grid:
            self.axes.grid(color=self._grid_color, linestyle=self._grid_line_style)

        if line_type != "bar":
            self.axes.legend(loc=0, fontsize='small', prop={'size': 8})

    def plot_family(self, family, x_path, y_path, mode, x_index=-1, y_index=-1):
        """
        plots y over x for all members that can be found in family sources
        :param family:
        :param x_path:
        :param y_path:
        :param mode:
        :param x_index:
        :param y_index:
        :return:
        """
        width = 0.2
        counter = 0
        x_all = []

        for member in family:
            x_list = get_sub_value(member, x_path)
            y_list = get_sub_value(member, y_path)
            x_list, y_list = self.sort_lists(x_list, y_list)

            if x_index >= 0:
                x_list[:] = [x[x_index] for x in x_list]
            if y_index >= 0:
                y_list[:] = [y[y_index] for y in y_list]

            # add x values to x_all if there are not in x_all
            for val in x_list:
                if val not in x_all:
                    x_all.append(val)

            if mode == 'line':
                self.axes.plot(x_list, y_list, 'o-', label=member)  # , color=st.color_cycle[member])
            elif mode == 'bar':
                # remove all None from yList
                x_list[:] = [x for x, y in zip(x_list, y_list) if y]
                y_list[:] = [i for i in y_list if i]

                # correction for the position of the bar
                x_list[:] = [k + width * counter for k in x_list]

                self.axes.bar(x_list, y_list, width, label=member)  # , color=st.color_cycle[controller])
                counter += 1

        if (mode == 'bar') and (len(x_all) > 1):
            # remove all None from x_all
            x_all.sort()
            x_all[:] = [i for i in x_all if i]

            # does not work for all constellations
            spacing = (x_all[-1] - x_all[0]) / (len(x_all) - 1)
            x_all.append(spacing + x_all[-1])
            x_all.append(x_all[0] - spacing)
            x_all.sort()

            x_all_label = [r'$' + str(i) + '$' for i in x_all]
            counter -= 1
            if mode == 'bar':
                x_all[:] = [i + width * counter for i in x_all]

            self.axes.set_xticks(x_all)
            self.axes.set_xticklabels(x_all_label)
