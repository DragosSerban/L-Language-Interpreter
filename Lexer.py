from .Regex import parse_regex
from .NFA import NFA
from .DFA import DFA

class Lexer:
    def __init__(self, spec: list[tuple[str, str]]) -> None:
        # initialisation converts the specification to a DFA which will be used in the lex method
        # the specification is a list of pairs (TOKEN_NAME:REGEX)
        S = set()
        K = {0}
        q0 = 0
        d = dict()
        F = set()
        crt_tuple_nb = 0

        for tuple in spec:
            # for each tuple
            nfa_crt_regex = parse_regex(tuple[1]).thompson() # create an NFA using the current regex

            # add the alphabet of the current NFA to the resulting NFA
            S |= nfa_crt_regex.S

            # when creating the new NFA's states, we also save information about the tuple and the tuple number
            for state in nfa_crt_regex.K:
                K |= {((tuple, crt_tuple_nb), state)}

            # create the new NFA's dictionary; 0 will be the initial state, it will have an Epsilon transition
            # to each of the old initial states
            if (0, "") not in d:
                d[(0, "")] = {((tuple, crt_tuple_nb), nfa_crt_regex.q0)}
            else:
                d[(0, "")] |= {((tuple, crt_tuple_nb), nfa_crt_regex.q0)}

            for (state, transition) in nfa_crt_regex.d:
                if (((tuple, crt_tuple_nb), state), transition) in d:
                    # if the transition from this state already exists,
                    # we add the remaining transitions to the next states in the current NFA to the resulting NFA
                    d[(((tuple, crt_tuple_nb), state), transition)] |= set(((tuple, crt_tuple_nb), x) for x in (nfa_crt_regex.d[(state, transition)]))
                else:
                    # otherwise we add the transitions to the next states in the current NFA to the resulting NFA
                    d[(((tuple, crt_tuple_nb), state), transition)] = set(((tuple, crt_tuple_nb), x) for x in nfa_crt_regex.d[(state, transition)])
            # add final states of current NFA to the resulting NFA
            for final_state in nfa_crt_regex.F:
                F |= {((tuple, crt_tuple_nb), final_state)}
            crt_tuple_nb += 1 # next NFA will be the one corresponding to crt_tuple_nb + 1

        self.nfa = NFA(S, K, q0, d, F) # create the NFA

        self.dfa = self.nfa.subset_construction() # convert NFA to DFA using subset construction


    def lex(self, word: str) -> list[tuple[str, str]] | None:
        # this method splits the lexer into tokens based on the specification and the rules described in the lecture
        # the result is a list of tokens in the form (TOKEN_NAME:MATCHED_STRING)

        # if an error occurs and the lexing fails, you should return none # todo: maybe add error messages as a task
        ret_list_tokens = [] # return value (a list of tuples / tokens)
        row_count = 0 # var that keeps track of the number of rows in the word
        col_count = 0 # var that keeps track of the number of columns in the word

        crt_dfa_state = self.dfa.q0 # we start from the initial state of the DFA
        char_index = 0 # index of current character in the string

        # verify if first character of the string is in the alphabet or not
        if (crt_dfa_state, word[char_index]) not in self.dfa.d:
            return [("", "No viable alternative at character 0, line 0")]

        crt_dfa_state = self.dfa.d[(crt_dfa_state, word[char_index])] # get current state in the DFA
        crt_subword = ""
        crt_verified_subword = ""

        # for each symbol in the word
        while char_index < word.__len__():
            crt_subword += word[char_index] # add current character to the current sub-word

            # if the first character of the string is '\n', increment row_count
            if word[char_index] == "\n":
                row_count += 1
                if col_count > 0:
                    col_count = -1

            # search for the first defined pair given as argument using the position stored in each element;
            # save the position only if the state is final in the NFA
            list_of_final_states = [elem[0][1] for elem in crt_dfa_state if elem in self.nfa.F]
            first_defined_pair = float('inf')
            if list_of_final_states:
                first_defined_pair = min(list_of_final_states)

            for elem in crt_dfa_state:
                if elem[0][1] == first_defined_pair and elem in self.nfa.F:
                    # save the tuple that we checked in a variable
                    prev_tuple = elem[0][0]
                    crt_verified_subword = crt_subword # save current subword

            # go to the next symbol in the string
            char_index += 1
            col_count += 1

            if char_index < word.__len__():
                # if the word didn't end yet:
                if (crt_dfa_state, word[char_index]) not in self.dfa.d:
                    # if current char was not defined as transition => invalid word
                    return [("", "No viable alternative at character " + str(col_count) + ", line " + str(row_count))]

                # get corresponding state to this last char's transition
                crt_dfa_state = self.dfa.d[(crt_dfa_state, word[char_index])]

                # if corresponding state is an empty frozenset
                if crt_dfa_state == frozenset():
                    if crt_verified_subword == "":
                        # we reached a final state and we don't have any matching regex for this subword => we throw an error
                        return [("", "No viable alternative at character " + str(col_count) + ", line " + str(row_count))]
                    ret_list_tokens.append((prev_tuple[0], crt_verified_subword)) # append the last verified word to the list
                    # go back to the first character that appears after the verified subword
                    # and start searching for a maximum regex
                    crt_subword = crt_subword[len(crt_verified_subword):]
                    char_index -= len(crt_subword)

                    # change row and column count based on what characters come before word[char_index]
                    if col_count - len(crt_subword) >= 0:
                        col_count -= len(crt_subword)
                    else:
                        col_count = 0
                        row_count = 0
                        for count in range(char_index):
                            if word[count] == '\n':
                                row_count += 1
                                col_count = 0
                            else:
                                col_count += 1

                    # we found the maximum possible regex for this subword, so we go to the first state in the DFA
                    # and start searching a maximum regex for the next subword, starting with its first character
                    crt_subword = ""
                    crt_verified_subword = ""
                    crt_dfa_state = self.dfa.d[(self.dfa.q0, word[char_index])]
            elif char_index == word.__len__():
                # we reached the end of the word
                first_defined_pair_index = float('inf')
                to_send = ""
                if crt_dfa_state in self.dfa.F:
                    # we are in a final state
                    # we find the first defined regex that matches the end of the word
                    for sub_state in crt_dfa_state:
                        if sub_state in self.nfa.F:
                            if first_defined_pair_index > sub_state[0][1]:
                                first_defined_pair_index = sub_state[0][1]
                                to_send = (sub_state[0][0][0], crt_verified_subword)

                    # append the token to the return list
                    ret_list_tokens.append(to_send)
                else:
                    # we didn't match any regex with the characters at the end of the word
                    return [("", "No viable alternative at character EOF, line " + str(row_count))]

        return ret_list_tokens
