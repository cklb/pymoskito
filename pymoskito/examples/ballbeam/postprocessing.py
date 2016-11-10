# -*- coding: utf-8 -*-
import os
import matplotlib as mpl
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

import pymoskito as pm

from . import settings as st

# TODO get those working again


class EvalA1(pm.PostProcessingModule):
    """
    create diagrams for evaluation step A1
    """
    name = 'A1'

    line_color = '#aaaaaa'
    line_style = '-'
    font_size = 20
    #    epsPercent = 2./5
    spacing = 0.01
    counter = 0

    def __init__(self):
        pm.PostProcessingModule.__init__(self)
        self.label_positions = None

    def calc_metrics(self, data, output):
        """
        calculate metrics for comaprism
        """

        L1NormITAE = self.calcL1NormITAE(data)
        L1NormAbs = self.calcL1NormAbs(data)
        #
        #        print 'ITAE score: ', errorIntegral
        print('L1NormITAE: ', L1NormITAE)
        print('L1NormAbs: ', L1NormAbs)
        print('\n')
        output.update({'L1NormITAE': L1NormITAE, 'L1NormAbs': L1NormAbs})

    def create_time_line(self, axes, t, y, time_value, label):
        """
        creates a  vertical line in the diagram, reaching from the x-axis to the plot at a given time t

        :param axes:
        :param t:
        :param y:
        :param time_value:
        :param label:
        :returns new counter value
        """
        # don't create lines on the very left
        if time_value == t[-1]:
            return

        # create timeLine
        time_line = Line2D([time_value, time_value],
                           [np.min(y), y[t.index(time_value)]],
                           ls=self.line_style,
                           c=self.line_color)
        axes.add_line(time_line)
        axes.text(time_value + self.spacing, self.label_posistions[self.label_counter], label, size=self.font_size)

    def run(self, data):
        self.label_counter = 0

        # map data-sets
        t = data["results"]["time"]
        y = data["results"]["Solver"][:, 0]
        yd = data["results"]["Trajectory"][-1, 0, 0]

        # evenly distribute labels
        self.label_positions = np.arange(np.min(y) + 0.1 * yd, yd, (yd - np.min(y)) / 4)

        # create plot
        self.axes.set_title(r"\textbf{Sprungantwort}")
        self.axes.plot(t, y, c="k")
        self.axes.set_xlim(left=0, right=t[-1])
        self.axes.set_ylim(0, 3.5)
        self.axes.set_xlabel(r"\textit{Zeit [s]}")
        self.axes.set_ylabel(r"\textit{Ballposition r(t) [m]}")

        # create desired line
        desired_line = Line2D([0, t[-1]], [yd, yd], lw=1, ls=self.line_style, c='k')
        self.axes.add_line(desired_line)

        return

        # calc rise-time (Anstiegszeit)
        try:
            tr = t[y.index([x for x in y if x > yd * 0.9][0])]
            self.create_time_line(self.axes, t, y, tr, r"$T_r$")
            self.results.update({"tr": tr})
        except IndexError:
            self._logger.warning("failed to calculate rise-time 't_r'")
            self.results.update({"tr": None})

        # calc correction-time (Anregelzeit)
        try:
            t_corr = t[y.index([x for x in y if x > yd][0])]
            self.create_time_line(self.axes, t, y, t_corr, r'$T_{anr}$')
            self.results.update({'tanr': t_corr})
        except IndexError:
            self._logger.warning("failed to calculate correction-time 't_corr'")
            self.results.update({'tanr': None})

        # calc overshoot-time and overshoot in percent (Überschwingzeit und Überschwingen)
        if self.results['tanr']:
            if yd > 0:
                y_max = np.max(y[t.index(t_corr):])
            else:
                y_max = np.min(y[t.index(t_corr):])

            t_over = t[y.index(y_max)]
            do = y_max - yd
            do_percent = do / yd * 100
            self.create_time_line(self.axes, t, y, t_over, r'$T_o$')
            self.results.update({'to': t_over, 'do': do, 'doPercent': do_percent})
        else:
            self._logger.warning("failed to calculate overshoot and overshoot time 't_over'")
            self.results.update({'to': None, 'do': None, 'doPercent': None})

        # calc damping-time (Beruhigungszeit)
        try:
            #            eps = self.epsPercent*yd/100
            # TODO relocate settings
            # eps = st.R
            eps = .1
            enter_idx = -1
            for idx, val in enumerate(y):
                if enter_idx == -1:
                    if abs(val - yd) < eps:
                        enter_idx = idx
                else:
                    if abs(val - yd) >= eps:
                        enter_idx = -1
            teps = t[enter_idx]
            # create and add line
            self.create_time_line(self.axes, t, y, teps, r'$T_{\epsilon}$')
            self.results.update({'teps': teps})
        except IndexError:
            # print 'DampingLine is not defined'
            self.results.update({'teps': None})

        # create epsilon tube
        upper_bound = Line2D([0, t[-1]], [yd + eps, yd + eps], ls='--', c=self.line_color)
        self.axes.add_line(upper_bound)
        lower_bound = Line2D([0, t[-1]], [yd - eps, yd - eps], ls='--', c=self.line_color)
        self.axes.add_line(lower_bound)

        # calc control deviation
        control_deviation = y[-1] - yd
        self.results.update({'control_deviation': control_deviation})


