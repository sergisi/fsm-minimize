""" Class of machine. It will get the attributes, and represent the 
state machine"""
import argparse
import pprint
import pygraphviz as pgv
from abc import ABC, abstractmethod


class PrintableInterfaceMachine(ABC):
    machine_attributes = {
        'directed': True,
        'strict': False,
        'rankdir': 'LR',
        'ratio': '0.3',
    }

    style_attributes = {
        'node': {
            'default': {
                'shape': 'circle',
                'height': '1.2',
                'style': 'filled',
                'fillcolor': 'white',
                'color': 'black',
            },
            'final': {
                'shape': 'doublecircle',
                'height': '1.2',
                'style': 'filled',
                'fillcolor': 'white',
                'color': 'black',
            },
            'initial': {
                'shape': 'point',
            }
        },
        'edge': {
            'default': {
                'color': 'black'
            },
        },
        'graph': {
            'default': {
                'color': 'black',
                'fillcolor': 'white'
            },
        }
    }

    def _add_nodes(self, machine, graph):
        for state in machine.states:
            if state in machine.finals:
                attr = self.style_attributes['node']['final']
            else:
                attr = self.style_attributes['node']['default']
            graph.add_node(state, **attr)

    def _add_initials(self, machine, graph):
        attr = self.style_attributes['node']['initial']
        for index, state in enumerate(machine.initials):
            graph.add_node('qi' + str(index), **attr)
            graph.add_edge('qi' + str(index), state)

    def _add_edges(self, machine, graph):
        for transition in machine.transitions_list:
            graph.add_edge(transition[1], transition[2], label=transition[0])

    @abstractmethod
    def represent(self, machine):
        raise NotImplementedError


class MyPrintableMachine(PrintableInterfaceMachine):
    def represent(self, machine):
        if not pgv:
            raise Exception('You need to have pygraphviz in order to work!!!')

        graph = pgv.AGraph(label=machine.name, compound=True, **self.machine_attributes)

        self._add_nodes(machine, graph)
        self._add_initials(machine, graph)
        self._add_edges(machine, graph)
        return graph


class Machine(object):

    def __init__(self, name, states, alphabet, transitions_list, initials,
                 finals):
        self.name = name
        self.states = states
        self.alphabet = alphabet
        self.transitions_list = transitions_list
        self._set_transitions()
        self.initials = initials
        self.finals = finals
        # afegit durant refactor
        self.interface = MyPrintableMachine()

    def __str__(self):
        return "{}\nALPHABET: {}\nSTATES: {}\nINITIAL STATES: {}\n" \
               "FINAL STATES: {}\nTRANSITIONS {}".format(self.name, self.alphabet, self.states, self.initials,
                                                         self.finals, pprint.pformat(self.transitions))
    
    def _set_transitions(self):
        transitions = {}
        for state in self.states:
            transitions[state] = {}
        for trans in self.transitions_list:
            transitions[trans[1]][trans[0]] = trans[2]
        self.transitions = transitions
    
    def minimize(self):
        state_group = self._minimize_first()
        length = len(state_group) + 1
        while length != len(state_group):
            length = len(state_group)
            state_group = self._minimize_process(state_group)
        return self._from_minimized(state_group)

    def _minimize_first(self):
        return [[state for state in self.states not in self.finals],
                self.finals]

    def _minimize_process(self, state_group):
        new_state_group = []
        values = self._values(state_group)[0]
        stack = list(state_group)
        while not stack:
            actual_states = stack.pop()
            actual_state = stack.pop()
            to_add = [actual_state]
            to_stack = []
            for state in actual_states:
                if self._same(actual_state, state, state_group, values):
                    to_add.append(state)
                else:
                    to_stack.append(state)
            stack.append(to_stack)
            new_state_group.append(to_add)
        return new_state_group
    
    def _values(self, state_group):
        index = 0
        values = {}
        for states in state_group:
            for state in states:
                values[state] = index
            index += 1
        return values, index
    
    def _same(self, state1, state2, state_group, values):
        if len(self.transitions[state1]) != len(self.transitions[state2]):
            return False
        for trans in self.transitions[state1]:
            if trans not in self.transitions[state2] and \
               values[self.transitions[state1][trans]] != \
               values[self.transitions[state2][trans]]:
                return False
        return True

    def _from_minimized(self, state_group):
        values, index = self._values(state_group)
        new_states = [i for i in range(index)]
        transitions_list = self._get_transitions(state_group, values)
        initials = list(dict.fromkeys([values[initial] 
                                       for initial in self.initials]))
        finals = list(dict.fromkeys([values[final] for final in self.finals]))
        return Machine(self.name + 'minimized', new_states, self.alphabet, 
                       transitions_list, initials, finals)

    def _get_transitions(self, states_group, values):
        trans = []
        for states in states_group:
            for transition in self.transitions[states[0]]:
                trans.append([transition, values[states[0],
                             values[self.transitions[states[0][transition]]]]])
        return trans

    def represent(self):
        return self.interface.represent(self)


