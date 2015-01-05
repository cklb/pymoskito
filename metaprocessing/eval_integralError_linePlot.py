# -*- coding: utf-8 -*-
import os
import settings as st

import matplotlib as mpl
mpl.use("Qt4Agg")
#mpl.rcParams['text.usetex']=True
#mpl.rcParams['text.latex.unicode']=True
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D as line

from postprocessor import MetaProcessingModule

class eval_integralError_linePlot(MetaProcessingModule):
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
            t_diff = i['t_diff']
            if dic.has_key(controller):
                dic[controller]['delta_t'].append(delta_t)
                dic[controller]['integralError'].append(integralError)
                dic[controller]['t_diff'].append(t_diff)
            else:
                dic.update({controller: {'delta_t': [delta_t],\
                                        'integralError': [integralError],\
                                        't_diff': [t_diff],\
                                        }})
        
        #create plot
        fig = Figure()
        #plot for integralError
        axes = fig.add_subplot(211)
        axes.set_title(r'Fehlerintegral w(t) und y(t)', size=st.title_size)
        axes.grid(color='#ababab', linestyle='--')
        #plot for time-difference
        axes1 = fig.add_subplot(212)
        axes1.set_title(r'\"Ubergangszeitfehler \"uber $\Delta t$', size=st.title_size)
        
        counter = 0
        t_all = []
        
        for i in dic:
            title = i
            delta_t = dic[i]['delta_t']
            t_diff = dic[i]['t_diff']
            integralError = dic[i]['integralError']
            
            #add times to t_all
            for j in delta_t:
                if t_all.count(j) == 0:
                    t_all.append(j)
                
            axes.plot(delta_t, integralError, 'o-', label=title, color=mpl.rcParams['axes.color_cycle'][counter])
            axes1.plot(delta_t, t_diff, 'o-', label=title, color=mpl.rcParams['axes.color_cycle'][counter])
            counter += 1            
        
        
        t_all.sort()
        # does not work for all constellations
        spacing = (t_all[-1] - t_all[0])/(len(t_all) - 1)
        t_all.append(spacing + t_all[-1])
        t_all.append(t_all[0] - spacing)
        t_all.sort()

        t_all_label = [r'$' + str(x) + '$' for x in t_all]
        axes.set_xticks(t_all)
        axes.set_xticklabels(t_all_label)
        axes.legend(loc=0)
        axes.set_xlabel(r'$\Delta t \, \lbrack s\rbrack$', size=st.label_size)
        axes.set_ylabel(r'$E \, \lbrack m^{2}\rbrack$', size=st.label_size)
        
        axes1.set_xticks(t_all)
        axes1.set_xticklabels(t_all_label)
        axes1.legend(loc=0)
        axes1.set_xlabel(r'$\Delta t \, \lbrack s\rbrack$', size=st.label_size)
        axes1.set_ylabel(r'$e_{t} \, \lbrack m^{2}\rbrack$', size=st.label_size)
        
                
        
        #write results
        filePath = os.path.join(os.path.pardir, 'results', 'metaprocessing', 'A1')
        if not os.path.isdir(filePath):
            os.makedirs(filePath)
        
        fileName = os.path.join(filePath, 'ITEA-plot')
        canvas = FigureCanvas(fig)
        fig.savefig(fileName+'.svg')

        results = [{'figure': canvas, 'name': 'ITEA-plot'}]

        return results
