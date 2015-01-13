#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import division

#---------------------------------------------------------------------
# visualization of the simulation
#--------------------------------------------------------------------- 

import vtk
import settings as st

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

    def __init__(self, parent):
        # create renderer and window
        self.ren = vtk.vtkRenderer()
        self.parent = parent
        parent.GetRenderWindow().AddRenderer(self.ren)

        #-------- add the beam ----
        # geometry
        self.beam = vtk.vtkCubeSource()
        self.beam.SetXLength(st.visBeamLength)
        self.beam.SetYLength(st.visBeamWidth)
        self.beam.SetZLength(st.visBeamDepth)

        #mapper
        self.beamMapper = vtk.vtkPolyDataMapper()
        self.beamMapper.SetInputConnection(self.beam.GetOutputPort())

        # actor
        self.beamActor = vtk.vtkLODActor()
        self.beamActor.SetMapper(self.beamMapper)

        #make it look nice
        self.beamProp = self.beamActor.GetProperty()
        self.beamProp.SetColor(101/255, 123/255, 131/255)

        self.ren.AddActor(self.beamActor)

        #-------- add the ball ----
        # geometry
        self.ball = vtk.vtkSphereSource()
        self.ball.SetRadius(st.visR)
        self.ball.SetThetaResolution(20)
        self.ball.SetPhiResolution(20)

        # mapper
        self.ballMapper = vtk.vtkPolyDataMapper()
        self.ballMapper.SetInputConnection(self.ball.GetOutputPort())

        # actor
        self.ballActor = vtk.vtkLODActor()
        self.ballActor.SetMapper(self.ballMapper)

        # make it look nice
        self.ballProp = self.ballActor.GetProperty()
        self.ballProp.SetColor(255/255, 255/255, 0)
        self.ballProp.SetAmbient(0.2)
        self.ballProp.SetDiffuse(0.8)
        self.ballProp.SetSpecular(0.5)
        self.ballProp.SetSpecularPower(0.5)

        self.ren.AddActor(self.ballActor)

        #add background
        self.ren.GradientBackgroundOn()
        self.ren.SetBackground(228/255, 232/255, 213/255)
        self.ren.SetBackground2(38/255, 139/255, 210/255)

        # get everybody into the frame
        self.ren.ResetCamera()
        self.ren.GetActiveCamera().Zoom(1.7)

        # setup the interactor
        self.iren = parent.GetRenderWindow().GetInteractor()
        self.iren.Initialize()

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
        self.setBodyState(self.beamActor, r_beam, T_beam)
        self.setBodyState(self.ballActor, r_ball, T_ball)

        self.parent.GetRenderWindow().Render()

