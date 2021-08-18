# -*- coding: utf-8 -*-
import numpy as np

import pymoskito as pm

import matplotlib as mpl
import matplotlib.patches
import matplotlib.transforms

import settings as st

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
    
    class BalanceBoard3DVisualizer(pm.VtkVisualizer):

        def __init__(self, renderer):
            pm.VtkVisualizer.__init__(self, renderer)

            # -------- add the board ----
            # geometry
            self.board = vtk.vtkCubeSource()
            self.board.SetXLength(st.visBoardLength)
            self.board.SetYLength(st.visBoardWidth)
            self.board.SetZLength(st.visBoardDepth)

            # mapper
            self.boardMapper = vtk.vtkPolyDataMapper()
            self.boardMapper.SetInputConnection(self.board.GetOutputPort())

            # actor
            self.boardActor = vtk.vtkLODActor()
            self.boardActor.SetMapper(self.boardMapper)

            # make it look nice
            self.boardProp = self.boardActor.GetProperty()
            self.boardProp.SetColor(25 / 255, 45 / 255, 100 / 255)

            self.ren.AddActor(self.boardActor)

            
            # -------- add the mass ----
            # geometry
            self.mass = vtk.vtkCubeSource()
            self.mass.SetXLength(st.visMassLength)
            self.mass.SetYLength(st.visMassWidth)
            self.mass.SetZLength(st.visMassDepth)

            # mapper
            self.massMapper = vtk.vtkPolyDataMapper()
            self.massMapper.SetInputConnection(self.mass.GetOutputPort())

            # actor
            self.massActor = vtk.vtkLODActor()
            self.massActor.SetMapper(self.massMapper)
            # make it look nice
            self.massProp = self.massActor.GetProperty()
            self.massProp.SetColor(205 / 255, 220 / 255, 40 / 255)

            self.ren.AddActor(self.massActor)


            # -------- add the cylinder ----
            # geometry
            self.cylinder = vtk.vtkCylinderSource()
            self.cylinder.SetCenter(0,0,0)
            self.cylinder.SetRadius(st.r)
            self.cylinder.SetHeight(st.visBoardDepth)
            self.cylinder.SetResolution(100);
            #drehen?
            
            # mapper
            self.cylinderMapper = vtk.vtkPolyDataMapper()
            self.cylinderMapper.SetInputConnection(self.cylinder.GetOutputPort())
            
            # actor
            self.cylinderActor = vtk.vtkLODActor()
            self.cylinderActor.SetMapper(self.cylinderMapper)
            
            # make it look nice
            self.cylinderProp = self.cylinderActor.GetProperty()
            self.cylinderProp.SetColor(25 / 255, 45 / 255, 100 / 255)
            self.ren.AddActor(self.cylinderActor)

            # -------- add the cylinder_marker ----
            # geometry
            self.cylinder_marker = vtk.vtkLineSource()
            self.cylinder_marker.SetPoint1(0, -st.visBoardDepth/2, 0)
            self.cylinder_marker.SetPoint2(0, -st.visBoardDepth/2, st.r)

            # mapper
            self.cylinder_markerMapper = vtk.vtkPolyDataMapper()
            self.cylinder_markerMapper.SetInputConnection(self.cylinder_marker.GetOutputPort())

            # actor
            self.cylinder_markerActor = vtk.vtkLODActor()
            self.cylinder_markerActor.SetMapper(self.cylinder_markerMapper)

            # make it look nice
            self.cylinder_markerProp = self.cylinder_markerActor.GetProperty()
            self.cylinder_markerProp.SetColor(205 / 255, 220 / 255, 40 / 255)

            self.ren.AddActor(self.cylinder_markerActor)

            # -------- add the ground ----
            # geometry
            self.ground = vtk.vtkPlaneSource()
            self.ground.SetCenter(0,-st.r,0)
            self.ground.SetNormal(0, 1, 0)

            # mapper
            self.groundMapper = vtk.vtkPolyDataMapper()
            self.groundMapper.SetInputConnection(self.ground.GetOutputPort())

            # actor
            self.groundActor = vtk.vtkLODActor()
            self.groundActor.SetMapper(self.groundMapper)

            # make it look nice
            self.groundProp = self.groundActor.GetProperty()
            self.groundProp.SetColor(160 / 255, 220 / 255, 240 / 255)

            self.ren.AddActor(self.groundActor)

            # -------- add marking line ----
            # geometry
            self.line = vtk.vtkLineSource()
            self.line.SetPoint1(0,-st.r,0.5)
            self.line.SetPoint2(0,-st.r,-0.5)

            # mapper
            self.lineMapper = vtk.vtkPolyDataMapper()
            self.lineMapper.SetInputConnection(self.line.GetOutputPort())

            # actor
            self.lineActor = vtk.vtkLODActor()
            self.lineActor.SetMapper(self.lineMapper)

            # make it look nice
            self.lineProp = self.lineActor.GetProperty()
            self.lineProp.SetColor(0 / 255, 0 / 255, 0 / 255)

            self.ren.AddActor(self.lineActor)


            # -------- misc ----
            # add background
            self.ren.GradientBackgroundOn()
            self.ren.SetBackground(228 / 255, 232 / 255, 213 / 255)
            self.ren.SetBackground2(38 / 255, 139 / 255, 210 / 255)

            # apply some sane initial state
            self.update_scene(np.array([0, 0, 0, 0, 0, 0]))

            # get everybody into the frame
            self.ren.ResetCamera()
            self.ren.GetActiveCamera().Zoom(1.8)

            # save this view
            self.save_camera_pose()

        @staticmethod
        def calc_positions(x):
            x1 = x[0]   # psi, board deflection
            x2 = x[1]   # gamma, carriage position
            x3 = x[2]   # theta, cylinder angle

            # matrices of rotation
            R_Theta = np.array([[np.cos(x3), -np.sin(x3), 0],
                                [np.sin(x3),  np.cos(x3), 0],
                                [        0 ,          0 , 1]])
            R_Psi   = np.array([[np.cos(x1), -np.sin(x1), 0],
                                [np.sin(x1),  np.cos(x1), 0],
                                [        0 ,          0 , 1]])
            
            # cylinder
            # needs to turn by 90°, since its initial position is not laying but standing
            phi = np.pi/2
            init_cylinder = np.array([[1,            0,           0],
                                      [0,  np.cos(phi), np.sin(phi)],
                                      [0, -np.sin(phi), np.cos(phi)]])
            t_cylinder = np.dot(R_Theta, init_cylinder)
            r_cylinder = np.array([-st.r*x3, 0, 0])
            
            # board
            t_board  = R_Psi
            r_board0 = np.array([st.r*(x1-x3), st.visBoardWidth/2 + st.r,0])
            r_board  = r_cylinder + np.dot(R_Psi, r_board0)
            
            # mass
            t_mass  = R_Psi
            r_mass0 = r_board0 + np.array([x2, st.visBoardWidth/2 + st.visMassWidth/2, 0])
            r_mass  = r_cylinder + np.dot(R_Psi, r_mass0)
            
            return[r_board, t_board, r_mass, t_mass, r_cylinder, t_cylinder]

        @staticmethod
        def set_body_state(actor, r, t):
            poke = vtk.vtkMatrix4x4()

            for i in range(3):
                for n in range(3):
                    poke.SetElement(i, n, t[i, n])
                poke.SetElement(i, 3, r[i])

            actor.PokeMatrix(poke)
        
        def update_scene(self, x):
            
            r_board, t_board, r_mass, t_mass, r_cylinder, t_cylinder = self.calc_positions(x)
            self.set_body_state(self.boardActor, r_board, t_board)
            self.set_body_state(self.massActor, r_mass, t_mass)
            self.set_body_state(self.cylinderActor, r_cylinder, t_cylinder)
            self.set_body_state(self.cylinder_markerActor, r_cylinder, t_cylinder)
            
