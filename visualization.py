#!/usr/bin/python
# -*- coding: utf-8 -*-

#---------------------------------------------------------------------
# visualization of the simulation
#--------------------------------------------------------------------- 

import vtk
from settings import *

class VtkVisualizer:
    ren = None
    renWin = None

    beam = None
    beamMapper = None
    beamActor = None
    beamProp = None

    ball = None
    ballMapper = None
    ballActor = None
    ballProp = None

    vPlane = None
    vPlaneMapper = None
    vPlaneActor = None
    vPlaneProp = None

    iren = None

    def __init__(self):
        # create renderer and window
        self.ren = vtk.vtkRenderer()
        self.ren.SetBackground(1, 1, 1)
        self.renWin = vtk.vtkRenderWindow()
        self.renWin.SetSize(1000, 500)
        self.renWin.AddRenderer(ren)
        self.renWin.SetWindowName("Ball and Beam Simulation")

        #-------- add the beam ----
        # geometry
        self.beam = vtk.vtkCubeSource()
        self.beam.SetXLength(beam_length)
        self.beam.SetYLength(beam_width)
        self.beam.SetZLength(beam_depth)

        #mapper
        self.beamMapper = vtk.vtkPolyDataMapper()
        self.beamMapper.SetInputConnection(self.beam.GetOutputPort())

        # actor
        self.beamActor = vtk.vtkLODActor()
        self.beamActor.SetMapper(self.beamMapper)
        self.beamActor.SetScale(scale)

        #make it look nice
        self.beamProp = self.beamActor.GetProperty()
        self.beamProp.SetColor(0.3, 0.3, 0.3)
        self.beamProp.SetAmbient(0.2)
        self.beamProp.SetDiffuse(0.8)
        self.beamProp.SetSpecular(0.5)
        self.beamProp.SetSpecularPower(0.5)

        self.ren.AddActor(self.beamActor)

        #-------- add the ball ----
        # geometry
        self.ball = vtk.vtkSphereSource()
        self.ball.SetRadius(R)
        self.ball.SetThetaResolution(20)
        self.ball.SetPhiResolution(20)

        # mapper
        self.ballMapper = vtk.vtkPolyDataMapper()
        self.ballMapper.SetInputConnection(self.ball.GetOutputPort())

        # actor
        self.ballActor = vtk.vtkLODActor()
        self.ballActor.SetMapper(self.ballMapper)
        self.ballActor.SetScale(scale)

        # make it look nice
        self.ballProp = self.ballActor.GetProperty()
        self.ballProp.SetColor(1, 1, 0)
        self.ballProp.SetAmbient(0.2)
        self.ballProp.SetDiffuse(0.8)
        self.ballProp.SetSpecular(0.5)
        self.ballProp.SetSpecularPower(0.5)

        self.ren.AddActor(self.ballActor)

        -------- add the back ----
        # geometry
        self.vPlane = vtk.vtkPlaneSource()
        self.vPlane.SetCenter(0, 0, -0.1)
        self.vPlane.SetNormal(0, 0, 1)

        # mapper
        self.vPlaneMapper = vtk.vtkPolyDataMapper()
        self.vPlaneMapper.SetInputConnection(self.vPlane.GetOutputPort())

        # actor
        self.vPlaneActor = vtk.vtkLODActor()
        self.vPlaneActor.SetMapper(self.vPlaneMapper)
        self.vPlaneActor.SetScale(2.5,1,1)

        # make it look nice
        self.vPlaneProp = self.vPlaneActor.GetProperty()
        col = [0.78125, 0.4570, 0.119]
        self.vPlaneProp.SetColor([x*0.7 for x in col])
        self.vPlaneProp.SetAmbient(0.2)
        self.vPlaneProp.SetDiffuse(0.8)
        self.vPlaneProp.SetSpecular(0.5)
        self.vPlaneProp.SetSpecularPower(0.5)

        self.ren.AddActor(self.vPlaneActor)


        # get everybody into the frame
        self.ren.ResetCamera()
        self.ren.GetActiveCamera().Zoom(2)

        # setup the interactor
        self.iren = vtk.vtkRenderWindowInteractor()
        self.iren.SetRenderWindow(self.renWin)
        self.ren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        self.ren.Initialize()

    def setBodyState(self, actor, r, T):
        poke = vtk.vtkMatrix4x4()
        
        for i in range(3):
            for n in range(3):
                poke.SetElement(i, n, T[i, n])
            poke.SetElement(i, 3, r[i])

        actor.PokeMatrix(poke)

    def updateScene(self, r_beam, T_beam, r_ball, T_ball):
        ''' 
        update the body states 
        '''
        setBodyState(self.beamActor, r_beam, T_beam)
        setBodyState(self.ballActor, r_ball, T_ball)

        self.renWin.Render()

