import sys
from os.path import dirname, join

from textx import metamodel_from_file


class StateMachine:
    """
    StateMachine model interpreter.
    """
    def __init__(self, model):
        self.model = model

        self.current_state = None

        # First state is initial
        self.initial_state = model.states[0]

        # We are in the initial state at the beginning
        self.set_state(self.initial_state)

    def set_state(self, state):
        if self.current_state is None or state is not self.current_state:
            # Trigger state actions
            for action in state.actions:
                print("Executing action ", action.name)
            print("Transition to state ", state.name)
            self.current_state = state

    def event(self, event):
        # Check if this is some of reset events
        if event in self.model.resetEvents:
            self.set_state(self.initial_state)
        else:
            for transition in self.current_state.transitions:
                if transition.event is event:
                    self.set_state(transition.to_state)
                    return

    def print_menu(self):
        print("Current state: ", self.current_state.name)
        print("Choose event:")
        for idx, event in enumerate(self.model.events):
            print(idx + 1, '-', event.name, event.code)
        print('q - quit')

    def interpret(self):
        """
        Main interpreter loop.
        """
        self.print_menu()
        while True:
            try:
                event = input()
                if event == 'q':
                    return
                event = int(event)
                event = self.model.events[event - 1]
            except Exception:
                print('Invalid input')

            self.event(event)
            self.print_menu()


if __name__ == '__main__':
    this_folder = dirname(__file__)
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <model>")
    else:
        meta_model = metamodel_from_file(join(this_folder, 'state_machine.tx'))
        model = meta_model.model_from_file(sys.argv[1])
        state_machine = StateMachine(model)
        state_machine.interpret()
