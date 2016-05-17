============
Installation
============

At the command line::

    $ pip install pymoskito

Or, if you have virtualenvwrapper installed::

    $ mkvirtualenv pymoskito
    $ pip install pymoskito

From the repository::

    $ git clone https://github.com/cklb/pymoskito
    $ python setup.py install


Troubleshooting
---------------
If importing ``vtk`` fails with::

    >>> Import Error: vtkIOAMRPython module not found

then look at the output of::

    $ ldd PATH/TO/SITE-PKGS/vtk/vtkIOAMRPython.so

to see which libs are missing.