class eval_A1_steps_in_one_plot(pm.PostProcessingModule):
    """
    create several step respond in one plot
    """

    line_color = '#aaaaaa'
    line_style = '-'
    font_size = 20
    epsPercent = 2. / 5
    spacing = 0.01
    counter = 0

    def __init__(self):
        pm.PostProcessingModule.__init__(self)
        return

    def process(self, files):

        print('processing ', self.name)

        # reset counter
        self.counter = 0

        # dict for calculated values
        #        output = {}
        yd = 0

        # create plot
        fig = Figure()
        axes = fig.add_subplot(111)
        axes.set_title(r'Sprungantworten')
        # search t max
        t_max = 0
        for data in files:
            t = data['modules']['solver']['end time']
            if t > t_max:
                t_max = t
        axes.set_xlim(left=0, right=t_max)
        axes.set_ylim(0, 4, 5)
        axes.set_xlabel(r'\textit{Zeit [s]}')
        axes.set_ylabel(r'\textit{Ballposition r(t) [m]}')

        controllerName = []
        # create plots
        counter = 0
        for data in files:
            #            print data['modules']
            #            print data['regime name']
            #            print data['results']['finished']
            # calculate data-sets
            t = data['results']['simTime']
            y = data['results']['model_output.0']
            yd = data['results']['trajectory_output.0'][-1]
            controllerName.append(data['modules']['controller']['type'])
            axes.plot(t, y, label=r'$r_{0} = ' + str(data['modules']['controller']['r0']) + '$',
                      c=mpl.rcParams['axes.color_cycle'][counter])
            counter += 1




            # check for sim success
        #            if not data['results']['finished']:
        #                for key in output.keys():
        #                    output[key] = None

        #        self.posLabel = np.arange(np.min(y) + 0.1*yd, yd, (yd-np.min(y))/4)

        # plot legend
        axes.legend()

        # create desired line
        desiredLine = Line2D([0, t[-1]], [yd, yd], lw=1, ls=self.line_style, c='k')
        axes.add_line(desiredLine)

        # create epsilon tube
        upperBoundLine = Line2D([0, t[-1]], [yd + st.R, yd + st.R], ls='--', c=self.line_color)
        axes.add_line(upperBoundLine)
        lowerBoundLine = Line2D([0, t[-1]], [yd - st.R, yd - st.R], ls='--', c=self.line_color)
        axes.add_line(lowerBoundLine)

        #        #calc control deviation
        #        control_deviation = y[-1] - yd
        #        output.update({'control_deviation': control_deviation})

        #        self.calcMetrics(data, output)


        # add settings and metrics to dictionary results
        results = {}
        #        results.update({'metrics': output})
        #        results.update({'modules': data['modules']})

        canvas = FigureCanvas(fig)

        self.writeOutputFiles(self.name, 'steps_in_one_plot', fig, results)

        return [{'name': '_'.join([controllerName[0], self.name]),
                 'figure': canvas}]

    def calcMetrics(self, data, output):
        '''
        calculate metrics for comaprism
        '''

        L1NormITAE = self.calcL1NormITAE(data)
        L1NormAbs = self.calcL1NormAbs(data)
        #                    
        #        print 'ITAE score: ', errorIntegral
        print('L1NormITAE: ', L1NormITAE)
        print('L1NormAbs: ', L1NormAbs)
        output.update({'L1NormITAE': L1NormITAE, 'L1NormAbs': L1NormAbs})


class EvalA2(pm.PostProcessingModule):
    """
    create diagrams like hauser did
    """
    line_color = '#aaaaaa'
    line_style = '-'

    name = 'A2'

    def __init__(self):
        pm.PostProcessingModule.__init__(self)
        return

    def run(self, data):
        print('processing ', data['regime name'])

        output = {}

        # calculate data-sets
        t = data['results']['simTime']
        yd = data['results']['trajectory_output.0']
        y = []
        for i in range(4):
            y.append(data['results']['model_output.' + str(i)])

        eps = np.subtract(y[0], yd)
        traj = data['results']['trajectory_output.0']

        # plots
        fig = Figure()
        fig.subplots_adjust(wspace=0.3, hspace=0.25)
        fig.suptitle(r'' + data['modules']['controller']['type'] + ' ' + \
                     '$A_d$ =' + str(data['modules']['trajectory']['Amplitude']) + ' ' + \
                     '$f_d$ =' + str(data['modules']['trajectory']['Frequency']),
                     size=st.title_size)

        axes1 = fig.add_subplot(2, 1, 1)
        # axes2.set_title(r'\textbf{Beam Angle}')
        axes1.plot(t, traj, c='k', ls='-', label='yd(t)')
        axes1.plot(t, y[0], c=st.color_cycle[data['modules']['controller']['type']],
                   ls='-', label='y(t)')
        axes1.set_xlim(left=0, right=t[-1])
        axes1.set_xlabel(r'$t [s]$', size=st.label_size)
        axes1.set_ylabel(r'$r [m]$', size=st.label_size)
        leg = [r'$y_d(t)$', r'$y(t)$']
        axes1.legend(leg, loc=0)

        axes2 = fig.add_subplot(2, 1, 2)
        #        axes.set_title(r'output error = yd - x0')        
        #        deltaE = 0.01
        #        eMax = line([0, t[-1]], [deltaE, deltaE], lw=1,\
        #                            ls='--', c=self.line_color)
        #        eMin = line([0, t[-1]], [-deltaE, -deltaE], lw=1,\
        #                            ls='--', c=self.line_color)        
        #        axes2.add_line(eMax)
        #        axes2.add_line(eMin)

        axes2.plot(t, eps, c='k')
        axes2.set_xlim(left=0, right=t[-1])
        #        axes2.set_ylim(top=0.4, bottom=-0.4)
        axes2.set_xlabel(r'$t [s]$', size=st.label_size)
        axes2.set_ylabel(r'$output error = x_{0} - y_{d} [m]$', size=st.label_size)

        self.calcMetrics(data, output)

        # check for sim succes
        if not data['results']['finished']:
            for key in list(output.keys()):
                output[key] = None

        # add settings and metrics to dictionary results
        results = {}
        results.update({'metrics': output})
        results.update({'modules': data['modules']})

        canvas = FigureCanvas(fig)

        self.writeOutputFiles(self.name, data['regime name'], fig, results)

        return {'name': '_'.join([data['regime name'], self.name]),
                'figure': canvas}

    def calcMetrics(self, data, output):
        '''
        calculate metrics for comaprism
        '''

        L1NormITAE = self.calcL1NormITAE(data)
        L1NormAbs = self.calcL1NormAbs(data)

        print('L1NormITAE: ', L1NormITAE)
        print('L1NormAbs: ', L1NormAbs)

        output.update({'L1NormITAE': L1NormITAE, 'L1NormAbs': L1NormAbs})


