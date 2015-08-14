# -*- coding: utf-8 -*-
from __future__ import division
import numpy as np
import matplotlib as mpl
mpl.use("Qt4Agg")
# mpl.rcParams['text.usetex'] = True
mpl.rcParams['text.latex.unicode'] = True
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D as Line

import pymoskito as pm
from processing_core import PostProcessingModule, MetaProcessingModule
from tools import sort_tree, get_sub_value

__author__ = 'stefan'


class StepResponse(PostProcessingModule):
    """
    create diagrams of step responses
    """
    line_color = '#aaaaaa'
    line_style = '-'
    font_size = 20
    spacing = 0.01
    counter = 0
    eps = 1e-3

    def __init__(self):
        PostProcessingModule.__init__(self)
        return

    def run(self, data):

        # dict for calculated values
        output = {}

        # reset counter
        self.counter = 0

        # calculate data sets
        t = data['results']['time']
        y = data['results']['Model']
        yd = data['results']['Trajectory'][-1][0]

        self.pos_label = np.arange(np.min(y) + 0.1*yd, yd, (yd-np.min(y))/4)

        # create plot
        fig = Figure()
        axes = fig.add_subplot(111)
        axes.set_title(r'\textbf{Sprungantwort}')
        axes.plot(t, y, c='k')
        axes.set_xlim(left=0, right=t[-1])
        axes.set_xlabel(r'\textit{Zeit [s]}')
        axes.set_ylabel(r'\textit{Systemausgang [m]}')

        # create desired line
        desired_line = Line([0, t[-1]], [yd, yd], lw=1, ls=self.line_style, c='k')
        axes.add_line(desired_line)

        # calc rise-time (Anstiegszeit)
        try:
            tr = t[np.where(y > 0.9*yd)][0]
            self.create_time_line(axes, t, y, tr, r'$T_r$')
            output.update({'tr': tr})
        except IndexError:
            output.update({'tr': None})

        # calc correction-time (Anregelzeit)
        try:
            correction_time = t[np.where(y > yd)][0]
            self.create_time_line(axes, t, y, correction_time, r'$T_{anr}$')
            output.update({'tanr': correction_time})
        except IndexError:
            output.update({'tanr': None})

        # calc overshoot-time and overshoot in percent (Überschwingzeit und Überschwingen)
        if output['tanr']:
            if yd > 0:
                y_max = np.max(y[np.where(t > correction_time)])
            else:
                y_max = np.min(y[np.where(t > correction_time)])

            overshoot_time = t[np.where(y == y_max)][0]
            do = y_max - yd
            doPercent = do/yd * 100

            self.create_time_line(axes, t, y, overshoot_time, r'$T_o$')
            output.update({'to': overshoot_time, 'do': do, 'doPercent': doPercent})
        else:
            output.update({'to': None, 'do': None, 'doPercent': None})

        # calc damping-time (Beruhigungszeit)
        try:
            enter_idx = -1
            for idx, val in enumerate(y):
                if enter_idx == -1:
                    if abs(val - yd) < self.eps:
                        enter_idx = idx
                else:
                    if abs(val - yd) >= self.eps:
                        enter_idx = -1

            damping_time = t[enter_idx]
            self.create_time_line(axes, t, y, damping_time, r'$T_{\epsilon}$')
            output.update({'teps': damping_time})
        except IndexError:
            output.update({'teps': None})

        # create epsilon tube
        upper_bound_line = Line([0, t[-1]], [yd + self.eps, yd + self.eps], ls='--', c=self.line_color)
        axes.add_line(upper_bound_line)
        lower_bound_line = Line([0, t[-1]], [yd - self.eps, yd - self.eps], ls='--', c=self.line_color)
        axes.add_line(lower_bound_line)

        # calc control deviation
        control_deviation = y[-1] - yd
        output.update({'control_deviation': control_deviation})

        self.calc_metrics(data, output)

        # check for sim success
        if not data["results"]["finished"]:
            for key in output.keys():
                output[key] = None

        # add settings and metrics to dictionary results
        results = {}
        results.update({'metrics': output})
        results.update({'modules': data['modules']})

        canvas = FigureCanvas(fig)

        self.write_output_files(data['regime name'], fig, results)

        return {'name': '_'.join([data['regime name'], self.name]), "figure": canvas}

    def create_time_line(self, axes, t, y, time_value, label):
        if time_value != t[-1]:
            time_line = Line([time_value, time_value],
                             [np.min(y), y[np.where(t == time_value)][0]],
                             ls=self.line_style,
                             c=self.line_color)
            axes.add_line(time_line)
            axes.text(time_value + self.spacing, self.pos_label[self.counter],
                      label, size=self.font_size)
            self.counter += 1

    def calc_metrics(self, data, output):
        """
        calculate metrics for comparison
        """
        # TODO check those they produce crap see output
        l1_norm_itae = self.calc_l1_norm_itae(*self.get_metric_values(data))
        l1_norm_abs = self.calc_l1_norm_abs(*self.get_metric_values(data))

        print 'L1NormITAE: ', l1_norm_itae
        print 'L1NormAbs: ', l1_norm_abs
        print '\n'

        output.update({'L1NormITAE': l1_norm_itae, 'L1NormAbs': l1_norm_abs})

    @staticmethod
    def get_metric_values(data):
        """
        helper function to extract data needed to calculate metrics for this postprocessor
        overload to fit custom model
        :param data: simulation data
        :return: tuple of (is_values, desired_values, step_width)
        """
        metric_values = (data["results"]["Model"],
                         data["results"]["Trajectory"],
                         1/data["modules"]["Solver"]["measure rate"])

        return metric_values

pm.register_processing_module(PostProcessingModule, StepResponse)


class XYMetaProcessor(MetaProcessingModule):
    """
    create XY-diagrams for the given key to be compared
    """
    def __init__(self, sort_key, x_path, y_path):
        MetaProcessingModule.__init__(self)
        self.sort_key = sort_key
        self.x_path = x_path
        self.y_path = y_path

        self.fig = None
        self.axes = None

        return

    def run(self, post_results):
        # create tree with relevant data
        source = sort_tree(post_results, self.sort_key)

        # create plot
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111)

        self.plot_family(source, self.x_path, self.y_path, "line")
        self.set_plot_labeling()

        # # plot for time-difference
        # axes1 = fig.add_subplot(212)
        # axes1 = self.plotVariousController(source, axes1,\
        #         xPath=['modules','trajectory', 'delta t'],\
        #         yPath=['metrics','t_diff'],\
        #         typ='line')
        # axes1 = self.plotSettings(axes1,\
        #         titel=r'\"Ubergangszeitfehler \"uber $\Delta t$',\
        #         grid=True,\
        #         xlabel=r'$\Delta t \, \lbrack s\rbrack$',\
        #         ylabel=r'$e_{t} \, \lbrack s \rbrack$',\
        #         )
        #
        # # spacing
        # fig.subplots_adjust(wspace=0.5, hspace=0.5)

        # extract member_names (subtract common appendix like *Controller or *Feedforward)
        member_names = [x[:-len(self.x_path[1])] for x in source.keys()]

        canvas = FigureCanvas(self.fig)

        # write output files
        file_name = self.name + "_".join([self.x_path[1], "("]) + "".join(member_names) + ")"
        self.write_output_files(file_name, self.fig)

        return [{'figure': canvas, 'name': self.name}]
