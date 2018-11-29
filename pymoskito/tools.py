# -*- coding: utf-8 -*-
"""
Tools, functions and other funny things
"""
import copy
import logging
import os
import re

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PyQt5.QtGui import QColor
import subprocess
import pybind11

import numpy as np
from PyQt5.QtGui import QColor

logger = logging.getLogger(__name__)

__all__ = ["rotation_matrix_xyz", "get_resource", "generate_binding"]


def sort_lists(a, b):
    b = [x for (y, x) in sorted(zip(a, b))]
    a = sorted(a)
    return a, b


def get_resource(res_name, res_type="icons"):
    """
    Build absolute path to specified resource within the package

    Args:
        res_name (str): name of the resource
        res_type (str): subdir

    Return:
        str: path to resource
    """
    own_path = os.path.dirname(__file__)
    resource_path = os.path.abspath(os.path.join(own_path, "resources", res_type))
    return os.path.join(resource_path, res_name)


def sort_tree(data_list, sort_key_path):
    """
    Helper method for data sorting.

    Takes a list of simulation results and sorts them into a tree whose index is
    given by the sort_key_path.

    Args:
        data_list(list): List of simulation results
        sort_key_path(list): List of dictionary keys to sort for.

    Return:
        dict: sorted dictionary
    """
    result = {}
    for elem in data_list:
        temp_element = copy.deepcopy(elem)
        sort_name = get_sub_value(temp_element, sort_key_path)
        if sort_name not in result:
            result.update({sort_name: {}})

        while temp_element:
            val, keys = _remove_deepest(temp_element)
            if keys:
                _add_sub_value(result[sort_name], keys, val)

    return result


def get_sub_value(source, key_path):
    sub_dict = source
    for key in key_path:
        sub_dict = sub_dict[key]

    return sub_dict


def _remove_deepest(top_dict, keys=None):
    """
    Iterates recursively over dict and removes deepest entry.

    Args:
        top_dict (dict): dictionary
        keys (list): select entries to remove

    Return:
        tuple: entry and path to entry
    """
    if not keys:
        keys = []

    for key in list(top_dict.keys()):
        val = top_dict[key]
        if isinstance(val, dict):
            if val:
                keys.append(key)
                return _remove_deepest(val, keys)
            else:
                del top_dict[key]
                continue
        else:
            del top_dict[key]
            keys.append(key)
            return val, keys

    return None, None


def _add_sub_value(top_dict, keys, val):
    if len(keys) == 1:
        # we are here
        if keys[0] in top_dict:
            top_dict[keys[0]].append(val)
        else:
            top_dict.update({keys[0]: [val]})
        return

    # keep iterating
    if keys[0] not in top_dict:
        top_dict.update({keys[0]: {}})

    _add_sub_value(top_dict[keys[0]], keys[1:], val)
    return


def rotation_matrix_xyz(axis, angle, angle_dim):
    """
    Calculate the rotation matrix for a rotation around a given axis with the angle :math:`\\varphi`.

    Args:
        axis (str): choose rotation axis "x", "y" or "z"
        angle (int or float): rotation angle :math:`\\varphi`
        angle_dim (str): choose "deg" for degree or "rad" for radiant

    Return:
        :obj:`numpy.ndarray`: rotation matrix
    """
    assert angle_dim == "deg" or angle_dim == "rad"
    assert axis is "x" or axis == "y" or axis == "z"
    x = 0
    y = 0
    z = 0

    if angle_dim == "deg":
        a = np.deg2rad(angle)
    else:
        a = angle

    if axis == "x":
        x = 1
        y = 0
        z = 0
    if axis == "y":
        x = 0
        y = 1
        z = 0
    if axis == "z":
        x = 0
        y = 0
        z = 1

    s = np.sin(a)
    c = np.cos(a)
    rotation_matrix = np.array([[c + x ** 2 * (1 - c), x * y * (1 - c) - z * s, x * z * (1 - c) + y * s],
                                [y * x * (1 - c) + z * s, c + y ** 2 * (1 - c), y * z * (1 - c) - x * s],
                                [z * x * (1 - c) - y * s, z * y * (1 - c) + x * s, c + z ** 2 * (1 - c)]])
    return rotation_matrix


