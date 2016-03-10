from __future__ import division
import logging
from cPickle import dump
import os
from abc import ABCMeta, abstractmethod

from PyQt4.QtCore import QObject, pyqtWrapperType

from tools import get_sub_value

"""
Base Classes for modules in the result-processing environment
"""
__author__ = 'stefan'


class ProcessingModuleMeta(ABCMeta, pyqtWrapperType):
    pass


class ProcessingModule(QObject):
    """
    Base Class for processing Modules.
    Each Module's run method is called with a list of results by the processing_gui
    """
    __metaclass__ = ProcessingModuleMeta

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
        self._logger = logging.getLogger(self.name)
        return

    @abstractmethod
    def process(self, result_data):
        """
        function that is called when the Processing environment processes all loaded result files
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
        return self.extract(data_list, ["modules", module_name, setting_name], names)

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
        this function exports the created diagram and saves calculation results in a POF
        (processing output file) File.
        :param result_name:
        :param figure:
        :param output:
        :return:
        """
        file_path = os.path.join(os.path.pardir, "results", "processing", self.name)
        if not os.path.isdir(file_path):
            os.makedirs(file_path)

        file_name = os.path.join(file_path, result_name)
        if output:
            with open(file_name + '.pof', 'w') as f:
                dump(output, f)

        if figure:
            for export_format in self._export_formats:
                figure.savefig(file_name + export_format, bbox_inches='tight')
                # setting bbox_inches='tight' remove the white space around a saved image


class PostProcessingModule(ProcessingModule):
    """
    Base Class for Postprocessing Modules
    """

    def __init__(self):
        ProcessingModule.__init__(self)
        return

    def process(self, files):
        """
        worker-wrapper function that processes an array of result files
        This is an convenience wrapper for simple processor implementation.
        Overload for more sophisticated implementations
        :param files:
        """
        output = []
        for res in files:
            self._logger.info("processing data set: {0}".format(res["regime name"]))
            output.extend(self.run(res))

        return output

    @abstractmethod
    def run(self, data):
        pass

    @staticmethod
    def calc_l1_norm_itae(is_values, desired_values, step_width):
        """
        this function calculates the L1 Norm with an additional time weighting between is and desired value
        unit: m*s**2
        :param step_width:
        :param desired_values:
        :param is_values:
        """
        l1norm_itae = 0
        for idx, val in enumerate(is_values):
            # version 1
            l1norm_itae += abs(desired_values[idx] - val) * step_width * (idx * step_width)

            # version 2 see also wikipedia
            # L1NormITAE += abs(yd[idx] - val - (y[-1] - yd[-1]))*dt*(idx*dt)

        return l1norm_itae

    @staticmethod
    def calc_l1_norm_abs(is_values, desired_values, step_width):
        """
        this function calculates the L1 Norm (absolute criterion) of a given dataset
        unit: m*s
        :param step_width:
        :param desired_values:
        :param is_values:
        """
        l1_norm_abs = 0
        for idx, val in enumerate(is_values):
            # version 1
            l1_norm_abs += abs(desired_values[idx] - val) * step_width

            # version 2 see also wikipedia
            # L1NormAbs += abs(yd[idx] - val - (y[-1] - yd[-1]))*dt

        return l1_norm_abs


class MetaProcessingModule(ProcessingModule):
    """
    Base Class for Meta-Processing Modules
    """

    def __init__(self):
        ProcessingModule.__init__(self)
        return

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

    def plot_family(self, family, x_path, y_path, typ, x_index=-1, y_index=-1):
        """
        plots y over x for all members that can be found in family sources
        :param family:
        :param x_path:
        :param y_path:
        :param typ:
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

            if typ == 'line':
                self.axes.plot(x_list, y_list, 'o-', label=member) #, color=st.color_cycle[member])
            elif typ == 'bar':
                # remove all None from yList
                x_list[:] = [x for x, y in zip(x_list, y_list) if y]
                y_list[:] = [i for i in y_list if i]

                # correction for the position of the bar
                x_list[:] = [k + width * counter for k in x_list]

                self.axes.bar(x_list, y_list, width, label=member)  #, color=st.color_cycle[controller])
                counter += 1

        if (typ == 'bar') and (len(x_all) > 1):
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
            if typ == 'bar':
                x_all[:] = [i + width * counter for i in x_all]

            self.axes.set_xticks(x_all)
            self.axes.set_xticklabels(x_all_label)
