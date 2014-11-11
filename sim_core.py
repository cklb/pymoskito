#!/usr/bin/python
# -*- coding: utf-8 -*-

#---------------------------------------------------------------------
# Core of the physical simulation
#--------------------------------------------------------------------- 

#import vtk
#import os.path
#from time import sleep

from __future__ import division

from numpy import sin, cos, pi
from numpy import array as narray
from scipy.integrate import ode

import settings

class Simulator:
    """Simulation Wrapper"""

    traj_gen = None
    controller = None
    solver = None
    logger = None
    visualizer = None

    def __init__(self, trajectory_generator, controller):
        self.traj_gen = trajectory_generator
        self.controller = controller

        # solver
        self.solver = ode(rhs)
        self.solver.set_initial_value(q0)
        self.solver.set_integrator(int_mode, method=int_method, rtol=int_rtol, atol=int_atol)

    def set_visualizer(self, visualizer_cb):
        self.visualizer = visualizer_cb

    def set_logger(self, logger_cb):
        self.logger = logger_cb

    def run(self):



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

#---------------------------------------------------------------------
# trajectory generation
#---------------------------------------------------------------------
def calcTrajectory(t,order):
    '''
    Calculates desired trajectory for ball position
    '''
    #TODO
    A = 1
    #A = 2
    #A = 3
    yd_0 = A * cos(pi*t/5)
    yd_1 = -A * (pi/5) * sin(pi*t/5)
    yd_2 = -A * (pi/5)**2 * cos(pi*t/5)
    yd_3 = A * (pi/5)**3 * sin(pi*t/5)
    yd_4 = A * (pi/5)**4 * cos(pi*t/5)
    yd_derivates = [yd_0 , yd_1 , yd_2 , yd_3 , yd_4]
    yd = []
        
    for i in range(order+1):
        yd.append(yd_derivates[i])
         
    return yd

#---------------------------------------------------------------------
# model equations
#---------------------------------------------------------------------
def rhs(t, q):
    '''
    Calculations of system state changes
    '''
    #definitoric
    x1 = q[0]
    x2 = q[1]
    x3 = q[2]
    x4 = q[3]
    y= x1

    dx1 = x2
    dx2 = B*(x1*x4**2 - G*sin(x3))
    dx3 = x4

    #choose controller
    tau = 0
#    tau = p_controller(t,q)
#    tau = f_controller(t,q)

    u = (tau - M* (2*x1*x2*x4 + G*x1*cos(x3))) / (M*x1**2 + J + Jb)
    dx4 = u

    #plotting data
    yd = calcTrajectory(t,0)
    new_row = [t, yd-x1, x3, 0, tau] #TODO psi3
    for i in range( table.GetNumberOfColumns()):
        table.GetColumn(i).InsertNextValue(new_row[i])

    return [dx1, dx2, dx3, dx4]

#---------------------------------------------------------------------
# controller
#---------------------------------------------------------------------
def p_controller(t,q):
    yd = calcTrajectory(t,0)
    x1 = q[0]
    x4 = q[3]
    # Kp for yd = 0.1 and dr = 0.01
    Kp = 8
    if yd<0:
        yd = yd*(-1)
    if (x1>-0.05 and x1<0.05) or x4==0:
        return 0
    # ball is on the right side
    if x1>0:
        return Kp*(yd-x1)
    
    # ball is on the left side
    if x1<0:
        return  Kp*(yd+x1)

# Controller for modification of f designed by Christoph
def f_controller(t,q):
    yd_0 , yd_1 , yd_2 , yd_3 , yd_4 = calcTrajectory(t,4)
    x1 = q[0]
    x2 = q[1]
    x3 = q[2]
    x4 = q[3]
    # gain of the controller
    k0 = 16
    k1 = 32
    k2 = 24
    k3 = 8
    
    # calculate nonlinear terms phi
    phi1 = x1
    phi2 = x2  
    phi3 = -B*G*sin(x3)
    phi4 = -B*G*x4*sin(x3)
    
    # calculate fictional input v
    v = yd_4 + k3*(yd_3 - phi4) + k2*(yd_2 - phi3) + k1*(yd_1 - phi2) + k0*(yd_0 - phi1)
    
    # calculate a(x)
    a = -B*G*cos(x3)
    # calculate b(x)
    b = B*G*x4**2*sin(x3)
    
    # calculate u
    u = (v-b)/a
    
    return u

    



#---------------------------------------------------------------------
#
#---------------------------------------------------------------------
def calcStep():
    '''
    Calcualte one step in simulation
    '''

    return solver.t, solver.integrate(solver.t+dt)