class PlainTextLogger(logging.Handler):
    """
    Logging handler hat formats log data for line display
    """

    def __init__(self, settings, level=logging.NOTSET):
        logging.Handler.__init__(self, level)
        self.name = "PlainTextLogger"
        self.settings = settings

        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%H:%M:%S")
        self.setFormatter(formatter)

        log_filter = PostFilter(invert=True)
        self.addFilter(log_filter)

        self.cb = None

    def set_target_cb(self, cb):
        self.cb = cb

    def emit(self, record):
        msg = self.format(record)
        if self.cb:
            clr = QColor(self.settings.value("log_colors/" + record.levelname,
                                             "#000000"))
            self.cb.setTextColor(clr)
            self.cb.append(msg)
        else:
            logging.getLogger().error("No callback configured!")


class PostFilter(logging.Filter):
    """
    Filter to sort out all not PostProcessing related log information
    """

    def __init__(self, invert=False):
        logging.Filter.__init__(self)
        self._invert = invert
        self.exp = re.compile(r"Post|Meta|Process")

    def filter(self, record):
        m = self.exp.match(record.name)
        if self._invert:
            return not bool(m)
        else:
            return bool(m)


def swap_cols(arr, frm, to):
    """ Swap the column `frm` from a given index `to` the given index.
    """
    arr[:, [frm, to]] = arr[:, [to, frm]]
    return arr


def swap_rows(arr, frm, to):
    """ Swap the rows `frm` from a given index `to` the given index.
    """
    if len(arr.shape) == 1:
        arr[[frm, to]] = arr[[to, frm]]
    elif len(arr.shape) == 2:
        arr[[frm, to], :] = arr[[to, frm], :]
    return arr


class LengthList(object):
    def __init__(self, maxLength):
        self.maxLength = maxLength
        self.ls = []

    def push(self, st):
        if len(self.ls) == self.maxLength:
            self.ls.pop(0)
        self.ls.append(st)

    def get_list(self):
        return self.ls

    def __len__(self):
        return len(self.ls)

    def __getitem__(self, key):
        return self.ls[key]


def get_figure_size(scale):
    """
    calculate optimal figure size with the golden ratio
    :param scale:
    :return:
    """
    # TODO: Get this from LaTeX using \the\textwidth
    fig_width_pt = 448.13095
    inches_per_pt = 1.0 / 72.27  # Convert pt to inch (stupid imperial system)
    golden_ratio = (np.sqrt(5.0) - 1.0) / 2.0  # Aesthetic ratio
    fig_width = fig_width_pt * inches_per_pt * scale  # width in inches
    fig_height = fig_width * golden_ratio  # height in inches
    fig_size = [fig_width, fig_height]
    return fig_size


class Exporter:
    def __init__(self, **kwargs):
        data_points = kwargs.get('data_points', None)

        if data_points is None:
            raise Exception("Given data points are None!")

        # build pandas data frame
        self.df = pd.DataFrame.from_dict(data_points)

        if 'time' in self.df.columns:
            self.df.set_index('time', inplace=True)

    def export_png(self, file_name):
        fig = plt.figure(figsize=(10, 6))
        gs = gridspec.GridSpec(1, 1, hspace=0.1)
        axes = plt.Subplot(fig, gs[0])

        for col in self.df.columns:
            self.df[col].plot(ax=axes, label=col)

        axes.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=4,
                    ncol=4, mode="expand", borderaxespad=0., framealpha=0.5)

        axes.grid(True)
        if self.df.index.name == 'time':
            axes.set_xlabel(r"Time (s)")

        fig.add_subplot(axes)

        fig.savefig(file_name, dpi=300)

    def export_csv(self, file_name, sep=','):
        self.df.to_csv(file_name, sep=sep)


