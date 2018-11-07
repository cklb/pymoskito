# -*- coding: utf-8 -*-
import numpy as np
import matplotlib as mpl
import matplotlib.patches

import pymoskito as pm

from . import settings as st

try:
    import vtk

    class VtkTankVisualizer(pm.VtkVisualizer):

        def __init__(self, renderer):
            pm.VtkVisualizer.__init__(self, renderer)

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

            # save this view
            self.save_camera_pose()

        @staticmethod
        def calc_positions(x):
            """
            Calculate stationary vectors and rot. matrices for bodies
            """
            # not used, because the fan is not visualized
            # r_fan = np.zeros(3)
            # t_fan = np.zeros((3, 3))

            r_ball = np.array([0, x[2]/st.scale, 0])
            t_ball = np.eye(3)

            return [r_ball, t_ball]

        @staticmethod
        def set_body_state(actor, r, t):
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

    pm.register_visualizer(VtkTankVisualizer)

except ImportError as e:
    vtk = None
    print("Tank Visualizer:")
    print(e)
    print("VTK Visualization not available.")


class MplTankVisualizer(pm.MplVisualizer):

    def __init__(self, q_widget, q_layout):
        pm.MplVisualizer.__init__(self, q_widget, q_layout)

        self.axes.set_xlim(-4 * st.rT1, 4 * st.rT1 + 2 * st.rT2 + 4 * st.rT2)
        self.axes.set_ylim(-0.1, st.hT1 + 0.1)
        self.axes.set_aspect("equal")
        self.axes.get_xaxis().set_visible(False)
        self.axes.get_yaxis().set_visible(False)

        tube1_house = mpl.patches.Rectangle(xy=[0, 0],
                                            width=2 * st.rT1,
                                            height=st.hT1,
                                            linewidth=2,
                                            fill=False,
                                            zorder=2)
        self.axes.add_patch(tube1_house)

        self.tube1 = mpl.patches.Rectangle(xy=[0, 0],
                                           width=2 * st.rT1,
                                           height=0,
                                           linewidth=0.1,
                                           fill=True,
                                           color='blue',
                                           zorder=1)
        self.axes.add_patch(self.tube1)

        tube2_house = mpl.patches.Rectangle(xy=[4 * st.rT1 + 2 * st.rT2, 0],
                                            width=2 * st.rT2,
                                            height=st.hT2,
                                            linewidth=2,
                                            fill=False,
                                            zorder=2)
        self.axes.add_patch(tube2_house)

        self.tube2 = mpl.patches.Rectangle(xy=[4 * st.rT1 + 2 * st.rT2, 0],
                                           width=2 * st.rT2,
                                           height=0,
                                           linewidth=0.1,
                                           fill=True,
                                           color='blue',
                                           zorder=1)
        self.axes.add_patch(self.tube2)

        conT1_house_above = mpl.lines.Line2D([-3 * st.rT1, -3 * st.rT1 + 3 * st.rT1],
                                             [0.1 * st.hT1 + 0.1 * st.hT1, 0.1 * st.hT1 + 0.1 * st.hT1],
                                             linewidth=2,
                                             color='black',
                                             zorder=3)
        self.axes.add_line(conT1_house_above)

        conT1_house_below = mpl.lines.Line2D([-3 * st.rT1, -3 * st.rT1 + 3 * st.rT1],
                                             [0.1 * st.hT1, 0.1 * st.hT1],
                                             linewidth=2,
                                             color='black',
                                             zorder=3)
        self.axes.add_line(conT1_house_below)

        self.conT1 = mpl.patches.Rectangle(xy=[(-3 * st.rT1), 0.1 * st.hT1],
                                           width=(3 * st.rT1),
                                           height=0.1 * st.hT1,
                                           linewidth=2,
                                           fill=True,
                                           color='white',
                                           zorder=3)
        self.axes.add_patch(self.conT1)

        conT1T2_house_above = mpl.lines.Line2D([2 * st.rT1, 2 * st.rT1 + 4 * st.rT1],
                                               [0.1 * st.hT1 + 0.1 * st.hT1, 0.1 * st.hT1 + 0.1 * st.hT1],
                                               linewidth=2,
                                               color='black',
                                               zorder=3)
        self.axes.add_line(conT1T2_house_above)

        conT1T2_house_below = mpl.lines.Line2D([2 * st.rT1, 2 * st.rT1 + 4 * st.rT1],
                                               [0.1 * st.hT1, 0.1 * st.hT1],
                                               linewidth=2,
                                               color='black',
                                               zorder=3)
        self.axes.add_line(conT1T2_house_below)

        self.conT1T2 = mpl.patches.Rectangle(xy=[(2 * st.rT1), 0.1 * st.hT1],
                                             width=(4 * st.rT1),
                                             height=0.1 * st.hT1,
                                             linewidth=2,
                                             fill=True,
                                             color='white',
                                             zorder=3)
        self.axes.add_patch(self.conT1T2)

        conT2_house_above = mpl.lines.Line2D([4 * st.rT1 + 4 * st.rT2, 4 * st.rT1 + 4 * st.rT2 + st.rT1],
                                             [0.1 * st.hT1 + 0.1 * st.hT1, 0.1 * st.hT1 + 0.1 * st.hT1],
                                             linewidth=2,
                                             color='black',
                                             zorder=3)
        self.axes.add_line(conT2_house_above)

        conT2_house_below = mpl.lines.Line2D([4 * st.rT1 + 4 * st.rT2, 4 * st.rT1 + 4 * st.rT2 + st.rT1],
                                             [0.1 * st.hT1, 0.1 * st.hT1],
                                             linewidth=2,
                                             color='black',
                                             zorder=3)
        self.axes.add_line(conT2_house_below)

        self.conT2 = mpl.patches.Rectangle(xy=[(4 * st.rT1 + 4 * st.rT2), 0.1 * st.hT1],
                                           width=st.rT1,
                                           height=0.1 * st.hT1,
                                           linewidth=2,
                                           fill=True,
                                           color='white',
                                           zorder=3)
        self.axes.add_patch(self.conT2)

        pump_house = mpl.patches.Circle(xy=[-1.5 * st.rT1, 0.15 * st.hT1],
                                        radius=0.1 * st.hT1,
                                        linewidth=1,
                                        edgecolor='black',
                                        facecolor='white',
                                        zorder=10)
        self.axes.add_patch(pump_house)

        pump = mpl.patches.Polygon([[-1.5 * st.rT1, 0.15 * st.hT1 + 0.1 * st.hT1],
                                    [-1.5 * st.rT1 + 0.1 * st.hT1, 0.15 * st.hT1],
                                    [-1.5 * st.rT1, 0.15 * st.hT1 - 0.1 * st.hT1]],
                                   linewidth=1,
                                   closed=False,
                                   edgecolor='black',
                                   facecolor='white',
                                   zorder=10)
        self.axes.add_patch(pump)

        ventil_house = mpl.patches.Rectangle(xy=[3.25 * st.rT1, 0.05 * st.hT1],
                                             width=1.5 * st.rT1,
                                             height=0.2 * st.hT1,
                                             fill=True,
                                             color='white',
                                             zorder=10)
        self.axes.add_patch(ventil_house)

        ventil = mpl.patches.Polygon([[3.25 * st.rT1, 0.05 * st.hT1],
                                      [3.25 * st.rT1 + 1.5 * st.rT1, 0.05 * st.hT1 + 0.2 * st.hT1],
                                      [3.25 * st.rT1 + 1.5 * st.rT1, 0.05 * st.hT1],
                                      [3.25 * st.rT1, 0.05 * st.hT1 + 0.2 * st.hT1]],
                                     linewidth=1,
                                     edgecolor='black',
                                     facecolor='white',
                                     zorder=10)
        self.axes.add_patch(ventil)

        self.axes.text(st.rT1, st.hT1 + 0.01, 'Tank 1', horizontalalignment='center')
        self.axes.text(4 * st.rT1 + 3 * st.rT2, st.hT2 + 0.01, 'Tank 2', horizontalalignment='center')

    def update_scene(self, x):
        if x[0] > 0:
            self.conT1.set_color('blue')
            self.tube1.set_height(x[0])
        else:
            self.conT1.set_color('white')
            self.tube1.set_height(0)
        if x[1] > 0:
            self.conT1T2.set_color('blue')
            self.conT2.set_color('blue')
            self.tube2.set_height(x[1])
        else:
            self.conT1T2.set_color('white')
            self.conT2.set_color('white')
            self.tube2.set_height(0)
        self.canvas.draw()


pm.register_visualizer(MplTankVisualizer)
