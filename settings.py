# -*- coding: utf-8 -*-

#---------------------------------------------------------------------
# global default settings for physical simulation
#--------------------------------------------------------------------- 

# standard values for integration
step_size = 0.001          # stepwidth
initial_state = [0.5, 0, 0, 0] # initial minimal state vector (r, dr, theta, dtheta) default values (used if none is given)
int_mode = 'vode'
int_method='adams'
int_rtol=1e-6
int_atol=1e-9
sim_time = 20

# standard system values
M = 0.05    # kg
R = 0.01    # m
J = 0.02    # kgm^2
Jb = 2e-6   # kgm^2
G = 9.81    # m/s^2
B = M/(Jb/R**2+M)

# operating point
q_op = [0, 0, 0, 0]
tau_op = 0

# poles for LSSController
poles_LSSController = [-2, -2, -2, -2]

# poles for LuenbergerObserver
poles_LuenbergerObserver = [-3, -3, -3, -3]

# Visualization
beam_width = 0.07   # m
beam_depth = 0.2   # m
beam_length = 9     # m
scale = 1
ballScale = 20

#-----------------------------------------------
#export settings latex-style
#-----------------------------------------------
latex_font_size = 14
label_size = 1*latex_font_size
title_size = 1.5*latex_font_size

#-----------------------------------------------
# color-settings for diagramms with more than
# one controller
#-----------------------------------------------
color_cycle = { 'FController': 'royalblue',\
                'GController': 'indianred',\
                'JController': 'mediumorchid',\
                'LSSController': 'limegreen',\
                'PIFeedbackController': 'darkorange',\
        }

#-----------------------------------------------
# TestCase A - Step and other Responses
#-----------------------------------------------
#best konwon poles - gained in A1
poles = {'FController': -3.6,\
        'GController': -3,\
        'JController': -2,\
        'LSSController': -3.3,\
        'PIFeedbackController': -1.5,\
        }

#-----------------------------------------------
# TestCase B - Paramter Variation
#-----------------------------------------------
#parameter variation list
paramVariationListB = ['M', 'Jb']
paramToleranceList = [0.2, 0.1]

#parameter stability limits for best known poles
paramStabilityLimits = {\
        'FController': {\
            'M': [0.01, 0.5],\
            'Jb': [0, 3e-6],\
            },\
        'GController': {\
            'M': [0, 1],\
            'Jb': [0, 3e-6],\
            },\
        'JController': {\
            'M': [0, 1],\
            'Jb': [0, 3e-6],\
            },\
        'LSSController': {\
            'M': [0, 1],\
            'Jb': [0, 3e-6],\
            },\
        'PIFeedbackController': {\
            'M': [0, 1],\
            'Jb': [0, 3e-6],\
            },\
        }

#-----------------------------------------------
# TestCase C1 - Paramter Variation
#-----------------------------------------------
paramVariationListC1 = ['sigma', 'delay']
                                 #lower_bound = 0 is not possible
paramVariationDictC1 = {'sigma': {'lower_bound': 0.01,\
                                 'upper_bound': 0.4,\
                                 'step_size': 0.05},\
                       'delay': {'lower_bound': 0,\
                                 'upper_bound': 3,\
                                 'step_size': 0.5,\
                                 }}

#-----------------------------------------------
# TestCase C2 - Limiter Variation
#-----------------------------------------------
paramVariationListC2 = ['limiter']
# lower_bound is equal to M*G*3
paramVariationDictC2 = {'limiter': {'lower_bound': 1.5,\
                                 'upper_bound': 3,\
                                 'step_size': 0.1,\
                                 }}








