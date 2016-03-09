#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_registry
----------------------------------

Tests for `registry` module.
"""

import unittest

# nice top level import for this guys
from pymoskito import get_registered_simulation_modules, get_registered_processing_modules

# normal import since those should not be used so often
from pymoskito.registry import get_registered_modules

from pymoskito.simulation_modules import SimulationModule, ModelMixer, Controller, Trajectory
import pymoskito.generic_simulation_modules as sim_modules

from pymoskito.processing_core import PostProcessingModule, MetaProcessingModule
import pymoskito.generic_processing_modules as post_modules


class TestRegistration(unittest.TestCase):
    # remember automatic registration in Module Definition is done by importing

    def setUp(self):
        pass

    def test_general(self):
        # general call
        self.assertEqual([(sim_modules.AdditiveMixer, "AdditiveMixer")],
                         get_registered_modules(SimulationModule, ModelMixer))

    def test_special(self):
        # special calls
        self.assertEqual([(sim_modules.PIDController, "PIDController")],
                         get_registered_simulation_modules(Controller))
        self.assertEqual([(sim_modules.HarmonicTrajectory, "HarmonicTrajectory"),
                          (sim_modules.SmoothTransition, "SmoothTransition")],
                         get_registered_simulation_modules(Trajectory))
        self.assertEqual([(post_modules.StepResponse, "StepResponse")],
                         get_registered_processing_modules(PostProcessingModule))

    def test_string(self):
        # should also work with names instead of class objects
        self.assertEqual([(sim_modules.PIDController, "PIDController")],
                         get_registered_modules("SimulationModule", "Controller"))
        self.assertEqual([(sim_modules.PIDController, "PIDController")],
                         get_registered_simulation_modules("Controller"))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