class eval_A2_epsilon(pm.PostProcessingModule):
    '''
    create diagrams like hauser did
    '''
    name = 'A2_epsilon'

    def __init__(self):
        pm.PostProcessingModule.__init__(self)
        return

    def run(self, data):
        print('processing ', data['regime name'])

        output = {}

        # calculate data-sets
        t = data['results']['simTime']
        yd = data['results']['trajectory_output.0']
        y = []
        for i in range(4):
            y.append(data['results']['model_output.' + str(i)])

        error = np.subtract(y[0], yd)
        output.update({'error': error})

        # plots
        fig = Figure()
        # fig.subplots_adjust(wspace=0.3, hspace=0.25)

        axes = fig.add_subplot(1, 1, 1)
        # axes.set_title(r'output error = yd - x0')
        axes.plot(t, error, c='k')
        axes.set_xlim(left=0, right=t[-1])
        axes.set_xlabel(r'$t [s]$')
        axes.set_ylabel(r'$output error = x_{0} - y_{d} [m]$')

        # calculate L1NormAbs
        L1NormAbs = self.calcL1NormAbs(data)
        output.update({'L1NormAbs': L1NormAbs})

        # check for sim succes
        if not data['results']['finished']:
            for key in list(output.keys()):
                output[key] = None

        # add settings and metrics to dictionary results
        results = {}
        results.update({'metrics': output})
        results.update({'modules': data['modules']})

        canvas = FigureCanvas(fig)

        self.writeOutputFiles(self.name, data['regime name'], fig, results)

        return {'name': '_'.join([data['regime name'], self.name]),
                'figure': canvas}


class eval_A2Hauser(pm.PostProcessingModule):
    '''
    create diagrams like hauser did
    '''

    name = 'A2_hauser'

    def __init__(self):
        pm.PostProcessingModule.__init__(self)
        return

    def run(self, data):
        results = {}
        output = {}
        print('processing ', data['regime name'])

        # calculate data-sets
        t = data['results']['simTime']
        yd = data['results']['trajectory_output.0']
        y = []
        for i in range(4):
            y.append(data['results']['model_output.' + str(i)])

        error = np.subtract(yd, y[0])

        # controlleroutput is a torque
        tau = data['results']['controller_output.0']
        # u in the neglected nonlinearity is theta_dd
        u = np.true_divide( \
            np.subtract( \
                np.subtract( \
                    tau, \
                    np.multiply( \
                        np.multiply( \
                            np.multiply( \
                                2 * st.M, \
                                y[0] \
                                ), \
                            y[1] \
                            ), \
                        y[3] \
                        ) \
                    ), \
                np.multiply( \
                    st.M * st.G, \
                    np.multiply( \
                        y[0], \
                        np.cos(y[2]) \
                        ) \
                    ) \
                ), \
            np.add(
                np.multiply( \
                    st.M, \
                    np.power(y[0], 2) \
                    ), \
                st.J + st.Jb \
                ) \
            )

        # Parameter from Controller -> modelling (estimate/meausre paramters)
        # and then neglect psi therm
        # if you are interested in the error through the negligence 
        if data['modules']['controller']['type'] == 'FController':
            psi = np.multiply(np.multiply(st.B, y[0]), np.power(y[3], 2))
        elif data['modules']['controller']['type'] == 'GController':
            psi = np.multiply(np.multiply(np.dot(2 * st.B, y[0]), y[3]), u)
        elif data['modules']['controller']['type'] == 'JController':
            psi = np.multiply(np.multiply(np.multiply(st.B, y[0]), np.power(y[3], 2)), \
                              np.multiply(st.B * st.G, np.subtract(y[2], np.sin(y[2]))))
        else:
            # psi is not defined in this case
            psi = np.dot(0, t)

        # plots
        fig = Figure()
        fig.subplots_adjust(wspace=0.3, hspace=0.25)

        axes1 = fig.add_subplot(2, 2, 1)
        # axes1.set_title(r'\textbf{output error = yd - x0}')
        axes1.plot(t, error, c='k')
        axes1.set_xlim(left=0, right=t[-1])
        axes1.set_xlabel(r'$t \,[s]$', size=st.label_size)
        axes1.set_ylabel(r'$e \,[m]$', size=st.label_size)

        axes2 = fig.add_subplot(2, 2, 2)
        # axes2.set_title(r'\textbf{Beam Angle}')
        axes2.plot(t, y[2], c='k')
        axes2.set_xlim(left=0, right=t[-1])
        axes2.set_xlabel(r'$t \, [s]$', size=st.label_size)
        axes2.set_ylabel(r'$\theta \, [rad]$', size=st.label_size)

        axes3 = fig.add_subplot(2, 2, 3)
        # axes3.set_title(r'\textbf{neglected nonlinearity}')
        axes3.plot(t, psi, c='k')
        axes3.set_xlim(left=0, right=t[-1])
        axes3.set_xlabel(r'$t [s]$', size=st.label_size)
        if data['modules']['controller']['type'] == 'FController':
            axes3.set_ylabel(r'$\psi_2 \, [\frac{m}{s^2}]$', size=st.label_size)
        if data['modules']['controller']['type'] == 'JController':
            axes3.set_ylabel(r'$\psi_2 \, [\frac{m}{s^2}]$', size=st.label_size)
        if data['modules']['controller']['type'] == 'GController':
            axes3.set_ylabel(r'$\psi_3 \, [\frac{m}{s^3}]$', size=st.label_size)

        axes4 = fig.add_subplot(2, 2, 4)
        # axes4.set_title(r'\textbf{Beam Torque}')
        axes4.plot(t, tau, c='k')
        axes4.set_xlim(left=0, right=t[-1])
        axes4.set_xlabel(r'$t \,[s]$', size=st.label_size)
        axes4.set_ylabel(r'$\tau \,[Nm]$', size=st.label_size)

        # calculate maximumError
        start = 30
        end = 40
        tStartIdx = next((idx for idx, x in enumerate(t) if x >= start), 0)
        tEndIdx = next((idx for idx, x in enumerate(t[start:]) if x >= end), len(t) - 1)

        maximumError = None
        if tStartIdx < tEndIdx:
            maximumError = max(error[tStartIdx:tEndIdx])

        print('maximum error between %d and %d seconds: %f' % \
              (start, end, maximumError))

        # collect results
        output.update({'maximumError': maximumError})

        # check for sim succes
        if not data['results']['finished']:
            for key in list(output.keys()):
                output[key] = None

        results.update({'metrics': output})
        results.update({'modules': data['modules']})

        # write results
        filePath = os.path.join(os.path.pardir, 'results', 'postprocessing', 'HauserDiagrams')
        if not os.path.isdir(filePath):
            os.makedirs(filePath)

        fileName = os.path.join(filePath, data['regime name'])
        with open(fileName + '.pof', 'w') as f:  # POF - Postprocessing Output File
            f.write(repr(results))

        canvas = FigureCanvas(fig)
        fig.savefig(fileName + '.svg')
        fig.savefig(fileName + '.png')
        fig.savefig(fileName + '.pdf')

        return {'name': '_'.join([data['regime name'], self.name]), \
                'figure': canvas}


