# -*- coding: utf-8 -*-
"""
Tools, functions and other funny things
"""
import copy
import logging
import os
import re

import numpy as np
from PyQt5.QtWidgets import QPlainTextEdit

logger = logging.getLogger(__name__)

__all__ = ["rotation_matrix_xyz", "get_resource"]


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
    Takes a list of simulation results and sorts them into a tree whose index is given by the sort_key_path

    Args:
        data_list (list): list of simulation results
        sort_key_path (str):

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

    for key in top_dict.keys():
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
    assert angle_dim is "deg" or angle_dim is "rad"
    assert axis is "x" or axis is "y" or axis is "z"
    x = 0
    y = 0
    z = 0

    if angle_dim is "deg":
        a = np.deg2rad(angle)
    else:
        a = angle

    if axis is "x":
        x = 1
        y = 0
        z = 0
    if axis is "y":
        x = 0
        y = 1
        z = 0
    if axis is "z":
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
    def __init__(self, level=logging.NOTSET):
        logging.Handler.__init__(self, level)
        self.name = "PlainTextLogger"

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
            self.cb(msg)
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