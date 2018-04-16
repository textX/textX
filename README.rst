.. image:: https://raw.githubusercontent.com/igordejanovic/textX/master/art/textX-logo.png

|pypi-badge| |license| |build-status| |docs|

textX is a meta-language for building Domain-Specific Languages (DSLs) in Python.
It is inspired by `Xtext`_.

In a nutshell, textX will help you build your textual language in an easy way.
You can invent your own language or build a support for already existing
textual language or file format.

From a single language description (grammar), textX will build a
parser and a meta-model (a.k.a. abstract syntax) for the language.
See the docs for the details.

textX follows the syntax and semantics of Xtext but `differs in some places
<http://igordejanovic.net/textX/about/comparison/>`_ and is implemented 100% in
Python using `Arpeggio`_ PEG parser - no grammar ambiguities, unlimited
lookahead, interpreter style of work.


Quick intro
===========

.. code:: python

    from textx import metamodel_from_str, get_children_of_type

    grammar = """
    Model: shapes*=Shape;
    Shape: Circle | Line;
    Circle: 'circle' center=Point '/' radius=INT;
    Line: 'line' start=Point '/' end=Point;
    Point: x=INT ',' y=INT;
    """

    mm = metamodel_from_str(grammar)

    # Meta-model knows how to parse and instantiate models.
    model = mm.model_from_str("""
        line 10, 10 / 20, 20
        line 14, 78 / 89, 33
        circle 14, 20/10
        line 18, 89 / 78, 65
    """)

    # At this point model is plain Python object graph with instances of
    # dynamically created classes and attributes following the grammar.

    def _(p):
        "returns coordinate of the given Point as string"
        return "{},{}".format(p.x, p.y)

    for shape in model.shapes:
        if shape.__class__.__name__ == 'Circle':
            print('Circle: center={}, radius={}'
                  .format(_(shape.center), shape.radius))
        else:
            print('Line: from={} to={}'.format(_(shape.start), _(shape.end)))

    # Output:
    # Line: from=10,10 to=20,20
    # Line: from=14,78 to=89,33
    # Circle: center=14,20, radius=10
    # Line: from=18,89 to=78,65

    # Collect all points starting from the root of the model
    points = get_children_of_type("Point", model)
    for point in points:
        print('Point: {}'.format(_(point)))

    # Output:
    # Point: 10,10
    # Point: 20,20
    # Point: 14,78
    # Point: 89,33
    # Point: 14,20
    # Point: 18,89
    # Point: 78,65

Video tutorials
===============


Introduction to textX
~~~~~~~~~~~~~~~~~~~~~

.. image:: https://img.youtube.com/vi/CN2IVtInapo/0.jpg
   :target: https://www.youtube.com/watch?v=CN2IVtInapo



Implementing Martin Fowler's State Machine DSL in textX
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. image:: https://img.youtube.com/vi/HI14jk0JIR0/0.jpg
   :target: https://www.youtube.com/watch?v=HI14jk0JIR0


Docs and tutorials
==================

The full documentation with tutorials is available at http://igordejanovic.net/textX/


Discussion and help
===================

For bug report, general discussion and help please use `GitHub issue tracker <https://github.com/igordejanovic/textX/issues>`_.


License
=======

MIT

Python versions
===============

Tested for 2.7, 3.3+


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


