import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

# ---------------- INFIX → POSTFIX ----------------
def in_to_post(infix):
    precedence = {'|': 1, '.': 2, '*': 3, '(': 0}
    output, stack = [], []
    for char in infix:
        if char.isalnum():
            output.append(char)
        elif char == '(':
            stack.append(char)
        elif char == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()
        else:
            while stack and precedence[char] <= precedence[stack[-1]]:
                output.append(stack.pop())
            stack.append(char)
    while stack:
        output.append(stack.pop())
    return ''.join(output)

# ---------------- NFA STRUCTURES ----------------
class NFA:
    def __init__(self, start, end, transitions):
        self.start = start
        self.end = end
        self.transitions = transitions

def new_state(counter):
    counter[0] += 1
    return counter[0]

def single_symbol(symbol, counter):
    s = new_state(counter)
    e = new_state(counter)
    transitions = [{'start': s, 'final': e, 'symbol': symbol}]
    return NFA(s, e, transitions)

def union(a, b, counter):
    s = new_state(counter)
    e = new_state(counter)
    transitions = a.transitions + b.transitions + [
        {'start': s, 'final': a.start, 'symbol': 'ε'},
        {'start': s, 'final': b.start, 'symbol': 'ε'},
        {'start': a.end, 'final': e, 'symbol': 'ε'},
        {'start': b.end, 'final': e, 'symbol': 'ε'},
    ]
    return NFA(s, e, transitions)

def concat(a, b):
    transitions = a.transitions + b.transitions + [
        {'start': a.end, 'final': b.start, 'symbol': 'ε'}
    ]
    return NFA(a.start, b.end, transitions)

def kleene(a, counter):
    s = new_state(counter)
    e = new_state(counter)
    transitions = a.transitions + [
        {'start': s, 'final': a.start, 'symbol': 'ε'},
        {'start': a.end, 'final': e, 'symbol': 'ε'},
        {'start': a.end, 'final': a.start, 'symbol': 'ε'},
        {'start': s, 'final': e, 'symbol': 'ε'},
    ]
    return NFA(s, e, transitions)

# ---------------- BUILD NFA ----------------
def build_nfa(postfix):
    stack = []
    counter = [0]
    for char in postfix:
        if char.isalnum():
            stack.append(single_symbol(char, counter))
        elif char == '*':
            a = stack.pop()
            stack.append(kleene(a, counter))
        elif char == '.':
            b = stack.pop()
            a = stack.pop()
            stack.append(concat(a, b))
        elif char == '|':
            b = stack.pop()
            a = stack.pop()
            stack.append(union(a, b, counter))
    return stack.pop()

# ---------------- SIMULATION HELPERS ----------------
def epsilon_closure(states, transitions):
    stack = list(states)
    closure = set(states)
    while stack:
        state = stack.pop()
        for t in transitions:
            if t['start'] == state and t['symbol'] == 'ε' and t['final'] not in closure:
                closure.add(t['final'])
                stack.append(t['final'])
    return closure

def move(states, symbol, transitions):
    next_states = set()
    for t in transitions:
        if t['start'] in states and t['symbol'] == symbol:
            next_states.add(t['final'])
    return next_states

def simulate_nfa(nfa, input_string):
    current_states = epsilon_closure({nfa.start}, nfa.transitions)
    for symbol in input_string:
        current_states = epsilon_closure(move(current_states, symbol, nfa.transitions), nfa.transitions)
    return nfa.end in current_states

# ---------------- VISUALIZATION ----------------
def viewGraph(transitions):
    st.subheader("ε-NFA Graph")
    G = nx.DiGraph()
    for t in transitions:
        G.add_edge(f"q{t['start']}", f"q{t['final']}", label=t['symbol'])
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=1000)
    labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    st.pyplot(plt)

# ---------------- STREAMLIT UI ----------------
st.title("ε-NFA Generator and Simulator")

regex = st.text_input("Enter Regular Expression (use '.' for concat, '|' for union, '*' for Kleene star):")
test_string = st.text_input("Enter Test String (empty for ε):")

if st.button("Build and Test"):
    if regex:
        postfix = in_to_post(regex)
        nfa = build_nfa(postfix)
        st.write(f"**Postfix:** `{postfix}`")

        st.subheader("Transition Table")
        for t in nfa.transitions:
            st.write(f"q{t['start']} → q{t['final']} : {t['symbol']}")

        accepted = simulate_nfa(nfa, test_string)
        if accepted:
            st.success(f"✅ The string '{test_string if test_string else 'ε'}' is ACCEPTED by the NFA")
        else:
            st.error(f"❌ The string '{test_string if test_string else 'ε'}' is REJECTED by the NFA")

        viewGraph(nfa.transitions)
    else:
        st.warning("Please enter a valid regular expression.")
