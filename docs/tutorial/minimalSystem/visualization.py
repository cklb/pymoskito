# -*- coding: utf-8 -*-
import numpy as np
import pymoskito as pm

import matplotlib as mpl
import matplotlib.patches
import matplotlib.transforms

from . import settings as mp


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



