# -*- coding: utf-8 -*-
import matplotlib as mpl
import numpy as np

import pymoskito as pm

from . import settings as st


class CarVisualizer(pm.MplVisualizer):
    def __init__(self, q_widget, q_layout):
        pm.MplVisualizer.__init__(self, q_widget, q_layout)
        self.image = None
        self.color = "green"
        self.axes.set_xlim(-1, 1)
        self.axes.set_ylim(-0, 2)
        self.axes.set_aspect('equal')
        self.axes.set_xlabel(r'$\xi_1/m$')
        self.axes.set_ylabel(r'$\xi_2/m$')
        self.update_scene(st.initial_state)

    def update_scene(self, x):
        x1, x2, theta1, theta2, theta3 = x
        d1, l2, d2, l3 = st.d1, st.l2, st.d2, st.l3
        dia = st.dia
        car_radius = st.dia / 2
        wheel = st.dia / 4
        ct1 = np.cos(theta1)
        st1 = np.sin(theta1)
        ct2 = np.cos(theta2)
        st2 = np.sin(theta2)
        ct3 = np.cos(theta3)
        st3 = np.sin(theta3)

        [xR1_1, yR1_1, xR1_2, yR1_2, xR2_1, yR2_1, xR2_2, yR2_2,
         x1_joint1, x2_joint1,
         x1_trailer1, x2_trailer1,
         x1T1_1, y1T1_1, x1T1_2, y1T1_2, x1T2_1, y1T2_1, x1T2_2, y1T2_2,
         x1_joint2, x2_joint2,
         x1_trailer2, x2_trailer2,
         x2T1_1, y2T1_1, x2T1_2, y2T1_2, x2T2_1, y2T2_1, x2T2_2, y2T2_2
         ] = self.calc_positions(
            x1, x2, theta1, theta2, theta3, dia, d1, l2, d2, l3, car_radius, wheel, ct1, st1, ct2, st2, ct3, st3)

        if self.image is None:
            # chassis
            sphere = mpl.patches.Circle((x1, x2), car_radius, color=self.color, zorder=0)
            self.axes.add_patch(sphere)

            # wheel 1
            wheel_1 = self.axes.add_line(
                mpl.lines.Line2D([xR1_1, xR1_2], [yR1_1, yR1_2], color='k', zorder=1, linewidth=3.0))

            # wheel 2
            wheel_2 = self.axes.add_line(
                mpl.lines.Line2D([xR2_1, xR2_2], [yR2_1, yR2_2], color='k', zorder=1, linewidth=3.0))
            track = None

            # rod 1
            rod_1 = self.axes.add_line(
                mpl.lines.Line2D([x1, x1_joint1], [x2, x2_joint1], color='k', zorder=3, linewidth=2.0))

            # rod 2
            rod_2 = self.axes.add_line(
                mpl.lines.Line2D([x1_joint1, x1_trailer1], [x2_joint1, x2_trailer1], color='k', zorder=3,
                                 linewidth=2.0))

            # rod 3
            rod_3 = self.axes.add_line(
                mpl.lines.Line2D([x1_trailer1, x1_joint2], [x2_trailer1, x2_joint2], color='k', zorder=3,
                                 linewidth=2.0))

            # rod 4
            rod_4 = self.axes.add_line(
                mpl.lines.Line2D([x1_joint2, x1_trailer2], [x2_joint2, x2_trailer2], color='k', zorder=3,
                                 linewidth=2.0))

            # joint 1
            joint_1 = mpl.patches.Circle((x1_joint1, x2_joint1), 0.01, color='k', zorder=3)
            self.axes.add_patch(joint_1)

            # joint 2
            joint_2 = mpl.patches.Circle((x1_joint2, x2_joint2), 0.01, color='k', zorder=3)
            self.axes.add_patch(joint_2)

            # trailer 1
            trailer1 = mpl.patches.FancyBboxPatch((x1_trailer1 - dia * 0.25, x2_trailer1 - dia * 0.25), 0.5 * dia,
                                                  0.5 * dia, color='0.5', zorder=0, fill=True, mutation_scale=0.05)
            t_start = self.axes.transData
            t = mpl.transforms.Affine2D().rotate_around(x1_trailer1, x2_trailer1, theta2)
            t_end = t + t_start
            trailer1.set_transform(t_end)
            self.axes.add_patch(trailer1)

            wheel_t11 = self.axes.add_line(
                mpl.lines.Line2D([x1T1_1, x1T1_2], [y1T1_1, y1T1_2], color='k', zorder=1, linewidth=3.0))

            wheel_t12 = self.axes.add_line(
                mpl.lines.Line2D([x1T2_1, x1T2_2], [y1T2_1, y1T2_2], color='k', zorder=1, linewidth=3.0))

            axis1 = self.axes.add_line(
                mpl.lines.Line2D([x1_trailer1 + 3. / 8. * dia * st2, x1_trailer1 + 0.5 * dia * st2],
                                 [x2_trailer1 - 3. / 8. * dia * ct2, x2_trailer1 - 0.5 * dia * ct2], color='k',
                                 zorder=1, linewidth=2.0))

            axis2 = self.axes.add_line(
                mpl.lines.Line2D([x1_trailer1 - 3. / 8. * dia * st2, x1_trailer1 - 0.5 * dia * st2],
                                 [x2_trailer1 + 3. / 8. * dia * ct2, x2_trailer1 + 0.5 * dia * ct2], color='k',
                                 zorder=1, linewidth=2.0))

            # trailer 2
            trailer2 = mpl.patches.FancyBboxPatch((x1_trailer2 - dia * 0.25, x2_trailer2 - dia * 0.25), 0.5 * dia,
                                                  0.5 * dia, color='0.5', zorder=0, fill=True, mutation_scale=0.05)
            t_start = self.axes.transData
            t = mpl.transforms.Affine2D().rotate_around(x1_trailer2, x2_trailer2, theta3)
            t_end = t + t_start
            trailer2.set_transform(t_end)
            self.axes.add_patch(trailer2)

            wheel_t21 = self.axes.add_line(
                mpl.lines.Line2D([x2T1_1, x2T1_2], [y2T1_1, y2T1_2], color='k', zorder=1, linewidth=3.0))

            wheel_t22 = self.axes.add_line(
                mpl.lines.Line2D([x2T2_1, x2T2_2], [y2T2_1, y2T2_2], color='k', zorder=1, linewidth=3.0))

            axis3 = self.axes.add_line(
                mpl.lines.Line2D([x1_trailer2 + 3. / 8. * dia * st3, x1_trailer2 + 0.5 * dia * st3],
                                 [x2_trailer2 - 3. / 8. * dia * ct3, x2_trailer2 - 0.5 * dia * ct3], color='k',
                                 zorder=1, linewidth=2.0))

            axis4 = self.axes.add_line(
                mpl.lines.Line2D([x1_trailer2 - 3. / 8. * dia * st3, x1_trailer2 - 0.5 * dia * st3],
                                 [x2_trailer2 + 3. / 8. * dia * ct3, x2_trailer2 + 0.5 * dia * ct3], color='k',
                                 zorder=1, linewidth=2.0))

            self.image = [sphere, wheel_1, wheel_2, track, rod_1, rod_2, rod_3, rod_4, joint_1, joint_2, trailer1,
                          trailer2, wheel_t11, wheel_t12, wheel_t21, wheel_t22, axis1, axis2, axis3, axis4]

        else:
            # IPS()
            # chassis
            self.image[0].center = (x1, x2)

            # wheel2
            self.image[1].set_data([xR1_1, xR1_2], [yR1_1, yR1_2])

            # wheel2
            self.image[2].set_data([xR2_1, xR2_2], [yR2_1, yR2_2])
            # track
            # self.image[3].set_data([self.x[:,0]],[self.x[:,1]])
            # flat track
            # self.image[3].set_data([self.P[:,0]],[self.P[:,1]])

            # rod 1
            self.image[4].set_data([x1, x1_joint1], [x2, x2_joint1])

            # rod 2
            self.image[5].set_data([x1_joint1, x1_trailer1], [x2_joint1, x2_trailer1])

            # rod 3
            self.image[6].set_data([x1_trailer1, x1_joint2], [x2_trailer1, x2_joint2])

            # rod 4
            self.image[7].set_data([x1_joint2, x1_trailer2], [x2_joint2, x2_trailer2])

            # joint1
            self.image[8].center = (x1_joint1, x2_joint1)

            # joint2
            self.image[9].center = (x1_joint2, x2_joint2)

            # trailer 1
            self.image[10].remove()
            trailer1 = mpl.patches.FancyBboxPatch((x1_trailer1 - dia * 0.25, x2_trailer1 - dia * 0.25), 0.5 * dia,
                                                  0.5 * dia, color='0.5', zorder=0, fill=True, mutation_scale=0.05)
            t_start = self.axes.transData
            t = mpl.transforms.Affine2D().rotate_around(x1_trailer1, x2_trailer1, theta2)
            t_end = t + t_start
            trailer1.set_transform(t_end)
            self.axes.add_patch(trailer1)
            self.image[10] = trailer1
            # trailer 2
            self.image[11].remove()
            trailer2 = mpl.patches.FancyBboxPatch((x1_trailer2 - dia * 0.25, x2_trailer2 - dia * 0.25), 0.5 * dia,
                                                  0.5 * dia, color='0.5', zorder=0, fill=True, mutation_scale=0.05)
            t_start = self.axes.transData
            t = mpl.transforms.Affine2D().rotate_around(x1_trailer2, x2_trailer2, theta3)
            t_end = t + t_start
            trailer2.set_transform(t_end)
            self.axes.add_patch(trailer2)
            self.image[11] = trailer2
            self.image[12].set_data([x1T1_1, x1T1_2], [y1T1_1, y1T1_2])
            self.image[13].set_data([x1T2_1, x1T2_2], [y1T2_1, y1T2_2])
            self.image[14].set_data([x2T1_1, x2T1_2], [y2T1_1, y2T1_2])
            self.image[15].set_data([x2T2_1, x2T2_2], [y2T2_1, y2T2_2])
            self.image[16].set_data([x1_trailer1 + 3. / 8. * dia * st2, x1_trailer1 + 0.5 * dia * st2],
                                    [x2_trailer1 - 3. / 8. * dia * ct2, x2_trailer1 - 0.5 * dia * ct2])
            self.image[17].set_data([x1_trailer1 - 3. / 8. * dia * st2, x1_trailer1 - 0.5 * dia * st2],
                                    [x2_trailer1 + 3. / 8. * dia * ct2, x2_trailer1 + 0.5 * dia * ct2])
            self.image[18].set_data([x1_trailer2 + 3. / 8. * dia * st3, x1_trailer2 + 0.5 * dia * st3],
                                    [x2_trailer2 - 3. / 8. * dia * ct3, x2_trailer2 - 0.5 * dia * ct3])
            self.image[19].set_data([x1_trailer2 - 3. / 8. * dia * st3, x1_trailer2 - 0.5 * dia * st3],
                                    [x2_trailer2 + 3. / 8. * dia * ct3, x2_trailer2 + 0.5 * dia * ct3])

        self.canvas.draw()

    def calc_positions(self, x1, x2, theta1, theta2, theta3, dia, d1, l2, d2, l3, car_wheelius, wheel, ct1, st1, ct2,
                       st2,
                       ct3, st3):
        # wheel 1
        xR1_1 = x1 + st1 * car_wheelius - ct1 * wheel
        yR1_1 = x2 - ct1 * car_wheelius - st1 * wheel
        xR1_2 = x1 + st1 * car_wheelius + ct1 * wheel
        yR1_2 = x2 - ct1 * car_wheelius + st1 * wheel

        # wheel2
        xR2_1 = x1 - st1 * car_wheelius - ct1 * wheel
        yR2_1 = x2 + ct1 * car_wheelius - st1 * wheel
        xR2_2 = x1 - st1 * car_wheelius + ct1 * wheel
        yR2_2 = x2 + ct1 * car_wheelius + st1 * wheel

        # rod 1
        x1_joint1 = x1 - d1 * ct1
        x2_joint1 = x2 - d1 * st1

        # trailer 1
        x1_trailer1 = x1_joint1 - l2 * ct2
        x2_trailer1 = x2_joint1 - l2 * st2

        # trailer 1 wheel 1
        x1T1_1 = x1_trailer1 + st2 * car_wheelius - ct2 * wheel
        y1T1_1 = x2_trailer1 - ct2 * car_wheelius - st2 * wheel
        x1T1_2 = x1_trailer1 + st2 * car_wheelius + ct2 * wheel
        y1T1_2 = x2_trailer1 - ct2 * car_wheelius + st2 * wheel

        # trailer 1 wheel2
        x1T2_1 = x1_trailer1 - st2 * car_wheelius - ct2 * wheel
        y1T2_1 = x2_trailer1 + ct2 * car_wheelius - st2 * wheel
        x1T2_2 = x1_trailer1 - st2 * car_wheelius + ct2 * wheel
        y1T2_2 = x2_trailer1 + ct2 * car_wheelius + st2 * wheel

        # rod 2
        x1_joint2 = x1_trailer1 - d2 * ct2
        x2_joint2 = x2_trailer1 - d2 * st2

        # trailer 2
        x1_trailer2 = x1_joint2 - l3 * ct3
        x2_trailer2 = x2_joint2 - l3 * st3

        # trailer 2 wheel 1
        x2T1_1 = x1_trailer2 + st3 * car_wheelius - ct3 * wheel
        y2T1_1 = x2_trailer2 - ct3 * car_wheelius - st3 * wheel
        x2T1_2 = x1_trailer2 + st3 * car_wheelius + ct3 * wheel
        y2T1_2 = x2_trailer2 - ct3 * car_wheelius + st3 * wheel

        # trailer  wheel 2
        x2T2_1 = x1_trailer2 - st3 * car_wheelius - ct3 * wheel
        y2T2_1 = x2_trailer2 + ct3 * car_wheelius - st3 * wheel
        x2T2_2 = x1_trailer2 - st3 * car_wheelius + ct3 * wheel
        y2T2_2 = x2_trailer2 + ct3 * car_wheelius + st3 * wheel

        return (xR1_1, yR1_1, xR1_2, yR1_2, xR2_1, yR2_1, xR2_2, yR2_2,
                x1_joint1, x2_joint1,
                x1_trailer1, x2_trailer1,
                x1T1_1, y1T1_1, x1T1_2, y1T1_2, x1T2_1, y1T2_1, x1T2_2, y1T2_2,
                x1_joint2, x2_joint2,
                x1_trailer2, x2_trailer2,
                x2T1_1, y2T1_1, x2T1_2, y2T1_2, x2T2_1, y2T2_1, x2T2_2, y2T2_2)

pm.register_visualizer(CarVisualizer)
