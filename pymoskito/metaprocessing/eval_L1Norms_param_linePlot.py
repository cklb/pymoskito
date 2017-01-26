# -*- coding: utf-8 -*-
import matplotlib as mpl

mpl.rcParams['text.usetex'] = True
mpl.rcParams['text.latex.unicode'] = True
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from processing_gui import MetaProcessingModule
import settings as st
from tools import sort_tree


class eval_L1Norms_param_linePlot(MetaProcessingModule):
    """
    create diagrams for evaluation of integralError
    """
    name = 'eval_L1_over_param'

    def __init__(self):
        MetaProcessingModule.__init__(self)
        return

    def run(self, post_results):
        # create tree with relevant data
        source = sort_tree(post_results, ['modules', 'controller', 'type'])

        # get ideal regime name
        file_name = post_results[0]['name']

        # extract parameter that has been varied
        param = next((param for param in st.paramVariationListB \
                      if '_' + param + '(' in file_name), \
                     None)
        self._logger.info("assuming that {} has been varied".format(param))

        # create plot
        figs = [Figure(), Figure()]

        # plot for L1NormAbs
        axes = [figs[0].add_subplot(111), figs[1].add_subplot(111)]

        self.plotVariousController(source, axes[0],
                                   xPath=['modules', 'model', param],
                                   yPath=['metrics', 'L1NormAbs'],
                                   typ='line')

        if param == 'M':
            xlbl = r'$M \, \lbrack kg\rbrack$'
        elif param == 'J':
            xlbl = r'$M \, \lbrack kg\rbrack$'
        else:
            xlbl = ''

        self.plotSettings(axes[0],
                          titel='Fehlerintegral',
                          grid=True,
                          xlabel=xlbl,
                          ylabel=r'$E \, \lbrack ms\rbrack$')
        self.plotVariousController(source, axes[1],
                                   xPath=['modules', 'model', param],
                                   yPath=['metrics', 'L1NormITAE'],
                                   typ='line')
        self.plotSettings(axes[1],
                          titel='ITAE Fehler',
                          grid=True,
                          xlabel=xlbl,
                          ylabel=r'$E \, \lbrack ms^2\rbrack$')

        # extract controller names
        controller_names = [x[:-len('Controller')] for x in source.keys()]

        canvas = [FigureCanvas(figs[0]), FigureCanvas(figs[1])]

        # write output files
        file_name = self.name[len('eval_'):] \
                    + '_Controller_(' + ''.join(controller_names) + ')'

        names = ['_'.join([file_name, param, 'Abs']), '_'.join([file_name, param, 'ITAE'])]

        self.writeOutputFiles(names[0], figs[0])
        self.writeOutputFiles(names[1], figs[1])

        return [
            {'figure': canvas[0], 'name': names[0]},
            {'figure': canvas[1], 'name': names[1]},
        ]
