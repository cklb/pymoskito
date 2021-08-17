.. :changelog:

=======
History
=======


0.4.0 (2021-08-XX)
------------------

* Added support to compile and call external C and C++ functions
  for hardware in the loop tests (Thanks to Jens)
* Add the possibility for the visualization the render the current model
  parameters (#56)
* Various improvements regarding plot creation and handling
* Visualizers can now be changed during runtime
* Migrated CI pipeline to Github Actions
* Fix various coding style issues
* Fix issue in playback logic (#62)
* Dropped support for Python 3.6

0.3.0 (2018-10-01)
------------------

* Added a new plot system
* Added a last simulation list
* Added more log messages 
* Removed latex as an requirement for the main GUI, only required for the Postprocessor

0.2.3 (2018-05-14)
------------------

* Added sensible examples for Post- and Meta processors in the Ball and Beam
  example
* Fixed Issue regarding the Disturbance Block
* Removed error-prone pseudo post processing
* Fixed problems due to changes in trajectory generators

0.2.2 (2018-03-28)
------------------

* Added extensive beginners guide (thanks to Jonas) and tutorial section
* Added extended documentation for examples (again, thanks to Jonas)

0.2.1 (2017-09-07)
------------------

* Fixed issue when installing via pip
* Fixed issue with metaprocessors and added example metaprocessor for ballbeam
* Downgraded requirements

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

0.1.0 (2015-01-11)
------------------

* First release on PyPI.

