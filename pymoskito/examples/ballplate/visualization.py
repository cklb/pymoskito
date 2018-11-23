# -*- coding: utf-8 -*-
import numpy as np

import pymoskito as pm

import matplotlib as mpl
import matplotlib.patches
import matplotlib.transforms

from . import settings as st

HKS41K100 = '#0b2a51'
HKS44K100 = '#0059a3'
HKS44K80 = '#346FB2'
HKS36K100 = '#512947'
HKS33K100 = '#811a78'
HKS57K100 = '#007a47'
HKS65K100 = '#22ad36'
HKS07K100 = '#e87b14'
HKS07K80 = '#ef9c51'


try:
    import vtk

    class BallPlateVisualizer(pm.VtkVisualizer):

        def __init__(self, renderer):
            pm.VtkVisualizer.__init__(self, renderer)

            # -------- add the beam ----
            # geometry
            self.beam = vtk.vtkCubeSource()
            self.beam.SetXLength(st.visBeamLength)
            self.beam.SetYLength(st.visBeamWidth)
            self.beam.SetZLength(st.visBeamDepth)

            # mapper
            self.beamMapper = vtk.vtkPolyDataMapper()
            self.beamMapper.SetInputConnection(self.beam.GetOutputPort())

            # actor
            self.beamActor = vtk.vtkLODActor()
            self.beamActor.SetMapper(self.beamMapper)

            # make it look nice
            self.beamProp = self.beamActor.GetProperty()
            self.beamProp.SetColor(101 / 255, 123 / 255, 131 / 255)

            self.ren.AddActor(self.beamActor)

            # -------- add the other things ----
            # 1
            # geometry


            # Teil Fachwerk --
            # Teil Fachwerk_1
            # geometry
            self.Fachwerk_1 = vtk.vtkCubeSource()
            self.Fachwerk_1.SetXLength(0.1)
            self.Fachwerk_1.SetYLength(0.1)
            self.Fachwerk_1.SetZLength(st.Fachwerk_length)

            # mapper
            self.Fachwerk_1Mapper = vtk.vtkPolyDataMapper()
            self.Fachwerk_1Mapper.SetInputConnection(self.Fachwerk_1.GetOutputPort())

            # actor
            self.Fachwerk_1Actor = vtk.vtkLODActor()
            self.Fachwerk_1Actor.SetMapper(self.Fachwerk_1Mapper)

            # make it look nice
            self.Fachwerk_1Prop = self.Fachwerk_1Actor.GetProperty()
            self.Fachwerk_1Prop.SetColor(255 / 255, 255 / 255, 255 / 255)

            self.ren.AddActor(self.Fachwerk_1Actor)
            # Teil Fachwerk_2
            # geometry
            self.Fachwerk_2 = vtk.vtkCubeSource()
            self.Fachwerk_2.SetXLength(0.1)
            self.Fachwerk_2.SetYLength(0.1)
            self.Fachwerk_2.SetZLength(st.Fachwerk_length)

            # mapper
            self.Fachwerk_2Mapper = vtk.vtkPolyDataMapper()
            self.Fachwerk_2Mapper.SetInputConnection(self.Fachwerk_2.GetOutputPort())

            # actor
            self.Fachwerk_2Actor = vtk.vtkLODActor()
            self.Fachwerk_2Actor.SetMapper(self.Fachwerk_2Mapper)

            # make it look nice
            self.Fachwerk_2Prop = self.Fachwerk_2Actor.GetProperty()
            self.Fachwerk_2Prop.SetColor(255 / 255, 255 / 255, 255 / 255)

            self.ren.AddActor(self.Fachwerk_2Actor)
            # Teil Fachwerk_3
            # geometry
            self.Fachwerk_3 = vtk.vtkCubeSource()
            self.Fachwerk_3.SetXLength(st.Fachwerk_length)
            self.Fachwerk_3.SetYLength(0.1)
            self.Fachwerk_3.SetZLength(0.1)

            # mapper
            self.Fachwerk_3Mapper = vtk.vtkPolyDataMapper()
            self.Fachwerk_3Mapper.SetInputConnection(self.Fachwerk_3.GetOutputPort())

            # actor
            self.Fachwerk_3Actor = vtk.vtkLODActor()
            self.Fachwerk_3Actor.SetMapper(self.Fachwerk_3Mapper)

            # make it look nice
            self.Fachwerk_3Prop = self.Fachwerk_3Actor.GetProperty()
            self.Fachwerk_3Prop.SetColor(255 / 255, 255 / 255, 255 / 255)

            self.ren.AddActor(self.Fachwerk_3Actor)
            # Teil Fachwerk_4
            # geometry
            self.Fachwerk_4 = vtk.vtkCubeSource()
            self.Fachwerk_4.SetXLength(st.Fachwerk_length)
            self.Fachwerk_4.SetYLength(0.1)
            self.Fachwerk_4.SetZLength(0.1)

            # mapper
            self.Fachwerk_4Mapper = vtk.vtkPolyDataMapper()
            self.Fachwerk_4Mapper.SetInputConnection(self.Fachwerk_4.GetOutputPort())

            # actor
            self.Fachwerk_4Actor = vtk.vtkLODActor()
            self.Fachwerk_4Actor.SetMapper(self.Fachwerk_4Mapper)

            # make it look nice
            self.Fachwerk_4Prop = self.Fachwerk_4Actor.GetProperty()
            self.Fachwerk_4Prop.SetColor(255 / 255, 255 / 255, 255 / 255)

            self.ren.AddActor(self.Fachwerk_4Actor)

            # Teil Achse_1 --
            # geometry
            self.Achse_1 = vtk.vtkCubeSource()
            self.Achse_1.SetXLength(0.1)
            self.Achse_1.SetYLength(0.1)
            self.Achse_1.SetZLength(10)

            # mapper
            self.Achse_1Mapper = vtk.vtkPolyDataMapper()
            self.Achse_1Mapper.SetInputConnection(self.Achse_1.GetOutputPort())

            # actor
            self.Achse_1Actor = vtk.vtkLODActor()
            self.Achse_1Actor.SetMapper(self.Achse_1Mapper)

            # make it look nice
            self.Achse_1Prop = self.Achse_1Actor.GetProperty()
            self.Achse_1Prop.SetColor(255 / 255, 255 / 255, 255 / 255)

            self.ren.AddActor(self.Achse_1Actor)

            # Teil Achse_2_1 --
            # geometry
            self.Achse_2_1 = vtk.vtkCubeSource()
            self.Achse_2_1.SetXLength(2)
            self.Achse_2_1.SetYLength(0.1)
            self.Achse_2_1.SetZLength(0.1)

            # mapper
            self.Achse_2_1Mapper = vtk.vtkPolyDataMapper()
            self.Achse_2_1Mapper.SetInputConnection(self.Achse_2_1.GetOutputPort())

            # actor
            self.Achse_2_1Actor = vtk.vtkLODActor()
            self.Achse_2_1Actor.SetMapper(self.Achse_2_1Mapper)

            # make it look nice
            self.Achse_2_1Prop = self.Achse_2_1Actor.GetProperty()
            self.Achse_2_1Prop.SetColor(255 / 255, 255 / 255, 255 / 255)

            self.ren.AddActor(self.Achse_2_1Actor)

            # Teil Achse_2_2 --
            # geometry
            self.Achse_2_2 = vtk.vtkCubeSource()
            self.Achse_2_2.SetXLength(2)
            self.Achse_2_2.SetYLength(0.1)
            self.Achse_2_2.SetZLength(0.1)

            # mapper
            self.Achse_2_2Mapper = vtk.vtkPolyDataMapper()
            self.Achse_2_2Mapper.SetInputConnection(self.Achse_2_2.GetOutputPort())

            # actor
            self.Achse_2_2Actor = vtk.vtkLODActor()
            self.Achse_2_2Actor.SetMapper(self.Achse_2_2Mapper)

            # make it look nice
            self.Achse_2_2Prop = self.Achse_2_2Actor.GetProperty()
            self.Achse_2_2Prop.SetColor(255 / 255, 255 / 255, 255 / 255)

            self.ren.AddActor(self.Achse_2_2Actor)

            # Teil Auflager_1_1 --
            # geometry
            self.Auflager_1_1 = vtk.vtkCubeSource()
            self.Auflager_1_1.SetXLength(0.1)
            self.Auflager_1_1.SetYLength(4)
            self.Auflager_1_1.SetZLength(0.1)

            # mapper
            self.Auflager_1_1Mapper = vtk.vtkPolyDataMapper()
            self.Auflager_1_1Mapper.SetInputConnection(self.Auflager_1_1.GetOutputPort())

            # actor
            self.Auflager_1_1Actor = vtk.vtkLODActor()
            self.Auflager_1_1Actor.SetMapper(self.Auflager_1_1Mapper)

            # make it look nice
            self.Auflager_1_1Prop = self.Auflager_1_1Actor.GetProperty()
            self.Auflager_1_1Prop.SetColor(255 / 255, 255 / 255, 255 / 255)

            self.ren.AddActor(self.Auflager_1_1Actor)

            # Teil Auflager_1_2 --
            # geometry
            self.Auflager_1_2 = vtk.vtkCubeSource()
            self.Auflager_1_2.SetXLength(0.1)
            self.Auflager_1_2.SetYLength(0.1)
            self.Auflager_1_2.SetZLength(4)

            # mapper
            self.Auflager_1_2Mapper = vtk.vtkPolyDataMapper()
            self.Auflager_1_2Mapper.SetInputConnection(self.Auflager_1_2.GetOutputPort())

            # actor
            self.Auflager_1_2Actor = vtk.vtkLODActor()
            self.Auflager_1_2Actor.SetMapper(self.Auflager_1_2Mapper)

            # make it look nice
            self.Auflager_1_2Prop = self.Auflager_1_2Actor.GetProperty()
            self.Auflager_1_2Prop.SetColor(255 / 255, 255 / 255, 255 / 255)

            self.ren.AddActor(self.Auflager_1_2Actor)

            # Teil Auflager_2_1 --
            # geometry
            self.Auflager_2_1 = vtk.vtkCubeSource()
            self.Auflager_2_1.SetXLength(0.1)
            self.Auflager_2_1.SetYLength(4)
            self.Auflager_2_1.SetZLength(0.1)

            # mapper
            self.Auflager_2_1Mapper = vtk.vtkPolyDataMapper()
            self.Auflager_2_1Mapper.SetInputConnection(self.Auflager_2_1.GetOutputPort())

            # actor
            self.Auflager_2_1Actor = vtk.vtkLODActor()
            self.Auflager_2_1Actor.SetMapper(self.Auflager_2_1Mapper)

            # make it look nice
            self.Auflager_2_1Prop = self.Auflager_2_1Actor.GetProperty()
            self.Auflager_2_1Prop.SetColor(255 / 255, 255 / 255, 255 / 255)

            self.ren.AddActor(self.Auflager_2_1Actor)

            # Teil Auflager_2_2 --
            # geometry
            self.Auflager_2_2 = vtk.vtkCubeSource()
            self.Auflager_2_2.SetXLength(0.1)
            self.Auflager_2_2.SetYLength(0.1)
            self.Auflager_2_2.SetZLength(4)

            # mapper
            self.Auflager_2_2Mapper = vtk.vtkPolyDataMapper()
            self.Auflager_2_2Mapper.SetInputConnection(self.Auflager_2_2.GetOutputPort())

            # actor
            self.Auflager_2_2Actor = vtk.vtkLODActor()
            self.Auflager_2_2Actor.SetMapper(self.Auflager_2_2Mapper)

            # make it look nice
            self.Auflager_2_2Prop = self.Auflager_2_2Actor.GetProperty()
            self.Auflager_2_2Prop.SetColor(255 / 255, 255 / 255, 255 / 255)

            self.ren.AddActor(self.Auflager_2_2Actor)

            # Teil Abstand_1_1 --
            # geometry
            self.Abstand_1_1 = vtk.vtkCubeSource()
            self.Abstand_1_1.SetXLength(0.1)
            self.Abstand_1_1.SetYLength(st.Abstand_a)
            self.Abstand_1_1.SetZLength(0.1)

            # mapper
            self.Abstand_1_1Mapper = vtk.vtkPolyDataMapper()
            self.Abstand_1_1Mapper.SetInputConnection(self.Abstand_1_1.GetOutputPort())

            # actor
            self.Abstand_1_1Actor = vtk.vtkLODActor()
            self.Abstand_1_1Actor.SetMapper(self.Abstand_1_1Mapper)

            # make it look nice
            self.Abstand_1_1Prop = self.Abstand_1_1Actor.GetProperty()
            self.Abstand_1_1Prop.SetColor(255 / 255, 255 / 255, 255 / 255)

            self.ren.AddActor(self.Abstand_1_1Actor)

            # Teil Abstand_2_1 --
            # geometry
            self.Abstand_2_1 = vtk.vtkCubeSource()
            self.Abstand_2_1.SetXLength(0.1)
            self.Abstand_2_1.SetYLength(st.Abstand_b)
            self.Abstand_2_1.SetZLength(0.1)

            # mapper
            self.Abstand_2_1Mapper = vtk.vtkPolyDataMapper()
            self.Abstand_2_1Mapper.SetInputConnection(self.Abstand_2_1.GetOutputPort())

            # actor
            self.Abstand_2_1Actor = vtk.vtkLODActor()
            self.Abstand_2_1Actor.SetMapper(self.Abstand_2_1Mapper)

            # make it look nice
            self.Abstand_2_1Prop = self.Abstand_2_1Actor.GetProperty()
            self.Abstand_2_1Prop.SetColor(255 / 255, 255 / 255, 255 / 255)

            self.ren.AddActor(self.Abstand_2_1Actor)

            # Teil Abstand_2_2 --
            # geometry
            self.Abstand_2_2 = vtk.vtkCubeSource()
            self.Abstand_2_2.SetXLength(0.1)
            self.Abstand_2_2.SetYLength(st.Abstand_b)
            self.Abstand_2_2.SetZLength(0.1)

            # mapper
            self.Abstand_2_2Mapper = vtk.vtkPolyDataMapper()
            self.Abstand_2_2Mapper.SetInputConnection(self.Abstand_2_2.GetOutputPort())

            # actor
            self.Abstand_2_2Actor = vtk.vtkLODActor()
            self.Abstand_2_2Actor.SetMapper(self.Abstand_2_2Mapper)

            # make it look nice
            self.Abstand_2_2Prop = self.Abstand_2_2Actor.GetProperty()
            self.Abstand_2_2Prop.SetColor(255 / 255, 255 / 255, 255 / 255)

            self.ren.AddActor(self.Abstand_2_2Actor)

            # For the ball --
            # Cylinder_1
            # geometry
            self.Cylinder_1 = vtk.vtkCylinderSource()
            self.Cylinder_1.SetRadius(st.visR+0.01)
            self.Cylinder_1.SetHeight(0.01)
            self.Cylinder_1.SetResolution(20)

            # mapper
            self.Cylinder_1Mapper = vtk.vtkPolyDataMapper()
            self.Cylinder_1Mapper.SetInputConnection(self.Cylinder_1.GetOutputPort())

            # actor
            self.Cylinder_1Actor = vtk.vtkLODActor()
            self.Cylinder_1Actor.SetMapper(self.Cylinder_1Mapper)

            # make it look nice
            self.Cylinder_1Prop = self.Cylinder_1Actor.GetProperty()
            self.Cylinder_1Prop.SetColor(200 / 255, 200 / 255, 0)

            self.ren.AddActor(self.Cylinder_1Actor)

            # Cylinder_2
            # geometry
            self.Cylinder_2 = vtk.vtkCylinderSource()
            self.Cylinder_2.SetRadius(st.visR + 0.01)
            self.Cylinder_2.SetHeight(0.01)
            self.Cylinder_2.SetResolution(20)

            # mapper
            self.Cylinder_2Mapper = vtk.vtkPolyDataMapper()
            self.Cylinder_2Mapper.SetInputConnection(self.Cylinder_2.GetOutputPort())

            # actor
            self.Cylinder_2Actor = vtk.vtkLODActor()
            self.Cylinder_2Actor.SetMapper(self.Cylinder_2Mapper)

            # make it look nice
            self.Cylinder_2Prop = self.Cylinder_2Actor.GetProperty()
            self.Cylinder_2Prop.SetColor(200 / 255, 200 / 255, 0)

            self.ren.AddActor(self.Cylinder_2Actor)

            # Cylinder_3
            # geometry
            self.Cylinder_3 = vtk.vtkCylinderSource()
            self.Cylinder_3.SetRadius(st.visR + 0.01)
            self.Cylinder_3.SetHeight(0.01)
            self.Cylinder_3.SetResolution(20)

            # mapper
            self.Cylinder_3Mapper = vtk.vtkPolyDataMapper()
            self.Cylinder_3Mapper.SetInputConnection(self.Cylinder_3.GetOutputPort())

            # actor
            self.Cylinder_3Actor = vtk.vtkLODActor()
            self.Cylinder_3Actor.SetMapper(self.Cylinder_3Mapper)

            # make it look nice
            self.Cylinder_3Prop = self.Cylinder_3Actor.GetProperty()
            self.Cylinder_3Prop.SetColor(200 / 255, 200 / 255, 0)

            self.ren.AddActor(self.Cylinder_3Actor)

            # -------- add the ball ----
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
            self.ballProp.SetColor(255 / 255, 255 / 255, 0)
            self.ballProp.SetAmbient(0.2)
            self.ballProp.SetDiffuse(0.8)
            self.ballProp.SetSpecular(0.5)
            self.ballProp.SetSpecularPower(0.5)

            self.ren.AddActor(self.ballActor)

            # add background
            self.ren.GradientBackgroundOn()
            self.ren.SetBackground(228 / 255, 232 / 255, 213 / 255)
            self.ren.SetBackground2(38 / 255, 139 / 255, 210 / 255)

            # apply some sane initial state
            self.update_scene(np.array([0, 0, 0, 0]), np.array([0, 0]))

            # get everybody into the frame
            self.ren.ResetCamera()
            self.ren.GetActiveCamera().Zoom(1.7)

            # save this view
            self.save_camera_pose()

        @staticmethod
        def calc_positions(x, u):
            """
            Calculate stationary vectors and rot. matrices for bodies
            """
            Winkel_1, Winkel_2 = u
            # Effe_Winkel_1 = np.arcsin(np.sin(x[2])*np.cos(Winkel_1)+np.sin(x[2])*np.sin(Winkel_1)*np.tan(Winkel_1));
            # beam
            D_1 = np.array([[np.cos(Winkel_1), -np.sin(Winkel_1), 0],
                            [np.sin(Winkel_1), np.cos(Winkel_1), 0],
                            [0, 0, 1]])
            D_2 = np.array([[np.cos(Winkel_2), -np.sin(Winkel_2), 0],
                            [np.sin(Winkel_2), np.cos(Winkel_2), 0],
                            [0, 0, 1]])
            T_1 = np.array([[0, 0, 1],
                            [1, 0, 0],
                            [0, 1, 0]])
            T_21 = np.array([[np.cos(Winkel_1), 0, np.sin(Winkel_1)],
                             [np.sin(Winkel_1), 0, -np.cos(Winkel_1)],
                             [0, 1, 0]])
            T_2 = np.array([[1, 0, 0],
                            [0, 0, -1],
                            [0, 1, 0]])

            D_20 = np.dot(np.dot(np.dot(T_1, np.dot(D_1, T_2)), D_2), np.dot(np.linalg.inv(T_2), np.linalg.inv(T_1)))
            D_10 = np.dot(np.dot(T_1, D_1), np.linalg.inv(T_1))
            # D_20 = np.dot(np.dot(np.dot(D_1, T_1), D_2), T_2)
            # D_10 = np.dot(T_1, D_1)
            t_beam = D_20

            r_beam0 = np.array([0, 4+st.Abstand_a+st.Abstand_b+st.visBeamWidth / 2, 0])
            r_beam = np.dot(t_beam, np.array([0, st.Abstand_a+st.visBeamWidth/2, 0]))+np.dot(D_10, np.array([0, st.Abstand_b, 0]))+np.array([0, 4, 0])

            # ball
            r_ball0 = np.array([x[0], 4+st.Abstand_a+st.Abstand_b+st.visBeamWidth+st.visR, x[2]])
            r_ball = np.dot(t_beam, np.array([x[0], st.Abstand_a+st.visBeamWidth+st.visR, -x[2]]))+np.dot(D_10, np.array([0, st.Abstand_b, 0]))+np.array([0, 4, 0])
            phi_1 = x[0] / st.visR
            phi_2 = x[2] / st.visR
            t_ball_1 = np.array([[np.cos(-phi_1), -np.sin(-phi_1), 0],
                                 [np.sin(-phi_1), np.cos(-phi_1), 0],
                                 [0, 0, 1]])
            t_ball_2 = np.array([[1, 0, 0],
                                 [0, np.cos(-phi_2), -np.sin(-phi_2)],
                                 [0, np.sin(-phi_2), np.cos(-phi_2)]])
            t_ball = np.dot(t_ball_1, t_ball_2)

            return [r_beam, t_beam, r_ball, t_ball]

        @staticmethod
        def set_body_state(actor, r, t):
            poke = vtk.vtkMatrix4x4()

            for i in range(3):
                for n in range(3):
                    poke.SetElement(i, n, t[i, n])
                poke.SetElement(i, 3, r[i])

            actor.PokeMatrix(poke)

        def update_scene(self, x, u):
            """
            update the body states
            """

            Winkel_1, Winkel_2 = u
            # Effe_Winkel_1 = np.arcsin(np.sin(x[2])*np.cos(Winkel_1)+np.sin(x[2])*np.sin(Winkel_1)*np.tan(Winkel_1));
            # beam
            D_1 = np.array([[np.cos(Winkel_1), -np.sin(Winkel_1), 0],
                            [np.sin(Winkel_1), np.cos(Winkel_1), 0],
                            [0, 0, 1]])
            D_2 = np.array([[np.cos(Winkel_2), -np.sin(Winkel_2), 0],
                            [np.sin(Winkel_2), np.cos(Winkel_2), 0],
                            [0, 0, 1]])
            T_1 = np.array([[0, 0, 1],
                            [1, 0, 0],
                            [0, 1, 0]])
            T_21 = np.array([[np.cos(Winkel_1), 0, np.sin(Winkel_1)],
                             [np.sin(Winkel_1), 0, -np.cos(Winkel_1)],
                             [0, 1, 0]])
            T_2 = np.array([[1, 0, 0],
                            [0, 0, -1],
                            [0, 1, 0]])

            D_20 = np.dot(np.dot(np.dot(T_1, np.dot(D_1, T_2)), D_2), np.dot(np.linalg.inv(T_2), np.linalg.inv(T_1)))
            D_10 = np.dot(np.dot(T_1, D_1), np.linalg.inv(T_1))
            # D_20 = np.dot(np.dot(np.dot(T_1, D_1), D_2), T_2)
            # D_10 = np.dot(T_1, D_1)

            r_beam, t_beam, r_ball, t_ball = self.calc_positions(x, u)
            self.set_body_state(self.beamActor, r_beam, t_beam)
            self.set_body_state(self.ballActor, r_ball, t_ball)

            # Fachwerk
            t_Fachwerk_1 = D_10
            r_Fachwerk_1 = np.dot(t_Fachwerk_1, np.array([0, st.Abstand_b, 0]))+np.array([5, 4, 0])
            self.set_body_state(self.Fachwerk_1Actor, r_Fachwerk_1, t_Fachwerk_1)
            t_Fachwerk_2 = D_10
            r_Fachwerk_2 = np.dot(t_Fachwerk_2, np.array([0, st.Abstand_b, 0]))+np.array([-5, 4, 0])
            self.set_body_state(self.Fachwerk_2Actor, r_Fachwerk_2, t_Fachwerk_2)
            t_Fachwerk_3 = D_10
            r_Fachwerk_3 = np.dot(t_Fachwerk_3, np.array([0, st.Abstand_b, -5]))+np.array([0, 4, 0])
            self.set_body_state(self.Fachwerk_3Actor, r_Fachwerk_3, t_Fachwerk_3)
            t_Fachwerk_4 = D_10
            r_Fachwerk_4 = np.dot(t_Fachwerk_4, np.array([0, st.Abstand_b, 5]))+np.array([0, 4, 0])
            self.set_body_state(self.Fachwerk_4Actor, r_Fachwerk_4, t_Fachwerk_4)
            # Achse_1
            t_Achse_1 = D_20
            r_Achse_1 = np.dot(t_Achse_1, np.array([0, 0, 0]))+np.dot(D_10, np.array([0, st.Abstand_b, 0]))+np.array([0, 4, 0])
            self.set_body_state(self.Achse_1Actor, r_Achse_1, t_Achse_1)
            # Achse_2_1
            t_Achse_2_1 = D_10
            r_Achse_2_1 = np.dot(t_Achse_2_1, np.array([0, 0, 0]))+np.array([6, 4, 0])
            self.set_body_state(self.Achse_2_1Actor, r_Achse_2_1, t_Achse_2_1)
            # Achse_2_2
            t_Achse_2_2 = D_10
            r_Achse_2_2 = np.dot(t_Achse_2_1, np.array([0, 0, 0]))+np.array([-6, 4, 0])
            self.set_body_state(self.Achse_2_2Actor, r_Achse_2_2, t_Achse_2_2)
            # Auflager_1_1
            t_Auflager_1_1 = np.array([[np.cos(0), -np.sin(0), 0],
                                       [np.sin(0), np.cos(0), 0],
                                       [0, 0, 1]])
            r_Auflager_1_1 = np.dot(t_Auflager_1_1, np.array([-7, 2, 0]))
            self.set_body_state(self.Auflager_1_1Actor, r_Auflager_1_1, t_Auflager_1_1)
            # Auflager_1_2
            t_Auflager_1_2 = np.array([[np.cos(0), -np.sin(0), 0],
                                       [np.sin(0), np.cos(0), 0],
                                       [0, 0, 1]])
            r_Auflager_1_2 = np.dot(t_Auflager_1_2, np.array([-7, 0, 0]))
            self.set_body_state(self.Auflager_1_2Actor, r_Auflager_1_2, t_Auflager_1_2)
            # Auflager_2_1
            t_Auflager_2_1 = np.array([[np.cos(0), -np.sin(0), 0],
                                       [np.sin(0), np.cos(0), 0],
                                       [0, 0, 1]])
            r_Auflager_2_1 = np.dot(t_Auflager_2_1, np.array([7, 2, 0]))
            self.set_body_state(self.Auflager_2_1Actor, r_Auflager_2_1, t_Auflager_2_1)
            # Auflager_2_2
            t_Auflager_2_2 = np.array([[np.cos(0), -np.sin(0), 0],
                                       [np.sin(0), np.cos(0), 0],
                                       [0, 0, 1]])
            r_Auflager_2_2 = np.dot(t_Auflager_2_2, np.array([7, 0, 0]))
            self.set_body_state(self.Auflager_2_2Actor, r_Auflager_2_2, t_Auflager_2_2)
            # Abstand_1_1
            t_Abstand_1_1 = D_20
            r_Abstand_1_1 = np.dot(t_Abstand_1_1, np.array([0, st.Abstand_a/2, 0]))+np.dot(D_10, np.array([0, st.Abstand_b, 0]))+np.array([0, 4, 0])
            self.set_body_state(self.Abstand_1_1Actor, r_Abstand_1_1, t_Abstand_1_1)
            # Abstand_2_1
            t_Abstand_2_1 = D_10
            r_Abstand_2_1 = np.dot(t_Abstand_2_1, np.array([0, st.Abstand_b / 2, 0]))+np.array([5, 4, 0])
            self.set_body_state(self.Abstand_2_1Actor, r_Abstand_2_1, t_Abstand_2_1)
            # Abstand_2_2
            t_Abstand_2_2 = D_10
            r_Abstand_2_2 = np.dot(t_Abstand_2_2, np.array([0, st.Abstand_b / 2, 0]))+np.array([-5, 4, 0])
            self.set_body_state(self.Abstand_2_2Actor, r_Abstand_2_2, t_Abstand_2_2)
            # Cylinder_1
            t_Cylinder_1 = t_ball
            r_Cylinder_1 = r_ball
            self.set_body_state(self.Cylinder_1Actor, r_Cylinder_1, t_Cylinder_1)
            # Cylinder_2
            t_Cylinder_2 = np.dot(t_ball, np.array([[0, -1, 0],[1, 0, 0],[0, 0, 1]]))
            r_Cylinder_2 = r_ball
            self.set_body_state(self.Cylinder_2Actor, r_Cylinder_2, t_Cylinder_2)
            # Cylinder_3
            t_Cylinder_3 = np.dot(t_ball, np.array([[1, 0, 0],[0, 0, -1],[0, 1, 0]]))
            r_Cylinder_3 = r_ball
            self.set_body_state(self.Cylinder_3Actor, r_Cylinder_3, t_Cylinder_3)
    pm.register_visualizer(BallPlateVisualizer)

except ImportError as e:
    vtk = None
    print("BallBeam Visualizer:")
    print(e)
    print("VTK Visualization not available.")


