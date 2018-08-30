# -*- coding: utf-8 -*-
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D as Line

from .processing_core import PostProcessingModule, MetaProcessingModule
from .resources import colors
from .tools import sort_tree

__all__ = ["StepResponse", "PlotAll", "XYMetaProcessor"]


class StepResponse(PostProcessingModule):
    """
    Postprocessor that creates diagrams for step response experiments.

    Various measures are taken, displayed in a diagram and saved to result
    files. The following list contains the measured/calculated entries and
    their explanations:

        - rise time (t_rise): time needed until the output reaches 90% of its
        desired value
        - correction time (t_corr): time needed until the output reaches the
        desired value for the first time
        - overshoot time (t_over): time of the greatest overshot
        - overshot: maximum error between is and desired while approaching the
        desired value
        - damping time (t_damp): time needed for the output to enter and remain
        in an epsilon region around the desired value

    Args:
        model_idx(int): Index of the model output to use.
        trajectory_idx(int): Index of the trajectory output to use.

    """
    line_color = colors.HKS41K100
    line_width = 2
    line_style = '-'
    font_size = 20
    font_color = colors.HKS41K100
    spacing = 0.05
    counter = 0
    eps = 1e-3

    def __init__(self, model_idx=0, trajectory_idx=0):
        PostProcessingModule.__init__(self)
        self.model_idx = model_idx
        self.trajectory_idx = trajectory_idx
        self.label_positions = None
        return

    def run(self, data):

        # dict for calculated values
        output = {}

        # reset counter
        self.counter = 0

        # calculate data sets
        t = data["results"]["time"]
        y = data["results"]["Model"][:, self.model_idx]
        traj_data = data["results"]["Trajectory"]
        if traj_data.ndim == 2:
            yd = data["results"]["Trajectory"][-1, self.trajectory_idx]
        elif traj_data.ndim == 3:
            yd = data["results"]["Trajectory"][-1, self.trajectory_idx, 0]
        else:
            raise ValueError("unknown Trajectory type.")

        self.label_positions = np.arange(y.min() + 0.1 * yd,
                                         yd,
                                         (yd - y.min()) / 4)

        # create plot
        fig = Figure()
        axes = fig.add_subplot(111)
        axes.grid()
        axes.set_title(r"Step Response")
        axes.plot(t, y, c=colors.HKS44K100, linewidth=self.line_width)
        axes.set_xlim(left=0, right=t[-1])
        axes.set_xlabel(r"Time in $\si{\second}$")
        axes.set_ylabel(r"System Output in $\si{\metre}$")

        # create desired line
        desired_line = Line([0, t[-1]], [yd, yd],
                            lw=1, ls=self.line_style, c='k')
        axes.add_line(desired_line)

        # calc rise-time (Anstiegszeit)
        try:
            t_rise = t[np.where(y > 0.9 * yd)][0]
            self.create_time_line(axes, t, y, t_rise, r"$T_r$")
            output.update({"t_rise": t_rise})
        except IndexError:
            output.update({"t_rise": None})

        # calc correction-time (Anregelzeit)
        try:
            t_corr = t[np.where(y > yd)][0]
            self.create_time_line(axes, t, y, t_corr, r"$T_{c}$")
            output.update({"t_corr": t_corr})
        except IndexError:
            output.update({"t_corr": None})

        # calc overshoot-time and overshoot in percent
        # (Überschwingzeit und Überschwingen)
        if output["t_corr"]:
            if yd > 0:
                y_max = np.max(y[np.where(t > output["t_corr"])])
            else:
                y_max = np.min(y[np.where(t > output["t_corr"])])

            t_over = t[np.where(y == y_max)][0]
            overshoot = y_max - yd
            overshoot_per = overshoot / yd * 100
            self._logger.info("Overshoot: {}%".format(overshoot_per))

            self.create_time_line(axes, t, y, t_over, r"$T_o$")
            output.update(dict(t_over=t_over,
                               overshoot=overshoot,
                               overshoot_percent=overshoot_per))
        else:
            output.update(dict(t_over=None,
                               overshoot=None,
                               overshoot_percent=None))

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

            t_damp = t[enter_idx]
            self.create_time_line(axes, t, y, t_damp, r"$T_{\epsilon}$")
            output.update({"t_damp": t_damp})
        except IndexError:
            output.update({"t_damp": None})

        # create epsilon tube
        upper_bound_line = Line([0, t[-1]], [yd + self.eps, yd + self.eps],
                                ls="--", c=self.line_color)
        axes.add_line(upper_bound_line)
        lower_bound_line = Line([0, t[-1]], [yd - self.eps, yd - self.eps],
                                ls="--", c=self.line_color)
        axes.add_line(lower_bound_line)

        # calc stationary control deviation
        control_deviation = y[-1] - yd
        output.update({"stationary_error": control_deviation})
        # check for sim success
        if not data["results"]["finished"]:
            for key in output.keys():
                output[key] = None

        # add settings and metrics to dictionary results
        results = {}
        y_des = np.ones_like(y) * yd
        step_width = 1 / data["modules"]["Solver"]["measure rate"]
        results.update({"metrics": self.calc_metrics(y,
                                                     y_des,
                                                     step_width,
                                                     output)})
        results.update({"modules": data["modules"]})

        canvas = FigureCanvas(fig)

        self.write_output_files(data["regime name"], fig, results)

        return [dict(name='_'.join([data["regime name"], self.name]),
                     figure=canvas)]

    def create_time_line(self, axes, t, y, time_value, label):
        if time_value != t[-1]:
            time_line = Line([time_value, time_value],
                             [np.min(y), y[np.where(t == time_value)][0]],
                             linewidth=self.line_width,
                             ls=self.line_style,
                             c=self.line_color)
            axes.add_line(time_line)
            axes.text(time_value + self.spacing,
                      self.label_positions[self.counter],
                      label,
                      color=self.font_color,
                      size=self.font_size)
            self.counter += 1

    def calc_metrics(self, measured_values, desired_values, step_width, output):
        """
        Calculate metrics

        Args:
            measured_values(array): Array holding the measured outputs.
            desired_values(array): Array holding the desired outputs.
            step_width(float): Simulation step width.

        Returns:
            dict: Calculated metrics.
        """
        l1_norm_itae = self.calc_l1_norm_itae(measured_values,
                                              desired_values,
                                              step_width)
        l1_norm_abs = self.calc_l1_norm_abs(measured_values,
                                            desired_values,
                                            step_width)

        self._logger.info("L1NormITAE: {}".format(l1_norm_itae))
        self._logger.info("L1NormAbs: {}".format(l1_norm_abs))

        return {'L1NormITAE': l1_norm_itae, 'L1NormAbs': l1_norm_abs}


