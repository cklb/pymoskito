#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import getopt
from time import sleep

from trajectory import HarmonicGenerator
from control import FController
from sim_core import Simulator
from model import BallBeamModel
from visualization import VtkVisualizer

#--------------------------------------------------------------------- 
# Main Application
#--------------------------------------------------------------------- 
class BallBeam:
    '''
    This is the main application launcher (it will get very fancy)
    '''

    model = None
    simulator = None
    run = False

    def __init__(self, controller):
        self.model = BallBeamModel(controller)
        self.simulator = Simulator(self.model)

    def run(self):
        self.run = True
        while self.run:
            t, q = self.simulator.calcStep()
            print t, ':\t', q

            if self.logger is not None:
                logger.log(t,q)

            if self.visualizer is not None:
                r_beam, T_beam, r_ball, T_ball = model.calcPositions(q)
                visualizer.updateScene(r_beam, T_beam, r_ball, T_ball)

            sleep(0.01)

    def stop(self):
        self.run = False


def process(arg):
    pass

def main():
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

    # TODO get these from cmd line
    trajG = HarmonicGenerator()
    cont = FController(trajG)

    bb = BallBeam(cont)

    bb.run()

    try:
        bb.run()
    except:
        bb.stop()


    ''' TODO
    # process arguments
    for arg in args:
        process(arg) # process() is defined elsewhere
    '''

if __name__ == "__main__":
    main()
        
