# -*- coding: utf-8 -*-
from tools import getSubValue

# mpl.rcParams['text.usetex']=True
# mpl.rcParams['text.latex.unicode']=True
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from processing_gui import MetaProcessingModule
from tools import sortTree
from tools import getSubValue


class eval_L1NormITAE_poles_linePlot(MetaProcessingModule):
    """
    create diagrams, which plot L1NormITAE over poles
    """

    def __init__(self):
        MetaProcessingModule.__init__(self)
        return

    def run(self, post_results):
        # create tree with all relevant data
        source = sortTree(post_results, ['modules', 'controller', 'type'])

        # Get the Poles for the Minimum 
        for controller in source:
            x_path = ['modules', 'controller', 'poles']
            y_path = ['metrics', 'L1NormITAE']
            x_list = getSubValue(source[controller], x_path)
            y_list = getSubValue(source[controller], y_path)

            x_list[:] = [x for x, y in zip(x_list, y_list) if y]
            y_list[:] = [i for i in y_list if i]

            self._logger.info("processing controller '{}'".format(controller))
            self._logger.info("min ITAE {}".format(min(y_list)))
            self._logger.info("opt poles {}".format(x_list[y_list.index(min(y_list))][0]))

        # create plot
        fig = Figure()
        #        fig.subplots_adjust(wspace=20, hspace=10, h_pad=50)
        fig.subplots_adjust(wspace=0.6, hspace=0.6)

        # plot for L1NormITAE over poles
        axes = fig.add_subplot(111)
        self.plotVariousController(source, axes,
                                   xPath=['modules', 'controller', 'poles'],
                                   yPath=['metrics', 'L1NormITAE'],
                                   typ='line',
                                   xIndex=0)
        self.plotSettings(axes,
                          titel=r'Fehlerintegral ITAE \"uber Polplatzierung',
                          grid=True,
                          xlabel=r'$Poles \, \lbrack s\rbrack$',
                          ylabel=r'$E \, \lbrack ms^{2} \rbrack$',
                          )

        # error minimum
        for controllerName in source.keys():
            error_list = getSubValue(source[controllerName], ['metrics', 'L1NormITAE'])
            error_min = min(x for x in error_list if x is not None)
            error_min_index = error_list.index(error_min)
            poles = getSubValue(source[controllerName], ['modules', 'controller', 'poles'])[error_min_index][0]
            self._logger.info("minimum error of {} for {} with poles at {}".format(error_min, controllerName, poles))

        # extract controllerNames
        controller_names = [x[:-len('Controller')] for x in source.keys()]

        canvas = FigureCanvas(fig)
        # write output files
        file_name = self.name[len('eval_'):] \
                    + '_Controller_(' + ''.join(controller_names) + ')'
        self.writeOutputFiles(file_name, fig)

        return [{'figure': canvas, 'name': self.name}]
