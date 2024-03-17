import streamlit as st
def in_to_post(infix):
    precedence = {'|': 1, '*': 2, '.': 1, '(': 0}
    postfix = []
    stack = ['#']
    for char in infix:
        if char.isalnum():
            postfix.append(char)
        elif char == '(':
            stack.append('(')
        elif char == ')':
            while stack[-1] != '#' and stack[-1] != '(':
                postfix.append(stack.pop())
            stack.pop()
        else:
            while stack[-1] != '#' and precedence[char] <= precedence[stack[-1]]:
                postfix.append(stack.pop())
            stack.append(char)
    while stack[-1] != '#':
        postfix.append(stack.pop())
    return ''.join(postfix)


def mktrans(a, b, c):
    global final1, table
    if c == '|':
        table.extend([
            {'start': final1, 'final': final1 + 1, 'symbol': 'ε'},
            {'start': final1, 'final': final1 + 3, 'symbol': 'ε'},
            {'start': final1 + 1, 'final': final1 + 2, 'symbol': a},
            {'start': final1 + 3, 'final': final1 + 4, 'symbol': b},
            {'start': final1 + 2, 'final': final1 + 5, 'symbol': 'ε'},
            {'start': final1 + 4, 'final': final1 + 5, 'symbol': 'ε'}
        ])
        final1 += 5
    elif c == '.':
        table.extend([
            {'start': final1, 'final': final1 + 1, 'symbol': a},
            {'start': final1 + 1, 'final': final1 + 2, 'symbol': b}
        ])
        final1 += 2


def kleene():
    global start1, final1, table
    table.extend([
        {'start': start1 - 1, 'final': start1, 'symbol': 'ε'},
        {'start': final1, 'final': start1, 'symbol': 'ε'},
        {'start': final1, 'final': final1 + 1, 'symbol': 'ε'},
        {'start': start1 - 1, 'final': final1 + 1, 'symbol': 'ε'}
    ])
    final1 += 1
    start1 -= 1


def single(a):
    global final1, table
    table.append({'start': final1, 'final': final1 + 1, 'symbol': a})
    final1 += 1

def check(regx):
    for i in range(len(regx)):
        if not (regx[i].isalpha() or regx[i] == '.' or regx[i] == '|' or regx[i] == '*'):
            return False
    return True

if __name__ == '__main__':
    st.title("ε-NFA Transition Table Generator")
    start1 = 0
    final1 = 0
    table = []
    regx=st.text_input("Enter the Regular Expression")
    regx = in_to_post(regx)
    i = 0
    while i < len(regx):
        if regx[i].isalpha():
            if i+1<len(regx) and regx[i + 1].isalpha():
                mktrans(regx[i], regx[i + 1], regx[i + 2])
                i += 2
            else:
                single(regx[i])
        elif regx[i] == '*':
            kleene()
        i += 1

    for transition in table:
        transition['start'] += abs(start1)
        transition['final'] += abs(start1)

    table.sort(key=lambda x: x['start'])
    if(st.button("Generate Table")):
        if(check(regx)):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Start State**")
            with col2:
                st.write(f"**End State**")
            with col3:
                st.write(f"**Transition**")
        
            for transition in table:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"q[{transition['start']}]")
                with col2:
                    st.write(f"q[{transition['final']}]")
                with col3:
                    st.write(f"{transition['symbol']}")
        else:
            st.write(f"**Enter a Valid Regular Expression**")
