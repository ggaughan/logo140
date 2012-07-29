import ply.yacc as yacc

# Get the token map from the lexer.  This is required.
from lexer import tokens

def p_commands(p):
    '''commands : command
                  | commands command
    '''
    if len(p) > 2:
        p[0] = p[1]
        if isinstance(p[2], list):
            p[0].extend(p[2])  #e.g. repeat is already a list
        else:
            p[0].append(p[2])
    else:
        if isinstance(p[1], list):
            p[0] = p[1]  ##e.g. repeat is already a list
        else:
            p[0] = [p[1]]

#def p_commands_repeat(p):
    #'''commands : repeat
    #'''
    #r, c = p[1][:-1], p[1][-1]
    #p[0] = [r] + c + [('endrepeat')]  #flatten so in-place
        
def p_command(p):
    '''command : movement
               | repeat
               | to
               | ID
    '''
    if isinstance(p[1], basestring): #ID
        if hasattr(p.lexer, 'context'):
            ns = p.lexer.context.namespace_lookup(p[1].lower())
            if ns is not None:
                p[0] = ('call', p[1].lower())  #standalone, known-name is a call  #todo we could add ns/lookup info here
            else:
                #todo if we're inside a TO definition with this name then allow this recursive call too
                #- it will then be resolved ok at runtime
                print "I don't know how to %s" % p[1]
                raise SyntaxError("I don't know how to %s" % p[1])
    else:
        p[0] = p[1]
    
def p_repeat(p):
    '''repeat : REPEAT NUMBER LBRACKET commands RBRACKET
              | REPEAT REPCOUNT LBRACKET commands RBRACKET
    '''
    #todo combine NUMBER/REPCOUNT!
    #todo handle missing NUMBER syntax error
    p[0] = [(p[1], p[2])]
    p[0].extend(p[4])
    p[0].append(('endrepeat', None))

def p_to(p):
    'to : TO ID commands END'
    p[0] = [(p[1], p[2])]
    p[0].extend(p[3])
    p[0].append(('endto', None))
    
    
def p_movement(p):
    '''movement : movement_type NUMBER
                | movement_type REPCOUNT
                | HOME
                | PENUP
                | PENDOWN
                | SETPENCOLOR ID
    '''
    #todo combine NUMBER/REPCOUNT!
    if len(p) > 2:
        p[0] = (p[1], p[2])
    else:
        p[0] = (p[1], None)
    
def p_movement_type(p):
    '''movement_type : FORWARD
                     | BACKWARD
                     | RIGHT
                     | LEFT
    '''
    p[0] = p[1]

def p_error(p):
    print "Syntax error in input! %s" % p
    yacc.restart()
    
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
