__author__ = 'stefan'
from abc import ABCMeta, abstractmethod, abstractproperty
from collections import OrderedDict
from PyQt4.QtCore import QObject, pyqtWrapperType
"""
Base Classes for modules in the result-processing environment
"""

class ProcessingModuleMeta(ABCMeta, pyqtWrapperType):
    pass

class ProcessingModule(QObject):
    """
    Base Class for processing Modules.
    Each Module's run method is called with a list of results by the processing_gui
    """
    __metaclass__ = ProcessingModuleMeta
    _base_font_size = 14
    _label_font_size = 1 * _base_font_size
    _title_font_size = 1.5 * _base_font_size

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.name = self.__class__.__name__
        return

    def extract_setting(self, data_list, names, module_name, setting_name):
        """
        extracts settings from simulation data
        """
        return self.extract(data_list, ["modules", module_name, setting_name], names)

    def extract_values(self, data_list, names, value_name):
        """
        extracts values from simulation data
        """
        return self.extract(data_list, ["results", value_name], names)

    def extract(self, data_list, keys, names):
        """
        general extraction from simulation data
        where the regime name contains all strings
        listed in names
        """
        if not isinstance(names, list):
            names = [names]

        return next((self._get_sub_dict(result, keys) for result in data_list if
                     all(name in result['regime name'] for name in names)),
                    None)

    def _get_sub_dict(self, top_dict, keys):
        sub_dict = top_dict
        for key in keys:
            sub_dict = sub_dict[key]
        return sub_dict


class PostProcessingModule(ProcessingModule):
    """
    Base Class for Postprocessing Modules
    """

    def __init__(self):
        ProcessingModule.__init__(self)
        return

    def process(self, files):
        """
        worker-wrapper function that processes an array of result files
        This is an convenience wrapper for simple processor implementation.
        Overload for more sophisticated implementations
        """
        output = []
        for res in files:
            output.append(self.run(res))

        return output

    @abstractmethod
    def run(self, data):
        pass

    def calcL1NormITAE(self, data):
        '''
        this function calculate the L1 Norm  with a
        additional time weighting
        unit: m*s**2
        '''
        y = data['results']['model_output.0']
        yd = data['results']['trajectory_output.0']
        dt = 1.0 / data['modules']['solver']['measure rate']

        if not data['results']['finished']:
            L1NormITAE = None
        else:
            L1NormITAE = 0
            for idx, val in enumerate(y):
                # version 1
                L1NormITAE += abs(yd[idx] - val) * dt * (idx * dt)
                # version 2 see also wikipedia
                # L1NormITAE += abs(yd[idx] - val - (y[-1] - yd[-1]))*dt*(idx*dt)
        return L1NormITAE

    def calcL1NormAbs(self, data):
        '''
        this function calculate the L1 Norm
        (absolute criterium)
        unit: m*s
        '''
        y = data['results']['model_output.0']
        yd = data['results']['trajectory_output.0']
        dt = 1.0 / data['modules']['solver']['measure rate']

        if not data['results']['finished']:
            L1NormAbs = None
        else:
            L1NormAbs = 0
            for idx, val in enumerate(y):
                # version 1
                L1NormAbs += abs(yd[idx] - val) * dt
                # version 2 see also wikipedia
                # L1NormAbs += abs(yd[idx] - val - (y[-1] - yd[-1]))*dt
        return L1NormAbs

    def writeOutputFiles(self, processorName, regimeName, figure, output):
        '''
        this function save calculated values
        in a POF (postprocessing output file) File
        and create pdf, png, svg datafiles from the plots
        '''

        filePath = os.path.join(os.path.pardir, 'results', 'postprocessing', processorName)
        if not os.path.isdir(filePath):
            os.makedirs(filePath)

        if regimeName:
            fileName = os.path.join(filePath, regimeName)
            with open(fileName + '.pof', 'w') as f:  # POF - Postprocessing Output File
                f.write(repr(output))

        if figure:
            figure.savefig(fileName + '.png')
            figure.savefig(fileName + '.pgf')
            figure.savefig(fileName + '.pdf')
            figure.savefig(fileName + '.svg')


class MetaProcessingModule(ProcessingModule):
    """
    Base Class for Meta-Processing Modules
    """

    def __init__(self):
        ProcessingModule.__init__(self)
        return

    def sortLists(self, a, b):
        b = [x for (y, x) in sorted(zip(a, b))]
        a = sorted(a)
        return a, b

    def plotSettings(self, axes, titel, grid, xlabel, ylabel, typ='line'):
        axes.set_title(titel, size=st.title_size)
        if grid == True:
            axes.grid(color='#ababab', linestyle='--')
        axes.set_xlabel(xlabel, size=st.label_size)
        axes.set_ylabel(ylabel, size=st.label_size)
        if typ != 'bar':
            axes.legend(loc=0, fontsize='small', prop={'size': 8})

        return axes

    def plotVariousController(self, source, axes, xPath, yPath, typ, xIndex=-1, yIndex=-1):
        '''
        plots y over x for all controllers
        '''

        width = 0.2
        counter = 0
        x_all = []

        for controller in source:
            xList = get_sub_value(source[controller], xPath)
            yList = get_sub_value(source[controller], yPath)
            xList, yList = self.sortLists(xList, yList)

            if xIndex >= 0:
                xList[:] = [x[xIndex] for x in xList]
            if yIndex >= 0:
                yList[:] = [y[yIndex] for y in yList]

            # add x values to x_all if there are not in x_all
            for val in xList:
                if val not in x_all:
                    x_all.append(val)

            if typ == 'line':
                axes.plot(xList, \
                          yList, \
                          'o-', \
                          label=controller, \
                          color=st.color_cycle[controller])
            elif typ == 'bar':
                # remove all None from yList
                xList[:] = [x for x, y in zip(xList, yList) if y]
                yList[:] = [i for i in yList if i]

                # correction for the position of the bar
                xList[:] = [k + width * counter for k in xList]

                axes.bar(xList, \
                         yList, \
                         width, \
                         label=controller, \
                         color=st.color_cycle[controller])
                counter += 1

        if (typ == 'bar') and (len(x_all) > 1):
            # remove all None from x_all
            x_all.sort()
            x_all[:] = [i for i in x_all if i]

            # does not work for all constellations
            spacing = (x_all[-1] - x_all[0]) / (len(x_all) - 1)
            x_all.append(spacing + x_all[-1])
            x_all.append(x_all[0] - spacing)
            x_all.sort()

            x_all_label = [r'$' + str(i) + '$' for i in x_all]
            counter -= 1
            if typ == 'bar':
                x_all[:] = [i + width * counter for i in x_all]

            axes.set_xticks(x_all)
            axes.set_xticklabels(x_all_label)

        return axes

    def writeOutputFiles(self, name, figure):
        '''
        this function create pdf, png, svg datafiles from the plots
        '''
        filePath = os.path.join(os.path.pardir, \
                                'results', 'metaprocessing', self.name)
        if not os.path.isdir(filePath):
            os.makedirs(filePath)

        fileName = os.path.join(filePath, name)

        if figure:
            figure.savefig(fileName + '.png')
            # figure.savefig(fileName + '.pdf')
            # figure.savefig(fileName + '.svg')
