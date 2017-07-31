#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_registry
----------------------------------

Tests for `registry` module.
"""

import unittest

# nice top level import for these guys
from pymoskito import (register_simulation_module, register_processing_module,
                       register_visualizer, get_registered_simulation_modules,
                       get_registered_processing_modules)

# normal import since those should not be used so often from the outside
from pymoskito.registry import (get_registered_modules,
                                get_registered_visualizers)
from pymoskito.simulation_modules import *
from pymoskito.generic_simulation_modules import *
from pymoskito.processing_core import (ProcessingModule, PostProcessingModule,
                                       MetaProcessingModule)
from pymoskito.generic_processing_modules import *

from pymoskito.examples.ballbeam.model import BallBeamModel
from pymoskito.examples.ballbeam.controller import FController
from pymoskito.examples.ballbeam.postprocessing import EvalA1
from pymoskito.examples.ballbeam.visualization import MplBallBeamVisualizer


class TestRegisterCalls(unittest.TestCase):
    def setUp(self):
        pass

    def test_generic_calls(self):
        """
        Check whether all generic simulation modules, postprocessing modules
        and visualizers are registered using the general getter call
        """

        # register a simulation module in wrong module category
        self.assertRaises(TypeError, register_simulation_module,
                          Controller, BallBeamModel)
        self.assertRaises(TypeError, register_processing_module,
                          PostProcessingModule, BallBeamModel)
        self.assertRaises(TypeError, register_visualizer, BallBeamModel)

        # register a postprocessor in wrong module category
        self.assertRaises(TypeError, register_simulation_module,
                          PostProcessingModule, EvalA1)
        self.assertRaises(TypeError, register_processing_module,
                          MetaProcessingModule, EvalA1)
        self.assertRaises(TypeError, register_visualizer, EvalA1)

        # register a visualizer in wrong module category
        self.assertRaises(TypeError, register_simulation_module,
                          Model, MplBallBeamVisualizer)
        self.assertRaises(TypeError, register_processing_module,
                          PostProcessingModule, MplBallBeamVisualizer)

        # check registration
        # (the modules are registered if the import was successful)
        self.assertTrue((BallBeamModel, "BallBeamModel")
                        in get_registered_simulation_modules(Model))
        self.assertTrue((FController, "FController")
                        in get_registered_simulation_modules(Controller))
        self.assertTrue(
            (EvalA1, "EvalA1")
            in get_registered_processing_modules(PostProcessingModule))
        # self.assertTrue(
        #     (XYMetaProcessor, "XYMetaProcessor")
        #     in get_registered_processing_modules(MetaProcessingModule))
        self.assertTrue(
            (MplBallBeamVisualizer, "MplBallBeamVisualizer")
            in get_registered_visualizers())

        # test for automatic duplicate recognition
        self.assertRaises(ValueError, register_simulation_module,
                          Model, BallBeamModel)
        self.assertRaises(ValueError, register_simulation_module,
                          Controller, FController)
        self.assertRaises(ValueError, register_processing_module,
                          PostProcessingModule, EvalA1)
        # self.assertRaises(ValueError, register_processing_module,
        #                   MetaProcessingModule, XYMetaProcessor)
        self.assertRaises(ValueError, register_visualizer,
                          MplBallBeamVisualizer)


class TestGetterCalls(unittest.TestCase):
    def setUp(self):
        # registration of generic modules is done in __init__.py
        pass

    def test_generic_calls(self):
        """
        check whether all generic simulation and postprocessing modules are
        registered using the general getter call
        """
        # ----------------------
        # simulation

        # solver
        self.assertTrue((ODEInt, "ODEInt")
                        in get_registered_modules(SimulationModule, Solver))

        # trajectory generators
        self.assertTrue((SmoothTransition, "SmoothTransition")
                        in get_registered_modules(SimulationModule, Trajectory))
        self.assertTrue((HarmonicTrajectory, "HarmonicTrajectory")
                        in get_registered_modules(SimulationModule, Trajectory))
        self.assertTrue((Setpoint, "Setpoint")
                        in get_registered_modules(SimulationModule, Trajectory))

        # controllers
        self.assertTrue((PIDController, "PIDController")
                        in get_registered_modules(SimulationModule, Controller))

        # mixers
        self.assertTrue((AdditiveMixer, "AdditiveMixer")
                        in get_registered_modules(SimulationModule, ModelMixer))
        self.assertTrue((AdditiveMixer, "AdditiveMixer")
                        in get_registered_modules(SimulationModule, ObserverMixer))

        # limiter
        self.assertTrue((ModelInputLimiter, "ModelInputLimiter")
                        in get_registered_modules(SimulationModule, Limiter))

        # sensors
        self.assertTrue((DeadTimeSensor, "DeadTimeSensor")
                        in get_registered_modules(SimulationModule, Sensor))

        # disturbance
        self.assertTrue((GaussianNoise, "GaussianNoise")
                        in get_registered_modules(SimulationModule, Disturbance))

        # ----------------------
        # processing

        # post-processors
        self.assertTrue((StepResponse, "StepResponse")
                        in get_registered_modules(ProcessingModule,
                                                  PostProcessingModule))
        self.assertTrue((PlotAll, "PlotAll")
                        in get_registered_modules(ProcessingModule,
                                                  PostProcessingModule))
        # meta-processors
        # self.assertTrue((XYMetaProcessor, "XYMetaProcessor")
        #                 in get_registered_modules(ProcessingModule,
        #                                           MetaProcessingModule))

    def test_special_call(self):
        """
        special calls, same modules but different functions for access
        """
        # ----------------------
        # simulation

        self.assertTrue((PIDController, "PIDController")
                        in get_registered_simulation_modules(Controller))
        self.assertTrue((SmoothTransition, "SmoothTransition")
                        in get_registered_simulation_modules(Trajectory))
        self.assertTrue((HarmonicTrajectory, "HarmonicTrajectory")
                        in get_registered_simulation_modules(Trajectory))
        self.assertTrue((Setpoint, "Setpoint")
                        in get_registered_simulation_modules(Trajectory))

        # ----------------------
        # processing

        self.assertTrue(
            (StepResponse, "StepResponse")
            in get_registered_processing_modules(PostProcessingModule))
        self.assertTrue(
            (PlotAll, "PlotAll")
            in get_registered_processing_modules(PostProcessingModule))
        # self.assertTrue(
        #     (XYMetaProcessor, "XYMetaProcessor")
        #     in get_registered_processing_modules(MetaProcessingModule))

    def test_string_call(self):
        """
        the calls should also work with names instead of class objects
        """
        self.assertTrue(
            (ODEInt, "ODEInt")
            in get_registered_modules("SimulationModule", "Solver"))
        self.assertTrue(
            (StepResponse, "StepResponse")
            in get_registered_processing_modules("PostProcessingModule"))
        self.assertTrue(
            (PlotAll, "PlotAll")
            in get_registered_processing_modules("PostProcessingModule"))

    def test_visualizer_call(self):
        """
        test interface for visualizer
        """
        self.assertTrue((MplBallBeamVisualizer, "MplBallBeamVisualizer")
                        in get_registered_visualizers())

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
