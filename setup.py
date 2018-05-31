#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import codecs
from setuptools import setup

VERSIONFILE = "textx/__init__.py"
VERSION = None
for line in open(VERSIONFILE, "r").readlines():
    if line.startswith('__version__'):
        VERSION = line.split('"')[1]

if not VERSION:
    raise RuntimeError('No version defined in textx.__init__.py')

README = codecs.open(os.path.join(os.path.dirname(__file__), 'README.rst'),
                     'r', encoding='utf-8').read()


if sys.argv[-1].startswith('publish'):
    if os.system("pip list | grep wheel"):
        print("wheel not installed.\nUse `pip install wheel`.\nExiting.")
        sys.exit()
    if os.system("pip list | grep twine"):
        print("twine not installed.\nUse `pip install twine`.\nExiting.")
        sys.exit()
    os.system("python setup.py sdist bdist_wheel")
    if sys.argv[-1] == 'publishtest':
        os.system("twine upload -r test dist/*")
    else:
        os.system("twine upload dist/*")
        print("You probably want to also tag the version now:")
        print("  git tag -a {0} -m 'version {0}'".format(VERSION))
        print("  git push --tags")
    sys.exit()

setup(
    name='textX',
    version=VERSION,
    description='Meta-language for DSL implementation inspired by Xtext',
    long_description=README,
    author='Igor R. Dejanovic',
    author_email='igor.dejanovic@gmail.com',
    license='MIT',
    url='https://github.com/igordejanovic/textX',
    download_url='https://github.com/igordejanovic/textX/archive/v%s.tar.gz'
        % VERSION,
    packages=["textx", "textx.commands", "textx.scoping"],
    install_requires=["Arpeggio"],
    tests_require=[
        'pytest',
    ],
    keywords="parser meta-language meta-model language DSL",
    entry_points={
        'console_scripts': [
            'textx = textx.commands.console:textx'
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
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