class EvalA2HauserLikeHauser(pm.PostProcessingModule):
    """
    create diagrams like hauser did
    """

    name = 'A2_hauser'

    def __init__(self):
        pm.PostProcessingModule.__init__(self)
        return

    def process(self, files):
        print('process() of A2Hauser_LikeHauser called')
        results = {}
        output = {}
        l = []

        controllerDict = {'FController': [], \
                          'GController': [], \
                          'JController': []}
        for elem in controllerDict:
            controllerDict.update({elem: {'e': {}, 'theta': {}, 'psi': {}, 'tau': {}}})
            for var in controllerDict[elem]:
                for i in range(1, 4, 1):
                    controllerDict[elem][var].update({i: [[], []]})

        for res in files:

            # calculate data-sets
            t = res['results']['simTime']

            yd = res['results']['trajectory_output.0']
            y = []
            for i in range(4):
                y.append(res['results']['model_output.' + str(i)])

            error = np.subtract(yd, y[0])

            # controlleroutput is a torque
            tau = res['results']['controller_output.0']
            # u in the neglected nonlinearity is theta_dd
            u = np.true_divide( \
                np.subtract( \
                    np.subtract( \
                        tau, \
                        np.multiply( \
                            np.multiply( \
                                np.multiply( \
                                    2 * st.M, \
                                    y[0] \
                                    ), \
                                y[1] \
                                ), \
                            y[3] \
                            ) \
                        ), \
                    np.multiply( \
                        st.M * st.G, \
                        np.multiply( \
                            y[0], \
                            np.cos(y[2]) \
                            ) \
                        ) \
                    ), \
                np.add(
                    np.multiply( \
                        st.M, \
                        np.power(y[0], 2) \
                        ), \
                    st.J + st.Jb \
                    ) \
                )

            # Parameter from Controller -> modelling (estimate/meausre paramters)
            # and then neglect psi therm
            # if you are interested in the error through the negligence 
            if res['modules']['controller']['type'] == 'FController':
                psi = np.multiply(np.multiply(st.B, y[0]), np.power(y[3], 2))
            elif res['modules']['controller']['type'] == 'GController':
                psi = np.multiply(np.multiply(np.dot(2 * st.B, y[0]), y[3]), u)
            elif res['modules']['controller']['type'] == 'JController' or \
                            res['modules']['controller']['type'] == 'LSSController':
                psi = np.multiply(np.multiply(np.multiply(st.B, y[0]), np.power(y[3], 2)), \
                                  np.multiply(st.B * st.G, np.subtract(y[2], np.sin(y[2]))))
            else:
                # psi is not defined in this case
                psi = np.dot(0, t)

            # Dict füllen
            level1 = res['modules']['controller']['type']
            level3 = res['modules']['trajectory']['Amplitude']

            # Zeit anhängen
            #            controllerDict[level1].update({'t':t})
            controllerDict[level1]['e'][level3][0] = t
            controllerDict[level1]['theta'][level3][0] = t
            controllerDict[level1]['psi'][level3][0] = t
            controllerDict[level1]['tau'][level3][0] = t
            #            # Werte anhängen           
            controllerDict[level1]['e'][level3][1] = error
            controllerDict[level1]['theta'][level3][1] = y[2]
            controllerDict[level1]['psi'][level3][1] = psi
            controllerDict[level1]['tau'][level3][1] = tau


            # Plots erzeugen
        #        contr = ['FController', 'GController', 'JController', 'LSSController']
        contr = ['FController', 'GController', 'JController']
        for c in contr:
            print('controller:', c)

            fig = Figure()
            #            fig.subplots_adjust(wspace=0.3, hspace=0.25) 
            fig.subplots_adjust(wspace=0.6, hspace=0.6)
            fig.suptitle(r'\textbf{' + c + '}', size=st.title_size)

            for i in range(1, 4, 1):
                axes1 = fig.add_subplot(2, 2, 1)
                axes1.set_title(r'output error = yd - x0', size=st.label_size)
                axes1.plot(controllerDict[c]['e'][i][0], controllerDict[c]['e'][i][1])
                axes1.set_xlim(left=0, right=controllerDict[c]['e'][1][0][-1])
                axes1.set_xlabel(r'$t \,[s]$', size=st.label_size)
                axes1.set_ylabel(r'$e \,[m]$', size=st.label_size)
                axes1.grid(color='#ababab', linestyle='--')

                axes2 = fig.add_subplot(2, 2, 2)
                axes2.set_title(r'beam angle', size=st.label_size)
                axes2.plot(controllerDict[c]['theta'][i][0], controllerDict[c]['theta'][i][1])
                axes2.set_xlim(left=0, right=controllerDict[c]['theta'][1][0][-1])
                axes2.set_xlabel(r'$t \, [s]$', size=st.label_size)
                axes2.set_ylabel(r'$\theta \, [rad]$', size=st.label_size)
                axes2.grid(color='#ababab', linestyle='--')

                axes3 = fig.add_subplot(2, 2, 3)
                axes3.set_title(r'neglected nonlinearity', size=st.label_size)
                axes3.plot(controllerDict[c]['psi'][i][0], controllerDict[c]['psi'][i][1])
                axes3.set_xlim(left=0, right=controllerDict[c]['psi'][1][0][-1])
                axes3.set_xlabel(r'$t [s]$', size=st.label_size)
                if res['modules']['controller']['type'] == 'FController':
                    axes3.set_ylabel(r'$\psi_2 \, [\frac{m}{s^2}]$', size=st.label_size)
                if res['modules']['controller']['type'] == 'JController':
                    axes3.set_ylabel(r'$\psi_2 \, [\frac{m}{s^2}]$', size=st.label_size)
                    #                axes3.set_ylim(top = 0.6, bottom = -0.6)
                if res['modules']['controller']['type'] == 'GController':
                    axes3.set_ylabel(r'$\psi_3 \, [\frac{m}{s^3}]$', size=st.label_size)
                axes3.grid(color='#ababab', linestyle='--')

                axes4 = fig.add_subplot(2, 2, 4)
                axes4.set_title(r'beam torque', size=st.label_size)
                axes4.plot(controllerDict[c]['tau'][i][0], controllerDict[c]['tau'][i][1])
                axes4.set_xlim(left=0, right=controllerDict[c]['tau'][1][0][-1])
                axes4.set_xlabel(r'$t \,[s]$', size=st.label_size)
                axes4.set_ylabel(r'$\tau \,[Nm]$', size=st.label_size)
                axes4.grid(color='#ababab', linestyle='--')

                # calculate maximumError
                start = 30
                end = 40
                tStartIdx = next((idx for idx, x in enumerate(controllerDict[c]['e'][i][0]) if x >= start), 0)
                tEndIdx = next((idx for idx, x in enumerate(controllerDict[c]['e'][i][0][start:]) if x >= end), \
                               len(controllerDict[c]['e'][i][0]) - 1)

                maximumError = None
                if tStartIdx < tEndIdx:
                    maximumError = max(controllerDict[c]['e'][i][1][tStartIdx:tEndIdx])

                print('maximum error between %d and %d seconds: %f' % \
                      (start, end, maximumError))

            # check for sim succes
            if not res['results']['finished']:
                for key in list(output.keys()):
                    output[key] = None

            results.update({'metrics': output})
            results.update({'modules': res['modules']})

            # write results
            filePath = os.path.join(os.path.pardir, 'results', 'postprocessing', 'HauserDiagramsLikeHauser')
            if not os.path.isdir(filePath):
                os.makedirs(filePath)

            fileName = os.path.join(filePath, c)  # res['regime name'])
            with open(fileName + '.pof', 'w') as f:  # POF - Postprocessing Output File
                f.write(repr(results))

            canvas = FigureCanvas(fig)
            fig.savefig(fileName + '.svg')
            fig.savefig(fileName + '.png')
            fig.savefig(fileName + '.pdf')

            #            l.append({'name':'_'.join([res['regime name'], self.name]),\
            #                        'figure': canvas})
            l.append({'name': '_'.join([c, self.name]), \
                      'figure': canvas})

        return l


