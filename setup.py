#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='aiohttp_swaggerify',
    version='0.1.0',
    description="Library to automatically generate swagger2.0 definition for aiohttp endpoints",
    long_description=readme + '\n\n' + history,
    author="Dmitry Chaplinsky",
    author_email='chaplinsky.dmitry@gmail.com',
    url='https://github.com/dchaplinsky/aiohttp_swaggerify',
    packages=[
        'aiohttp_swaggerify',
    ],
    package_dir={'aiohttp_swaggerify':
                 'aiohttp_swaggerify'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='aiohttp_swaggerify',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
