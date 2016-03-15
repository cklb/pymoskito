#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_registry
----------------------------------

Tests for `registry` module.
"""

import unittest

# nice top level import for this guys
from pymoskito import register_simulation_module, register_processing_module, register_visualizer,\
    get_registered_simulation_modules, get_registered_processing_modules

# normal import since those should not be used so often
from pymoskito.registry import get_registered_modules, get_registered_visualizers

from pymoskito.simulation_modules import *
from pymoskito.generic_simulation_modules import *

from pymoskito.processing_core import ProcessingModule, PostProcessingModule, MetaProcessingModule
from pymoskito.generic_processing_modules import *

from examples.ballbeam.model import BallBeamModel
from examples.ballbeam.control import FController
from examples.ballbeam.postprocessing import EvalA1
from examples.ballbeam.visualization import BallBeamVisualizer
from examples.balltube.visualization import BallInTubeVisualizer


class TestRegisterCalls(unittest.TestCase):
    def setUp(self):
        pass

    def test_generic_calls(self):
        """
        check whether all generic simulation and postprocessing modules are registered using the general getter call
        """
        # register in wrong module category
        self.assertRaises(TypeError, register_simulation_module, PostProcessingModule, EvalA1)
        self.assertRaises(TypeError, register_processing_module, MetaProcessingModule, EvalA1)
        register_processing_module(PostProcessingModule, EvalA1)

        # check registration
        self.assertEqual([(EvalA1, "EvalA1")],
                         get_registered_processing_modules(PostProcessingModule)[-1:])

        # test for automatic duplicate recognition
        self.assertRaises(ValueError, register_processing_module, PostProcessingModule, EvalA1)

    def test_visualizer(self):
        self.assertRaises(TypeError, register_visualizer, EvalA1)
        register_visualizer(BallInTubeVisualizer)
        self.assertIn((BallInTubeVisualizer, "BallInTubeVisualizer"),
                      get_registered_visualizers())


class TestGetterCalls(unittest.TestCase):
    def setUp(self):
        # registration of generic modules is done in __init__.py
        pass

    def test_generic_calls(self):
        """
        check whether all generic simulation and postprocessing modules are registered using the general getter call
        """
        # ----------------------
        # simulation

        # solver
        self.assertEqual([(ODEInt, "ODEInt")],
                         get_registered_modules(SimulationModule, Solver))

        # trajectory generators
        self.assertEqual([(SmoothTransition, "SmoothTransition"),
                          (HarmonicTrajectory, "HarmonicTrajectory"),
                          (Setpoint, "Setpoint")
                          ],
                         get_registered_modules(SimulationModule, Trajectory))

        # controllers
        self.assertEqual([(PIDController, "PIDController")],
                         get_registered_modules(SimulationModule, Controller))

        # feedforward
        self.assertEqual([(PyTrajectory, "PyTrajectory")],
                         get_registered_modules(SimulationModule, Feedforward))

        # mixers
        self.assertEqual([(AdditiveMixer, "AdditiveMixer")],
                         get_registered_modules(SimulationModule, ModelMixer))
        self.assertEqual([(AdditiveMixer, "AdditiveMixer")],
                         get_registered_modules(SimulationModule, ObserverMixer))

        # limiter
        self.assertEqual([(ModelInputLimiter, "ModelInputLimiter")],
                         get_registered_modules(SimulationModule, Limiter))

        # sensors
        self.assertEqual([(DeadTimeSensor, "DeadTimeSensor")],
                         get_registered_modules(SimulationModule, Sensor))

        # disturbance
        self.assertEqual([(GaussianNoise, "GaussianNoise")],
                         get_registered_modules(SimulationModule, Disturbance))

        # ----------------------
        # processing

        # post-processors
        self.assertEqual([(StepResponse, "StepResponse"),
                          (PlotAll, "PlotAll")
                          ],
                         get_registered_modules(ProcessingModule, PostProcessingModule))

        # # meta-processors
        # self.assertEqual([(XYMetaProcessor, "XYMetaProcessor")],
        #                  get_registered_modules(ProcessingModule, MetaProcessingModule))

    def test_special_call(self):
        """
        special calls, same modules but different functions for access
        """
        # ----------------------
        # simulation

        self.assertEqual([(PIDController, "PIDController")],
                         get_registered_simulation_modules(Controller))
        self.assertEqual([(SmoothTransition, "SmoothTransition"),
                          (HarmonicTrajectory, "HarmonicTrajectory"),
                          (Setpoint, "Setpoint"),
                          ],
                         get_registered_simulation_modules(Trajectory))

        # ----------------------
        # processing

        self.assertEqual([(StepResponse, "StepResponse"),
                          (PlotAll, "PlotAll")],
                         get_registered_processing_modules(PostProcessingModule))
        # self.assertEqual([(XYMetaProcessor, "XYMetaProcessor")],
        #                  get_registered_processing_modules(MetaProcessingModule))

    def test_string_call(self):
        """
        the calls should also work with names instead of class objects
        """
        self.assertEqual([(ODEInt, "ODEInt")],
                         get_registered_modules("SimulationModule", "Solver"))
        self.assertEqual([(StepResponse, "StepResponse"),
                          (PlotAll, "PlotAll")
                          ],
                         get_registered_processing_modules("PostProcessingModule"))

    def test_visualizer_call(self):
        """
        test interface for visualizer
        """
        # register a visualizer for testing
        register_visualizer(BallBeamVisualizer)

        self.assertEqual([(BallBeamVisualizer, "BallBeamVisualizer")],
                         get_registered_visualizers())

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
