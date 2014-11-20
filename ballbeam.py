#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import getopt
from time import sleep
import traceback

from trajectory import HarmonicGenerator, FixedPointGenerator
from control import PController, FController, GController, JController, LSSController, IOLController
from sim_core import Simulator
from model import BallBeamModel
from visualization import VtkVisualizer
from logging import Logger

from settings import dt

#--------------------------------------------------------------------- 
# Main Application
#--------------------------------------------------------------------- 
class BallBeam:
    '''
    This is the main application (it will get very fancy)
    '''

    model = None
    simulator = None
    visualizer = None
    logger = None
    run = False

    def __init__(self, initialState=None, logger=None):
        if logger is not None:
            self.logger = logger
        self.model = BallBeamModel(logger=logger)


        # Trajectory
        #self.trajG = HarmonicGenerator(logger=logger)
        #self.trajG.setAmplitude(0.5)
        self.trajG = FixedPointGenerator(logger=logger)
        self.trajG.setPosition(0)

        # Control
        self.cont = FController(logger=logger)
        #    cont = GController(trajG)
        #self.cont = JController(logger=logger)
        #self.cont = PController(logger=logger)
        #self.cont = LSSController(logger=logger)
        #self.cont = IOLController(logger=logger)

        self.simulator = Simulator(self.model, initialState, \
                trajectory=self.trajG, controller=self.cont, \
                logger=logger)

    def setVisualizer(self, visualizer):
        self.visualizer = visualizer

    #TODO setController setTrajectory etc

    def run(self):
        self.run = True

        while self.run:
            q = self.simulator.calcStep()

            if self.visualizer is not None:
                r_beam, T_beam, r_ball, T_ball = self.model.calcPositions(q)
                self.visualizer.updateScene(r_beam, T_beam, r_ball, T_ball)

            sleep(dt)

    def stop(self):
        self.run = False

def process(arg):
    pass

def main():
    '''
    Ball and Bem Simulation Toolkit
    '''
    # parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)

    # process options
    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)
    
    # process arguments
    for arg in args:
        process(arg) 

    with Logger() as l:
        bb = BallBeam(initialState=[0, 0.2, 0, 0], logger=l)
        vis = VtkVisualizer()
        bb.setVisualizer(vis)

        #Run main application
        try:
            bb.run()
        except Exception, err:
            print traceback.format_exc()


if __name__ == "__main__":
    main()
        
