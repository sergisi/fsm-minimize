""" Class of machine. It will get the attributes, and represent the 
state machine"""

import pygraphviz as pgv


class Machine():
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

    def __init__(self, states, alphabet, transitions_list, initials,
                 finals):
        self.states = states
        self.alphabet = alphabet
        self.transitions_list = transitions_list
        self._set_transitions()
        self.initials = initials
        self.finals = finals
    
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
        values = self._values(state_group)
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
        return values
    
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
        pass  # TODO: this should return a Machine minimized        

    def _add_nodes(self, graph):
        for state in self.states:
            if state in self.finals:
                attr = self.style_attributes['node']['final']
            else:
                attr = self.style_attributes['node']['default']
            graph.add_node(state, **attr)
    

    def _add_initials(self, graph):
        attr = self.style_attributes['node']['initial']
        for index, state in enumerate(self.initials):
            graph.add_node('qi' + str(index), **attr)
            graph.add_edge('qi' + str(index), state)
    

    def _add_edges(self, graph):
        for transition in self.transitions_list:
            graph.add_edge(transition[1], transition[2], label=transition[0])


    def represent(self, title=None):
        if not pgv:
            raise Exception('You need to have pygraphviz in order to work')
        if title is False:
            title = ''
        
        graph = pgv.AGraph(label=title, compound=True, **self.machine_attributes)

        self._add_nodes(graph)
        self._add_initials(graph)
        self._add_edges(graph)
        # graph.draw('file', format='svg', prog='dot')
        return graph


if __name__ == '__main__':
    af = Machine(['0', '1'], ['a', 'b'], [['a', '0', '1'],
                                          ['a', '1', '1'],
                                          ['b', '1', '1']],
                 ['0'], ['1'])
    af.represent(title='Test').draw('file.png', format='png', prog='dot')
