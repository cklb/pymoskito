#!/usr/bin/python
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt 
plt.ion()
from settings import *

#--------------------------------------------------------------------- 
# data logging helper
#--------------------------------------------------------------------- 
class Logger:
    """ base class for data logger
    """


    def __init__(self, dimensions):
        self.dim = dimensions
        self.data = {}
        self.data['x'] = []
        self.data['y'] = []
        for i in range(self.dim):
            self.data['y'].append([])


    def log(self, data):
        print 'ERROR not there yet!'
        return


    def finalize(self):
        ''' dump data to disk
        '''
        #TODO
    
class GraphLogger(Logger):
    ''' 
    Provides y(x) plotting for data
    '''


    def __init__(self, name='Untitled', dimensions=1, yonly=False, x_range=[0, 10]):
        Logger.__init__(self, dimensions)

        self.yonly = yonly
        #create a plot for every dimension
        self.figure, self.axes = plt.subplots(self.dim, sharex=True)
        self.lines = []
        for i in range(self.dim):
            if yonly:
                self.lines.append(self.axes.plot([], [], 'b-')[0])
                self.axes.set_autoscalex_on(True)
                self.axes.set_autoscaley_on(True)
                self.axes.grid()
            else:
                self.lines.append(self.axes[i].plot([], [], 'b-')[0])
                self.axes[i].set_autoscaley_on(True)
                self.axes[i].set_xlim(x_range)
                self.axes[i].grid()

    def log(self, x, y):
        '''
        expects 1 value for x-axis and a list of values for y-axis
        '''
        if x is not None:
            self.data['x'].append(x)
        else:
            if len(self.data['x']) == 0:
                self.data['x'].append(0)
            else:
                self.data['x'].append(self.data['x'][-1] + 1)

        if len(y) != self.dim:
            print 'Error: Y-Data corrupt:', len(y), '!=', self.dim
            return

        for index, val in enumerate(y):
            self.data['y'][index].append(val)
        
        self.takeAction()

    def takeAction(self):
        ''' 
        Implements the actual plotting
        '''

        for index, line in enumerate(self.lines):
            line.set_xdata(self.data['x'])
            line.set_ydata(self.data['y'][index])
            if self.yonly:
                self.axes.relim()
                self.axes.autoscale_view()
            else:
                self.axes[index].relim()
                self.axes[index].autoscale_view()

        self.figure.canvas.draw()
        self.figure.canvas.flush_events()
        return

class QtGraphLogger(Logger):
    ''' 
    Provides y(x) plotting for data
    '''


    def __init__(self, name='Untitled', dimensions=1, yonly=False, x_range=[0, 10]):
        Logger.__init__(self, dimensions)



        

        self.yonly = yonly
        #create a plot for every dimension
        self.figure, self.axes = plt.subplots(self.dim, sharex=True)
        self.lines = []
        for i in range(self.dim):
            if yonly:
                self.lines.append(self.axes.plot([], [], 'b-')[0])
                self.axes.set_autoscalex_on(True)
                self.axes.set_autoscaley_on(True)
                self.axes.grid()
            else:
                self.lines.append(self.axes[i].plot([], [], 'b-')[0])
                self.axes[i].set_autoscaley_on(True)
                self.axes[i].set_xlim(x_range)
                self.axes[i].grid()

    def log(self, x, y):
        '''
        expects 1 value for x-axis and a list of values for y-axis
        '''
        if x is not None:
            self.data['x'].append(x)
        else:
            if len(self.data['x']) == 0:
                self.data['x'].append(0)
            else:
                self.data['x'].append(self.data['x'][-1] + 1)

        if len(y) != self.dim:
            print 'Error: Y-Data corrupt:', len(y), '!=', self.dim
            return

        for index, val in enumerate(y):
            self.data['y'][index].append(val)
        
        self.takeAction()

    def takeAction(self):
        ''' 
        Implements the actual plotting
        '''

        for index, line in enumerate(self.lines):
            line.set_xdata(self.data['x'])
            line.set_ydata(self.data['y'][index])
            if self.yonly:
                self.axes.relim()
                self.axes.autoscale_view()
            else:
                self.axes[index].relim()
                self.axes[index].autoscale_view()

        self.figure.canvas.draw()
        self.figure.canvas.flush_events()
        return
