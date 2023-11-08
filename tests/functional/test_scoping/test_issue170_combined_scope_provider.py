from textx import metamodel_from_str, textx_isinstance
from textx.scoping.providers import FQN, RelativeName


class MyScope:
    """
    Demo of a combined scope provider:
    Dependent of the underlying data structure an appropriate
    provider is selected...
    """

    def __init__(self, meta):
        self.meta = meta
        self.pStart = RelativeName("parent.event.parameters")
        self.pEvent1 = RelativeName("parent.parameters")
        # also possible: self.pEvent1 = FQN()

    def __call__(self, obj, attr, obj_ref):
        if textx_isinstance(obj.parent, self.meta["Start"]):
            return self.pStart(obj, attr, obj_ref)
        else:
            return self.pEvent1(obj, attr, obj_ref)


def test_combined_scope_provider():
    grammar = """
     F:
         definitions *= Event1
         (start = Start )?
     ;

     Event1:
         'event' name=ID '(' parameters+=Variable[','] ')' ':'
         argumentos+=Repetition[',']
         'end'
     ;

     Start:
         'start' name=ID 'link' event=[Event1] '('
         argumentos+=Repetition[','] ')'
         'end'
     ;

     Repetition:
        name=ID '=' paramName=[Variable];

     Variable: name=ID;
     """

    meta = metamodel_from_str(grammar)
    meta.register_scope_providers({"*.*": FQN(), "Repetition.paramName": MyScope(meta)})

    code = """
    event eventA (varA,varB,varC):
        x1=varA,
        x2=varB,
        x3=varC
    end

    start eventoB link eventA (
        x1=varA,
        x2=varB,
        x3=varC )
    end
    """

    meta.model_from_str(code)
