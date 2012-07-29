# Logo (cut-down) Lexer
# Leeds Hack 2012
# Monkey Tennis

reserved = {
   'repeat' : 'REPEAT',
   'fd': 'FORWARD',
   'bk': 'BACKWARD',
   'lt': 'LEFT',
   'rt': 'RIGHT',
   'to': 'TO',
   'end': 'END',
   'repcount': 'REPCOUNT',
   'home': 'HOME',
   'pu': 'PENUP',
   'pd': 'PENDOWN',
   'setpc': 'SETPENCOLOR',
   #etc
}

# List of token names.   This is always required
tokens = [
   'NUMBER',
   'PLUS',
   'MINUS',
   'TIMES',
   'DIVIDE',
   'LPAREN',
   'RPAREN',
   'LBRACKET',
   'RBRACKET',
   'ID',
   'NS_ID',
   ] + list(reserved.values())

# Regular expression rules for simple tokens
#t_PLUS    = r'\+'
#t_MINUS   = r'-'
#t_TIMES   = r'\*'
#t_DIVIDE  = r'/'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_LBRACKET  = r'\['
t_RBRACKET  = r'\]'
#todo better?
literals = "+-*/"


# A regular expression rule with some action code
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)    
    return t

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value.lower(), 'ID')    # Check for reserved words
    return t


# Error handling rule
def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)
    
if __name__ == "__main__":
    import ply.lex as lex

    # Build the lexer
    lexer = lex.lex()

    # Test it out
    data = '''  repeat  3 FD 2 fd 5  + greg + 4 * 10      + -20 *2  IF then ELse '''

    # Give the lexer some input
    lexer.input(data)

    # Tokenize
    while True:
        tok = lexer.token()
        if not tok: break      # No more input
        print tok
