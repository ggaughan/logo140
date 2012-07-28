import ply.yacc as yacc

# Get the token map from the lexer.  This is required.
from lexer import tokens

def p_commands(p):
    '''commands : command
                  | commands command
    '''
    if len(p) > 2:
        p[0] = p[1]
        p[0].append(p[2])
    else:
        p[0] = [p[1]]

def p_command(p):
    'command : movement'
    p[0] = p[1]   
    
def p_movement(p):
    'movement : movement_type NUMBER'
    p[0] = (p[1], p[2])
    
def p_movement_type(p):
    '''movement_type : FORWARD
                     | BACKWARD
                     | RIGHT
                     | LEFT
    '''
    p[0] = p[1]

parser = yacc.yacc()
    
    
if __name__ == "__main__":
    import ply.lex as lex
    # Build the parser
    parser = yacc.yacc()

    while True:
        try:
            s = raw_input('test > ')
        except EOFError:
            break
        if not s: continue
        result = parser.parse(s, lexer=lex.lex())
        print result    
