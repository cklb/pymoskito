#!/usr/bin/python
# -*- coding: utf-8 -*-


from __future__ import division
from scipy.integrate import ode

from settings import *

#--------------------------------------------------------------------- 
# Core of the physical simulation
#--------------------------------------------------------------------- 
class Simulator:
    """Simulation Wrapper"""

    traj_gen = None
    controller = None
    model = None
    solver = None
    logger = None
    visualizer = None

    def __init__(self, model):
        # model
        self.model = model

        # solver
        self.solver = ode(model.stateFunc)
        self.solver.set_initial_value(q0)
        self.solver.set_integrator(int_mode, method=int_method, rtol=int_rtol, atol=int_atol)

    def set_visualizer(self, visualizer_cb):
        self.visualizer = visualizer_cb

    def set_logger(self, logger_cb):
        self.logger = logger_cb

    def calcStep(self):
        '''
        Calcualte one step in simulation
        '''

        return self.solver.t, self.solver.integrate(self.solver.t+dt)

#TODO vv
'''
#---------------------------------------------------------------------
# plotting 
#---------------------------------------------------------------------
table = vtk.vtkTable()
#Time:
arrTime = vtk.vtkFloatArray()
arrTime.SetName("time")
#Error: yd-r
arrE = vtk.vtkFloatArray()
arrE.SetName("epsilon")
#psi3
arrPsi3 = vtk.vtkFloatArray()
arrPsi3.SetName("psi3")
#theta
arrTheta = vtk.vtkFloatArray()
arrTheta.SetName("theta")
#tau
arrTau = vtk.vtkFloatArray()
arrTau.SetName("tau")
# add rows to table 
table.AddColumn(arrTime)
table.AddColumn(arrE)
table.AddColumn(arrTheta)
table.AddColumn(arrPsi3)
table.AddColumn(arrTau)


print '\n-> End of Simulation dumping measurements:'
table.Dump(6)

done = False
while not done:
    fileName = '../measurements/' + raw_input('Please specify filename: ') + '.vtk'
    if os.path.isfile(fileName):
        if raw_input('file already exists, overwrite? (y/n)') == 'y':
            done = True
    else:
        done  = True
    
print 'saving to', fileName

tWriter = vtk.vtkTableWriter()
tWriter.SetInputData(table)
tWriter.SetFileName(fileName)
tWriter.Update()
'''
