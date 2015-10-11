.. image:: https://raw.githubusercontent.com/igordejanovic/textX/master/art/textX-logo.png

textX
=====

|pypi-badge| |license| |build-status| |docs|

textX is a meta-language for building Domain-Specific Languages (DSLs) inspired
by `Xtext`_.  From a single language description (grammar) textX will build a
parser and a meta-model (a.k.a. abstract syntax) for the language.

textX follows the syntax and semantics of Xtext but differs in some places and is
implemented 100% in Python using `Arpeggio`_ parser.
It is fully dynamic - no code generation at all!


Documentation is available at http://igordejanovic.net/textX/


.. _Arpeggio: https://github.com/igordejanovic/Arpeggio
.. _Xtext: http://www.eclipse.org/Xtext/

.. |pypi-badge| image:: https://img.shields.io/pypi/v/textX.svg
   :target: https://pypi.python.org/pypi/textX
   :alt: PyPI Version

.. |license| image:: https://img.shields.io/pypi/l/Arpeggio.svg

.. |build-status| image:: https://travis-ci.org/igordejanovic/textX.svg?branch=master
   :target: https://travis-ci.org/igordejanovic/textX

.. |docs| image:: https://img.shields.io/badge/docs-latest-green.svg
   :target: http://igordejanovic.net/textX/
   :alt: Documentation Status