class EvalA3(pm.PostProcessingModule):
    """
    create diagrams for evaluation step A3
    """

    name = 'A3'

    line_color = '#aaaaaa'
    line_style = '-'
    font_size = 20
    epsPercent = 2.5
    spacing = 0.01
    counter = 0

    def __init__(self):
        pm.PostProcessingModule.__init__(self)
        return

    def run(self, data):
        print('processing ', data['regime name'])

        # dict for calculated values
        output = {}

        # reset counter
        self.counter = 0

        # calculate data-sets
        t = data['results']['simTime']
        y = data['results']['model_output.0']
        traj = data['results']['trajectory_output.0']
        yd = data['results']['trajectory_output.0'][-1]

        self.posLabel = np.arange(np.min(y) + 0.1 * yd, yd, (yd - np.min(y)) / 4)

        # create plot
        fig = Figure()
        axes = fig.add_subplot(111)
        axes.set_title(r'\textbf{Vergleich Signalverlaeufe (Systemantwort und Trajektorie)}')
        axes.plot(t, traj, c='b', ls='-', label='w(t)')
        # create t_desired line
        # search time value for t_desired
        t_desired = t[traj.index(yd)]
        self.createTimeLine(axes, t, traj, t_desired, r'$T_{des}$')
        # add real t_desired to dict output
        output.update({'t_desired': data['modules']['trajectory']['delta t']})
        # plot y(t)
        axes.plot(t, y, c='k', ls='-', label='y(t)')
        # axes scaling
        axes.set_xlim(left=0, right=t[-1])
        y_min = np.min(y)
        y_max = np.max(y)
        if (np.max(y) == 0):
            axes.set_ylim(np.min(traj), np.max(traj) + np.max(traj) * 0.1)
        else:
            axes.set_ylim(y_min, y_max + y_max * 0.1)
        axes.set_xlabel(r'\textit{Zeit [s]}')
        axes.set_ylabel(r'\textit{Ballposition r(t) [m]}')
        axes.legend(loc=4)

        # create desired line
        desiredLine = Line2D([0, t[-1]], [yd, yd], lw=1, ls=self.line_style, c='k')
        axes.add_line(desiredLine)

        # calc damping-time (Beruhigungszeit)
        eps = self.epsPercent * yd / 100
        enterIdx = -1
        for idx, val in enumerate(y):
            if enterIdx == -1:
                if abs(val - yd) < eps:
                    enterIdx = idx
            else:
                if abs(val - yd) >= eps:
                    enterIdx = -1
        if enterIdx == -1:
            # print 'DampingLine is not defined'
            output.update({'td': None})
        else:
            td = t[enterIdx]
            # create and add line
            self.createTimeLine(axes, t, y, td, r'$T_{\epsilon}$')
            output.update({'td': td})

        # create epsilon tube
        upperBoundLine = Line2D([0, t[-1]], [yd + eps, yd + eps], ls='--', c=self.line_color)
        axes.add_line(upperBoundLine)
        lowerBoundLine = Line2D([0, t[-1]], [yd - eps, yd - eps], ls='--', c=self.line_color)
        axes.add_line(lowerBoundLine)

        # calc control deviation
        control_deviation = y[-1] - yd
        output.update({'control_deviation': control_deviation})

        self.calcMetrics(data, output)

        # check for sim sucess
        if not data['results']['finished']:
            for key in output.keys():
                output[key] = None

        # add settings and metrics to dictionary results
        results = {}
        results.update({'metrics': output})
        results.update({'modules': data['modules']})

        canvas = FigureCanvas(fig)

        self.writeOutputFiles(self.name, data['regime name'], fig, results)

        return {'name': '_'.join([data['regime name'], self.name]), \
                'figure': canvas}

    def createTimeLine(self, axes, t, y, time_value, label):
        if time_value != t[-1]:
            # create timeLine
            timeLine = Line2D([time_value, time_value], \
                              [axes.get_ylim()[0], y[t.index(time_value)]], \
                              ls=self.line_style, \
                              c=self.line_color)
            axes.add_line(timeLine)
            # create label
            axes.text(time_value + self.spacing, self.posLabel[self.counter], label, size=self.font_size)
            self.counter = self.counter + 1

    def calcMetrics(self, data, output):
        '''
        calculate metrics for comaprism
        '''

        # calculate time difference
        if output['td'] == None:
            t_diff = None
        else:
            t_diff = output['td'] - data['modules']['trajectory']['delta t']

        # extract delta_t
        delta_t = data['modules']['trajectory']['delta t']

        L1NormITAE = self.calcL1NormITAE(data)
        L1NormAbs = self.calcL1NormAbs(data)

        print('L1NormITAE: ', L1NormITAE)
        print('L1NormAbs: ', L1NormAbs)

        output.update({'L1NormITAE': L1NormITAE, \
                       'L1NormAbs': L1NormAbs, \
                       'delta_t': delta_t, \
                       't_diff': t_diff, \
                       })


