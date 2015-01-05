# -*- coding: utf-8 -*-
import os
import settings as st

import matplotlib as mpl
mpl.use("Qt4Agg")
#mpl.rcParams['text.usetex']=True
#mpl.rcParams['text.latex.unicode']=True
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from postprocessor import MetaProcessingModule

class eval_integralError_barPlot(MetaProcessingModule):
    '''
    create diagrams for evaluation of integralError
    '''

    def __init__(self):
        MetaProcessingModule.__init__(self)
        return

    def run(self, postResults):
        #aquire data      
        dic = {}
        for i in postResults:
            controller = i['modules']['controller']['type']
            integralError = i['integralError']
            delta_t = i['delta_t']
            if dic.has_key(controller):
                dic[controller]['delta_t'].append(delta_t)
                dic[controller]['integralError'].append(integralError)
            else:
                dic.update({controller: {'delta_t': [delta_t],\
                                        'integralError': [integralError]}})
        
        #create plot
        fig = Figure()
        axes = fig.add_subplot(111)
        axes.set_title(r'Fehlerintegral w(t) und y(t)', size=st.title_size)
        axes.grid(color='#ababab', linestyle='--')
        width = 0.1
        counter = 0
        t_all = []
        
        for i in dic:
            title = i
            t = dic[i]['delta_t']
            integralError = dic[i]['integralError']
            #add times to t_all
            for j in t:
                if t_all.count(j) == 0:
                    t_all.append(j)
                
            # replace None with 0
            for index, value in enumerate(integralError):
                if value == None:
                    integralError[index] = 0
            t[:] = [x + width*counter for x in t]  
            axes.bar(t, integralError, width, label=title, color=mpl.rcParams['axes.color_cycle'][counter])
            counter += 1

        t_all.sort()
        t_all_label = [str(x) for x in t_all]
        counter -= 1
        t_all[:] = [x + width*counter for x in t_all]
        axes.set_xticks(t_all)
        axes.set_xticklabels(t_all_label)
        axes.set_xlabel(r'$\Delta \, t\lbrack s\rbrack$', size=st.label_size)
        axes.set_ylabel(r'$E \, \lbrack m^{2}\rbrack$', size=st.label_size)
        axes.legend()
        
        #write results
        filePath = os.path.join(os.path.pardir, 'results', 'metaprocessing', 'A1')
        if not os.path.isdir(filePath):
            os.makedirs(filePath)
        
        fileName = os.path.join(filePath, 'ITEA-plot')
        canvas = FigureCanvas(fig)
        fig.savefig(fileName+'.svg')

        results = [{'figure': canvas, 'name': 'ITEA-plot'}]

        return results
