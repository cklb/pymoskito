# -*- coding: utf-8 -*-

import importlib.util
import logging
import os
import subprocess
import sys
from pathlib import Path

try:
    import pybind11
except ModuleNotFoundError:
    logging.warning("Package 'pybind11' could not be loaded, binding modules "
                    "will not be available")

__all__ = ["CppBase"]

BUILD_DIR = "_build"
CMAKE_LISTS = "CMakeLists.txt"


class BindingException(Exception):
    """
    Exception to be raised if the cpp binding raises.
    """
    pass


class CppBase:
    """
    Mix-in class for modules written in C++.

    This class uses pybind and cmake to automatically compile and link the
    provided sources and load them as an python module.

    Args:
        :module_path: Path to directory that contains the sources.
        :module_name: Name of the module
        :binding_source: cpp file including the binding definition
        :additional_sources: List of additional cpp files to compile into module
        :additional_lib: dict with key 'lib name' and additional lines for the
          CMakeLists

    Warn:
        `additional_sources` will be added to the compilation unit.
        *Every other file* is ignored by this routine so far.

    """

    def __init__(self,
                 module_path=None,
                 module_name=None,
                 binding_source=None,
                 additional_sources=None,
                 binding_class_name=None,
                 additional_lib=None):
        self._logger = logging.getLogger(self.__class__.__name__)

        # adapt to os-specific extensions
        if os.name == 'nt':
            self.sfx = '.pyd'
        else:
            self.sfx = '.so'

        if module_name is None:
            message = "Instantiation of binding class without module_name is not allowed!"
            self._logger.error(message)
            raise BindingException(message)
        self.module_name = module_name

        if module_path is None:
            message = "Instantiation of binding class without module_path is not allowed!"
            self._logger.error(message)
            raise BindingException(message)

        if binding_source is None:
            if binding_class_name is not None:
                binding_source = binding_class_name + ".cpp"
                module_source = module_name + ".cpp"
                additional_sources = additional_sources.append(module_source) if additional_sources else [module_source]
                self._logger.warn("Use of binding_class_name is deprecated. Please migrate to binding_source")
            else:
                message = "Instantiation of binding class without binding_source is not allowed!"
                self._logger.error(message)
                raise BindingException(message)

        self.module_path = Path(module_path).resolve()
        self.build_path = self.module_path / BUILD_DIR
        self.sources = [binding_source] if additional_sources is None else [*additional_sources, binding_source]

        self.additional_lib = None
        if additional_lib is not None:
            assert (isinstance(additional_lib, dict))
            self.additional_lib = additional_lib

        if self.create_binding_config():
            self.build_binding()
            ModuleFinder().register(self.module_name,
                                    (self.build_path / self.module_name).with_suffix(self.sfx))
            self.bindings = self.load()

    def create_binding_config(self):
        # check if folder exists
        if not self.module_path.is_dir():
            self._logger.error("Config folder '{}' does not exist."
                               "".format(self.module_path))
            return False

        if not self.build_path.is_dir():
            self.build_path.mkdir()

        for src in self.sources:
            if not (self.module_path / src).is_file():
                self._logger.error("Source file '{}' could not be found in the "
                                   "given module path '{}'."
                                   "".format(src,
                                             self.module_path))
                return False

        if not (self.build_path / CMAKE_LISTS).is_file():
            self._logger.info("CMakeLists.txt not found in module build dir.")
            self._logger.info("Generating new CMake config.")
            self.create_cmake_lists()

        config_changed = self.update_binding_config()
        if config_changed:
            self.build_config()

        return True

    def create_cmake_lists(self):
        """
        Create the stub of a `CMakeLists.txt` .

        Returns:
        """
        py_ver = sys.version_info
        c_make_lists = """
cmake_minimum_required(VERSION 3.15)
project(Bindings)

find_package(Python REQUIRED COMPONENTS Interpreter Development)

find_package(pybind11 CONFIG REQUIRED PATHS ${Python_SITELIB})
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY .)
set(PYTHON_MODULE_EXTENSION ".so")
"""

        with open(self.build_path / CMAKE_LISTS, "w") as f:
            f.write(c_make_lists)

    def update_binding_config(self):
        """
        Add the module config to the cmake lists.

        Returns:
            bool: True if build config has been changed and cmake has to be
            rerun.
        """
        cmake_line = "\ninclude({}.cmake)\n".format(self.module_name)
        config_line = "\npybind11_add_module({} SHARED {})\n".format(
            self.module_name,
            " ".join([Path(os.path.relpath(self.module_path / src, self.build_path)).as_posix() for src in self.sources]),
        )
        if self.additional_lib:
            for value in self.additional_lib.values():
                config_line += value
            config_line += "\ntarget_link_libraries({} PRIVATE {})\n".format(
                self.module_name,
                " ".join(self.additional_lib.keys()),
            )
        ret = False
        with open(self.build_path / "{}.cmake".format(self.module_name), 'w+') as f:
            if config_line not in f.read():
                f.write(config_line)
                ret = True

        with open(self.build_path / CMAKE_LISTS, "r+") as f:
            if cmake_line not in f.read():
                self._logger.info("Appending build info for '{}'".format(self.module_name))
                f.write(cmake_line)
                ret = True

        return ret

    def build_config(self):
        # generate config
        if os.name == 'nt' and 'GCC' not in sys.version:
            cmd = ['cmake', '-A', 'x64', '-S', '.', '-B', '.']
        else:
            cmd = ['cmake', '.']
        result = subprocess.run(cmd, cwd=self.build_path)

        if result.returncode != 0:
            message = "Generation of binding config failed."
            self._logger.error(message)
            raise BindingException(message)

    def build_binding(self):
        # build
        if os.name == 'nt' and 'GCC' not in sys.version:
            cmd = ['cmake', '--build', '.', '--config', 'Release', '--target', 'INSTALL']
        else:
            cmd = ['cmake', '--build', '.', '-t', self.module_name]
        result = subprocess.run(cmd, cwd=self.build_path)

        if result.returncode != 0:
            message = "Build failed!"
            self._logger.error(message)
            raise BindingException(message)

    def load(self):
        if self.module_name in sys.modules:
            del sys.modules[self.module_name]
        return importlib.import_module(self.module_name)


class ModuleFinder(importlib.abc.MetaPathFinder):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModuleFinder, cls).__new__(cls)
            cls._instance.path_map = dict()
            sys.meta_path.insert(0, cls._instance)
        return cls._instance

    def register(self, name, path):
        if name in self.path_map.keys():
            return
        self.path_map[name] = path

    def find_spec(self, name, path, target=None):
        if not name in self.path_map:
            return None
        return importlib.util.spec_from_file_location(name, self.path_map[name])
