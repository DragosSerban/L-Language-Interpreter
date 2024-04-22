from .NFA import NFA

crt_state = 0

#function used for combining NFAs by sticking them together
def combine_nfas(nfa_list):
    combined_nfa = NFA(S={''}, K=set(), q0=nfa_list[0].q0,
                d={}, F=set())

    last_final_state = -1

    for nfa in nfa_list:
        # add states and alphabet of the current NFA to the resulting one
        combined_nfa.S.update(nfa.S)
        combined_nfa.K.update(nfa.K)

        # add transsitions of the current NFA to the resulting one
        for (state, symbol), next_states in nfa.d.items():
            combined_nfa.d[(state, symbol)] = next_states

        # connect the last and current NFAs with an Epsilon transition
        if last_final_state != -1:
            combined_nfa.d[(last_final_state, "")] = {nfa.q0}
        
        last_final_state = nfa.F.pop()

    # add final state to the resulting NFA
    combined_nfa.F = {last_final_state}

    return combined_nfa

# function that returns a list of characters alphabetically from char1 to char2
def get_letters_interval(char1 : str, char2 : str):
    return [chr(i) for i in range(ord(char1), ord(char2) + 1)]

# we use a tree structure in order to parse the regex
class Node:
    def __init__(self, data, children =[]):
        self.data = data
        self.children = children

    def thompson(self) -> NFA[int]:
        global crt_state
        nfa_list = []
        # Thompson is called; root node is "\\Concat"
        if self.data == "\\Concat":
            # verify if there is a union; if there is one, then we create the union between the child of "|" and the other nodes
            # in this concatenation (it's a concatenation created specifically for the union)
            if self.children[0].data == "|":
                # we concatenate the rest of the children (1...n), as the tree wasn't created with them concatenated
                nfa_list.append(Union(self.children[0].children[0], Node("\\Concat", self.children[1:len(self.children)])).thompson())
            else:
                # else:
                # we can have another concatenation, so we call Thomspon on that as well
                # or we can have a [c1-c2] situation, so we call the Thompson mwthod for that class
                # or we can have a "*" situation, so again, we call the function for that class
                # etc
                for child in self.children:
                    if child.data == "\\Concat":
                        nfa_list.append(child.thompson())
                    elif child.data[0] == "[":
                        nfa_list.append(FromTo(child.data).thompson())
                    elif child.data == "\\*":
                        nfa_list.append(Star(child.children[0]).thompson())
                    elif child.data == "\\?":
                        nfa_list.append(Question(child.children[0]).thompson())
                    elif child.data == "\\+":
                        nfa_list.append(Plus(child.children[0]).thompson())
                    else:
                        nfa_list.append(Character(child.data).thompson())

        # in the end, we combine all the resulting NFAs into one using the function combine_nfas
        return combine_nfas(nfa_list)

class Regex:
    def thompson(self) -> NFA[int]:
        raise NotImplementedError('the thompson method of the Regex class should never be called')

class Character(Regex):
    # Thomson for char: S0 --(char)--> S1
    def __init__(self, char: str):
        self.char = char

    def thompson(self) -> NFA[int]:
        global crt_state

        nfa = NFA(S=set(self.char), K=set([crt_state, crt_state + 1]), q0=crt_state,
                  d= {(crt_state, self.char): set([crt_state + 1])}, F=set([crt_state + 1]))
        crt_state += 2
        return nfa

class FromTo(Regex):
    # here we have a group of letters (transitions)
    # example: [a-z]; we have to get these letters and using the get_letters_interval function,
    # create an NFA using Thomson with 2 states and len(interval) transitions
    def __init__(self, char: str):
        self.char = char

    def thompson(self) -> NFA[int]:
        global crt_state

        tranzitions = get_letters_interval(self.char[1], self.char[3])
        d = {}
        for tranzition in tranzitions:
            d[(crt_state, tranzition)] = set([crt_state + 1])
        nfa = NFA(S=set(tranzitions), K=set([crt_state, crt_state + 1]), q0=crt_state, d=d, F=set([crt_state + 1]))
        crt_state += 2
        return nfa