except ImportError as e:
    vtk = None
    print("BallBeam Visualizer:")
    print(e)
    print("VTK Visualization not available.")


class BalanceBoard2DVisualizer(pm.MplVisualizer):

    def __init__(self, q_widget, q_layout):
        pm.MplVisualizer.__init__(self, q_widget, q_layout)
        self.axes.set_xlim(st.x_min_plot, st.x_max_plot)
        self.axes.set_ylim(st.y_min_plot, st.y_max_plot)
        self.axes.set_aspect("equal")
        
        self.cylinder_base = mpl.patches.Circle(
            xy=[0, 0],
            radius=st.r,
            color=HKS44K100,
            zorder=1)
        self.cylinder_highlight = mpl.patches.Wedge(
            center=[0, 0],
            r=st.r,
            theta1=0,
            theta2=90,
            color=HKS07K100,
            zorder=2)
        self.board = mpl.patches.Rectangle(
            xy=[-st.visBoardLength/2, st.r],
            width=st.visBoardLength,
            height=st.visBoardWidth,
            color=HKS41K100,
            zorder=0)
        self.mass = mpl.patches.Rectangle(
            xy=[-st.visMassLength/2, st.r + st.visBoardWidth],
            width=st.visMassLength,
            height=st.visMassWidth,
            color=HKS41K100,
            zorder=0)

        ground_height = 0.01
        ground = mpl.patches.Rectangle(
            xy=[st.x_min_plot, -st.r - ground_height],
            width=st.x_max_plot-st.x_min_plot,
            height=ground_height,
            color=HKS41K100,
            zorder=0)
        marker_width = ground_height
        marker_length = 0.03
        middle_marker = mpl.patches.Rectangle(
            xy=[-marker_width/2, -st.r - ground_height - marker_length],
            width=marker_width,
            height=marker_length,
            color=HKS41K100,
            zorder=0)

        self.axes.add_patch(self.cylinder_base)
        self.axes.add_patch(self.cylinder_highlight)
        self.axes.add_patch(self.board)
        self.axes.add_patch(self.mass)
        self.axes.add_patch(ground)
        self.axes.add_patch(middle_marker)


    def update_scene(self, x):
        psi_board, gamma_mass, theta_cylinder, dpsi_board, dgamma_mass, dtheta_cylinder = x

        t_cylinder = (mpl.transforms.Affine2D().rotate_around(0, 0, theta_cylinder)
                        + mpl.transforms.Affine2D().translate(-st.r*theta_cylinder, 0)
                      + self.axes.transData)
        t_board    = (mpl.transforms.Affine2D().translate(st.r*(psi_board - theta_cylinder), 0)
                        + mpl.transforms.Affine2D().rotate_around(0, 0, psi_board-theta_cylinder)
                        + t_cylinder)
        t_mass     = (mpl.transforms.Affine2D().translate(gamma_mass, 0)
                        + t_board)

        self.cylinder_base.set_transform(t_cylinder)
        self.cylinder_highlight.set_transform(t_cylinder)
        self.board.set_transform(t_board)
        self.mass.set_transform(t_mass)
        
        self.canvas.draw()
