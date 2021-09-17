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

**Missing dependencies (windows)**

If the provided packages on your system are to old, pip may feel obligated to
update them. Since the majority of packages now provide ready to use wheels
for windows on pypi_ this should work automatically.
If for some reason this process fails, you will most certainly find an
appropriate wheel here_ . After downloading just navigate your shell into the
directory and call::

    $ pip install PACKAGE_NAME.whl

to install it.

.. _pypi: https://pypi.python.org/pypi
.. _here: https://www.lfd.uci.edu/~gohlke/pythonlibs/

**Missing vtk libraries (linux)**

If importing ``vtk`` fails with something similar to::

    >>> Import Error: vtkIOAMRPython module not found

then look at the output of::

    $ ldd PATH/TO/SITE-PKGS/vtk/vtkIOAMRPython.so

to see which libs are missing.

**GUI looks blurry on high-dpi displays**

You may add the line::

    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

before you import pymoskito to enable autoscaling in Qt.
