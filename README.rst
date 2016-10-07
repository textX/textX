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

textX follows the syntax and semantics of Xtext but differs in some places and is
implemented 100% in Python using `Arpeggio`_ PEG parser - no grammar
ambiguities, unlimited lookahead, interpreter style of work.


Quick intro
===========

.. code:: python

    from textx.metamodel import metamodel_from_str
    from textx.model import children_of_type

    grammar = """
    Model: shapes*=Shape;
    Shape: Circle | Line;
    Circle: 'circle' center=Point '/' radius=INT;
    Line: 'line' start=Point '/' end=Point;
    Point: x=INT ',' y=INT;
    """

    mm = metamodel_from_str(grammar)
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

    # Collect all points starting from the root of the model
    points = children_of_type(model, "Point")
    for point in points:
        print('Point: {}'.format(_(point)))


Docs and tutorials
==================

The full documentation with tutorials is available at http://igordejanovic.net/textX/


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


