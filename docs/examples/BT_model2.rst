=========================
Ball in Tube Spring Model
=========================

This model contains all equations of the :doc:`Ball in Tube Model <BT_model1>`
except for one single change:
The dynamics of the ball bouncing back up once it falls to the ground.

Instead of overriding the ball's position and speed once the ball falls below the fan,
the fourth system equation is overwritten by an extended version.
This inserts a spring with the stiffness :math:`K` and the damping :math:`D` at the ground of the tube:

.. math::
    
    \dot{x}_4 = \frac{K x_3}{m} - \frac{D x_4}{m} + \frac{k_L}{m}\left(\frac{k_V x_1 - A_B x_4}{A_{Sp}}\right)^2-g
    




