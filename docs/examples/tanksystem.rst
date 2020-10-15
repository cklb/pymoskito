============
2-Tanksystem
============

Two tanks are connected in series, where tank 1 is filled with a water inflow controled by
pump.

.. tikz::
    :include: ../tikz/tanksystem.tex

    The 2-Tanksystem


For the first tank:

.. math::

    A_1 \dot{h}_1(t) & = q_{\mathrm{in}} - q_1

assuming the linear resistance to flow

.. math::

    q_1 & = \frac{h_1 - h_2}{R_1}


For the second tank:

.. math::

    A_2 \dot{h}_2(t) & = q_1 - q_0

assuming the linear resistance to flow

.. math::

    q_0 & = \frac{h_2}{R_2}



The parameters of the system are collected in table :numref:``

.. list-table::
    :widths: 33 33 33
    :header-rows: 1

    * - Parameter
      - Value
      - Unit
    * - :math:`A_1`
      - :math:`\num{0.025}`
      - :math:`\si{\square\meter}`
    * - :math:`A_2`
      - :math:`\num{0.025}`
      - :math:`\si{\square\meter}`
    * - :math:`R_1`
      - :math:`\num{0.025}`
      - :math:`\si{\meter\per\second}`
    * - :math:`R_1`
      - :math:`\num{0.025}`
      - :math:`\si{\meter\per\second}`
    * - :math:`H_1`
      - :math:`\num{0.025}`
      - :math:`\si{\meter}`
    * - :math:`H_2`
      - :math:`\num{0.025}`
      - :math:`\si{\meter}`

