#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read().replace(".. :changelog:", "")

with open("requirements.txt") as requirements_file:
    requirements = requirements_file.read()

test_requirements = [
]

extra_requirements = {
    "3D": ["vtk>=6.3.0"],
    "CPP": ["pybind11>=2.6.0"],
    "docs": ["Sphinx >= 1.4.9",
             "sphinx - rtd - theme >= 0.1.9",
             "sphinxcontrib - tikz >= 0.4.7",
             ],
    "test": [],
}

setup(
    name="pymoskito",
    version="0.3.0",
    description="Python based modular simulation & postprocessing kickass "
                "toolbox",
    long_description=readme + "\n\n" + history,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="pymoskito control simulation feedback feedforward",
    url="https://github.com/cklb/pymoskito",
    author="Stefan Ecklebe",
    author_email="stefan.ecklebe@tu-dresden.de",
    license="GPLv3",
    packages=["pymoskito"],
    package_dir={"pymoskito": "pymoskito"},
    install_requires=requirements,
    include_package_data=True,
    test_suite="pymoskito.tests",
    extras_require=extra_requirements,
    zip_safe=False
)
