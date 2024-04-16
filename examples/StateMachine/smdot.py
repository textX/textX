"""
Export state machine models to dot.
"""
import codecs
import sys
from os.path import dirname, join

from textx import metamodel_from_file

HEADER = '''
    digraph textX {
    fontname = "Bitstream Vera Sans"
    fontsize = 8
    node[
        shape=record,
        style=rounded
    ]
    edge[dir=black,arrowtail=empty]


'''


def sm_to_dot(model):
    """
    Transforms given state machine model to dot str.
    """

    dot_str = HEADER

    # Render states
    first = True
    for state in model.states:
        dot_str += '{}[label="{{{}{}|{}}}"]\n'.format(
            id(state), r"-\> " if first else "", state.name,
            "\\n".join(action.name for action in state.actions))
        first = False

        # Render transitions
        for transition in state.transitions:
            dot_str += f'{id(state)} -> {id(transition.to_state)}' \
                       f' [label="{transition.event.name}"]\n'

    # If there are reset events declared render them.
    if model.resetEvents:
        dot_str += 'reset_events [label="{{Reset Events|{}}}", style=""]\n'\
            .format("\\n".join(event.name for event in model.resetEvents))

    dot_str += '\n}\n'
    return dot_str


if __name__ == '__main__':
    this_folder = dirname(__file__)
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} <model>\n')
    else:
        model_name = sys.argv[1]
        meta = metamodel_from_file(join(this_folder, 'state_machine.tx'))
        model = meta.model_from_file(model_name)
        with codecs.open(f"{model_name}.dot", 'w',
                         encoding='utf-8') as f:
            f.write(sm_to_dot(model))
