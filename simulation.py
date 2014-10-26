#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
# Rendering Tests

import vtk
from time import sleep
from numpy import sin, cos, pi
from numpy import array as narray
from scipy.integrate import ode

#---------------------------------------------------------------------
# global settings
#--------------------------------------------------------------------- 
dt = 0.01       # stepwidth
q0 = [0, 0.1, 0, 0]    # initial minimal state vector (r, dr, theta, dtheta)'

M = 0.05    #kg
R = 0.01    #m
J = 0.02    #kgm^2
Jb = 2e-6   #kgm^2
G = 9.81    #m/s^2
l = 0.5     #m
beam_width = 0.01
beam_depth = 0.03

scale = 1

#---------------------------------------------------------------------
# model equations
#---------------------------------------------------------------------
def calcTrajectory(t):
    '''
    Calculates desired trajectory for ball position
    '''

    #TODO
    A = 1
    #A = 2
    #A = 3
    yd = A * cos(pi*t/5)

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
    B = M/(Jb/R**2+M)
    dx2 = B*(x1*x4**2 - G*sin(x3))
    dx3 = x4

    #choose controller
    tau = 0
#    tau = p_controller(calcTrajectory(t), y)

    u = (tau - M* (2*x1*x2*x4 + G*x1*cos(x3))) / (M*x1**2 + J + Jb)
    dx4 = u

    return [dx1, dx2, dx3, dx4]

#---------------------------------------------------------------------
# controller
#---------------------------------------------------------------------
def p_controller(yd, y):
    Kp = 10
    return  Kp*(yd-y)

#---------------------------------------------------------------------
# solver
#---------------------------------------------------------------------
solver = ode(rhs)
solver.set_initial_value(q0)
solver.set_integrator('vode', method='adams', rtol=1e-6, atol=1e-9)


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

    if abs(r_ball[1]) > l :
        print '\n###################################### \n#  Ball fell down -> exiting application.'
        quit()


#------- visualisation --------------------------------
# create renderer and window
ren = vtk.vtkRenderer()
ren.SetBackground(1, 1, 1)
renWin = vtk.vtkRenderWindow()
renWin.SetSize(500, 500)
renWin.AddRenderer(ren)


#-------- add the beam ----
# geometry
beam = vtk.vtkCubeSource()
beam.SetXLength(l)
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
ballProp.SetColor(0, 0.8, 0.3)
ballProp.SetAmbient(0.2)
ballProp.SetDiffuse(0.8)
ballProp.SetSpecular(0.5)
ballProp.SetSpecularPower(0.5)

ren.AddActor(ballActor)

# get everybody into the frame
ren.ResetCamera()

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

    
