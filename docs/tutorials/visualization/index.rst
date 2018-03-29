Visualization
=============

This tutorial covers the subject of how to visualize your system using pymoskito.

To do this, you can provide a :py:class:`pm.Visualizer` to the toolbox which
will then be used to show the system. To accomplish this, pymoskito uses the
VisualizationToolkit (vtk_) for natty 3d plots. However, if vtk_ is not available
a fallback method using the matplotlib_ is also supported.

Before we start visualizing, we need to choose a system. For sake of simplicity,
the simple_example system from the :doc:`introduction <../getting_started/system>`
will be used. Visualizers for both toolkits will be explained in the following
sections.

.. toctree::
    :maxdepth: 2

    visualizer_mpl
    visualizer_vtk



.. _vtk: https://www.vtk.org/
.. _matplotlib: https://www.matplotlib.org/
