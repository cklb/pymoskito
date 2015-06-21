# -*- coding: utf-8 -*-

from __future__ import division
import numpy as np
import vtk

from pymoskito.visualization import Visualizer

import settings as st


class BallInTubeVisualizer(Visualizer):

    def __init__(self, renderer):
        Visualizer.__init__(self)

        assert isinstance(renderer, vtk.vtkRenderer)
        self.ren = renderer

        # -------- add a line ----
        # geometry
        self.line = vtk.vtkLineSource()
        self.line.SetPoint1(0, 0, 0)
        self.line.SetPoint2(0, +st.visTubeLength, 0)

        # mapper
        self.lineMapper = vtk.vtkPolyDataMapper()
        self.lineMapper.SetInputConnection(self.line.GetOutputPort())

        # actor
        self.lineActor = vtk.vtkLODActor()
        self.lineActor.SetMapper(self.lineMapper)

        # make it look nice
        self.lineProp = self.lineActor.GetProperty()
        self.lineProp.SetOpacity(0.0)

        self.ren.AddActor(self.lineActor)

        # -------- add a tube around the line ----
        # geometry
        self.tube = vtk.vtkTubeFilter()
        self.tube.SetNumberOfSides(100)
        self.tube.SetInputConnection(self.line.GetOutputPort())
        self.tube.SetRadius(st.visTubeDiameter/2)

        # mapper
        self.tubeMapper = vtk.vtkPolyDataMapper()
        self.tubeMapper.SetInputConnection(self.tube.GetOutputPort())

        # actor
        self.tubeActor = vtk.vtkLODActor()
        self.tubeActor.SetMapper(self.tubeMapper)

        # make it look nice
        self.tubeProp = self.tubeActor.GetProperty()
        self.tubeProp.SetColor(101/255, 123/255, 131/255)
        self.tubeProp.SetOpacity(0.5)

        self.ren.AddActor(self.tubeActor)

        # -------- add the ball ----
        # geometry
        self.ball = vtk.vtkSphereSource()
        self.ball.SetRadius(st.visBallDiameter/2)
        self.ball.SetThetaResolution(30)
        self.ball.SetPhiResolution(30)
        self.ball.SetCenter(0, st.visBallDiameter/2, 0)

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

        # -------- add background ----
        self.ren.GradientBackgroundOn()
        self.ren.SetBackground(228/255, 232/255, 213/255)
        self.ren.SetBackground2(38/255, 139/255, 210/255)

        # get everybody into the frame
        self.ren.ResetCamera()
        self.ren.GetActiveCamera().Zoom(1.0)

    def calc_positions(self, x):
        """
        Calculate stationary vectors and rot. matrices for bodies
        """
        # not used, because the fan is not visualized
        # r_fan = np.zeros(3)
        # t_fan = np.zeros((3, 3))

        r_ball = np.array([0, x[2]/st.scale, 0])
        t_ball = np.eye(3)

        return [r_ball, t_ball]

    def set_body_state(self, actor, r, t):
        poke = vtk.vtkMatrix4x4()

        for i in range(3):
            for n in range(3):
                poke.SetElement(i, n, t[i, n])
            poke.SetElement(i, 3, r[i])

        actor.PokeMatrix(poke)

    def update_scene(self, x):
        """
        update the body states
        """
        r_ball, t_ball = self.calc_positions(x)
        self.set_body_state(self.ballActor, r_ball, t_ball)

