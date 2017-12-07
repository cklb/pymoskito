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
    
    x_1 &= \frac {A_{Sp}}{k_V}\sqrt{\frac{m}{k_L}(\ddot{y} + g)} + \frac{A_B}{k_V} \dot{y}
    \\  &= f_1 (y, \dot{y}, \ddot{y})

    x_2 &= \frac {m A_{Sp}^2 y^{(3)}}{2 k_V k_L (k_V x_1 - A_B \dot{y})} + \frac{A_B}{k_V} \ddot{y}
    \\  &= f_2 (y, \dot{y}, \ddot{y}, y^{(3)})
    
    u   &= \frac {m T^2 A_{Sp}^2 y^{(4)} - 2 k_L T^2 (k_V x_2 - A_B \ddot{y})^2}{2 k_s k_V k_L (k_V x_1 - A_B \dot{y})}
    + \frac {A_B T^2}{k_s k_V} y^{(3)} + \frac {2 d T}{k_s} x_2 + \frac{1}{k_s} x_1
    \\  &= f_u (y, \dot{y}, \ddot{y}, y^{(3)}, y^{(4)})
    
The last equation :math:`u= f_u (y, \dot{y}, \ddot{y}, y^{(3)}, y^{(4)})` is implented in this feedforward module.
The highest order of derivatives is :math:`y^{(4)}`, so the trajectory generator 
needs to provide a trajectory that is differentiable at least four times.