class EvalB(pm.PostProcessingModule):
    """
    create diagrams for evaluation step B
    """

    name = 'B'
    # padding = .2
    padding = .5
    offset = 0

    line_color = '#aaaaaa'
    line_style = '-'
    font_size = 20
    epsPercent = 2.5

    # spacing = 0.01
    # counter = 0

    def __init__(self):
        pm.PostProcessingModule.__init__(self)
        return

    def process(self, dataList):
        print('process() of B called')
        output = {}

        # ideal regime name
        regName = next((result['regime name'] \
                        for result in dataList if 'ideal' in result['regime name']), None)

        # extract the needed curves
        t = self.extractValues(dataList, 'ideal', 'simTime')
        y_ideal = self.extractValues(dataList, 'ideal', 'model_output.0')
        y_desired = self.extractValues(dataList, 'ideal', 'trajectory_output.0')
        yd = y_desired[-1]
        y_pTolMin = self.extractValues(dataList, 'paramTolMin', 'model_output.0')
        y_pTolMax = self.extractValues(dataList, 'paramTolMax', 'model_output.0')

        par = next((param for param in st.paramVariationListB if param in regName), None)
        print('assuming that', par, 'has been varied.')

        # sort files by variied parameter
        modDataList = sorted(dataList, key=lambda k: k['modules']['model'][par], reverse=False)

        # find minimal stable iteration
        resAbsMin = next((res \
                          for res in modDataList if res['results']['finished']), None)
        y_pAbsMin = resAbsMin['results']['model_output.0']

        # find maximum stable iteration
        resAbsMax = next((res \
                          for res in reversed(modDataList) if res['results']['finished']), None)
        y_pAbsMax = resAbsMax['results']['model_output.0']
        # print len(y_pAbsMin), len(y_pAbsMax), len(y_ideal)

        print('stablity limits are:', \
              resAbsMin['modules']['model'][par], '/', resAbsMax['modules']['model'][par])

        output.update({'parameter': par, \
                       'minLimit': resAbsMin['modules']['model'][par], \
                       'maxLimit': resAbsMax['modules']['model'][par], \
                       })

        # create plot
        fig = Figure()
        axes = fig.add_subplot(111)
        axes.set_title('Vergleich Signalverläufe')

        # create epsilon tub
        # eps = self.epsPercent*yd/100
        eps = st.R

        upperBoundLine = Line2D([0, t[-1]], [yd + eps, yd + eps], ls='--', c=self.line_color)
        axes.add_line(upperBoundLine)
        lowerBoundLine = Line2D([0, t[-1]], [yd - eps, yd - eps], ls='--', c=self.line_color)
        axes.add_line(lowerBoundLine)

        # create signals
        axes.add_line(lowerBoundLine)
        axes.plot(t, y_desired, c='b', ls='-', label='w(t)')
        axes.plot(t, y_ideal, c='limegreen', ls='-', label='exakter Wert')
        axes.plot(t, y_pTolMin, c='indianred', ls='-', label='untere Toleranzgrenze')
        axes.plot(t, y_pTolMax, c='darkorange', ls='-', label='obere Toleranzgrenze')
        # axes.plot(t, y_pAbsMin, c='orange', ls='-', label='untere Stabilitaetsgrenze')
        # axes.plot(t, y_pAbsMax, c='r', ls='-', label='obere Stabilitaetsgrenze')

        # customize
        axes.set_xlim(left=0, right=t[-1])
        #        axes.set_ylim(bottom=(self.offset+yd*(1-self.padding/2)),\
        #                top=(self.offset+yd*(1+self.padding)))

        axes.legend(loc=0, fontsize='small')
        axes.set_xlabel(r'$t \, \lbrack s \rbrack$')
        axes.set_ylabel(r'$r \, \lbrack m \rbrack$')

        canvas = FigureCanvas(fig)
        extendedName = os.path.join(self.name, par)

        # create output files because run is not called
        for data in dataList:
            results = {}
            results.update({'metrics': {}})
            self.calcMetrics(data, results['metrics'])

            # add settings and metrics to dictionary results
            results.update({'modules': data['modules']})

            self.writeOutputFiles(extendedName, data['regime name'], None, results)

        results = {'metrics': output}

        # create new dir for parameter
        self.writeOutputFiles(extendedName, 'paramLimits_' + regName[:-len('ideal')], \
                              fig, results)

        return [{'name': '_'.join([regName[:-len('ideal')], 'paramLimits', self.name]), \
                 'figure': canvas}]

    def calcMetrics(self, data, output):
        '''
        calculate metrics for comaprism
        '''
        # calc L1NormAbs
        L1NormAbs = self.calcL1NormAbs(data)

        # calc L1NormITAE
        L1NormITAE = self.calcL1NormITAE(data)
        output.update({ \
            'L1NormITAE': L1NormITAE, \
            'L1NormAbs': L1NormAbs, \
            })


