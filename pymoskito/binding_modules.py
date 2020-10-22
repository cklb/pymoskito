import logging
import os
import subprocess
from pathlib import Path
import importlib.util

from PyQt5.QtCore import QObject

__all__ = ["CppBase"]


class BindingException(Exception):
    """
    Exception to be raised if the cpp binding raises.
    """
    pass


class CppBase(QObject):
    def __init__(self, module_name=None, module_path=None):
        QObject.__init__(self, None)

        self._logger = logging.getLogger(self.__class__.__name__)

        if module_name is None:
            self._logger.error("Instantiation of binding class without"
                               " module_name is not allowed!")
            raise BindingException("Instantiation of binding class without"
                                   " module_name is not allowed!")
        self.module_name = module_name

        if module_path is None:
            self._logger.error("Instantiation of binding class without"
                               " module_path is not allowed!")
            raise BindingException("Instantiation of binding class without"
                                   " module_path is not allowed!")

        self.module_path = Path(module_path)
        self.module_inc_path = self.module_path / str(self.module_name + ".h")
        self.module_src_path = self.module_path / str(self.module_name + '.cpp')
        self.cmake_lists_path = self.module_path / "CMakeLists.txt"

        if self.create_binding_config():
            self.build_binding()
            self.install_binding()

    def create_binding_config(self):
        # check if folder exists
        if not self.module_path.is_dir():
            self._logger.error("CPP bindings could not be found in the given "
                               "folder '{}'".format(os.getcwd()))
            self._logger.info("Make sure that the directory '{}' exists in that"
                              " path.".format(BINDING_DIR))
            return False

        if not self.module_inc_path.exists():
            self._logger.error("Module '{}' could not found in binding folder"
                               "".format(self.module_inc_path))
            return False

        if not self.cmake_lists_path.exists():
            self._logger.warning("No CMakeLists.txt found!")
            self._logger.info("Generating new CMake config.")
            self.create_cmake_lists()

        config_changed = self.update_binding_config()
        if config_changed:
            self.build_config()

        return True

    def build_config(self):
        # generate config
        if os.name == 'nt':
            cmd = ['cmake', '-A', 'x64', '-S' , '.', '-B', '_build']
        else:
            cmd = ['cmake -S . -B _build']
        result = subprocess.run(cmd, cwd=self.module_path, shell=True)

        if result.returncode != 0:
            self._logger.error("Generation of binding config failed.")
            raise BindingException("Generation of binding config failed.")

    def install_binding(self):
        # generate config
        if os.name == 'nt':
            cmd = ['cmake', '--install', '_build']
        else:
            cmd = ['cmake --install _build']
        result = subprocess.run(cmd, cwd=self.module_path, shell=True)

        if result.returncode != 0:
            self._logger.error("Installation of binding config failed.")
            raise BindingException("Installation of binding config failed.")

    def build_binding(self):
        # build
        if os.name == 'nt':
            cmd = ['cmake', '--build', '.', '--config', 'Release']
        else:
            cmd = ['cmake --build _build']
        result = subprocess.run(cmd, cwd=self.module_path, shell=True)

        if result.returncode != 0:
            self._logger.error("Build failed!")
            raise BindingException("Build failed!")

    def update_binding_config(self):
        """
        Add the module config to the cmake lists.

        Returns:
            bool: True if build config has been changed and cmake has to be
            rerun.
        """
        config_line = "add_library({} SHARED {} {})".format(
            self.module_name, self.module_src_path.as_posix(),
            'binding_' + self.module_name + '.cpp')

        if os.name == 'nt':
            config_line += "\nset_target_properties({} PROPERTIES PREFIX \"\" OUTPUT_NAME \"{}\" SUFFIX \".pyd\")\n".format(
                self.module_name,
                self.module_name)
        else:
            config_line += "\nset_target_properties({} PROPERTIES PREFIX \"\" OUTPUT_NAME \"{}\" SUFFIX \".so\")\n".format(
                self.module_name,
                self.module_name)

        config_line += "target_link_libraries({} ${{PYTHON_LIBRARIES}})".format(
            self.module_name
        )
        if os.name == 'nt':
            config_line += "\ninstall(FILES _build/{}.pyd DESTINATION {})".format(
                self.module_name,
                self.module_path.as_posix()
            )
        else:
            config_line += "\n\ninstall(FILES _build/{}.so DESTINATION {})".format(
                self.module_name,
                self.module_path.as_posix()
            )

        with open(self.cmake_lists_path, "r") as f:
            if config_line in f.read():
                return False

        self._logger.info("Appending build info for '{}'".format(self.module_name))
        with open(self.cmake_lists_path, "a") as f:
            f.write("\n")
            f.write(config_line)

        return True

    def create_cmake_lists(self):
        """
        Create the stub of a `CMakeLists.txt` .

        Returns:

        """
        c_make_lists = "cmake_minimum_required(VERSION 3.4)\n"
        c_make_lists += "project({})\n\n".format(self.module_name)

        c_make_lists += "set( CMAKE_CXX_STANDARD 11 )\n\n"
        c_make_lists += "find_package(PythonLibs REQUIRED)\n\n"

        c_make_lists += "set( CMAKE_RUNTIME_OUTPUT_DIRECTORY . )\n"
        c_make_lists += "set( CMAKE_LIBRARY_OUTPUT_DIRECTORY . )\n"
        c_make_lists += "set( CMAKE_ARCHIVE_OUTPUT_DIRECTORY . )\n\n"

        c_make_lists += "foreach( OUTPUTCONFIG ${CMAKE_CONFIGURATION_TYPES} )\n"
        c_make_lists += "\tstring( TOUPPER ${OUTPUTCONFIG} OUTPUTCONFIG )\n"
        c_make_lists += "\tset( CMAKE_RUNTIME_OUTPUT_DIRECTORY_${OUTPUTCONFIG} . )\n"
        c_make_lists += "\tset( CMAKE_LIBRARY_OUTPUT_DIRECTORY_${OUTPUTCONFIG} . )\n"
        c_make_lists += "\tset( CMAKE_ARCHIVE_OUTPUT_DIRECTORY_${OUTPUTCONFIG} . )\n"
        c_make_lists += "endforeach( OUTPUTCONFIG CMAKE_CONFIGURATION_TYPES )\n\n"

        c_make_lists += "include_directories(${PYTHON_INCLUDE_DIRS})\n"

        with open(self.cmake_lists_path, "w") as f:
            f.write(c_make_lists)

    def get_class_from_module(self):
        try:
            if os.name == 'nt':
                module_path = self.module_path / str(self.module_name + '.pyd')
            else:
                module_path = self.module_path / str(self.module_name + '.so')

            spec = importlib.util.spec_from_file_location(self.module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except ImportError as e:
            self._logger.error("Cannot load module: {}".format(e))
            raise e
