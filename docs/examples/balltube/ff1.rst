=========================
Ball in Tube Feedforward
=========================

Analyzing the system for flatness leads to finding the ball's position as the flat output of the system,
meaning that all other system variables can be calculated from it.
This can be retraced easily with the following chain of equations:

.. math::
    
    x_3 &= y
    \\  &= f_3 (y)
    
    x_4 &= \dot{y} 
    \\  &= f_4 (\dot{y})
    
    x_1 &= \frac {A_{\textup{Sp}}}{k_{\textup{V}}}\sqrt{\frac{m}{k_{\textup{L}}}(\ddot{y} + g)} + \frac{A_{\textup{B}}}{k_{\textup{V}}} \dot{y}
    \\  &= f_1 (y, \dot{y}, \ddot{y})

    x_2 &= \frac {m A_{\textup{Sp}}^2 y^{(3)}}{2 k_{\textup{V}} k_{\textup{L}} (k_{\textup{V}} x_1 - A_{\textup{B}} \dot{y})} + \frac{A_{\textup{B}}}{k_{\textup{V}}} \ddot{y}
    \\  &= f_2 (y, \dot{y}, \ddot{y}, y^{(3)})
    
    u   &= \frac {m T^2 A_{\textup{Sp}}^2 y^{(4)} - 2 k_{\textup{L}} T^2 (k_{\textup{V}} x_2 - A_{\textup{B}} \ddot{y})^2}{2 k_{\textup{s}} k_{\textup{V}} k_{\textup{L}} (k_{\textup{V}} x_1 - A_{\textup{B}} \dot{y})}
    + \frac {A_{\textup{B}} T^2}{k_{\textup{s}} k_{\textup{V}}} y^{(3)} + \frac {2 d T}{k_{\textup{s}}} x_2 + \frac{1}{k_{\textup{s}}} x_1
    \\  &= f_u (y, \dot{y}, \ddot{y}, y^{(3)}, y^{(4)})
    
The last equation :math:`u= f_u (y, \dot{y}, \ddot{y}, y^{(3)}, y^{(4)})` is implented in this feedforward module.
The highest order of derivatives is :math:`y^{(4)}`, so the trajectory generator 
needs to provide a trajectory that is differentiable at least four times.