class EvalC2(pm.PostProcessingModule):
    """
    create diagrams for evaluation step C - limitations
    """

    # padding = .2
    padding = .5
    offset = 0

    line_color = '#aaaaaa'
    line_style = '-'
    font_size = 20

    def __init__(self):
        pm.PostProcessingModule.__init__(self)
        return

    def process(self, dataList):
        print('process() of C2 called')

        output = []
        for cName in st.smoothPoles.keys():
            # check whether controller was in result files
            t = [None, None]
            t[0] = self.extractValues(dataList, [cName, '_unlimited'], 'simTime')
            t[1] = self.extractValues(dataList, [cName, '_limited'], 'simTime')
            if not (t[0] and t[1]):
                continue

            timeIdx = 0
            if len(t[1]) > len(t[0]):
                # limited controller lastet longer
                timeIdx = 1

            print('found entry of ', cName)

            # get curves
            r = [None, None]
            y = [None, None]
            ydes = [None, None]
            r[0] = self.extractValues(dataList, [cName, '_unlimited'], 'controller_output.0')
            r[1] = self.extractValues(dataList, [cName, '_limited'], 'controller_output.0')
            l = self.extractValues(dataList, [cName, '_limited'], 'limiter_output.0')
            ydes[0] = self.extractValues(dataList, [cName, '_unlimited'], 'trajectory_output.0')
            ydes[1] = self.extractValues(dataList, [cName, '_limited'], 'trajectory_output.0')
            ydEnd = ydes[timeIdx][-1]
            y[0] = self.extractValues(dataList, [cName, '_unlimited'], 'model_output.0')
            y[1] = self.extractValues(dataList, [cName, '_limited'], 'model_output.0')

            # get settings
            limits = self.extractSetting(dataList, [cName, '_limited'], 'limiter', 'limits')
            eps = st.R

            # create plot
            fig = Figure()
            fig.subplots_adjust(hspace=0.4)
            axes = []

            # fig1 controller output
            axes.append(fig.add_subplot(211))
            axes[0].set_title("Reglerausgänge im Vergleich")

            # create limitation tube
            upperBoundLine = Line2D([0, t[timeIdx][-1]], [limits[0]] * 2, ls='--', c=self.line_color)
            axes[0].add_line(upperBoundLine)
            lowerBoundLine = Line2D([0, t[timeIdx][-1]], [limits[1]] * 2, ls='--', c=self.line_color)
            axes[0].add_line(lowerBoundLine)

            axes[0].plot(t[0], r[0], c='limegreen', ls='-', label='r(t) unlimitriert')
            axes[0].plot(t[1], r[1], c='indianred', ls='-', label='r(t) limitiert')

            # customize
            axes[0].set_xlim(left=0, right=t[timeIdx][-1])
            #        axes.set_ylim(bottom=(self.offset+yd*(1-self.padding/2)),\
            #                top=(self.offset+yd*(1+self.padding)))

            axes[0].legend(loc=0, fontsize='small')
            axes[0].set_xlabel(r'$t \, \lbrack s \rbrack$')
            axes[0].set_ylabel(r'$\tau \, \lbrack Nm \rbrack$')

            # fig2 model output
            axes.append(fig.add_subplot(212))
            axes[1].set_title("Ausgangsverläufe im Vergleich")

            # create epsilon tube
            upperBoundLine = Line2D([0, t[timeIdx][-1]], [ydEnd + eps, ydEnd + eps], ls='--', c=self.line_color)
            axes[1].add_line(upperBoundLine)
            lowerBoundLine = Line2D([0, t[timeIdx][-1]], [ydEnd - eps, ydEnd - eps], ls='--', c=self.line_color)
            axes[1].add_line(lowerBoundLine)

            axes[1].plot(t[timeIdx], ydes[timeIdx], c='b', ls='-', label='w(t)')
            axes[1].plot(t[0], y[0], c='limegreen', ls='-', label='y(t) unlimitriert')
            axes[1].plot(t[1], y[1], c='indianred', ls='-', label='y(t) limitiert')

            # customize
            axes[1].set_xlim(left=0, right=t[timeIdx][-1])
            #        axes.set_ylim(bottom=(self.offset+yd*(1-self.padding/2)),\
            #                top=(self.offset+yd*(1+self.padding)))

            axes[1].legend(loc=0, fontsize='small')
            axes[1].set_xlabel(r'$t \, \lbrack s \rbrack$')
            axes[1].set_ylabel(r'$r \, \lbrack m \rbrack$')

            canvas = FigureCanvas(fig)

            # create output files because run is not called
            data_sets = [dataSet for dataSet in dataList if cName in dataSet['regime name']]
            for data in data_sets:
                results = {}
                results.update({'metrics': {}})
                self.calcMetrics(data, results['metrics'])

                # add settings and metrics to dictionary results
                results.update({'modules': data['modules']})
                if '_unlimited' in data['regime name']:
                    appendix = '_unlimited'
                else:
                    appendix = '_limited'
                self.writeOutputFiles(self.name, data['regime name'], fig, results)

            output.append({'name': '_'.join([cName, self.name]), \
                           'figure': canvas})
        return output

    def calcMetrics(self, data, output):
        '''
        calculate metrics for comaprism
        '''
        # calc L1NormAbs
        L1NormAbs = self.calcL1NormAbs(data)

        # calc L1NormITAE
        L1NormITAE = self.calcL1NormITAE(data)
        output.update({'L1NormITAE': L1NormITAE,
                       'L1NormAbs': L1NormAbs,
                       })


