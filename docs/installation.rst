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

PyMoskito depends on Qt5 and VTK .

Qt5 is already included in the most python distributions, to have an easy start
we recommend to use Winpython_ .

The wheel for the *VTK* package (Version >= 7) can be obtained from
http://www.lfd.uci.edu/~gohlke/pythonlibs/#vtk .
It can be installed using the Winpython Control Panel or directly via::

    $ pip install VTK-VERSION_NAME_HERE.whl

from your winpython shell.

.. _Winpython: https://winpython.github.io/

Troubleshooting
---------------

**Missing vtk libraries (linux)**

If importing ``vtk`` fails with something similar to::

    >>> Import Error: vtkIOAMRPython module not found

then look at the output of::

    $ ldd PATH/TO/SITE-PKGS/vtk/vtkIOAMRPython.so

to see which libs are missing.