class PlotAll(PostProcessingModule):
    """
    plot diagrams of all system quantities
    """

    def __init__(self):
        PostProcessingModule.__init__(self)
        return

    def run(self, data):

        # dict for calculated values
        output = {}
        return_list = []

        t = data["results"]["time"]
        val = t  # default

        for module_name, module_data in data["results"].items():
            if module_name in ["time", "finished", "Simulation"]:
                continue

            module_shape = module_data.shape
            for idx in range(module_shape[1]):
                if len(module_shape) == 3:
                    val = module_data[:, idx, 0]
                if len(module_shape) == 2:
                    val = module_data[:, idx]

                plot_name = "_".join([data["regime name"],
                                      self.name,
                                      module_name, str(idx)])
                fig = Figure()
                axes = fig.add_subplot(111)
                axes.set_title(r"\textbf{"
                               + "{} {}".format(
                                    module_name.replace("_", " "), idx)
                               + "}")
                axes.plot(t, val, c='k')
                axes.set_xlim(left=0, right=t[-1])
                axes.set_xlabel(r"Time in s")
                axes.set_ylabel(r"{} {}".format(
                    module_name.replace("_", " "), idx))
                axes.grid(True)
                canvas = FigureCanvas(fig)

                return_list.append({"name": plot_name, "figure": canvas})

        return return_list


class XYMetaProcessor(MetaProcessingModule):
    """
    Create XY-diagrams for the given keys from metadata.

    Args:
        x_path(list): List of dictionary keys pointing to the desired values
            of the x axis.
        y_path(list): List of dictionary keys pointing to the desired values
            of the y axis.
        sort_key(list): List of dictionary keys used for grouping the meta data.
        x_idx(int): If the *x_path* points to an array but only one component
            is to be selected, its index can be given. [-1]
        y_idx(int): If the *y_path* points to an array but only one component
            is to be selected, its index can be given. [-1]
        line_style(str): Either ``line`` or ``bar``.
    """

    def __init__(self, x_path, y_path, sort_key, x_idx=-1, y_idx=-1,
                 line_style="line", title="", x_label="", y_label=""):
        MetaProcessingModule.__init__(self)
        self.x_path = x_path
        self.x_idx = x_idx
        self.y_path = y_path
        self.y_idx = y_idx
        self.sort_key = sort_key
        self.line_style = line_style
        self.title = title
        self.x_lbl = x_label
        self.y_lbl = y_label

        self.fig = None
        self.axes = None

        return

    def process(self, post_results):
        # create tree with relevant data
        source = sort_tree(post_results, self.sort_key)

        # create plot
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111)

        self.plot_family(source,
                         self.x_path,
                         self.y_path,
                         self.line_style,
                         self.x_idx,
                         self.y_idx)
        self.set_plot_labeling(self.title, True, self.x_lbl, self.y_lbl,
                               self.line_style)

        # extract member_names, therefore
        # (subtract common appendix like *Controller or *Feedforward)
        member_names = [x[:-len(self.x_path[1])] for x in source.keys()]

        canvas = FigureCanvas(self.fig)

        # write output files
        file_name = (self.name
                     + "_".join([self.x_path[1], "("])
                     + "".join(member_names) + ")")
        self.write_output_files(file_name, self.fig)

        return [{'figure': canvas, 'name': self.name}]


def construct_result_dict(data, output):
    # check for sim success
    if not data["results"]["finished"]:
        for key in output.keys():
            output[key] = None

    # add settings and metrics to dictionary results
    results = {}
    results.update({'metrics': output})
    results.update({'modules': data['modules']})

    return results
