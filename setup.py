#!/usr/bin/env python

import os.path

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

from setuptools import setup, find_packages
setup(
    name="pycnc",
    version="1.1.0",
    packages=find_packages(),
    scripts=['pycnc'],
    include_package_data=True,

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.js', '*.html', '.conf'],
    },

    data_files=[
        ('/cnc/etc/', [os.path.join('extra', 'pycnc.conf')]),
        ('/cnc/webiopi/', [os.path.join('htdocs', 'index.html'), os.path.join('htdocs', 'jquery.js'), os.path.join('htdocs', 'webiopi.css'),os.path.join('htdocs', 'webiopi.js') ]),
    ],

    # metadata for upload to PyPI
    author="Nikolay Khabarov",
    author_email="2xl@mail.ru",
    description="CNC machine controller",
    long_description=long_description,
    license="MIT",
    keywords="CNC 3D printer robot raspberry pi",
    url="https://github.com/Nikolay-Kha/PyCNC",
)
