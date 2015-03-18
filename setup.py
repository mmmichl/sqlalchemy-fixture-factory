# -*- coding: utf-8 -*-

"""
SQLAlchemy-Fixture-Factory

A fixture factory for SQLAlchemy to easily build test scenarios for unit or integration testing.
Build test scenarios organically and instantiate them with one line including all dependencies.
"""

from __future__ import absolute_import, print_function, unicode_literals, division

import os
import re
from setuptools import setup, find_packages


HERE = os.path.dirname(os.path.abspath(__file__))


def get_version():
    filename = os.path.join(HERE, 'sqlalchemy_fixture_factory', '__init__.py')
    with open(filename) as f:
        contents = f.read()
    pattern = r"^__version__ = '(.*?)'$"
    return re.search(pattern, contents, re.MULTILINE).group(1)


setup(
    name='SQLAlchemy-Fixture-Factory',
    version=get_version(),
    url='https://github.com/mmmichl/sqlalchemy-fixture-factory',
    license='MIT',
    author='Michael Pickelbauer',
    author_email='mmmichlPi' '@' 'gmail.com',
    description='Test Fixture Factory for SQLAlchemy.',
    long_description=__doc__,
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'SQLAlchemy>=0.7',
    ],
    extras_require = {},
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Topic :: Database',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ]
)