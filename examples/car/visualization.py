# -*- coding: utf-8 -*-
from __future__ import division
from pymoskito.visualization import MplVisualizer

import settings as st
import matplotlib as mpl
import numpy as np


class CarVisualizer(MplVisualizer):

    def __init__(self, q_widget, q_layout):
        MplVisualizer.__init__(self, q_widget, q_layout)
        self.image = None
        self.color = "green"
        self.axes.set_xlim(-1, 1);
        self.axes.set_ylim(-0, 2);
        self.axes.set_aspect('equal')
        self.axes.set_xlabel(r'$\xi_1/m$')
        self.axes.set_ylabel(r'$\xi_2/m$')
        self.update_scene(st.initial_state)

    def update_scene(self, x):
        x1, x2, theta1, theta2, theta3 = x
        d1, l2, d2, l3 = st.d1, st.l2, st.d2, st.l3
        dia = st.dia
        car_radius = st.dia/2
        wheel = st.dia/4
        ct1 = np.cos(theta1)
        st1 = np.sin(theta1)
        ct2 = np.cos(theta2)
        st2 = np.sin(theta2)
        ct3 = np.cos(theta3)
        st3 = np.sin(theta3)

        [xR1_1, yR1_1, xR1_2 ,yR1_2,xR2_1,yR2_1,xR2_2,yR2_2,x1_gelenk1,x2_gelenk1, \
         x1_trailer1,x2_trailer1,x1T1_1,y1T1_1,x1T1_2,y1T1_2,x1T2_1,y1T2_1,x1T2_2,y1T2_2,x1_gelenk2,x2_gelenk2, \
         x1_trailer2,x2_trailer2,x2T1_1,y2T1_1,x2T1_2,y2T1_2 ,x2T2_1,y2T2_1,x2T2_2,y2T2_2] \
            = self.calc_positions(x1,x2,theta1,theta2,theta3,dia, d1, l2, d2, l3, car_radius,wheel,ct1,st1,ct2,st2,ct3,st3)

        if self.image is None:
            #Gehäuse
            sphere=mpl.patches.Circle((x1,x2),car_radius,color=self.color,zorder=0)
            self.axes.add_patch(sphere)
            #Rad1
            rad1=self.axes.add_line(mpl.lines.Line2D([xR1_1,xR1_2],[yR1_1,yR1_2],color='k',zorder=1,linewidth=3.0))
            #Rad2
            rad2=self.axes.add_line(mpl.lines.Line2D([xR2_1,xR2_2],[yR2_1,yR2_2],color='k',zorder=1,linewidth=3.0))
            track = None
            #Stange1
            stange1=self.axes.add_line(mpl.lines.Line2D([x1,x1_gelenk1],[x2,x2_gelenk1],color='k',zorder=3,linewidth=2.0))
            #Stange2
            stange2=self.axes.add_line(mpl.lines.Line2D([x1_gelenk1,x1_trailer1],[x2_gelenk1,x2_trailer1],color='k',zorder=3,linewidth=2.0))
            #Stange3
            stange3=self.axes.add_line(mpl.lines.Line2D([x1_trailer1,x1_gelenk2],[x2_trailer1,x2_gelenk2],color='k',zorder=3,linewidth=2.0))
            #Stange4
            stange4=self.axes.add_line(mpl.lines.Line2D([x1_gelenk2,x1_trailer2],[x2_gelenk2,x2_trailer2],color='k',zorder=3,linewidth=2.0))
            #Gelenk1
            gelenk1=mpl.patches.Circle((x1_gelenk1,x2_gelenk1),0.01,color='k',zorder=3)
            self.axes.add_patch(gelenk1)
            #Gelenk2
            gelenk2=mpl.patches.Circle((x1_gelenk2,x2_gelenk2),0.01,color='k',zorder=3)
            self.axes.add_patch(gelenk2)
            #Hänger1
            trailer1 = mpl.patches.FancyBboxPatch((x1_trailer1-dia*0.25,x2_trailer1-dia*0.25),0.5*dia,0.5*dia,color='0.5',zorder=0,fill=True,mutation_scale=0.05)
            t_start = self.axes.transData
            t = mpl.transforms.Affine2D().rotate_around(x1_trailer1,x2_trailer1,theta2)
            t_end = t + t_start
            trailer1.set_transform(t_end)
            self.axes.add_patch(trailer1)
            radt11=self.axes.add_line(mpl.lines.Line2D([x1T1_1,x1T1_2],[y1T1_1,y1T1_2],color='k',zorder=1,linewidth=3.0))
            radt12=self.axes.add_line(mpl.lines.Line2D([x1T2_1,x1T2_2],[y1T2_1,y1T2_2],color='k',zorder=1,linewidth=3.0))
            achse1=self.axes.add_line(mpl.lines.Line2D([x1_trailer1 + 3./8.*dia*st2,x1_trailer1 + 0.5*dia*st2],[x2_trailer1 - 3./8.*dia*ct2,x2_trailer1 - 0.5*dia*ct2],color='k',zorder=1,linewidth=2.0))
            achse2=self.axes.add_line(mpl.lines.Line2D([x1_trailer1 - 3./8.*dia*st2,x1_trailer1 - 0.5*dia*st2],[x2_trailer1 + 3./8.*dia*ct2,x2_trailer1 + 0.5*dia*ct2],color='k',zorder=1,linewidth=2.0))
            #Hänger2
            trailer2 = mpl.patches.FancyBboxPatch((x1_trailer2-dia*0.25,x2_trailer2-dia*0.25),0.5*dia,0.5*dia,color='0.5',zorder=0,fill=True,mutation_scale=0.05)
            t_start = self.axes.transData
            t = mpl.transforms.Affine2D().rotate_around(x1_trailer2,x2_trailer2,theta3)
            t_end = t + t_start
            trailer2.set_transform(t_end)
            self.axes.add_patch(trailer2)
            radt21=self.axes.add_line(mpl.lines.Line2D([x2T1_1,x2T1_2],[y2T1_1,y2T1_2],color='k',zorder=1,linewidth=3.0))
            radt22=self.axes.add_line(mpl.lines.Line2D([x2T2_1,x2T2_2],[y2T2_1,y2T2_2],color='k',zorder=1,linewidth=3.0))
            achse3=self.axes.add_line(mpl.lines.Line2D([x1_trailer2 + 3./8.*dia*st3,x1_trailer2 + 0.5*dia*st3],[x2_trailer2 - 3./8.*dia*ct3,x2_trailer2 - 0.5*dia*ct3],color='k',zorder=1,linewidth=2.0))
            achse4=self.axes.add_line(mpl.lines.Line2D([x1_trailer2 - 3./8.*dia*st3,x1_trailer2 - 0.5*dia*st3],[x2_trailer2 + 3./8.*dia*ct3,x2_trailer2 + 0.5*dia*ct3],color='k',zorder=1,linewidth=2.0))

            self.image = [sphere,rad1,rad2,track,stange1,stange2,stange3,stange4,gelenk1,gelenk2,trailer1,trailer2,radt11,radt12,radt21,radt22,achse1,achse2,achse3,achse4]

        else:
            #IPS()
            #Gehäuse
            self.image[0].center = (x1,x2)
            #Rad2
            self.image[1].set_data([xR1_1,xR1_2],[yR1_1,yR1_2])
            #Rad2
            self.image[2].set_data([xR2_1,xR2_2],[yR2_1,yR2_2])
            #track
            #self.image[3].set_data([self.x[:,0]],[self.x[:,1]])
            #flat track
            # self.image[3].set_data([self.P[:,0]],[self.P[:,1]])
            #Stange1
            self.image[4].set_data([x1,x1_gelenk1],[x2,x2_gelenk1])
            #Stange2
            self.image[5].set_data([x1_gelenk1,x1_trailer1],[x2_gelenk1,x2_trailer1])
            #Stange3
            self.image[6].set_data([x1_trailer1,x1_gelenk2],[x2_trailer1,x2_gelenk2])
            #Stange4
            self.image[7].set_data([x1_gelenk2,x1_trailer2],[x2_gelenk2,x2_trailer2])
            #Gelenk1
            self.image[8].center = (x1_gelenk1,x2_gelenk1)
            #Gelenk2
            self.image[9].center = (x1_gelenk2,x2_gelenk2)
            #Hänger1
            self.image[10].remove()
            trailer1 = mpl.patches.FancyBboxPatch((x1_trailer1-dia*0.25,x2_trailer1-dia*0.25),0.5*dia,0.5*dia,color='0.5',zorder=0,fill=True,mutation_scale=0.05)
            t_start = self.axes.transData
            t = mpl.transforms.Affine2D().rotate_around(x1_trailer1,x2_trailer1,theta2)
            t_end = t + t_start
            trailer1.set_transform(t_end)
            self.axes.add_patch(trailer1)
            self.image[10] = trailer1
            #Hänger2
            self.image[11].remove()
            trailer2 = mpl.patches.FancyBboxPatch((x1_trailer2-dia*0.25,x2_trailer2-dia*0.25),0.5*dia,0.5*dia,color='0.5',zorder=0,fill=True,mutation_scale=0.05)
            t_start = self.axes.transData
            t = mpl.transforms.Affine2D().rotate_around(x1_trailer2,x2_trailer2,theta3)
            t_end = t + t_start
            trailer2.set_transform(t_end)
            self.axes.add_patch(trailer2)
            self.image[11] = trailer2
            self.image[12].set_data([x1T1_1,x1T1_2],[y1T1_1,y1T1_2])
            self.image[13].set_data([x1T2_1,x1T2_2],[y1T2_1,y1T2_2])
            self.image[14].set_data([x2T1_1,x2T1_2],[y2T1_1,y2T1_2])
            self.image[15].set_data([x2T2_1,x2T2_2],[y2T2_1,y2T2_2])
            self.image[16].set_data([x1_trailer1 + 3./8.*dia*st2,x1_trailer1 + 0.5*dia*st2],[x2_trailer1 - 3./8.*dia*ct2,x2_trailer1 - 0.5*dia*ct2])
            self.image[17].set_data([x1_trailer1 - 3./8.*dia*st2,x1_trailer1 - 0.5*dia*st2],[x2_trailer1 + 3./8.*dia*ct2,x2_trailer1 + 0.5*dia*ct2])
            self.image[18].set_data([x1_trailer2 + 3./8.*dia*st3,x1_trailer2 + 0.5*dia*st3],[x2_trailer2 - 3./8.*dia*ct3,x2_trailer2 - 0.5*dia*ct3])
            self.image[19].set_data([x1_trailer2 - 3./8.*dia*st3,x1_trailer2 - 0.5*dia*st3],[x2_trailer2 + 3./8.*dia*ct3,x2_trailer2 + 0.5*dia*ct3])

        self.canvas.draw()
        self.save_if_checked()

    def calc_positions(self,x1,x2,theta1,theta2,theta3,dia, d1, l2, d2, l3, car_radius,wheel,ct1,st1,ct2,st2,ct3,st3):

        #Rad1
        xR1_1 = x1 + st1*car_radius - ct1*wheel
        yR1_1 = x2 - ct1*car_radius - st1*wheel
        xR1_2 = x1 + st1*car_radius + ct1*wheel
        yR1_2 = x2 - ct1*car_radius + st1*wheel
        #Rad2
        xR2_1 = x1 - st1*car_radius - ct1*wheel
        yR2_1 = x2 +ct1*car_radius - st1*wheel
        xR2_2 = x1 - st1*car_radius + ct1*wheel
        yR2_2 = x2 + ct1*car_radius + st1*wheel
        #Stange1
        x1_gelenk1 = x1 - d1*ct1
        x2_gelenk1 = x2 - d1*st1

        #Hänger1
        x1_trailer1 = x1_gelenk1 - l2*ct2
        x2_trailer1 = x2_gelenk1 - l2*st2
        #Hänger1 Rad1
        x1T1_1 = x1_trailer1 + st2*car_radius - ct2*wheel
        y1T1_1 = x2_trailer1 - ct2*car_radius - st2*wheel
        x1T1_2 = x1_trailer1 + st2*car_radius + ct2*wheel
        y1T1_2 = x2_trailer1 - ct2*car_radius + st2*wheel
        #Hänger1 Rad2
        x1T2_1 = x1_trailer1 - st2*car_radius - ct2*wheel
        y1T2_1 = x2_trailer1 + ct2*car_radius - st2*wheel
        x1T2_2 = x1_trailer1 - st2*car_radius + ct2*wheel
        y1T2_2 = x2_trailer1 + ct2*car_radius + st2*wheel
        #Stange2
        x1_gelenk2 = x1_trailer1 - d2*ct2
        x2_gelenk2 = x2_trailer1 - d2*st2

        #Hänger2
        x1_trailer2 = x1_gelenk2 - l3*ct3
        x2_trailer2 = x2_gelenk2 - l3*st3
        #Hänger2 Rad1
        x2T1_1 = x1_trailer2 + st3*car_radius - ct3*wheel
        y2T1_1 = x2_trailer2 - ct3*car_radius - st3*wheel
        x2T1_2 = x1_trailer2 + st3*car_radius + ct3*wheel
        y2T1_2 = x2_trailer2 - ct3*car_radius + st3*wheel
        #Hänger Rad2
        x2T2_1 = x1_trailer2 - st3*car_radius - ct3*wheel
        y2T2_1 = x2_trailer2 + ct3*car_radius - st3*wheel
        x2T2_2 = x1_trailer2 - st3*car_radius + ct3*wheel
        y2T2_2 = x2_trailer2 + ct3*car_radius + st3*wheel

        return  xR1_1, yR1_1, xR1_2 ,yR1_2,xR2_1,yR2_1,xR2_2,yR2_2,x1_gelenk1,x2_gelenk1, \
                x1_trailer1,x2_trailer1,x1T1_1,y1T1_1,x1T1_2,y1T1_2,x1T2_1,y1T2_1,x1T2_2,y1T2_2,x1_gelenk2,x2_gelenk2, \
                x1_trailer2,x2_trailer2,x2T1_1,y2T1_1,x2T1_2,y2T1_2 ,x2T2_1,y2T2_1,x2T2_2,y2T2_2
