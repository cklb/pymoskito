#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_simulation_gui
----------------------------------

Tests for `simulation_gui` module.
"""

import unittest

from PyQt5.QtWidgets import QApplication

import pymoskito as pm


class TestGUI(unittest.TestCase):

    def setUp(self):
        self.app = QApplication([])

    def test_sim_gui(self):
        g = pm.SimulationGui()

    # TODO more ...

    def tearDown(self):
        del self.app

if __name__ == '__main__':
    unittest.main()