def parse_input_file(path):
    """
    :param path: ruta al fitxer amb format:
                1- Declaració alfabet: a [lletra]
                2- Declaració estats: e [estat]
                3- Declaració estat inicial: i [estat]
                4- Declaració estat final: f [estat]
                5- Declaració transició: t [lletra] [estat_origen] [estat_destí]
    :return: diccionari amb keys: states, alpha, init, end, trans
    """

    with open(path, 'r') as f:
        elements = {'states': [], 'alpha': [], 'init': [], 'end': [], 'trans': []}
        i = 0
        for line in f:
            i += 1
            words = line.split()
            if words[0] == "a":
                if len(words) >= 2:
                    for word in words[1:]:
                        elements['alpha'].append(word)
                else:
                    raise Exception("Error in line: " + str(i) + "\n\t" + str(line))
            elif words[0] == "e":
                if len(words) >= 2:
                    for word in words[1:]:
                        elements['states'].append(word)
                else:
                    raise Exception("Error in line: " + str(i) + "  " + line)
            elif words[0] == "i":
                if len(words) == 2:
                    if words[1] in elements.get('states'):
                        elements['init'].append(words[1])
                    else:
                        raise Exception("Error STATE DOES NOT EXIST in line: " + str(i) + "\n\t" + str(line))
                else:
                    raise Exception("Error in line: " + str(i) + "\n\t" + str(line))
            elif words[0] == "f":
                if len(words) == 2:
                    if words[1] in elements.get('states'):
                        elements['end'].append(words[1])
                    else:
                        raise Exception("Error STATE DOES NOT EXIST in line: " + str(i) + "\n\t" + str(line))
                else:
                    raise Exception("Error in line: " + str(i) + "\n\t" + str(line))
            elif words[0] == "t":
                if len(words) == 4:
                    if words[1] in elements.get('alpha'):
                        if words[2] in elements.get('states') and words[3] in elements.get('states'):
                            elements['trans'].append((words[1], words[2], words[3]))
                        else:
                            raise Exception("Error STATE DOES NOT EXIST in line: " + str(i) + "\n\t" + str(line))
                    else:
                        raise Exception("Error WORD DOES NOT EXIST in alphabet: " + str(i) + "\n\t" + str(line))
                else:
                    raise Exception("Error in line: " + str(i) + "\n\t" + str(line))
            else:
                raise Exception("Input file does not match the format expected")
    return elements


def generate_file(name, content, mode="w"):
    with open(name, mode) as f:
        f.write(content)


if __name__ == '__main__':
    # parse args

    parser = argparse.ArgumentParser(description="Representa i/o minimitza un autòmat finit")

    parser.add_argument("-i", dest="input", required=True,
                        help="Especifica fitxer amb la definició del autòmat")
    parser.add_argument("-o", dest="output", default=False, action="store_true",
                        help="Genera fitxer de sortida amb la definició del autòmat")
    parser.add_argument("-p", choices=['simple', 'verbose', 'no'], dest="print", default='simple',
                        help="Generar imatge amb la representació del autòmat")
    parser.add_argument("-m", dest="minimize", default=False, action="store_true",
                        help="Minimitza el autòmat")
    parser.add_argument("-n", dest="name", default="automata",
                        help="Defineix nom del autòmat, (default = automata)")

    args = parser.parse_args()

    # dummy at the moment
    variables = parse_input_file(args.input)

    af = Machine(args.name, variables.get('states'), variables.get('alpha'),
                 variables.get('trans'), variables.get('init'), variables.get('end'))

    if args.minimize:
        # af.minimize()
        raise NotImplementedError
    if args.print != "no":
        af.represent().draw(args.name + ".png", format='png', prog='dot')
    if args.output:
        generate_file(args.name + "_repr", str(af))
