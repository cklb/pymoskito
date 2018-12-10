import logging
import os
import subprocess

from PyQt5.QtCore import QObject

__all__ = ["CppBinding"]


class BindingException(Exception):
    """
    Exception to be raised if the cpp binding raises.
    """
    pass


class CppBinding(QObject):
    def __init__(self, module_name=None, module_path=None):
        QObject.__init__(self, None)

        self._logger = logging.getLogger(self.__class__.__name__)

        if module_name is None:
            raise BindingException("Instanciation of binding class without module_name is not allowed!")
        else:
            self.module_name = module_name

        if module_path is None:
            raise BindingException("Instanciation of binding class without module_path is not allowed!")
        else:
            self.module_path = module_name

        self.create_binding_config()
        self.build_binding()

    def create_binding_config(self):
        self.src_path = os.path.join(os.path.dirname(self.module_path), "binding")
        self.module_inc_path = os.path.join(self.src_path, self.module_name + ".h")
        self.module_src_path = os.path.join(self.src_path, self.module_name + ".cpp")

        self.pybind_path = os.path.join(os.path.dirname(__file__),
                                        "libs",
                                        "pybind11")
        self.cmake_lists_path = os.path.join(self.src_path, 'CMakeLists.txt')

        # check if folder exists
        if not os.path.isdir(self.src_path):
            self._logger.error("Dir binding not available in project folder '{}'"
                              "".format(os.getcwd()))
            return

        if not os.path.exists(self.module_inc_path):
            self._logger.error("Module '{}'.h could not found in binding folder"
                              "".format(self.module_inc_path))
            return

        if not os.path.exists(self.module_inc_path):
            self._logger.error("Module '{}'.h could not found in binding folder"
                              "".format(self.module_src_path))
            return

        if not os.path.exists(self.cmake_lists_path):
            self._logger.warning("No CMakeLists.txt found!")
            self._logger.info("Generating new CMake config.")
            self.create_cmake_lists()

        self.add_binding_config()

        # generate config
        if os.name == 'nt':
            result = subprocess.run(['cmake', '-A', 'x64', '.'],
                                    cwd=self.src_path,
                                    shell=True)
        else:
            result = subprocess.run(['cmake .'], cwd=self.src_path, shell=True)

        if result.returncode != 0:
            self._logger.error("Generation of binding config failed.")
            raise BindingException("Generation of binding config failed.")

    def build_binding(self):
        # build
        if os.name == 'nt':
            result = subprocess.run(
                ['cmake', '--build', '.', '--config', 'Release'],
                cwd=self.src_path,
                shell=True)
        else:
            result = subprocess.run(['make'], cwd=self.src_path, shell=True)

        if result.returncode != 0:
            self._logger.error("Build failed!")
            raise BindingException("Build failed!")

    def add_binding_config(self):
        """
        Add the module config to the cmake lists.

        """
        config_line = "pybind11_add_module({} {} {})".format(
            self.module_name,
            self.module_name + '.cpp',
            'binding_' + self.module_name + '.cpp')

        with open(self.cmake_lists_path, "r") as f:
            if config_line in f.read():
                return

        self._logger.info("Appending build info for '{}'".format(self.module_name))
        with open(self.cmake_lists_path, "a") as f:
            f.write("\n")
            f.write(config_line)

    def create_cmake_lists(self):
        """
        Create the stub of a `CMakeLists.txt` .

        Returns:

        """
        c_make_lists = "cmake_minimum_required(VERSION 2.8.12)\n"
        c_make_lists += "project({})\n\n".format(self.module_name)

        c_make_lists += "set( CMAKE_RUNTIME_OUTPUT_DIRECTORY . )\n"
        c_make_lists += "set( CMAKE_LIBRARY_OUTPUT_DIRECTORY . )\n"
        c_make_lists += "set( CMAKE_ARCHIVE_OUTPUT_DIRECTORY . )\n\n"

        c_make_lists += "foreach( OUTPUTCONFIG ${CMAKE_CONFIGURATION_TYPES} )\n"
        c_make_lists += "\tstring( TOUPPER ${OUTPUTCONFIG} OUTPUTCONFIG )\n"
        c_make_lists += "\tset( CMAKE_RUNTIME_OUTPUT_DIRECTORY_${OUTPUTCONFIG} . )\n"
        c_make_lists += "\tset( CMAKE_LIBRARY_OUTPUT_DIRECTORY_${OUTPUTCONFIG} . )\n"
        c_make_lists += "\tset( CMAKE_ARCHIVE_OUTPUT_DIRECTORY_${OUTPUTCONFIG} . )\n"
        c_make_lists += "endforeach( OUTPUTCONFIG CMAKE_CONFIGURATION_TYPES )\n\n"

        # TODO get pybind install via pip running and use this line:
        # c_make_lists += "find_package(pybind11)"
        c_make_lists += "add_subdirectory({} pybind11)\n".format(self.pybind_path)

        with open(self.cmake_lists_path, "w") as f:
            f.write(c_make_lists)
