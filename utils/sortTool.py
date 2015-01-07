# -*- coding: utf-8 -*-

data = [{'metrics': {'to': 2.416999999999845,\
         'ys': 0.06267154539884068,\
         'ITAE': 15.02186129335023,\
         'do': 0.30959165610216033,\
        'td': 20.00000000000146,\
        'doPercent': 10.319721870072012,\
        'tr': 1.45999999999995,\
        'tanr': 1.6819999999999256},\
         'modules': {'feedforward': {},\
                     'controller': {'tick divider': 1.0, 'poles': [-3.6000000000000014, -3.6000000000000014, -3.6000000000000014, -3.6000000000000014], 'type': 'FController'},\
                     'disturbance': {},\
                     'observer': {},\
                     'solver': {'end time': 20.0, 'rTol': 1e-06, 'step size': 0.001, 'initial state': [0.0, 0.0, 0.0, 0.0], 'aTol': 1e-09, 'measure rate': 1000.0, 'type': 'VODESolver', 'Method': 'adams'},\
                     'trajectory': {'Position': 3.0, 'type': 'FixedPointTrajectory'},\
                     'model': {'R': 0.01, 'beam length': 9.0, 'G': 9.81, 'beam width': 0.01, 'beam depth': 0.03, 'M': 0.05, 'J': 0.02, 'type': 'BallBeamModel', 'Jb': 2e-06},\
                     'limiter': {},\
                     'sensor': {}}},\
        {'metrics':{'to': 2.416999999999845,\
         'ys': 0.06267154539884068,\
         'ITAE': 15.02186129335023,\
         'do': 0.30959165610216033,\
        'td': 20.00000000000146,\
        'doPercent': 10.319721870072012,\
        'tr': 1.45999999999995,\
        'tanr': 1.6819999999999256},\
         'modules': {'feedforward': {},\
                     'controller': {'tick divider': 1.0, 'poles': [-3.6000000000000014, -3.6000000000000014, -3.6000000000000014, -3.6000000000000014], 'type': 'FController'},\
                     'disturbance': {},\
                     'observer': {},\
                     'solver': {'end time': 20.0, 'rTol': 1e-06, 'step size': 0.001, 'initial state': [0.0, 0.0, 0.0, 0.0], 'aTol': 1e-09, 'measure rate': 1000.0, 'type': 'VODESolver', 'Method': 'adams'},\
                     'trajectory': {'Position': 3.0, 'type': 'FixedPointTrajectory'},\
                     'model': {'R': 0.01, 'beam length': 9.0, 'G': 9.81, 'beam width': 0.01, 'beam depth': 0.03, 'M': 0.05, 'J': 0.02, 'type': 'BallBeamModel', 'Jb': 2e-06},\
                     'limiter': {},\
                     'sensor': {}}}]

def createDictionary(data):
    dic = {}
    for elem in data:
        controllerName = elem['modules']['controller']['type']
        
        if dic.has_key(controllerName):
            print 'controller vorhanden'
#                dic[controllerName]['delay'].append('bla')
        else:
            for key, value in elem.items():
                
#                print 'sub: ',_getSubElement(value, [value.keys()])
                print key
                print value
                dic.update({controllerName:{\
                                    }})        
                                    
                                    
    print '\n .........................................................\n'
    print 'dic: ', dic
    return dic     
      
def _getSubElement(topDict, keys):
    subDict = topDict
    for key in keys:
        if subDict.has_key(key):
            subDict = subDict[key]
        else:
            return None
    return subDict

createDictionary(data)



