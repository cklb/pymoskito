#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_simulation_gui
----------------------------------

Tests for `simulation_gui` module.
"""

import unittest

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

import pymoskito as pm

from pymoskito.simulation_interface import PropertyItem, PropertyDelegate


class TestPropertyItem(unittest.TestCase):

    def setUp(self):
        self.props = {"Name": "TestName",
                      "Integer Value": 12,
                      "Float Value": 3.14,
                      "List": [1, 2],
                      "None": None,
                      "Dictionary": dict(a=2, b=7),
                      }

    def test_data(self):
        # Edit is performed using the raw data
        key_items = []
        val_items = []
        for key, val in self.props.items():
            key_items.append(PropertyItem(key))
            val_items.append(PropertyItem(val))

        for idx in range(len(key_items)):
            # default role should return string
            name = key_items[idx].data(role=Qt.DisplayRole)
            self.assertIsInstance(name, str)

            data_string = val_items[idx].data(role=Qt.DisplayRole)
            self.assertIsInstance(data_string, str)
            self.assertEqual(data_string, str(self.props[name]))

            # Data should be available in raw format using special role
            data = val_items[idx].data(role=PropertyItem.RawDataRole)
            self.assertEqual(self.props[name], data)

    def test_setData(self):
        # only if the returned string can be parsed it should be accepted
        item = PropertyItem(self.props["List"])

        edit_str = item.data(role=Qt.EditRole)
        self.assertIsInstance(edit_str, str)
        self.assertEqual(edit_str, str(self.props["List"]))

        new_list = [1, 3, 5]
        item.setData(new_list, role=PropertyItem.RawDataRole)
        self.assertEqual(item.data(role=PropertyItem.RawDataRole),
                         new_list)
        new_str = str(new_list)
        self.assertEqual(item.data(role=Qt.DisplayRole),
                         new_str)

        # invalid data should be rejected and exception should be printed to log
        item.setData(edit_str[:-1], role=Qt.EditRole)
        self.assertEqual(item.data(role=Qt.DisplayRole),
                         new_str)


class TestGUI(unittest.TestCase):

    def setUp(self):
        self.app = QApplication([])

    def test_sim_gui(self):
        g = pm.SimulationGui()
        g.close()

    # TODO more ...

    def tearDown(self):
        del self.app

if __name__ == '__main__':
    unittest.main()
