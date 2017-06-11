#!/usr/bin/env python

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

from setuptools import setup, find_packages
setup(
    name="pycnc",
    version="0.1.3",
    packages=find_packages(),
    scripts=['pycnc'],

    # metadata for upload to PyPI
    author="Nikolay Khabarov",
    author_email="2xl@mail.ru",
    description="CNC machine controller",
    long_description=long_description,
    license="MIT",
    keywords="CNC 3D printer robot raspberry pi",
    url="https://github.com/Nikolay-Kha/PyCNC",
)