class Star(Regex):
    def __init__(self, node: Node):
        self.node = node

    def thompson(self) -> NFA[int]:
        global crt_state

        # verify if the node is the result of a concatenation, if so we call Thompson on the node and get the resulting NFA
        if self.node.data == "\\Concat":
            nfa = self.node.thompson()
            # add 2 new states;
            # we can go from previous final state to the new final state or to the previous initial state
            # or we can go from the new initial state to the previous initial state or to the new final state
            nfa.K.update({crt_state, crt_state + 1})
            nfa.d[(nfa.F.pop(), "")] = {nfa.q0, crt_state + 1}
            nfa.d[(crt_state, "")] = {nfa.q0, crt_state + 1}
            nfa.q0 = crt_state # new initial state
            nfa.F = {crt_state + 1} # new final state
            crt_state += 2 # we added 2 new states
            return nfa

        if self.node.data[0] == "[":
            # if the node contains a [c1-c2] type structure, find and add the transitions
            tranzitions = get_letters_interval(self.node.data[1], self.node.data[3])
            d = {}
            d[(crt_state, "")] = set([crt_state + 1, crt_state + 3]) # init state goes to next state or final state
            d[(crt_state + 2, "")] = set([crt_state + 1, crt_state + 3]) # penultimate state goes to second state or to the final state
            for tranzition in tranzitions:
                d[(crt_state + 1, tranzition)] = set([crt_state + 2]) # the [c1-c2] corresponding transitions
            # create the NFA
            nfa = NFA(S={''}.union(set(tranzitions)), K=set([crt_state, crt_state + 1, crt_state + 2, crt_state + 3]),
                      q0=crt_state, d=d, F={crt_state + 3})
        else:
            # else if it is a symbol, create 4 states and 2 transitions (Epsilon + symbol transition)
            # the dictionary is created the same way as it is in the if bracket
            nfa = NFA(S={self.node.data, ''}, K=set([crt_state, crt_state + 1, crt_state + 2, crt_state + 3]), q0=crt_state,
                      d= {(crt_state, ""): set([crt_state + 1, crt_state + 3]), (crt_state + 1, self.node.data): set([crt_state + 2]),
                          (crt_state + 2, ""): set([crt_state + 1, crt_state + 3])}, F={crt_state + 3})
        
        crt_state += 4 # we added four new states
        return nfa

class Question(Regex):
    def __init__(self, node: Node):
        self.node = node

    def thompson(self) -> NFA[int]:
        global crt_state

        # verify if the node is the result of a concatenation, if so we call Thompson on the node and get the resulting NFA
        if self.node.data == "\\Concat":
            nfa = self.node.thompson()
            # add a transition from the intial state to the final state
            nfa.d.setdefault((nfa.q0, ""), set()).add(list(nfa.F)[-1])
            return nfa

        if self.node.data[0] == "[":
            # if the node contains a [c1-c2] type structure, find and add the transitions
            tranzitions = get_letters_interval(self.node.data[1], self.node.data[3])
            d = {}
            for tranzition in tranzitions:
                d[(crt_state, tranzition)] = {crt_state + 1}
            # add an Epsilon transition from the initial state to the final state
            d[(crt_state, "")] = {crt_state + 1}
            # create the NFA
            nfa = NFA(S={''}.union(set(tranzitions)), K=set([crt_state, crt_state + 1]), q0=crt_state, d=d, F=set([crt_state + 1]))
        else:
            # else if it is a symbol, create 2 states and 2 transitions (Epsilon + symbol transition)
            nfa = NFA(S={self.node.data, ''}, K=set([crt_state, crt_state + 1]), q0=crt_state, d= {(crt_state, self.node.data): set([crt_state + 1]), (crt_state, ""): set([crt_state + 1])}, F=set([crt_state + 1]))

        crt_state += 2
        return nfa

