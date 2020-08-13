from __future__ import unicode_literals
from textx.metamodel import metamodel_from_str
from pytest import raises
from textx.exceptions import TextXSemanticError

grammar = """
MyModel: 'model' name=ID
  connections+=Connection
  sender+=Sender
  receiver+=Receiver;

Sender:
  'outgoing' name=ID 'over' connection=[Connection|ID];

Receiver:
 'incoming' name=ID 'over' connection=[Connection|ID];

// fix/works (no unused user classes):
// ConnectionHandler: Sender|Receiver;

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


class ConnectionHandler(object):
    def _init_(self):
        print('')

    def awesomeMethod4SenderAndReceiver(self):
        print("I am really important for Sender and Receiver")


class Sender(ConnectionHandler):
    def __init__(self, name=None, connection=None, parent=None):
        super(Sender).__init__()
        print('')


class Receiver(ConnectionHandler):
    def __init__(self, name=None, connection=None, parent=None):
        super(Receiver).__init__()
        print('')


def test_issue270():
    # fix/works (no unused user classes):
    mm = metamodel_from_str(grammar, classes=[Sender, Receiver])
    _ = mm.model_from_str(modelstring)

    # does not work
    mm = metamodel_from_str(grammar, classes=[ConnectionHandler, Sender, Receiver])
    with raises(TextXSemanticError,
                match="unexpected: ConnectionHandler seems to be unused in the grammar"):
        _ = mm.model_from_str(modelstring)

    # does work (allow unused user classes)
    mm = metamodel_from_str(grammar, classes=[ConnectionHandler, Sender, Receiver],
                            allow_unused_user_classes=True)
    _ = mm.model_from_str(modelstring)
