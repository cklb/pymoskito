# -*- coding: utf-8 -*-
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import pymoskito as pm


class TwoPendulum(pm.PostProcessingModule):
    """
    plot diagrams of all system quantities
    """
    def __init__(self):
        pm.PostProcessingModule.__init__(self)
        return

    def run(self, data):
        return_list = []

        t = data["results"]["time"]
        x0 = data["results"]["Solver"][:, 0]
        x0_vel = data["results"]["Solver"][:, 1]
        phi1 = data["results"]["Solver"][:, 2]
        phi1_vel = data["results"]["Solver"][:, 3]
        phi2 = data["results"]["Solver"][:, 4]
        phi2_vel = data["results"]["Solver"][:, 5]

        val_list = [x0, x0_vel, phi1, phi1_vel, phi2, phi2_vel]

        title_list = ["Position of the cart",
                      "Velocity of the cart",
                      "Angle long pendulum",
                      "Angular velocity long pendulum",
                      "Angle short pendulum",
                      "Angular velocity short pendulum"]
        x_label_list = [r"$x_{0}$ in m",
                        r"$\dot{x}_{0}$ in m/s",
                        r"$\varphi_{1}$ in degree",
                        r"$\dot{\varphi}_{1}$ in degree/s",
                        r"$\varphi_{2}$ in degree",
                        r"$\dot{\varphi}_{2}$ in degree/s"]
        filename_list = ["x0",
                         "x0_vel",
                         "phi1",
                         "phi1_vel",
                         "phi2",
                         "phi2_vel"]
        if 0:
            for idx, val in enumerate(val_list):
                fig = Figure()
                axes = fig.add_subplot(111)
                axes.set_title(r"\textbf{%s}" % title_list[idx])
                axes.plot(t, val, c="k")
                axes.set_xlim(left=0, right=t[-1])
                axes.set_xlabel(r"Time in s")
                axes.set_ylabel(r"%s" % x_label_list[idx])
                axes.grid(True)
                canvas = FigureCanvas(fig)

                plot_name = "_".join([data["regime name"], self.name, filename_list[idx]])
                return_list.append({"name": plot_name, "figure": canvas})

                # save file
                self.write_output_files(result_name="_".join([data["regime name"], filename_list[idx]]),
                                        figure=fig,
                                        output=pm.construct_result_dict(data, output={}))

        #################################################
        # this section is for combined and custom plots
        # plot both angle of the pendulums in one plot
        plot_selection = {"x0_x0_vel": True,
                          "phi1_phi2": True,
                          "V_V_dot": True}

        if plot_selection["x0_x0_vel"]:
            self._logger.info("creating x0_x0_vel plot")

            fig = Figure()
            axes = fig.add_subplot(111)
            axes.plot(t, x0, c="b", label=r"$x_{0}$ in m")
            axes.plot(t, x0_vel, c="r", label=r"$\dot{x}_{0}$ in $\frac{\mathrm{m}}{\mathrm{s}}$")
            axes.set_xlim(left=t[0], right=t[-1])
            axes.set_xlabel(r"Time in s")
            axes.set_ylabel(r"")

            axes.grid(True)
            axes.legend()
            axes.legend(loc=0)
            canvas = FigureCanvas(fig)

            plot_name = "_".join([data["regime name"], self.name, "x0_x0_vel"])
            return_list.append({"name": plot_name, "figure": canvas})

            # save file
            self.write_output_files(result_name="_".join([data["regime name"], "x0_x0_vel"]),
                                    figure=fig,
                                    output=pm.construct_result_dict(data, output={}))

        if plot_selection["phi1_phi2"]:
            self._logger.info("creating phi1_phi2 plot")

            fig = Figure()
            axes = fig.add_subplot(111)
            axes.plot(t, np.rad2deg(phi1), c="k", label=r"$\varphi_{1}$")
            axes.plot(t, np.rad2deg(phi2), c="b", label=r"$\varphi_{2}$")
            axes.set_xlim(left=t[0], right=t[-1])
            axes.set_xlabel(r"Time in s")
            axes.set_ylabel(r"Angle in $^{\circ}$")

            # start, end = axes.get_ylim()
            # fine segmentation
            # axes.set_yticks(np.arange(int(start/30)*30, int(end/30)*30 + 30, 30), minor=True)
            # axes.set_yticks(np.arange(int(start/90)*90, int(end/90)*90 + 90, 90), minor=False)
            # rough segmentation
            # axes.set_yticks(np.arange(int(start/90)*90, int(end/90)*90 + 90, 90), minor=True)
            # axes.set_yticks(np.arange(int(start/180)*180, int(end/180)*180 + 180, 180), minor=False)
            # axes.grid(which="minor", alpha=0.2)
            # axes.grid(which="major", alpha=0.5)
            axes.grid(True)
            axes.legend()
            axes.legend(loc=0)
            canvas = FigureCanvas(fig)

            plot_name = "_".join([data["regime name"], self.name, "phi1_phi2"])
            return_list.append({"name": plot_name, "figure": canvas})

            # save file
            self.write_output_files(result_name="_".join([data["regime name"], "phi1_phi2"]),
                                    figure=fig,
                                    output=pm.construct_result_dict(data, output={}))

        if plot_selection["V_V_dot"]:
            self._logger.debug("creating V_V_dot plot")

            V, V_dot = self.calc_v_and_v_dot(data, val_list)

            fig = Figure()
            axes = fig.add_subplot(111)
            axes.plot(t, V, c="k", label=r"$V$ in $\frac{\mathrm{kg}^{2}\mathrm{m}^{4}}{\mathrm{s}^{4}}$")
            # axes.plot(t, V_dot, c="b", label=r"$\dot{V}$ in $\frac{\mathrm{kg}^{2}\mathrm{m}^{4}}{\mathrm{s}^{5}}$")
            axes.set_xlim(left=t[0], right=t[-1])
            axes.set_xlabel(r"Time in s")
            axes.set_ylabel(r"")

            axes.grid(True)
            axes.legend()
            axes.legend(loc=0)
            canvas = FigureCanvas(fig)

            plot_name = "_".join([data["regime name"], self.name, "V_V_dot"])
            return_list.append({"name": plot_name, "figure": canvas})

            # save file
            self.write_output_files(result_name="_".join([data["regime name"], "V_V_dot"]),
                                    figure=fig,
                                    output=pm.construct_result_dict(data, output={}))

        return return_list

    @staticmethod
    def calc_v_and_v_dot(data, val_list):
        if "Controller" in data["modules"]:
            if "long pendulum" in data["modules"]["Controller"] and "short pendulum" in data["modules"]["Controller"]:
                # extract parameter to simplify the calculation of V and V_dot
                m0_star = data["modules"]["Model"]["m0*"]
                m1_star = data["modules"]["Model"]["m1*"]
                m2_star = data["modules"]["Model"]["m2*"]
                l1_star = data["modules"]["Model"]["l1*"]
                l2_star = data["modules"]["Model"]["l2*"]
                # d0 = data["modules"]["Model"]["d0"]
                d1 = data["modules"]["Model"]["d1"]
                d2 = data["modules"]["Model"]["d2"]
                J_DP1 = data["modules"]["Model"]["J_DP1"]
                J_DP2 = data["modules"]["Model"]["J_DP2"]
                g = data["modules"]["Model"]["g"]
                k = data["modules"]["Controller"]["k"]

                # calculate point mass model parameter
                l1 = J_DP1/(m1_star*l1_star)
                l2 = J_DP2/(m2_star*l2_star)

                m1 = (m1_star*l1_star)**2/J_DP1
                m2 = (m2_star*l2_star)**2/J_DP2
                m0 = m0_star + (m1_star - m1) + (m2_star - m2)

                w = m1*l1/(m2*l2)

                # extract state from val_list
                x0, x0_vel, phi1, phi1_vel, phi2, phi2_vel = val_list
                E0 = 0.5*m0*x0**2
                E1 = 0
                E2 = 0

                if data["modules"]["Controller"]["long pendulum"] == "u":
                    E1 = 0.5*m1*l1**2*phi1_vel**2 + m1*g*l1*(np.cos(phi1) + 1)
                elif data["modules"]["Controller"]["long pendulum"] == "o":
                    E1 = 0.5*m1*l1**2*phi1_vel**2 + m1*g*l1*(np.cos(phi1) - 1)

                if data["modules"]["Controller"]["short pendulum"] == "u":
                    E2 = 0.5*m2*l2**2*phi2_vel**2 + m2*g*l2*(np.cos(phi2) + 1)
                elif data["modules"]["Controller"]["short pendulum"] == "o":
                    E2 = 0.5*m2*l2**2*phi2_vel**2 + m2*g*l2*(np.cos(phi2) - 1)

                G = m0*x0_vel*E0 + m1*l1*phi1_vel*np.cos(phi1)*E1 + m2*l2*phi2_vel*np.cos(phi2)*E2*w**2

                V = 0.5*E0**2 + 0.5*E1**2 + 0.5*E2**2

                V_dot = -k*G**2 - d1*phi1_vel**2*E1 - d2*phi2_vel**2*E2

        else:
            V = np.zeros(len(val_list[0]))
            V_dot = np.zeros(len(val_list[0]))

        return [V, V_dot]


