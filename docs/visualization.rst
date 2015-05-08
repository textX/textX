.. _visualization:

Visualization
=============

A meta-model, model and parse-tree can be exported to dot files (`GraphViz`_)
for visualization. Module :code:`textx.export` contains functions
:code:`metamodel_export` and :code:`model_export` that can export meta-model and
model to dot file respectively.

If :ref:`debugging` is enabled, meta-model, model and parse trees will
automatically get exported to dot.

.. _GraphViz: http://www.graphviz.org/


Meta-model visualization
------------------------

To visualize meta-model::

  from textx.metamodel import metamodel_from_file
  from textx.export import metamodel_export

  entity_mm = metamodel_from_file('entity.tx')

  metamodel_export(entity_mm, 'entity.dot')


:code:`entity.dot` file will be created. You can visualize this file by a
various dot viewers or can convert it to various image formats by :code:'dot'
tool::

  dot -Tpng -O entity.dot

The following image is generated:

|entity_mm|


Model visualization
-------------------

Similar to meta-model visualization you can visualize your models also::

  from textx.export import model_export

  person_model = entity_mm.model_from_file('person.ent')

  model_export(person_model, 'person.dot')


Convert this dot file to png with::

  dot -Tpng -O person.dot

The following image is generated:

|person_model|


.. |entity_mm| image:: https://raw.githubusercontent.com/igordejanovic/textX/master/examples/Entity/dotexport/entity_meta.dot.png
.. |person_model| image:: https://raw.githubusercontent.com/igordejanovic/textX/master/examples/Entity/dotexport/entity.dot.png


