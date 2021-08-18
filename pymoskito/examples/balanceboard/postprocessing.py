# -*- coding: utf-8 -*-
import matplotlib as mpl
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D as Line

import pymoskito as pm

from pymoskito.processing_core import PostProcessingModule, MetaProcessingModule
from pymoskito.tools import sort_tree
from pymoskito.resources import colors

class SimpleBalanceBoardPostProcessor(PostProcessingModule):
    """
    plot the three system states
    """

    def __init__(self):
        PostProcessingModule.__init__(self)
        return

    def run(self, data):

        # dict for calculated values
        return_list = []

        t = data["results"]["time"]
        val = t  # default
        diagrams = ["Psi","gamma","Theta"]
        diagrams_descr = ["Brettwinkel","Schlittenauslenkung","Zylinderwinkel"]
        diagram_labels = ["Psi in degree","gamma in m","Theta in degree"]


        for i in range(0,3):
            val = data['results']['Solver'][:,i]
            plot_name = "_".join([data["regime name"],
                                  self.name,
                                  # module_name,
                                  diagrams[i],
                                  str(i)])
            fig = Figure()
            axes = fig.add_subplot(111)
            axes.set_title(diagrams_descr[i] + " " + diagrams[i])
            axes.plot(t, val, c='k')
            axes.set_xlim(left=0, right=t[-1])
            axes.set_xlabel(r"Time in s")
            axes.set_ylabel(diagram_labels[i])
            axes.grid(True)
            canvas = FigureCanvas(fig)

            self.write_output_files((data["regime name"] + "_" +  diagrams[i]), fig, output=None) #output=None to surpress .pof

            return_list.append({"name": plot_name, "figure": canvas})

        return return_list

class ComparisonBalanceBoardPostProcessor(PostProcessingModule):
    """
    plot the three system states
    compare multiple files in one diagram
    """

    def __init__(self):
        PostProcessingModule.__init__(self)
        return

    def run(self, data):

        # dict for calculated values
        return_list = []

        t = data["results"]["time"]
        return_list.append(t)

        for i in range(0, 3):
            val = data['results']['Solver'][:, i]
            return_list.append(val)

        return_list.append(data["regime name"])
        return_list.append(data["simulation"]["step size"])

        return return_list

    def process(self, files):

        result_list = []
        raw_data = []
        for data in files:
            self._logger.info("processing data set: {0}".format(data["regime name"]))
            raw_data.append(self.run(data))

        #-----------------------------read data from list of results--------------------------------------
        t = raw_data[0][0]
        # find longest timeline
        for k in range(0, len(raw_data)):
            if len(raw_data[k][0]) > len(t):
                t = raw_data[k][0]

        #**********************settings for plots*************************************
        val = t  # default
        file_name = "Anfangsauslenkung"
        state_variable = ["$\\Psi$", "$\\gamma$", "$\\Theta$"]
        diagrams_descr = ["Brettwinkel", "Schlittenauslenkung", "Zylinderwinkel"]
        units = ["rad", "$m$", "rad"]
        colours = ["#192D64","#A0C850","r","m","k","#CDDC28","#A0DCF0"]
        plot_linewidth = 1.7
        #plot_labels = ["$\Psi^0 = 25$","$\gamma^0 = 0.2$","$\Theta^0 = 40$","d","e","f"]
        # ****************************************************************************
        plot_labels = []
        step_size = []
        for j in range(0, len(raw_data)):
            plot_labels.append(raw_data[j][4])
            plot_labels[j] = plot_labels[j].replace("_", ", ")
            plot_labels[j] = plot_labels[j].replace("NoCtrl", "System ohne Regler")
            plot_labels[j] = plot_labels[j].replace("LinearCtrl", "Linearer Regler")
            plot_labels[j] = plot_labels[j].replace("GainSchedulingCtrl,", "Gain Scheduling Regler, \n")
            plot_labels[j] = plot_labels[j].replace("theta", "$\\Theta_0$=")
            plot_labels[j] = plot_labels[j].replace("gamma", "$\\gamma_0$=")
            plot_labels[j] = plot_labels[j].replace("psi", "$\\Psi_0$=")
            plot_labels[j] = plot_labels[j].replace("m1", "$m_1$=")
            plot_labels[j] = plot_labels[j].replace("m2", "$m_2$=")
            plot_labels[j] = plot_labels[j].replace("to", "$\\Theta_d$=")
            plot_labels[j] = plot_labels[j].replace("eq0,", "$\\Theta^0$=0, \n")
            plot_labels[j] = plot_labels[j].replace("RL", "von Ruhelage aus (RL)")

            plot_labels[j] = plot_labels[j].replace("-", "$-$")

            step_size.append(raw_data[j][5])


        # create plot
        fig = Figure()
        for i in range(1,4): # index zero is time t

            axes = fig.add_subplot(2, 2, i)
            #axes.set_title(diagrams_descr[i-1] + " " + state_variable[i-1])
            axes.set_xlim(left=0, right=t[-1])
            axes.set_xlabel(r"Zeit in $s$")
            axes.set_ylabel(state_variable[i-1] + ' in ' + units[i-1])
            axes.grid(True)

            for k in range(0, len(raw_data)):
                val = raw_data[k][i]

                #fill up missing values with zeros
                while len(val)<len(t):
                        val = np.append(val,0)


                new_line = axes.plot((step_size[k]/0.001)*t, val, linewidth = plot_linewidth, c = colours[k], label = plot_labels[k])

        axes.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

        fig.tight_layout()
        canvas = FigureCanvas(fig)

        # -------------------------------------------------------------------

        plot_name = file_name
        result_list.append({"name": plot_name, "figure": canvas})

        self.write_output_files(plot_name, fig, output=None)  # output=None to surpress .pof

        return result_list