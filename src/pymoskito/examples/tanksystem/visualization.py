# -*- coding: utf-8 -*-
import matplotlib as mpl
import matplotlib.patches

import pymoskito as pm
from . import settings as st


class MplTankVisualizer(pm.MplVisualizer):

    def __init__(self, q_widget, q_layout):
        pm.MplVisualizer.__init__(self, q_widget, q_layout)

        self.rT = 0.06
        self.hT = 0.3
        self.axes.set_xlim(-4 * self.rT, 4 * self.rT + 2 * self.rT + 4 * self.rT)
        self.axes.set_ylim(-0.1, self.hT + 0.1)
        self.axes.set_aspect("equal")
        self.axes.get_xaxis().set_visible(False)
        self.axes.get_yaxis().set_visible(False)

        tube1_house = mpl.patches.Rectangle(xy=[0, 0],
                                            width=2 * self.rT,
                                            height=self.hT,
                                            linewidth=2,
                                            fill=False,
                                            zorder=2)
        self.axes.add_patch(tube1_house)

        self.tube1 = mpl.patches.Rectangle(xy=[0, 0],
                                           width=2 * self.rT,
                                           height=0,
                                           linewidth=0.1,
                                           fill=True,
                                           color='blue',
                                           zorder=1)
        self.axes.add_patch(self.tube1)

        tube2_house = mpl.patches.Rectangle(xy=[4 * self.rT + 2 * self.rT, 0],
                                            width=2 * self.rT,
                                            height=self.hT,
                                            linewidth=2,
                                            fill=False,
                                            zorder=2)
        self.axes.add_patch(tube2_house)

        self.tube2 = mpl.patches.Rectangle(xy=[4 * self.rT + 2 * self.rT, 0],
                                           width=2 * self.rT,
                                           height=0,
                                           linewidth=0.1,
                                           fill=True,
                                           color='blue',
                                           zorder=1)
        self.axes.add_patch(self.tube2)

        conT1_house_above = mpl.lines.Line2D([-3 * self.rT, -3 * self.rT + 3 * self.rT],
                                             [0.1 * self.hT + 0.1 * self.hT, 0.1 * self.hT + 0.1 * self.hT],
                                             linewidth=2,
                                             color='black',
                                             zorder=3)
        self.axes.add_line(conT1_house_above)

        conT1_house_below = mpl.lines.Line2D([-3 * self.rT, -3 * self.rT + 3 * self.rT],
                                             [0.1 * self.hT, 0.1 * self.hT],
                                             linewidth=2,
                                             color='black',
                                             zorder=3)
        self.axes.add_line(conT1_house_below)

        self.conT1 = mpl.patches.Rectangle(xy=[(-3 * self.rT), 0.1 * self.hT],
                                           width=(3 * self.rT),
                                           height=0.1 * self.hT,
                                           linewidth=2,
                                           fill=True,
                                           color='white',
                                           zorder=3)
        self.axes.add_patch(self.conT1)

        conT1T2_house_above = mpl.lines.Line2D([2 * self.rT, 2 * self.rT + 4 * self.rT],
                                               [0.1 * self.hT + 0.1 * self.hT, 0.1 * self.hT + 0.1 * self.hT],
                                               linewidth=2,
                                               color='black',
                                               zorder=3)
        self.axes.add_line(conT1T2_house_above)

        conT1T2_house_below = mpl.lines.Line2D([2 * self.rT, 2 * self.rT + 4 * self.rT],
                                               [0.1 * self.hT, 0.1 * self.hT],
                                               linewidth=2,
                                               color='black',
                                               zorder=3)
        self.axes.add_line(conT1T2_house_below)

        self.conT1T2 = mpl.patches.Rectangle(xy=[(2 * self.rT), 0.1 * self.hT],
                                             width=(4 * self.rT),
                                             height=0.1 * self.hT,
                                             linewidth=2,
                                             fill=True,
                                             color='white',
                                             zorder=3)
        self.axes.add_patch(self.conT1T2)

        conT2_house_above = mpl.lines.Line2D([4 * self.rT + 4 * self.rT, 4 * self.rT + 4 * self.rT + self.rT],
                                             [0.1 * self.hT + 0.1 * self.hT, 0.1 * self.hT + 0.1 * self.hT],
                                             linewidth=2,
                                             color='black',
                                             zorder=3)
        self.axes.add_line(conT2_house_above)

        conT2_house_below = mpl.lines.Line2D([4 * self.rT + 4 * self.rT, 4 * self.rT + 4 * self.rT + self.rT],
                                             [0.1 * self.hT, 0.1 * self.hT],
                                             linewidth=2,
                                             color='black',
                                             zorder=3)
        self.axes.add_line(conT2_house_below)

        self.conT2 = mpl.patches.Rectangle(xy=[(4 * self.rT + 4 * self.rT), 0.1 * self.hT],
                                           width=self.rT,
                                           height=0.1 * self.hT,
                                           linewidth=2,
                                           fill=True,
                                           color='white',
                                           zorder=3)
        self.axes.add_patch(self.conT2)

        pump_house = mpl.patches.Circle(xy=[-1.5 * self.rT, 0.15 * self.hT],
                                        radius=0.1 * self.hT,
                                        linewidth=1,
                                        edgecolor='black',
                                        facecolor='white',
                                        zorder=10)
        self.axes.add_patch(pump_house)

        pump = mpl.patches.Polygon([[-1.5 * self.rT, 0.15 * self.hT + 0.1 * self.hT],
                                    [-1.5 * self.rT + 0.1 * self.hT, 0.15 * self.hT],
                                    [-1.5 * self.rT, 0.15 * self.hT - 0.1 * self.hT]],
                                   linewidth=1,
                                   closed=False,
                                   edgecolor='black',
                                   facecolor='white',
                                   zorder=10)
        self.axes.add_patch(pump)

        ventil_house = mpl.patches.Rectangle(xy=[3.25 * self.rT, 0.05 * self.hT],
                                             width=1.5 * self.rT,
                                             height=0.2 * self.hT,
                                             fill=True,
                                             color='white',
                                             zorder=10)
        self.axes.add_patch(ventil_house)

        ventil = mpl.patches.Polygon([[3.25 * self.rT, 0.05 * self.hT],
                                      [3.25 * self.rT + 1.5 * self.rT, 0.05 * self.hT + 0.2 * self.hT],
                                      [3.25 * self.rT + 1.5 * self.rT, 0.05 * self.hT],
                                      [3.25 * self.rT, 0.05 * self.hT + 0.2 * self.hT]],
                                     linewidth=1,
                                     edgecolor='black',
                                     facecolor='white',
                                     zorder=10)
        self.axes.add_patch(ventil)

        self.axes.text(self.rT, self.hT + 0.01, 'Tank 1', horizontalalignment='center')
        self.axes.text(4 * self.rT + 3 * self.rT, self.hT + 0.01, 'Tank 2', horizontalalignment='center')

    def update_scene(self, x):
        if 0 < x[0] < st.hT:
            self.conT1.set_color('blue')
            self.tube1.set_height(x[0] * self.hT / st.hT)
        elif x[0] >= st.hT:
            self.conT1.set_color('blue')
            self.tube1.set_height(self.hT)
        else:
            self.conT1.set_color('white')
            self.tube1.set_height(0)
        if 0 < x[1] < st.hT:
            self.conT1T2.set_color('blue')
            self.conT2.set_color('blue')
            self.tube2.set_height(x[1] * self.hT / st.hT)
        elif x[1] >= st.hT:
            self.conT1.set_color('blue')
            self.tube1.set_height(self.hT)
        else:
            self.conT1T2.set_color('white')
            self.conT2.set_color('white')
            self.tube2.set_height(0)
        self.canvas.draw()


pm.register_visualizer(MplTankVisualizer)
