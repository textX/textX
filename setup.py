#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>"
__version__ = "0.2-dev"

from setuptools import setup

NAME = 'textX'
VERSION = __version__
DESC = 'Meta-language in Arpeggio inspired by Xtext'
AUTHOR = 'Igor R. Dejanovic'
AUTHOR_EMAIL = 'igor DOT dejanovic AT gmail DOT com'
LICENSE = 'MIT'
URL = 'https://github.com/igordejanovic/textX'
DOWNLOAD_URL = 'https://github.com/igordejanovic/textX/archive/v%s.tar.gz' % VERSION

setup(
    name = NAME,
    version = VERSION,
    description = DESC,
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    maintainer = AUTHOR,
    maintainer_email = AUTHOR_EMAIL,
    license = LICENSE,
    url = URL,
    download_url = DOWNLOAD_URL,
    packages = ["textx"],
    install_requires = ["Arpeggio"],
    keywords = "parser meta-language meta-model language DSL",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Interpreters',
        'Topic :: Software Development :: Compilers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        ]

)
