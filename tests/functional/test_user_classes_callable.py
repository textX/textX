from pytest import raises

from textx.exceptions import TextXSemanticError
from textx.metamodel import metamodel_from_str

grammar = """
MyModel: 'model' name=ID
  connections+=Connection
  sender+=Sender
  receiver+=Receiver;

Sender:
  'outgoing' name=ID 'over' connection=[Connection:ID];

Receiver:
 'incoming' name=ID 'over' connection=[Connection:ID];

Connection:
  'connection' name=ID
  'port' port=STRING
  'ip' ip=STRING;
"""


grammar_with_baseclass_fix = """
MyModel: 'model' name=ID
  connections+=Connection
  sender+=Sender
  receiver+=Receiver;

Sender:
  'outgoing' name=ID 'over' connection=[Connection:ID];

Receiver:
 'incoming' name=ID 'over' connection=[Connection:ID];

// fix/works (no unused user classes):
ConnectionHandler: Sender|Receiver;

Connection:
  'connection' name=ID
  'port' port=STRING
  'ip' ip=STRING;
"""


modelstring = """
model Example
connection conn port "1" ip "127.0.0.1"

outgoing out0 over conn
incoming in0 over conn

"""


class ConnectionHandler:
    def _init_(self):
        print("")

    def awesomeMethod4SenderAndReceiver(self):
        print("I am really important for Sender and Receiver")


class Sender(ConnectionHandler):
    def __init__(self, name=None, connection=None, parent=None):
        super().__init__()
        print("")


class Receiver(ConnectionHandler):
    def __init__(self, name=None, connection=None, parent=None):
        super().__init__()
        print("")


def test_user_classes_callable():
    """
    See metamodel.md, "Custom classes"
    See issue270
    """
    # fix/works (no unused user classes):
    mm = metamodel_from_str(grammar, classes=[Sender, Receiver])
    _ = mm.model_from_str(modelstring)

    # fix/works (no unused user classes; see grammar_with_baseclass_fix):
    mm = metamodel_from_str(
        grammar_with_baseclass_fix, classes=[ConnectionHandler, Sender, Receiver]
    )
    _ = mm.model_from_str(modelstring)

    # does not work
    with raises(
        TextXSemanticError, match="ConnectionHandler class is not used in the grammar"
    ):
        _ = metamodel_from_str(grammar, classes=[ConnectionHandler, Sender, Receiver])

    # does work (allow unused user classes by providing a callable instead of
    # a list of classes: the callable returns a user class for a given rule name
    # or None)
    def class_provider(name):
        classes = [ConnectionHandler, Sender, Receiver]
        classes = dict(map(lambda x: (x.__name__, x), classes))
        return classes.get(name)

    mm = metamodel_from_str(grammar, classes=class_provider)
    m = mm.model_from_str(modelstring)
    for s in m.sender:
        assert isinstance(s, Sender)
    for r in m.receiver:
        assert isinstance(r, Receiver)
