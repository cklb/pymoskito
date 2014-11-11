#!/usr/bin/python
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt 
from settings import *

#--------------------------------------------------------------------- 
# data logging helper
#--------------------------------------------------------------------- 
class Logger:
    """ base class for data logger
    
    """

    data = []

    def __init__(self):
        pass

    def log(self, inputData):
        self.data.append(inputData)
        self.takeAction()

    def finalize(self):
        ''' dump data to disk
        '''
        #TODO
    
class GraphLogger(Logger):

    fig = None
    ax = None

    def __init__(self):
        Logger.__init__(self)
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        plt.show(block=False)

    def takeAction(self):
        return

        #TODO
        self.ax.plot([Logger.values[i][0] for i in range(len(Logger.values))], \
                [Logger.values[i][1][0] for i in range(len(Logger.values))])
        self.fig.canvas.draw()


