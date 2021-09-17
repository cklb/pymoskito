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
    "3d": ["vtk>=6.3.0"],
    "cpp": ["pybind11>=2.7.0"],
    "docs": ["Sphinx>=1.4.9",
             "sphinx-rtd-theme>=0.1.9",
             "sphinxcontrib-tikz>=0.4.7",
             "docutils",
             ],
    "test": [],
}

setup(
    name="pymoskito",
    version="0.4.0rc4",
    description="Python based modular simulation & postprocessing kickass "
                "toolbox",
    long_description=readme + "\n\n" + history,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords="pymoskito control simulation feedback feedforward",
    long_description_content_type="text/x-rst",
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