class EvalCObserver(pm.PostProcessingModule):
    """
    create diagrams like hauser did
    """
    line_color = '#aaaaaa'
    line_style = '-'

    name = 'C_observer'

    def __init__(self):
        pm.PostProcessingModule.__init__(self)
        return

    def run(self, data):
        print('processing ', data['regime name'])

        output = {}

        # vectorise skalar functions
        vSubt = np.vectorize(self.subt)

        # calculate data-sets
        t = data['results']['simTime']
        xm = []
        xo = []
        e = []
        for i in range(4):
            xm.append(data['results']['model_output.' + str(i)])
            xo.append(data['results']['observer_output.' + str(i)])
            e.append(vSubt(xo[i], xm[i]))

        # plots
        fig = Figure()
        fig.subplots_adjust(wspace=0.3, hspace=0.25)

        axes = []
        for i in range(4):
            axes.append(fig.add_subplot(5, 1, i + 1))
            axes[i].plot(t, xo[i], c='b', ls='-', label='xo[' + str(i) + ']')
            axes[i].plot(t, xm[i], c='k', ls='-', label='xm[' + str(i) + ']')
            axes[i].set_xlim(left=0, right=t[-1])

        axes.append(fig.add_subplot(5, 1, 5))
        leg = []
        for i in range(4):
            axes[4].plot(t, e[i], ls='-', label='e[' + str(i) + ']')
            leg.append('e[' + str(i) + ']')

        axes[4].legend(leg, loc=0, fontsize='small')

        # calculate results
        # L1 
        dt = 1.0 / data['modules']['solver']['measure rate']
        errorIntegrals = [0, 0, 0, 0]

        # check for sim success
        if not data['results']['finished']:
            for key in output.keys():
                output[key] = None

        for i in range(len(errorIntegrals)):
            for k, val in enumerate(xo[i]):
                # vgl. Betragskriterium L^1
                errorIntegrals[i] += 1
                errorIntegrals[i] += abs(val - xm[i][k]) * dt

            print('errorIntegral_x[' + str(i) + ']:', errorIntegrals[i])
            output.update({'error_L1Norm_x[' + str(i) + ']': errorIntegrals[i]})

        # add settings and metrics to dictionary results
        results = {}
        results.update({'metrics': output})
        results.update({'modules': data['modules']})

        canvas = FigureCanvas(fig)

        self.writeOutputFiles(self.name, data["regime name"], fig, results)

        return dict(name="_".join({data["regime name"], self.name}), figure=canvas)

pm.register_processing_module(pm.PostProcessingModule, EvalA1)
