============
Installation
============

General Options
---------------

At the command line::

    $ pip install pymoskito

Or, if you have virtualenvwrapper installed::

    $ mkvirtualenv pymoskito
    $ pip install pymoskito

From the repository::

    $ git clone https://github.com/cklb/pymoskito
    $ python setup.py install

For Windows
-----------

PyMoskito depends on Qt5 and VTK.
Qt5 is already included in the most python distributions, e.g. ::

    $ Winpyzthon

VTK can be obtained from::

    $ VTK Link


Troubleshooting
---------------
If importing ``vtk`` fails with::

    >>> Import Error: vtkIOAMRPython module not found

then look at the output of::

    $ ldd PATH/TO/SITE-PKGS/vtk/vtkIOAMRPython.so

to see which libs are missing.