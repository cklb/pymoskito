#!/usr/bin/python
# -*- coding: utf-8 -*-

import time

import matplotlib.pyplot as plt 
plt.ion()
from settings import *

#--------------------------------------------------------------------- 
# data logging helper
#--------------------------------------------------------------------- 

class Logger:
    """ Main Data Logger
    """

    def __init__(self):
        self.subscribers = []
        self.data = {}
        self.timestep = 0
        self.filename = '../logs/'+time.strftime('%Y%m%d-%H%M%S')+'_logdata'

    def __enter__(self):
        return self

    def log(self, input_data):
        for key, val in input_data.iteritems():
            if key not in self.data:
                self.data.update({key: [val]})
            else:
                if len(self.data[key]) != self.timestep:
                    print 'ERROR in Logging Data! Too much input from: ', key
                    print self.timestep, '>',  len(self.data[key])
                self.data[key].append(val)

        if 't' in input_data:
            self.timestep += 1

        #update all subscriptions that got new data
        updated_callbacks = []
        for key, val in input_data.iteritems():
            for item in self.subscribers:
                if key in item[1] and item[0] not in updated_callbacks:
                    #build paket
                    paket = {}
                    for element in item[1]:
                        paket.update({element: self.data[element]})
                    #send it
                    item[0](paket)
                    #remember subscriber
                    updated_callbacks.append(item[0])
        return

    def subscribe(self, keys, callback):
        for item in self.subscribers:
            if item[0] == callback:
                item[1].append(keys)

        self.subscribers.append((callback, keys))

    def __exit__(self, exc_type, exc_value, traceback):
        ''' dump data to disk
        '''
        with open(self.filename, 'w+') as f:
            f.write(repr(self.data))
    
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
