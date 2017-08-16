.. :changelog:

History
-------

0.1.0 (2015-01-11)
------------------

* First release on PyPI.

0.2.0 (2017-08-18)
------------------

* Second minor release with lots of new features.
* Completely overhauled graphical user interface with menus and shortcuts.
* PyMoskito now comes with three full-fledged examples from the world of
  control theory, featuring the Ball and Beam- and a Tandem-Pendulum system.
* The main application now has a logger window which makes it easier to see what
  is going on in the simulation circuit.
* Several bugs concerning encoding issues have been fixed
* Unittest have been added and the development now uses travis-ci
* Version change from PyQt4 to Pyt5
* Version change form Python 2.7 to 3.5+
* Changed version to GPLv3 and added appropriate references for the used images.
* Improved the export of simulation results
* Introduced persistent settings that make opening files less painful.
* Made vtk an optional dependency and added matplotlib based visualizers.
* Large improvements concerning the sphinx-build documentation
* Fixed issue concerning possible data types for simulation module properties
* Introduced new generic modules that directly work on scipy StateSpace objects.