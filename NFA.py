from .DFA import DFA

from dataclasses import dataclass
from collections.abc import Callable

EPSILON = ''  # this is how epsilon is represented by the checker in the transition function of NFAs


@dataclass
class NFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], set[STATE]]
    F: set[STATE]

    def epsilon_closure(self, state: STATE) -> set[STATE]:
        epsilon_closure_set = {state}  # first element in the set is the initial state
        queue = [state]  # we place initial state in a queue

        while queue:
            crt_state = queue.pop(0) # pop first state in the queue
            # for each state in the queue, get the states reachable by an EPSILON transition
            epsilon_states = self.d.get((crt_state, EPSILON), set())
            # for each reachable state, if it is not in the epsilon closure set,
            # add it to the set and to the queue using filter and a lambda function
            queue += filter(lambda state: not (state in epsilon_closure_set),
                            list(epsilon_states))
            epsilon_closure_set |= epsilon_states

        return epsilon_closure_set

    def subset_construction(self) -> DFA[frozenset[STATE]]:
        # get initial state of DFA using epsilon_closure on q0 of NFA; create sink state
        dfa_initial_state = frozenset(self.epsilon_closure(self.q0))

        queue = [dfa_initial_state]  # create queue for unvisited states

        dfa_states = set()  # set in which we'll place the states for the resulting DFA
        dfa_transitions = {}  # dictionary for the DFA transitions

        while queue:
            crt_dfa_state = queue[0]  # get first unvisited DFA state from the queue

            # for each symbol in the alphabet, go throught each substate in the DFA state,
            # get next states
            for symbol in self.S:
                dfa_transitions.setdefault((crt_dfa_state, symbol), frozenset())
                # get next states list for every NFA substate for current symbol using
                # list comprehension
                nfa_next_states = [state for nfa_state in crt_dfa_state
                                   for state in self.d.get((nfa_state, symbol), frozenset())]
                # use list comprehension so that we get all epsilon transition states
                # from all next states, add it to the epsilon_states list, then
                # concatenate with the value for the current key in the transitions
                # dictionary
                epsilon_states = [state for nfa_next_state in nfa_next_states
                                    for state in self.epsilon_closure(nfa_next_state)]
                dfa_transitions[(crt_dfa_state, symbol)] |= set(epsilon_states)

                # if we have a transition from the current DFA state to another one,
                # we add the next state to the queue if it wasn't already visited or if it
                # isn't already in the queue; otherwise we create a transition from the
                # current DFA state to the sink state
                next_state = dfa_transitions[(crt_dfa_state, symbol)]
                if next_state not in dfa_states and next_state not in queue:
                    queue.append(frozenset(next_state))

            # current state visited, so we pop it and we add it to the visited DFA states set
            dfa_states.add(crt_dfa_state)
            queue.pop(0)

        # get final states using filter on a lambda function that searches if at least an NFA
        # substate is part of the final NFA states
        dfa_final_states = set(filter(lambda state: any(nfa_state in self.F
                                                        for nfa_state in state), dfa_states))

        return DFA(S=self.S, K=dfa_states, q0=dfa_initial_state,
                   d=dfa_transitions, F=dfa_final_states)

    def remap_states[OTHER_STATE](self, f: 'Callable[[STATE], OTHER_STATE]') -> 'NFA[OTHER_STATE]':
        # optional, but may be useful for the second stage of the project. Works similarly to 'remap_states'
        # from the DFA class. See the comments there for more details.
        pass