def generate_binding(module_name, module_path):
    src_path = os.path.join(os.path.dirname(module_path), "binding")
    module_inc_path = os.path.join(src_path, module_name + ".h")
    module_src_path = os.path.join(src_path, module_name + ".cpp")

    pybind_path = os.path.join(os.path.dirname(__file__),
                               os.pardir,
                               "libs",
                               "pybind11")
    c_make_lists_path = os.path.join(src_path, 'CMakeLists.txt')

    # check if folder exists
    if not os.path.isdir(src_path):
        logger.error("Dir binding not available in project folder '{}'"
                     "".format(os.getcwd()))
        return

    if not os.path.exists(module_inc_path):
        logger.error("Module '{}'.h could not found in binding folder"
                     "".format(module_inc_path))
        return

    if not os.path.exists(module_inc_path):
        logger.error("Module '{}'.h could not found in binding folder"
                     "".format(module_src_path))
        return

    if not os.path.exists(c_make_lists_path):
        logger.warning("No CMakeLists.txt found!")
        logger.info("Generating new CMake config.")
        create_cmake_lists(c_make_lists_path, pybind_path, module_name)

    add_binding_config(c_make_lists_path, module_name)

    # build
    if os.name == 'nt':
        result = subprocess.run(['cmake', '-A', 'x64', '.'],
                                cwd=src_path,
                                shell=True)
        if result.returncode == 0:
            result = subprocess.run(
                ['cmake', '--build', '.', '--config', 'Release'],
                cwd=src_path,
                shell=True)
    else:
        result = subprocess.run(['cmake . && make'], cwd=src_path, shell=True)

    if result.returncode != 0:
        logger.error("Build failed.")


def add_binding_config(cmake_lists_path, module_name):
    """
    Add the module config to the cmake lists.

    Args:
        cmake_lists_path(str): Path to `CmakeLists.txt`.
        module_name(str): Name of module to add.
    """
    config_line = "pybind11_add_module({} {} {})".format(
        module_name,
        module_name + '.cpp',
        'binding_' + module_name + '.cpp')

    with open(cmake_lists_path, "r") as f:
        if config_line in f.read():
            return

    logger.info("Appending build info for '{}'".format(module_name))
    with open(cmake_lists_path, "a") as f:
        f.write("\n")
        f.write(config_line)


def create_cmake_lists(cmake_lists_path, pybind_dir, project_name="cpp_bindings"):
    """
    Create the stub of a `CMakeLists.txt` .

    Args:
        cmake_lists_path(str): Path to `CmakeLists.txt`.
        pybind_dir(str): Path of the pybind checkout.
        project_name(str): Name of cmake project.

    Returns:

    """
    c_make_lists = "cmake_minimum_required(VERSION 2.8.12)\n"
    c_make_lists += "project({})\n\n".format(project_name)

    c_make_lists += "set( CMAKE_RUNTIME_OUTPUT_DIRECTORY . )\n"
    c_make_lists += "set( CMAKE_LIBRARY_OUTPUT_DIRECTORY . )\n"
    c_make_lists += "set( CMAKE_ARCHIVE_OUTPUT_DIRECTORY . )\n\n"

    c_make_lists += "foreach( OUTPUTCONFIG ${CMAKE_CONFIGURATION_TYPES} )\n"
    c_make_lists += "\tstring( TOUPPER ${OUTPUTCONFIG} OUTPUTCONFIG )\n"
    c_make_lists += "\tset( CMAKE_RUNTIME_OUTPUT_DIRECTORY_${OUTPUTCONFIG} . )\n"
    c_make_lists += "\tset( CMAKE_LIBRARY_OUTPUT_DIRECTORY_${OUTPUTCONFIG} . )\n"
    c_make_lists += "\tset( CMAKE_ARCHIVE_OUTPUT_DIRECTORY_${OUTPUTCONFIG} . )\n"
    c_make_lists += "endforeach( OUTPUTCONFIG CMAKE_CONFIGURATION_TYPES )\n\n"

    # TODO get pybind install via pip running and use this line:
    # c_make_lists += "find_package(pybind11)"
    c_make_lists += "add_subdirectory({} pybind11)\n".format(pybind_dir)

    with open(cmake_lists_path, "w") as f:
        f.write(c_make_lists)

