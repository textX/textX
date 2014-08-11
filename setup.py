#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>"
__version__ = "0.1-dev"

from setuptools import setup

NAME = 'textX'
VERSION = __version__
DESC = 'Meta-language in Arpeggio inspired by Xtext'
AUTHOR = 'Igor R. Dejanovic'
AUTHOR_EMAIL = 'igor DOT dejanovic AT gmail DOT com'
LICENCE = 'MIT'
URL = 'https://github.com/igordejanovic/textX'

setup(
    name = NAME,
    version = VERSION,
    description = DESC,
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    maintainer = AUTHOR,
    maintainer_email = AUTHOR_EMAIL,
    license = LICENCE,
    url = URL,
    packages = ["textx"],
    keywords = "parser meta-language language",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Interpreters',
        'Topic :: Software Development :: Compilers',
        'Topic :: Software Development :: Libraries :: Python Modules'
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        ]

)