#---------------------------------------------------------------------
#
#---------------------------------------------------------------------
def calcPositions(q):
    '''
    Calculate stationary vectors and rot. matrices for bodies
    '''

    #beam
    r_beam = [0, -R/2 - beam_width, 0]
    T_beam = narray([[cos(q[2]), -sin(q[2]), 0], [sin(q[2]), cos(q[2]), 0], [0, 0, 1]])

    #ball
    r_ball = [cos(q[2])*q[0], sin(q[2])*q[0], 0]
    T_ball = narray([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

    return r_beam, T_beam, r_ball, T_ball

    
#---------------------------------------------------------------------
#
#---------------------------------------------------------------------
def setBodyState(actor, r, T):
    poke = vtk.vtkMatrix4x4()
    
    for i in range(3):
        for n in range(3):
            poke.SetElement(i, n, T[i, n])
        poke.SetElement(i, 3, r[i])

    actor.PokeMatrix(poke)
    
#---------------------------------------------------------------------
#
#---------------------------------------------------------------------
def updateScene(*args):
    '''
    Calculate new states and update the scene
    '''

    t, q = calcStep()
    print t,'\t', q
    r_beam, T_beam, r_ball, T_ball = calcPositions(q)

    setBodyState(beamActor, r_beam, T_beam)
    setBodyState(ballActor, r_ball, T_ball)

    renWin.Render()

    if abs(q[0]) > beam_length/2 :
        print '\n###################################### \n#  Ball fell down -> exiting application.'
        quit()
        raw_input('Simulation paused press Enter to continue')


#------- visualisation --------------------------------
# create renderer and window
ren = vtk.vtkRenderer()
ren.SetBackground(1, 1, 1)
renWin = vtk.vtkRenderWindow()
renWin.SetSize(1000, 500)
renWin.AddRenderer(ren)
renWin.SetWindowName("Ball and Beam Simulation")

#-------- add the beam ----
# geometry
beam = vtk.vtkCubeSource()
beam.SetXLength(beam_length)
beam.SetYLength(beam_width)
beam.SetZLength(beam_depth)

#mapper
beamMapper = vtk.vtkPolyDataMapper()
beamMapper.SetInputConnection(beam.GetOutputPort())

# actor
beamActor = vtk.vtkLODActor()
beamActor.SetMapper(beamMapper)
beamActor.SetScale(scale)

#make it look nice
beamProp = beamActor.GetProperty()
beamProp.SetColor(0.3, 0.3, 0.3)
beamProp.SetAmbient(0.2)
beamProp.SetDiffuse(0.8)
beamProp.SetSpecular(0.5)
beamProp.SetSpecularPower(0.5)

ren.AddActor(beamActor)

#-------- add the ball ----
# geometry
ball = vtk.vtkSphereSource()
ball.SetRadius(R)
ball.SetThetaResolution(20)
ball.SetPhiResolution(20)

#mapper
ballMapper = vtk.vtkPolyDataMapper()
ballMapper.SetInputConnection(ball.GetOutputPort())

# actor
ballActor = vtk.vtkLODActor()
ballActor.SetMapper(ballMapper)
ballActor.SetScale(scale)

#make it look nice
ballProp = ballActor.GetProperty()
ballProp.SetColor(1, 1, 0)
ballProp.SetAmbient(0.2)
ballProp.SetDiffuse(0.8)
ballProp.SetSpecular(0.5)
ballProp.SetSpecularPower(0.5)

ren.AddActor(ballActor)

#-------- add the back ----
# geometry
vPlane = vtk.vtkPlaneSource()
vPlane.SetCenter(0, 0, -0.1)
vPlane.SetNormal(0, 0, 1)

#mapper
vPlaneMapper = vtk.vtkPolyDataMapper()
vPlaneMapper.SetInputConnection(vPlane.GetOutputPort())

# actor
vPlaneActor = vtk.vtkLODActor()
vPlaneActor.SetMapper(vPlaneMapper)
vPlaneActor.SetScale(2.5,1,1)

#make it look nice
vPlaneProp = vPlaneActor.GetProperty()
col = [0.78125, 0.4570, 0.119]
vPlaneProp.SetColor([x*0.7 for x in col])
vPlaneProp.SetAmbient(0.2)
vPlaneProp.SetDiffuse(0.8)
vPlaneProp.SetSpecular(0.5)
vPlaneProp.SetSpecularPower(0.5)

ren.AddActor(vPlaneActor)


# get everybody into the frame
ren.ResetCamera()
ren.GetActiveCamera().Zoom(2)

# setup the interactor
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)
iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
iren.Initialize()
iren.AddObserver('TimerEvent', updateScene)
iren.CreateRepeatingTimer(20)

# Start the Simulation
iren.Start()

# End of Simulation
iren.GetRenderWindow().Finalize()

quit()

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
