import numpy as np
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from pymoskito.generic_processing_modules import construct_result_dict
from pymoskito.processing_core import PostProcessingModule


class TwoPendulum(PostProcessingModule):
    """
    plot diagrams of all system quantities
    """
    def __init__(self):
        PostProcessingModule.__init__(self)
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
        if 'Simulator' in data["modules"]:  # convert radiant to degree if it is a simulation setup
            phi1 *= (180.0/np.pi)
            phi1_vel *= (180.0/np.pi)
            phi2 *= (180.0/np.pi)
            phi2_vel *= (180.0/np.pi)

        val_list = [x0, x0_vel, phi1, phi1_vel, phi2, phi2_vel]

        title_list = ["Wagenposition",
                      "Wagengeschwindigkeit",
                      "Winkel gro\ss{}es Pendel",
                      "Winkelgeschwindigkeit gro\ss{}es Pendel",
                      "Winkel kleines Pendel",
                      "Winkelgeschwindigkeit kleines Pendel"]
        x_label_list = [r"$x_{0}$ in m",
                        r"$\dot{x}_{0}$ in m/s",
                        r"$\varphi_{1}$ in Grad",
                        r"$\dot{\varphi}_{1}$ in Grad/s",
                        r"$\varphi_{2}$ in Grad",
                        r"$\dot{\varphi}_{2}$ in Grad/s"]
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
                axes.set_title(r'\textbf{%s}' % title_list[idx])
                axes.plot(t, val, c='k')
                axes.set_xlim(left=0, right=t[-1])
                axes.set_xlabel(r'Zeit in s')
                axes.set_ylabel(r'%s' % x_label_list[idx])
                axes.grid(True)
                canvas = FigureCanvas(fig)

                plot_name = '_'.join([data['regime name'], self.name, filename_list[idx]])
                return_list.append({'name': plot_name, 'figure': canvas})

                # save file
                self.write_output_files(result_name='_'.join([data['regime name'], filename_list[idx]]),
                                        figure=fig,
                                        output=construct_result_dict(data, output={}))

        #################################################
        # this section is for combined and custom plots
        # plot both angle of the pendulums in one plot
        plot_selection = {'x0_x0_vel': False,
                          'phi1_phi2': False,
                          'V_V_dot': True}

        if plot_selection['x0_x0_vel']:
            self._logger.debug("creating x0_x0_vel plot")

            fig = Figure()
            axes = fig.add_subplot(111)
            axes.plot(t, x0, c='b', label=r'$x_{0}$ in m')
            axes.plot(t, x0_vel, c='r', label=r'$\dot{x}_{0}$ in $\frac{\mathrm{m}}{\mathrm{s}}$')
            axes.set_xlim(left=t[0], right=t[-1])
            axes.set_xlabel(r'Zeit in s')
            axes.set_ylabel(r'keine Ahnung')

            axes.grid(True)
            axes.legend()
            axes.legend(loc=0)
            canvas = FigureCanvas(fig)

            plot_name = '_'.join([data['regime name'], self.name, "x0_x0_vel"])
            return_list.append({'name': plot_name, 'figure': canvas})

            # save file
            self.write_output_files(result_name='_'.join([data['regime name'], "x0_x0_vel"]),
                                    figure=fig,
                                    output=construct_result_dict(data, output={}))

        if plot_selection['phi1_phi2']:
            self._logger.debug("creating phi1_phi2 plot")

            fig = Figure()
            axes = fig.add_subplot(111)
            axes.plot(t, phi1, c='k', label=r'$\varphi_{1}$')
            axes.plot(t, phi2, c='b', label=r'$\varphi_{2}$')
            axes.set_xlim(left=t[0], right=t[-1])
            axes.set_xlabel(r'Zeit in s')
            axes.set_ylabel(r'Winkel in $^{\circ}$')

            start, end = axes.get_ylim()
            # fine segmentation
            # axes.set_yticks(np.arange(int(start/30)*30, int(end/30)*30 + 30, 30), minor=True)
            # axes.set_yticks(np.arange(int(start/90)*90, int(end/90)*90 + 90, 90), minor=False)
            # rough segmentation
            axes.set_yticks(np.arange(int(start/90)*90, int(end/90)*90 + 90, 90), minor=True)
            axes.set_yticks(np.arange(int(start/180)*180, int(end/180)*180 + 180, 180), minor=False)
            axes.grid(which='both')
            axes.grid(which='minor', alpha=0.2)
            axes.grid(which='major', alpha=0.5)
            axes.legend()
            axes.legend(loc=0)
            canvas = FigureCanvas(fig)

            plot_name = '_'.join([data['regime name'], self.name, "phi1_phi2"])
            return_list.append({'name': plot_name, 'figure': canvas})

            # save file
            self.write_output_files(result_name='_'.join([data['regime name'], "phi1_phi2"]),
                                    figure=fig,
                                    output=construct_result_dict(data, output={}))

        if plot_selection['V_V_dot']:
            self._logger.debug("creating V_V_dot plot")

            V , V_dot = self.calc_v_and_v_dot(data, val_list)

            fig = Figure()
            axes = fig.add_subplot(111)
            axes.plot(t, V, c='k', label=r'$V$ in $\frac{\mathrm{kg}^{2}\mathrm{m}^{4}}{\mathrm{s}^{4}}$')
            # axes.plot(t, V_dot, c='b', label=r'$\dot{V}$ in $\frac{\mathrm{kg}^{2}\mathrm{m}^{4}}{\mathrm{s}^{5}}$')
            axes.set_xlim(left=t[0], right=t[-1])
            axes.set_xlabel(r'Zeit in s')
            axes.set_ylabel(r'keine Ahnung')

            axes.grid(True)
            axes.legend()
            axes.legend(loc=0)
            canvas = FigureCanvas(fig)

            plot_name = '_'.join([data['regime name'], self.name, "V_V_dot"])
            return_list.append({'name': plot_name, 'figure': canvas})

            # save file
            self.write_output_files(result_name='_'.join([data['regime name'], "V_V_dot"]),
                                    figure=fig,
                                    output=construct_result_dict(data, output={}))

        return return_list

    def calc_v_and_v_dot(self, data, val_list):
        if 'long pendulum' in data['modules']['Controller'] and 'short pendulum' in data['modules']['Controller']:

            # extract parameter to simplify the calculation of V and V_dot
            m0_star = data['modules']['Model']['m0*']
            m1_star = data['modules']['Model']['m1*']
            m2_star = data['modules']['Model']['m2*']
            l1_star = data['modules']['Model']['l1*']
            l2_star = data['modules']['Model']['l2*']
            d0 = data['modules']['Model']['d0']
            d1 = data['modules']['Model']['d1']
            d2 = data['modules']['Model']['d2']
            J_DP1 = data['modules']['Model']['J_DP1']
            J_DP2 = data['modules']['Model']['J_DP2']
            g = data['modules']['Model']['g']
            k = data['modules']['Controller']['k']

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

            if data['modules']['Controller']['long pendulum'] == 'u':
                E1 = 0.5*m1*l1**2*phi1_vel**2 + m1*g*l1*(np.cos(phi1) + 1)
            elif data['modules']['Controller']['long pendulum'] == 'o':
                E1 = 0.5*m1*l1**2*phi1_vel**2 + m1*g*l1*(np.cos(phi1) - 1)

            if data['modules']['Controller']['short pendulum'] == 'u':
                E2 = 0.5*m2*l2**2*phi2_vel**2 + m2*g*l2*(np.cos(phi2) + 1)
            elif data['modules']['Controller']['short pendulum'] == 'o':
                E2 = 0.5*m2*l2**2*phi2_vel**2 + m2*g*l2*(np.cos(phi2) - 1)

            G = m0*x0_vel*E0 + m1*l1*phi1_vel*np.cos(phi1)*E1 + m2*l2*phi2_vel*np.cos(phi2)*E2*w**2

            V = 0.5*E0**2 + 0.5*E1**2 + 0.5*E2**2

            V_dot = -k*G**2 - d1*phi1_vel**2*E1 - d2*phi2_vel**2*E2

        else:
            V = np.zeros(len(val_list[0]))
            V_dot = np.zeros(len(val_list[0]))

        return [V, V_dot]
