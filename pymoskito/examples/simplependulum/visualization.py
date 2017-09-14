# -*- coding: utf-8 -*-
import numpy as np
import pymoskito as pm

import matplotlib as mpl
import matplotlib.patches
import matplotlib.transforms

#from python.rod_pendulum import model_parameter as mp
from . import settings as mp

# try:
#     import vtk
#
#     class TwoPendulumVisualizer(pm.VtkVisualizer):
#
#         def __init__(self, renderer):
#             pm.VtkVisualizer.__init__(self)
#             assert isinstance(renderer, vtk.vtkRenderer)
#             self.ren = renderer
#
#             # -------- add the beam ----
#             # geometry
#             self.beam = vtk.vtkCubeSource()
#             self.beam.SetXLength(st.beam_length)
#             self.beam.SetYLength(st.beam_height)
#             self.beam.SetZLength(st.beam_depth)
#
#             # mapper
#             self.beam_Mapper = vtk.vtkPolyDataMapper()
#             self.beam_Mapper.SetInputConnection(self.beam.GetOutputPort())
#
#             # actor
#             self.beam_Actor = vtk.vtkLODActor()
#             self.beam_Actor.SetMapper(self.beam_Mapper)
#             self.beam_Actor.SetPosition(0, -(st.cart_height / 2 + st.beam_height / 2), 0)
#
#             # make it look nice
#             self.beam_Prop = self.beam_Actor.GetProperty()
#             # RAL 9007, grey-aluminium
#             self.beam_Prop.SetColor(142 / 255, 142 / 255, 139 / 255)
#
#             self.ren.AddActor(self.beam_Actor)
#
#             # -------- add cart ----
#             # geometry
#             self.cart = vtk.vtkCubeSource()
#             self.cart.SetXLength(st.cart_length)
#             self.cart.SetYLength(st.cart_height)
#             self.cart.SetZLength(st.cart_depth)
#
#             # mapper
#             self.cart_Mapper = vtk.vtkPolyDataMapper()
#             self.cart_Mapper.SetInputConnection(self.cart.GetOutputPort())
#
#             # actor
#             self.cart_Actor = vtk.vtkLODActor()
#             self.cart_Actor.SetPosition(0, 0, 0)
#             self.cart_Actor.RotateWXYZ(0, 1, 0, 0)
#             self.cart_Actor.SetMapper(self.cart_Mapper)
#
#             # make it look nice
#             self.cart_Prop = self.cart_Actor.GetProperty()
#             # RAL 7011, iron-grey
#             self.cart_Prop.SetColor(64 / 255, 74 / 255, 84 / 255)
#
#             self.ren.AddActor(self.cart_Actor)
#             # save pose
#             self.cart_pose = [np.array([0, 0, 0]), np.eye(3)]
#
#             # -------- add axis ----
#             # geometry
#             self.axis = vtk.vtkCylinderSource()
#             self.axis.SetHeight(st.axis_height)
#             self.axis.SetRadius(st.axis_radius)
#             self.axis.SetResolution(100)
#
#             # mapper
#             self.axis_Mapper = vtk.vtkPolyDataMapper()
#             self.axis_Mapper.SetInputConnection(self.axis.GetOutputPort())
#
#             # actor
#             self.axis_Actor = vtk.vtkLODActor()
#             self.axis_Actor.SetPosition(0, 0, st.cart_depth/2 + st.axis_height/2)
#             self.axis_Actor.RotateWXYZ(90, 1, 0, 0)
#             self.axis_Actor.SetMapper(self.axis_Mapper)
#
#             # make it look nice
#             self.axis_Prop = self.axis_Actor.GetProperty()
#             # RAL 7011, iron-grey
#             self.axis_Prop.SetColor(64 / 255, 74 / 255, 84 / 255)
#
#             self.ren.AddActor(self.axis_Actor)
#             # save pose
#             self.axis_pose = [np.array([0, 0, st.cart_depth/2 + st.axis_height/2]),
#                               pm.rotation_matrix_xyz("x", 90, "deg")]
#
#             # -------- add short pendulum ----
#             # add short pendulum shaft
#             # geometry
#             self.short_pendulum_shaft = vtk.vtkCylinderSource()
#             self.short_pendulum_shaft.SetHeight(st.pendulum_shaft_height)
#             self.short_pendulum_shaft.SetRadius(st.pendulum_shaft_radius)
#             self.short_pendulum_shaft.SetResolution(100)
#
#             # mapper
#             self.short_pendulum_shaft_Mapper = vtk.vtkPolyDataMapper()
#             self.short_pendulum_shaft_Mapper.SetInputConnection(self.short_pendulum_shaft.GetOutputPort())
#
#             # actor
#             self.short_pendulum_shaft_Actor = vtk.vtkLODActor()
#             self.short_pendulum_shaft_Actor.SetPosition(0,
#                                                         0,
#                                                         st.cart_depth/2 + st.axis_height + st.pendulum_shaft_height/2)
#             self.short_pendulum_shaft_Actor.RotateWXYZ(90, 1, 0, 0)
#             self.short_pendulum_shaft_Actor.SetMapper(self.short_pendulum_shaft_Mapper)
#
#             # make it look nice
#             self.short_pendulum_shaft_Prop = self.short_pendulum_shaft_Actor.GetProperty()
#             # RAL 9007, grey-aluminium, a little bit darker
#             self.short_pendulum_shaft_Prop.SetColor(122 / 255, 122 / 255, 119 / 255)
#
#             self.ren.AddActor(self.short_pendulum_shaft_Actor)
#             # save pose
#             self.short_pendulum_shaft_pose = [np.array([0,
#                                                         0,
#                                                         st.cart_depth/2 + st.axis_height + st.pendulum_shaft_height/2]),
#                                               pm.rotation_matrix_xyz("x", 90, "deg")]
#
#             # add short pendulum
#             # geometry
#             self.short_pendulum = vtk.vtkCylinderSource()
#             self.short_pendulum.SetHeight(st.short_pendulum_height)
#             self.short_pendulum.SetRadius(st.short_pendulum_radius)
#             self.short_pendulum.SetResolution(100)
#
#             # mapper
#             self.short_pendulum_Mapper = vtk.vtkPolyDataMapper()
#             self.short_pendulum_Mapper.SetInputConnection(self.short_pendulum.GetOutputPort())
#
#             # actor
#             self.short_pendulum_Actor = vtk.vtkLODActor()
#             self.short_pendulum_Actor.SetPosition(0,
#                                                   st.short_pendulum_height/2,
#                                                   st.cart_depth/2 + st.axis_height + st.pendulum_shaft_height/2)
#             self.short_pendulum_Actor.RotateWXYZ(0, 1, 0, 0)
#             self.short_pendulum_Actor.SetMapper(self.short_pendulum_Mapper)
#
#             # make it look nice
#             self.short_pendulum_Prop = self.short_pendulum_Actor.GetProperty()
#             # RAL 9007, grey-aluminium, a little bit darker
#             self.short_pendulum_Prop.SetColor(122 / 255, 122 / 255, 119 / 255)
#
#             self.ren.AddActor(self.short_pendulum_Actor)
#             self.short_pendulum_pose = [np.array([0,
#                                                   st.short_pendulum_height/2,
#                                                   st.cart_depth/2 + st.axis_height + st.pendulum_shaft_height/2]),
#                                         np.eye(3)]
#
#             # add short pendulum weight
#             # geometry
#             self.short_pendulum_weight = vtk.vtkCylinderSource()
#             self.short_pendulum_weight.SetHeight(st.pendulum_weight_height)
#             self.short_pendulum_weight.SetRadius(st.pendulum_weight_radius)
#             self.short_pendulum_weight.SetResolution(100)
#
#             # mapper
#             self.short_pendulum_weight_Mapper = vtk.vtkPolyDataMapper()
#             self.short_pendulum_weight_Mapper.SetInputConnection(self.short_pendulum_weight.GetOutputPort())
#
#             # actor
#             self.short_pendulum_weight_Actor = vtk.vtkLODActor()
#             self.short_pendulum_weight_Actor.SetPosition(0,
#                                                          (st.short_pendulum_height + st.pendulum_weight_height/2),
#                                                          st.cart_depth/2 + st.axis_height + st.pendulum_shaft_height/2)
#             self.short_pendulum_weight_Actor.RotateWXYZ(0, 1, 0, 0)
#             self.short_pendulum_weight_Actor.SetMapper(self.short_pendulum_weight_Mapper)
#
#             # make it look nice
#             self.short_pendulum_weight_Prop = self.short_pendulum_weight_Actor.GetProperty()
#             # RAL 9006, white-aluminium
#             self.short_pendulum_weight_Prop.SetColor(162 / 255, 166 / 255, 164 / 255)
#
#             self.ren.AddActor(self.short_pendulum_weight_Actor)
#             self.short_pendulum_weight_pose = [
#                 np.array([0,
#                           (st.short_pendulum_height + st.pendulum_weight_height/2),
#                           st.cart_depth/2 + st.axis_height + st.pendulum_shaft_height/2]),
#                 np.eye(3)
#             ]
#
#             # -------- add long pendulum ----
#             # add long pendulum shaft
#             # geometry
#             self.long_pendulum_shaft = vtk.vtkCylinderSource()
#             self.long_pendulum_shaft.SetHeight(st.pendulum_shaft_height)
#             self.long_pendulum_shaft.SetRadius(st.pendulum_shaft_radius)
#             self.long_pendulum_shaft.SetResolution(100)
#
#             # mapper
#             self.long_pendulum_shaft_Mapper = vtk.vtkPolyDataMapper()
#             self.long_pendulum_shaft_Mapper.SetInputConnection(self.long_pendulum_shaft.GetOutputPort())
#
#             # actor
#             self.long_pendulum_shaft_Actor = vtk.vtkLODActor()
#             self.long_pendulum_shaft_Actor.SetPosition(0,
#                                                        0,
#                                                        st.cart_depth/2
#                                                        + st.axis_height
#                                                        + st.pendulum_shaft_height
#                                                        + st.pendulum_shaft_height/2)
#             self.long_pendulum_shaft_Actor.RotateWXYZ(90, 1, 0, 0)
#             self.long_pendulum_shaft_Actor.SetMapper(self.long_pendulum_shaft_Mapper)
#
#             # make it look nice
#             self.long_pendulum_shaft_Prop = self.long_pendulum_shaft_Actor.GetProperty()
#             # RAL 9007, grey-aluminium
#             self.long_pendulum_shaft_Prop.SetColor(142 / 255, 142 / 255, 139 / 255)
#
#             self.ren.AddActor(self.long_pendulum_shaft_Actor)
#             # save pose
#             self.long_pendulum_shaft_pose = [np.array([0,
#                                                        0,
#                                                        st.cart_depth/2
#                                                        + st.axis_height
#                                                        + st.pendulum_shaft_height
#                                                        + st.pendulum_shaft_height/2]),
#                                              pm.rotation_matrix_xyz("x", 90, "deg")]
#
#             # add long pendulum
#             # geometry
#             self.long_pendulum = vtk.vtkCylinderSource()
#             self.long_pendulum.SetHeight(st.long_pendulum_height)
#             self.long_pendulum.SetRadius(st.long_pendulum_radius)
#             self.long_pendulum.SetResolution(100)
#
#             # mapper
#             self.long_pendulum_Mapper = vtk.vtkPolyDataMapper()
#             self.long_pendulum_Mapper.SetInputConnection(self.long_pendulum.GetOutputPort())
#
#             # actor
#             self.long_pendulum_Actor = vtk.vtkLODActor()
#             self.long_pendulum_Actor.SetPosition(0,
#                                                  st.long_pendulum_height/2,
#                                                  st.cart_depth/2
#                                                  + st.axis_height
#                                                  + st.pendulum_shaft_height
#                                                  + st.pendulum_shaft_height/2)
#             self.long_pendulum_Actor.RotateWXYZ(0, 1, 0, 0)
#             self.long_pendulum_Actor.SetMapper(self.long_pendulum_Mapper)
#
#             # make it look nice
#             self.long_pendulum_Prop = self.long_pendulum_Actor.GetProperty()
#             # RAL 9007, grey-aluminium
#             self.long_pendulum_Prop.SetColor(142 / 255, 142 / 255, 139 / 255)
#
#             self.ren.AddActor(self.long_pendulum_Actor)
#             self.long_pendulum_pose = [np.array([0,
#                                                  st.long_pendulum_height/2,
#                                                  st.cart_depth/2
#                                                  + st.axis_height
#                                                  + st.pendulum_shaft_height
#                                                  + st.pendulum_shaft_height/2]),
#                                        np.eye(3)]
#
#             # add long pendulum weight
#             # geometry
#             self.long_pendulum_weight = vtk.vtkCylinderSource()
#             self.long_pendulum_weight.SetHeight(st.pendulum_weight_height)
#             self.long_pendulum_weight.SetRadius(st.pendulum_weight_radius)
#             self.long_pendulum_weight.SetResolution(100)
#
#             # mapper
#             self.long_pendulum_weight_Mapper = vtk.vtkPolyDataMapper()
#             self.long_pendulum_weight_Mapper.SetInputConnection(self.long_pendulum_weight.GetOutputPort())
#
#             # actor
#             self.long_pendulum_weight_Actor = vtk.vtkLODActor()
#             self.long_pendulum_weight_Actor.SetPosition(0,
#                                                         (st.long_pendulum_height + st.pendulum_weight_height/2),
#                                                         st.cart_depth/2
#                                                         + st.axis_height
#                                                         + st.pendulum_shaft_height
#                                                         + st.pendulum_shaft_height/2)
#             self.long_pendulum_weight_Actor.RotateWXYZ(0, 1, 0, 0)
#             self.long_pendulum_weight_Actor.SetMapper(self.long_pendulum_weight_Mapper)
#
#             # make it look nice
#             self.long_pendulum_weight_Prop = self.long_pendulum_weight_Actor.GetProperty()
#             # RAL 9006, white-aluminium
#             self.long_pendulum_weight_Prop.SetColor(162 / 255, 166 / 255, 164 / 255)
#
#             self.ren.AddActor(self.long_pendulum_weight_Actor)
#             self.long_pendulum_weight_pose = [np.array([0,
#                                                         (st.long_pendulum_height + st.pendulum_weight_height/2),
#                                                         st.cart_depth/2
#                                                         + st.axis_height
#                                                         + st.pendulum_shaft_height
#                                                         + st.pendulum_shaft_height/2]),
#                                               np.eye(3)]
#
#             # add background
#             self.ren.GradientBackgroundOn()
#             self.ren.SetBackground(228 / 255, 232 / 255, 213 / 255)
#             self.ren.SetBackground2(38 / 255, 139 / 255, 210 / 255)
#
#             # get everybody into the frame
#             self.ren.ResetCamera()
#             self.ren.GetActiveCamera().Zoom(1.45)
#             self.ren.GetActiveCamera().SetFocalPoint(0, 0, 0)
#
#             # add camera reset functionality
#             self.can_reset_view = True
#             self.position = self.ren.GetActiveCamera().GetPosition()
#             self.focal_point = self.ren.GetActiveCamera().GetFocalPoint()
#             self.view_up = self.ren.GetActiveCamera().GetViewUp()
#             self.view_angle = self.ren.GetActiveCamera().GetViewAngle()
#             self.parallel_projection = self.ren.GetActiveCamera().GetParallelProjection()
#             self.parallel_scale = self.ren.GetActiveCamera().GetParallelScale()
#             self.clipping_range = self.ren.GetActiveCamera().GetClippingRange()
#
#         def calc_positions(self, x):
#             """
#             Calculate stationary vectors and rot. matrices for bodies
#             """
#             positions_dict = {}
#
#             # cart
#             t_cart = np.array([x[0], 0, 0]) + self.cart_pose[0]
#             r_cart = np.eye(3) @ self.cart_pose[1]
#             positions_dict.update({"cart": [self.cart_Actor, t_cart, r_cart]})
#
#             # axis
#             t_axis = np.array([x[0], 0, 0]) + self.axis_pose[0]
#             r_axis = np.eye(3) @ self.axis_pose[1]
#             positions_dict.update({"axis": [self.axis_Actor, t_axis, r_axis]})
#
#             # short_pendulum_shaft
#             t_short_pendulum_shaft = np.array([x[0], 0, 0]) + self.short_pendulum_shaft_pose[0]
#             r_short_pendulum_shaft = pm.rotation_matrix_xyz("z", x[4], "rad") @ self.short_pendulum_shaft_pose[1]
#             positions_dict.update({"short_pendulum_shaft": [self.short_pendulum_shaft_Actor,
#                                                             t_short_pendulum_shaft,
#                                                             r_short_pendulum_shaft]})
#             # short_pendulum
#             t_short_pendulum = (np.array([x[0], 0, 0])
#                                 + pm.rotation_matrix_xyz("z", x[4], "rad") @ self.short_pendulum_pose[0])
#
#             r_short_pendulum = pm.rotation_matrix_xyz("z", x[4], "rad") @ self.short_pendulum_pose[1]
#             positions_dict.update({"short_pendulum": [self.short_pendulum_Actor,
#                                                       t_short_pendulum,
#                                                       r_short_pendulum]})
#
#             # short_pendulum_weight
#             t_short_pendulum_weight = (np.array([x[0], 0, 0])
#                                        + pm.rotation_matrix_xyz("z", x[4], "rad") @ self.short_pendulum_weight_pose[0])
#             r_short_pendulum_weight = pm.rotation_matrix_xyz("z", x[4], "rad") @ self.short_pendulum_weight_pose[1]
#             positions_dict.update({"short_pendulum_weight": [self.short_pendulum_weight_Actor,
#                                                              t_short_pendulum_weight,
#                                                              r_short_pendulum_weight]})
#
#             # long_pendulum_shaft
#             t_long_pendulum_shaft = np.array([x[0], 0, 0]) + self.long_pendulum_shaft_pose[0]
#             r_long_pendulum_shaft = pm.rotation_matrix_xyz("z", x[2], "rad") @ self.long_pendulum_shaft_pose[1]
#             positions_dict.update({"long_pendulum_shaft": [self.long_pendulum_shaft_Actor,
#                                                            t_long_pendulum_shaft,
#                                                            r_long_pendulum_shaft]})
#
#             # long_pendulum
#             t_long_pendulum = (np.array([x[0], 0, 0])
#                                + pm.rotation_matrix_xyz("z", x[2], "rad") @ self.long_pendulum_pose[0])
#             r_long_pendulum = pm.rotation_matrix_xyz("z", x[2], "rad") @ self.long_pendulum_pose[1]
#             positions_dict.update({"long_pendulum": [self.long_pendulum_Actor,
#                                                      t_long_pendulum,
#                                                      r_long_pendulum]})
#
#             # long_pendulum_weight
#             t_long_pendulum_weight = (np.array([x[0], 0, 0])
#                                       + pm.rotation_matrix_xyz("z", x[2], "rad") @ self.long_pendulum_weight_pose[0])
#             r_long_pendulum_weight = pm.rotation_matrix_xyz("z", x[2], "rad") @ self.long_pendulum_weight_pose[1]
#             positions_dict.update({"long_pendulum_weight": [self.long_pendulum_weight_Actor,
#                                                             t_long_pendulum_weight,
#                                                             r_long_pendulum_weight]})
#
#             return positions_dict
#
#         @staticmethod
#         def set_body_state(pos_dict):
#
#             for x in pos_dict.values():
#                 poke = vtk.vtkMatrix4x4()
#                 actor = x[0]
#                 t = x[1]
#                 r = x[2]
#                 for i in range(3):
#                     for n in range(3):
#                         poke.SetElement(i, n, r[i, n])
#                     poke.SetElement(i, 3, t[i])
#
#                 actor.PokeMatrix(poke)
#
#         def update_scene(self, x):
#             """
#             update the body states
#             """
#             self.set_body_state(self.calc_positions(x))
#
#     pm.register_visualizer(TwoPendulumVisualizer)
#
# except ImportError as e:
#     print("BallTube Visualizer:")
#     print(e.msg)
#     print("VTK Visualization not available.")


