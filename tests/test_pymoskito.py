#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_pymoskito
----------------------------------

Tests for `pymoskito` module.
"""

import unittest

from pymoskito import pymoskito as pm
from pymoskito.simulation_modules import SimulationModule, ModelMixer, Controller, Trajectory
import pymoskito.generic_simulation_modules as sim_modules

from pymoskito.processing_core import PostProcessingModule, MetaProcessingModule
import pymoskito.generic_postprocessing_modules as post_modules

class TestPymoskito(unittest.TestCase):

    def setUp(self):
        pass

    def test_registration(self):
        # remember automatic registration in Module Definition by import

        # general call
        self.assertEqual([(sim_modules.AdditiveMixer, "AdditiveMixer")],
                         pm.get_registered_modules(SimulationModule, ModelMixer))

        # special calls
        self.assertEqual([(sim_modules.PIDController, "PIDController")],
                         pm.get_registered_simulation_modules(Controller))
        self.assertEqual([(sim_modules.HarmonicTrajectory, "HarmonicTrajectory"),
                          (sim_modules.SmoothTransition, "SmoothTransition")],
                         pm.get_registered_simulation_modules(Trajectory))
        self.assertEqual([(post_modules.StepResponse, "StepResponse")],
                         pm.get_registered_processing_modules(PostProcessingModule))

        # should also work with names instead of class objects
        self.assertEqual([(sim_modules.PIDController, "PIDController")],
                         pm.get_registered_modules("SimulationModule", "Controller"))
        self.assertEqual([(sim_modules.PIDController, "PIDController")],
                         pm.get_registered_simulation_modules("Controller"))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
