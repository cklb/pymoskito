#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_pymoskito
----------------------------------

Tests for `pymoskito` module.
"""

import unittest

from pymoskito import pymoskito as pm
from pymoskito.simulation_modules import Controller, Model
from examples.ballbeam.model import BallBeamModel
from examples.ballbeam.control import FController

class TestPymoskito(unittest.TestCase):

    def setUp(self):
        pass

    def test_registration(self):
        # empty List as default
        self.assertEqual([], pm.get_registered_modules(Model))

        pm.register_simulation_module(Model, BallBeamModel)
        self.assertEqual([BallBeamModel], pm.get_registered_modules(Model))

        pm.register_simulation_module(Controller, FController)
        self.assertEqual([FController], pm.get_registered_modules(Controller))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
