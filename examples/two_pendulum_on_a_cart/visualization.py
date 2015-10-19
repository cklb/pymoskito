# -*- coding: utf-8 -*-

from __future__ import division
import numpy as np
import vtk

from pymoskito.visualization import Visualizer

import settings as st


class TwoPendulumVisualizer(Visualizer):

    def __init__(self, renderer):
        Visualizer.__init__(self)

        assert isinstance(renderer, vtk.vtkRenderer)
        self.ren = renderer

        # # -------- add the beam ----
        # # geometry
        # self.beam = vtk.vtkCubeSource()
        # self.beam.SetXLength(st.beam_length)
        # self.beam.SetYLength(st.beam_width)
        # self.beam.SetZLength(st.beam_depth)
        #
        # # mapper
        # self.beamMapper = vtk.vtkPolyDataMapper()
        # self.beamMapper.SetInputConnection(self.beam.GetOutputPort())
        #
        # # actor
        # self.beamActor = vtk.vtkLODActor()
        # self.beamActor.SetMapper(self.beamMapper)
        #
        # # make it look nice
        # self.beamProp = self.beamActor.GetProperty()
        # self.beamProp.SetColor(101 / 255, 123 / 255, 131 / 255)
        #
        # self.ren.AddActor(self.beamActor)

        # -------- add cart ----
        # geometry
        self.cart = vtk.vtkCubeSource()
        self.cart.SetXLength(st.cart_length)
        self.cart.SetYLength(st.cart_width)
        self.cart.SetZLength(st.cart_depth)

        # mapper
        self.cartMapper = vtk.vtkPolyDataMapper()
        self.cartMapper.SetInputConnection(self.cart.GetOutputPort())

        # actor
        self.cartActor = vtk.vtkLODActor()
        self.cartActor.SetPosition(0, 0, 0)
        self.cartActor.RotateWXYZ(0, 1, 0, 0)
        self.cartActor.SetMapper(self.cartMapper)

        # make it look nice
        self.cartProp = self.cartActor.GetProperty()
        self.cartProp.SetColor(101 / 255, 123 / 255, 131 / 255)
        self.ren.AddActor(self.cartActor)

        # -------- add axis ----
        # geometry
        self.axis = vtk.vtkCylinderSource()
        self.axis.SetHeight(st.axis_height)
        self.axis.SetRadius(st.axis_radius)
        self.axis.SetResolution(100)

        # mapper
        self.axis_Mapper = vtk.vtkPolyDataMapper()
        self.axis_Mapper.SetInputConnection(self.axis.GetOutputPort())

        # actor
        self.axis_Actor = vtk.vtkLODActor()
        self.axis_Actor.SetPosition(0, 0, st.cart_depth/2 + st.axis_height/2)
        self.axis_Actor.RotateX(90)
        self.axis_Actor.SetMapper(self.axis_Mapper)

        # make it look nice
        self.axis_Prop = self.axis_Actor.GetProperty()
        self.axis_Prop.SetColor(90 / 255, 123 / 255, 131 / 255)

        self.ren.AddActor(self.axis_Actor)

        # -------- add short pendulum ----
        # add short pendulum shaft
        # geometry
        self.short_pendulum_shaft = vtk.vtkCylinderSource()
        self.short_pendulum_shaft.SetHeight(st.pendulum_shaft_height)
        self.short_pendulum_shaft.SetRadius(st.pendulum_shaft_radius)
        self.short_pendulum_shaft.SetResolution(100)

        # mapper
        self.short_pendulum_shaft_Mapper = vtk.vtkPolyDataMapper()
        self.short_pendulum_shaft_Mapper.SetInputConnection(self.short_pendulum_shaft.GetOutputPort())

        # actor
        self.short_pendulum_shaft_Actor = vtk.vtkLODActor()
        self.short_pendulum_shaft_Actor.SetPosition(0,
                                                    0,
                                                    st.cart_depth/2 + st.axis_height + st.pendulum_shaft_height/2)
        self.short_pendulum_shaft_Actor.RotateX(90)
        self.short_pendulum_shaft_Actor.SetMapper(self.short_pendulum_shaft_Mapper)

        # make it look nice
        self.short_pendulum_shaft_Prop = self.short_pendulum_shaft_Actor.GetProperty()
        self.short_pendulum_shaft_Prop.SetColor(90 / 255, 123 / 255, 131 / 255)

        self.ren.AddActor(self.short_pendulum_shaft_Actor)

        # add short pendulum
        # geometry
        self.short_pendulum = vtk.vtkCylinderSource()
        self.short_pendulum.SetHeight(st.short_pendulum_height)
        self.short_pendulum.SetRadius(st.short_pendulum_radius)
        self.short_pendulum.SetResolution(100)

        # mapper
        self.short_pendulum_Mapper = vtk.vtkPolyDataMapper()
        self.short_pendulum_Mapper.SetInputConnection(self.short_pendulum.GetOutputPort())

        # actor
        self.short_pendulum_Actor = vtk.vtkLODActor()
        self.short_pendulum_Actor.SetPosition(0,
                                        -st.short_pendulum_height/2,
                                        st.cart_depth/2 + st.axis_height + st.pendulum_shaft_height/2)
        self.short_pendulum_Actor.RotateWXYZ(0, 1, 0, 0)
        self.short_pendulum_Actor.SetMapper(self.short_pendulum_Mapper)

        # make it look nice
        self.short_pendulum_Prop = self.short_pendulum_Actor.GetProperty()
        self.short_pendulum_Prop.SetColor(90 / 255, 123 / 255, 131 / 255)

        self.ren.AddActor(self.short_pendulum_Actor)

        # add short pendulum weight
        # geometry
        self.short_pendulum_weight = vtk.vtkCylinderSource()
        self.short_pendulum_weight.SetHeight(st.pendulum_weight_height)
        self.short_pendulum_weight.SetRadius(st.pendulum_weight_radius)
        self.short_pendulum_weight.SetResolution(100)

        # mapper
        self.short_pendulum_weight_Mapper = vtk.vtkPolyDataMapper()
        self.short_pendulum_weight_Mapper.SetInputConnection(self.short_pendulum_weight.GetOutputPort())

        # actor
        self.short_pendulum_weight_Actor = vtk.vtkLODActor()
        self.short_pendulum_weight_Actor.SetPosition(0,
                                                     -(st.short_pendulum_height + st.pendulum_weight_height/2),
                                                     st.cart_depth/2 + st.axis_height + st.pendulum_shaft_height/2)
        self.short_pendulum_weight_Actor.RotateWXYZ(0, 1, 0, 0)
        self.short_pendulum_weight_Actor.SetMapper(self.short_pendulum_weight_Mapper)

        # make it look nice
        self.short_pendulum_weight_Prop = self.short_pendulum_weight_Actor.GetProperty()
        # self.short_pendulum_weight_Prop.SetColor(90 / 255, 123 / 255, 131 / 255)

        self.ren.AddActor(self.short_pendulum_weight_Actor)



        # # -------- add the ball ----
        # # geometry
        # self.ball = vtk.vtkSphereSource()
        # self.ball.SetRadius(0.3)
        # self.ball.SetThetaResolution(20)
        # self.ball.SetPhiResolution(20)
        #
        # # mapper
        # self.ballMapper = vtk.vtkPolyDataMapper()
        # self.ballMapper.SetInputConnection(self.ball.GetOutputPort())
        #
        # # actor
        # self.ballActor = vtk.vtkLODActor()
        # self.ballActor.SetMapper(self.ballMapper)
        #
        # # make it look nice
        # self.ballProp = self.ballActor.GetProperty()
        # self.ballProp.SetColor(255 / 255, 255 / 255, 0)
        # self.ballProp.SetAmbient(0.2)
        # self.ballProp.SetDiffuse(0.8)
        # self.ballProp.SetSpecular(0.5)
        # self.ballProp.SetSpecularPower(0.5)
        #
        # self.ren.AddActor(self.ballActor)

        # add background
        self.ren.GradientBackgroundOn()
        self.ren.SetBackground(228 / 255, 232 / 255, 213 / 255)
        self.ren.SetBackground2(38 / 255, 139 / 255, 210 / 255)

        # get everybody into the frame
        self.ren.ResetCamera()
        self.ren.GetActiveCamera().Zoom(1.7)

    def calc_positions(self, x):
        """
        Calculate stationary vectors and rot. matrices for bodies
        """
        positions = []
        # cart
        r_cart = np.array([x[0], 0, 0])
        t_cart = np.eye(3)
        positions.append(r_cart)
        positions.append(t_cart)
        # axis
        print self.axis_Actor.GetPosition()
        print self.axis_Actor.GetMatrix()
        print self.axis_Actor.GetOrientation()
        r_axis = np.array([x[0], 0, self.axis_Actor.GetPosition()[2]])
        t_axis = np.eye(3)
        positions.append(r_axis)
        positions.append(t_axis)

        # # beam
        # t_beam = np.array([[np.cos(x[2]), -np.sin(x[2]), 0],
        #                    [np.sin(x[2]), np.cos(x[2]), 0],
        #                    [0, 0, 1]])
        # r_beam0 = np.array([0, -st.visR - st.visBeamWidth / 2, 0])
        # r_beam = np.dot(t_beam, r_beam0)
        #
        # # ball
        # r_ball0 = np.array([x[0], 0, 0])
        # r_ball = np.dot(t_beam, r_ball0)
        # phi = x[0] / st.visR
        # t_ball = np.array([[np.cos(phi), -np.sin(phi), 0],
        #                    [np.sin(phi), np.cos(phi), 0],
        #                    [0, 0, 1]])

        return positions

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
        r_cart, t_cart, r_axis, t_axis = self.calc_positions(x)
        self.set_body_state(self.cartActor, r_cart, t_cart)
        self.set_body_state(self.axis_Actor, r_axis, t_axis)