class SimulationVerification(pm.PostProcessingModule):
    """
    plot diagrams of all system quantities
    """

    def __init__(self):
        pm.PostProcessingModule.__init__(self)
        return

    def run(self, data):
        return_list = []

        t = data["results"]["time"]
        x0 = data["results"]["Solver"][:, 0]
        x0_vel = data["results"]["Solver"][:, 1]
        phi1 = data["results"]["Solver"][:, 2]
        phi1_vel = data["results"]["Solver"][:, 3]
        phi2 = data["results"]["Solver"][:, 4]
        phi2_vel = data["results"]["Solver"][:, 5]

        # extract parameter for further calculation
        m0_star = data["modules"]["Model"]["m0*"]
        m1_star = data["modules"]["Model"]["m1*"]
        m2_star = data["modules"]["Model"]["m2*"]
        l1_star = data["modules"]["Model"]["l1*"]
        l2_star = data["modules"]["Model"]["l2*"]
        d0 = data["modules"]["Model"]["d0"]
        d1 = data["modules"]["Model"]["d1"]
        d2 = data["modules"]["Model"]["d2"]
        J_DP1 = data["modules"]["Model"]["J_DP1"]
        J_DP2 = data["modules"]["Model"]["J_DP2"]
        g = data["modules"]["Model"]["g"]

        # calculate point mass model parameter
        l1 = J_DP1/(m1_star*l1_star)
        l2 = J_DP2/(m2_star*l2_star)
        m1 = (m1_star*l1_star)**2/J_DP1
        m2 = (m2_star*l2_star)**2/J_DP2
        m0 = m0_star + (m1_star - m1) + (m2_star - m2)

        # calculate the analytic solution of a pendulum angle
        # initial equation
        # phi_dd = g*sin(phi)/l1 - (d1*phi_d)/(m1*l1**2) + cos(phi)*u/l1
        # linearisation in point phi_e = pi and u = 0 --> transformation: phi_lin = phi - phi_e
        phi_e = np.pi
        phi_vel_e = 0
        # phi_dd_lin  + (d1*phi_d_lin)/(m1*l1**2) + g*phi_lin/l1
        # usage of the appropriation method
        # lambda**2 + (d1/(m1*l1**2))*lambda + g/l = 0
        # usage of the pq-formula
        p = d1/(m1*l1**2)
        q = g/l1
        # parameter of the conjugate complex zero pair
        a = -p/2
        b = np.sqrt(abs((p/2)**2 - q))

        # get initial values for angle and angle velocity
        phi1_0 = phi1[0]
        phi1_0_vel = phi1_vel[0]
        # transform initial values into linear valid range
        phi1_0_lin = phi1_0 - phi_e
        phi1_0_vel_lin = phi1_0_vel - phi_vel_e

        # calculate unknown parameter of the analytic solution
        C1 = phi1_0_lin
        C2 = -a*phi1_0_lin/b

        phi1_lin_analytic = np.exp(a*t)*(C1*np.cos(b*t) + C2*np.sin(b*t))
        phi1_vel_lin_analytic = np.exp(a*t)*(a*(C1*np.cos(b*t) + C2*np.sin(b*t)) + b*(-C1*np.sin(b*t) + C2*np.cos(b*t)))

        # re-transformation of phi with phi = phi_lin + phi_e
        phi1_analytic = phi1_lin_analytic + phi_e
        phi1_vel_analytic = phi1_vel_lin_analytic + phi_vel_e

        self._logger.debug("creating plot for verification")
        self._logger.debug("error of phi1 and phi1 analytic: {}".format(sum(abs(phi1-phi1_analytic))))
        self._logger.debug("Parameter of the analytic solution: a={}, b={}, C1={}, C2={}".format(a, b, C1, C2))

        fig = Figure()
        axes = fig.add_subplot(211)
        axes.plot(t, np.rad2deg(phi1),
                  c="k",
                  linestyle="-",
                  label=r"$\varphi_{1}$")
        axes.plot(t, np.rad2deg(phi1_analytic),
                  c="red",
                  linestyle="--",
                  linewidth=0.8,
                  label=r"$\varphi_{1,\mathrm{ana}}$")
        axes.set_xlim(left=t[0], right=t[-1])
        axes.set_xlabel(r"Time in s")
        axes.set_ylabel(r"Angle in $^{\circ}$")
        axes.grid()
        axes.legend()
        axes.legend(loc=0)

        axes1 = fig.add_subplot(212)
        axes1.plot(t, np.rad2deg(phi1_vel),
                   c="k",
                   linestyle="-",
                   label=r"$\dot{\varphi}_{1}$")
        axes1.plot(t, np.rad2deg(phi1_vel_analytic),
                   c="red",
                   linestyle="--",
                   linewidth=0.8,
                   label=r"$\dot{\varphi}_{1,\mathrm{ana}}$")
        axes1.set_xlim(left=t[0], right=t[-1])
        axes1.set_xlabel(r"Time in s")
        axes1.set_ylabel(r"Angular velocity in $^\circ\hspace{-3pt}/\mathrm{s}$")
        axes1.grid()
        axes1.legend()
        axes1.legend(loc=0)
        canvas = FigureCanvas(fig)

        plot_name = "_".join([data["regime name"], self.name, "phi1"])
        return_list.append({"name": plot_name, "figure": canvas})

        # save file
        self.write_output_files(result_name="_".join([data["regime name"], "phi1"]),
                                figure=fig,
                                output=pm.construct_result_dict(data, output={}))

        return return_list

        # parameter of the oscillation differential equation
        # D = d1*np.sqrt(g/l1)/(2*m1*l1**2)
        # omega0 = np.sqrt(l1/g)

pm.register_processing_module(pm.PostProcessingModule, TwoPendulum)
pm.register_processing_module(pm.PostProcessingModule, SimulationVerification)