class Plus(Regex):
    def __init__(self, node: Node):
        self.node = node

    def thompson(self) -> NFA[int]:
        # concatenate regular NFA with a star type NFA of this node
        # we will use Thompson on a Node object, and then on a Star object
        return combine_nfas([Node("\\Concat", [self.node]).thompson(), Star(self.node).thompson()])

class Union(Regex):
    # here we'll create a union of 2 NFAs
    def __init__(self, node1: Node, node2: Node):
        self.node1 = node1
        self.node2 = node2

    def thompson(self) -> NFA[int]:
        global crt_state

        nfa_list = [self.node1.thompson(), self.node2.thompson()] # create the NFAs of both nodes
        combined_nfa = NFA(S={''}, K=set(), q0=crt_state,
                   d={}, F={crt_state + 1})

        final_states = [] # final states for the 2 NFAs
        initial_states = [] # initial states for the 2 NFAs

        for nfa in nfa_list:
            # add states and alphabet of the current NFA to the resulting one
            combined_nfa.S.update(nfa.S)
            combined_nfa.K.update(nfa.K)

            # add transitions of the current NFA to the resulting one
            for (state, symbol), next_states in nfa.d.items():
                combined_nfa.d.setdefault((state, symbol), set()).update(next_states)

            # add initial and final states of each NFA
            initial_states.append(nfa.q0)
            final_states.extend(list(nfa.F))

        combined_nfa.K.update({crt_state, crt_state + 1}) # new initial and final state

        # add transitions from the new initial state to the previous ones
        combined_nfa.d[(combined_nfa.q0, "")] = {state for state in initial_states}

        # add transitions from the old final states to the new one
        for state in final_states:
            combined_nfa.d[(state, "")] = {crt_state + 1}

        crt_state += 2 # we added 2 new states, so increment crt_state counter
        return combined_nfa

def parse_regex(regex: str) -> Regex:
    global crt_state
    crt_state = 0
    
    stack = []
    tree = Node("\\Concat", children=[])
    i = 0
    # take every element from the regex and use it in order to create the root children
    while i < len(regex):
        symbol = regex[i]

        if symbol == "[":
            stack.append(Node(regex[i:i+5], [])) # add [c1-c2] to the stack
            i += 4
        elif symbol in "*+?":
            # create a new node with with "*"/"+"/"?" for the previous node in the stack
            stack.append(Node("\\" + symbol, [stack.pop()]))
        elif symbol == "(":
            stack.append(Node(symbol, [])) # create a node for the open bracket
        elif symbol == ")":
            # the closed bracket appeared, so we take all elements in the stack until we find the opening of the bracket
            crt_node = Node("\\Concat", [])

            # we add all these elements that we take from the stack as children to the Concat node
            while (crt := stack.pop()).data != "(":
                crt_node.children.append(crt)

            # reverse the children list and add resulting node to the stack
            crt_node.children.reverse()
            stack.append(crt_node)
        elif symbol == "|":
            crt_node = Node("\\Concat", [])

            # get every node in the stack that was concatenated; stop if we find a "(",
            # because that means the union character is inside brackets "...(...{something}...|...)"
            # => we create a node with the elements positioned in the string after the open bracket
            while stack and (crt := stack.pop()):
                if crt.data == "(":
                    stack.append(crt)
                    break
                else:
                    crt_node.children.append(crt)

            # reverse the children list and add resulting node to the stack
            crt_node.children.reverse()
            stack.append(Node("|", [crt_node]))
        elif symbol == "\\":
            # add the special '\{something}' characters to the stack
            i += 1
            stack.append(Node(regex[i], []))
        elif symbol != " ":
            # add every element to the stack, besides the " "
            stack.append(Node(symbol, []))

        i += 1

    # add all root children to the stack
    while stack:
        tree.children.append(stack.pop())

    tree.children.reverse() # reverse the children list
    return tree
