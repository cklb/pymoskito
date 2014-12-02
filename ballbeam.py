#!/usr/bin/python
# -*- coding: utf-8 -*-

#system
import sys
import getopt
from time import sleep
import traceback

#own
from trajectory import HarmonicGenerator, FixedPointGenerator
from control import PController, FController, GController, JController, LSSController, IOLController
from sim_core import Simulator
from model import BallBeamModel, ModelException
from visualization import VtkVisualizer
from logging import DataLogger

from settings import dt

#--------------------------------------------------------------------- 
# 
#--------------------------------------------------------------------- 
class BallBeam:
    '''
    This is the main class
    '''

    model = None
    simulator = None
    visualizer = None
    logger = None
    run = False

    def __init__(self, initialState=None, logger=None):
        if logger is not None:
            self.logger = logger

        #TODO let those be set dynamically
        self.model = BallBeamModel(logger=logger)

        # Trajectory
        self.trajG = HarmonicGenerator(logger=logger)
        self.trajG.setAmplitude(0.5)
        #self.trajG = FixedPointGenerator(logger=logger)
        #self.trajG.setPosition(0.5)

        # Control
        #self.cont = FController(logger=logger)
        #self.cont = GController(logger=logger)
        #self.cont = JController(logger=logger)
        #self.cont = PController(logger=logger)
        self.cont = LSSController(logger=logger)
        #self.cont = IOLController(logger=logger)

        self.simulator = Simulator(self.model, initialState, \
                trajectory=self.trajG, controller=self.cont, \
                logger=logger)


    def setModel(self, model):
        self.model = model

    def setController(self, controller):
        self.cont = controller

    def setTrajectoryGenerator(self, generator):
        self.trajG = generator

    def setVisualizer(self, visualizer):
        self.visualizer = visualizer

    #TODO setController setTrajectory etc

    def update(self):
        try:
            q = self.simulator.calcStep()

            if self.visualizer is not None:
                r_beam, T_beam, r_ball, T_ball = self.model.calcPositions(q)
                self.visualizer.updateScene(r_beam, T_beam, r_ball, T_ball)

        except ModelException as e:
            print 'Model ERROR: ', e.args[0]
            raise Exception('Error in Maineventloop.')

