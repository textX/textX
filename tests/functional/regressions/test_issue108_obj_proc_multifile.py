from os.path import dirname, join

import textx
import textx.scoping.providers as scoping_providers


def test_issue108_obj_proc_multifile():
    """
    see issue 108 for a detailed error report
    """

    mm = textx.metamodel_from_str(
        """
        Model:
          imports*=Import
          classes*=Class;
        Import: 'import' importURI=STRING ';';
        Class: 'class' name=ID '{' '}';
    """
    )

    lst_class_names = []
    lst_models = []

    def print_obj(x):
        lst_class_names.append(x.name)

    def print_model(m, mm):
        lst_models.append(m)

    mm.register_scope_providers({"*.*": scoping_providers.PlainNameImportURI()})
    mm.register_obj_processors({"Class": print_obj})
    mm.register_model_processor(print_model)

    current_dir = dirname(__file__)
    mm.model_from_file(join(current_dir, "issue108", "a.dsl"))

    assert len(lst_models) == 2
    assert len(lst_class_names) == 2
