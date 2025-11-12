import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

# --- INFIX TO POSTFIX ---
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

# --- NFA STRUCTURES ---
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

# --- BUILD NFA FROM POSTFIX ---
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

# --- VISUALIZE GRAPH ---
def viewGraph(transitions):
    st.header("ε-NFA Graph")
    G = nx.DiGraph()
    for t in transitions:
        G.add_edge(f"q{t['start']}", f"q{t['final']}", label=t['symbol'])
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=1000)
    labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    st.pyplot(plt)

# --- STREAMLIT UI ---
st.title("ε-NFA Generator from Regular Expression")

regex = st.text_input("Enter Regular Expression (use '.' for concat, '|' for union, '*' for Kleene star):")

if st.button("Generate ε-NFA"):
    if regex:
        postfix = in_to_post(regex)
        nfa = build_nfa(postfix)
        
        st.subheader("Transition Table")
        for t in nfa.transitions:
            st.write(f"q{t['start']} → q{t['final']} : {t['symbol']}")
        
        viewGraph(nfa.transitions)
    else:
        st.warning("Please enter a valid regular expression.")
