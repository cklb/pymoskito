# -*- coding: utf-8 -*-
import numpy as np
import matplotlib as mpl
import matplotlib.patches

import pymoskito as pm

from . import settings as st


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
        if 0 < x[0] < st.hT1:
            self.conT1.set_color('blue')
            self.tube1.set_height(x[0])
        elif x[0] >= st.hT1:
            self.conT1.set_color('blue')
            self.tube1.set_height(st.hT1)
        else:
            self.conT1.set_color('white')
            self.tube1.set_height(0)
        if 0 < x[1] < st.hT2:
            self.conT1T2.set_color('blue')
            self.conT2.set_color('blue')
            self.tube2.set_height(x[1])
        elif x[1] >= st.hT2:
            self.conT1.set_color('blue')
            self.tube1.set_height(st.hT2)
        else:
            self.conT1T2.set_color('white')
            self.conT2.set_color('white')
            self.tube2.set_height(0)
        self.canvas.draw()


pm.register_visualizer(MplTankVisualizer)