class MplRodPendulumVisualizer(pm.MplVisualizer):

    def __init__(self, q_widget, q_layout):
        pm.MplVisualizer.__init__(self, q_widget, q_layout)
        self.axes.set_xlim(mp.x_min_plot, mp.x_max_plot)
        self.axes.set_ylim(mp.y_min_plot, mp.y_max_plot)
        self.axes.set_aspect("equal")

        self.beam = mpl.patches.Rectangle(xy=[-mp.beam_length/2, -(mp.beam_height + mp.cart_height/2)],
                                          width=mp.beam_length,
                                          height=mp.beam_height,
                                          color="lightgrey")
        self.cart = mpl.patches.Rectangle(xy=[-mp.cart_length/2, -mp.cart_height/2],
                                          width=mp.cart_length,
                                          height=mp.cart_height,
                                          color="dimgrey")
        self.rod_pendulum_shaft = mpl.patches.Circle(xy=[0, 0],
                                                     radius=mp.pendulum_shaft_radius,
                                                     color="lightgrey",
                                                     zorder=3)

        t = mpl.transforms.Affine2D().rotate_deg(180) + self.axes.transData
        self.rod_pendulum = mpl.patches.Rectangle(xy=[-mp.rod_pendulum_radius, 0],
                                                  width=2*mp.rod_pendulum_radius,
                                                  height=mp.rod_pendulum_height,
                                                  color="#0059A3",  # TUD CD HKS 44_K
                                                  zorder=1,
                                                  transform=t)
        self.axes.add_patch(self.beam)
        self.axes.add_patch(self.cart)
        self.axes.add_patch(self.rod_pendulum_shaft)
        self.axes.add_patch(self.rod_pendulum)

    def update_scene(self, x):
        x0 = x[0]
        phi = np.rad2deg(x[1])

        # cart and shaft
        self.cart.set_x(-mp.cart_length/2 + x0)
        self.rod_pendulum_shaft.center = [x0, 0]

        t_phi1 = mpl.transforms.Affine2D().rotate_deg_around(x0, 0, phi) + self.axes.transData

        # rod pendulum
        self.rod_pendulum.set_xy([-mp.rod_pendulum_radius + x0, 0])
        self.rod_pendulum.set_transform(t_phi1)

        self.canvas.draw()

pm.register_visualizer(MplRodPendulumVisualizer)


