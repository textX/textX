.. _debugging:

Debugging
=========

textX supports debugging on the meta-model (grammar) and model level. If
debugging is enabled textX will print various debugging messages.

If :code:`debug` parameter to meta-model construction is set to :code:`True`
debug messages during grammar parsing and meta-model construction will be
printed. Additionally a parse tree created during grammar parse as well as
meta-model (if constructed successfully) dot files will be generated::

  form textx.metamodel import metamodel_from_file

  my_metamodel = metamodel_from_file('mygrammar.tx', debug=True)

If :code:`debug` is set in the :code:`model_from_file/str` calls than various
messages during model parsing and construction will be printed. Additionally,
parse tree created from the input as well as model will be exported to dot
file::

  my_model = my_metamodel.model_from_file('mymodel.mod', debug=True)
